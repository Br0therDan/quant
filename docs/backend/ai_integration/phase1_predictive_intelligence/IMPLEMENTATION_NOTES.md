# Phase 1 Predictive Intelligence – Implementation Notes

This document captures the engineering deliverables implemented during the
Phase 1 execution for predictive intelligence. It maps directly to the D1–D3
scope defined in the execution plan and highlights integration points.

## D1 – ML Signal Service

- Added `MLSignalService` backed by DuckDB feature extraction to generate
  probability scores, feature contributions, and recommendations per symbol.
- Exposed the service via `GET /signals/{symbol}` with configurable lookback
  windows and metadata payloads.
- Updated the backtest orchestrator to request ML signal enrichments for each
  strategy signal, embedding probability and recommendation context.

## D2 – Regime Detection API

- Introduced the `MarketRegime` Beanie document and the
  `RegimeDetectionService` to classify market regimes using trailing return,
  volatility, drawdown, and momentum statistics.
- Persisted regime snapshots in MongoDB with `symbol + as_of` uniqueness and
  added the `/market-data/regime` route to fetch or refresh snapshots.
- Dashboard service composes regime metadata for predictive insights and keeps
  the latest snapshot warm.

## D3 – Probabilistic KPI Forecasts

- Built the `ProbabilisticKPIService` to derive percentile forecasts from
  historical portfolio equity curves using a Gaussian projection heuristic.
- Extended DuckDB schema with `portfolio_forecast_history` to track forecast
  evaluations and wired the service through the existing `PortfolioService`.
- Surfaced the combined signal, regime, and forecast view through
  `/dashboard/predictive/overview`, ready for UI consumption.

## Additional Integration

- ServiceFactory now manages the lifecycle of all predictive services and
  pre-initialises them during application startup for consistent readiness.
- Dashboard service exposes a single `get_predictive_snapshot` helper that
  aggregates the three predictive domains for downstream clients.

