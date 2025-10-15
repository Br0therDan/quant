"""Schemas for evaluation harness APIs (Phase 4 D3)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.evaluation import (
    BenchmarkMetric,
    ComplianceStatus,
    DetailedMetrics,
    EvaluationStatus,
    EvaluationSummary,
    ExplainabilityArtifact,
    MetricComparison,
    ScenarioEvent,
)


class ScenarioCreate(BaseModel):
    name: str = Field(..., min_length=3)
    description: str
    symbols: list[str] = Field(default_factory=list)
    start_date: datetime | None = None
    end_date: datetime | None = None
    baseline_backtest_ids: list[str] = Field(default_factory=list)
    benchmark_metrics: list[BenchmarkMetric] = Field(default_factory=list)
    stress_events: list[ScenarioEvent] = Field(default_factory=list)


class ScenarioUpdate(BaseModel):
    description: str | None = None
    symbols: list[str] | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    baseline_backtest_ids: list[str] | None = None
    benchmark_metrics: list[BenchmarkMetric] | None = None
    stress_events: list[ScenarioEvent] | None = None


class ScenarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: str
    symbols: list[str]
    start_date: datetime | None
    end_date: datetime | None
    baseline_backtest_ids: list[str]
    benchmark_metrics: list[BenchmarkMetric]
    stress_events: list[ScenarioEvent]
    created_at: datetime
    updated_at: datetime


class EvaluationRequest(BaseModel):
    scenario_name: str
    candidate_backtest_id: str
    candidate_model_name: str
    candidate_model_version: str | None = None
    candidate_metrics: dict[str, float] = Field(default_factory=dict)
    explainability: list[ExplainabilityArtifact] = Field(default_factory=list)
    compliance_inputs: dict[str, Any] = Field(default_factory=dict)


class EvaluationRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    scenario_name: str
    candidate_backtest_id: str
    candidate_model_name: str
    candidate_model_version: str | None
    status: EvaluationStatus
    started_at: datetime
    completed_at: datetime | None
    summary: EvaluationSummary | None
    explainability: list[ExplainabilityArtifact]
    compliance_checks: dict[str, Any]


class EvaluationReport(BaseModel):
    scenario_name: str
    candidate_model_name: str
    candidate_model_version: str | None
    compliance: ComplianceStatus
    metrics: list[MetricComparison]
    notes: str | None = None


# ============================================================================
# Benchmark Suite Schemas
# ============================================================================


class TestCaseCreate(BaseModel):
    """벤치마크 테스트 케이스"""

    name: str = Field(..., min_length=1)
    description: str
    expected_metrics: dict[str, float] = Field(default_factory=dict)


class BenchmarkCreate(BaseModel):
    """벤치마크 스위트 생성"""

    name: str = Field(..., min_length=3)
    description: str
    test_cases: list[TestCaseCreate] = Field(default_factory=list)


class BenchmarkResponse(BaseModel):
    """벤치마크 스위트 응답"""

    model_config = ConfigDict(from_attributes=True)

    name: str
    description: str
    test_cases: list[dict[str, Any]]
    created_at: datetime
    updated_at: datetime


class BenchmarkRunRequest(BaseModel):
    """벤치마크 실행 요청"""

    benchmark_name: str
    model_id: str
    model_version: str | None = None


class BenchmarkRunResponse(BaseModel):
    """벤치마크 실행 결과"""

    benchmark_name: str
    model_id: str
    model_version: str | None
    results: dict[str, Any]
    passed: bool
    started_at: datetime
    completed_at: datetime | None


# ============================================================================
# A/B Testing Schemas
# ============================================================================


class ABTestCreate(BaseModel):
    """A/B 테스트 생성"""

    name: str = Field(..., min_length=3)
    description: str
    model_a_id: str
    model_b_id: str
    traffic_split_a: float = Field(default=50.0, ge=0, le=100)
    sample_size: int = Field(default=1000, gt=0)
    confidence_level: float = Field(default=0.95, gt=0, lt=1)


class ABTestResponse(BaseModel):
    """A/B 테스트 응답"""

    model_config = ConfigDict(from_attributes=True)

    name: str
    description: str
    model_a_id: str
    model_b_id: str
    traffic_split_a: float
    sample_size: int
    confidence_level: float
    status: str
    results: dict[str, Any] | None
    created_at: datetime
    completed_at: datetime | None


# ============================================================================
# Fairness Audit Schemas
# ============================================================================


class FairnessAuditRequest(BaseModel):
    """공정성 감사 요청"""

    model_id: str
    protected_attributes: list[str] = Field(
        ..., min_length=1, description="보호 속성 (예: gender, race, age)"
    )
    fairness_threshold: float = Field(default=0.8, gt=0, le=1)


class FairnessReportResponse(BaseModel):
    """공정성 감사 보고서"""

    model_id: str
    protected_attributes: list[str]
    group_metrics: dict[str, dict[str, float]]
    overall_fairness_score: float
    passed: bool
    recommendations: list[str]
    created_at: datetime


# Re-export DetailedMetrics for API routes
__all__ = [
    "ScenarioCreate",
    "ScenarioUpdate",
    "ScenarioResponse",
    "EvaluationRequest",
    "EvaluationRunResponse",
    "EvaluationReport",
    "DetailedMetrics",
    # Benchmark
    "TestCaseCreate",
    "BenchmarkCreate",
    "BenchmarkResponse",
    "BenchmarkRunRequest",
    "BenchmarkRunResponse",
    # A/B Testing
    "ABTestCreate",
    "ABTestResponse",
    # Fairness
    "FairnessAuditRequest",
    "FairnessReportResponse",
]
