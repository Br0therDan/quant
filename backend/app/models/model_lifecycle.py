"""Model lifecycle management documents (Phase 4 D2)."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from beanie import Document
from pydantic import BaseModel, Field
from pymongo import IndexModel

from .base_model import BaseDocument


class ExperimentStatus(str, Enum):
    """Lifecycle state for an experiment."""

    ACTIVE = "active"
    ARCHIVED = "archived"


class RunStatus(str, Enum):
    """Execution status for a model run."""

    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ModelStage(str, Enum):
    """Deployment stage for a model version."""

    EXPERIMENTAL = "experimental"
    STAGING = "staging"
    PRODUCTION = "production"
    ARCHIVED = "archived"


class ChecklistStatus(str, Enum):
    """Approval checklist states."""

    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"


class DriftSeverity(str, Enum):
    """Severity flag for drift events."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DeploymentChecklistItem(BaseModel):
    """Individual checklist item used during approvals."""

    name: str = Field(..., description="Checklist 항목 이름")
    status: ChecklistStatus = Field(
        default=ChecklistStatus.PENDING, description="체크 상태"
    )
    note: str | None = Field(None, description="검토 메모")
    completed_at: datetime | None = Field(None, description="완료 시간")


class MetricSnapshot(BaseModel):
    """Metric snapshot stored alongside runs/versions."""

    metric_name: str = Field(..., description="메트릭 이름")
    value: float = Field(..., description="메트릭 값")
    dataset: str | None = Field(None, description="평가 데이터셋")


class ParameterSnapshot(BaseModel):
    """Parameter capture for a run."""

    name: str = Field(..., description="파라미터 이름")
    value: Any = Field(..., description="파라미터 값")


class ArtifactReference(BaseModel):
    """Reference to persisted artifacts (MLflow/W&B)."""

    name: str = Field(..., description="아티팩트 이름")
    uri: str = Field(..., description="저장 위치 URI")
    artifact_type: str = Field(..., description="아티팩트 타입 (model, report 등)")


class ModelExperiment(BaseDocument):
    """Registered experiment grouping related runs."""

    name: str = Field(..., description="실험 이름", min_length=3)
    description: str = Field(..., description="실험 설명")
    owner: str = Field(..., description="담당자")
    status: ExperimentStatus = Field(
        default=ExperimentStatus.ACTIVE, description="실험 상태"
    )
    tags: list[str] = Field(default_factory=list, description="태그")
    metadata: dict[str, Any] = Field(default_factory=dict, description="추가 메타데이터")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="생성 시간"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="업데이트 시간"
    )

    class Settings:
        name = "model_experiments"
        indexes = [
            IndexModel([("name", 1)], unique=True),
            IndexModel([("owner", 1)]),
            IndexModel([("status", 1)]),
        ]


class ModelRun(BaseDocument):
    """Single training/evaluation run tracked for lifecycle governance."""

    run_id: str = Field(..., description="실행 ID", min_length=8)
    experiment_name: str = Field(..., description="실험 이름")
    status: RunStatus = Field(default=RunStatus.RUNNING, description="실행 상태")
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="시작 시간"
    )
    completed_at: datetime | None = Field(None, description="완료 시간")
    parameters: list[ParameterSnapshot] = Field(
        default_factory=list, description="파라미터"
    )
    metrics: list[MetricSnapshot] = Field(default_factory=list, description="메트릭")
    dataset_name: str | None = Field(None, description="데이터셋 이름")
    dataset_version: str | None = Field(None, description="데이터셋 버전")
    tags: list[str] = Field(default_factory=list, description="태그")
    artifacts: list[ArtifactReference] = Field(
        default_factory=list, description="연결된 아티팩트"
    )
    notes: str | None = Field(None, description="추가 메모")

    class Settings:
        name = "model_runs"
        indexes = [
            IndexModel([("run_id", 1)], unique=True),
            IndexModel([("experiment_name", 1)]),
            IndexModel([("status", 1)]),
            IndexModel([("started_at", -1)]),
        ]


class ModelVersion(BaseDocument):
    """Model registry entry tracking deployment approvals."""

    model_name: str = Field(..., description="모델 이름")
    version: str = Field(..., description="버전")
    run_id: str = Field(..., description="연결된 실행 ID")
    stage: ModelStage = Field(default=ModelStage.EXPERIMENTAL, description="배포 단계")
    approval_checklist: list[DeploymentChecklistItem] = Field(
        default_factory=list, description="배포 체크리스트"
    )
    metrics: list[MetricSnapshot] = Field(default_factory=list, description="메트릭")
    approved_by: str | None = Field(None, description="승인자")
    approved_at: datetime | None = Field(None, description="승인 시간")
    rollback_notes: str | None = Field(None, description="롤백 메모")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="생성 시간"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="업데이트 시간"
    )

    class Settings:
        name = "model_versions"
        indexes = [
            IndexModel([("model_name", 1), ("version", 1)], unique=True),
            IndexModel([("model_name", 1), ("stage", 1)]),
            IndexModel([("approved_at", -1)]),
        ]


class DriftEvent(Document):
    """Detected drift events for monitoring."""

    model_name: str = Field(..., description="모델 이름")
    version: str = Field(..., description="모델 버전")
    detected_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="감지 시간"
    )
    severity: DriftSeverity = Field(..., description="심각도")
    metric_name: str = Field(..., description="감지된 메트릭")
    metric_value: float = Field(..., description="메트릭 값")
    threshold: float | None = Field(None, description="임계값")
    message: str | None = Field(None, description="추가 메시지")
    remediation_action: str | None = Field(
        None, description="대응 계획 (재학습, 롤백 등)"
    )

    class Settings:
        name = "model_drift_events"
        indexes = [
            IndexModel([("model_name", 1), ("version", 1), ("detected_at", -1)]),
            IndexModel([("severity", 1)]),
        ]
