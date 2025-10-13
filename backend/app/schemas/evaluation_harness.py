"""Schemas for evaluation harness APIs (Phase 4 D3)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.evaluation import (
    BenchmarkMetric,
    ComplianceStatus,
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
