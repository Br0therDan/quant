"""
Base models for Market Data
모든 마켓 데이터 모델의 기본 클래스들
"""

from datetime import datetime, UTC, timezone
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
            self.updated_at = datetime.now(UTC)

        # data_quality_score가 없으면 자동 계산 (DataQualityMixin이 있는 경우)
        if self.data_quality_score is None and hasattr(self, "calculate_quality_score"):
            try:
                self.data_quality_score = self.calculate_quality_score()
            except Exception:
                # 계산 실패 시 기본값 유지 (None)
                pass


class DataQualityMixin:
    """데이터 품질 관련 메서드를 제공하는 Mixin"""

    def calculate_quality_score(self) -> float:
        """데이터 품질 점수 계산 (0-100)

        기본 구현: 필수 필드의 존재 여부를 기반으로 점수 계산
        각 모델별로 오버라이드하여 특화된 품질 검증 로직 구현 가능
        """
        total_fields = 0
        valid_fields = 0

        # 모델의 모든 필드 검사 (Pydantic v2)
        if hasattr(self, "model_fields"):
            model_fields = getattr(self, "model_fields", {})
            for field_name in model_fields:
                total_fields += 1
                value = getattr(self, field_name, None)

                # None이 아니고 빈 문자열이 아닌 경우 유효한 데이터로 간주
                if value is not None and value != "":
                    valid_fields += 1

        # 기본 점수 (필드가 없을 경우 100점)
        if total_fields == 0:
            return 100.0

        return (valid_fields / total_fields) * 100.0

    def is_valid_data(self) -> bool:
        """데이터 유효성 검증

        기본 구현: 품질 점수가 50점 이상이면 유효한 데이터로 간주
        각 모델별로 오버라이드하여 특화된 검증 로직 구현 가능
        """
        return self.calculate_quality_score() >= 50.0

    def get_anomalies(self) -> list:
        """데이터 이상치 탐지

        기본 구현: 기본적인 이상치 패턴 검사
        각 모델별로 오버라이드하여 특화된 이상치 탐지 로직 구현 가능
        """
        anomalies = []

        # 숫자 필드에서 극값 검사 (Pydantic v2)
        if hasattr(self, "model_fields"):
            model_fields = getattr(self, "model_fields", {})
            for field_name in model_fields:
                value = getattr(self, field_name, None)

                # 숫자 타입 필드에서 음수 가격이나 거래량 검사
                if isinstance(value, (int, float)) and value is not None:
                    if "price" in field_name.lower() and value < 0:
                        anomalies.append(
                            f"Negative price detected: {field_name}={value}"
                        )
                    elif "volume" in field_name.lower() and value < 0:
                        anomalies.append(
                            f"Negative volume detected: {field_name}={value}"
                        )
                    elif value == float("inf") or value == float("-inf"):
                        anomalies.append(
                            f"Infinite value detected: {field_name}={value}"
                        )

        return anomalies


class DataQualityScore(BaseModel):
    """데이터 품질 점수 모델"""

    overall_score: float = Field(..., ge=0, le=100, description="전체 품질 점수")
    completeness_score: float = Field(..., ge=0, le=100, description="완성도 점수")
    accuracy_score: float = Field(..., ge=0, le=100, description="정확도 점수")
    consistency_score: float = Field(..., ge=0, le=100, description="일관성 점수")
    timeliness_score: float = Field(..., ge=0, le=100, description="적시성 점수")
    issues: List[str] = Field(default_factory=list, description="발견된 문제점들")
