"""Schemas for prompt governance APIs (Phase 4 D4)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.gen_ai.prompt_governance import (
    PromptEvaluationSummary,
    PromptRiskLevel,
    PromptStatus,
)


class PromptTemplateCreate(BaseModel):
    prompt_id: str
    version: str
    name: str
    description: str
    content: str
    owner: str
    tags: list[str] = Field(default_factory=list)
    risk_level: PromptRiskLevel = PromptRiskLevel.MEDIUM
    policies: list[str] = Field(default_factory=list)


class PromptTemplateUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    content: str | None = None
    tags: list[str] | None = None
    risk_level: PromptRiskLevel | None = None
    policies: list[str] | None = None
    status: PromptStatus | None = None
    approval_notes: str | None = None


class PromptTemplateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    prompt_id: str
    version: str
    name: str
    description: str
    content: str
    owner: str
    tags: list[str]
    status: PromptStatus
    risk_level: PromptRiskLevel
    policies: list[str]
    evaluation: PromptEvaluationSummary | None
    approval_notes: str | None
    created_at: datetime
    updated_at: datetime


class PromptEvaluationRequest(BaseModel):
    prompt_id: str
    version: str
    content: str
    evaluator: str = "automated"
    context_samples: list[str] = Field(default_factory=list)


class PromptEvaluationResponse(BaseModel):
    evaluation: PromptEvaluationSummary


class PromptAuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    prompt_id: str
    version: str
    action: str
    actor: str
    details: dict[str, Any]
    created_at: datetime


class PromptUsageLogCreate(BaseModel):
    prompt_id: str
    version: str
    session_id: str
    outcome: str
    toxicity_score: float | None = None
    hallucination_flags: list[str] = Field(default_factory=list)


class PromptUsageLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    prompt_id: str
    version: str
    session_id: str
    outcome: str
    toxicity_score: float | None
    hallucination_flags: list[str]
    created_at: datetime


class PromptWorkflowAction(BaseModel):
    reviewer: str
    notes: str | None = None
