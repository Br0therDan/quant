"""
Initialize API routes package
"""

from fastapi import APIRouter
from .routes import (
    market_data_router,  # 새로운 도메인별 구조
    backtests_router,
    strategies_router,
    watchlists_router,
    dashboard_router,
    tasks_router,
    signals_router,
    ml_router,
    chatops_router,
    narrative_router,
    strategy_builder_router,
    chatops_advanced_router,
    feature_store_router,
)

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(market_data_router, prefix="/market-data")
api_router.include_router(strategies_router, prefix="/strategies")
api_router.include_router(backtests_router, prefix="/backtests", tags=["Backtest"])
api_router.include_router(watchlists_router, prefix="/watchlists", tags=["Watchlist"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(tasks_router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(signals_router, prefix="/signals", tags=["Signals"])
api_router.include_router(ml_router, prefix="/ml", tags=["ML"])
api_router.include_router(chatops_router, prefix="/chatops", tags=["ChatOps"])
api_router.include_router(narrative_router, prefix="/narrative", tags=["Narrative"])
api_router.include_router(
    strategy_builder_router, prefix="/strategy-builder", tags=["Strategy Builder"]
)
api_router.include_router(
    chatops_advanced_router, prefix="/chatops-advanced", tags=["ChatOps Advanced"]
)
api_router.include_router(
    feature_store_router, prefix="/features", tags=["Feature Store"]
)


__all__ = ["api_router"]
