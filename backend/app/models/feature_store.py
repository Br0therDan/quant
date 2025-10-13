"""
Feature Store Models using Beanie (MongoDB ODM)

Phase 4 D1: Feature Store Launch
"""

from datetime import datetime, UTC
from enum import Enum
from typing import Any

from beanie import Document
from pydantic import BaseModel, Field
from pymongo import IndexModel


class FeatureType(str, Enum):
    """피처 타입"""

    TECHNICAL_INDICATOR = "technical_indicator"
    FUNDAMENTAL = "fundamental"
    SENTIMENT = "sentiment"
    MACRO_ECONOMIC = "macro_economic"
    DERIVED = "derived"
    RAW = "raw"


class FeatureStatus(str, Enum):
    """피처 상태"""

    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"
    DRAFT = "draft"


class DataType(str, Enum):
    """데이터 타입"""

    FLOAT = "float"
    INTEGER = "integer"
    STRING = "string"
    BOOLEAN = "boolean"
    TIMESTAMP = "timestamp"


# Embedded Models (내장 모델)
class FeatureLineageNode(BaseModel):
    """피처 계보 노드 (upstream/downstream)"""

    feature_name: str = Field(..., description="피처 이름")
    version: str = Field(..., description="피처 버전")
    relationship: str = Field(..., description="관계 (depends_on, derived_from, used_by)")


class FeatureTransformation(BaseModel):
    """피처 변환 로직"""

    transformation_type: str = Field(..., description="변환 타입 (sql, python, spark)")
    code: str = Field(..., description="변환 코드")
    parameters: dict[str, Any] = Field(default_factory=dict, description="파라미터")


class FeatureValidation(BaseModel):
    """피처 검증 규칙"""

    rule_type: str = Field(..., description="규칙 타입 (range, null_check, outlier)")
    parameters: dict[str, Any] = Field(..., description="규칙 파라미터")
    is_blocking: bool = Field(default=False, description="블로킹 여부")


class FeatureUsageRecord(BaseModel):
    """피처 사용 기록"""

    model_name: str = Field(..., description="모델 이름")
    model_version: str = Field(..., description="모델 버전")
    usage_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="사용 시간"
    )
    environment: str = Field(..., description="환경 (dev, staging, production)")


# Document Models (MongoDB 컬렉션)
class FeatureDefinition(Document):
    """피처 정의 문서 (Feature Registry 메인 모델)"""

    # 기본 정보
    feature_name: str = Field(..., description="피처 고유 이름")
    current_version: str = Field(default="1.0.0", description="현재 버전 (Semantic)")
    feature_type: FeatureType = Field(..., description="피처 타입")
    data_type: DataType = Field(..., description="데이터 타입")
    status: FeatureStatus = Field(default=FeatureStatus.DRAFT, description="상태")

    # 메타데이터
    description: str = Field(..., min_length=10, description="피처 설명")
    owner: str = Field(..., description="담당자 (사용자 ID)")
    tags: list[str] = Field(default_factory=list, description="태그")

    # 계보 (Lineage) - 간단한 문자열 리스트로 변경
    upstream_features: list[str] = Field(
        default_factory=list, description="상위 의존 피처 이름 목록"
    )
    downstream_features: list[str] = Field(
        default_factory=list, description="하위 파생 피처 이름 목록"
    )

    # 변환 로직
    transformation: FeatureTransformation | None = Field(
        None, description="변환 로직 (SQL, Python 등)"
    )

    # 검증 규칙
    validation_rules: list[FeatureValidation] = Field(
        default_factory=list, description="검증 규칙"
    )

    # 스토리지 정보
    duckdb_table: str | None = Field(None, description="DuckDB 테이블 이름")
    duckdb_view: str | None = Field(None, description="DuckDB 뷰 이름")

    # 통계
    usage_count: int = Field(default=0, description="사용 횟수")
    last_used_at: datetime | None = Field(None, description="마지막 사용 시간")

    # 시간 정보
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="생성 시간"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="업데이트 시간"
    )
    deprecated_at: datetime | None = Field(None, description="폐기 시간")

    class Settings:
        name = "feature_definitions"
        indexes = [
            IndexModel([("feature_name", 1)], unique=True),  # 고유 이름
            IndexModel([("owner", 1)]),
            IndexModel([("feature_type", 1)]),
            IndexModel([("status", 1)]),
            IndexModel([("tags", 1)]),
            IndexModel([("created_at", -1)]),
            IndexModel([("feature_name", 1), ("current_version", 1)]),  # 복합 인덱스
        ]


class FeatureVersion(Document):
    """피처 버전 히스토리"""

    feature_name: str = Field(..., description="피처 이름")
    version: str = Field(..., description="버전 (Semantic)")

    # 변경 사항
    changelog: str = Field(..., min_length=10, description="변경 사항 설명")
    breaking_changes: bool = Field(default=False, description="호환성 깨짐 여부")

    # 스냅샷 (버전 생성 시점의 피처 정의)
    transformation_snapshot: FeatureTransformation | None = Field(
        None, description="변환 로직 스냅샷"
    )
    validation_snapshot: list[FeatureValidation] = Field(
        default_factory=list, description="검증 규칙 스냅샷"
    )

    # 메타데이터
    created_by: str = Field(..., description="생성자")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="생성 시간"
    )

    # 롤백 정보
    is_rolled_back: bool = Field(default=False, description="롤백 여부")
    rolled_back_at: datetime | None = Field(None, description="롤백 시간")

    class Settings:
        name = "feature_versions"
        indexes = [
            IndexModel([("feature_name", 1), ("version", 1)], unique=True),
            IndexModel([("feature_name", 1), ("created_at", -1)]),
            IndexModel([("created_at", -1)]),
        ]


class FeatureUsage(Document):
    """피처 사용 추적"""

    feature_name: str = Field(..., description="피처 이름")
    feature_version: str = Field(..., description="사용된 피처 버전")

    # 사용 컨텍스트
    used_by_model: str = Field(..., description="모델 이름")
    model_version: str = Field(..., description="모델 버전")
    environment: str = Field(..., description="환경 (dev, staging, production)")

    # 성능 메트릭 (옵션)
    feature_importance: float | None = Field(None, description="피처 중요도")
    correlation_with_target: float | None = Field(None, description="타겟 상관계수")

    # 시간 정보
    usage_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="사용 시간"
    )

    # 실행 정보
    execution_id: str | None = Field(None, description="실행 ID (백테스트/학습)")
    execution_duration_ms: int | None = Field(None, description="실행 시간 (밀리초)")

    class Settings:
        name = "feature_usages"
        indexes = [
            IndexModel([("feature_name", 1)]),
            IndexModel([("used_by_model", 1)]),
            IndexModel([("environment", 1)]),
            IndexModel([("usage_timestamp", -1)]),
            IndexModel([("feature_name", 1), ("usage_timestamp", -1)]),  # 복합 인덱스
        ]
