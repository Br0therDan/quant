# Phase 1 Plan – Predictive Intelligence Foundations

## 1. Executive Summary
- **Objective:** Deliver production-grade predictive services (ML signals, regime classification, probabilistic KPI forecasts) that plug into the enhanced Strategy & Backtest workflow without disrupting existing FastAPI routes.
- **Business Value:** Improves trade timing confidence and portfolio risk visibility for quant traders and investors, enabling better scenario planning based on Strategy & Backtest outputs.
- **Timeframe:** 6 weeks (2025-01-06 → 2025-02-14).

## 2. Scope & Deliverables
| ID | Deliverable | Description | Acceptance Criteria |
| -- | ----------- | ----------- | ------------------- |
| D1 | ML Signal Service | ServiceFactory-registered `MLSignalService` scoring endpoints using LightGBM/CatBoost models fed by DuckDB features. | - DuckDB feature pipeline documented<br>- `/signals/{symbol}` route returns probability & feature attribution<br>- BacktestService consumes signal scores in orchestrator |
| D2 | Regime Detection API | Regime classification workflow with MongoDB persistence and `/market-data/regime` route. | - Batch job updates regime labels daily<br>- DashboardService exposes regime metadata alongside KPI panels |
| D3 | Probabilistic KPI Forecast | PortfolioService integration with inference engine returning percentile forecasts. | - Forecast endpoint supplies 5/50/95 percentile equity projections<br>- DuckDB stores historical forecast evaluations |

### Out of Scope
- Reinforcement learning executors (Phase 2).
- LLM narrative generation (Phase 3).
- MLflow deployment automation (Phase 4).

## 3. Workstreams & Backlog Mapping
| Workstream | Backlog Items | Notes |
| ---------- | ------------- | ----- |
| Feature Engineering | D1, D2 | Extend DuckDB feature store aligned with Strategy & Backtest architecture diagrams.【F:docs/backend/strategy_backtest/ARCHITECTURE.md†L1-L120】 |
| Model Development | D1, D3 | Train gradient boosting classifiers and forecasting models using historical Alpha Vantage data via MarketDataService integrations.【F:docs/backend/ai_integration/master_plan.md†L13-L46】【F:docs/backend/ai_integration/master_plan.md†L47-L82】 |
| Service Integration | D1, D2, D3 | Register new services in ServiceFactory and integrate with BacktestService orchestrator flows.【F:docs/backend/strategy_backtest/ARCHITECTURE.md†L1-L87】 |
| Analytics Enablement | D2, D3 | Surface new metrics within DashboardService for analyst consumption.【F:docs/backend/ai_integration/master_plan.md†L47-L82】 |

## 4. Milestones
| Milestone | Date | Owner | Exit Criteria |
| --------- | ---- | ----- | ------------- |
| M1: Feature Spec Sign-off | 2025-01-10 | Data Engineering | Approved feature list and DuckDB schema updates |
| M2: Model Training Complete | 2025-01-24 | Quant Research | Cross-validated metrics documented; models stored in artifact repo |
| M3: API Integration Review | 2025-02-05 | Backend Team | Routes deployed to staging; ServiceFactory registry updated |
| M4: Phase Demo | 2025-02-14 | Product | Live demo showing BacktestService consuming signals and displaying forecasts |

## 5. Dependencies & Interfaces
- **Strategy & Backtest Stack:** Uses Orchestrator and DatabaseManager pipelines for data retrieval and results persistence.【F:docs/backend/strategy_backtest/ARCHITECTURE.md†L33-L108】
- **Market Data Refresh Jobs:** Required for timely feature computation and anomaly handling.
- **DuckDB Cache & MongoDB:** Persistence layers for features, regimes, and forecasts.
- **Analytics Dashboard:** Consumers of regime metadata and probabilistic KPIs.

## 6. Risks & Mitigations
| Risk | Impact | Likelihood | Response |
| ---- | ------ | ---------- | -------- |
| Data gaps in Alpha Vantage feeds | Delays model training and reduces accuracy | Medium | Implement anomaly detection hooks per master plan Section 3.3 as pre-processing guardrails.【F:docs/backend/ai_integration/master_plan.md†L109-L132】 |
| Model latency impacting Backtest runtime | Medium | Low | Cache model artifacts in memory; pre-compute features during nightly jobs. |
| Integration complexity with existing orchestrator | Medium | Medium | Align service contracts with Strategy & Backtest diagrams; schedule integration pairing sessions. |

## 7. Metrics & Reporting
- **Leading Indicators:** Model AUC/accuracy, feature pipeline SLA, regime refresh latency.
- **Lagging Indicators:** Backtest Sharpe delta vs baseline, portfolio VaR coverage vs realized drawdown.
- **Quality Gates:** Automated tests covering ServiceFactory registration, API contract tests, forecast calibration checks.

## 8. Resource Plan
| Role | Allocation | Notes |
| ---- | ---------- | ----- |
| Backend Engineer | 1.5 FTE | Focus on API integration and ServiceFactory updates |
| Data Engineer | 1 FTE | Feature pipeline and DuckDB orchestration |
| Quant Researcher | 1 FTE | Model development and validation |
| Product Analyst | 0.5 FTE | KPI definition, dashboard validation |

## 9. Communication Cadence
- Weekly sprint reviews aligned with Strategy & Backtest squads.
- Mid-phase architecture review to ensure compatibility with orchestrator and DatabaseManager components.

## 10. Exit Criteria
- All deliverables accepted in staging with automated regression tests.
- Documentation updated in repo (feature specs, API schemas, runbooks).
- Handover checklist signed by Strategy & Backtest owners.
