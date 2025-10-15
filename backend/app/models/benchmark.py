"""Benchmark suite models for evaluation harness."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pymongo import IndexModel
from pydantic import Field

from .base_model import BaseDocument


class Benchmark(BaseDocument):
    """Benchmark suite for systematic model testing."""

    name: str = Field(..., description="벤치마크 이름", min_length=3)
    description: str = Field(..., description="설명")
    test_cases: list[dict[str, Any]] = Field(
        default_factory=list, description="테스트 케이스"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="생성 시간"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="업데이트 시간"
    )

    class Settings:
        name = "benchmarks"
        indexes = [
            IndexModel([("name", 1)], unique=True),
            IndexModel([("created_at", -1)]),
        ]


class BenchmarkRun(BaseDocument):
    """Benchmark execution record."""

    benchmark_name: str = Field(..., description="벤치마크 이름")
    model_id: str = Field(..., description="모델 ID")
    model_version: str | None = Field(None, description="모델 버전")
    results: dict[str, Any] = Field(default_factory=dict, description="실행 결과")
    passed: bool = Field(default=False, description="통과 여부")
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="시작 시간"
    )
    completed_at: datetime | None = Field(None, description="완료 시간")

    class Settings:
        name = "benchmark_runs"
        indexes = [
            IndexModel([("benchmark_name", 1), ("started_at", -1)]),
            IndexModel([("model_id", 1), ("model_version", 1)]),
        ]
