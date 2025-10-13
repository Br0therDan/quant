"""Optimization API routes for Optuna-based hyperparameter tuning."""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query

from app.schemas.optimization import (
    OptimizationRequest,
    OptimizationResponse,
    StudyListResponse,
)
from app.services.service_factory import service_factory

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Optimization"])


@router.post("/", response_model=OptimizationResponse)
async def create_optimization_study(
    request: OptimizationRequest,
    background_tasks: BackgroundTasks,
) -> OptimizationResponse:
    """Create and start a new optimization study.

    Args:
        request: Optimization configuration
        background_tasks: FastAPI background tasks for async execution

    Returns:
        OptimizationResponse with study name and status
    """
    try:
        optimization_service = service_factory.get_optimization_service()

        # Create study
        study_name = await optimization_service.create_study(request)

        # Run study in background
        background_tasks.add_task(
            _run_optimization_study,
            study_name=study_name,
        )

        logger.info(f"Started optimization study: {study_name}")

        return OptimizationResponse(
            status="success",
            study_name=study_name,
            message=f"Optimization study started: {study_name}",
            data=None,
        )

    except Exception as e:
        logger.error(f"Failed to create optimization study: {e}", exc_info=e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{study_name}", response_model=OptimizationResponse)
async def get_optimization_progress(study_name: str) -> OptimizationResponse:
    """Get current progress of an optimization study.

    Args:
        study_name: Study identifier

    Returns:
        OptimizationResponse with progress information
    """
    try:
        optimization_service = service_factory.get_optimization_service()
        progress = await optimization_service.get_study_progress(study_name)

        return OptimizationResponse(
            status="success",
            study_name=study_name,
            message=f"Progress: {progress.trials_completed}/{progress.n_trials} trials",
            data=progress,
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get optimization progress: {e}", exc_info=e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{study_name}/result", response_model=OptimizationResponse)
async def get_optimization_result(study_name: str) -> OptimizationResponse:
    """Get final result of a completed optimization study.

    Args:
        study_name: Study identifier

    Returns:
        OptimizationResponse with optimization result
    """
    try:
        optimization_service = service_factory.get_optimization_service()
        result = await optimization_service.get_study_result(study_name)

        return OptimizationResponse(
            status="success",
            study_name=study_name,
            message=f"Optimization completed with best value: {result.best_value:.4f}",
            data=result,
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get optimization result: {e}", exc_info=e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=StudyListResponse)
async def list_optimization_studies(
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    strategy_name: Optional[str] = Query(None, description="Filter by strategy name"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of studies"),
) -> StudyListResponse:
    """List optimization studies with optional filters.

    Args:
        symbol: Filter by symbol
        strategy_name: Filter by strategy name
        status: Filter by status (pending/running/completed/failed)
        limit: Maximum number of studies to return

    Returns:
        StudyListResponse with list of studies
    """
    try:
        optimization_service = service_factory.get_optimization_service()
        studies = await optimization_service.list_studies(
            symbol=symbol,
            strategy_name=strategy_name,
            status=status,
            limit=limit,
        )

        return StudyListResponse(
            status="success",
            total=len(studies),
            studies=studies,
        )

    except Exception as e:
        logger.error(f"Failed to list optimization studies: {e}", exc_info=e)
        raise HTTPException(status_code=500, detail=str(e))


async def _run_optimization_study(study_name: str) -> None:
    """Background task to run optimization study.

    Args:
        study_name: Study identifier
    """
    try:
        optimization_service = service_factory.get_optimization_service()
        result = await optimization_service.run_study(study_name)
        logger.info(
            f"Optimization study completed: {study_name}, "
            f"best_value={result.best_value:.4f}"
        )
    except Exception as e:
        logger.error(
            f"Optimization study failed: {study_name}",
            exc_info=e,
        )


__all__ = ["router"]
