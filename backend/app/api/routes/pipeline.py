"""
Data Pipeline API Routes
"""

from datetime import datetime, timezone
from typing import List, Optional, AsyncGenerator
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel

from app.services.data_pipeline import DataPipeline

router = APIRouter(prefix="/pipeline", tags=["Data Pipeline"])


class UpdateRequest(BaseModel):
    """Update request model"""

    symbols: Optional[List[str]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class WatchlistUpdate(BaseModel):
    """Watchlist update model"""

    symbols: List[str]


class WatchlistCreate(BaseModel):
    """Watchlist creation model"""

    name: str
    symbols: List[str]
    description: str = ""


async def get_data_pipeline() -> AsyncGenerator[DataPipeline, None]:
    """Dependency to get data pipeline with proper cleanup"""
    pipeline = DataPipeline()
    try:
        yield pipeline
    finally:
        await pipeline.cleanup()


@router.post("/update")
async def run_pipeline_update(
    request: UpdateRequest,
    background_tasks: BackgroundTasks,
    pipeline: DataPipeline = Depends(get_data_pipeline),
):
    """Run data pipeline update for specified symbols"""
    try:
        # Run update in background
        background_tasks.add_task(pipeline.run_full_update, request.symbols)

        return {
            "message": "Pipeline update started in background",
            "symbols": request.symbols or "default watchlist",
            "started_at": datetime.now(timezone.utc),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/watchlist")
async def update_watchlist(
    request: WatchlistUpdate,
    pipeline: DataPipeline = Depends(get_data_pipeline),
):
    """Update the pipeline watchlist"""
    try:
        await pipeline.update_watchlist(request.symbols)
        return {
            "message": "Watchlist updated successfully",
            "symbols": request.symbols,
            "count": len(request.symbols),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_pipeline_status(
    pipeline: DataPipeline = Depends(get_data_pipeline),
):
    """Get current pipeline status with detailed coverage information"""
    try:
        status = await pipeline.get_update_status()
        return status

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/coverage/{symbol}")
async def get_symbol_coverage(
    symbol: str,
    pipeline: DataPipeline = Depends(get_data_pipeline),
):
    """Get detailed data coverage for a specific symbol"""
    try:
        coverage = await pipeline._get_symbol_coverage(symbol.upper())
        return coverage

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/setup-defaults")
async def setup_default_symbols(
    pipeline: DataPipeline = Depends(get_data_pipeline),
):
    """Setup default watchlist symbols"""
    try:
        await pipeline.setup_default_symbols()
        return {
            "message": "Default symbols setup completed",
            "symbols": pipeline.symbols_to_update,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/collect-info/{symbol}")
async def collect_stock_info(
    symbol: str,
    pipeline: DataPipeline = Depends(get_data_pipeline),
):
    """Collect basic information for a specific symbol"""
    try:
        success = await pipeline.collect_stock_info(symbol.upper())

        if success:
            return {
                "message": f"Stock info collected for {symbol}",
                "symbol": symbol.upper(),
                "success": True,
            }
        else:
            return {
                "message": f"Failed to collect info for {symbol}",
                "symbol": symbol.upper(),
                "success": False,
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/collect-data/{symbol}")
async def collect_daily_data(
    symbol: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    pipeline: DataPipeline = Depends(get_data_pipeline),
):
    """Collect daily price data for a specific symbol"""
    try:
        success = await pipeline.collect_daily_data(
            symbol.upper(), start_date, end_date
        )

        if success:
            return {
                "message": f"Daily data collected for {symbol}",
                "symbol": symbol.upper(),
                "start_date": start_date,
                "end_date": end_date,
                "success": True,
            }
        else:
            return {
                "message": f"Failed to collect data for {symbol}",
                "symbol": symbol.upper(),
                "success": False,
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/company/{symbol}")
async def get_company_info(
    symbol: str,
    pipeline: DataPipeline = Depends(get_data_pipeline),
):
    """Get stored company information for a symbol"""
    try:
        company = await pipeline.get_company_info(symbol.upper())

        if company:
            return {
                "symbol": company.symbol,
                "name": company.name,
                "description": company.description,
                "sector": company.sector,
                "industry": company.industry,
                "country": company.country,
                "currency": company.currency,
                "market_cap": company.market_cap,
                "pe_ratio": company.pe_ratio,
                "dividend_yield": company.dividend_yield,
                "updated_at": company.updated_at,
            }
        else:
            raise HTTPException(
                status_code=404, detail=f"Company information not found for {symbol}"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/companies")
async def get_all_companies(
    pipeline: DataPipeline = Depends(get_data_pipeline),
):
    """Get all stored companies"""
    try:
        companies = await pipeline.get_all_companies()

        return {
            "companies": [
                {
                    "symbol": company.symbol,
                    "name": company.name,
                    "sector": company.sector,
                    "industry": company.industry,
                    "market_cap": company.market_cap,
                    "updated_at": company.updated_at,
                }
                for company in companies
            ],
            "total_count": len(companies),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/watchlists")
async def create_watchlist(
    request: WatchlistCreate,
    pipeline: DataPipeline = Depends(get_data_pipeline),
):
    """Create a new watchlist"""
    try:
        watchlist = await pipeline.create_watchlist(
            name=request.name,
            symbols=request.symbols,
            description=request.description,
        )

        if watchlist:
            return {
                "message": f"Watchlist '{request.name}' created successfully",
                "name": watchlist.name,
                "symbols": watchlist.symbols,
                "description": watchlist.description,
                "created_at": watchlist.created_at,
            }
        else:
            raise HTTPException(
                status_code=400, detail=f"Failed to create watchlist '{request.name}'"
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/watchlists/{name}")
async def get_watchlist(
    name: str,
    pipeline: DataPipeline = Depends(get_data_pipeline),
):
    """Get a specific watchlist by name"""
    try:
        watchlist = await pipeline.get_watchlist(name)

        if watchlist:
            return {
                "name": watchlist.name,
                "description": watchlist.description,
                "symbols": watchlist.symbols,
                "auto_update": watchlist.auto_update,
                "update_interval": watchlist.update_interval,
                "last_updated": watchlist.last_updated,
                "created_at": watchlist.created_at,
            }
        else:
            raise HTTPException(status_code=404, detail=f"Watchlist '{name}' not found")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/watchlists")
async def list_watchlists(
    pipeline: DataPipeline = Depends(get_data_pipeline),
):
    """List all watchlists"""
    try:
        watchlists = await pipeline.list_watchlists()

        return {
            "watchlists": [
                {
                    "name": wl.name,
                    "description": wl.description,
                    "symbol_count": len(wl.symbols),
                    "auto_update": wl.auto_update,
                    "last_updated": wl.last_updated,
                    "created_at": wl.created_at,
                }
                for wl in watchlists
            ],
            "total_count": len(watchlists),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
