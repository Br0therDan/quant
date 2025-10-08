"""
Stock API Routes
주식 데이터 관련 API 엔드포인트
"""

from datetime import date
from typing import List, Literal, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Path
from pydantic import BaseModel

from app.services.service_factory import service_factory


router = APIRouter()


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
):
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
):
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
):
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
    response_model=Dict[str, Any],
    description="지정된 종목의 실시간 호가 정보를 조회합니다.",
)
async def get_quote(symbol: str = Path(..., description="종목 심볼 (예: AAPL, TSLA)")):
    """실시간 주식 호가 조회"""
    try:
        stock_service = service_factory.get_market_data_service().stock
        global_quote = await stock_service.get_real_time_quote(symbol=symbol.upper())

        if not global_quote:
            raise HTTPException(status_code=404, detail=f"호가 데이터를 찾을 수 없습니다: {symbol}")
        return global_quote

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"호가 데이터 조회 중 오류 발생: {str(e)}")


@router.get(
    "/intraday/{symbol}",
    response_model=Dict[str, Any],
    description="지정된 종목의 실시간 또는 분봉 데이터를 조회합니다.",
)
async def get_intraday_data(
    symbol: str = Path(..., description="종목 심볼 (예: AAPL, TSLA)"),
    interval: Literal["1min", "5min", "15min", "30min", "60min"] = Query(
        default="15min", description="데이터 간격 (1min, 5min, 15min, 30min, 60min)"
    ),
    extended_hours: bool = Query(default=False, description="연장 거래 시간 포함 여부"),
    adjusted: bool = Query(default=True, description="조정 가격 여부"),
    start_date: Optional[date] = Query(
        default=date.today(), description="시작 날짜 (YYYY-MM-DD)"
    ),
    end_date: Optional[date] = Query(
        default=date.today(), description="종료 날짜 (YYYY-MM-DD)"
    ),
    outputsize: Literal["compact", "full"]
    | None = Query(default="compact", description="데이터 크기 (compact/full)"),
):
    """실시간/분봉 주가 데이터 조회"""
    try:
        stock_service = service_factory.get_stock_service()

        # StockService의 get_intraday_data 메서드 호출
        intraday_data = await stock_service.get_intraday_data(
            symbol=symbol.upper(),
            interval=interval,
            adjusted=adjusted,
            extended_hours=extended_hours,
            outputsize=outputsize,
        )

        if not intraday_data:
            raise HTTPException(status_code=404, detail=f"주식 데이터를 찾을 수 없습니다: {symbol}")

        return intraday_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"주식 데이터 조회 중 오류 발생: {str(e)}")


@router.get(
    "/search",
    response_model=StockSymbolsResponse,
    description="종목 심볼 검색 (Alpha Vantage SYMBOL_SEARCH)",
)
async def search_symbols(
    keywords: str = Query(..., description="검색 키워드 (예: Apple, Tesla)"),
):
    """종목 심볼 검색"""
    try:
        stock_service = service_factory.get_market_data_service().stock
        search_results = await stock_service.search_symbols(keywords=keywords)

        # Alpha Vantage API 응답 처리 - bestMatches 키를 가진 딕셔너리
        best_matches = search_results.get("bestMatches", [])

        symbols_list = []
        for item in best_matches:
            symbol_info = SymbolInfo(
                symbol=item.get("1. symbol", ""),
                name=item.get("2. name", ""),
                type=item.get("3. type", ""),
                region=item.get("4. region", ""),
                market_open=item.get("5. marketOpen"),
                market_close=item.get("6. marketClose"),
                timezone=item.get("7. timezone"),
                currency=item.get("8. currency"),
                match_score=float(item.get("9. matchScore", 0)),
            )
            symbols_list.append(symbol_info)

        return StockSymbolsResponse(
            symbols=symbols_list,
            count=len(symbols_list),
            search_term=keywords,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"심볼 검색 중 오류 발생: {str(e)}")
