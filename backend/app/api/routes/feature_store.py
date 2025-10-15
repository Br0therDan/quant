"""
Feature Store API Routes

Phase 4 D1: Feature Store Launch - ML 재사용을 위한 버전 관리 피처 레지스트리
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.models.feature_store import FeatureStatus, FeatureType
from app.schemas.feature_store import (
    FeatureCreate,
    FeatureLineageResponse,
    FeatureListResponse,
    FeatureResponse,
    FeatureStatisticsResponse,
    FeatureUpdate,
    FeatureUsageCreate,
    FeatureUsageResponse,
    FeatureVersionCreate,
    FeatureVersionListResponse,
    FeatureVersionResponse,
)
from app.services.service_factory import service_factory

router = APIRouter()
logger = logging.getLogger(__name__)


def to_feature_response(feature) -> FeatureResponse:
    """Beanie Document를 FeatureResponse로 변환"""
    data = feature.model_dump()
    data["id"] = str(feature.id)
    return FeatureResponse(**data)


def to_version_response(version) -> FeatureVersionResponse:
    """Beanie Document를 FeatureVersionResponse로 변환"""
    data = version.model_dump()
    data["id"] = str(version.id)
    return FeatureVersionResponse(**data)


def to_usage_response(usage) -> FeatureUsageResponse:
    """Beanie Document를 FeatureUsageResponse로 변환"""
    data = usage.model_dump()
    data["id"] = str(usage.id)
    return FeatureUsageResponse(**data)


# ============================================================
# 피처 정의 관리
# ============================================================


@router.post("", response_model=FeatureResponse, status_code=201)
async def create_feature(feature_data: FeatureCreate):
    """
    새 피처 생성

    - **feature_name**: 피처 고유 식별자 (중복 불가)
    - **feature_type**: RAW, DERIVED, AGGREGATED
    - **data_type**: numeric, categorical, text, datetime, boolean
    - **transformation**: 변환 로직 (SQL, Python 등)
    - **validation_rules**: 검증 규칙 (타입, 범위, 제약조건)
    - **upstream_features**: 의존하는 상위 피처 목록
    """
    service = service_factory.get_feature_store_service()
    try:
        feature = await service.create_feature(feature_data)
        return to_feature_response(feature)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("", response_model=FeatureListResponse)
async def list_features(
    owner: Optional[str] = None,
    feature_type: Optional[FeatureType] = None,
    status: Optional[FeatureStatus] = None,
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """
    피처 목록 조회 (필터링/페이지네이션)

    - **owner**: 소유자 필터
    - **feature_type**: 피처 타입 필터 (RAW, DERIVED, AGGREGATED)
    - **status**: 상태 필터 (DRAFT, ACTIVE, DEPRECATED)
    - **tags**: 태그 필터 (comma-separated: "financial,risk")
    - **skip/limit**: 페이지네이션
    """
    service = service_factory.get_feature_store_service()
    tag_list = [t.strip() for t in tags.split(",")] if tags else None
    features = await service.list_features(
        owner=owner,
        feature_type=feature_type,
        status=status,
        tags=tag_list,
        skip=skip,
        limit=limit,
    )
    return FeatureListResponse(
        features=[to_feature_response(f) for f in features],
        total=len(features),
    )


@router.get("/{feature_name}", response_model=FeatureResponse)
async def get_feature(feature_name: str):
    """피처 상세 조회"""
    service = service_factory.get_feature_store_service()
    feature = await service.get_feature(feature_name)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    return to_feature_response(feature)


@router.put("/{feature_name}", response_model=FeatureResponse)
async def update_feature(feature_name: str, update_data: FeatureUpdate):
    """
    피처 업데이트

    - 변환 로직이나 검증 규칙 변경 시 새 버전 생성 권장
    - 메타데이터(description, tags)만 업데이트 시 버전 증가 없음
    """
    service = service_factory.get_feature_store_service()
    feature = await service.update_feature(feature_name, update_data)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    return to_feature_response(feature)


@router.delete("/{feature_name}", status_code=204)
async def delete_feature(feature_name: str):
    """
    피처 삭제 (소프트 삭제)

    - 실제 데이터는 유지되며 상태만 DEPRECATED로 변경
    - 하위 피처(downstream_features)가 있으면 삭제 불가
    """
    service = service_factory.get_feature_store_service()
    success = await service.delete_feature(feature_name)
    if not success:
        raise HTTPException(
            status_code=404, detail="Feature not found or has downstream features"
        )


# ============================================================
# 피처 상태 관리
# ============================================================


@router.post("/{feature_name}/activate", response_model=FeatureResponse)
async def activate_feature(feature_name: str):
    """
    피처 활성화 (DRAFT → ACTIVE)

    - 검증 규칙을 통과해야 활성화 가능
    - 활성화 후 프로덕션 환경에서 사용 가능
    """
    service = service_factory.get_feature_store_service()
    feature = await service.activate_feature(feature_name)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    return to_feature_response(feature)


@router.post("/{feature_name}/deprecate", response_model=FeatureResponse)
async def deprecate_feature(feature_name: str):
    """
    피처 폐기 (ACTIVE → DEPRECATED)

    - 더 이상 사용하지 않는 피처 표시
    - 하위 피처(downstream_features)가 있으면 폐기 불가
    - 기존 사용처는 계속 작동하지만 신규 사용 불가
    """
    service = service_factory.get_feature_store_service()
    feature = await service.deprecate_feature(feature_name)
    if not feature:
        raise HTTPException(
            status_code=404, detail="Feature not found or has downstream features"
        )
    return to_feature_response(feature)


# ============================================================
# 버전 관리
# ============================================================


@router.post("/{feature_name}/versions", response_model=FeatureVersionResponse)
async def create_version(feature_name: str, version_data: FeatureVersionCreate):
    """
    새 버전 생성

    - 변환 로직이나 검증 규칙 변경 시 필수
    - Semantic Versioning 권장 (1.0.0 → 1.1.0 → 2.0.0)
    - breaking_changes=True면 Major 버전 증가 (1.x.x → 2.0.0)
    """
    service = service_factory.get_feature_store_service()
    try:
        version = await service.create_version(feature_name, version_data)
        return to_version_response(version)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/{feature_name}/versions", response_model=FeatureVersionListResponse)
async def get_feature_versions(feature_name: str):
    """피처의 모든 버전 조회 (최신순)"""
    service = service_factory.get_feature_store_service()
    versions = await service.get_feature_versions(feature_name)
    return FeatureVersionListResponse(
        versions=[to_version_response(v) for v in versions],
        total=len(versions),
    )


@router.post("/{feature_name}/rollback", response_model=FeatureVersionResponse)
async def rollback_version(
    feature_name: str, target_version: str = Query(..., description="롤백할 버전")
):
    """
    버전 롤백

    - 이전 버전으로 복원 (변환 로직, 검증 규칙 스냅샷 복원)
    - 현재 버전에 `is_rolled_back=True` 표시
    - 새 버전이 생성되며 current_version 업데이트
    """
    service = service_factory.get_feature_store_service()
    try:
        new_version = await service.rollback_version(feature_name, target_version)
        return to_version_response(new_version)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


# ============================================================
# 계보 추적 (Lineage)
# ============================================================


@router.get("/{feature_name}/lineage", response_model=FeatureLineageResponse)
async def get_feature_lineage(
    feature_name: str, recursive: bool = Query(True, description="재귀적 의존성 추적")
):
    """
    피처 계보 추적

    - upstream_features: 이 피처가 의존하는 상위 피처들
    - downstream_features: 이 피처를 사용하는 하위 피처들
    - recursive=True: 재귀적으로 전체 의존성 트리 추적
    """
    service = service_factory.get_feature_store_service()
    try:
        lineage = await service.get_feature_lineage(feature_name, recursive=recursive)
        return lineage
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


# ============================================================
# 사용 통계
# ============================================================


@router.post("/usage", response_model=FeatureUsageResponse, status_code=201)
async def record_feature_usage(usage_data: FeatureUsageCreate):
    """
    피처 사용 기록

    - 모델이 피처를 사용할 때마다 호출
    - feature_importance: 모델에서의 중요도 (0.0 ~ 1.0)
    - correlation_with_target: 타겟과의 상관관계 (-1.0 ~ 1.0)
    """
    service = service_factory.get_feature_store_service()
    usage = await service.record_feature_usage(usage_data)
    return to_usage_response(usage)


@router.get("/{feature_name}/statistics", response_model=FeatureStatisticsResponse)
async def get_feature_statistics(feature_name: str):
    """
    피처 사용 통계 조회

    - total_usage: 총 사용 횟수
    - unique_models: 사용한 고유 모델 수
    - environments: 사용 환경 분포 (dev, staging, production)
    - avg_importance: 평균 feature importance
    - avg_correlation: 평균 상관관계
    - last_used_at: 마지막 사용 시각
    """
    service = service_factory.get_feature_store_service()
    try:
        stats = await service.get_feature_statistics(feature_name)
        return stats
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


# ============================================================
# 데이터셋 관리
# ============================================================


@router.get("/datasets", response_model=dict)
async def list_datasets():
    """
    데이터셋 목록 조회

    MongoDB에 저장된 데이터셋 메타데이터 목록 반환
    """
    service = service_factory.get_feature_store_service()
    datasets = await service.list_datasets()

    # Beanie Document를 dict로 변환
    dataset_list = []
    for ds in datasets:
        data = ds.model_dump()
        data["id"] = str(ds.id)
        dataset_list.append(data)

    return {"datasets": dataset_list, "total": len(dataset_list)}


@router.get("/datasets/{dataset_id}", response_model=dict)
async def get_dataset(dataset_id: str):
    """
    데이터셋 상세 조회

    Args:
        dataset_id: Dataset ID (MongoDB ObjectId)

    Returns:
        Dataset 상세 정보 (마지막 접근 시간 자동 업데이트)
    """
    service = service_factory.get_feature_store_service()
    dataset = await service.get_dataset(dataset_id)

    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")

    data = dataset.model_dump()
    data["id"] = str(dataset.id)
    return data
