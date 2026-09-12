"""
scoring.py
----------
Deliberately NOT a black box: every weight here is a named constant so the
formula can be read, audited, and argued with in a design review — which is
exactly the property the earlier design doc flagged as missing from a lot of
"confidence score" hand-waving in similar projects.
"""

# --- weights for pre-investigation priority (which flagged shipments to
#     investigate first, before any tool evidence is gathered) -------------
W_DWELL_Z = 0.5
W_PRIORITY = 0.3
W_VALUE = 0.2

VALUE_HIGH_INR = 300_000
VALUE_MED_INR = 100_000


def compute_priority_score(detection_report: dict) -> float:
    """0-100. Higher = investigate sooner."""
    z = min(detection_report["dwell_zscore"], 6.0) / 6.0  # normalize, cap outliers
    priority_component = 1.0 if detection_report["priority"] == "express" else 0.4

    value = detection_report["declared_value_inr"]
    if value >= VALUE_HIGH_INR:
        value_component = 1.0
    elif value >= VALUE_MED_INR:
        value_component = 0.6
    else:
        value_component = 0.3

    score = 100 * (W_DWELL_Z * z + W_PRIORITY * priority_component + W_VALUE * value_component)
    return round(min(score, 100.0), 1)


# --- weights for post-investigation evidence strength per candidate cause -
WEATHER_SEVERITY_FLAG = 0.6   # >= this counts as "weather implicated"
CONGESTION_FLAG_PCT = 80.0    # >= this counts as "congestion implicated"
COMPLIANCE_FLAG_STATUSES = {"pending", "flagged"}


def evidence_strength_weather(weather_reading: dict) -> float:
    """0-1 score for how strongly the weather tool's reading implicates weather."""
    condition = (weather_reading.get("condition") or "").lower()
    precip = weather_reading.get("precipitation_mm", 0) or 0
    if any(k in condition for k in ["thunder", "heavy", "fog", "storm"]) or precip > 8:
        return 0.9
    if any(k in condition for k in ["rain", "drizzle", "cloud"]) or precip > 1:
        return 0.5
    return 0.05


def evidence_strength_compliance(compliance_reading: dict) -> float:
    status = compliance_reading.get("status", "cleared")
    if status == "flagged":
        return 0.95
    if status == "pending":
        return 0.75
    return 0.05


def evidence_strength_congestion(congestion_reading: dict) -> float:
    pct = congestion_reading.get("congestion_pct", 0)
    if pct >= 85:
        return 0.9
    if pct >= 70:
        return 0.6
    if pct >= 55:
        return 0.3
    return 0.05


def compute_diagnosis_confidence(evidence_scores: dict, dwell_zscore: float) -> float:
    """
    Combine tool-evidence strength with the statistical anomaly magnitude
    into one 0-1 confidence figure for the TOP candidate cause.
    This number is computed here, deterministically — the LLM's job is to
    explain and prioritize among causes, not to invent the confidence figure.
    """
    if not evidence_scores:
        return 0.0
    top_cause_strength = max(evidence_scores.values())
    z_component = min(dwell_zscore, 5.0) / 5.0
    confidence = 0.7 * top_cause_strength + 0.3 * z_component
    return round(min(confidence, 0.99), 2)


def compute_sla_risk_pct(dwell_zscore: float, priority: str, top_evidence_strength: float) -> float:
    """Rough SLA-breach-probability estimate (0-100), same transparent-weights approach."""
    base = min(dwell_zscore, 6.0) / 6.0 * 60          # anomaly severity -> up to 60 pts
    priority_bump = 20 if priority == "express" else 5
    evidence_bump = top_evidence_strength * 20         # confirmed cause -> up to 20 pts
    return round(min(base + priority_bump + evidence_bump, 99.0), 1)
