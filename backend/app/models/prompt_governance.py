"""Prompt governance models (Phase 4 D4)."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field
from pymongo import IndexModel

from .base_model import BaseDocument


class PromptStatus(str, Enum):
    """Lifecycle status for prompts."""

    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class PromptRiskLevel(str, Enum):
    """Risk tier for prompts."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PromptEvaluationSummary(BaseModel):
    """Summary of automated evaluation results."""

    toxicity_score: float = Field(..., description="독성 점수 0-1")
    hallucination_score: float = Field(..., description="환각 가능성 점수 0-1")
    factual_consistency: float = Field(..., description="사실 일치 점수 0-1")
    risk_level: PromptRiskLevel = Field(..., description="위험도")
    evaluator: str = Field(..., description="평가자 또는 시스템")
    evaluated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="평가 시각"
    )


class PromptTemplate(BaseDocument):
    """Prompt template with versioning and workflow state."""

    prompt_id: str = Field(..., description="프롬프트 식별자")
    version: str = Field(..., description="버전")
    name: str = Field(..., description="프롬프트 이름")
    description: str = Field(..., description="설명")
    content: str = Field(..., description="프롬프트 내용")
    owner: str = Field(..., description="담당자")
    tags: list[str] = Field(default_factory=list, description="태그")
    status: PromptStatus = Field(default=PromptStatus.DRAFT, description="상태")
    risk_level: PromptRiskLevel = Field(
        default=PromptRiskLevel.MEDIUM, description="위험도"
    )
    policies: list[str] = Field(
        default_factory=list, description="적용 정책 ID 또는 설명"
    )
    evaluation: PromptEvaluationSummary | None = Field(
        None, description="평가 요약"
    )
    approval_notes: str | None = Field(None, description="검토 메모")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="생성 시간"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="업데이트 시간"
    )

    class Settings:
        name = "prompt_templates"
        indexes = [
            IndexModel([("prompt_id", 1), ("version", 1)], unique=True),
            IndexModel([("status", 1)]),
            IndexModel([("tags", 1)]),
        ]


class PromptAuditLog(BaseDocument):
    """Audit log for prompt actions."""

    prompt_id: str = Field(..., description="프롬프트 ID")
    version: str = Field(..., description="버전")
    action: str = Field(..., description="실행된 액션")
    actor: str = Field(..., description="행위자")
    details: dict[str, Any] = Field(default_factory=dict, description="추가 정보")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="생성 시간"
    )

    class Settings:
        name = "prompt_audit_logs"
        indexes = [
            IndexModel([("prompt_id", 1), ("version", 1), ("created_at", -1)]),
        ]


class PromptUsageLog(BaseDocument):
    """Operational usage tracking for prompts."""

    prompt_id: str = Field(..., description="프롬프트 ID")
    version: str = Field(..., description="버전")
    session_id: str = Field(..., description="세션 ID")
    outcome: str = Field(..., description="결과")
    toxicity_score: float | None = Field(None, description="실행 중 감지된 독성")
    hallucination_flags: list[str] = Field(
        default_factory=list, description="환각 플래그"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="생성 시간"
    )

    class Settings:
        name = "prompt_usage_logs"
        indexes = [
            IndexModel([("prompt_id", 1), ("version", 1), ("created_at", -1)]),
            IndexModel([("session_id", 1)]),
        ]
