"""
Data schemas for request/response models
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class MarketDataResponse(BaseModel):
    """Response model for market data"""

    symbol: str
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    adjusted_close: Optional[float] = None
    dividend_amount: Optional[float] = None
    split_coefficient: Optional[float] = None


class MarketDataRequest(BaseModel):
    """Request model for market data"""

    symbol: str = Field(..., description="Stock symbol")
    start_date: datetime = Field(..., description="Start date")
    end_date: datetime = Field(..., description="End date")
    interval: str = Field(
        default="daily", description="Data interval (daily, weekly, monthly)"
    )


class DataQualityResponse(BaseModel):
    """Response model for data quality metrics"""

    symbol: str
    date_range_start: datetime
    date_range_end: datetime
    total_records: int
    missing_days: int
    duplicate_records: int
    price_anomalies: int
    quality_score: float
    analyzed_at: datetime


class DataRequestStatus(BaseModel):
    """Response model for data request status"""

    id: str
    symbol: str
    start_date: datetime
    end_date: datetime
    status: str
    error_message: Optional[str] = None
    records_count: Optional[int] = None
    requested_at: datetime
    completed_at: Optional[datetime] = None


class BulkDataRequest(BaseModel):
    """Request model for bulk data operations"""

    symbols: List[str] = Field(..., description="List of symbols")
    start_date: datetime = Field(..., description="Start date")
    end_date: datetime = Field(..., description="End date")
    interval: str = Field(default="daily", description="Data interval")


class HealthCheckResponse(BaseModel):
    """Health check response model"""

    status: str
    timestamp: datetime
    database_connected: bool
    alpha_vantage_available: bool
    total_symbols: int
    last_update: Optional[datetime] = None
