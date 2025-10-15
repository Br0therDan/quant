"""Fairness audit models for evaluation harness."""

from __future__ import annotations

from datetime import UTC, datetime

from pymongo import IndexModel
from pydantic import Field

from .base_model import BaseDocument


class FairnessReport(BaseDocument):
    """Fairness audit report for model bias detection."""

    model_id: str = Field(..., description="모델 ID")
    protected_attributes: list[str] = Field(
        default_factory=list, description="보호 속성 (예: gender, race, age)"
    )
    group_metrics: dict[str, dict[str, float]] = Field(
        default_factory=dict, description="그룹별 메트릭"
    )
    overall_fairness_score: float = Field(default=0.0, description="전체 공정성 점수")
    passed: bool = Field(default=False, description="통과 여부")
    recommendations: list[str] = Field(default_factory=list, description="개선 권장 사항")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="생성 시간"
    )

    class Settings:
        name = "fairness_reports"
        indexes = [
            IndexModel([("model_id", 1), ("created_at", -1)]),
            IndexModel([("passed", 1)]),
        ]
