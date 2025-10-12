"""
Technical Indicator API schemas
기술적 지표 API 스키마들
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
from decimal import Decimal

from .base import DataResponse, SymbolParams


# Request Schemas
class TechnicalIndicatorRequest(SymbolParams):
    """기술적 지표 요청 기본 스키마"""

    interval: Literal[
        "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
    ] = Field("daily", description="시간 간격")
    time_period: Optional[int] = Field(None, ge=1, le=200, description="시간 주기")
    series_type: Literal["close", "open", "high", "low"] = Field(
        "close", description="계산에 사용할 가격 데이터"
    )
    month: Optional[str] = Field(
        None, pattern=r"^\d{4}-\d{2}$", description="월별 데이터 (YYYY-MM)"
    )


class SMARequest(TechnicalIndicatorRequest):
    """단순이동평균(SMA) 요청"""

    time_period: int = Field(20, ge=1, le=200, description="이동평균 기간")


class EMARequest(TechnicalIndicatorRequest):
    """지수이동평균(EMA) 요청"""

    time_period: int = Field(20, ge=1, le=200, description="이동평균 기간")


class RSIRequest(TechnicalIndicatorRequest):
    """상대강도지수(RSI) 요청"""

    time_period: int = Field(14, ge=2, le=200, description="RSI 계산 기간")


class MACDRequest(TechnicalIndicatorRequest):
    """MACD 요청"""

    fastperiod: Optional[int] = Field(12, ge=2, le=200, description="빠른 이동평균 기간")
    slowperiod: Optional[int] = Field(26, ge=2, le=200, description="느린 이동평균 기간")
    signalperiod: Optional[int] = Field(9, ge=1, le=200, description="시그널 라인 기간")


class BBANDSRequest(TechnicalIndicatorRequest):
    """볼린저밴드(BBANDS) 요청"""

    time_period: int = Field(20, ge=2, le=200, description="이동평균 기간")
    nbdevup: Optional[int] = Field(2, ge=1, le=5, description="상단 밴드 표준편차 배수")
    nbdevdn: Optional[int] = Field(2, ge=1, le=5, description="하단 밴드 표준편차 배수")
    matype: Optional[int] = Field(
        0, ge=0, le=8, description="이동평균 타입 (0=SMA, 1=EMA, etc.)"
    )


class STOCHRequest(BaseModel):
    """스토캐스틱(STOCH) 요청"""

    symbol: str = Field(..., description="주식 심볼")
    interval: Literal[
        "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
    ] = Field("daily", description="시간 간격")
    fastkperiod: Optional[int] = Field(5, ge=1, le=200, description="Fast K 기간")
    slowkperiod: Optional[int] = Field(3, ge=1, le=200, description="Slow K 기간")
    slowdperiod: Optional[int] = Field(3, ge=1, le=200, description="Slow D 기간")
    slowkmatype: Optional[int] = Field(0, ge=0, le=8, description="Slow K 이동평균 타입")
    slowdmatype: Optional[int] = Field(0, ge=0, le=8, description="Slow D 이동평균 타입")
    month: Optional[str] = Field(
        None, pattern=r"^\d{4}-\d{2}$", description="월별 데이터 (YYYY-MM)"
    )


class ADXRequest(TechnicalIndicatorRequest):
    """평균방향성지수(ADX) 요청"""

    time_period: int = Field(14, ge=2, le=200, description="ADX 계산 기간")


class MultipleIndicatorsRequest(BaseModel):
    """여러 지표를 한 번에 요청하는 스키마"""

    symbol: str = Field(..., description="주식 심볼")
    interval: Literal[
        "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
    ] = Field("daily", description="시간 간격")

    # 이동평균
    sma: Optional[List[int]] = Field(None, description="SMA 기간들 (예: [20, 50, 200])")
    ema: Optional[List[int]] = Field(None, description="EMA 기간들 (예: [12, 26])")

    # 모멘텀 오실레이터
    rsi: Optional[int] = Field(None, ge=2, le=200, description="RSI 기간")
    macd: Optional[bool] = Field(None, description="MACD 포함 여부")
    stoch: Optional[bool] = Field(None, description="Stochastic 포함 여부")
    adx: Optional[int] = Field(None, ge=2, le=200, description="ADX 기간")

    # 변동성 지표
    bbands: Optional[int] = Field(None, ge=2, le=200, description="Bollinger Bands 기간")
    atr: Optional[int] = Field(None, ge=1, le=200, description="ATR 기간")

    # 거래량 지표
    obv: Optional[bool] = Field(None, description="OBV 포함 여부")


# Response Data Models
class IndicatorDataPoint(BaseModel):
    """지표 데이터 포인트"""

    date: Optional[datetime] = Field(None, description="날짜 (daily 이상)")
    timestamp: Optional[datetime] = Field(None, description="타임스탬프 (intraday)")
    value: Optional[Decimal] = Field(None, description="지표 값")

    # MACD, Bollinger Bands 등 여러 값이 있는 경우
    values: Optional[Dict[str, Decimal]] = Field(None, description="복수 지표 값들")


class TechnicalIndicatorData(BaseModel):
    """기술적 지표 응답 데이터 모델"""

    symbol: str = Field(..., description="주식 심볼")
    indicator_type: str = Field(..., description="지표 타입 (SMA, EMA, RSI, etc.)")
    interval: str = Field(..., description="시간 간격")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="지표 파라미터")

    # 시계열 데이터
    data: List[IndicatorDataPoint] = Field(default_factory=list, description="시계열 데이터")

    # 메타데이터
    data_points_count: int = Field(default=0, description="데이터 포인트 개수")
    latest_value: Optional[Decimal] = Field(None, description="최신 지표 값")
    latest_date: Optional[datetime] = Field(None, description="최신 데이터 날짜")


class MultipleIndicatorsData(BaseModel):
    """여러 지표 응답 데이터 모델"""

    symbol: str = Field(..., description="주식 심볼")
    interval: str = Field(..., description="시간 간격")
    indicators: Dict[str, TechnicalIndicatorData] = Field(
        default_factory=dict, description="지표별 데이터 (키: 지표명_기간)"
    )


# Response Schemas
class TechnicalIndicatorResponse(DataResponse):
    """단일 기술적 지표 응답"""

    data: Optional[TechnicalIndicatorData] = Field(None, description="지표 데이터")


class MultipleIndicatorsResponse(DataResponse):
    """여러 기술적 지표 응답"""

    data: Optional[MultipleIndicatorsData] = Field(None, description="여러 지표 데이터")


class IndicatorListResponse(DataResponse):
    """지원하는 지표 목록 응답"""

    data: Optional[Dict[str, Any]] = Field(
        None,
        description="지표 카테고리별 목록 (moving_averages, oscillators, volatility, volume)",
    )
