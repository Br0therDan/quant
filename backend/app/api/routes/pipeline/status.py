"""
Pipeline Status and Monitoring API Routes
"""

from datetime import datetime, timezone
from typing import AsyncGenerator
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks

from app.api.deps import get_current_active_verified_user
from app.schemas.watchlist import UpdateRequest
from app.services.data_pipeline import DataPipeline

router = APIRouter(dependencies=[Depends(get_current_active_verified_user)])


async def get_data_pipeline() -> AsyncGenerator[DataPipeline, None]:
    """
    Dependency injection for DataPipeline service.

    Provides a DataPipeline instance with proper resource cleanup.
    The pipeline is automatically cleaned up after the request completes
    to ensure proper database connection management.

    Yields:
        DataPipeline: Configured data pipeline service instance
    """
    pipeline = DataPipeline()
    try:
        yield pipeline
    finally:
        await pipeline.cleanup()


@router.get("/")
async def get_pipeline_status(
    pipeline: DataPipeline = Depends(get_data_pipeline),
):
    """
    Get comprehensive pipeline status and health information.

    Returns detailed information about the current state of the data pipeline,
    including data coverage statistics, update timestamps, and system health metrics.
    This endpoint is essential for monitoring the overall health of the data
    collection and processing system.

    Returns:
        dict: Pipeline status containing:
            - overall_status: Current pipeline health status
            - last_update: Timestamp of last successful update
            - coverage_stats: Data coverage statistics per symbol
            - active_symbols: Currently monitored symbols count
            - error_count: Number of recent errors

    Raises:
        HTTPException: 500 if status retrieval fails
    """
    try:
        status = await pipeline.get_update_status()
        return status

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/setup-defaults")
async def setup_default_symbols(
    pipeline: DataPipeline = Depends(get_data_pipeline),
):
    """
    Initialize default watchlist with standard symbols.

    Sets up the pipeline with a predefined set of popular stock symbols
    for immediate use. This is typically called during initial system setup
    or when resetting the pipeline to defaults. Creates the 'default' watchlist
    if it doesn't exist.

    Default symbols include major tech stocks: AAPL, MSFT, GOOGL, AMZN, etc.

    Returns:
        dict: Setup confirmation containing:
            - message: Success confirmation message
            - symbols: List of symbols that were set up

    Raises:
        HTTPException: 500 if default setup fails
    """
    try:
        await pipeline.setup_default_symbols()
        return {
            "message": "Default symbols setup completed",
            "symbols": pipeline.symbols_to_update,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update")
async def run_pipeline_update(
    request: UpdateRequest,
    background_tasks: BackgroundTasks,
    pipeline: DataPipeline = Depends(get_data_pipeline),
):
    """
    Execute comprehensive data pipeline update for specified symbols.

    Initiates a full data collection and update process for the specified
    symbols or the default watchlist. The update runs asynchronously in the
    background to avoid blocking the API response. Includes company information
    retrieval, historical price data collection, and data validation.

    Args:
        request: Update configuration containing:
            - symbols: Optional list of symbols to update (uses default if None)
            - start_date: Optional start date for data collection
            - end_date: Optional end date for data collection
        background_tasks: FastAPI background task manager

    Returns:
        dict: Update initiation confirmation containing:
            - message: Update start confirmation
            - symbols: Symbols being updated
            - started_at: UTC timestamp when update began

    Raises:
        HTTPException: 500 if update initiation fails

    Note:
        This is an asynchronous operation. Use /status endpoint to monitor progress.
    """
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
