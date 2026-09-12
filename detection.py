from data_generator import Shipment, HUB_DWELL_BASELINE, HOP_TRANSIT_BASELINE

Z_SCORE_FLAG_THRESHOLD = 2.0


def zscore(actual: float, mean: float, std: float) -> float:
    if std <= 0:
        return 0.0
    return (actual - mean) / std


def evaluate_shipment(ship: Shipment) -> dict:
    hub = ship.current_hub
    mean, std = HUB_DWELL_BASELINE[hub]
    actual_dwell = ship.dwell_hours.get(hub, mean)
    dwell_z = zscore(actual_dwell, mean, std)
    dwell_deviation_pct = ((actual_dwell - mean) / mean) * 100 if mean else 0.0

    worst_hop_z = 0.0
    worst_hop = None
    for (a, b), actual in ship.transit_hours.items():
        m, s = HOP_TRANSIT_BASELINE[(a, b)]
        z = zscore(actual, m, s)
        if z > worst_hop_z:
            worst_hop_z = z
            worst_hop = (a, b)

    is_flagged = dwell_z >= Z_SCORE_FLAG_THRESHOLD or worst_hop_z >= Z_SCORE_FLAG_THRESHOLD

    return {
        "shipment_id": ship.id,
        "route": ship.route_name,
        "current_hub": hub,
        "dwell_hours_actual": round(actual_dwell, 2),
        "dwell_hours_baseline_mean": mean,
        "dwell_hours_baseline_std": std,
        "dwell_zscore": round(dwell_z, 2),
        "dwell_deviation_pct": round(dwell_deviation_pct, 1),
        "worst_transit_hop": worst_hop,
        "worst_transit_zscore": round(worst_hop_z, 2),
        "is_flagged": bool(is_flagged),
        "priority": ship.priority,
        "declared_value_inr": ship.declared_value_inr,
    }
