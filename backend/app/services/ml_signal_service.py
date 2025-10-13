"""
Machine learning signal scoring service.

Phase 3.2 ML Integration:
- Uses trained LightGBM model for signal prediction
- Falls back to heuristic scoring if model not available
- Integrates FeatureEngineer for technical indicators
- Model versioning via ModelRegistry
"""

from __future__ import annotations

import asyncio
import logging
import math
from dataclasses import dataclass
from datetime import UTC
from pathlib import Path
from typing import Dict, Iterable, List

import pandas as pd

from app.schemas.predictive import (
    FeatureContribution,
    MLSignalInsight,
    SignalRecommendation,
)
from app.services.database_manager import DatabaseManager
from app.services.ml import FeatureEngineer, ModelRegistry

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
    """
    Service responsible for generating ML-driven signal scores.

    Phase 3.2 Features:
    - Uses trained LightGBM model for predictions
    - Automatic feature engineering with FeatureEngineer
    - Model versioning and selection via ModelRegistry
    - Fallback to heuristic scoring if model unavailable
    """

    def __init__(
        self,
        database_manager: DatabaseManager,
        model_dir: Path | str = "app/data/models",
        use_ml_model: bool = True,
    ):
        """
        Args:
            database_manager: Database manager instance
            model_dir: Directory containing trained models
            use_ml_model: Whether to use ML model (True) or heuristic (False)
        """
        self._db_manager = database_manager
        self._use_ml_model = use_ml_model
        self._feature_engineer = FeatureEngineer()
        self._model_registry = ModelRegistry(base_dir=model_dir)
        self._model = None
        self._model_metadata = None

        # Try to load latest model
        if self._use_ml_model:
            try:
                self._model, self._model_metadata = self._model_registry.load_model(
                    model_type="signal"
                )
                logger.info(
                    f"Loaded ML model {self._model_metadata['version']} "
                    f"(accuracy: {self._model_metadata['metrics'].get('accuracy', 'N/A')})"
                )
            except (ValueError, FileNotFoundError) as e:
                logger.warning(
                    f"Failed to load ML model, falling back to heuristic: {e}"
                )
                self._use_ml_model = False

    async def score_symbol(
        self, symbol: str, lookback_days: int = 60
    ) -> MLSignalInsight:
        """
        Generate an ML signal score for the requested symbol.

        Phase 3.2: Uses trained LightGBM model if available,
        otherwise falls back to heuristic scoring.
        """

        df = await asyncio.to_thread(self._load_price_history, symbol, lookback_days)
        if df.empty:
            raise ValueError(f"No price history available for {symbol}")

        # Use ML model if available
        if self._use_ml_model and self._model is not None:
            return await self._score_with_ml_model(df, symbol, lookback_days)

        # Fallback to heuristic scoring
        return await self._score_with_heuristic(df, symbol, lookback_days)

    async def _score_with_ml_model(
        self, df: pd.DataFrame, symbol: str, lookback_days: int
    ) -> MLSignalInsight:
        """Score using trained LightGBM model."""

        # 1. Calculate technical indicators
        try:
            df_features = await asyncio.to_thread(
                self._feature_engineer.calculate_technical_indicators, df
            )
        except Exception as e:
            logger.warning(
                f"Feature engineering failed for {symbol}, falling back: {e}"
            )
            return await self._score_with_heuristic(df, symbol, lookback_days)

        if df_features.empty:
            logger.warning(f"No features calculated for {symbol}, falling back")
            return await self._score_with_heuristic(df, symbol, lookback_days)

        # 2. Get latest features
        latest_features = df_features.iloc[[-1]]
        feature_cols = self._feature_engineer.get_feature_columns()
        available_features = [
            col for col in feature_cols if col in latest_features.columns
        ]

        if not available_features:
            logger.warning(f"No features available for {symbol}, falling back")
            return await self._score_with_heuristic(df, symbol, lookback_days)

        X = latest_features[available_features]

        # 3. Predict with model
        try:
            prediction_proba = self._model.predict(X)[0]  # type: ignore
            # For binary classification: [prob_class_0, prob_class_1]
            # We want probability of buy signal (class 1)
            if isinstance(prediction_proba, (list, tuple)):
                probability = float(prediction_proba[1])
            else:
                probability = float(prediction_proba)  # type: ignore

            # Ensure probability is in [0, 1]
            probability = max(0.0, min(1.0, probability))

        except Exception as e:
            logger.error(f"Model prediction failed for {symbol}: {e}")
            return await self._score_with_heuristic(df, symbol, lookback_days)

        # 4. Calculate feature contributions (using model feature importance)
        contributions = self._calculate_ml_contributions(X, available_features)

        # 5. Generate insight
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
                "model_version": self._model_metadata["version"] if self._model_metadata else "N/A",  # type: ignore
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

    async def _score_with_heuristic(
        self, df: pd.DataFrame, symbol: str, lookback_days: int
    ) -> MLSignalInsight:
        """Score using heuristic-based approach (original implementation)."""

        features = await asyncio.to_thread(self._engineer_features, df)
        probability, contributions = self._score_probability(features)
        as_of = df.index[-1].to_pydatetime().replace(tzinfo=UTC)

        confidence = min(1.0, max(0.2, len(df) / max(lookback_days, 1)))
        recommendation = self._map_recommendation(probability)
        top_signals = self._summarise_drivers(contributions)

        logger.info(
            "Generated heuristic signal",
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

    def _calculate_ml_contributions(
        self, X: pd.DataFrame, feature_names: list[str]
    ) -> List[FeatureContribution]:
        """
        Calculate feature contributions using model feature importance.

        Args:
            X: Feature dataframe (single row)
            feature_names: List of feature names

        Returns:
            List of FeatureContribution objects
        """
        if self._model is None:
            return []

        # Get feature importance from model
        importance = self._model.feature_importance(importance_type="gain")

        contributions = []
        for i, feature_name in enumerate(feature_names):
            if i >= len(importance):
                break

            feature_value = X[feature_name].iloc[0]
            weight = importance[i] / importance.sum()  # Normalize
            impact = feature_value * weight

            # Format direction
            if impact > 0:
                direction = f"{feature_name.replace('_', ' ')} supports upside"
            elif impact < 0:
                direction = f"{feature_name.replace('_', ' ')} pressures downside"
            else:
                direction = f"{feature_name.replace('_', ' ')} neutral"

            contributions.append(
                FeatureContribution(
                    feature=feature_name,
                    value=float(feature_value),
                    weight=float(weight),
                    impact=float(impact),
                    direction=direction,
                )
            )

        # Sort by absolute impact
        contributions.sort(key=lambda c: abs(c.impact), reverse=True)
        return contributions

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
            if isinstance(result, MLSignalInsight):  # Type guard
                scored[str(symbol)] = result
        return scored

    def _load_price_history(self, symbol: str, lookback_days: int) -> pd.DataFrame:
        conn = self._db_manager.duckdb_conn
        query = """
            SELECT date, open, high, low, close, volume
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
        volumes = df["volume"].astype(float).ffill()  # Updated pandas syntax

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
            trend_series = pd.Series(
                range(20), index=closes.tail(20).index, dtype=float
            )
            trend_strength = closes.tail(20).corr(trend_series)  # type: ignore
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
