"""Schemas for predictive intelligence services (Phase 1).

These schemas cover machine learning signal scoring, market regime
detection, and probabilistic KPI forecasts that power the predictive
intelligence layer introduced in Phase 1 of the AI integration plan.
"""

from __future__ import annotations

from datetime import datetime, UTC
from enum import Enum
from typing import Dict, List, Optional
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.market_data.regime import MarketRegimeType
from app.schemas.market_data.base import (
    BaseResponse,
    CacheInfo,
    DataQualityInfo,
    DataResponse,
    MetadataInfo,
)


def _default_predictive_metadata() -> MetadataInfo:
    now = datetime.now(UTC)
    return MetadataInfo(
        data_quality=DataQualityInfo(
            quality_score=Decimal("85.0"),
            last_updated=now,
            data_source="predictive_intelligence",
            confidence_level="model_based",
        ),
        cache_info=CacheInfo(
            cached=False,
            cache_hit=False,
            cache_timestamp=None,
            cache_ttl=None,
        ),
        processing_time_ms=0.0,
    )


class SignalRecommendation(str, Enum):
    """Recommendation derived from model probability."""

    STRONG_BUY = "strong_buy"
    BUY = "buy"
    HOLD = "hold"
    SELL = "sell"
    STRONG_SELL = "strong_sell"


class FeatureContribution(BaseModel):
    """Contribution details for a single engineered feature."""

    feature: str = Field(..., description="Feature name")
    value: float = Field(..., description="Computed feature value")
    weight: float = Field(..., description="Relative weight applied in scoring")
    impact: float = Field(..., description="Signed contribution to probability")
    direction: Optional[str] = Field(
        None,
        description="Human readable description of how the feature influences the score",
    )


class MLSignalInsight(BaseModel):
    """Inference payload produced by the ML signal service."""

    symbol: str = Field(..., description="Instrument symbol")
    as_of: datetime = Field(..., description="Timestamp of the latest observation")
    lookback_days: int = Field(
        ..., ge=5, description="Lookback window used for features"
    )
    probability: float = Field(
        ..., ge=0, le=1, description="Probability of positive move"
    )
    confidence: float = Field(
        ..., ge=0, le=1, description="Confidence proxy from data depth"
    )
    recommendation: SignalRecommendation = Field(
        ..., description="Recommendation bucket derived from probability"
    )
    feature_contributions: List[FeatureContribution] = Field(
        default_factory=list, description="Ordered list of feature contributions"
    )
    top_signals: List[str] = Field(
        default_factory=list, description="Human readable highlights from the model"
    )


class MLSignalResponse(DataResponse[MLSignalInsight]):
    """API response wrapper for ML signal insights."""

    data: MLSignalInsight = Field(..., description="Signal inference payload")
    metadata: MetadataInfo = Field(..., description="Response metadata")


class RegimeMetrics(BaseModel):
    """Quantitative metrics used for regime detection."""

    trailing_return_pct: float = Field(..., description="Lookback total return in %")
    volatility_pct: float = Field(..., description="Annualised volatility in %")
    drawdown_pct: float = Field(..., description="Max drawdown observed in %")
    momentum_z: float = Field(..., description="Z-score of short term momentum")


class MarketRegimeSnapshot(BaseModel):
    """Market regime classification snapshot."""

    symbol: str = Field(
        ..., description="Instrument symbol for the regime classification"
    )
    as_of: datetime = Field(..., description="Reference timestamp for the snapshot")
    lookback_days: int = Field(..., ge=5, description="Lookback window in days")
    regime: MarketRegimeType = Field(..., description="Detected market regime")
    confidence: float = Field(
        ..., ge=0, le=1, description="Confidence of classification"
    )
    probabilities: Dict[MarketRegimeType, float] = Field(
        default_factory=dict, description="Probability distribution across regimes"
    )
    metrics: RegimeMetrics = Field(..., description="Supporting quantitative metrics")
    notes: List[str] = Field(
        default_factory=list, description="Notable drivers or anomalies"
    )


class MarketRegimeResponse(DataResponse[MarketRegimeSnapshot]):
    """API response for regime classification."""

    data: MarketRegimeSnapshot = Field(..., description="Regime snapshot")
    metadata: MetadataInfo = Field(..., description="Response metadata")


class ForecastPercentileBand(BaseModel):
    """Single percentile projection for a future portfolio value."""

    percentile: int = Field(..., ge=0, le=100, description="Percentile value (0-100)")
    projected_value: float = Field(
        ..., description="Projected portfolio value at percentile"
    )


class PortfolioForecastDistribution(BaseModel):
    """Distribution of future portfolio values based on Monte Carlo proxy."""

    as_of: datetime = Field(..., description="Timestamp the forecast was generated")
    horizon_days: int = Field(..., ge=1, description="Forecast horizon in days")
    last_portfolio_value: float = Field(
        ..., description="Most recent observed portfolio value"
    )
    expected_return_pct: float = Field(
        ..., description="Expected return over the horizon (%)"
    )
    expected_volatility_pct: float = Field(
        ..., description="Expected volatility over the horizon (%)"
    )
    percentile_bands: List[ForecastPercentileBand] = Field(
        ..., description="Projected percentile bands"
    )
    methodology: str = Field(
        "gaussian_projection",
        description="Shorthand name of the forecasting methodology",
    )


class PortfolioForecastResponse(DataResponse[PortfolioForecastDistribution]):
    """API response for probabilistic portfolio forecasts."""

    data: PortfolioForecastDistribution = Field(..., description="Forecast output")
    metadata: MetadataInfo = Field(..., description="Response metadata")


class PredictiveDashboardInsights(BaseModel):
    """Aggregated predictive insights exposed on the dashboard."""

    signal: MLSignalInsight = Field(..., description="Latest ML signal insight")
    regime: MarketRegimeSnapshot = Field(
        ..., description="Current market regime snapshot"
    )
    forecast: PortfolioForecastDistribution = Field(
        ..., description="Probabilistic portfolio forecast"
    )


class PredictiveInsightsResponse(BaseResponse):
    """Response wrapper for predictive dashboard bundle."""

    data: PredictiveDashboardInsights = Field(
        ..., description="Combined predictive intelligence payload"
    )
    metadata: MetadataInfo = Field(
        default_factory=_default_predictive_metadata,
        description="Response metadata for predictive payload",
    )
