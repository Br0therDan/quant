"""
Base models for Market Data
모든 마켓 데이터 모델의 기본 클래스들
"""

from datetime import datetime, timezone
from typing import Optional, List
from beanie import Document
from pydantic import BaseModel, Field


class BaseMarketDataDocument(Document):
    """마켓 데이터 모델의 기본 클래스"""

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="생성 시간"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="수정 시간"
    )
    source: str = Field(default="alpha_vantage", description="데이터 소스")
    data_quality_score: Optional[float] = Field(None, description="데이터 품질 점수 (0-100)")

    class Settings:
        # 모든 하위 클래스에서 이 인덱스들이 적용됨
        indexes = ["created_at", "updated_at", "source"]

    def __init__(self, **data):
        super().__init__(**data)
        # 수정 시간 자동 업데이트
        if hasattr(self, "id") and self.id:
            self.updated_at = datetime.utcnow()


class DataQualityMixin:
    """데이터 품질 관련 메서드를 제공하는 Mixin"""

    def calculate_quality_score(self) -> float:
        """데이터 품질 점수 계산 (0-100)"""
        # TODO: 구현 예정 - 각 모델별로 오버라이드
        return 100.0

    def is_valid_data(self) -> bool:
        """데이터 유효성 검증"""
        # TODO: 구현 예정 - 각 모델별로 오버라이드
        return True

    def get_anomalies(self) -> list:
        """데이터 이상치 탐지"""
        # TODO: 구현 예정 - 각 모델별로 오버라이드
        return []


class DataQualityScore(BaseModel):
    """데이터 품질 점수 모델"""

    overall_score: float = Field(..., ge=0, le=100, description="전체 품질 점수")
    completeness_score: float = Field(..., ge=0, le=100, description="완성도 점수")
    accuracy_score: float = Field(..., ge=0, le=100, description="정확도 점수")
    consistency_score: float = Field(..., ge=0, le=100, description="일관성 점수")
    timeliness_score: float = Field(..., ge=0, le=100, description="적시성 점수")
    issues: List[str] = Field(default_factory=list, description="발견된 문제점들")
