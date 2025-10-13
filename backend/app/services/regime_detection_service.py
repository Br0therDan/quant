"""Market regime detection service leveraging DuckDB features."""

from __future__ import annotations

import asyncio
import logging
import math
from datetime import UTC
from typing import Dict, List, Optional

import pandas as pd
from app.models.market_data.regime import MarketRegime, MarketRegimeType
from app.services.database_manager import DatabaseManager
from app.schemas.predictive import MarketRegimeSnapshot, RegimeMetrics

logger = logging.getLogger(__name__)


class RegimeDetectionService:
    """Detects and stores market regimes for symbols."""

    def __init__(self, database_manager: DatabaseManager):
        self._db_manager = database_manager

    async def refresh_regime(
        self, symbol: str, lookback_days: int = 90
    ) -> MarketRegimeSnapshot:
        """Compute and persist the latest regime snapshot for a symbol."""

        df = await asyncio.to_thread(self._load_price_history, symbol, lookback_days)
        if df.empty:
            raise ValueError(f"No market data available for regime detection: {symbol}")

        metrics = await asyncio.to_thread(self._compute_metrics, df)
        probabilities = self._estimate_probabilities(metrics)
        regime, confidence = self._select_regime(probabilities)
        notes = self._build_notes(metrics, regime)

        snapshot = MarketRegimeSnapshot(
            symbol=symbol,
            as_of=df.index[-1].to_pydatetime().replace(tzinfo=UTC),
            lookback_days=lookback_days,
            regime=regime,
            confidence=confidence,
            probabilities=probabilities,
            metrics=metrics,
            notes=notes,
        )

        await self._persist_snapshot(snapshot)
        logger.info(
            "Refreshed market regime",
            extra={
                "symbol": symbol,
                "regime": regime.value,
                "confidence": confidence,
            },
        )

        return snapshot

    async def get_latest_regime(self, symbol: str) -> Optional[MarketRegimeSnapshot]:
        """Fetch the most recent regime snapshot from MongoDB."""

        document = (
            await MarketRegime.find(MarketRegime.symbol == symbol)
            .sort("-as_of")
            .limit(1)
            .first_or_none()
        )
        if not document:
            return None

        return MarketRegimeSnapshot(
            symbol=document.symbol,
            as_of=document.as_of,
            lookback_days=document.lookback_days,
            regime=document.regime,
            confidence=document.confidence,
            probabilities={
                MarketRegimeType(key): value
                for key, value in document.probabilities.items()
            },
            metrics=RegimeMetrics(**document.metrics),
            notes=document.notes or [],
        )

    async def _persist_snapshot(self, snapshot: MarketRegimeSnapshot) -> None:
        payload = {
            "symbol": snapshot.symbol,
            "as_of": snapshot.as_of,
            "lookback_days": snapshot.lookback_days,
            "regime": snapshot.regime,
            "confidence": snapshot.confidence,
            "probabilities": {k.value: v for k, v in snapshot.probabilities.items()},
            "metrics": snapshot.metrics.model_dump(),
            "notes": snapshot.notes,
            "source": "predictive_intelligence",
        }

        existing = await MarketRegime.find_one(
            MarketRegime.symbol == snapshot.symbol,
            MarketRegime.as_of == snapshot.as_of,
        )
        if existing:
            await existing.set(payload)
        else:
            await MarketRegime(**payload).insert()

    def _load_price_history(self, symbol: str, lookback_days: int) -> pd.DataFrame:
        conn = self._db_manager.duckdb_conn
        query = """
            SELECT date, close
            FROM daily_prices
            WHERE symbol = ?
            ORDER BY date DESC
            LIMIT ?
        """
        df = conn.execute(query, [symbol, lookback_days + 30]).fetch_df()
        if df.empty:
            return df

        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").set_index("date")
        return df

    def _compute_metrics(self, df: pd.DataFrame) -> RegimeMetrics:
        closes = df["close"].astype(float)
        returns = closes.pct_change().dropna()

        trailing_return = (
            (closes.iloc[-1] / closes.iloc[0]) - 1 if len(closes) > 1 else 0.0
        )
        volatility = returns.std() * math.sqrt(252) if not returns.empty else 0.0

        rolling_max = closes.cummax()
        drawdown_series = (closes / rolling_max) - 1
        max_drawdown = drawdown_series.min() if not drawdown_series.empty else 0.0

        momentum_window = closes.tail(10)
        momentum_mean = momentum_window.mean() if not momentum_window.empty else 0.0
        momentum_std = momentum_window.std() if len(momentum_window) > 1 else 1.0
        latest_close = closes.iloc[-1]
        momentum_z = (
            (latest_close - momentum_mean) / momentum_std if momentum_std else 0.0
        )

        return RegimeMetrics(
            trailing_return_pct=float(trailing_return * 100),
            volatility_pct=float(volatility * 100),
            drawdown_pct=float(abs(max_drawdown) * 100),
            momentum_z=float(momentum_z),
        )

    def _estimate_probabilities(
        self, metrics: RegimeMetrics
    ) -> Dict[MarketRegimeType, float]:
        bullish_score = max(
            0.0, metrics.trailing_return_pct / 10 + metrics.momentum_z * 0.5
        )
        bearish_score = max(
            0.0, (metrics.drawdown_pct / 5) + max(0.0, -metrics.momentum_z) * 0.7
        )
        volatile_score = max(0.0, (metrics.volatility_pct - 15) / 10)

        base = 1.0 + bullish_score + bearish_score + volatile_score
        probs = {
            MarketRegimeType.BULLISH: max(0.05, bullish_score / base),
            MarketRegimeType.BEARISH: max(0.05, bearish_score / base),
            MarketRegimeType.VOLATILE: max(0.05, volatile_score / base),
        }
        probs[MarketRegimeType.SIDEWAYS] = max(0.05, 1.0 - sum(probs.values()))

        total = sum(probs.values())
        return {regime: value / total for regime, value in probs.items()}

    def _select_regime(
        self, probabilities: Dict[MarketRegimeType, float]
    ) -> tuple[MarketRegimeType, float]:
        regime = max(probabilities.items(), key=lambda item: item[1])[0]
        confidence = probabilities[regime]
        return regime, confidence

    def _build_notes(
        self, metrics: RegimeMetrics, regime: MarketRegimeType
    ) -> List[str]:
        notes: List[str] = []
        if metrics.trailing_return_pct > 5:
            notes.append("Strong positive trailing returns")
        if metrics.drawdown_pct > 10:
            notes.append("Elevated drawdown risk")
        if metrics.volatility_pct > 25:
            notes.append("High realised volatility")
        if regime == MarketRegimeType.SIDEWAYS and abs(metrics.momentum_z) < 0.5:
            notes.append("Momentum neutral – consolidating price action")
        return notes
