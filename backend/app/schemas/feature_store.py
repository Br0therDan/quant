"""
Feature Store Schemas (Pydantic)

Phase 4 D1: Feature Store Launch
"""

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.feature_store import (
    FeatureType,
    FeatureStatus,
    DataType,
    FeatureLineageNode,
    FeatureTransformation,
    FeatureValidation,
)


# Request Schemas
class FeatureCreate(BaseModel):
    """피처 생성 요청"""

    feature_name: str = Field(..., min_length=3, max_length=100, description="피처 이름")
    feature_type: FeatureType = Field(..., description="피처 타입")
    data_type: DataType = Field(..., description="데이터 타입")
    description: str = Field(..., min_length=10, max_length=1000, description="설명")
    owner: str = Field(..., description="담당자 ID")
    tags: list[str] = Field(default_factory=list, description="태그")

    # 선택적 필드
    transformation: FeatureTransformation | None = Field(None, description="변환 로직")
    validation_rules: list[FeatureValidation] = Field(
        default_factory=list, description="검증 규칙"
    )
    upstream_features: list[str] = Field(
        default_factory=list, description="상위 의존 피처 이름 목록"
    )
    duckdb_table: str | None = Field(None, description="DuckDB 테이블")
    duckdb_view: str | None = Field(None, description="DuckDB 뷰")


class FeatureUpdate(BaseModel):
    """피처 업데이트 요청"""

    description: str | None = Field(None, min_length=10, description="설명")
    tags: list[str] | None = Field(None, description="태그")
    status: FeatureStatus | None = Field(None, description="상태")
    transformation: FeatureTransformation | None = Field(None, description="변환 로직")
    validation_rules: list[FeatureValidation] | None = Field(None, description="검증 규칙")
    duckdb_table: str | None = Field(None, description="DuckDB 테이블")
    duckdb_view: str | None = Field(None, description="DuckDB 뷰")


class FeatureVersionCreate(BaseModel):
    """피처 버전 생성 요청"""

    version: str = Field(..., description="버전 (Semantic Versioning)")
    changelog: str = Field(..., min_length=10, description="변경 사항")
    breaking_changes: bool = Field(default=False, description="호환성 깨짐 여부")
    created_by: str = Field(..., description="생성자 ID")

    # 스냅샷
    transformation_snapshot: FeatureTransformation | None = Field(
        None, description="변환 로직 스냅샷"
    )
    validation_snapshot: list[FeatureValidation] = Field(
        default_factory=list, description="검증 규칙 스냅샷"
    )


class FeatureUsageCreate(BaseModel):
    """피처 사용 기록 생성"""

    feature_name: str = Field(..., description="피처 이름")
    feature_version: str = Field(..., description="피처 버전")
    used_by_model: str = Field(..., description="모델 이름")
    model_version: str = Field(..., description="모델 버전")
    environment: str = Field(..., description="환경")

    # 선택적 메트릭
    feature_importance: float | None = Field(None, description="피처 중요도")
    correlation_with_target: float | None = Field(None, description="타겟 상관계수")
    execution_id: str | None = Field(None, description="실행 ID")
    execution_duration_ms: int | None = Field(None, description="실행 시간")


# Response Schemas
class FeatureResponse(BaseModel):
    """피처 조회 응답"""

    id: str = Field(..., description="MongoDB ObjectId")
    feature_name: str = Field(..., description="피처 이름")
    current_version: str = Field(..., description="현재 버전")
    feature_type: FeatureType = Field(..., description="피처 타입")
    data_type: DataType = Field(..., description="데이터 타입")
    status: FeatureStatus = Field(..., description="상태")
    description: str = Field(..., description="설명")
    owner: str = Field(..., description="담당자")
    tags: list[str] = Field(..., description="태그")

    # 계보
    upstream_features: list[str] = Field(..., description="상위 의존 피처")
    downstream_features: list[str] = Field(..., description="하위 파생 피처")

    # 변환 및 검증
    transformation: FeatureTransformation | None = Field(None, description="변환 로직")
    validation_rules: list[FeatureValidation] = Field(..., description="검증 규칙")

    # 스토리지
    duckdb_table: str | None = Field(None, description="DuckDB 테이블")
    duckdb_view: str | None = Field(None, description="DuckDB 뷰")

    # 통계
    usage_count: int = Field(..., description="사용 횟수")
    last_used_at: datetime | None = Field(None, description="마지막 사용 시간")

    # 시간 정보
    created_at: datetime = Field(..., description="생성 시간")
    updated_at: datetime = Field(..., description="업데이트 시간")
    deprecated_at: datetime | None = Field(None, description="폐기 시간")


class FeatureListResponse(BaseModel):
    """피처 목록 응답"""

    features: list[FeatureResponse] = Field(..., description="피처 목록")
    total: int = Field(..., description="전체 개수")


class FeatureVersionResponse(BaseModel):
    """피처 버전 응답"""

    id: str = Field(..., description="MongoDB ObjectId")
    feature_name: str = Field(..., description="피처 이름")
    version: str = Field(..., description="버전")
    changelog: str = Field(..., description="변경 사항")
    breaking_changes: bool = Field(..., description="호환성 깨짐 여부")

    # 스냅샷
    transformation_snapshot: FeatureTransformation | None = Field(
        None, description="변환 로직 스냅샷"
    )
    validation_snapshot: list[FeatureValidation] = Field(..., description="검증 규칙 스냅샷")

    # 메타데이터
    created_by: str = Field(..., description="생성자")
    created_at: datetime = Field(..., description="생성 시간")
    is_rolled_back: bool = Field(..., description="롤백 여부")
    rolled_back_at: datetime | None = Field(None, description="롤백 시간")


class FeatureVersionListResponse(BaseModel):
    """피처 버전 목록 응답"""

    versions: list[FeatureVersionResponse] = Field(..., description="버전 목록")
    total: int = Field(..., description="전체 개수")


class FeatureUsageResponse(BaseModel):
    """피처 사용 기록 응답"""

    id: str = Field(..., description="MongoDB ObjectId")
    feature_name: str = Field(..., description="피처 이름")
    feature_version: str = Field(..., description="피처 버전")
    used_by_model: str = Field(..., description="모델 이름")
    model_version: str = Field(..., description="모델 버전")
    environment: str = Field(..., description="환경")

    # 메트릭
    feature_importance: float | None = Field(None, description="피처 중요도")
    correlation_with_target: float | None = Field(None, description="타겟 상관계수")

    # 실행 정보
    execution_id: str | None = Field(None, description="실행 ID")
    execution_duration_ms: int | None = Field(None, description="실행 시간")
    usage_timestamp: datetime = Field(..., description="사용 시간")


class FeatureUsageListResponse(BaseModel):
    """피처 사용 기록 목록 응답"""

    usages: list[FeatureUsageResponse] = Field(..., description="사용 기록 목록")
    total: int = Field(..., description="전체 개수")


class FeatureLineageResponse(BaseModel):
    """피처 계보 응답"""

    feature_name: str = Field(..., description="피처 이름")
    current_version: str = Field(..., description="현재 버전")

    # 계보 그래프
    upstream_features: list[FeatureLineageNode] = Field(
        ..., description="상위 의존 피처 (이 피처가 사용하는 피처들)"
    )
    downstream_features: list[FeatureLineageNode] = Field(
        ..., description="하위 파생 피처 (이 피처를 사용하는 피처들)"
    )

    # 전체 계보 (재귀적으로 계산)
    all_upstream: list[str] = Field(..., description="전체 상위 의존성")
    all_downstream: list[str] = Field(..., description="전체 하위 의존성")

    # 사용 통계
    direct_dependents_count: int = Field(..., description="직접 의존하는 피처 수")
    total_dependents_count: int = Field(..., description="전체 의존하는 피처 수")


class FeatureStatisticsResponse(BaseModel):
    """피처 통계 응답"""

    feature_name: str = Field(..., description="피처 이름")
    total_usage_count: int = Field(..., description="총 사용 횟수")
    unique_models_count: int = Field(..., description="사용한 고유 모델 수")
    environments: dict[str, int] = Field(..., description="환경별 사용 횟수")

    # 성능 메트릭 (평균)
    avg_feature_importance: float | None = Field(None, description="평균 피처 중요도")
    avg_correlation: float | None = Field(None, description="평균 타겟 상관계수")

    # 시간 정보
    first_used_at: datetime | None = Field(None, description="최초 사용 시간")
    last_used_at: datetime | None = Field(None, description="마지막 사용 시간")


class FeatureValidationResult(BaseModel):
    """피처 검증 결과"""

    feature_name: str = Field(..., description="피처 이름")
    is_valid: bool = Field(..., description="검증 성공 여부")
    validation_errors: list[str] = Field(default_factory=list, description="검증 오류")
    warnings: list[str] = Field(default_factory=list, description="경고")

    # 검증 세부 사항
    schema_valid: bool = Field(..., description="스키마 유효성")
    lineage_valid: bool = Field(..., description="계보 유효성")
    transformation_valid: bool = Field(..., description="변환 로직 유효성")
    storage_valid: bool = Field(..., description="스토리지 접근 가능성")
