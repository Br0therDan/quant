"""
Base schemas for market data API
시장 데이터 API용 기본 스키마들
"""

from datetime import datetime
from typing import Optional, List, Generic, TypeVar
from pydantic import BaseModel, Field
from decimal import Decimal


# Generic type for paginated responses
T = TypeVar("T")


class BaseResponse(BaseModel):
    """API 응답 기본 스키마"""

    success: bool = Field(True, description="요청 성공 여부")
    message: Optional[str] = Field(None, description="응답 메시지")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="응답 시간")


class ErrorResponse(BaseResponse):
    """에러 응답 스키마"""

    success: bool = Field(False, description="요청 성공 여부")
    error_code: Optional[str] = Field(None, description="에러 코드")
    details: Optional[dict] = Field(None, description="에러 상세 정보")


class PaginationParams(BaseModel):
    """페이지네이션 파라미터"""

    page: int = Field(1, ge=1, description="페이지 번호")
    size: int = Field(50, ge=1, le=1000, description="페이지 크기")


class PaginationInfo(BaseModel):
    """페이지네이션 정보"""

    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")
    total: int = Field(..., description="전체 항목 수")
    pages: int = Field(..., description="전체 페이지 수")
    has_next: bool = Field(..., description="다음 페이지 존재 여부")
    has_prev: bool = Field(..., description="이전 페이지 존재 여부")


class PaginatedResponse(BaseResponse, Generic[T]):
    """페이지네이션 응답 스키마"""

    data: List[T] = Field(..., description="데이터 목록")
    pagination: PaginationInfo = Field(..., description="페이지네이션 정보")


class DateRangeParams(BaseModel):
    """날짜 범위 파라미터"""

    start_date: Optional[datetime] = Field(None, description="시작 날짜")
    end_date: Optional[datetime] = Field(None, description="종료 날짜")


class SymbolParams(BaseModel):
    """주식 심볼 파라미터"""

    symbol: str = Field(..., description="주식 심볼", min_length=1, max_length=10)


class MultiSymbolParams(BaseModel):
    """다중 주식 심볼 파라미터"""

    symbols: List[str] = Field(..., description="주식 심볼 목록")


class SortParams(BaseModel):
    """정렬 파라미터"""

    sort_by: Optional[str] = Field("date", description="정렬 기준 필드")
    sort_order: Optional[str] = Field(
        "desc", pattern="^(asc|desc)$", description="정렬 순서"
    )


class FilterParams(BaseModel):
    """필터링 파라미터"""

    country: Optional[str] = Field(None, description="국가 코드")
    exchange: Optional[str] = Field(None, description="거래소")
    sector: Optional[str] = Field(None, description="섹터")
    industry: Optional[str] = Field(None, description="산업")


class DataQualityInfo(BaseModel):
    """데이터 품질 정보"""

    quality_score: Decimal = Field(..., description="품질 점수 (0-100)")
    last_updated: datetime = Field(..., description="마지막 업데이트 시간")
    data_source: str = Field(..., description="데이터 출처")
    confidence_level: Optional[str] = Field(None, description="신뢰도 수준")


class CacheInfo(BaseModel):
    """캐시 정보"""

    cached: bool = Field(..., description="캐시된 데이터 여부")
    cache_hit: bool = Field(..., description="캐시 히트 여부")
    cache_timestamp: Optional[datetime] = Field(None, description="캐시 생성 시간")
    cache_ttl: Optional[int] = Field(None, description="캐시 TTL (초)")


class MetadataInfo(BaseModel):
    """메타데이터 정보"""

    data_quality: DataQualityInfo = Field(..., description="데이터 품질 정보")
    cache_info: CacheInfo = Field(..., description="캐시 정보")
    processing_time_ms: Optional[float] = Field(None, description="처리 시간 (밀리초)")


class DataResponse(BaseResponse, Generic[T]):
    """데이터 응답 스키마 (메타데이터 포함)"""

    data: T = Field(..., description="데이터")
    metadata: MetadataInfo = Field(..., description="메타데이터")


class BulkDataResponse(BaseResponse, Generic[T]):
    """대량 데이터 응답 스키마"""

    data: List[T] = Field(..., description="데이터 목록")
    metadata: MetadataInfo = Field(..., description="메타데이터")
    count: int = Field(..., description="데이터 개수")


# 공통 Request 스키마들
class RefreshDataRequest(BaseModel):
    """데이터 새로고침 요청"""

    force_refresh: bool = Field(False, description="강제 새로고침 여부")
    include_cache_warmup: bool = Field(True, description="캐시 워밍업 포함 여부")


class BulkSymbolRequest(BaseModel):
    """대량 심볼 처리 요청"""

    symbols: List[str] = Field(..., description="심볼 목록")
    parallel_processing: bool = Field(True, description="병렬 처리 여부")
    fail_on_error: bool = Field(False, description="오류 시 전체 실패 여부")


class HistoricalDataRequest(DateRangeParams, SymbolParams, SortParams):
    """과거 데이터 요청"""

    interval: Optional[str] = Field("daily", description="데이터 간격")
    include_splits: bool = Field(True, description="주식분할 포함 여부")
    include_dividends: bool = Field(True, description="배당 포함 여부")
    adjusted: bool = Field(True, description="수정주가 사용 여부")


# 공통 응답 데이터 모델들
class PriceData(BaseModel):
    """가격 데이터 공통 스키마"""

    open: Decimal = Field(..., description="시가", gt=0)
    high: Decimal = Field(..., description="고가", gt=0)
    low: Decimal = Field(..., description="저가", gt=0)
    close: Decimal = Field(..., description="종가", gt=0)
    volume: int = Field(..., description="거래량", ge=0)


class FinancialMetrics(BaseModel):
    """재무 지표 공통 스키마"""

    revenue: Optional[Decimal] = Field(None, description="매출")
    net_income: Optional[Decimal] = Field(None, description="순이익")
    eps: Optional[Decimal] = Field(None, description="주당순이익")
    pe_ratio: Optional[Decimal] = Field(None, description="PER", ge=0)
    market_cap: Optional[Decimal] = Field(None, description="시가총액", ge=0)


class EconomicIndicatorData(BaseModel):
    """경제지표 데이터 공통 스키마"""

    indicator_name: str = Field(..., description="지표명")
    value: Decimal = Field(..., description="지표값")
    unit: Optional[str] = Field(None, description="단위")
    frequency: str = Field(..., description="발표 주기")
    country: str = Field(..., description="국가")


class SentimentData(BaseModel):
    """감정 분석 데이터 공통 스키마"""

    sentiment_score: Decimal = Field(..., description="감정 점수")
    sentiment_label: str = Field(..., description="감정 라벨")
    confidence: Optional[Decimal] = Field(None, description="신뢰도", ge=0, le=1)
    source: str = Field(..., description="데이터 출처")
