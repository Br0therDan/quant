# Phase 2 Plan – Automation & Optimization Loop

## 1. Executive Summary
- **Objective:** Automate strategy optimization and data quality enforcement by embedding Optuna-driven tuning, reinforcement learning experimentation, and anomaly detection into the backtest ecosystem.
- **Business Value:** Accelerates strategy iteration cycles, adapts to evolving regimes, and protects model integrity through proactive data checks.
- **Timeframe:** 6 weeks (2025-02-17 → 2025-03-28).

## 2. Scope & Deliverables
| ID | Deliverable | Description | Acceptance Criteria |
| -- | ----------- | ----------- | ------------------- |
| D1 | Backtest Optimizer API | `/backtests/optimize` endpoint orchestrating Optuna/Hyperopt studies against BacktestService. | - Async execution pipeline with progress callbacks<br>- Persisted study metadata in MongoDB<br>- Dashboard leaderboard of top trials |
| D2 | Reinforcement Learning Executor | `RLEngine` interfacing with TradingSimulator via OpenAI Gym semantics for RL policy evaluation. | - Training loop with Stable-Baselines3 integration<br>- Policy playback via BacktestService for deterministic evaluation<br>- Resource usage guardrails documented |
| D3 | Data Quality Sentinel | Online anomaly detection integrated into MarketDataService ingestion with alert surfacing. | - Isolation Forest/Prophet scores stored with market data<br>- DashboardService exposes anomaly counts & severity<br>- Alerting webhook for critical issues |

### Out of Scope
- Production deployment of RL agent to live trading.
- Feature store governance (Phase 4).

## 3. Workstreams & Backlog Mapping
| Workstream | Backlog Items | Notes |
| ---------- | ------------- | ----- |
| Optimization Framework | D1 | Align optimization loop with BacktestService execution order and persistence patterns from Strategy & Backtest architecture.【F:docs/backend/strategy_backtest/ARCHITECTURE.md†L49-L87】 |
| RL Experimentation | D2 | Extend TradingSimulator to expose step/reset for RL per master plan Section 3.2.【F:docs/backend/ai_integration/master_plan.md†L89-L108】 |
| Data Quality & Monitoring | D3 | Implement anomaly scoring pipeline per master plan Section 3.3 with outputs feeding DashboardService.【F:docs/backend/ai_integration/master_plan.md†L109-L132】 |
| Platform Integration | D1, D2, D3 | Ensure ServiceFactory registrations, orchestrator hooks, and telemetry align with Strategy & Backtest workflows.【F:docs/backend/strategy_backtest/ARCHITECTURE.md†L1-L108】 |

## 4. Milestones
| Milestone | Date | Owner | Exit Criteria |
| --------- | ---- | ----- | ------------- |
| M1: Optimizer Design Review | 2025-02-21 | Backend Lead | Approved Optuna architecture, background job strategy | 
| M2: RL Sandbox Ready | 2025-03-07 | Quant Research | RL environment validated with sample policy checkpoints |
| M3: Data Sentinel Launch | 2025-03-14 | Data Engineering | Ingestion pipeline emitting anomaly events to dashboard |
| M4: Integrated Demo | 2025-03-28 | Product | Demonstrate optimizer, RL playback, anomaly reporting in a unified workflow |

## 5. Dependencies & Interfaces
- **Phase 1 Outputs:** Signal and regime services feed optimizer objective functions and RL state features.【F:docs/backend/ai_integration/master_plan.md†L13-L82】
- **Background Task Runner:** Celery or FastAPI background tasks needed for long-running studies.
- **DashboardService Enhancements:** Display optimization leaderboards and anomaly metrics.
- **Compute Resources:** GPU/CPU allocation planning for RL training windows.

## 6. Risks & Mitigations
| Risk | Impact | Likelihood | Response |
| ---- | ------ | ---------- | -------- |
| Optuna job starvation during market hours | High | Medium | Schedule optimization windows; implement job prioritization by asset class. |
| RL training instability | Medium | Medium | Start with constrained action spaces; enable deterministic evaluation for acceptance. |
| False positives in anomaly alerts | Medium | High | Calibrate thresholds using historical backtest data; allow analyst override workflow. |

## 7. Metrics & Reporting
- **Optimization Efficiency:** Trials/hour, best Sharpe improvement vs baseline.
- **RL Performance:** Policy Sharpe ratio delta, drawdown compliance, episode length stability.
- **Data Quality:** Number of anomalies per ingest batch, resolution time, false-positive rate.

## 8. Resource Plan
| Role | Allocation | Notes |
| ---- | ---------- | ----- |
| Backend Engineer | 1.5 FTE | Optuna API, background orchestration, telemetry |
| Quant Researcher | 1 FTE | RL experimentation, reward shaping |
| Data Engineer | 0.5 FTE | Anomaly pipeline and monitoring |
| DevOps Engineer | 0.5 FTE | Compute orchestration, job scheduling |

## 9. Communication Cadence
- Fortnightly deep-dive with Quant Research on RL progress.
- Weekly sync with SRE/DevOps on job scheduling and resource usage.

## 10. Exit Criteria
- Optimizer, RL executor, and anomaly sentinel deployed to staging with automated smoke tests.
- Runbooks and KPI dashboards updated.
- Post-phase retrospective capturing lessons for generative phase transition.
