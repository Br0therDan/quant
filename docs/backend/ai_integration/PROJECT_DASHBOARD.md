# AI Integration Program Dashboard

## Overview
- **Program Sponsor:** Backend Platform & Quant Research Leads
- **Scope:** Embed machine learning and generative AI capabilities into the FastAPI-based strategy and backtest platform while preserving existing service-factory architecture.
- **Current Focus:** Deliver high-impact predictive intelligence and automated optimization features that leverage the enhanced Strategy & Backtest stack before scaling into generative UX and platform-wide MLOps.

## Phase Timeline Snapshot
| Phase | Title | Target Start | Target Finish | Health | Key Outcomes |
| ----- | ----- | ------------ | ------------- | ------ | ------------ |
| 1 | Predictive Intelligence Foundations | 2025-01-06 | 2025-02-14 | 🟢 On Track | ML signal API, regime detection service, probabilistic KPI forecasts |
| 2 | Automation & Optimization Loop | 2025-02-17 | 2025-03-28 | 🟡 At Risk | Backtest optimizer endpoint, RL executor prototype, data QA guardrails |
| 3 | Generative Insights & ChatOps | 2025-03-31 | 2025-05-09 | 🟢 Planned | Narrative report service, conversational strategy builder, Ops co-pilot |
| 4 | MLOps Platform Enablement | 2025-05-12 | 2025-06-20 | 🔵 Planning | Feature store governance, model registry, evaluation harness |

## Prioritized Backlog
| Rank | Epic | Deliverable | Dependency | Phase | Status |
| ---- | ---- | ----------- | ---------- | ----- | ------ |
| 1 | ML Signal Service | DuckDB feature pipeline & LightGBM scoring endpoint | MarketDataService cache, Strategy backtest orchestration | Phase 1 | In Progress |
| 2 | Regime Classification | `/market-data/regime` API with MongoDB regime cache | DuckDB refresh pipeline | Phase 1 | Planned |
| 3 | Portfolio Probabilistic KPIs | Forecast API returning percentile bands | PortfolioService performance aggregation | Phase 1 | Planned |
| 4 | Optuna Backtest Optimizer | `/backtests/optimize` orchestration with study persistence | BacktestService orchestration, DuckDB metrics | Phase 2 | Planned |
| 5 | Reinforcement Learning Executor | `RLEngine` integration with TradingSimulator | Optimizer telemetry, MarketDataService signals | Phase 2 | Blocked (compute sizing) |
| 6 | Data Quality Sentinel | Isolation Forest anomaly alerts surfaced via DashboardService | MarketData ingest jobs | Phase 2 | Planned |
| 7 | Narrative Report Generator | `/backtests/{id}/report` LLM service with guardrails | Phase 1 KPI outputs | Phase 3 | Planned |
| 8 | Conversational Strategy Builder | Generative builder route translating NL to strategy config | StrategyService templates, embeddings store | Phase 3 | Planned |
| 9 | ChatOps Operations Agent | Tool-enabled LLM for cache and pipeline health | Data quality sentinel, health check APIs | Phase 3 | Planned |
| 10 | Feature Store Launch | Versioned DuckDB views for ML reuse | DuckDB governance, anomaly flags | Phase 4 | Planned |
| 11 | Model Lifecycle Management | MLflow/W&B integration with MongoDB metadata | Feature store, optimizer outputs | Phase 4 | Planned |
| 12 | Evaluation Harness | Benchmark suites with explainability capture | Backtest results schema | Phase 4 | Planned |

## Milestone Progress
- **M1 – Feature Engineering Blueprint (2025-01-24):** Draft the DuckDB feature store schema, mapping to BacktestService inputs. _Status: On Track_
- **M2 – ML Signal API GA (2025-02-14):** Expose probability scores via ServiceFactory and integrate with strategy execution. _Status: On Track_
- **M3 – Optimization API Beta (2025-03-21):** Complete Optuna orchestration and persistence. _Status: At Risk_
- **M4 – Generative Insights MVP (2025-04-25):** Deliver automated narrative reports and conversational builder. _Status: Planned_
- **M5 – MLOps Platform Launch (2025-06-20):** Enable feature store, model registry, evaluation harness. _Status: Planned_

## Key Risks & Mitigations
| Risk | Impact | Likelihood | Mitigation |
| ---- | ------ | ---------- | ---------- |
| Compute constraints for RL and forecasting workloads | Delivery delays for Phase 2 RL executor | Medium | Prototype using sampled symbols; plan GPU burst capacity and checkpoint offloading |
| Data drift across Alpha Vantage feeds | Reduces accuracy of ML signals | High | Implement anomaly sentinel and rolling retraining cadence tied to DuckDB refreshes |
| LLM hallucination in narrative reports | Lowers trust in insights | Medium | Enforce structured prompts, Pydantic validation, and fact cross-check against KPI store |
| ServiceFactory coupling complexity | Slows integration of new services | Low | Standardize service registration templates and align with existing Strategy/Backtest architecture |

## Reporting Cadence
- **Standups:** Twice weekly with Strategy & Backtest engineering.
- **Steering Updates:** Bi-weekly slides including KPI deltas and risk log.
- **Artifacts:** Phase plans (see `/docs/backend/ai_integration/phase*`), backlog board synced with this dashboard, architecture diagrams referencing Strategy & Backtest docs.
