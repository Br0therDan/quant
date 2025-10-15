"""
System API routes
"""
from fastapi import APIRouter, Depends
from mysingle_quant.auth import get_current_active_superuser
from .health import router as health_router
from .tasks import router as tasks_router

router = APIRouter(dependencies=[Depends(get_current_active_superuser)])

router.include_router(health_router, prefix="/health")
router.include_router(tasks_router, prefix="/tasks")
