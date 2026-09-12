W_DWELL_Z = 0.5
W_PRIORITY = 0.3
W_VALUE = 0.2

VALUE_HIGH_INR = 300_000
VALUE_MED_INR = 100_000


def compute_priority_score(detection_report: dict) -> float:
    z = min(detection_report["dwell_zscore"], 6.0) / 6.0
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


WEATHER_SEVERITY_FLAG = 0.6
CONGESTION_FLAG_PCT = 80.0
COMPLIANCE_FLAG_STATUSES = {"pending", "flagged"}


def evidence_strength_weather(weather_reading: dict) -> float:
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
    if not evidence_scores:
        return 0.0
    top_cause_strength = max(evidence_scores.values())
    z_component = min(dwell_zscore, 5.0) / 5.0
    confidence = 0.7 * top_cause_strength + 0.3 * z_component
    return round(min(confidence, 0.99), 2)


def compute_sla_risk_pct(dwell_zscore: float, priority: str, top_evidence_strength: float) -> float:
    base = min(dwell_zscore, 6.0) / 6.0 * 60
    priority_bump = 20 if priority == "express" else 5
    evidence_bump = top_evidence_strength * 20
    return round(min(base + priority_bump + evidence_bump, 99.0), 1)
