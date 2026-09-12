# BharatFlow AI — Shipment Exception & Root-Cause Intelligence

A live, working MVP of an agentic AI system for logistics exception handling,
built around Indian shipment corridors (Delhi, Mumbai, Bengaluru, Jaipur, and
others). Deterministic statistical exception detection feeds an LLM agent that
investigates using real and simulated tools, produces a confidence-scored
root-cause diagnosis, and logs everything to an audit trail.

**Built with a hard constraint: zero model training, zero paid APIs.**

## Why this exists

Most "AI agent" portfolio projects either (a) never leave a Jupyter notebook,
or (b) sprawl into an architecture diagram that's 20% implemented. This is
the trimmed, actually-deployable slice of a larger design — every box in the
pipeline below is real, working code, not a diagram.

## Pipeline

```
Simulated shipment stream
        │
        ▼
Deterministic exception detection (statistics vs. historical baselines)
        │  (only flagged shipments proceed — LLM is never in the hot path)
        ▼
Agentic investigation (LLM decides which tools to call: weather / compliance / congestion)
        │
        ▼
Transparent confidence & SLA-risk scoring (hand-specified formulas, not LLM-invented)
        │
        ▼
Structured diagnosis (primary cause, contributing factors, explanation, recommended action)
        │
        ▼
Audit log (every investigation traceable)
```

A separate **evaluation harness** runs the same pipeline against simulated
shipments with a hidden ground-truth cause and reports top-1 accuracy — so
there's a real number behind "the agent works," not just good-looking demo
output.

## Zero-cost stack

| Layer | Choice | Cost |
|---|---|---|
| Hosting | Streamlit Community Cloud | Free |
| LLM reasoning | Groq API, Llama 3.3 (open-weight, no training) | Free tier |
| Live weather | Open-Meteo | Free, no key |
| Compliance / congestion signals | Simulated (documented integration points) | N/A |
| Audit log | Local SQLite | Free |

No credit card is required anywhere in this stack.

## Design decisions worth defending in an interview

- **Detection is pure statistics, not an LLM call.** Every shipment gets a
  cheap z-score check; the LLM only runs on the subset that's actually
  flagged. This is a deliberate cost/latency/determinism choice.
- **The agent must finish with a structured tool call** (`submit_diagnosis`),
  never free-form text — this removes an entire class of "now how do I parse
  this" bugs.
- **Confidence and SLA-risk are computed by named, inspectable formulas**
  (see `scoring.py`), not asked of the LLM. The LLM explains and prioritizes;
  it doesn't invent the numbers a downstream system would act on.
- **The simulator intentionally breaks the 1:1 cause→signal mapping.**
  ~15% of delays have no clean cause, ~20% of true causes are "muted" in the
  tool reading, and some shipments have multiple contributing causes. This
  matters: without it, the agent would just be doing lookup, not inference,
  and the evaluation number would be meaningless.
- **Rule-based fallback.** If no API key is set, or the LLM call fails for
  any reason (rate limit, network hiccup), the app falls back to a
  deterministic diagnosis using the same evidence — the demo never just
  crashes for a visitor.

## Honest limitations

- Compliance and hub-congestion data are **simulated** — no free public
  e-way bill or hub WMS API exists to integrate with. This is called out
  explicitly in the UI, not hidden.
- The audit log is local SQLite; Streamlit Community Cloud does not guarantee
  disk persistence across app restarts/sleeps. Fine for a demo; a real
  deployment would use a hosted Postgres (e.g. Supabase's free tier is a
  drop-in swap).
- This is a decision-support demo, not a system of record — no shipment here
  is real.

## Running locally

```bash
git clone <your-repo-url>
cd bharatflow-ai
python -m venv venv && source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt

cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# edit .streamlit/secrets.toml and paste in a free Groq API key from https://console.groq.com

streamlit run app.py
```

The app also runs without a Groq key — it just uses the rule-based fallback
engine instead of the LLM (sidebar will show a warning).

## Deploying live (for your resume link)

1. Push this folder to a **public GitHub repo**.
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub.
3. Click **New app**, pick your repo/branch, set the main file to `app.py`.
4. Before or after deploying, open **App settings → Secrets** and paste:
   ```toml
   GROQ_API_KEY = "your-groq-api-key-here"
   ```
5. Get a free Groq key (no credit card) at [console.groq.com](https://console.groq.com).
6. Your app will be live at `https://<your-app-name>.streamlit.app` — that's
   your resume link.

**Note:** free Community Cloud apps sleep after ~12 hours of no traffic and
take ~10–20 seconds to wake up on the next visit. This is normal — if a
recruiter's first load looks slow, that's why.

## Project structure

```
bharatflow-ai/
├── app.py              # Streamlit UI (all tabs)
├── data_generator.py   # synthetic India hub/route network + shipment generator
├── detection.py        # deterministic statistical exception detection
├── scoring.py          # transparent confidence / risk formulas
├── tools.py            # weather (live Open-Meteo) / compliance / congestion tools
├── agent.py            # Groq-based agentic tool-calling loop + rule-based fallback
├── evaluation.py        # accuracy evaluation harness against hidden ground truth
├── audit.py             # SQLite audit log
├── requirements.txt
├── .streamlit/secrets.toml.example
└── README.md
```

## Roadmap (explicitly out of scope for this MVP, by design)

- Real streaming ingestion (Kafka/Redpanda) in place of the in-app simulator
- Real e-way bill / customs API integration in place of simulated compliance
- Hosted Postgres for durable audit history across restarts
- A digital-twin network graph view with corridor-level risk propagation
