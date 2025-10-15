"""
ML Platform domain API routes
"""
from fastapi import APIRouter, Depends
from mysingle_quant.auth import get_current_active_verified_user
from .evaluation import router as evaluation_router
from .lifecycle import router as lifecycle_router
from .train import router as train_router
from .feature_store import router as feature_store_router

router = APIRouter(dependencies=[Depends(get_current_active_verified_user)])

router.include_router(evaluation_router, prefix="/evaluation")
router.include_router(lifecycle_router, prefix="/lifecycle")
router.include_router(train_router, prefix="/train")
router.include_router(feature_store_router, prefix="/features")
