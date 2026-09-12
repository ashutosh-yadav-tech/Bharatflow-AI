<div align="center">

# BharatFlow AI
### Autonomous Freight Exception & Root-Cause Intelligence Platform

**Deterministic Statistical Anomaly Detection | Agentic Multi-Tool Reasoning | SLA-Risk Prioritization**

[ **English** ] · [ **हिन्दी (Hindi)**](./README_HI.md) · [ **Español (Spanish)**](./README_ES.md) · [ **简体中文 (Chinese)**](./README_ZH.md)

<br/>

[![Live Production Demo](https://img.shields.io/badge/Live%20Demo-bharatflow--ai-00b894?style=for-the-badge&logo=render&logoColor=white)](https://bharatflow-ai-nvbz.onrender.com)
[![GitHub Stars](https://img.shields.io/github/stars/az-cod/Bharatflow-AI?style=for-the-badge&logo=github)](https://github.com/az-cod/Bharatflow-AI)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Architecture](https://img.shields.io/badge/Architecture-Event--Driven%20%7C%20REST-orange?style=for-the-badge)](https://bharatflow-ai-nvbz.onrender.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

</div>

---

## Language Navigation / भाषा विकल्प / Opciones de Idioma / 语言选项

| Language | Document | Description |
|---|---|---|
| **English** | [**README.md**](./README.md) | Official English documentation and architecture guide. |
| **हिन्दी (Hindi)** | [**README_HI.md**](./README_HI.md) | संपूर्ण हिन्दी तकनीकी दस्तावेज़ एवं उपयोग मार्गदर्शिका। |
| **Español** | [**README_ES.md**](./README_ES.md) | Documentación técnica en Español y guía de arquitectura. |
| **简体中文** | [**README_ZH.md**](./README_ZH.md) | 官方简体中文技术架构文档与快速上手指南。 |

---

## Overview

BharatFlow AI is an enterprise-grade agentic AI operations platform designed for freight exception handling and root-cause intelligence across high-volume Indian logistics corridors including Delhi, Mumbai, Bengaluru, Pune, Hyderabad, and Jaipur.

The platform resolves operational vulnerability in freight networks: alert fatigue and delayed exception triage. By coupling deterministic statistical z-score detection with an autonomous LLM reasoning agent (`qwen/qwen3.8-27b`), BharatFlow AI processes nominal shipments at sub-millisecond speeds, while autonomously diagnosing anomalies using real-time atmospheric, telematics, and compliance signals.

Zero-Cost Architecture: Built with zero model training requirements and zero paid APIs.

---

## Live Production Deployment

- Global Web Application: https://bharatflow-ai-nvbz.onrender.com
- API Status Healthcheck: https://bharatflow-ai-nvbz.onrender.com/api/status

---

## End-to-End Pipeline Architecture

```
                    ┌───────────────────────────────────┐
                    │     Simulated Telemetry Stream    │
                    │   (GPS, Dwell Times, Transit Hops)│
                    └─────────────────┬─────────────────┘
                                      │
                                      ▼
                    ┌───────────────────────────────────┐
                    │ Deterministic Anomaly Detection   │
                    │ (Z-Score > 2.0σ vs Hub Baselines) │
                    └───────┬───────────────────┬───────┘
                            │                   │
                 [Nominal Stream (< 2σ)]        │ [Flagged Exception (> 2σ)]
                            │                   ▼
                            ▼       ┌───────────────────────────────────┐
                    ┌───────────────┤ Autonomous Multi-Tool Agent       │
                    │ Instant Pass  │ • get_weather (Live Open-Meteo)   │
                    │ (Zero LLM $)  │ • get_hub_congestion (Telematics) │
                    └───────────────┤ • get_compliance_status (E-Way)   │
                                    └─────────────────┬─────────────────┘
                                                      │
                                                      ▼
                                    ┌───────────────────────────────────┐
                                    │ Formulaic Scoring Engine          │
                                    │ • Transparent Confidence Formula  │
                                    │ • Priority Score: Value × Delay²  │
                                    └─────────────────┬─────────────────┘
                                                      │
                                                      ▼
                                    ┌───────────────────────────────────┐
                                    │ Structured Diagnostic Record      │
                                    │ (Root Cause, Action, Audit Trail) │
                                    └───────────────────────────────────┘
```

---

## Key Architectural Highlights

### 1. Deterministic Detection (Statistical Filtering)
The LLM is never in the high-frequency hot path. Over 80% of logistics telemetry is nominal. Every shipment undergoes statistical z-score verification against rolling corridor baselines ($Z = \frac{x - \mu}{\sigma}$). Only deviations exceeding $2.0\sigma$ trigger agentic investigation, drastically reducing inference costs and eliminating latency spikes.

### 2. Autonomous Multi-Tool Investigation
When an anomaly is flagged, the agent dynamically interrogates external sensory tools in parallel:
- `get_weather`: Direct integration with Open-Meteo API for real-time wind speed, precipitation, and storm alerts across GPS coordinates.
- `get_hub_congestion`: Yard dwell density and dock turnaround times.
- `get_compliance_status`: E-way bill validity, GSTIN compliance, and verification checkpoints.

### 3. Concurrency-Engineered Benchmark Lab
Includes a standardized evaluation harness ([`evaluation.py`](./evaluation.py)) validating agent accuracy against hidden ground-truth causes. Powered by a multi-threaded `ThreadPoolExecutor(max_workers=3)`, it achieves 100% Top-1 Attribution Accuracy in ~12 seconds without triggering API rate limits.

### 4. Zero-Emoji Enterprise DHL Design System
The frontend ([`web/`](./web)) implements a professional design system adhering to the 60-30-10 Rule:
- 60% Neutral Canvas: `#FFFFFF` main background with `#F4F4F4` elevated section separation.
- 30% Structure & Headers: `#242832` graphite slate sidebar with `#111111` typography.
- 10% Brand Accents: High-contrast DHL Red (`#D40511`) for primary calls to action, and DHL Yellow (`#FFCC00`) for active states.
- Pure SVG Icons: 100% custom inline vector graphics with zero emojis.

---

## Zero-Cost Tech Stack

| Component | Technology | Cost / License |
|---|---|---|
| **Runtime & Server** | Python 3.10+, Standard `http.server`, Threading | Open-Source |
| **Frontend UI** | HTML5, Vanilla CSS3, JavaScript (ES6+), Clean SVGs | Native / Zero Framework Overhead |
| **LLM Inference** | Groq Cloud (`qwen/qwen3.8-27b` / `llama-3.3-70b-versatile`) | Free Tier (30 RPM) |
| **Weather Telemetry** | Open-Meteo API | Free / No API Key Required |
| **Audit Ledger** | SQLite with ACID Transaction Logging | Free / Local Embedded |
| **Cloud Hosting** | Render Free Web Service (`render.yaml`) | Free ($0/month) |

---

## REST API Documentation

The backend exposes a lightweight, zero-dependency REST API:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/status` | Healthcheck, model configuration, hub coordinates, and route metadata. |
| `GET` | `/api/shipments` | Returns all active corridor shipments with z-scores and exception flags. |
| `POST` | `/api/generate` | Ingests a new synthetic telemetry cohort across active Indian corridors. |
| `POST` | `/api/investigate` | Dispatches the autonomous LLM agent for structured root-cause analysis on a shipment. |
| `POST` | `/api/evaluate` | Runs the multi-threaded benchmark harness against hidden ground-truth datasets. |
| `GET` | `/api/audit` | Retrieves the immutable audit log of all investigative decisions. |
| `POST` | `/api/audit/clear`| Resets the investigative audit trail. |

---

## Local Development & Setup

### Prerequisites
- Python 3.10 or higher
- Git

### 1. Clone Repository
```bash
git clone https://github.com/az-cod/Bharatflow-AI.git
cd Bharatflow-AI
```

### 2. Environment Configuration
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. API Key Setup (Optional for LLM Mode)
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```
```toml
GROQ_API_KEY = "gsk_your_groq_api_key_here"
```

### 4. Run the Application

- Modern Web Application:
  ```bash
  python server.py 8000
  ```

- Streamlit Interface:
  ```bash
  streamlit run app.py
  ```

---

## Cloud Deployment Guide

### Deploying to Render
1. Push this repository to your GitHub account.
2. Navigate to dashboard.render.com and select New Web Service.
3. Select the repository.
4. Render automatically processes [`render.yaml`](./render.yaml):
   - Environment: Python 3
   - Plan: Free
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python server.py`
5. Optional environment variable: `GROQ_API_KEY`.
6. Click Deploy Web Service.

---

## License

This project is open-source software licensed under the [MIT License](./LICENSE).
