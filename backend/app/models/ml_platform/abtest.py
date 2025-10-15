"""A/B testing models for evaluation harness."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pymongo import IndexModel
from pydantic import Field

from app.models.base_model import BaseDocument


class ABTest(BaseDocument):
    """A/B test for comparing two model variants."""

    name: str = Field(..., description="A/B 테스트 이름", min_length=3)
    description: str = Field(..., description="설명")
    model_a_id: str = Field(..., description="모델 A ID")
    model_b_id: str = Field(..., description="모델 B ID")
    traffic_split_a: float = Field(default=50.0, description="모델 A 트래픽 비율 (%)")
    sample_size: int = Field(default=1000, description="샘플 크기")
    confidence_level: float = Field(default=0.95, description="신뢰 수준")
    status: str = Field(default="pending", description="상태 (pending/running/completed)")
    results: dict[str, Any] | None = Field(None, description="결과")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="생성 시간"
    )
    completed_at: datetime | None = Field(None, description="완료 시간")

    class Settings:
        name = "ab_tests"
        indexes = [
            IndexModel([("name", 1)], unique=True),
            IndexModel([("status", 1), ("created_at", -1)]),
        ]
