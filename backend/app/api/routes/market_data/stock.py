"""
Stock API Routes
주식 데이터 관련 API 엔드포인트
"""

import logging
from datetime import date, datetime
from typing import List, Literal, Optional, Dict, Any
from decimal import Decimal
from fastapi import APIRouter, HTTPException, Query, Path
from pydantic import BaseModel

from app.schemas.market_data.stock import QuoteResponse
from app.schemas.market_data.base import MetadataInfo, DataQualityInfo, CacheInfo
from app.services.service_factory import service_factory


router = APIRouter()
logger = logging.getLogger(__name__)


# 임시 응답 모델들 (나중에 스키마로 이동)
class SymbolInfo(BaseModel):
    symbol: str
    name: str
    type: str
    region: str
    market_open: Optional[str] = None
    market_close: Optional[str] = None
    timezone: Optional[str] = None
    currency: Optional[str] = None
    match_score: Optional[float] = None


class StockSymbolsResponse(BaseModel):
    symbols: List[SymbolInfo]
    count: int
    search_term: Optional[str] = None


class HistoricalDataResponse(BaseModel):
    symbol: str
    data: List[Dict[str, Any]]
    count: int
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    frequency: str


@router.get(
    "/daily/{symbol}",
    response_model=HistoricalDataResponse,
    description="지정된 종목의 일일 주가 데이터(OHLCV)를 조회합니다.",
)
async def get_daily_prices(
    symbol: str = Path(..., description="종목 심볼 (예: AAPL, TSLA)"),
    outputsize: str = Query(
        default="compact", description="데이터 크기 (compact: 최근 100일, full: 전체)"
    ),
    start_date: Optional[date] = Query(default=None, description="시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(default=None, description="종료 날짜 (YYYY-MM-DD)"),
) -> HistoricalDataResponse:
    """일일 주가 데이터 조회"""
    try:
        # 심볼 유효성 검사
        if not symbol or len(symbol.strip()) == 0:
            raise HTTPException(status_code=400, detail="유효한 종목 심볼을 입력해주세요")

        symbol = symbol.upper().strip()

        # 기본적인 심볼 포맷 검사 (1-5자의 영문 대문자)
        import re

        if not re.match(r"^[A-Z]{1,5}$", symbol):
            raise HTTPException(
                status_code=400,
                detail=f"잘못된 심볼 형식입니다: {symbol}. 1-5자의 영문 대문자만 허용됩니다 (예: AAPL, TSLA)",
            )

        market_service = service_factory.get_market_data_service()
        daily_prices = await market_service.stock.get_daily_prices(
            symbol=symbol, outputsize=outputsize
        )

        if not daily_prices:
            raise HTTPException(status_code=404, detail=f"주식 데이터를 찾을 수 없습니다: {symbol}")

        # 날짜 필터링 디버깅
        logger.info(f"📅 필터링 전 데이터: {len(daily_prices)}개")
        logger.info(f"📅 필터 조건 - start_date: {start_date}, end_date: {end_date}")
        if daily_prices:
            first_date = (
                daily_prices[0].date.date()
                if hasattr(daily_prices[0].date, "date")
                else daily_prices[0].date
            )
            last_date = (
                daily_prices[-1].date.date()
                if hasattr(daily_prices[-1].date, "date")
                else daily_prices[-1].date
            )
            logger.info(f"📅 데이터 범위: {first_date} ~ {last_date}")

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
                        "open": float(price.open) if price.open else None,
                        "high": float(price.high) if price.high else None,
                        "low": float(price.low) if price.low else None,
                        "close": float(price.close) if price.close else None,
                        "volume": int(price.volume) if price.volume else None,
                    }
                )

        logger.info(f"📅 필터링 후 데이터: {len(filtered_prices)}개")

        return HistoricalDataResponse(
            symbol=symbol.upper(),
            data=filtered_prices,
            count=len(filtered_prices),
            start_date=start_date,
            end_date=end_date,
            frequency="daily",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"주식 데이터 조회 중 오류 발생: {str(e)}")


@router.get(
    "/weekly/{symbol}",
    response_model=HistoricalDataResponse,
    description="지정된 종목의 주간 주가 데이터(OHLCV)를 조회합니다.",
)
async def get_weekly_prices(
    symbol: str = Path(..., description="종목 심볼 (예: AAPL, TSLA)"),
    start_date: Optional[date] = Query(default=None, description="시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(default=None, description="종료 날짜 (YYYY-MM-DD)"),
    outputsize: str = Query(
        "compact", description="데이터 크기 (compact: 최근 100개, full: 전체)"
    ),
) -> HistoricalDataResponse:
    """주간 주가 데이터 조회"""
    try:
        # 심볼 유효성 검사
        if not symbol or len(symbol.strip()) == 0:
            raise HTTPException(status_code=400, detail="유효한 종목 심볼을 입력해주세요")

        symbol = symbol.upper().strip()

        # 기본적인 심볼 포맷 검사 (1-5자의 영문 대문자)
        import re

        if not re.match(r"^[A-Z]{1,5}$", symbol):
            raise HTTPException(
                status_code=400,
                detail=f"잘못된 심볼 형식입니다: {symbol}. 1-5자의 영문 대문자만 허용됩니다 (예: AAPL, TSLA)",
            )

        market_service = service_factory.get_market_data_service()
        weekly_prices = await market_service.stock.get_weekly_prices(
            symbol=symbol, outputsize=outputsize
        )

        if not weekly_prices:
            raise HTTPException(status_code=404, detail=f"주식 데이터를 찾을 수 없습니다: {symbol}")

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
                        "open": float(price.open) if price.open else None,
                        "high": float(price.high) if price.high else None,
                        "low": float(price.low) if price.low else None,
                        "close": float(price.close) if price.close else None,
                        "volume": price.volume,
                        "adjusted_close": (
                            float(price.adjusted_close)
                            if price.adjusted_close
                            else None
                        ),
                        "dividend_amount": (
                            float(price.dividend_amount)
                            if price.dividend_amount
                            else None
                        ),
                        "split_coefficient": (
                            float(price.split_coefficient)
                            if price.split_coefficient
                            else None
                        ),
                    }
                )

        return HistoricalDataResponse(
            symbol=symbol.upper(),
            data=filtered_prices,
            count=len(filtered_prices),
            start_date=filtered_prices[-1]["date"] if filtered_prices else None,
            end_date=filtered_prices[0]["date"] if filtered_prices else None,
            frequency="weekly",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"주간 데이터 조회 중 오류 발생: {str(e)}")


@router.get(
    "/monthly/{symbol}",
    response_model=HistoricalDataResponse,
    description="지정된 종목의 월간 주가 데이터(OHLCV)를 조회합니다.",
)
async def get_monthly_prices(
    symbol: str = Path(..., description="종목 심볼 (예: AAPL, TSLA)"),
    start_date: Optional[date] = Query(default=None, description="시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(default=None, description="종료 날짜 (YYYY-MM-DD)"),
    outputsize: str = Query(
        "compact", description="데이터 크기 (compact: 최근 100개, full: 전체)"
    ),
) -> HistoricalDataResponse:
    """월간 주가 데이터 조회"""
    try:
        # 심볼 유효성 검사
        if not symbol or len(symbol.strip()) == 0:
            raise HTTPException(status_code=400, detail="유효한 종목 심볼을 입력해주세요")

        symbol = symbol.upper().strip()

        # 기본적인 심볼 포맷 검사 (1-5자의 영문 대문자)
        import re

        if not re.match(r"^[A-Z]{1,5}$", symbol):
            raise HTTPException(
                status_code=400,
                detail=f"잘못된 심볼 형식입니다: {symbol}. 1-5자의 영문 대문자만 허용됩니다 (예: AAPL, TSLA)",
            )

        market_service = service_factory.get_market_data_service()
        monthly_prices = await market_service.stock.get_monthly_prices(
            symbol=symbol, outputsize=outputsize
        )

        if not monthly_prices:
            raise HTTPException(status_code=404, detail=f"주식 데이터를 찾을 수 없습니다: {symbol}")

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
                        "open": float(price.open) if price.open else None,
                        "high": float(price.high) if price.high else None,
                        "low": float(price.low) if price.low else None,
                        "close": float(price.close) if price.close else None,
                        "volume": price.volume,
                        "adjusted_close": (
                            float(price.adjusted_close)
                            if price.adjusted_close
                            else None
                        ),
                        "dividend_amount": (
                            float(price.dividend_amount)
                            if price.dividend_amount
                            else None
                        ),
                        "split_coefficient": (
                            float(price.split_coefficient)
                            if price.split_coefficient
                            else None
                        ),
                    }
                )

        return HistoricalDataResponse(
            symbol=symbol.upper(),
            data=filtered_prices,
            count=len(filtered_prices),
            start_date=filtered_prices[-1]["date"] if filtered_prices else None,
            end_date=filtered_prices[0]["date"] if filtered_prices else None,
            frequency="monthly",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"월간 데이터 조회 중 오류 발생: {str(e)}")


@router.get(
    "/quote/{symbol}",
    response_model=QuoteResponse,
    description="지정된 종목의 실시간 호가 정보를 조회합니다.",
)
async def get_quote(
    symbol: str = Path(..., description="종목 심볼 (예: AAPL, TSLA)")
) -> QuoteResponse:
    """실시간 주식 호가 조회"""
    try:
        stock_service = service_factory.get_market_data_service().stock
        quote_data = await stock_service.get_real_time_quote(symbol=symbol.upper())

        if not quote_data:
            raise HTTPException(status_code=404, detail=f"호가 데이터를 찾을 수 없습니다: {symbol}")

        # QuoteResponse 생성 (DataResponse[QuoteData] 구조)
        return QuoteResponse(
            success=True,
            message=f"{symbol} 실시간 호가 조회 완료",
            data=quote_data,
            metadata=MetadataInfo(
                data_quality=DataQualityInfo(
                    quality_score=Decimal("95.0"),
                    last_updated=quote_data.timestamp,
                    data_source="alpha_vantage",
                    confidence_level="high",
                ),
                cache_info=CacheInfo(
                    cached=True,
                    cache_hit=True,
                    cache_timestamp=datetime.now(),
                    cache_ttl=3600,  # 1시간
                ),
                processing_time_ms=None,
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 호가 데이터 조회 실패: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"호가 데이터 조회 중 오류 발생: {str(e)}")


@router.get(
    "/intraday/{symbol}",
    response_model=HistoricalDataResponse,
    description="지정된 종목의 실시간 또는 분봉 데이터를 조회합니다.",
)
async def get_intraday_data(
    symbol: str = Path(..., description="종목 심볼 (예: AAPL, TSLA)"),
    interval: Literal["1min", "5min", "15min", "30min", "60min"] = Query(
        default="15min", description="데이터 간격 (1min, 5min, 15min, 30min, 60min)"
    ),
    extended_hours: bool = Query(default=False, description="연장 거래 시간 포함 여부"),
    adjusted: bool = Query(default=True, description="조정 가격 여부"),
    start_date: Optional[date] = Query(default=None, description="시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(default=None, description="종료 날짜 (YYYY-MM-DD)"),
    outputsize: Literal["compact", "full"] = Query(
        default="compact", description="데이터 크기 (compact/full)"
    ),
):
    """실시간/분봉 주가 데이터 조회"""
    try:
        # 심볼 유효성 검사
        if not symbol or len(symbol.strip()) == 0:
            raise HTTPException(status_code=400, detail="유효한 종목 심볼을 입력해주세요")

        symbol = symbol.upper().strip()

        # 기본적인 심볼 포맷 검사 (1-5자의 영문 대문자)
        import re

        if not re.match(r"^[A-Z]{1,5}$", symbol):
            raise HTTPException(
                status_code=400,
                detail=f"잘못된 심볼 형식입니다: {symbol}. 1-5자의 영문 대문자만 허용됩니다 (예: AAPL, TSLA)",
            )

        # 서비스 팩토리를 통한 마켓 데이터 서비스 호출
        market_service = service_factory.get_market_data_service()
        intraday_prices = await market_service.stock.get_intraday_data(
            symbol=symbol,
            interval=interval,
            adjusted=adjusted,
            extended_hours=extended_hours,
            outputsize=outputsize,
        )

        if not intraday_prices:
            raise HTTPException(status_code=404, detail=f"주식 데이터를 찾을 수 없습니다: {symbol}")

        logger.info(f"📅 필터링 전 intraday 데이터: {len(intraday_prices)}개")
        logger.info(f"📅 필터 조건 - start_date: {start_date}, end_date: {end_date}")

        # 날짜 필터링 및 데이터 변환 (daily와 동일한 패턴)
        filtered_prices = []
        for price in intraday_prices:
            if price.date:
                # datetime을 date로 변환 (intraday는 datetime 포함)
                price_date = (
                    price.date.date() if hasattr(price.date, "date") else price.date
                )

                # 날짜 필터링
                if start_date and price_date < start_date:
                    continue
                if end_date and price_date > end_date:
                    continue

                # datetime 정보 포함 (intraday는 시간 정보 중요)
                timestamp = (
                    price.date.isoformat()
                    if hasattr(price.date, "isoformat")
                    else str(price.date)
                )

                filtered_prices.append(
                    {
                        "date": timestamp,  # ISO 8601 형식 (2025-01-11T09:30:00)
                        "open": float(price.open) if price.open else None,
                        "high": float(price.high) if price.high else None,
                        "low": float(price.low) if price.low else None,
                        "close": float(price.close) if price.close else None,
                        "volume": int(price.volume) if price.volume else None,
                    }
                )

        logger.info(f"📅 필터링 후 intraday 데이터: {len(filtered_prices)}개")

        return HistoricalDataResponse(
            symbol=symbol.upper(),
            data=filtered_prices,
            count=len(filtered_prices),
            start_date=start_date,
            end_date=end_date,
            frequency=f"intraday_{interval}",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Intraday 데이터 조회 실패: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"주식 데이터 조회 중 오류 발생: {str(e)}")


@router.get(
    "/search",
    response_model=StockSymbolsResponse,
    description="주식 심볼 검색 (Alpha Vantage의 심볼 서치 기능 활용)",
)
async def search_stock_symbols(
    keywords: str = Query(..., description="검색 키워드 (예: Apple, Tesla)"),
) -> StockSymbolsResponse:
    """주식 심볼 검색"""
    try:
        if not keywords or len(keywords) == 0:
            raise HTTPException(status_code=400, detail="유효한 검색 키워드를 입력해주세요")

        market_service = service_factory.get_market_data_service()
        response = await market_service.stock.search_symbols(keywords=keywords.strip())

        # Alpha Vantage 응답을 SymbolInfo 리스트로 변환
        symbols = []
        if isinstance(response, dict) and "bestMatches" in response:
            for match in response.get("bestMatches", []):
                try:
                    symbol_info = SymbolInfo(
                        symbol=match.get("1. symbol", ""),
                        name=match.get("2. name", ""),
                        type=match.get("3. type", ""),
                        region=match.get("4. region", ""),
                        market_open=match.get("5. marketOpen"),
                        market_close=match.get("6. marketClose"),
                        timezone=match.get("7. timezone"),
                        currency=match.get("8. currency"),
                        match_score=float(match.get("9. matchScore", 0.0)),
                    )
                    symbols.append(symbol_info)
                except Exception as e:
                    logger.warning(f"⚠️ Failed to parse symbol info: {e}")
                    continue

        return StockSymbolsResponse(
            symbols=symbols, count=len(symbols), search_term=keywords
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 심볼 검색 실패: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"심볼 검색 중 오류 발생: {str(e)}")
