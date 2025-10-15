"""ML Platform Domain Enums"""

from enum import Enum


class ExperimentStatus(str, Enum):
    """실험 상태"""

    ACTIVE = "active"
    ARCHIVED = "archived"


class RunStatus(str, Enum):
    """실행 상태"""

    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ModelStage(str, Enum):
    """모델 배포 단계"""

    EXPERIMENTAL = "experimental"
    STAGING = "staging"
    PRODUCTION = "production"
    ARCHIVED = "archived"


class ChecklistStatus(str, Enum):
    """체크리스트 상태"""

    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"


class DriftSeverity(str, Enum):
    """드리프트 심각도"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DeploymentStatus(str, Enum):
    """모델 배포 상태"""

    PENDING = "pending"
    VALIDATING = "validating"
    DEPLOYING = "deploying"
    ACTIVE = "active"
    FAILED = "failed"
    ROLLBACK = "rollback"
    TERMINATED = "terminated"


class DeploymentEnvironment(str, Enum):
    """배포 환경"""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class FeatureType(str, Enum):
    """피처 타입"""

    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    TEXT = "text"


class FeatureStatus(str, Enum):
    """피처 상태"""

    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class DataType(str, Enum):
    """데이터 타입"""

    FLOAT = "float"
    INTEGER = "integer"
    STRING = "string"
    BOOLEAN = "boolean"
    TIMESTAMP = "timestamp"


class DatasetSourceType(str, Enum):
    """데이터셋 소스 타입"""

    DUCKDB = "duckdb"
    CSV = "csv"
    PARQUET = "parquet"
    MONGODB = "mongodb"
    API = "api"


class EvaluationStatus(str, Enum):
    """평가 상태"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ComplianceStatus(str, Enum):
    """컴플라이언스 상태"""

    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"


class EvaluationMetricType(str, Enum):
    """평가 지표 타입"""

    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    AUC_ROC = "auc_roc"
    MAE = "mae"
    MSE = "mse"
    RMSE = "rmse"
    SHARPE_RATIO = "sharpe_ratio"
