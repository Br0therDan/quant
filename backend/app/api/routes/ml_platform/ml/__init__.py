"""ML API routes - Phase 3.2 ML Integration."""

from fastapi import APIRouter

from app.api.routes.ml_platform.ml import lifecycle, train
from app.api.routes.ml_platform.ml import evaluation

router = APIRouter()
router.include_router(train.router)
router.include_router(lifecycle.router)
router.include_router(evaluation.router)

__all__ = ["router"]
