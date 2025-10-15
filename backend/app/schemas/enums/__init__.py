"""
Unified Enum definitions for all domains
모든 도메인의 Enum 타입을 통합 관리

이 패키지는 도메인별로 분리된 Enum들을 re-export하여
기존 코드의 import 경로를 유지합니다.

사용 예:
    from app.schemas.enums import BacktestStatus, StrategyType
"""

# Trading Domain Enums
from .trading import (
    BacktestStatus,
    OrderType,
    SignalType,
    StrategyType,
    TradeType,
)

# Market Data Domain Enums
from .market_data import (
    DataInterval,
    DataQualitySeverity,
    MarketRegimeType,
)

# ML Platform Domain Enums
from .ml_platform import (
    ChecklistStatus,
    ComplianceStatus,
    DatasetSourceType,
    DataType,
    DeploymentEnvironment,
    DeploymentStatus,
    DriftSeverity,
    EvaluationMetricType,
    EvaluationStatus,
    ExperimentStatus,
    FeatureStatus,
    FeatureType,
    ModelStage,
    RunStatus,
)

# Generative AI Domain Enums
from .gen_ai import (
    ChatCommandType,
    ConversationRole,
    IntentType,
    PromptRiskLevel,
    PromptStatus,
    ReportFormat,
    ReportRecommendation,
    ReportSectionType,
)

# User Domain Enums
from .user import (
    NotificationType,
    WatchlistType,
)

# System Domain Enums
from .system import (
    LogLevel,
    SeverityLevel,
    TaskStatus,
)

__all__ = [
    # Trading
    "BacktestStatus",
    "OrderType",
    "SignalType",
    "StrategyType",
    "TradeType",
    # Market Data
    "DataInterval",
    "DataQualitySeverity",
    "MarketRegimeType",
    # ML Platform
    "ChecklistStatus",
    "ComplianceStatus",
    "DatasetSourceType",
    "DataType",
    "DeploymentEnvironment",
    "DeploymentStatus",
    "DriftSeverity",
    "EvaluationMetricType",
    "EvaluationStatus",
    "ExperimentStatus",
    "FeatureStatus",
    "FeatureType",
    "ModelStage",
    "RunStatus",
    # Gen AI
    "ChatCommandType",
    "ConversationRole",
    "IntentType",
    "PromptRiskLevel",
    "PromptStatus",
    "ReportFormat",
    "ReportRecommendation",
    "ReportSectionType",
    # User
    "NotificationType",
    "WatchlistType",
    # System
    "LogLevel",
    "SeverityLevel",
    "TaskStatus",
]
