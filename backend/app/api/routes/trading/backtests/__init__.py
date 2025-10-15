from fastapi import APIRouter
from .backtests import router as backtests_router
from .optimize_backtests import router as optimize_backtests_router

router = APIRouter()

router.include_router(backtests_router)
router.include_router(optimize_backtests_router, prefix="/optimize")
