from datetime import datetime
from typing import List, Optional
from .base_schema import BaseSchema


class UpdateRequest(BaseSchema):
    """Update request model"""

    symbols: Optional[List[str]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
