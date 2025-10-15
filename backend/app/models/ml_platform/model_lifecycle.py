"""Model lifecycle management documents (Phase 4 D2)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from beanie import Document
from pydantic import BaseModel, Field
from pymongo import IndexModel

from app.schemas.enums import (
    ChecklistStatus,
    DeploymentEnvironment,
    DeploymentStatus,
    DriftSeverity,
    ExperimentStatus,
    ModelStage,
    RunStatus,
)

from app.models.base_model import BaseDocument


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

    # Phase 4 Enhancement: 메트릭 추적
    metrics: dict[str, float] = Field(
        default_factory=dict, description="실험 메트릭 (accuracy, f1_score 등)"
    )
    duration_seconds: float | None = Field(None, description="실행 시간 (초)")

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
    remediation_action: str | None = Field(None, description="대응 계획 (재학습, 롤백 등)")

    class Settings:
        name = "model_drift_events"
        indexes = [
            IndexModel([("model_name", 1), ("version", 1), ("detected_at", -1)]),
            IndexModel([("severity", 1)]),
            IndexModel([("model_name", 1), ("severity", 1)]),
            IndexModel([("detected_at", -1)]),
        ]


class EndpointConfig(BaseModel):
    """Deployment endpoint configuration."""

    instances: int = Field(default=1, ge=1, description="인스턴스 수")
    instance_type: str = Field(default="standard", description="인스턴스 타입")
    auto_scaling: bool = Field(default=False, description="자동 스케일링 여부")
    min_instances: int | None = Field(None, ge=1, description="최소 인스턴스 수")
    max_instances: int | None = Field(None, ge=1, description="최대 인스턴스 수")


class DeploymentMetrics(BaseModel):
    """Deployment monitoring metrics."""

    request_count: int = Field(default=0, description="총 요청 수")
    error_count: int = Field(default=0, description="에러 수")
    avg_latency_ms: float | None = Field(None, description="평균 응답 시간 (ms)")
    p95_latency_ms: float | None = Field(None, description="P95 응답 시간 (ms)")
    p99_latency_ms: float | None = Field(None, description="P99 응답 시간 (ms)")
    last_updated: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="마지막 업데이트 시간"
    )


class Deployment(BaseDocument):
    """Model deployment tracking document."""

    # Model information
    model_name: str = Field(..., description="모델 이름")
    model_version: str = Field(..., description="모델 버전")
    experiment_name: str | None = Field(None, description="실험 이름")

    # Deployment configuration
    status: DeploymentStatus = Field(
        default=DeploymentStatus.PENDING, description="배포 상태"
    )
    environment: DeploymentEnvironment = Field(..., description="배포 환경")
    endpoint: str | None = Field(None, description="엔드포인트 URL")
    endpoint_config: EndpointConfig | None = Field(default=None, description="엔드포인트 설정")

    # Health and monitoring
    health_status: str | None = Field(None, description="헬스 상태")
    metrics: DeploymentMetrics | None = Field(default=None, description="모니터링 메트릭")

    # Metadata
    created_by: str = Field(..., description="배포자")
    deployed_at: datetime | None = Field(None, description="배포 완료 시간")
    terminated_at: datetime | None = Field(None, description="종료 시간")
    rollback_from: str | None = Field(None, description="롤백 이전 배포 ID")

    # Logs and notes
    deployment_notes: str | None = Field(None, description="배포 노트")
    error_message: str | None = Field(None, description="에러 메시지")

    class Settings:
        name = "deployments"
        indexes = [
            IndexModel([("model_name", 1)]),
            IndexModel([("model_version", 1)]),
            IndexModel([("environment", 1)]),
            IndexModel([("status", 1)]),
            IndexModel([("created_at", -1)]),
            IndexModel([("model_name", 1), ("environment", 1)]),
        ]
