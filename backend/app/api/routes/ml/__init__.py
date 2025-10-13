"""ML API routes - Phase 3.2 ML Integration."""

from fastapi import APIRouter

from app.api.routes.ml import train

router = APIRouter()
router.include_router(train.router)

__all__ = ["router"]
