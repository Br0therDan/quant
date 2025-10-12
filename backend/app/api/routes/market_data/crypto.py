"""
Crypto API Routes
암호화폐 데이터 관련 API 엔드포인트
"""

import logging
from datetime import date
from typing import List, Literal, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Path
from pydantic import BaseModel

from app.services.service_factory import service_factory


router = APIRouter()
logger = logging.getLogger(__name__)


# 임시 응답 모델들
class CryptoHistoricalDataResponse(BaseModel):
    symbol: str
    market: str
    data: List[Dict[str, Any]]
    count: int
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    frequency: str


@router.get(
    "/exchange-rate/{from_currency}/{to_currency}",
    response_model=Dict[str, Any],
    description="암호화폐/법정화폐 간의 실시간 환율을 조회합니다.",
)
async def get_exchange_rate(
    from_currency: str = Path(..., description="기준 통화 (예: BTC, ETH, USD)"),
    to_currency: str = Path(..., description="대상 통화 (예: USD, EUR, KRW)"),
) -> Dict[str, Any]:
    """암호화폐 환율 조회"""
    try:
        market_service = service_factory.get_market_data_service()
        rate = await market_service.crypto.get_exchange_rate(
            from_currency=from_currency.upper(),
            to_currency=to_currency.upper(),
        )

        if not rate:
            raise HTTPException(
                status_code=404,
                detail=f"환율 정보를 찾을 수 없습니다: {from_currency}/{to_currency}",
            )

        return {
            "from_currency": rate.from_currency,
            "to_currency": rate.to_currency,
            "exchange_rate": float(rate.exchange_rate),
            "bid_price": float(rate.bid_price) if rate.bid_price else None,
            "ask_price": float(rate.ask_price) if rate.ask_price else None,
            "timestamp": rate.timestamp.isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"환율 조회 중 오류 발생: {str(e)}")


@router.post(
    "/exchange-rates/bulk",
    response_model=Dict[str, Any],
    description="여러 암호화폐의 환율을 일괄 조회합니다.",
)
async def get_bulk_exchange_rates(
    crypto_symbols: List[str] = Query(..., description="암호화폐 심볼 리스트"),
    target_currency: str = Query(default="USD", description="목표 통화"),
) -> Dict[str, Any]:
    """대량 암호화폐 환율 조회"""
    try:
        market_service = service_factory.get_market_data_service()
        rates = await market_service.crypto.get_bulk_exchange_rates(
            crypto_symbols=crypto_symbols, target_currency=target_currency
        )

        results = {}
        for symbol, rate in rates.items():
            if rate:
                results[symbol] = {
                    "exchange_rate": float(rate.exchange_rate),
                    "bid_price": float(rate.bid_price) if rate.bid_price else None,
                    "ask_price": float(rate.ask_price) if rate.ask_price else None,
                    "timestamp": rate.timestamp.isoformat(),
                }
            else:
                results[symbol] = None

        return {
            "data": results,
            "target_currency": target_currency,
            "count": len(results),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"환율 조회 중 오류 발생: {str(e)}")


@router.get(
    "/daily/{symbol}",
    response_model=CryptoHistoricalDataResponse,
    description="암호화폐의 일일 가격 데이터(OHLCV)를 조회합니다.",
)
async def get_daily_prices(
    symbol: str = Path(..., description="암호화폐 심볼 (예: BTC, ETH)"),
    market: str = Query(default="USD", description="시장/통화 (예: USD, EUR, KRW)"),
    start_date: Optional[date] = Query(default=None, description="시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(default=None, description="종료 날짜 (YYYY-MM-DD)"),
) -> CryptoHistoricalDataResponse:
    """암호화폐 일일 가격 데이터 조회"""
    try:
        market_service = service_factory.get_market_data_service()
        daily_prices = await market_service.crypto.get_daily_prices(
            symbol=symbol.upper(), market=market.upper()
        )

        if not daily_prices:
            raise HTTPException(
                status_code=404,
                detail=f"암호화폐 데이터를 찾을 수 없습니다: {symbol}/{market}",
            )

        # 날짜 필터링 및 데이터 변환
        filtered_prices = []
        for price in daily_prices:
            if price.date:
                price_date = (
                    price.date.date() if hasattr(price.date, "date") else price.date
                )
                if start_date and price_date < start_date:
                    continue
                if end_date and price_date > end_date:
                    continue

                filtered_prices.append(
                    {
                        "date": price_date.isoformat(),
                        "open_market": (
                            float(price.open_market) if price.open_market else None
                        ),
                        "high_market": (
                            float(price.high_market) if price.high_market else None
                        ),
                        "low_market": (
                            float(price.low_market) if price.low_market else None
                        ),
                        "close_market": (
                            float(price.close_market) if price.close_market else None
                        ),
                        "volume": float(price.volume) if price.volume else None,
                        "market_cap": (
                            float(price.market_cap) if price.market_cap else None
                        ),
                        "open_usd": float(price.open_usd) if price.open_usd else None,
                        "high_usd": float(price.high_usd) if price.high_usd else None,
                        "low_usd": float(price.low_usd) if price.low_usd else None,
                        "close_usd": (
                            float(price.close_usd) if price.close_usd else None
                        ),
                        "market_cap_usd": (
                            float(price.market_cap_usd)
                            if price.market_cap_usd
                            else None
                        ),
                    }
                )

        return CryptoHistoricalDataResponse(
            symbol=symbol.upper(),
            market=market.upper(),
            data=filtered_prices,
            count=len(filtered_prices),
            start_date=start_date,
            end_date=end_date,
            frequency="daily",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"암호화폐 데이터 조회 중 오류 발생: {str(e)}")


@router.get(
    "/weekly/{symbol}",
    response_model=CryptoHistoricalDataResponse,
    description="암호화폐의 주간 가격 데이터(OHLCV)를 조회합니다.",
)
async def get_weekly_prices(
    symbol: str = Path(..., description="암호화폐 심볼 (예: BTC, ETH)"),
    market: str = Query(default="USD", description="시장/통화 (예: USD, EUR)"),
    start_date: Optional[date] = Query(default=None, description="시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(default=None, description="종료 날짜 (YYYY-MM-DD)"),
) -> CryptoHistoricalDataResponse:
    """암호화폐 주간 가격 데이터 조회"""
    try:
        market_service = service_factory.get_market_data_service()
        weekly_prices = await market_service.crypto.get_weekly_prices(
            symbol=symbol.upper(), market=market.upper()
        )

        if not weekly_prices:
            raise HTTPException(
                status_code=404,
                detail=f"암호화폐 데이터를 찾을 수 없습니다: {symbol}/{market}",
            )

        # 날짜 필터링 및 데이터 변환
        filtered_prices = []
        for price in weekly_prices:
            if price.date:
                price_date = (
                    price.date.date() if hasattr(price.date, "date") else price.date
                )
                if start_date and price_date < start_date:
                    continue
                if end_date and price_date > end_date:
                    continue

                filtered_prices.append(
                    {
                        "date": price_date.isoformat(),
                        "open_market": (
                            float(price.open_market) if price.open_market else None
                        ),
                        "high_market": (
                            float(price.high_market) if price.high_market else None
                        ),
                        "low_market": (
                            float(price.low_market) if price.low_market else None
                        ),
                        "close_market": (
                            float(price.close_market) if price.close_market else None
                        ),
                        "volume": float(price.volume) if price.volume else None,
                        "market_cap": (
                            float(price.market_cap) if price.market_cap else None
                        ),
                        "open_usd": float(price.open_usd) if price.open_usd else None,
                        "high_usd": float(price.high_usd) if price.high_usd else None,
                        "low_usd": float(price.low_usd) if price.low_usd else None,
                        "close_usd": (
                            float(price.close_usd) if price.close_usd else None
                        ),
                        "market_cap_usd": (
                            float(price.market_cap_usd)
                            if price.market_cap_usd
                            else None
                        ),
                    }
                )

        return CryptoHistoricalDataResponse(
            symbol=symbol.upper(),
            market=market.upper(),
            data=filtered_prices,
            count=len(filtered_prices),
            start_date=start_date,
            end_date=end_date,
            frequency="weekly",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"암호화폐 데이터 조회 중 오류 발생: {str(e)}")


@router.get(
    "/monthly/{symbol}",
    response_model=CryptoHistoricalDataResponse,
    description="암호화폐의 월간 가격 데이터(OHLCV)를 조회합니다.",
)
async def get_monthly_prices(
    symbol: str = Path(..., description="암호화폐 심볼 (예: BTC, ETH)"),
    market: str = Query(default="USD", description="시장/통화 (예: USD, EUR)"),
    start_date: Optional[date] = Query(default=None, description="시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(default=None, description="종료 날짜 (YYYY-MM-DD)"),
) -> CryptoHistoricalDataResponse:
    """암호화폐 월간 가격 데이터 조회"""
    try:
        market_service = service_factory.get_market_data_service()
        monthly_prices = await market_service.crypto.get_monthly_prices(
            symbol=symbol.upper(), market=market.upper()
        )

        if not monthly_prices:
            raise HTTPException(
                status_code=404,
                detail=f"암호화폐 데이터를 찾을 수 없습니다: {symbol}/{market}",
            )

        # 날짜 필터링 및 데이터 변환
        filtered_prices = []
        for price in monthly_prices:
            if price.date:
                price_date = (
                    price.date.date() if hasattr(price.date, "date") else price.date
                )
                if start_date and price_date < start_date:
                    continue
                if end_date and price_date > end_date:
                    continue

                filtered_prices.append(
                    {
                        "date": price_date.isoformat(),
                        "open_market": (
                            float(price.open_market) if price.open_market else None
                        ),
                        "high_market": (
                            float(price.high_market) if price.high_market else None
                        ),
                        "low_market": (
                            float(price.low_market) if price.low_market else None
                        ),
                        "close_market": (
                            float(price.close_market) if price.close_market else None
                        ),
                        "volume": float(price.volume) if price.volume else None,
                        "market_cap": (
                            float(price.market_cap) if price.market_cap else None
                        ),
                        "open_usd": float(price.open_usd) if price.open_usd else None,
                        "high_usd": float(price.high_usd) if price.high_usd else None,
                        "low_usd": float(price.low_usd) if price.low_usd else None,
                        "close_usd": (
                            float(price.close_usd) if price.close_usd else None
                        ),
                        "market_cap_usd": (
                            float(price.market_cap_usd)
                            if price.market_cap_usd
                            else None
                        ),
                    }
                )

        return CryptoHistoricalDataResponse(
            symbol=symbol.upper(),
            market=market.upper(),
            data=filtered_prices,
            count=len(filtered_prices),
            start_date=start_date,
            end_date=end_date,
            frequency="monthly",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"암호화폐 데이터 조회 중 오류 발생: {str(e)}")


# Convenience endpoints for Bitcoin and Ethereum
@router.get(
    "/bitcoin/{period}",
    response_model=CryptoHistoricalDataResponse,
    description="비트코인 가격 데이터를 조회합니다.",
)
async def get_bitcoin_price(
    period: Literal["daily", "weekly", "monthly"] = Path(
        ..., description="조회 기간 (daily, weekly, monthly)"
    ),
    market: str = Query(default="USD", description="시장/통화 (예: USD, EUR, KRW)"),
    start_date: Optional[date] = Query(default=None, description="시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(default=None, description="종료 날짜 (YYYY-MM-DD)"),
) -> CryptoHistoricalDataResponse:
    """비트코인 가격 조회"""
    try:
        market_service = service_factory.get_market_data_service()
        prices = await market_service.crypto.get_bitcoin_price(
            market=market.upper(), period=period
        )

        if not prices:
            raise HTTPException(
                status_code=404, detail=f"비트코인 데이터를 찾을 수 없습니다: {market}"
            )

        # 데이터 변환
        filtered_prices = []
        for price in prices:
            if price.date:
                price_date = (
                    price.date.date() if hasattr(price.date, "date") else price.date
                )
                if start_date and price_date < start_date:
                    continue
                if end_date and price_date > end_date:
                    continue

                filtered_prices.append(
                    {
                        "date": price_date.isoformat(),
                        "open_market": float(price.open_market),
                        "high_market": float(price.high_market),
                        "low_market": float(price.low_market),
                        "close_market": float(price.close_market),
                        "volume": float(price.volume),
                        "market_cap": (
                            float(price.market_cap) if price.market_cap else None
                        ),
                    }
                )

        return CryptoHistoricalDataResponse(
            symbol="BTC",
            market=market.upper(),
            data=filtered_prices,
            count=len(filtered_prices),
            start_date=start_date,
            end_date=end_date,
            frequency=period,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"비트코인 데이터 조회 중 오류 발생: {str(e)}")


@router.get(
    "/ethereum/{period}",
    response_model=CryptoHistoricalDataResponse,
    description="이더리움 가격 데이터를 조회합니다.",
)
async def get_ethereum_price(
    period: Literal["daily", "weekly", "monthly"] = Path(
        ..., description="조회 기간 (daily, weekly, monthly)"
    ),
    market: str = Query(default="USD", description="시장/통화 (예: USD, EUR, KRW)"),
    start_date: Optional[date] = Query(default=None, description="시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(default=None, description="종료 날짜 (YYYY-MM-DD)"),
) -> CryptoHistoricalDataResponse:
    """이더리움 가격 조회"""
    try:
        market_service = service_factory.get_market_data_service()
        prices = await market_service.crypto.get_ethereum_price(
            market=market.upper(), period=period
        )

        if not prices:
            raise HTTPException(
                status_code=404, detail=f"이더리움 데이터를 찾을 수 없습니다: {market}"
            )

        # 데이터 변환
        filtered_prices = []
        for price in prices:
            if price.date:
                price_date = (
                    price.date.date() if hasattr(price.date, "date") else price.date
                )
                if start_date and price_date < start_date:
                    continue
                if end_date and price_date > end_date:
                    continue

                filtered_prices.append(
                    {
                        "date": price_date.isoformat(),
                        "open_market": float(price.open_market),
                        "high_market": float(price.high_market),
                        "low_market": float(price.low_market),
                        "close_market": float(price.close_market),
                        "volume": float(price.volume),
                        "market_cap": (
                            float(price.market_cap) if price.market_cap else None
                        ),
                    }
                )

        return CryptoHistoricalDataResponse(
            symbol="ETH",
            market=market.upper(),
            data=filtered_prices,
            count=len(filtered_prices),
            start_date=start_date,
            end_date=end_date,
            frequency=period,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이더리움 데이터 조회 중 오류 발생: {str(e)}")
