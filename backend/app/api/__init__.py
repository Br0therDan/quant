"""
Initialize API routes package
"""

from fastapi import APIRouter
from .routes import (
    market_data_router,  # 새로운 도메인별 구조
    backtests_router,
    strategies_router,
    signals_router,
    watchlists_router,
    dashboard_router,
    system_router,
    ml_router,
    gen_ai_router,
)

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(
    market_data_router, prefix="/market-data", tags=["Market Data"]
)
api_router.include_router(watchlists_router, prefix="/watchlists", tags=["Watchlist"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(backtests_router, prefix="/backtests", tags=["Backtest"])
api_router.include_router(strategies_router, prefix="/strategies", tags=["Strategy"])
api_router.include_router(signals_router, prefix="/signals", tags=["Signals"])
api_router.include_router(ml_router, prefix="/ml", tags=["ML"])
api_router.include_router(gen_ai_router, prefix="/gen-ai", tags=["Gen AI"])
api_router.include_router(system_router, prefix="/system", tags=["System"])


__all__ = ["api_router"]
