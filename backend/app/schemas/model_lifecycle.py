"""Schemas for model lifecycle management (Phase 4 D2)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.model_lifecycle import (
    ArtifactReference,
    DeploymentChecklistItem,
    DriftSeverity,
    ExperimentStatus,
    MetricSnapshot,
    ModelStage,
    ParameterSnapshot,
    RunStatus,
)


class ExperimentCreate(BaseModel):
    name: str = Field(..., min_length=3)
    description: str
    owner: str
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExperimentUpdate(BaseModel):
    description: str | None = None
    owner: str | None = None
    status: ExperimentStatus | None = None
    tags: list[str] | None = None
    metadata: dict[str, Any] | None = None


class ExperimentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: str
    owner: str
    status: ExperimentStatus
    tags: list[str]
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class RunCreate(BaseModel):
    run_id: str = Field(..., min_length=8)
    experiment_name: str
    parameters: list[ParameterSnapshot] = Field(default_factory=list)
    metrics: list[MetricSnapshot] = Field(default_factory=list)
    dataset_name: str | None = None
    dataset_version: str | None = None
    tags: list[str] = Field(default_factory=list)
    artifacts: list[ArtifactReference] = Field(default_factory=list)
    notes: str | None = None


class RunUpdate(BaseModel):
    status: RunStatus | None = None
    metrics: list[MetricSnapshot] | None = None
    completed_at: datetime | None = None
    artifacts: list[ArtifactReference] | None = None
    notes: str | None = None


class RunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    run_id: str
    experiment_name: str
    status: RunStatus
    started_at: datetime
    completed_at: datetime | None
    parameters: list[ParameterSnapshot]
    metrics: list[MetricSnapshot]
    dataset_name: str | None
    dataset_version: str | None
    tags: list[str]
    artifacts: list[ArtifactReference]
    notes: str | None


class ChecklistUpdateRequest(BaseModel):
    stage: ModelStage | None = None
    checklist: list[DeploymentChecklistItem]
    approved_by: str | None = None
    approval_notes: str | None = None


class ModelVersionCreate(BaseModel):
    model_name: str
    version: str
    run_id: str
    stage: ModelStage = ModelStage.EXPERIMENTAL
    metrics: list[MetricSnapshot] = Field(default_factory=list)
    approval_checklist: list[DeploymentChecklistItem] = Field(default_factory=list)


class ModelVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    model_name: str
    version: str
    run_id: str
    stage: ModelStage
    approval_checklist: list[DeploymentChecklistItem]
    metrics: list[MetricSnapshot]
    approved_by: str | None
    approved_at: datetime | None
    rollback_notes: str | None
    created_at: datetime
    updated_at: datetime


class ModelComparisonRequest(BaseModel):
    versions: list[str] = Field(..., min_length=1)


class MetricComparison(BaseModel):
    metric_name: str
    values: dict[str, float]


class ModelComparisonResponse(BaseModel):
    model_name: str
    comparisons: list[MetricComparison]


class DriftEventCreate(BaseModel):
    model_name: str
    version: str
    severity: DriftSeverity
    metric_name: str
    metric_value: float
    threshold: float | None = None
    message: str | None = None
    remediation_action: str | None = None


class DriftEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    model_name: str
    version: str
    detected_at: datetime
    severity: DriftSeverity
    metric_name: str
    metric_value: float
    threshold: float | None
    message: str | None
    remediation_action: str | None
