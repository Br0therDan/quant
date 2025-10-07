"""
Stock data API schemas
주식 데이터 API 스키마들
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from decimal import Decimal

from .base import (
    DataResponse,
    BulkDataResponse,
    PaginatedResponse,
    SymbolParams,
    MultiSymbolParams,
    DateRangeParams,
    PaginationParams,
    SortParams,
    HistoricalDataRequest,
    PriceData,
)


# Request Schemas
class DailyPriceRequest(HistoricalDataRequest):
    """일봉 데이터 요청 스키마"""

    output_size: Optional[str] = Field(
        "compact", pattern="^(compact|full)$", description="출력 크기"
    )
    adjusted: bool = Field(True, description="수정주가 사용 여부")


class IntradayPriceRequest(SymbolParams, DateRangeParams, PaginationParams):
    """분봉 데이터 요청 스키마"""

    interval: str = Field(
        "1min", pattern="^(1min|5min|15min|30min|60min)$", description="시간 간격"
    )
    extended_hours: bool = Field(False, description="시간외 거래 포함 여부")


class QuoteRequest(SymbolParams):
    """실시간 호가 요청 스키마"""

    include_extended_hours: bool = Field(False, description="시간외 거래 포함 여부")


class BulkQuoteRequest(MultiSymbolParams):
    """대량 실시간 호가 요청 스키마"""

    include_extended_hours: bool = Field(False, description="시간외 거래 포함 여부")
    batch_size: int = Field(50, ge=1, le=100, description="배치 크기")


class DividendRequest(SymbolParams, DateRangeParams, SortParams):
    """배당 정보 요청 스키마"""

    frequency: Optional[str] = Field(None, description="배당 주기 필터")


class SplitRequest(SymbolParams, DateRangeParams, SortParams):
    """주식분할 정보 요청 스키마"""

    pass


# Response Data Models
class DailyPriceData(PriceData):
    """일봉 데이터 응답 모델"""

    symbol: str = Field(..., description="주식 심볼")
    date: datetime = Field(..., description="날짜")
    adjusted_close: Optional[Decimal] = Field(None, description="수정 종가")
    dividend_amount: Optional[Decimal] = Field(None, description="배당금")
    split_coefficient: Optional[Decimal] = Field(None, description="주식분할 계수")
    price_change: Optional[Decimal] = Field(None, description="전일 대비 변동")
    price_change_percent: Optional[Decimal] = Field(None, description="전일 대비 변동률 (%)")


class IntradayPriceData(PriceData):
    """분봉 데이터 응답 모델"""

    symbol: str = Field(..., description="주식 심볼")
    timestamp: datetime = Field(..., description="시각")
    interval: str = Field(..., description="간격")


class QuoteData(BaseModel):
    """실시간 호가 응답 모델"""

    symbol: str = Field(..., description="주식 심볼")
    timestamp: datetime = Field(..., description="시각")

    # 현재 가격 정보
    price: Decimal = Field(..., description="현재가", gt=0)
    change: Optional[Decimal] = Field(None, description="전일 대비 변동")
    change_percent: Optional[Decimal] = Field(None, description="변동률 (%)")

    # 일일 통계
    previous_close: Optional[Decimal] = Field(None, description="전일 종가")
    open_price: Optional[Decimal] = Field(None, description="당일 시가")
    high_price: Optional[Decimal] = Field(None, description="당일 고가")
    low_price: Optional[Decimal] = Field(None, description="당일 저가")
    volume: Optional[int] = Field(None, description="당일 누적 거래량")

    # 호가 정보
    bid_price: Optional[Decimal] = Field(None, description="매수 호가")
    ask_price: Optional[Decimal] = Field(None, description="매도 호가")
    bid_size: Optional[int] = Field(None, description="매수 호가 수량")
    ask_size: Optional[int] = Field(None, description="매도 호가 수량")


class DividendData(BaseModel):
    """배당 정보 응답 모델"""

    symbol: str = Field(..., description="주식 심볼")
    ex_date: datetime = Field(..., description="배당락일")
    payment_date: Optional[datetime] = Field(None, description="배당 지급일")
    record_date: Optional[datetime] = Field(None, description="배당 기준일")
    declaration_date: Optional[datetime] = Field(None, description="배당 선언일")

    amount: Decimal = Field(..., description="배당금", gt=0)
    frequency: Optional[str] = Field(None, description="배당 주기")
    dividend_type: str = Field(default="cash", description="배당 유형")


class SplitData(BaseModel):
    """주식분할 정보 응답 모델"""

    symbol: str = Field(..., description="주식 심볼")
    date: datetime = Field(..., description="분할 실행일")
    ratio: Decimal = Field(..., description="분할 비율", gt=0)
    from_factor: int = Field(..., description="분할 전 주식 수", gt=0)
    to_factor: int = Field(..., description="분할 후 주식 수", gt=0)


# 종합 주식 데이터 모델
class StockOverviewData(BaseModel):
    """주식 종합 정보 응답 모델"""

    symbol: str = Field(..., description="주식 심볼")
    name: str = Field(..., description="회사명")
    exchange: str = Field(..., description="거래소")
    currency: str = Field(..., description="통화")

    # 현재 가격 정보
    current_price: Decimal = Field(..., description="현재가", gt=0)
    price_change: Optional[Decimal] = Field(None, description="가격 변동")
    price_change_percent: Optional[Decimal] = Field(None, description="가격 변동률 (%)")

    # 일중 통계
    day_high: Optional[Decimal] = Field(None, description="일중 최고가")
    day_low: Optional[Decimal] = Field(None, description="일중 최저가")
    day_volume: Optional[int] = Field(None, description="일일 거래량")

    # 52주 통계
    fifty_two_week_high: Optional[Decimal] = Field(None, description="52주 최고가")
    fifty_two_week_low: Optional[Decimal] = Field(None, description="52주 최저가")

    # 기본 지표
    market_cap: Optional[Decimal] = Field(None, description="시가총액")
    pe_ratio: Optional[Decimal] = Field(None, description="PER")
    dividend_yield: Optional[Decimal] = Field(None, description="배당 수익률 (%)")


# Response Schemas
class DailyPriceResponse(DataResponse[DailyPriceData]):
    """일봉 데이터 응답 스키마"""

    pass


class DailyPriceListResponse(BulkDataResponse[DailyPriceData]):
    """일봉 데이터 목록 응답 스키마"""

    pass


class IntradayPriceResponse(DataResponse[IntradayPriceData]):
    """분봉 데이터 응답 스키마"""

    pass


class IntradayPriceListResponse(PaginatedResponse[IntradayPriceData]):
    """분봉 데이터 목록 응답 스키마"""

    pass


class QuoteResponse(DataResponse[QuoteData]):
    """실시간 호가 응답 스키마"""

    pass


class BulkQuoteResponse(BulkDataResponse[QuoteData]):
    """대량 실시간 호가 응답 스키마"""

    pass


class DividendListResponse(PaginatedResponse[DividendData]):
    """배당 정보 목록 응답 스키마"""

    pass


class SplitListResponse(PaginatedResponse[SplitData]):
    """주식분할 정보 목록 응답 스키마"""

    pass


class StockOverviewResponse(DataResponse[StockOverviewData]):
    """주식 종합 정보 응답 스키마"""

    pass


# 특수 Request/Response 스키마들
class StockSearchRequest(BaseModel):
    """주식 검색 요청 스키마"""

    query: str = Field(..., description="검색어", min_length=1, max_length=100)
    search_type: str = Field("all", pattern="^(symbol|name|all)$", description="검색 유형")
    limit: int = Field(20, ge=1, le=100, description="결과 수 제한")


class StockSearchData(BaseModel):
    """주식 검색 결과 데이터"""

    symbol: str = Field(..., description="주식 심볼")
    name: str = Field(..., description="회사명")
    exchange: str = Field(..., description="거래소")
    currency: str = Field(..., description="통화")
    match_score: float = Field(..., description="매칭 점수", ge=0, le=1)


class StockSearchResponse(BulkDataResponse[StockSearchData]):
    """주식 검색 응답 스키마"""

    pass


class MarketStatusData(BaseModel):
    """시장 상태 데이터"""

    market: str = Field(..., description="시장명")
    status: str = Field(..., description="상태 (open, closed, pre_market, after_hours)")
    last_updated: datetime = Field(..., description="마지막 업데이트")
    next_open: Optional[datetime] = Field(None, description="다음 개장 시간")
    next_close: Optional[datetime] = Field(None, description="다음 폐장 시간")


class MarketStatusResponse(BulkDataResponse[MarketStatusData]):
    """시장 상태 응답 스키마"""

    pass


# 배치 처리를 위한 스키마들
class BatchStockRequest(BaseModel):
    """배치 주식 데이터 요청"""

    symbols: List[str] = Field(..., description="주식 심볼 목록")
    data_types: List[str] = Field(..., description="요청할 데이터 유형 목록")
    date_range: Optional[DateRangeParams] = Field(None, description="날짜 범위")
    priority: str = Field(
        "normal", pattern="^(low|normal|high)$", description="처리 우선순위"
    )


class BatchStockStatus(BaseModel):
    """배치 처리 상태"""

    batch_id: str = Field(..., description="배치 ID")
    status: str = Field(..., description="상태 (pending, processing, completed, failed)")
    progress: float = Field(..., description="진행률 (0-1)", ge=0, le=1)
    total_symbols: int = Field(..., description="전체 심볼 수")
    completed_symbols: int = Field(..., description="완료된 심볼 수")
    failed_symbols: List[str] = Field(default_factory=list, description="실패한 심볼 목록")
    estimated_completion: Optional[datetime] = Field(None, description="예상 완료 시간")


class BatchStockResponse(DataResponse[BatchStockStatus]):
    """배치 주식 데이터 응답 스키마"""

    pass
