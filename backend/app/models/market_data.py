"""
Market Data Models using Beanie (MongoDB ODM)
"""

from datetime import datetime
from typing import Optional
from .base_model import BaseDocument
from pydantic import Field


class MarketData(BaseDocument):
    """Market data document model"""

    symbol: str = Field(..., description="Stock symbol")
    date: datetime = Field(..., description="Date of the data")
    open_price: float = Field(..., alias="open", description="Opening price")
    high_price: float = Field(..., alias="high", description="High price")
    low_price: float = Field(..., alias="low", description="Low price")
    close_price: float = Field(..., alias="close", description="Closing price")
    volume: int = Field(..., description="Trading volume")

    # Additional fields
    adjusted_close: Optional[float] = Field(None, description="Adjusted closing price")
    dividend_amount: Optional[float] = Field(None, description="Dividend amount")
    split_coefficient: Optional[float] = Field(None, description="Split coefficient")

    # Metadata
    source: str = Field(default="alpha_vantage", description="Data source")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "market_data"
        indexes = [
            [("symbol", 1), ("date", 1)],  # Compound index
            "symbol",
            "date",
            "created_at",
        ]


class DataRequest(BaseDocument):
    """Data request tracking document"""

    symbol: str = Field(..., description="Requested symbol")
    start_date: datetime = Field(..., description="Start date")
    end_date: datetime = Field(..., description="End date")
    interval: str = Field(default="daily", description="Data interval")

    # Status tracking
    status: str = Field(default="pending", description="Request status")
    error_message: Optional[str] = Field(
        default=None, description="Error message if failed"
    )
    records_count: Optional[int] = Field(
        default=None, description="Number of records fetched"
    )

    # Timestamps
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(
        default=None, description="Completion timestamp"
    )

    class Settings:
        name = "data_requests"
        indexes = ["symbol", "status", "requested_at"]


class DataQuality(BaseDocument):
    """Data quality metrics document"""

    symbol: str = Field(..., description="Symbol")
    date_range_start: datetime = Field(..., description="Start of date range")
    date_range_end: datetime = Field(..., description="End of date range")

    # Quality metrics
    total_records: int = Field(..., description="Total records in range")
    missing_days: int = Field(default=0, description="Number of missing trading days")
    duplicate_records: int = Field(default=0, description="Number of duplicate records")
    price_anomalies: int = Field(default=0, description="Number of price anomalies")

    # Quality score (0-100)
    quality_score: float = Field(..., description="Overall quality score")

    # Analysis metadata
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)
    analysis_version: str = Field(
        default="1.0", description="Analysis algorithm version"
    )

    class Settings:
        name = "data_quality"
        indexes = ["symbol", "quality_score", "analyzed_at"]
