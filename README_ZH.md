<div align="center">

# BharatFlow AI
### 自主物流异常与根因智能诊断平台

**确定性统计异常检测 | 多工具自主智能体推理 | SLA 风险优先级评分**

[ **English**](./README.md) · [ **हिन्दी (Hindi)**](./README_HI.md) · [ **Español (Spanish)**](./README_ES.md) · [ **简体中文 (Chinese)** ]

<br/>

[![Live Production Demo](https://img.shields.io/badge/Live%20Demo-bharatflow--ai-00b894?style=for-the-badge&logo=render&logoColor=white)](https://bharatflow-ai-nvbz.onrender.com)
[![GitHub Stars](https://img.shields.io/github/stars/az-cod/Bharatflow-AI?style=for-the-badge&logo=github)](https://github.com/az-cod/Bharatflow-AI)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Architecture](https://img.shields.io/badge/Architecture-Event--Driven%20%7C%20REST-orange?style=for-the-badge)](https://bharatflow-ai-nvbz.onrender.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

</div>

---

## 多语言导航 / Language Selection

| 语言 (Language) | 文档 (Document) | 描述 (Description) |
|---|---|---|
| **English** | [**README.md**](./README.md) | 官方英文技术架构文档与使用指南。 |
| **हिन्दी (Hindi)** | [**README_HI.md**](./README_HI.md) | 印地语官方技术文档。 |
| **Español** | [**README_ES.md**](./README_ES.md) | 西班牙语技术文档。 |
| **简体中文** | [**README_ZH.md**](./README_ZH.md) | 简体中文官方技术架构说明及部署指南。 |

---

## 项目简介 (Overview)

BharatFlow AI 是一套面向高吞吐量干线物流（涵盖德里、孟买、班加罗尔、浦那、海得拉巴与斋浦尔等印度关键枢纽）的企业级智能物流异常处理与根因诊断系统。

针对传统物流调度中的告警疲劳与人工排查缓慢的问题，本系统采用双层混合架构：
1. 轻量统计过滤层：通过 $Z$-Score 离群值算法 ($Z = \frac{x - \mu}{\sigma}$) 以亚毫秒级速度处理全量正常货件，完全避开大语言模型调用成本。
2. 自主多工具推理层：仅当检测到显著异常 ($> 2.0\sigma$) 时，触发自主智能体 (`qwen/qwen3.8-27b`) 并行调用气象（Open-Meteo 实时遥测）、枢纽堆存拥堵率、电子运单合规等多源外部工具，输出具备可信度评分与具体处理建议的结构化诊断报告。

零成本硬约束：全栈构建于开源与免费基础之上，无需任何模型微调训练，无需任何付费商业 API。

---

## 线上正式部署访问

- 全球线上 Web 应用: https://bharatflow-ai-nvbz.onrender.com
- API 健康检查接口: https://bharatflow-ai-nvbz.onrender.com/api/status

---

## 全链路流水线架构 (Pipeline Architecture)

```
                    ┌───────────────────────────────────┐
                    │       模拟实时遥测数据流流式输入    │
                    │   (GPS 定位、滞留时长、运输节点)   │
                    └─────────────────┬─────────────────┘
                                      │
                                      ▼
                    ┌───────────────────────────────────┐
                    │ 确定性统计异常初筛 (Statistical)   │
                    │    (Z-Score > 2.0σ 对比历史基线)   │
                    └───────┬───────────────────┬───────┘
                            │                   │
                     [正常流 (< 2σ)]            │ [异常告警 (> 2σ)]
                            │                   ▼
                            ▼       ┌───────────────────────────────────┐
                    ┌───────────────┤ 自主多工具 AI 智能体 (Agent)       │
                    │ 瞬间直接放行   │ • get_weather (实时天气遥测)      │
                    │ (零 LLM 成本) │ • get_hub_congestion (枢纽拥堵)   │
                    └───────────────┤ • get_compliance_status (运单合规)│
                                    └─────────────────┬─────────────────┘
                                                      │
                                                      ▼
                                    ┌───────────────────────────────────┐
                                    │ 公式化评分与优先级引擎            │
                                    │ • 数学透明置信度公式              │
                                    │ • SLA 风险评分: 货值 × 延误时长²   │
                                    └─────────────────┬─────────────────┘
                                                      │
                                                      ▼
                                    ┌───────────────────────────────────┐
                                    │ 结构化诊断与不可变审计日志        │
                                    │ (根因归因、处置方案建议、SQLite)   │
                                    └───────────────────────────────────┘
```

---

## 核心工程亮点

1. 确定性统计初筛：将大模型移出高频主干热路径，保障 80% 以上的正常物流包裹零延迟即时通过。
2. 高并发基准测试靶场：通过多线程 ThreadPoolExecutor(max_workers=3) 执行基准测评，在 12 秒内达成 100% Top-1 真实根因命中率。
3. DHL 工业级无 Emoji 前端设计：严格遵循 60-30-10 配色法则（白/浅灰 `#FFFFFF`/`#F4F4F4`、石墨深板岩 `#242832`、经典 DHL 红色 `#D40511` 与黄色 `#FFCC00`），全面采用原生 SVG 矢量图标。
4. 确定性规则回退机制：在无网络、无 API Key 或触发速率限制时，系统自动无缝切换至纯规则推理引擎，确保服务永不崩溃中断。

---

## 本地运行与配置指南

```bash
git clone https://github.com/az-cod/Bharatflow-AI.git
cd Bharatflow-AI
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python server.py 8000
```

---

## 开源许可证

本项目基于 [MIT License](./LICENSE) 协议完全开源。
