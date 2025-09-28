"""
Market Data API Routes
"""

from datetime import datetime
from typing import List, AsyncGenerator
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import ValidationError

from app.schemas.market_data import (
    MarketDataResponse,
    DataQualityResponse,
    DataRequestStatus,
    BulkDataRequest,
)
from app.services.service_factory import service_factory
from app.services.market_data_service import MarketDataService

router = APIRouter(prefix="/market-data", tags=["Market Data"])


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
    try:
        # Validate date range
        if start_date > end_date:
            raise HTTPException(
                status_code=400, detail="Start date must be before end date"
            )

        if start_date > datetime.now():
            raise HTTPException(
                status_code=400, detail="Start date cannot be in the future"
            )

        # Get data
        data = await service.get_market_data(
            symbol.upper(), start_date, end_date, force_refresh
        )

        # Convert to response model
        response = []
        for item in data:
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

        return response

    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
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
