from datetime import datetime
from typing import List, Optional
from .base_schema import BaseSchema


class UpdateRequest(BaseSchema):
    """Update request model"""

    symbols: Optional[List[str]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class WatchlistUpdate(BaseSchema):
    """Watchlist update model"""

    symbols: List[str]
    name: Optional[str] = "default"
    description: Optional[str] = ""


class WatchlistCreate(BaseSchema):
    """Watchlist creation model"""

    name: str
    symbols: List[str]
    description: str = ""
