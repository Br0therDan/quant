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
    description="지정된 종목의 실시간 호가 정보를 조회합니다.",
)
async def get_quote(symbol: str = Path(..., description="종목 심볼 (예: AAPL, TSLA)")):
    """실시간 주식 호가 조회"""
    try:
        # Note: Alpha Vantage GLOBAL_QUOTE API는 더 이상 사용되지 않음
        # Daily 데이터의 최신 데이터를 활용하여 유사한 기능 제공
        market_service = service_factory.get_market_data_service()
        daily_prices = await market_service.stock.get_daily_prices(
            symbol=symbol.upper(), outputsize="compact"
        )

        if not daily_prices:
            return {
                "success": False,
                "message": f"{symbol.upper()}의 호가 데이터를 찾을 수 없습니다.",
                "data": None,
                "metadata": {"symbol": symbol.upper(), "status": "no_data"},
            }

        # 최신 데이터 (첫 번째 요소)
        latest_price = daily_prices[0]
        quote_data = {
            "symbol": symbol.upper(),
            "price": float(latest_price.close) if latest_price.close else None,
            "open": float(latest_price.open) if latest_price.open else None,
            "high": float(latest_price.high) if latest_price.high else None,
            "low": float(latest_price.low) if latest_price.low else None,
            "volume": int(latest_price.volume) if latest_price.volume else None,
            "date": latest_price.date.isoformat() if latest_price.date else None,
            "change": None,  # 전일 대비 변동
            "change_percent": None,  # 전일 대비 변동률
        }

        # 전일 대비 변동 계산 (데이터가 2개 이상 있을 때)
        if len(daily_prices) >= 2:
            prev_price = daily_prices[1]
            if latest_price.close and prev_price.close:
                change = float(latest_price.close) - float(prev_price.close)
                change_percent = (change / float(prev_price.close)) * 100
                quote_data["change"] = round(change, 2)
                quote_data["change_percent"] = round(change_percent, 2)

        return {
            "success": True,
            "message": f"{symbol.upper()}의 호가 데이터 조회 완료",
            "data": quote_data,
            "metadata": {
                "symbol": symbol.upper(),
                "source": "Alpha Vantage Daily Data",
                "note": "실시간 데이터가 아닌 일일 데이터의 최신 정보입니다.",
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"호가 데이터 조회 중 오류 발생: {str(e)}")


@router.get(
    "/intraday/{symbol}",
    response_model=Dict[str, Any],
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
        # Note: Alpha Vantage Intraday API는 제한이 있음 (Premium 요구)
        # 기본적인 샘플 데이터 제공
        sample_data = {
            "symbol": symbol.upper(),
            "interval": interval,
            "last_refreshed": "2024-12-07 16:00:00",
            "time_zone": "US/Eastern",
            "data": [
                {
                    "time": "2024-12-07 16:00:00",
                    "open": 150.25,
                    "high": 151.00,
                    "low": 149.80,
                    "close": 150.75,
                    "volume": 125000,
                },
                {
                    "time": "2024-12-07 15:59:00",
                    "open": 150.10,
                    "high": 150.30,
                    "low": 149.95,
                    "close": 150.25,
                    "volume": 98000,
                },
            ],
        }

        return {
            "success": True,
            "message": f"{symbol.upper()}의 인트라데이 데이터 조회 완료 (샘플 데이터)",
            "data": sample_data,
            "metadata": {
                "symbol": symbol.upper(),
                "interval": interval,
                "outputsize": outputsize,
                "status": "sample_data",
                "note": "Alpha Vantage Intraday API는 Premium 요구사항입니다.",
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"인트라데이 데이터 조회 중 오류 발생: {str(e)}")


@router.get(
    "/historical/{symbol}",
    response_model=HistoricalDataResponse,
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
        market_service = service_factory.get_market_data_service()

        # 기본적으로 daily 데이터 사용 (weekly, monthly는 Alpha Vantage에서 별도 API)
        if frequency == "daily":
            daily_prices = await market_service.stock.get_daily_prices(
                symbol=symbol.upper(), outputsize="full"
            )

            # 날짜 필터링
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
                frequency=frequency,
            )
        else:
            # weekly, monthly는 샘플 데이터 반환
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
