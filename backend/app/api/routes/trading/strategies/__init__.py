from .strategy import router as strategies_router
from .template import router as templates_router
from fastapi import APIRouter

router = APIRouter()

router.include_router(strategies_router)
router.include_router(templates_router, prefix="/templates")
