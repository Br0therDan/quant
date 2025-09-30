"""
Backtest API Schemas
"""

from pydantic import BaseModel, Field


# Request Schemas
class BaseSchema(BaseModel):
    user_id: str | None = Field(None, description="사용자 ID")
