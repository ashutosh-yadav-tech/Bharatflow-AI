"""
data_generator.py
------------------
Synthetic India logistics network (hubs, routes, baselines) and a shipment
event generator.

Design note (important): the generator does NOT create a 1:1 mapping between
"true cause" and the signals tools will observe. This is deliberate — if the
simulator always makes the weather tool loudly confirm a weather-caused delay,
the agent isn't doing inference, it's doing lookup. Instead:
  - ~15% of delays have NO clean single cause (genuine noise) — the agent
    should be able to say "insufficient evidence for a confident root cause"
    rather than confabulate one.
  - ~20% of "true cause" delays have a MUTED signal (e.g. weather caused it,
    but by the time the tool is queried conditions have improved) — the agent
    has to weigh evidence, not just pattern-match on presence/absence.
  - Some shipments have MULTIPLE contributing causes at once.
"""

import random
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

# ---------------------------------------------------------------------------
# Network topology
# ---------------------------------------------------------------------------

HUBS = {
    "Delhi":     (28.6139, 77.2090),
    "Mumbai":    (19.0760, 72.8777),
    "Pune":      (18.5204, 73.8567),
    "Bengaluru": (12.9716, 77.5946),
    "Hyderabad": (17.3850, 78.4867),
    "Chennai":   (13.0827, 80.2707),
    "Kolkata":   (22.5726, 88.3639),
    "Ahmedabad": (23.0225, 72.5714),
    "Jaipur":    (26.9124, 75.7873),
    "Lucknow":   (26.8467, 80.9462),
    "Guwahati":  (26.1445, 91.7362),
}

ROUTES = {
    "Delhi-Mumbai":     ["Delhi", "Jaipur", "Ahmedabad", "Mumbai"],
    "Delhi-Bengaluru":  ["Delhi", "Hyderabad", "Bengaluru"],
    "Mumbai-Chennai":   ["Mumbai", "Pune", "Bengaluru", "Chennai"],
    "Delhi-Kolkata":    ["Delhi", "Lucknow", "Kolkata"],
    "Mumbai-Bengaluru": ["Mumbai", "Pune", "Bengaluru"],
    "Hyderabad-Delhi":  ["Hyderabad", "Jaipur", "Delhi"],
}

CAUSE_TAGS = ["weather", "compliance", "congestion"]

# ---------------------------------------------------------------------------
# Baselines (mean/std) per hub-dwell and per transit-hop, seeded for
# reproducibility. These play the role of "historical data" a real system
# would compute from months of scan events.
# ---------------------------------------------------------------------------

_rng = random.Random(42)

HUB_DWELL_BASELINE = {}   # hub -> (mean_hours, std_hours)
for hub in HUBS:
    mean = _rng.uniform(3.0, 5.5)
    std = mean * 0.18
    HUB_DWELL_BASELINE[hub] = (round(mean, 2), round(std, 2))

HOP_TRANSIT_BASELINE = {}  # (from_hub, to_hub) -> (mean_hours, std_hours)
for route, path in ROUTES.items():
    for a, b in zip(path[:-1], path[1:]):
        mean = _rng.uniform(6.0, 11.0)
        std = mean * 0.15
        HOP_TRANSIT_BASELINE[(a, b)] = (round(mean, 2), round(std, 2))


@dataclass
class Shipment:
    id: str
    route_name: str
    path: list
    created_at: datetime
    current_hub_index: int
    dwell_hours: dict = field(default_factory=dict)   # hub -> actual dwell hrs
    transit_hours: dict = field(default_factory=dict)  # (a,b) -> actual hrs
    declared_value_inr: float = 0.0
    priority: str = "standard"
    ground_truth_causes: list = field(default_factory=list)  # hidden, for eval only
    state: str = "IN_TRANSIT"

    # Simulated external-system readings (as if queried from real systems).
    # These are generated WITH intentional noise/muting relative to
    # ground_truth_causes so an agent can't just echo the tag back.
    compliance_status: str = "cleared"       # cleared | pending | flagged
    hub_congestion_pct: float = 0.0          # 0-100
    weather_severity_sim: float = 0.0        # 0-1, used only in eval mode
    weather_label_sim: str = "clear"

    @property
    def current_hub(self) -> str:
        idx = min(self.current_hub_index, len(self.path) - 1)
        return self.path[idx]

    @property
    def destination(self) -> str:
        return self.path[-1]


_counter = [1000]


def _next_id() -> str:
    _counter[0] += 1
    return f"SHP-{_counter[0]}"


def generate_shipment(exception_prob: float = 0.35, rng: Optional[random.Random] = None) -> Shipment:
    """Generate one shipment currently sitting at some hub along its route,
    with realistic (imperfectly correlated) delay causes."""
    r = rng or random
    route_name = r.choice(list(ROUTES.keys()))
    path = ROUTES[route_name]

    # shipment is somewhere between hub 0 (origin, already departed) and the
    # second-to-last hub (still has a leg to go) — pick a hub index >=1 so it
    # has at least one completed hop behind it
    current_idx = r.randint(1, len(path) - 1)
    current_hub = path[current_idx]

    ship = Shipment(
        id=_next_id(),
        route_name=route_name,
        path=path,
        created_at=datetime.utcnow() - timedelta(hours=r.uniform(10, 40)),
        current_hub_index=current_idx,
        declared_value_inr=round(r.uniform(15000, 450000), 2),
        priority=r.choice(["standard", "standard", "standard", "express"]),
    )

    is_exception = r.random() < exception_prob
    chosen_causes = []
    if is_exception:
        n_causes = r.choices([0, 1, 2], weights=[15, 65, 20])[0]  # 0 = unexplained noise
        chosen_causes = r.sample(CAUSE_TAGS, k=n_causes) if n_causes > 0 else []
        ship.ground_truth_causes = chosen_causes

    # fill dwell times for every hub visited so far (including current)
    for i in range(1, current_idx + 1):
        hub = path[i]
        mean, std = HUB_DWELL_BASELINE[hub]
        actual = r.gauss(mean, std)
        if is_exception and i == current_idx:
            # inflate dwell at the CURRENT hub if an exception is active
            multiplier = r.uniform(2.0, 4.5)
            actual *= multiplier
        ship.dwell_hours[hub] = max(0.5, round(actual, 2))

    # fill transit times for every hop completed so far
    for i in range(current_idx):
        a, b = path[i], path[i + 1]
        mean, std = HOP_TRANSIT_BASELINE[(a, b)]
        actual = r.gauss(mean, std)
        if is_exception and i == current_idx - 1 and "congestion" in chosen_causes:
            actual *= r.uniform(1.4, 2.2)
        ship.transit_hours[(a, b)] = max(0.5, round(actual, 2))

    ship.state = "HUB_PROCESSING" if is_exception else "IN_TRANSIT"

    # ---- simulated external-system signals (with muting/noise) ----
    # Compliance
    if "compliance" in chosen_causes:
        ship.compliance_status = r.choices(
            ["pending", "flagged", "cleared"], weights=[65, 15, 20]  # 20% muted
        )[0]
    else:
        ship.compliance_status = r.choices(["cleared", "pending"], weights=[96, 4])[0]

    # Hub congestion
    if "congestion" in chosen_causes:
        ship.hub_congestion_pct = round(
            r.uniform(80, 98) if r.random() > 0.20 else r.uniform(55, 75), 1
        )
    else:
        ship.hub_congestion_pct = round(r.uniform(25, 65), 1)

    # Weather severity (used only by the evaluation harness — the live app
    # queries real Open-Meteo instead, see tools.py)
    if "weather" in chosen_causes:
        ship.weather_severity_sim = round(
            r.uniform(0.7, 1.0) if r.random() > 0.20 else r.uniform(0.2, 0.4), 2
        )
    else:
        ship.weather_severity_sim = round(r.uniform(0.0, 0.3), 2)
    ship.weather_label_sim = (
        "heavy rain / fog" if ship.weather_severity_sim > 0.6
        else "light rain" if ship.weather_severity_sim > 0.3
        else "clear"
    )

    return ship


def generate_batch(n: int, exception_prob: float = 0.35, seed: Optional[int] = None) -> list:
    r = random.Random(seed) if seed is not None else random
    return [generate_shipment(exception_prob=exception_prob, rng=r) for _ in range(n)]
