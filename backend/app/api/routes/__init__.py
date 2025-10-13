"""
Initialize routes package
"""

from .market_data import router as market_data_router  # 새로운 도메인별 구조
from .strategies import router as strategies_router
from .backtests import router as backtests_router
from .health import router as health_router
from .watchlists import router as watchlists_router
from .dashboard import router as dashboard_router
from .tasks import router as tasks_router
from .signals import router as signals_router
from .ml import router as ml_router
from .chatops import router as chatops_router
from .narrative import router as narrative_router


__all__ = [
    "market_data_router",  # 새로운 도메인별 구조
    "health_router",
    "backtests_router",
    "strategies_router",
    "watchlists_router",
    "dashboard_router",
    "tasks_router",
    "signals_router",
    "ml_router",
    "chatops_router",
    "narrative_router",
]
