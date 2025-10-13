"""Market regime persistence models for predictive intelligence."""

from __future__ import annotations

from datetime import datetime, UTC
from enum import Enum
from typing import Dict, List, Optional

from pydantic import Field

from .base import BaseMarketDataDocument


class MarketRegimeType(str, Enum):
    """Supported market regimes for classification."""

    BULLISH = "bullish"
    BEARISH = "bearish"
    VOLATILE = "volatile"
    SIDEWAYS = "sideways"


class MarketRegime(BaseMarketDataDocument):
    """Document storing detected market regimes for instruments."""

    symbol: str = Field(..., description="Symbol associated with the regime")
    as_of: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp representing the end of the lookback window",
    )
    lookback_days: int = Field(
        60, ge=5, description="Number of days used for regime detection"
    )
    regime: MarketRegimeType = Field(..., description="Detected market regime")
    confidence: float = Field(
        0.5, ge=0, le=1, description="Confidence score for the classification"
    )
    probabilities: Dict[str, float] = Field(
        default_factory=dict, description="Probability distribution per regime"
    )
    metrics: Dict[str, float] = Field(
        default_factory=dict, description="Supporting quantitative metrics"
    )
    notes: Optional[List[str]] = Field(
        default_factory=list,
        description="Narrative notes describing primary drivers",
    )

    class Settings:
        name = "market_regimes"
        indexes = [
            "symbol",
            "as_of",
            {"fields": ["symbol", "as_of"], "unique": True},
        ]
