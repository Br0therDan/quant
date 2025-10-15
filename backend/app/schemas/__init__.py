"""
Backend Schemas Package
모든 도메인의 Pydantic 스키마를 통합 관리

도메인별로 분리된 스키마는 직접 import하여 사용합니다.

사용 예:
    from app.schemas.trading.backtest import BacktestCreate, BacktestResponse
    from app.schemas.trading.strategy import StrategyCreate, StrategyResponse
    from app.schemas.ml_platform.model_lifecycle import ExperimentCreate
    from app.schemas.gen_ai.narrative import NarrativeReportResponse
"""

# 순환 import 방지를 위해 자동 re-export하지 않습니다.
# 각 도메인 스키마는 명시적으로 import하여 사용하세요.
__all__ = []  # 명시적으로 빈 리스트로 설정


# Trading Domain
from .trading import *

# ML Platform Domain
from .ml_platform import *

# Generative AI Domain
from .gen_ai import *

# User Domain
from .user import *

# Market Data Domain (기존 구조 유지)
from .market_data import *

# Base schemas
from app.schemas.base_schema import *

# Trading Domain
from .trading import *

# ML Platform Domain
from .ml_platform import *

# Generative AI Domain
from .gen_ai import *

# User Domain
from .user import *

# Market Data Domain (기존 구조 유지)
from .market_data import *

# Base schemas
from app.schemas.base_schema import *
