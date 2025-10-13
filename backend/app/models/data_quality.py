"""Data quality monitoring models and enums."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any, Dict, Optional

from beanie import Document
from pydantic import Field


class SeverityLevel(str, Enum):
    """Severity level used by the data quality sentinel."""

    NORMAL = "normal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DataQualityEvent(Document):
    """Recorded anomaly emitted by the data quality sentinel."""

    symbol: str = Field(..., description="Asset symbol for the anomaly event")
    data_type: str = Field(
        ..., description="Data slice that triggered the anomaly (e.g. daily)"
    )
    occurred_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp associated with the anomalous datapoint",
    )
    severity: SeverityLevel = Field(
        default=SeverityLevel.NORMAL, description="Sentinel severity classification"
    )
    anomaly_type: str = Field(
        ..., description="Primary anomaly category selected by the sentinel"
    )
    iso_score: Optional[float] = Field(
        None, description="IsolationForest based anomaly score (0-1 range)"
    )
    prophet_score: Optional[float] = Field(
        None, description="Prophet-style residual z-score used for trend deviation"
    )
    price_change_pct: Optional[float] = Field(
        None, description="Percent change versus the previous close"
    )
    volume_z_score: Optional[float] = Field(
        None, description="Z-score of the traded volume relative to recent history"
    )
    message: str = Field(..., description="Human readable anomaly summary")
    source: str = Field("alpha_vantage", description="Origin of the ingested dataset")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional context for dashboards/webhooks"
    )
    acknowledged: bool = Field(
        default=False, description="Whether the anomaly has been acknowledged"
    )
    resolved_at: Optional[datetime] = Field(
        default=None, description="Timestamp when the anomaly was resolved"
    )

    class Settings:
        name = "data_quality_events"
        indexes = [
            [("symbol", 1), ("occurred_at", -1)],
            [("severity", 1), ("occurred_at", -1)],
            [("data_type", 1), ("occurred_at", -1)],
            [("symbol", 1), ("data_type", 1), ("occurred_at", -1)],
        ]


__all__ = ["SeverityLevel", "DataQualityEvent"]
