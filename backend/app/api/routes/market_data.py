"""
Market Data API Routes
"""

from datetime import datetime
from typing import List, AsyncGenerator
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import ValidationError

from app.api.deps import get_current_active_verified_user
from app.schemas.market_data import (
    MarketDataResponse,
    DataQualityResponse,
    DataRequestStatus,
    BulkDataRequest,
)
from app.services.service_factory import service_factory
from app.services.market_data_service import MarketDataService

router = APIRouter(dependencies=[Depends(get_current_active_verified_user)])


async def get_market_data_service() -> AsyncGenerator[MarketDataService, None]:
    """Dependency to get market data service with proper cleanup"""
    service = service_factory.get_market_data_service()
    try:
        yield service
    finally:
        pass  # ServiceFactory manages cleanup


@router.get("/symbols", response_model=List[str])
async def get_available_symbols(
    service: MarketDataService = Depends(get_market_data_service),
):
    """Get list of all available symbols"""
    try:
        symbols = await service.get_available_symbols()
        return symbols
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data/{symbol}", response_model=List[MarketDataResponse])
async def get_market_data(
    symbol: str,
    start_date: datetime = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: datetime = Query(..., description="End date (YYYY-MM-DD)"),
    force_refresh: bool = Query(False, description="Force refresh from external API"),
    service: MarketDataService = Depends(get_market_data_service),
):
    """Get market data for a specific symbol and date range"""

    import logging

    logger = logging.getLogger(__name__)

    logger.info(f"🌐 API Request: GET /data/{symbol}")
    logger.info(
        f"📅 Parameters: start_date={start_date}, end_date={end_date}, force_refresh={force_refresh}"
    )

    try:
        # Validate date range
        if start_date > end_date:
            logger.error(
                f"❌ Invalid date range: start_date={start_date} > end_date={end_date}"
            )
            raise HTTPException(
                status_code=400, detail="Start date must be before end date"
            )

        # 🔧 Timezone 문제 해결: 모든 datetime을 timezone-naive로 변환
        if start_date.tzinfo is not None:
            start_date = start_date.replace(tzinfo=None)
        if end_date.tzinfo is not None:
            end_date = end_date.replace(tzinfo=None)

        # Future date validation with timezone-naive comparison
        now = datetime.now()
        if start_date > now:
            logger.error(f"❌ Future start date: start_date={start_date}")
            raise HTTPException(
                status_code=400, detail="Start date cannot be in the future"
            )

        logger.info(f"✅ Date validation passed for {symbol}")

        # Get data
        logger.info(f"🔄 Calling service.get_market_data for {symbol.upper()}")
        data = await service.get_market_data(
            symbol.upper(), start_date, end_date, force_refresh
        )

        logger.info(
            f"📊 Service returned {len(data) if data else 0} records for {symbol}"
        )

        # Convert to response model
        response = []
        for item in data:
            try:
                response.append(
                    MarketDataResponse(
                        symbol=item.symbol,
                        date=item.date,
                        open=item.open_price,
                        high=item.high_price,
                        low=item.low_price,
                        close=item.close_price,
                        volume=item.volume,
                        adjusted_close=item.adjusted_close,
                        dividend_amount=item.dividend_amount,
                        split_coefficient=item.split_coefficient,
                    )
                )
            except Exception as e:
                logger.error(f"❌ Failed to convert record for {symbol}: {e}")
                logger.error(f"Record data: {item}")
                raise e

        logger.info(f"✅ Successfully converted {len(response)} records for {symbol}")
        return response

    except ValidationError as e:
        logger.error(f"❌ Validation error for {symbol}: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except HTTPException as e:
        logger.error(f"❌ HTTP error for {symbol}: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"💥 Unexpected error for {symbol}: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback

        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/data/bulk", response_model=List[DataRequestStatus])
async def request_bulk_data(
    request: BulkDataRequest,
    service: MarketDataService = Depends(get_market_data_service),
):
    """Request bulk market data for multiple symbols"""
    try:
        # Validate request
        if not request.symbols:
            raise HTTPException(status_code=400, detail="Symbols list cannot be empty")

        if request.start_date > request.end_date:
            raise HTTPException(
                status_code=400, detail="Start date must be before end date"
            )

        # Create data requests
        requests = []
        for symbol in request.symbols:
            data_request = await service.create_data_request(
                symbol.upper(), request.start_date, request.end_date
            )
            requests.append(
                DataRequestStatus(
                    id=str(data_request.id),
                    symbol=data_request.symbol,
                    start_date=data_request.start_date,
                    end_date=data_request.end_date,
                    status=data_request.status,
                    requested_at=data_request.requested_at,
                )
            )

        # TODO: Implement background task processing

        return requests

    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/coverage/{symbol}")
async def get_data_coverage(
    symbol: str, service: MarketDataService = Depends(get_market_data_service)
):
    """Get data coverage information for a symbol"""
    try:
        coverage = await service.get_data_coverage(symbol.upper())
        return coverage
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quality/{symbol}", response_model=DataQualityResponse)
async def analyze_data_quality(
    symbol: str,
    start_date: datetime = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: datetime = Query(..., description="End date (YYYY-MM-DD)"),
    service: MarketDataService = Depends(get_market_data_service),
):
    """Analyze data quality for a symbol and date range"""
    try:
        # Validate date range
        if start_date > end_date:
            raise HTTPException(
                status_code=400, detail="Start date must be before end date"
            )

        quality = await service.analyze_data_quality(
            symbol.upper(), start_date, end_date
        )

        return DataQualityResponse(
            symbol=quality.symbol,
            date_range_start=quality.date_range_start,
            date_range_end=quality.date_range_end,
            total_records=quality.total_records,
            missing_days=quality.missing_days,
            duplicate_records=quality.duplicate_records,
            price_anomalies=quality.price_anomalies,
            quality_score=quality.quality_score,
            analyzed_at=quality.analyzed_at,
        )

    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/cache-performance")
async def get_cache_performance_stats(
    service: MarketDataService = Depends(get_market_data_service),
):
    """DuckDB 캐시 성능 통계 조회"""
    try:
        if not service.database_manager:
            return {"status": "disabled", "message": "DuckDB 캐시가 비활성화됨"}

        # DuckDB 통계 수집
        symbols = service.database_manager.get_available_symbols()

        # 캐시된 데이터 요약
        stats = {
            "cache_enabled": True,
            "cached_symbols_count": len(symbols),
            "sample_symbols": symbols[:10],
            "database_path": service.database_manager.db_path,
            "connection_status": (
                "connected" if service.database_manager.connection else "disconnected"
            ),
            "performance_notes": [
                "DuckDB 캐시를 통해 10-100배 빠른 시계열 조회",
                "force_refresh=true로 캐시 우회 가능",
                "자동으로 Alpha Vantage → DuckDB → MongoDB 순서로 조회",
            ],
        }

        return {
            "status": "success",
            "cache_stats": stats,
            "analyzed_at": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"캐시 통계 조회 실패: {str(e)}")


@router.get("/analytics/symbol-coverage")
async def get_symbols_coverage_analytics(
    service: MarketDataService = Depends(get_market_data_service),
):
    """심볼별 데이터 커버리지 분석"""
    try:
        if not service.database_manager:
            return {"status": "disabled", "message": "DuckDB 분석 기능이 비활성화됨"}

        symbols = service.database_manager.get_available_symbols()

        # 각 심볼의 데이터 범위 조회
        coverage_summary = []
        for symbol in symbols[:20]:  # 처음 20개 심볼만 분석
            try:
                start_date, end_date = service.database_manager.get_data_range(symbol)
                coverage_summary.append(
                    {
                        "symbol": symbol,
                        "start_date": start_date,
                        "end_date": end_date,
                        "has_data": bool(start_date and end_date),
                    }
                )
            except Exception:
                coverage_summary.append(
                    {
                        "symbol": symbol,
                        "start_date": None,
                        "end_date": None,
                        "has_data": False,
                    }
                )

        return {
            "status": "success",
            "total_symbols": len(symbols),
            "analyzed_symbols": len(coverage_summary),
            "coverage_summary": coverage_summary,
            "analyzed_at": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"커버리지 분석 실패: {str(e)}")
