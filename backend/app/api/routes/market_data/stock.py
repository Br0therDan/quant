"""
Stock API Routes
주식 데이터 관련 API 엔드포인트
"""

from datetime import datetime, date
from typing import List, Optional, Dict, Any
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
    response_model=Dict[str, Any],  # 임시로 Dict 사용
    summary="일일 주가 데이터 조회",
    description="지정된 종목의 일일 주가 데이터(OHLCV)를 조회합니다.",
)
async def get_daily_prices(
    symbol: str = Path(..., description="종목 심볼 (예: AAPL, TSLA)"),
    outputsize: str = Query(
        default="compact", description="데이터 크기 (compact: 최근 100일, full: 전체)"
    ),
):
    """일일 주가 데이터 조회"""
    try:
        stock_service = service_factory.get_stock_service()

        # StockService의 get_daily_prices 메서드 호출
        daily_prices = await stock_service.get_daily_prices(
            symbol=symbol.upper(), outputsize=outputsize
        )

        if not daily_prices:
            raise HTTPException(status_code=404, detail=f"주식 데이터를 찾을 수 없습니다: {symbol}")

        # 모델 데이터를 딕셔너리로 변환
        price_data = []
        for price in daily_prices:
            price_data.append(
                {
                    "date": (
                        price.date.isoformat()
                        if hasattr(price, "date") and price.date
                        else None
                    ),
                    "open": (
                        float(price.open)
                        if hasattr(price, "open") and price.open is not None
                        else None
                    ),
                    "high": (
                        float(price.high)
                        if hasattr(price, "high") and price.high is not None
                        else None
                    ),
                    "low": (
                        float(price.low)
                        if hasattr(price, "low") and price.low is not None
                        else None
                    ),
                    "close": (
                        float(price.close)
                        if hasattr(price, "close") and price.close is not None
                        else None
                    ),
                    "volume": (
                        int(price.volume)
                        if hasattr(price, "volume") and price.volume is not None
                        else None
                    ),
                }
            )

        return {
            "success": True,
            "message": f"{symbol} 일일 주가 데이터 조회 완료",
            "data": {
                "symbol": symbol.upper(),
                "prices": price_data,
                "count": len(price_data),
                "outputsize": outputsize,
            },
            "metadata": {
                "last_refreshed": datetime.now().isoformat(),
                "time_zone": "US/Eastern",
                "source": "Alpha Vantage",
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"주식 데이터 조회 중 오류 발생: {str(e)}")


@router.get(
    "/quote/{symbol}",
    response_model=Dict[str, Any],
    summary="실시간 주식 호가 조회",
    description="지정된 종목의 실시간 호가 정보를 조회합니다.",
)
async def get_quote(symbol: str = Path(..., description="종목 심볼 (예: AAPL, TSLA)")):
    """실시간 주식 호가 조회"""
    try:
        # TODO: StockService에 get_quote 메서드 구현 필요
        # stock_service = service_factory.get_stock_service()
        # quote_data = await stock_service.get_quote(symbol.upper())

        # 임시 구현 (실제로는 Alpha Vantage GLOBAL_QUOTE API 사용)
        return {
            "success": False,
            "message": "실시간 호가 조회 기능은 아직 구현되지 않았습니다.",
            "data": None,
            "metadata": {"symbol": symbol.upper(), "status": "not_implemented"},
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"호가 데이터 조회 중 오류 발생: {str(e)}")


@router.get(
    "/intraday/{symbol}",
    response_model=Dict[str, Any],
    summary="실시간/인트라데이 데이터 조회",
    description="지정된 종목의 실시간 또는 분봉 데이터를 조회합니다.",
)
async def get_intraday_data(
    symbol: str = Path(..., description="종목 심볼 (예: AAPL, TSLA)"),
    interval: str = Query(
        default="1min", description="데이터 간격 (1min, 5min, 15min, 30min, 60min)"
    ),
    outputsize: str = Query(default="compact", description="데이터 크기 (compact/full)"),
):
    """실시간/인트라데이 데이터 조회"""
    try:
        # TODO: StockService에 get_intraday_data 메서드 구현 필요
        return {
            "success": False,
            "message": "인트라데이 데이터 조회 기능은 아직 구현되지 않았습니다.",
            "data": None,
            "metadata": {
                "symbol": symbol.upper(),
                "interval": interval,
                "outputsize": outputsize,
                "status": "not_implemented",
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"인트라데이 데이터 조회 중 오류 발생: {str(e)}")


@router.get(
    "/historical/{symbol}",
    response_model=HistoricalDataResponse,
    summary="장기 히스토리 데이터 조회",
    description="지정된 종목의 장기 히스토리 데이터를 조회합니다.",
)
async def get_historical_data(
    symbol: str = Path(..., description="종목 심볼 (예: AAPL, TSLA)"),
    start_date: Optional[date] = Query(default=None, description="시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(default=None, description="종료 날짜 (YYYY-MM-DD)"),
    frequency: str = Query(
        default="daily", description="데이터 주기 (daily, weekly, monthly)"
    ),
):
    """장기 히스토리 데이터 조회"""
    try:
        # TODO: StockService에 get_historical_data 메서드 구현 필요
        return HistoricalDataResponse(
            symbol=symbol.upper(),
            data=[],
            count=0,
            start_date=start_date,
            end_date=end_date,
            frequency=frequency,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"히스토리 데이터 조회 중 오류 발생: {str(e)}")
