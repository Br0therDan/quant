"""
Technical Indicator data models
기술적 지표 데이터 모델들
"""

from datetime import datetime
from typing import Optional, Literal, Dict, Any
from pydantic import Field, field_validator
from decimal import Decimal

from .base import BaseMarketDataDocument, DataQualityMixin


class TechnicalIndicator(BaseMarketDataDocument, DataQualityMixin):
    """기술적 지표 데이터 모델

    Alpha Vantage의 기술적 지표 데이터를 저장합니다.
    DuckDB에 캐시되며, MongoDB에는 메타데이터만 저장됩니다.
    """

    symbol: str = Field(..., description="주식 심볼 (예: AAPL, TSLA)")
    indicator_type: str = Field(
        ...,
        description="지표 타입 (SMA, EMA, RSI, MACD, BBANDS, ADX, STOCH, etc.)",
    )
    interval: Literal[
        "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
    ] = Field(..., description="시간 간격")

    # 지표별 파라미터 (JSON 형태로 저장)
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="지표 계산 파라미터 (time_period, series_type, fastperiod, etc.)",
    )

    # 데이터 포인트 수 (메타데이터)
    data_points_count: int = Field(default=0, description="저장된 데이터 포인트 수", ge=0)

    # 시계열 데이터는 DuckDB에 저장되므로 여기서는 제외
    # (필요 시 최신 몇 개만 샘플로 저장 가능)
    latest_value: Optional[Decimal] = Field(None, description="최신 지표 값")
    latest_date: Optional[datetime] = Field(None, description="최신 데이터 날짜")

    # 캐시 메타데이터
    cache_ttl: int = Field(default=86400, description="캐시 유효 기간 (초, 기본값: 24시간)", gt=0)
    last_fetched: Optional[datetime] = Field(None, description="마지막 데이터 갱신 시각")

    @field_validator("latest_value", mode="before")
    @classmethod
    def convert_decimal128(cls, v):
        """다양한 숫자 타입을 Decimal로 변환"""
        if v is None:
            return v
        try:
            from bson import Decimal128

            if isinstance(v, Decimal128):
                return Decimal(str(v.to_decimal()))
        except ImportError:
            pass

        try:
            return Decimal(str(v))
        except Exception:
            return v

    class Settings:
        name = "technical_indicators"
        indexes = [
            [("symbol", 1), ("indicator_type", 1), ("interval", 1)],
            "symbol",
            "indicator_type",
            "last_fetched",
        ]


class IndicatorDataPoint(BaseMarketDataDocument):
    """기술적 지표 개별 데이터 포인트 (선택적 MongoDB 저장용)

    대부분의 시계열 데이터는 DuckDB에 저장되지만,
    특정 케이스에서 MongoDB에 저장이 필요한 경우 사용합니다.
    """

    symbol: str = Field(..., description="주식 심볼")
    indicator_type: str = Field(..., description="지표 타입")
    interval: str = Field(..., description="시간 간격")

    # 시간 정보
    date: Optional[datetime] = Field(None, description="날짜 (daily, weekly, monthly)")
    timestamp: Optional[datetime] = Field(None, description="타임스탬프 (intraday)")

    # 지표 값들 (지표 타입에 따라 다름)
    values: Dict[str, Decimal] = Field(
        default_factory=dict, description="지표 값들 (예: {sma: 150.25, ema: 151.30})"
    )

    @field_validator("values", mode="before")
    @classmethod
    def convert_values_to_decimal(cls, v):
        """값들을 Decimal로 변환"""
        if not isinstance(v, dict):
            return v

        converted = {}
        for key, value in v.items():
            if value is None:
                converted[key] = None
                continue

            try:
                from bson import Decimal128

                if isinstance(value, Decimal128):
                    converted[key] = Decimal(str(value.to_decimal()))
                    continue
            except ImportError:
                pass

            try:
                converted[key] = Decimal(str(value))
            except Exception:
                converted[key] = value

        return converted

    class Settings:
        name = "technical_indicator_data_points"
        indexes = [
            [
                ("symbol", 1),
                ("indicator_type", 1),
                ("interval", 1),
                ("date", -1),
            ],
            [
                ("symbol", 1),
                ("indicator_type", 1),
                ("interval", 1),
                ("datetime", -1),
            ],
        ]
