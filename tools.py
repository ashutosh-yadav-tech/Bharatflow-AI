"""
tools.py
--------
Three "tools" the agent can call while investigating a flagged shipment.

get_weather_live -> a REAL network call to Open-Meteo (free, no API key).
                     This is what makes the live demo genuinely live rather
                     than fully canned.
get_weather_simulated -> used only by the offline evaluation harness, so
                     accuracy numbers are reproducible and not dependent on
                     whatever the real weather happens to be right now.
get_compliance_status / get_hub_congestion -> simulated system lookups.
                     A real e-way bill / hub WMS API isn't publicly available
                     for free, so these read the shipment's simulated system
                     fields instead. This is called out explicitly in the
                     README as the integration point a real deployment would
                     replace.
"""

import requests
from data_generator import HUBS

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

_WMO_CODE_MAP = {
    0: "clear", 1: "mostly clear", 2: "partly cloudy", 3: "overcast",
    45: "fog", 48: "fog",
    51: "light drizzle", 53: "drizzle", 55: "heavy drizzle",
    61: "light rain", 63: "rain", 65: "heavy rain",
    71: "light snow", 73: "snow", 75: "heavy snow",
    80: "rain showers", 81: "rain showers", 82: "violent rain showers",
    95: "thunderstorm", 96: "thunderstorm with hail", 99: "thunderstorm with hail",
}


def get_weather_live(hub_name: str) -> dict:
    lat, lon = HUBS[hub_name]
    try:
        resp = requests.get(
            OPEN_METEO_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,precipitation,weathercode,wind_speed_10m",
                "timezone": "Asia/Kolkata",
            },
            timeout=6,
        )
        resp.raise_for_status()
        cur = resp.json().get("current", {})
        code = cur.get("weathercode", cur.get("weather_code", 0))
        return {
            "hub": hub_name,
            "condition": _WMO_CODE_MAP.get(code, "unknown"),
            "temperature_c": cur.get("temperature_2m"),
            "precipitation_mm": cur.get("precipitation", 0),
            "wind_kmh": cur.get("wind_speed_10m"),
            "source": "open-meteo (live)",
        }
    except Exception as e:
        return {
            "hub": hub_name,
            "condition": "unavailable",
            "temperature_c": None,
            "precipitation_mm": 0,
            "wind_kmh": None,
            "source": f"fallback - live weather call failed ({type(e).__name__})",
        }


def get_weather_simulated(ship) -> dict:
    return {
        "hub": ship.current_hub,
        "condition": ship.weather_label_sim,
        "precipitation_mm": round(ship.weather_severity_sim * 12, 1),
        "temperature_c": None,
        "wind_kmh": None,
        "source": "simulated (evaluation mode)",
    }


def get_compliance_status(ship) -> dict:
    return {
        "shipment_id": ship.id,
        "status": ship.compliance_status,
        "source": "simulated e-way bill / customs system (integration point for real deployment)",
    }


def get_hub_congestion(ship) -> dict:
    pct = ship.hub_congestion_pct
    label = "high" if pct >= 80 else "medium" if pct >= 55 else "low"
    return {
        "hub": ship.current_hub,
        "congestion_pct": pct,
        "label": label,
        "source": "simulated hub WMS feed (integration point for real deployment)",
    }


TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather conditions at the shipment's current hub city.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_compliance_status",
            "description": "Check customs/e-way bill compliance status for this shipment.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_hub_congestion",
            "description": "Get current congestion/load level at the shipment's current hub.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "submit_diagnosis",
            "description": "Submit your final root-cause diagnosis once you have gathered enough evidence. Call this exactly once, last.",
            "parameters": {
                "type": "object",
                "properties": {
                    "primary_cause": {
                        "type": "string",
                        "enum": ["weather", "compliance", "congestion", "unexplained"],
                    },
                    "contributing_causes": {
                        "type": "array",
                        "items": {"type": "string", "enum": ["weather", "compliance", "congestion"]},
                    },
                    "explanation": {"type": "string", "description": "2-3 sentence plain-language explanation grounded in the evidence you gathered."},
                    "recommended_action": {"type": "string"},
                },
                "required": ["primary_cause", "explanation", "recommended_action"],
            },
        },
    },
]
