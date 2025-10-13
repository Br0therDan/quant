"""Machine learning signal scoring service (Phase 1 deliverable)."""

from __future__ import annotations

import asyncio
import logging
import math
from dataclasses import dataclass
from datetime import UTC
from typing import Dict, Iterable, List

import pandas as pd

from app.services.database_manager import DatabaseManager
from app.schemas.predictive import (
    FeatureContribution,
    MLSignalInsight,
    SignalRecommendation,
)

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class _SignalFeatures:
    """Container for engineered features."""

    momentum_5d: float
    momentum_20d: float
    volatility_20d: float
    volume_ratio: float
    trend_strength: float


class MLSignalService:
    """Service responsible for generating ML-inspired signal scores."""

    def __init__(self, database_manager: DatabaseManager):
        self._db_manager = database_manager

    async def score_symbol(
        self, symbol: str, lookback_days: int = 60
    ) -> MLSignalInsight:
        """Generate an ML signal score for the requested symbol."""

        df = await asyncio.to_thread(self._load_price_history, symbol, lookback_days)
        if df.empty:
            raise ValueError(f"No price history available for {symbol}")

        features = await asyncio.to_thread(self._engineer_features, df)
        probability, contributions = self._score_probability(features)
        as_of = df.index[-1].to_pydatetime().replace(tzinfo=UTC)

        confidence = min(1.0, max(0.2, len(df) / max(lookback_days, 1)))
        recommendation = self._map_recommendation(probability)
        top_signals = self._summarise_drivers(contributions)

        logger.info(
            "Generated ML signal",
            extra={
                "symbol": symbol,
                "probability": probability,
                "confidence": confidence,
                "recommendation": recommendation.value,
            },
        )

        return MLSignalInsight(
            symbol=symbol,
            as_of=as_of,
            lookback_days=lookback_days,
            probability=probability,
            confidence=confidence,
            recommendation=recommendation,
            feature_contributions=contributions,
            top_signals=top_signals,
        )

    async def score_symbols(
        self, symbols: Iterable[str], lookback_days: int = 60
    ) -> Dict[str, MLSignalInsight]:
        """Batch scoring helper used by orchestrators or dashboards."""

        tasks = [
            self.score_symbol(symbol, lookback_days=lookback_days) for symbol in symbols
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        scored: Dict[str, MLSignalInsight] = {}
        for symbol, result in zip(symbols, results):
            if isinstance(result, Exception):
                logger.warning("Signal scoring failed", exc_info=result)
                continue
            scored[str(symbol)] = result
        return scored

    def _load_price_history(self, symbol: str, lookback_days: int) -> pd.DataFrame:
        conn = self._db_manager.duckdb_conn
        query = """
            SELECT date, close, volume
            FROM daily_prices
            WHERE symbol = ?
            ORDER BY date DESC
            LIMIT ?
        """
        df = conn.execute(query, [symbol, lookback_days + 20]).fetch_df()
        if df.empty:
            return df

        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").set_index("date")
        df = df[df["close"].notna()]
        return df

    def _engineer_features(self, df: pd.DataFrame) -> _SignalFeatures:
        closes = df["close"].astype(float)
        volumes = df["volume"].astype(float).fillna(method="ffill")

        momentum_5d = self._safe_pct_change(closes, periods=5)
        momentum_20d = self._safe_pct_change(closes, periods=20)

        returns = closes.pct_change().dropna()
        volatility_20d = (
            returns.tail(20).std() * math.sqrt(252)
            if not returns.tail(20).empty
            else 0.0
        )

        volume_ratio = 0.0
        if len(volumes) >= 20 and volumes.tail(20).mean() > 0:
            volume_ratio = volumes.tail(5).mean() / volumes.tail(20).mean() - 1

        trend_strength = 0.0
        if len(closes) >= 20:
            trend_strength = closes.tail(20).corr(
                pd.Series(range(20), index=closes.tail(20).index)
            )
            if pd.isna(trend_strength):
                trend_strength = 0.0

        return _SignalFeatures(
            momentum_5d=float(momentum_5d),
            momentum_20d=float(momentum_20d),
            volatility_20d=float(volatility_20d),
            volume_ratio=float(volume_ratio),
            trend_strength=float(trend_strength),
        )

    def _safe_pct_change(self, series: pd.Series, periods: int) -> float:
        if len(series) <= periods:
            return 0.0
        try:
            value = (series.iloc[-1] / series.iloc[-periods - 1]) - 1
            if math.isfinite(value):
                return float(value)
            return 0.0
        except (ZeroDivisionError, IndexError):
            return 0.0

    def _score_probability(
        self, features: _SignalFeatures
    ) -> tuple[float, List[FeatureContribution]]:
        weights = {
            "momentum_5d": 2.1,
            "momentum_20d": 1.4,
            "volatility_20d": -1.6,
            "volume_ratio": 0.9,
            "trend_strength": 1.2,
        }

        score = (
            features.momentum_5d * weights["momentum_5d"]
            + features.momentum_20d * weights["momentum_20d"]
            + features.volatility_20d * weights["volatility_20d"]
            + features.volume_ratio * weights["volume_ratio"]
            + features.trend_strength * weights["trend_strength"]
        )

        probability = 1.0 / (1.0 + math.exp(-score))

        contributions = [
            FeatureContribution(
                feature=name,
                value=getattr(features, name),
                weight=weight,
                impact=getattr(features, name) * weight,
                direction=self._format_direction(name, getattr(features, name), weight),
            )
            for name, weight in weights.items()
        ]

        contributions.sort(key=lambda c: abs(c.impact), reverse=True)
        return probability, contributions

    def _format_direction(self, name: str, value: float, weight: float) -> str:
        impact = value * weight
        if impact > 0:
            adjective = "supports"
        elif impact < 0:
            adjective = "pressures"
        else:
            adjective = "neutral"
        return f"{name.replace('_', ' ')} {adjective} upside"

    def _map_recommendation(self, probability: float) -> SignalRecommendation:
        if probability >= 0.75:
            return SignalRecommendation.STRONG_BUY
        if probability >= 0.6:
            return SignalRecommendation.BUY
        if probability <= 0.25:
            return SignalRecommendation.STRONG_SELL
        if probability <= 0.4:
            return SignalRecommendation.SELL
        return SignalRecommendation.HOLD

    def _summarise_drivers(self, contributions: List[FeatureContribution]) -> List[str]:
        highlights: List[str] = []
        for contribution in contributions[:3]:
            direction = "positive" if contribution.impact >= 0 else "negative"
            highlights.append(
                f"{contribution.feature.replace('_', ' ').title()} {direction} impact"
            )
        return highlights
