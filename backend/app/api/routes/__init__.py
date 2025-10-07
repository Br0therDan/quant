"""
Initialize routes package
"""

from .market_data import router as market_data_router  # 새로운 도메인별 구조
from .strategies import router as strategies_router
from .templates import router as templates_router
from .backtests import router as backtests_router
from .health import router as health_router
from .pipeline import router as pipeline_router


__all__ = [
    "market_data_router",  # 새로운 도메인별 구조
    "health_router",
    "backtests_router",
    "strategies_router",
    "templates_router",
    "pipeline_router",
]
