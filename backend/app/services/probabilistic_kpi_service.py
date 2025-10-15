"""Probabilistic KPI forecasting service for portfolio analytics."""

from __future__ import annotations

import asyncio
import logging
import math
from datetime import UTC, datetime
from statistics import NormalDist, fmean, pstdev
from typing import Iterable, List

from app.schemas.user.dashboard import PortfolioDataPoint
from app.schemas.ml_platform.predictive import (
    ForecastPercentileBand,
    PortfolioForecastDistribution,
)
from app.services.database_manager import DatabaseManager

logger = logging.getLogger(__name__)


class ProbabilisticKPIService:
    """Forecast portfolio value distributions using historical returns."""

    def __init__(self, database_manager: DatabaseManager):
        self._db_manager = database_manager

    async def forecast_from_history(
        self,
        data_points: Iterable[PortfolioDataPoint],
        horizon_days: int = 30,
    ) -> PortfolioForecastDistribution:
        """Generate percentile forecasts from a historical equity curve."""

        points = list(sorted(data_points, key=lambda p: p.timestamp))
        if not points:
            raise ValueError("Portfolio history is required for forecasting")

        distribution = await asyncio.to_thread(
            self._compute_distribution, points, horizon_days
        )
        await asyncio.to_thread(self._record_forecast, distribution)
        return distribution

    def _compute_distribution(
        self, points: List[PortfolioDataPoint], horizon_days: int
    ) -> PortfolioForecastDistribution:
        returns = self._compute_returns(points)
        mean_return = fmean(returns) if returns else 0.0
        volatility = pstdev(returns) if len(returns) > 1 else 0.0

        horizon_return = mean_return * horizon_days
        horizon_volatility = volatility * math.sqrt(horizon_days)

        last_value = points[-1].portfolio_value
        now = datetime.now(UTC)

        normal = NormalDist(mu=horizon_return, sigma=horizon_volatility or 1e-6)

        percentiles = [5, 50, 95]
        percentile_bands = [
            ForecastPercentileBand(
                percentile=percentile,
                projected_value=float(
                    max(0.0, last_value * (1 + normal.inv_cdf(percentile / 100)))
                ),
            )
            for percentile in percentiles
        ]

        expected_return_pct = horizon_return * 100
        expected_volatility_pct = horizon_volatility * 100

        logger.info(
            "Generated probabilistic KPI forecast",
            extra={
                "horizon_days": horizon_days,
                "expected_return_pct": expected_return_pct,
                "expected_volatility_pct": expected_volatility_pct,
            },
        )

        return PortfolioForecastDistribution(
            as_of=now,
            horizon_days=horizon_days,
            last_portfolio_value=last_value,
            expected_return_pct=float(expected_return_pct),
            expected_volatility_pct=float(expected_volatility_pct),
            percentile_bands=percentile_bands,
        )

    def _compute_returns(self, points: List[PortfolioDataPoint]) -> List[float]:
        returns: List[float] = []
        for prev, curr in zip(points[:-1], points[1:]):
            if prev.portfolio_value == 0:
                continue
            returns.append(
                (curr.portfolio_value - prev.portfolio_value) / prev.portfolio_value
            )
        return returns

    def _record_forecast(self, distribution: PortfolioForecastDistribution) -> None:
        try:
            percentile_map = {
                band.percentile: band.projected_value
                for band in distribution.percentile_bands
            }
            self._db_manager.record_portfolio_forecast(
                as_of=distribution.as_of,
                horizon_days=distribution.horizon_days,
                p05=percentile_map.get(5, distribution.last_portfolio_value),
                p50=percentile_map.get(50, distribution.last_portfolio_value),
                p95=percentile_map.get(95, distribution.last_portfolio_value),
                expected_return_pct=distribution.expected_return_pct,
                expected_volatility_pct=distribution.expected_volatility_pct,
            )
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.warning("Failed to persist forecast history", exc_info=exc)
