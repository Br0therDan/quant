"""
Watchlist Models
"""

from datetime import datetime
from typing import List, Optional
from .base_model import BaseDocument
from pydantic import Field


class Watchlist(BaseDocument):
    """Watchlist for tracking symbols to monitor"""

    name: str = Field(..., description="Watchlist name")
    description: Optional[str] = Field(None, description="Watchlist description")
    symbols: List[str] = Field(..., description="List of stock symbols")

    # Configuration
    auto_update: bool = Field(default=True, description="Auto-update data")
    update_interval: int = Field(default=3600, description="Update interval in seconds")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: Optional[datetime] = Field(
        default=None, description="Last data update"
    )

    class Settings:
        name = "watchlists"
        indexes = [
            "name",
            "created_at",
        ]
