"""
Backtest API Schemas
"""

from pydantic import BaseModel


# Request Schemas
class BaseSchema(BaseModel):
    user_id: str | None = None
