"""
System API routes
"""
from fastapi import APIRouter
from .health import router as health_router
from .tasks import router as tasks_router

router = APIRouter()

router.include_router(health_router, prefix="/health")
router.include_router(tasks_router, prefix="/tasks")
