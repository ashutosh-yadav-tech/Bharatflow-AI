import json
import os

from scoring import (
    evidence_strength_weather,
    evidence_strength_compliance,
    evidence_strength_congestion,
    compute_diagnosis_confidence,
    compute_sla_risk_pct,
)
from tools import (
    TOOL_SCHEMAS,
    get_weather_live,
    get_weather_simulated,
    get_compliance_status,
    get_hub_congestion,
)

if not os.environ.get("GROQ_API_KEY"):
    try:
        import toml
        secrets_path = os.path.join(os.path.dirname(__file__), ".streamlit", "secrets.toml")
        if os.path.exists(secrets_path):
            sec = toml.load(secrets_path)
            if "GROQ_API_KEY" in sec and sec["GROQ_API_KEY"]:
                os.environ["GROQ_API_KEY"] = sec["GROQ_API_KEY"]
    except Exception:
        pass

MODEL_NAME = os.environ.get("BHARATFLOW_MODEL", "qwen/qwen3.8-27b")
MAX_TOOL_ITERATIONS = 5

SYSTEM_PROMPT = """You are a logistics root-cause investigation agent for an Indian \
parcel network (BharatFlow). You are given a shipment that has been statistically \
flagged as delayed beyond its normal baseline at a hub.

Your job:
1. Call all available investigative tools (get_weather, get_compliance_status, get_hub_congestion) in parallel in your initial turn to gather comprehensive telemetry.
2. Reason about which factor(s) actually explain the delay. Do not assume every tool \
result matters - a tool coming back clean is also evidence.
3. If no tool result clearly explains the delay, it is correct and expected to say \
primary_cause = "unexplained" rather than force an explanation onto weak evidence.
4. Finish by calling submit_diagnosis exactly once with your conclusion.

Only ground your explanation in the tool results you actually received - never invent \
data you did not retrieve."""


def _shipment_context(ship, detection_report) -> str:
    return f"""Shipment {ship.id} on route {ship.route_name}.
Currently at hub: {ship.current_hub}
Dwell time at this hub: {detection_report['dwell_hours_actual']}h \
(baseline mean {detection_report['dwell_hours_baseline_mean']}h, \
z-score {detection_report['dwell_zscore']})
Priority: {ship.priority}
Declared value: ₹{ship.declared_value_inr:,.0f}
"""


def _dispatch_tool(name: str, ship, mode: str) -> dict:
    if name == "get_weather":
        return get_weather_live(ship.current_hub) if mode == "live" else get_weather_simulated(ship)
    if name == "get_compliance_status":
        return get_compliance_status(ship)
    if name == "get_hub_congestion":
        return get_hub_congestion(ship)
    return {"error": f"unknown tool {name}"}


def _rule_based_fallback(ship, detection_report, mode: str) -> dict:
    weather = get_weather_live(ship.current_hub) if mode == "live" else get_weather_simulated(ship)
    compliance = get_compliance_status(ship)
    congestion = get_hub_congestion(ship)

    scores = {
        "weather": evidence_strength_weather(weather),
        "compliance": evidence_strength_compliance(compliance),
        "congestion": evidence_strength_congestion(congestion),
    }
    top_cause, top_score = max(scores.items(), key=lambda kv: kv[1])
    primary = top_cause if top_score >= 0.4 else "unexplained"
    contributing = [c for c, s in scores.items() if s >= 0.4 and c != primary]

    confidence = compute_diagnosis_confidence(scores, detection_report["dwell_zscore"])
    sla_risk = compute_sla_risk_pct(detection_report["dwell_zscore"], ship.priority, top_score)

    return {
        "shipment_id": ship.id,
        "primary_cause": primary,
        "contributing_causes": contributing,
        "explanation": (
            f"[Rule-based fallback - no LLM] Highest evidence signal was {top_cause} "
            f"(strength {top_score:.2f}). Dwell z-score {detection_report['dwell_zscore']}."
        ),
        "recommended_action": "Escalate for manual review." if primary == "unexplained" else f"Address {primary} factor and monitor.",
        "confidence": confidence,
        "sla_risk_pct": sla_risk,
        "evidence": {"weather": weather, "compliance": compliance, "congestion": congestion},
        "tool_trace": ["get_weather", "get_compliance_status", "get_hub_congestion"],
        "engine": "rule-based-fallback",
    }


def run_investigation(ship, detection_report, mode: str = "live") -> dict:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return _rule_based_fallback(ship, detection_report, mode)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1", timeout=12.0, max_retries=1)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _shipment_context(ship, detection_report)},
        ]

        tool_trace = []
        evidence = {}
        diagnosis = None

        for i in range(MAX_TOOL_ITERATIONS):
            force_final = i == MAX_TOOL_ITERATIONS - 1
            resp = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                tools=TOOL_SCHEMAS,
                tool_choice=(
                    {"type": "function", "function": {"name": "submit_diagnosis"}}
                    if force_final else "auto"
                ),
            )
            msg = resp.choices[0].message
            messages.append(msg.model_dump(exclude_none=True))

            if not msg.tool_calls:
                break

            for tc in msg.tool_calls:
                fn_name = tc.function.name
                if fn_name == "submit_diagnosis":
                    diagnosis = json.loads(tc.function.arguments)
                    messages.append({
                        "role": "tool", "tool_call_id": tc.id,
                        "content": "diagnosis recorded",
                    })
                    continue
                tool_trace.append(fn_name)
                result = _dispatch_tool(fn_name, ship, mode)
                evidence[fn_name.replace("get_", "").replace("_status", "")] = result
                messages.append({
                    "role": "tool", "tool_call_id": tc.id,
                    "content": json.dumps(result),
                })

            if diagnosis is not None:
                break

        if diagnosis is None:
            return _rule_based_fallback(ship, detection_report, mode)

        scores = {}
        if "weather" in evidence:
            scores["weather"] = evidence_strength_weather(evidence["weather"])
        if "compliance" in evidence:
            scores["compliance"] = evidence_strength_compliance(evidence["compliance"])
        if "congestion" in evidence:
            scores["congestion"] = evidence_strength_congestion(evidence["congestion"])

        confidence = compute_diagnosis_confidence(scores, detection_report["dwell_zscore"])
        top_strength = max(scores.values()) if scores else 0.0
        sla_risk = compute_sla_risk_pct(detection_report["dwell_zscore"], ship.priority, top_strength)

        return {
            "shipment_id": ship.id,
            "primary_cause": diagnosis.get("primary_cause", "unexplained"),
            "contributing_causes": diagnosis.get("contributing_causes", []),
            "explanation": diagnosis.get("explanation", ""),
            "recommended_action": diagnosis.get("recommended_action", ""),
            "confidence": confidence,
            "sla_risk_pct": sla_risk,
            "evidence": evidence,
            "tool_trace": tool_trace,
            "engine": f"groq/{MODEL_NAME}",
        }

    except Exception as e:
        fallback = _rule_based_fallback(ship, detection_report, mode)
        fallback["explanation"] = f"[LLM call failed: {type(e).__name__}: {e}] " + fallback["explanation"]
        return fallback
