from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class UpdateRequest(BaseModel):
    """Update request model"""

    symbols: Optional[List[str]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class WatchlistUpdate(BaseModel):
    """Watchlist update model"""

    symbols: List[str]
    name: Optional[str] = "default"
    description: Optional[str] = ""


class WatchlistCreate(BaseModel):
    """Watchlist creation model"""

    name: str
    symbols: List[str]
    description: str = ""
