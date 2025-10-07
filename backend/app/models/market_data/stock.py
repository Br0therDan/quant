"""
Stock-related data models
주식 관련 데이터 모델들
"""

from datetime import datetime
from typing import Optional
from pydantic import Field, field_validator
from decimal import Decimal

from .base import BaseMarketDataDocument, DataQualityMixin


class DailyPrice(BaseMarketDataDocument, DataQualityMixin):
    """일일 주가 데이터 모델"""

    symbol: str = Field(..., description="주식 심볼")
    date: datetime = Field(..., description="날짜")

    # OHLCV 데이터
    open_price: Decimal = Field(..., alias="open", description="시가", gt=0)
    high_price: Decimal = Field(..., alias="high", description="고가", gt=0)
    low_price: Decimal = Field(..., alias="low", description="저가", gt=0)
    close_price: Decimal = Field(..., alias="close", description="종가", gt=0)
    volume: int = Field(..., description="거래량", ge=0)

    # 추가 데이터
    adjusted_close: Optional[Decimal] = Field(None, description="수정 종가")
    dividend_amount: Optional[Decimal] = Field(None, description="배당금")
    split_coefficient: Optional[Decimal] = Field(None, description="주식분할 계수", gt=0)

    # 계산된 필드들
    price_change: Optional[Decimal] = Field(None, description="전일 대비 변동")
    price_change_percent: Optional[Decimal] = Field(None, description="전일 대비 변동률 (%)")

    class Settings:
        name = "daily_prices"
        indexes = [
            [("symbol", 1), ("date", 1)],  # 복합 인덱스 (고유성 보장)
            "symbol",
            "date",
            "volume",
            "created_at",
        ]

    @field_validator("high_price", "low_price", "close_price")
    def validate_prices(cls, v, values):
        """가격 데이터 검증"""
        if "open_price" in values:
            open_price = values["open_price"]
            # 고가는 시가보다 크거나 같아야 함
            if v < open_price and cls.__name__ == "high_price":
                raise ValueError("고가는 시가보다 작을 수 없습니다")
        return v

    def calculate_quality_score(self) -> float:
        """데이터 품질 점수 계산"""
        score = 100.0

        # 가격 일관성 검증
        if self.high_price < max(self.open_price, self.close_price):
            score -= 20
        if self.low_price > min(self.open_price, self.close_price):
            score -= 20
        if self.volume == 0:
            score -= 10

        return max(score, 0.0)


class IntradayPrice(BaseMarketDataDocument, DataQualityMixin):
    """실시간/분봉 주가 데이터 모델"""

    symbol: str = Field(..., description="주식 심볼")
    timestamp: datetime = Field(..., description="타임스탬프")
    interval: str = Field(..., description="시간 간격 (1min, 5min, 15min, 30min, 60min)")

    # OHLCV 데이터
    open_price: Decimal = Field(..., alias="open", description="시가", gt=0)
    high_price: Decimal = Field(..., alias="high", description="고가", gt=0)
    low_price: Decimal = Field(..., alias="low", description="저가", gt=0)
    close_price: Decimal = Field(..., alias="close", description="종가", gt=0)
    volume: int = Field(..., description="거래량", ge=0)

    class Settings:
        name = "intraday_prices"
        indexes = [
            [("symbol", 1), ("timestamp", 1), ("interval", 1)],
            "symbol",
            "timestamp",
            "interval",
        ]


class Quote(BaseMarketDataDocument, DataQualityMixin):
    """실시간 호가 정보 모델"""

    symbol: str = Field(..., description="주식 심볼")
    timestamp: datetime = Field(..., description="타임스탬프")

    # 현재 가격 정보
    price: Decimal = Field(..., description="현재가", gt=0)
    change: Optional[Decimal] = Field(None, description="전일 대비 변동")
    change_percent: Optional[Decimal] = Field(None, description="전일 대비 변동률 (%)")

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

    class Settings:
        name = "quotes"
        indexes = [
            [("symbol", 1), ("timestamp", -1)],  # 최신 순 정렬
            "symbol",
            "timestamp",
        ]


class Dividend(BaseMarketDataDocument):
    """배당 정보 모델"""

    symbol: str = Field(..., description="주식 심볼")
    ex_date: datetime = Field(..., description="배당락일")
    payment_date: Optional[datetime] = Field(None, description="배당 지급일")
    record_date: Optional[datetime] = Field(None, description="배당 기준일")
    declaration_date: Optional[datetime] = Field(None, description="배당 선언일")

    amount: Decimal = Field(..., description="배당금", gt=0)
    frequency: Optional[str] = Field(
        None, description="배당 주기 (quarterly, monthly, annual)"
    )
    dividend_type: str = Field(default="cash", description="배당 유형 (cash, stock)")

    class Settings:
        name = "dividends"
        indexes = [[("symbol", 1), ("ex_date", 1)], "symbol", "ex_date"]


class Split(BaseMarketDataDocument):
    """주식 분할 정보 모델"""

    symbol: str = Field(..., description="주식 심볼")
    date: datetime = Field(..., description="분할 실행일")
    ratio: Decimal = Field(..., description="분할 비율", gt=0)
    from_factor: int = Field(..., description="분할 전 주식 수", gt=0)
    to_factor: int = Field(..., description="분할 후 주식 수", gt=0)

    class Settings:
        name = "splits"
        indexes = [[("symbol", 1), ("date", 1)], "symbol", "date"]
