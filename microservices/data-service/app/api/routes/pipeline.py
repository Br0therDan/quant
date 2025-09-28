"""
Data Pipeline API Routes
"""

from datetime import datetime
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
            "started_at": datetime.utcnow(),
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
    """Get current pipeline status"""
    try:
        status = await pipeline.get_update_status()
        return status

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
