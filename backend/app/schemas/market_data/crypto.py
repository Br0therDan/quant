"""
Crypto data API schemas
암호화폐 데이터 API 스키마들
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from decimal import Decimal

from .base import (
    DataResponse,
    BulkDataResponse,
)


# Request Schemas
class CryptoExchangeRateRequest(BaseModel):
    """암호화폐 환율 요청 스키마"""

    from_currency: str = Field(..., description="기준 통화 (예: BTC, ETH, USD)")
    to_currency: str = Field(..., description="대상 통화 (예: USD, EUR, BTC)")


class CryptoBulkExchangeRateRequest(BaseModel):
    """대량 암호화폐 환율 요청 스키마"""

    crypto_symbols: List[str] = Field(
        ..., description="암호화폐 심볼 리스트 (예: ['BTC', 'ETH', 'LTC'])"
    )
    target_currency: str = Field(default="USD", description="목표 통화 (예: USD, EUR, KRW)")


class CryptoDailyPriceRequest(BaseModel):
    """암호화폐 일봉 데이터 요청 스키마"""

    symbol: str = Field(..., description="암호화폐 심볼 (예: BTC, ETH)")
    market: str = Field(default="USD", description="시장/통화 (예: USD, EUR, KRW)")
    start_date: Optional[datetime] = Field(None, description="시작 날짜")
    end_date: Optional[datetime] = Field(None, description="종료 날짜")


class CryptoWeeklyPriceRequest(BaseModel):
    """암호화폐 주봉 데이터 요청 스키마"""

    symbol: str = Field(..., description="암호화폐 심볼 (예: BTC, ETH)")
    market: str = Field(default="USD", description="시장/통화 (예: USD, EUR)")
    start_date: Optional[datetime] = Field(None, description="시작 날짜")
    end_date: Optional[datetime] = Field(None, description="종료 날짜")


class CryptoMonthlyPriceRequest(BaseModel):
    """암호화폐 월봉 데이터 요청 스키마"""

    symbol: str = Field(..., description="암호화폐 심볼 (예: BTC, ETH)")
    market: str = Field(default="USD", description="시장/통화 (예: USD, EUR)")
    start_date: Optional[datetime] = Field(None, description="시작 날짜")
    end_date: Optional[datetime] = Field(None, description="종료 날짜")


class CryptoIntradayPriceRequest(BaseModel):
    """암호화폐 인트라데이 데이터 요청 스키마"""

    symbol: str = Field(..., description="암호화폐 심볼 (예: BTC, ETH)")
    market: str = Field(..., description="시장/통화 (예: USD, EUR)")
    interval: str = Field(
        ...,
        pattern="^(1min|5min|15min|30min|60min)$",
        description="시간 간격 (1min, 5min, 15min, 30min, 60min)",
    )
    outputsize: Optional[str] = Field(
        "compact", pattern="^(compact|full)$", description="출력 크기"
    )
    start_date: Optional[datetime] = Field(None, description="시작 시간")
    end_date: Optional[datetime] = Field(None, description="종료 시간")


# Response Data Models
class CryptoExchangeRateData(BaseModel):
    """암호화폐 환율 응답 모델"""

    from_currency: str = Field(..., description="기준 통화")
    to_currency: str = Field(..., description="대상 통화")
    timestamp: datetime = Field(..., description="타임스탬프")
    exchange_rate: Decimal = Field(..., description="환율")
    bid_price: Optional[Decimal] = Field(None, description="매수 가격")
    ask_price: Optional[Decimal] = Field(None, description="매도 가격")


class CryptoIntradayPriceData(BaseModel):
    """암호화폐 인트라데이 가격 응답 모델"""

    symbol: str = Field(..., description="암호화폐 심볼")
    market: str = Field(..., description="시장/통화")
    timestamp: datetime = Field(..., description="타임스탬프")
    interval: str = Field(..., description="간격")

    # 시장 통화 기준 OHLCV
    open_market: Decimal = Field(..., description="시가 (시장 통화)")
    high_market: Decimal = Field(..., description="고가 (시장 통화)")
    low_market: Decimal = Field(..., description="저가 (시장 통화)")
    close_market: Decimal = Field(..., description="종가 (시장 통화)")
    volume: Decimal = Field(..., description="거래량")

    # USD 기준 가격 (옵션)
    open_usd: Optional[Decimal] = Field(None, description="시가 (USD)")
    high_usd: Optional[Decimal] = Field(None, description="고가 (USD)")
    low_usd: Optional[Decimal] = Field(None, description="저가 (USD)")
    close_usd: Optional[Decimal] = Field(None, description="종가 (USD)")


class CryptoDailyPriceData(BaseModel):
    """암호화폐 일봉 데이터 응답 모델"""

    symbol: str = Field(..., description="암호화폐 심볼")
    market: str = Field(..., description="시장/통화")
    date: datetime = Field(..., description="날짜")

    # 시장 통화 기준 OHLCV
    open_market: Decimal = Field(..., description="시가 (시장 통화)")
    high_market: Decimal = Field(..., description="고가 (시장 통화)")
    low_market: Decimal = Field(..., description="저가 (시장 통화)")
    close_market: Decimal = Field(..., description="종가 (시장 통화)")
    volume: Decimal = Field(..., description="거래량")
    market_cap: Optional[Decimal] = Field(None, description="시가총액 (시장 통화)")

    # USD 기준 가격
    open_usd: Optional[Decimal] = Field(None, description="시가 (USD)")
    high_usd: Optional[Decimal] = Field(None, description="고가 (USD)")
    low_usd: Optional[Decimal] = Field(None, description="저가 (USD)")
    close_usd: Optional[Decimal] = Field(None, description="종가 (USD)")
    market_cap_usd: Optional[Decimal] = Field(None, description="시가총액 (USD)")

    # 계산된 필드
    price_change: Optional[Decimal] = Field(None, description="전일 대비 변동")
    price_change_percent: Optional[Decimal] = Field(None, description="전일 대비 변동률 (%)")


class CryptoWeeklyPriceData(BaseModel):
    """암호화폐 주봉 데이터 응답 모델"""

    symbol: str = Field(..., description="암호화폐 심볼")
    market: str = Field(..., description="시장/통화")
    date: datetime = Field(..., description="주간 시작일")

    # 시장 통화 기준 OHLCV
    open_market: Decimal = Field(..., description="시가 (시장 통화)")
    high_market: Decimal = Field(..., description="고가 (시장 통화)")
    low_market: Decimal = Field(..., description="저가 (시장 통화)")
    close_market: Decimal = Field(..., description="종가 (시장 통화)")
    volume: Decimal = Field(..., description="거래량")
    market_cap: Optional[Decimal] = Field(None, description="시가총액 (시장 통화)")

    # USD 기준 가격
    open_usd: Optional[Decimal] = Field(None, description="시가 (USD)")
    high_usd: Optional[Decimal] = Field(None, description="고가 (USD)")
    low_usd: Optional[Decimal] = Field(None, description="저가 (USD)")
    close_usd: Optional[Decimal] = Field(None, description="종가 (USD)")
    market_cap_usd: Optional[Decimal] = Field(None, description="시가총액 (USD)")


class CryptoMonthlyPriceData(BaseModel):
    """암호화폐 월봉 데이터 응답 모델"""

    symbol: str = Field(..., description="암호화폐 심볼")
    market: str = Field(..., description="시장/통화")
    date: datetime = Field(..., description="월간 시작일")

    # 시장 통화 기준 OHLCV
    open_market: Decimal = Field(..., description="시가 (시장 통화)")
    high_market: Decimal = Field(..., description="고가 (시장 통화)")
    low_market: Decimal = Field(..., description="저가 (시장 통화)")
    close_market: Decimal = Field(..., description="종가 (시장 통화)")
    volume: Decimal = Field(..., description="거래량")
    market_cap: Optional[Decimal] = Field(None, description="시가총액 (시장 통화)")

    # USD 기준 가격
    open_usd: Optional[Decimal] = Field(None, description="시가 (USD)")
    high_usd: Optional[Decimal] = Field(None, description="고가 (USD)")
    low_usd: Optional[Decimal] = Field(None, description="저가 (USD)")
    close_usd: Optional[Decimal] = Field(None, description="종가 (USD)")
    market_cap_usd: Optional[Decimal] = Field(None, description="시가총액 (USD)")


# Response Wrappers
class CryptoExchangeRateResponse(DataResponse):
    """암호화폐 환율 응답"""

    data: CryptoExchangeRateData


class CryptoBulkExchangeRateResponse(BulkDataResponse):
    """대량 암호화폐 환율 응답"""

    data: List[CryptoExchangeRateData]


class CryptoIntradayPriceResponse(BulkDataResponse):
    """암호화폐 인트라데이 가격 응답"""

    data: List[CryptoIntradayPriceData]


class CryptoDailyPriceResponse(BulkDataResponse):
    """암호화폐 일봉 데이터 응답"""

    data: List[CryptoDailyPriceData]


class CryptoWeeklyPriceResponse(BulkDataResponse):
    """암호화폐 주봉 데이터 응답"""

    data: List[CryptoWeeklyPriceData]


class CryptoMonthlyPriceResponse(BulkDataResponse):
    """암호화폐 월봉 데이터 응답"""

    data: List[CryptoMonthlyPriceData]


# Bitcoin & Ethereum Convenience Responses
class BitcoinPriceResponse(BulkDataResponse):
    """비트코인 가격 응답"""

    data: List[CryptoDailyPriceData]


class EthereumPriceResponse(BulkDataResponse):
    """이더리움 가격 응답"""

    data: List[CryptoDailyPriceData]
