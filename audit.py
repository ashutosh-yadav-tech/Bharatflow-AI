"""
audit.py
--------
Minimal append-style audit log. Uses a local SQLite file so it's zero-cost
and needs no external DB service. Note (documented in README too): on
Streamlit Community Cloud, local disk isn't guaranteed to persist across
app restarts/sleeps - for a resume demo this is an acceptable, clearly
stated limitation. Swapping in a free-tier hosted Postgres (e.g. Supabase)
is a drop-in upgrade if persistence across restarts is required.
"""

import json
import sqlite3
from datetime import datetime

DB_PATH = "bharatflow_audit.db"


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS investigations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            shipment_id TEXT,
            route TEXT,
            current_hub TEXT,
            primary_cause TEXT,
            confidence REAL,
            sla_risk_pct REAL,
            engine TEXT,
            full_record TEXT
        )
    """)
    return conn


def log_investigation(ship, detection_report: dict, diagnosis: dict) -> None:
    conn = _connect()
    conn.execute(
        """INSERT INTO investigations
           (timestamp, shipment_id, route, current_hub, primary_cause, confidence,
            sla_risk_pct, engine, full_record)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            datetime.utcnow().isoformat(),
            ship.id,
            ship.route_name,
            ship.current_hub,
            diagnosis.get("primary_cause"),
            diagnosis.get("confidence"),
            diagnosis.get("sla_risk_pct"),
            diagnosis.get("engine"),
            json.dumps(diagnosis, default=str),
        ),
    )
    conn.commit()
    conn.close()


def fetch_log(limit: int = 100):
    conn = _connect()
    rows = conn.execute(
        """SELECT timestamp, shipment_id, route, current_hub, primary_cause,
                  confidence, sla_risk_pct, engine
           FROM investigations ORDER BY id DESC LIMIT ?""",
        (limit,),
    ).fetchall()
    conn.close()
    cols = ["timestamp", "shipment_id", "route", "current_hub", "primary_cause",
            "confidence", "sla_risk_pct", "engine"]
    return [dict(zip(cols, row)) for row in rows]


def clear_log() -> None:
    conn = _connect()
    conn.execute("DELETE FROM investigations")
    conn.commit()
    conn.close()
