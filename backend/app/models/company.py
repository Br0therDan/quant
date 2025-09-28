"""
Company Information Models
"""

from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import Field


class Company(Document):
    """Company information document model"""

    symbol: str = Field(..., description="Stock symbol")
    name: str = Field(..., description="Company name")
    description: Optional[str] = Field(None, description="Company description")

    # Basic info
    sector: Optional[str] = Field(None, description="Business sector")
    industry: Optional[str] = Field(None, description="Industry category")
    country: Optional[str] = Field(None, description="Country of operation")
    currency: Optional[str] = Field(None, description="Trading currency")
    exchange: Optional[str] = Field(None, description="Stock exchange")

    # Financial info
    market_cap: Optional[int] = Field(None, description="Market capitalization")
    shares_outstanding: Optional[int] = Field(None, description="Shares outstanding")
    pe_ratio: Optional[float] = Field(None, description="P/E ratio")
    dividend_yield: Optional[float] = Field(None, description="Dividend yield")

    # Trading info
    market_open: Optional[str] = Field(None, description="Market open time")
    market_close: Optional[str] = Field(None, description="Market close time")
    timezone: Optional[str] = Field(None, description="Market timezone")

    # Metadata
    source: str = Field(default="alpha_vantage", description="Data source")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "companies"
        indexes = [
            "symbol",
            "name",
            "sector",
            "industry",
            "created_at",
        ]


class Watchlist(Document):
    """Watchlist for tracking symbols to monitor"""

    name: str = Field(..., description="Watchlist name")
    description: Optional[str] = Field(None, description="Watchlist description")
    symbols: list[str] = Field(default=[], description="List of symbols to track")

    # Configuration
    auto_update: bool = Field(default=True, description="Auto-update data")
    update_interval: int = Field(default=3600, description="Update interval in seconds")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: Optional[datetime] = Field(None, description="Last data update")

    class Settings:
        name = "watchlists"
        indexes = [
            "name",
            "created_at",
        ]
