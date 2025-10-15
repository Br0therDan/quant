from datetime import datetime
from typing import List, Optional
from pydantic import ConfigDict
from app.schemas.base_schema import BaseSchema


class WatchlistUpdate(BaseSchema):
    """워치리스트 업데이트 모델"""

    symbols: List[str]
    name: Optional[str] = "default"
    description: Optional[str] = ""


class WatchlistCreate(BaseSchema):
    """워치리스트 생성 모델"""

    name: str
    symbols: List[str]
    description: str = ""


class WatchlistResponse(BaseSchema):
    """워치리스트 응답 모델"""

    name: str
    symbols: List[str]
    description: Optional[str] = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class WatchlistListResponse(BaseSchema):
    """워치리스트 목록 응답 모델"""

    watchlists: List[WatchlistResponse] = []
    total_count: int = 0

    model_config = ConfigDict(from_attributes=True)
