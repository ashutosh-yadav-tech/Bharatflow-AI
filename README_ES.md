<div align="center">

# 📦 BharatFlow AI
### Plataforma Autónoma de Inteligencia de Excepciones de Carga y Causa Raíz

**Detección Estadística Determinista • Razonamiento Autónomo Multi-Herramienta • Priorización de Riesgo SLA**

[ **English**](./README.md) · [ **हिन्दी (Hindi)**](./README_HI.md) · [ **Español (Spanish)** ] · [ **简体中文 (Chinese)**](./README_ZH.md)

<br/>

[![Live Production Demo](https://img.shields.io/badge/Live%20Demo-bharatflow--ai-00b894?style=for-the-badge&logo=render&logoColor=white)](https://bharatflow-ai-nvbz.onrender.com)
[![GitHub Stars](https://img.shields.io/github/stars/az-cod/Bharatflow-AI?style=for-the-badge&logo=github)](https://github.com/az-cod/Bharatflow-AI)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Architecture](https://img.shields.io/badge/Architecture-Event--Driven%20%7C%20REST-orange?style=for-the-badge)](https://bharatflow-ai-nvbz.onrender.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

</div>

---

## 🌐 Navegación de Idiomas / Language Selection

| Idioma (Language) | Documento (Document) | Descripción (Description) |
|---|---|---|
| **English** | [**README.md**](./README.md) | Documentación técnica oficial y guía de arquitectura. |
| **हिन्दी (Hindi)** | [**README_HI.md**](./README_HI.md) | Guía técnica completa en Hindi. |
| **Español** | [**README_ES.md**](./README_ES.md) | Documentación completa en Español y guía de despliegue. |
| **简体中文** | [**README_ZH.md**](./README_ZH.md) | Documentación técnica en Chino Simplificado. |

---

## 📖 Descripción General

**BharatFlow AI** es una plataforma de operaciones logísticas impulsada por agentes autónomos de Inteligencia Artificial, diseñada para el triaje y diagnóstico de excepciones de transporte en los corredores logísticos más transitados de la India (Delhi, Mumbai, Bengaluru, Pune, Hyderabad y Jaipur).

El sistema mitiga la **fatiga por alertas** mediante un diseño híbrido de dos capas:
1. **Filtrado Estadístico Rápido ($Z\text{-score}$)**: Analiza el 100% de los envíos con latencia inferior a un milisegundo sin incurrir en costos de inferencia LLM.
2. **Agente Autónomo de Razonamiento (`qwen/qwen3.8-27b`)**: Interroga herramientas sensoriales en tiempo real (meteorología en vivo vía Open-Meteo, congestión portuaria/hub, y validación tributaria y de aduanas E-Way Bill) únicamente cuando se confirma una anomalía estadística ($> 2.0\sigma$).

> **Restricción de Costo Cero**: Construido sin entrenamiento de modelos y **sin APIs de pago** (100% de uso de capas gratuitas).

---

## 🚀 Despliegue en Producción

- **Aplicación Web Global**: [https://bharatflow-ai-nvbz.onrender.com](https://bharatflow-ai-nvbz.onrender.com)
- **Endpoint de Estado**: [https://bharatflow-ai-nvbz.onrender.com/api/status](https://bharatflow-ai-nvbz.onrender.com/api/status)

---

## 🏗️ Arquitectura del Sistema

```
                    ┌───────────────────────────────────┐
                    │     Flujo Telemétrico Simulado    │
                    │ (GPS, Tiempos de Espera, Paradas) │
                    └─────────────────┬─────────────────┘
                                      │
                                      ▼
                    ┌───────────────────────────────────┐
                    │  Detección Estadística de Desvío  │
                    │   (Z-Score > 2.0σ vs Histórico)   │
                    └───────┬───────────────────┬───────┘
                            │                   │
                     [Envío Normal]             │ [Anomalía Confirmada]
                            │                   ▼
                            ▼       ┌───────────────────────────────────┐
                    ┌───────────────┤ Agente Autónomo Multi-Herramienta │
                    │ Aprobación    │ • get_weather (Open-Meteo en vivo)│
                    │ Inmediata     │ • get_hub_congestion (Telemetría) │
                    │ ($0 LLM)      │ • get_compliance_status (E-Way)   │
                    └───────────────┴─────────────────┬─────────────────┘
                                                      │
                                                      ▼
                                    ┌───────────────────────────────────┐
                                    │ Motor de Puntuación Transparente  │
                                    │ • Confianza Matemática Fórmulada  │
                                    │ • Prioridad: Valor × Demora²      │
                                    └─────────────────┬─────────────────┘
                                                      │
                                                      ▼
                                    ┌───────────────────────────────────┐
                                    │ Registro de Diagnóstico y Auditoría│
                                    │ (Causa Raíz, Acción Recomendada)  │
                                    └───────────────────────────────────┘
```

---

## ⚙️ Puntos Clave de Ingeniería

1. **Eficiencia de Coste y Latencia**: El modelo LLM nunca se sitúa en la ruta de alta frecuencia. Más del 80% de los paquetes normales pasan instantáneamente.
2. **Evaluación Concurrente**: Arnés de pruebas con `ThreadPoolExecutor(max_workers=3)` que valida el 100% de precisión Top-1 en menos de 15 segundos.
3. **Diseño Visual DHL (Sin Emojis)**: Paleta corporativa balanceada 60-30-10 (`#FFFFFF`, `#242832`, `#D40511`, `#FFCC00`) con gráficos vectoriales SVG 100% nativos.

---

## 🛠️ Ejecución Local

```bash
# 1. Clonar el repositorio
git clone https://github.com/az-cod/Bharatflow-AI.git
cd Bharatflow-AI

# 2. Configurar entorno virtual
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux / macOS:
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Iniciar el servidor
python server.py 8000
# Abrir en el navegador: http://localhost:8000
```

---

## 📄 Licencia

Este proyecto es software de código abierto bajo la licencia [MIT](./LICENSE).
