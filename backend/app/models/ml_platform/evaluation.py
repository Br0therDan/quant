"""Evaluation harness documents for Phase 4 D3."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field
from pymongo import IndexModel

from app.schemas.enums import ComplianceStatus, EvaluationStatus

from app.models.base_model import BaseDocument


class BenchmarkMetric(BaseModel):
    """Benchmark metric definition used by evaluation scenarios."""

    name: str = Field(..., description="메트릭 이름")
    threshold: float | None = Field(None, description="임계값")
    higher_is_better: bool = Field(default=True, description="높을수록 좋은 메트릭 여부")


class ScenarioEvent(BaseModel):
    """Historical event or stress period definition."""

    label: str = Field(..., description="이벤트 라벨")
    start: datetime = Field(..., description="시작일")
    end: datetime = Field(..., description="종료일")


class ExplainabilityArtifact(BaseModel):
    """Explainability artifact reference (e.g., SHAP)."""

    feature_name: str = Field(..., description="피처 이름")
    importance: float = Field(..., description="중요도")
    impact_direction: str | None = Field(None, description="영향 방향 (+/-)")


class EvaluationScenario(BaseDocument):
    """Pre-configured evaluation scenario."""

    name: str = Field(..., description="시나리오 이름", min_length=3)
    description: str = Field(..., description="설명")
    symbols: list[str] = Field(default_factory=list, description="평가 심볼")
    start_date: datetime | None = Field(None, description="시작일")
    end_date: datetime | None = Field(None, description="종료일")
    baseline_backtest_ids: list[str] = Field(
        default_factory=list, description="비교용 백테스트 ID"
    )
    benchmark_metrics: list[BenchmarkMetric] = Field(
        default_factory=list, description="벤치마크 메트릭"
    )
    stress_events: list[ScenarioEvent] = Field(
        default_factory=list, description="중요 이벤트"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="생성 시간"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="업데이트 시간"
    )

    class Settings:
        name = "evaluation_scenarios"
        indexes = [
            IndexModel([("name", 1)], unique=True),
            IndexModel([("created_at", -1)]),
        ]


class MetricComparison(BaseModel):
    """Comparison between candidate and baseline."""

    metric_name: str = Field(..., description="메트릭 이름")
    candidate: float = Field(..., description="후보 모델 값")
    baseline_average: float | None = Field(None, description="기준 평균")
    delta: float | None = Field(None, description="차이")


class DetailedMetrics(BaseModel):
    """Detailed evaluation metrics for single job."""

    confusion_matrix: list[list[int]] = Field(default_factory=list, description="혼동 행렬")
    class_labels: list[str] = Field(default_factory=list, description="클래스 라벨")
    roc_curve: dict[str, list[float]] | None = Field(
        None, description="ROC 커브 (fpr, tpr, thresholds)"
    )
    precision_recall_curve: dict[str, list[float]] | None = Field(
        None, description="PR 커브 (precision, recall, thresholds)"
    )
    accuracy: float | None = Field(None, description="정확도")
    precision: float | None = Field(None, description="정밀도")
    recall: float | None = Field(None, description="재현율")
    f1_score: float | None = Field(None, description="F1 점수")
    auc_roc: float | None = Field(None, description="AUC-ROC")


class EvaluationSummary(BaseModel):
    """Summary of evaluation outputs."""

    metrics: list[MetricComparison] = Field(default_factory=list, description="메트릭 비교")
    compliance: ComplianceStatus = Field(
        default=ComplianceStatus.PASSED, description="컴플라이언스 결과"
    )
    notes: str | None = Field(None, description="메모")
    detailed_metrics: DetailedMetrics | None = Field(None, description="상세 평가 메트릭")


class EvaluationRun(BaseDocument):
    """Stored evaluation execution."""

    scenario_name: str = Field(..., description="시나리오 이름")
    candidate_backtest_id: str = Field(..., description="후보 백테스트 ID")
    candidate_model_name: str = Field(..., description="모델 이름")
    candidate_model_version: str | None = Field(None, description="모델 버전")
    status: EvaluationStatus = Field(
        default=EvaluationStatus.PENDING, description="실행 상태"
    )
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="시작 시간"
    )
    completed_at: datetime | None = Field(None, description="완료 시간")
    summary: EvaluationSummary | None = Field(None, description="요약")
    explainability: list[ExplainabilityArtifact] = Field(
        default_factory=list, description="설명 가능성 아티팩트"
    )
    compliance_checks: dict[str, Any] = Field(
        default_factory=dict, description="컴플라이언스 점검 기록"
    )

    class Settings:
        name = "evaluation_runs"
        indexes = [
            IndexModel([("scenario_name", 1), ("started_at", -1)]),
            IndexModel([("candidate_model_name", 1), ("candidate_model_version", 1)]),
        ]
