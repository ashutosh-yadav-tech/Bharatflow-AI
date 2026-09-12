"""
app.py
------
BharatFlow AI - Shipment Exception & Root-Cause Intelligence (Modernized Streamlit Edition)

Zero-cost stack: Streamlit Community Cloud (hosting) + Groq free-tier API
(Qwen / Llama open-weight models, no training, no cost) + Open-Meteo (free live
weather) + simulated compliance/congestion signals (documented integration
points for a real deployment).

100% SVG Icons, Zero Emojis.
"""

import os
import pandas as pd
import plotly.express as px
import streamlit as st

from data_generator import HUBS, generate_shipment
from detection import evaluate_shipment
from scoring import compute_priority_score
from agent import run_investigation, MODEL_NAME
from evaluation import run_evaluation
import audit

# ---------------------------------------------------------------------------
# Setup & Secrets
# ---------------------------------------------------------------------------

st.set_page_config(page_title="BharatFlow AI — Logistics Intelligence", layout="wide")

try:
    if "GROQ_API_KEY" in st.secrets and st.secrets["GROQ_API_KEY"]:
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
except Exception:
    pass

HAS_API_KEY = bool(os.environ.get("GROQ_API_KEY"))

if "shipments" not in st.session_state:
    st.session_state.shipments = []
if "diagnoses" not in st.session_state:
    st.session_state.diagnoses = {}

# Custom Industrial CSS & SVG Injections (No Emojis) — DHL Balanced Palette
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background-color: #ffffff;
        color: #333333;
    }
    
    header[data-testid="stHeader"] {
        background-color: #ffffff;
    }

    section[data-testid="stSidebar"] {
        background-color: #242832 !important;
        color: #ffffff !important;
    }

    section[data-testid="stSidebar"] * {
        color: #e5e7eb;
    }

    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }

    /* Primary Buttons in DHL Red */
    .stButton>button {
        background-color: #d40511 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: transform 0.1s ease, background-color 0.15s ease;
    }

    .stButton>button:hover {
        background-color: #b8040e !important;
        color: #ffffff !important;
    }

    .stButton>button:active {
        transform: scale(0.97);
    }
    
    .svg-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
    }
    .badge-flagged {
        background-color: rgba(212, 5, 17, 0.08);
        color: #d40511;
        border: 1px solid rgba(212, 5, 17, 0.35);
    }
    .badge-normal {
        background-color: rgba(5, 150, 105, 0.1);
        color: #059669;
        border: 1px solid rgba(5, 150, 105, 0.3);
    }
    .badge-weather {
        background-color: rgba(2, 132, 199, 0.1);
        color: #0284c7;
        border: 1px solid rgba(2, 132, 199, 0.3);
    }
    .badge-compliance {
        background-color: rgba(212, 5, 17, 0.08);
        color: #d40511;
        border: 1px solid rgba(212, 5, 17, 0.35);
    }
    .badge-congestion {
        background-color: rgba(255, 204, 0, 0.2);
        color: #92400e;
        border: 1px solid #d97706;
    }
    .badge-unexplained {
        background-color: #f4f4f4;
        color: #4b5563;
        border: 1px solid #d1d5db;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

st.sidebar.markdown("""
<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M16.5 9.4 7.55 4.24a1.78 1.78 0 0 0-2.5 1.55v12.42a1.78 1.78 0 0 0 2.5 1.55L16.5 14.6a1.78 1.78 0 0 0 0-3.2Z"></path>
        <path d="m21 16-4.5-2.6"></path>
        <path d="m21 8-4.5 2.6"></path>
        <path d="M7.5 4.2 12 6.8"></path>
        <path d="M7.5 19.8 12 17.2"></path>
    </svg>
    <h2 style="margin: 0; font-size: 1.25rem; font-weight: 700; color: #ffffff;">BharatFlow AI</h2>
</div>
""", unsafe_allow_html=True)
st.sidebar.caption("Shipment exception & root-cause agent — India network telemetry")

if HAS_API_KEY:
    st.sidebar.success(f"Agent engine: Groq LLM ({MODEL_NAME}) (live)")
else:
    st.sidebar.warning("No GROQ_API_KEY set — running in rule-based fallback mode.")

n_new = st.sidebar.slider("Shipments to generate", 1, 15, 5)
exc_prob = st.sidebar.slider("Exception probability", 0.0, 1.0, 0.35, 0.05)

if st.sidebar.button("Generate new shipment events", use_container_width=True):
    for _ in range(n_new):
        st.session_state.shipments.append(generate_shipment(exception_prob=exc_prob))

if st.sidebar.button("Reset session telemetry", use_container_width=True):
    st.session_state.shipments = []
    st.session_state.diagnoses = {}

st.sidebar.divider()
st.sidebar.markdown(
    "**Stack:** Streamlit Community Cloud · Groq (open-weight, free tier) · "
    "Open-Meteo (live) · zero training, zero paid APIs."
)

# ---------------------------------------------------------------------------
# Tabs (Strictly Text Labels & SVG Badges — Zero Emojis)
# ---------------------------------------------------------------------------

tab_board, tab_investigate, tab_eval, tab_audit, tab_about = st.tabs(
    ["Live Board", "Investigate", "Evaluation", "Audit Log", "About"]
)

# --- Live Board -------------------------------------------------------------
with tab_board:
    st.subheader("Active shipments")

    if not st.session_state.shipments:
        st.info("Generate some shipment events from the sidebar to get started.")
    else:
        rows = []
        for ship in st.session_state.shipments:
            report = evaluate_shipment(ship)
            rows.append({
                "Shipment": ship.id,
                "Route": ship.route_name,
                "Current Hub": ship.current_hub,
                "Dwell (h)": report["dwell_hours_actual"],
                "Baseline (h)": report["dwell_hours_baseline_mean"],
                "Z-score": report["dwell_zscore"],
                "Flagged": "FLAGGED" if report["is_flagged"] else "NORMAL",
                "Priority score": compute_priority_score(report) if report["is_flagged"] else 0.0,
                "Investigated": "yes" if ship.id in st.session_state.diagnoses else "no",
            })
        df = pd.DataFrame(rows).sort_values("Priority score", ascending=False)
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.subheader("Network map")
        hub_df = pd.DataFrame(
            [{"hub": h, "lat": lat, "lon": lon} for h, (lat, lon) in HUBS.items()]
        )
        flagged_hubs = {r["Current Hub"] for r in rows if r["Flagged"] == "FLAGGED"}
        hub_df["status"] = hub_df["hub"].apply(lambda h: "flagged shipment here" if h in flagged_hubs else "normal")
        fig = px.scatter_mapbox(
            hub_df, lat="lat", lon="lon", color="status", text="hub",
            color_discrete_map={"flagged shipment here": "#e63946", "normal": "#457b9d"},
            zoom=3.6, height=450,
        )
        fig.update_layout(mapbox_style="open-street-map", margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)

# --- Investigate --------------------------------------------------------
with tab_investigate:
    st.subheader("Investigate a flagged shipment")

    flagged_ids = [
        s.id for s in st.session_state.shipments if evaluate_shipment(s)["is_flagged"]
    ]
    if not flagged_ids:
        st.info("No flagged shipments yet. Generate some events on the sidebar first "
                 "(try raising the exception probability slider).")
    else:
        chosen_id = st.selectbox("Flagged shipment", flagged_ids)
        ship = next(s for s in st.session_state.shipments if s.id == chosen_id)
        report = evaluate_shipment(ship)

        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown(f"**Route:** {ship.route_name}")
            st.markdown(f"**Current hub:** {ship.current_hub}")
            st.markdown(f"**Dwell:** {report['dwell_hours_actual']}h "
                        f"(baseline {report['dwell_hours_baseline_mean']}h, "
                        f"z={report['dwell_zscore']})")
        with col2:
            st.markdown(f"**Priority:** {ship.priority}")
            st.markdown(f"**Declared value:** ₹{ship.declared_value_inr:,.0f}")
            st.markdown(f"**Path:** {' → '.join(ship.path)}")

        if st.button("Run agent investigation", type="primary"):
            with st.spinner("Agent gathering evidence and reasoning..."):
                diagnosis = run_investigation(ship, report, mode="live")
                st.session_state.diagnoses[ship.id] = diagnosis
                audit.log_investigation(ship, report, diagnosis)

        if ship.id in st.session_state.diagnoses:
            d = st.session_state.diagnoses[ship.id]
            st.divider()
            st.markdown(f"### Diagnosis — engine: `{d['engine']}`")

            cause = d.get('primary_cause', 'unexplained')
            st.markdown(f"""
            <div style="margin-bottom: 12px;">
                <span style="font-weight: 600; margin-right: 8px;">Primary cause:</span>
                <span class="svg-badge badge-{cause}">
                    {cause.upper()}
                </span>
            </div>
            """, unsafe_allow_html=True)

            if d.get("contributing_causes"):
                st.markdown(f"**Contributing factors:** {', '.join(d['contributing_causes'])}")
            st.progress(min(d["confidence"], 1.0), text=f"Confidence: {d['confidence']:.0%}")
            st.progress(min(d["sla_risk_pct"] / 100, 1.0), text=f"Estimated SLA breach risk: {d['sla_risk_pct']}%")
            st.markdown(f"**Explanation:** {d['explanation']}")
            st.markdown(f"**Recommended action:** {d['recommended_action']}")

            with st.expander("Tool call evidence trace (for auditability)"):
                st.json(d.get("evidence", {}))

# --- Evaluation ----------------------------------------------------------
with tab_eval:
    st.subheader("Agent accuracy evaluation")
    st.caption(
        "Runs the full pipeline against simulated shipments with a hidden ground-truth "
        "cause, then checks whether the agent's stated primary cause matches. Uses "
        "simulated weather (not live) so results are reproducible run to run."
    )
    n_eval = st.slider("Shipments to simulate", 10, 50, 20)
    if st.button("Run evaluation batch"):
        with st.spinner("Simulating shipments and running the agent on flagged ones..."):
            results = run_evaluation(n_shipments=n_eval)
        st.metric("Top-1 cause accuracy", f"{results['top1_accuracy']:.0%}" if results['top1_accuracy'] is not None else "n/a")
        st.caption(f"{results['n_flagged']} of {results['n_generated']} simulated shipments were flagged as exceptions.")
        st.dataframe(pd.DataFrame(results["details"]), use_container_width=True, hide_index=True)

# --- Audit Log -------------------------------------------------------------
with tab_audit:
    st.subheader("Investigation audit log")
    st.caption("Every agent investigation is logged here with its diagnosis and confidence — "
               "the traceability layer a compliance-sensitive deployment would require.")
    log_rows = audit.fetch_log()
    if log_rows:
        st.dataframe(pd.DataFrame(log_rows), use_container_width=True, hide_index=True)
    else:
        st.info("No investigations logged yet this session.")
    if st.button("Clear audit log"):
        audit.clear_log()
        st.rerun()

# --- About -----------------------------------------------------------------
with tab_about:
    st.markdown("""
## BharatFlow AI — Shipment Exception & Root-Cause Intelligence

A trimmed, actually-deployable MVP of a larger control-tower design, built to
demonstrate senior-level AI engineering judgment rather than a sprawling
half-finished architecture.

**Pipeline:** deterministic statistical exception detection → agentic tool-calling
investigation (weather / compliance / congestion) → transparent, hand-specified
confidence & risk scoring → structured diagnosis → audit log.

**Design choices worth discussing in an interview:**
- Exception detection is pure statistics (z-scores vs. historical baselines) —
  no LLM in the hot path for every shipment, only for the ones actually flagged.
- The agent can call tools, but must finish with a structured `submit_diagnosis`
  call — no free-form, unparseable output.
- Confidence and SLA-risk are computed by hand-specified, inspectable formulas
  (see `scoring.py`), not invented by the LLM.
- The simulator intentionally does NOT give the agent clean 1:1 signal — causes
  are sometimes muted, sometimes multiple, sometimes genuinely absent — so the
  evaluation tab measures real inference, not lookup.
- Zero training, zero paid APIs: Groq's free tier serves open-weight models;
  Open-Meteo provides real live weather; compliance/congestion are
  clearly-labeled simulated integration points.

**Honest limitations:** compliance/congestion data is simulated (no free public
e-way bill API exists); the audit log is local SQLite and may not persist across
a Streamlit Cloud restart; this is a decision-support demo, not a production
system of record.
""")
