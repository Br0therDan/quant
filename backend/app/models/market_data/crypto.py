"""
Crypto-related data models
암호화폐 관련 데이터 모델들
"""

from datetime import datetime
from typing import Optional
from pydantic import Field, field_validator
from decimal import Decimal, InvalidOperation

from .base import BaseMarketDataDocument, DataQualityMixin


class CryptoExchangeRate(BaseMarketDataDocument, DataQualityMixin):
    """암호화폐 환율 데이터 모델"""

    from_currency: str = Field(..., description="기준 통화 (예: BTC, ETH, USD)")
    to_currency: str = Field(..., description="대상 통화 (예: USD, EUR, BTC)")
    timestamp: datetime = Field(..., description="타임스탬프")

    # 환율 정보
    exchange_rate: Decimal = Field(..., description="환율", gt=0)
    bid_price: Optional[Decimal] = Field(None, description="매수 가격", gt=0)
    ask_price: Optional[Decimal] = Field(None, description="매도 가격", gt=0)

    @field_validator(
        "exchange_rate",
        "bid_price",
        "ask_price",
        mode="before",
    )
    @classmethod
    def convert_decimal128(cls, v):
        """다양한 숫자 타입을 Decimal로 변환"""
        if v is None:
            return v
        try:
            from bson import Decimal128

            if isinstance(v, Decimal128):
                return Decimal(str(v))
        except ImportError:
            pass

        if isinstance(v, (int, float)):
            return Decimal(str(v))
        elif isinstance(v, str):
            try:
                return Decimal(v)
            except (ValueError, TypeError, InvalidOperation):
                return v
        return v

    class Settings:
        name = "crypto_exchange_rate"
        indexes = [
            [("from_currency", 1), ("to_currency", 1), ("timestamp", 1)],
            "from_currency",
            "to_currency",
            "timestamp",
        ]


class CryptoIntradayPrice(BaseMarketDataDocument, DataQualityMixin):
    """암호화폐 인트라데이 가격 데이터 모델"""

    symbol: str = Field(..., description="암호화폐 심볼 (예: BTC, ETH)")
    market: str = Field(..., description="시장/통화 (예: USD, EUR)")
    timestamp: datetime = Field(..., description="타임스탬프")
    interval: str = Field(..., description="시간 간격 (1min, 5min, 15min, 30min, 60min)")

    # OHLCV 데이터 (시장 통화 기준)
    open_market: Decimal = Field(..., description="시가 (시장 통화)", gt=0)
    high_market: Decimal = Field(..., description="고가 (시장 통화)", gt=0)
    low_market: Decimal = Field(..., description="저가 (시장 통화)", gt=0)
    close_market: Decimal = Field(..., description="종가 (시장 통화)", gt=0)
    volume: Decimal = Field(..., description="거래량", ge=0)

    # USD 기준 가격 (옵션)
    open_usd: Optional[Decimal] = Field(None, description="시가 (USD)", gt=0)
    high_usd: Optional[Decimal] = Field(None, description="고가 (USD)", gt=0)
    low_usd: Optional[Decimal] = Field(None, description="저가 (USD)", gt=0)
    close_usd: Optional[Decimal] = Field(None, description="종가 (USD)", gt=0)

    @field_validator(
        "open_market",
        "high_market",
        "low_market",
        "close_market",
        "volume",
        "open_usd",
        "high_usd",
        "low_usd",
        "close_usd",
        mode="before",
    )
    @classmethod
    def convert_decimal128(cls, v):
        """다양한 숫자 타입을 Decimal로 변환"""
        if v is None:
            return v
        try:
            from bson import Decimal128

            if isinstance(v, Decimal128):
                return Decimal(str(v))
        except ImportError:
            pass

        if isinstance(v, (int, float)):
            return Decimal(str(v))
        elif isinstance(v, str):
            try:
                return Decimal(v)
            except (ValueError, TypeError, InvalidOperation):
                return v
        return v

    class Settings:
        name = "crypto_price_intraday"
        indexes = [
            [("symbol", 1), ("market", 1), ("timestamp", 1), ("interval", 1)],
            "symbol",
            "market",
            "timestamp",
            "interval",
        ]


class CryptoDailyPrice(BaseMarketDataDocument, DataQualityMixin):
    """암호화폐 일일 가격 데이터 모델"""

    symbol: str = Field(..., description="암호화폐 심볼 (예: BTC, ETH)")
    market: str = Field(..., description="시장/통화 (예: USD, EUR)")
    date: datetime = Field(..., description="날짜")

    # OHLCV 데이터 (시장 통화 기준)
    open_market: Decimal = Field(..., description="시가 (시장 통화)", gt=0)
    high_market: Decimal = Field(..., description="고가 (시장 통화)", gt=0)
    low_market: Decimal = Field(..., description="저가 (시장 통화)", gt=0)
    close_market: Decimal = Field(..., description="종가 (시장 통화)", gt=0)
    volume: Decimal = Field(..., description="거래량", ge=0)
    market_cap: Optional[Decimal] = Field(None, description="시가총액 (시장 통화)", ge=0)

    # USD 기준 가격
    open_usd: Optional[Decimal] = Field(None, description="시가 (USD)", gt=0)
    high_usd: Optional[Decimal] = Field(None, description="고가 (USD)", gt=0)
    low_usd: Optional[Decimal] = Field(None, description="저가 (USD)", gt=0)
    close_usd: Optional[Decimal] = Field(None, description="종가 (USD)", gt=0)
    market_cap_usd: Optional[Decimal] = Field(None, description="시가총액 (USD)", ge=0)

    # 계산된 필드들
    price_change: Optional[Decimal] = Field(None, description="전일 대비 변동")
    price_change_percent: Optional[Decimal] = Field(None, description="전일 대비 변동률 (%)")

    @field_validator(
        "open_market",
        "high_market",
        "low_market",
        "close_market",
        "volume",
        "market_cap",
        "open_usd",
        "high_usd",
        "low_usd",
        "close_usd",
        "market_cap_usd",
        "price_change",
        "price_change_percent",
        mode="before",
    )
    @classmethod
    def convert_decimal128(cls, v):
        """다양한 숫자 타입을 Decimal로 변환"""
        if v is None:
            return v
        try:
            from bson import Decimal128

            if isinstance(v, Decimal128):
                return Decimal(str(v))
        except ImportError:
            pass

        if isinstance(v, (int, float)):
            return Decimal(str(v))
        elif isinstance(v, str):
            try:
                return Decimal(v)
            except (ValueError, TypeError, InvalidOperation):
                return v
        return v

    class Settings:
        name = "crypto_price_daily"
        indexes = [
            [("symbol", 1), ("market", 1), ("date", 1)],
            "symbol",
            "market",
            "date",
        ]


class CryptoWeeklyPrice(BaseMarketDataDocument, DataQualityMixin):
    """암호화폐 주간 가격 데이터 모델"""

    symbol: str = Field(..., description="암호화폐 심볼")
    market: str = Field(..., description="시장/통화")
    date: datetime = Field(..., description="주간 시작일")

    # OHLCV 데이터 (시장 통화 기준)
    open_market: Decimal = Field(..., description="시가 (시장 통화)", gt=0)
    high_market: Decimal = Field(..., description="고가 (시장 통화)", gt=0)
    low_market: Decimal = Field(..., description="저가 (시장 통화)", gt=0)
    close_market: Decimal = Field(..., description="종가 (시장 통화)", gt=0)
    volume: Decimal = Field(..., description="거래량", ge=0)
    market_cap: Optional[Decimal] = Field(None, description="시가총액 (시장 통화)", ge=0)

    # USD 기준 가격
    open_usd: Optional[Decimal] = Field(None, description="시가 (USD)", gt=0)
    high_usd: Optional[Decimal] = Field(None, description="고가 (USD)", gt=0)
    low_usd: Optional[Decimal] = Field(None, description="저가 (USD)", gt=0)
    close_usd: Optional[Decimal] = Field(None, description="종가 (USD)", gt=0)
    market_cap_usd: Optional[Decimal] = Field(None, description="시가총액 (USD)", ge=0)

    @field_validator(
        "open_market",
        "high_market",
        "low_market",
        "close_market",
        "volume",
        "market_cap",
        "open_usd",
        "high_usd",
        "low_usd",
        "close_usd",
        "market_cap_usd",
        mode="before",
    )
    @classmethod
    def convert_decimal128(cls, v):
        """다양한 숫자 타입을 Decimal로 변환"""
        if v is None:
            return v
        try:
            from bson import Decimal128

            if isinstance(v, Decimal128):
                return Decimal(str(v))
        except ImportError:
            pass

        if isinstance(v, (int, float)):
            return Decimal(str(v))
        elif isinstance(v, str):
            try:
                return Decimal(v)
            except (ValueError, TypeError, InvalidOperation):
                return v
        return v

    class Settings:
        name = "crypto_price_weekly"
        indexes = [
            [("symbol", 1), ("market", 1), ("date", 1)],
            "symbol",
            "market",
            "date",
        ]


class CryptoMonthlyPrice(BaseMarketDataDocument, DataQualityMixin):
    """암호화폐 월간 가격 데이터 모델"""

    symbol: str = Field(..., description="암호화폐 심볼")
    market: str = Field(..., description="시장/통화")
    date: datetime = Field(..., description="월간 시작일")

    # OHLCV 데이터 (시장 통화 기준)
    open_market: Decimal = Field(..., description="시가 (시장 통화)", gt=0)
    high_market: Decimal = Field(..., description="고가 (시장 통화)", gt=0)
    low_market: Decimal = Field(..., description="저가 (시장 통화)", gt=0)
    close_market: Decimal = Field(..., description="종가 (시장 통화)", gt=0)
    volume: Decimal = Field(..., description="거래량", ge=0)
    market_cap: Optional[Decimal] = Field(None, description="시가총액 (시장 통화)", ge=0)

    # USD 기준 가격
    open_usd: Optional[Decimal] = Field(None, description="시가 (USD)", gt=0)
    high_usd: Optional[Decimal] = Field(None, description="고가 (USD)", gt=0)
    low_usd: Optional[Decimal] = Field(None, description="저가 (USD)", gt=0)
    close_usd: Optional[Decimal] = Field(None, description="종가 (USD)", gt=0)
    market_cap_usd: Optional[Decimal] = Field(None, description="시가총액 (USD)", ge=0)

    @field_validator(
        "open_market",
        "high_market",
        "low_market",
        "close_market",
        "volume",
        "market_cap",
        "open_usd",
        "high_usd",
        "low_usd",
        "close_usd",
        "market_cap_usd",
        mode="before",
    )
    @classmethod
    def convert_decimal128(cls, v):
        """다양한 숫자 타입을 Decimal로 변환"""
        if v is None:
            return v
        try:
            from bson import Decimal128

            if isinstance(v, Decimal128):
                return Decimal(str(v))
        except ImportError:
            pass

        if isinstance(v, (int, float)):
            return Decimal(str(v))
        elif isinstance(v, str):
            try:
                return Decimal(v)
            except (ValueError, TypeError, InvalidOperation):
                return v
        return v

    class Settings:
        name = "crypto_price_monthly"
        indexes = [
            [("symbol", 1), ("market", 1), ("date", 1)],
            "symbol",
            "market",
            "date",
        ]
