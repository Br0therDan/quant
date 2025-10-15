"""
Feature Store Service

Phase 4 D1: Feature Store Launch - ML 재사용을 위한 버전 관리 피처 레지스트리
"""

import logging
from datetime import UTC, datetime
from typing import Optional

from beanie import SortDirection
from beanie.operators import In

from app.models.ml_platform.feature_store import (
    FeatureDefinition,
    FeatureStatus,
    FeatureUsage,
    FeatureVersion,
)
from app.schemas.ml_platform.feature_store import (
    FeatureCreate,
    FeatureUpdate,
    FeatureUsageCreate,
    FeatureVersionCreate,
)

logger = logging.getLogger(__name__)


class FeatureStoreService:
    """
    Feature Store Service - ML 피처 관리 및 버전 제어

    책임:
    - 피처 정의 CRUD
    - 버전 관리 및 계보 추적
    - 사용 통계 수집
    - 피처 검증 및 품질 관리
    """

    def __init__(self):
        """Initialize Feature Store Service"""
        logger.info("FeatureStoreService initialized")

    # ==================== 피처 정의 관리 ====================

    async def create_feature(self, feature_data: FeatureCreate) -> FeatureDefinition:
        """
        새 피처 생성

        Args:
            feature_data: 피처 생성 데이터

        Returns:
            FeatureDefinition: 생성된 피처

        Raises:
            ValueError: 피처 이름 중복
        """
        # 중복 체크
        existing = await FeatureDefinition.find_one(
            FeatureDefinition.feature_name == feature_data.feature_name
        )
        if existing:
            raise ValueError(f"Feature '{feature_data.feature_name}' already exists")

        # 피처 생성
        feature = FeatureDefinition(
            feature_name=feature_data.feature_name,
            current_version="1.0.0",
            feature_type=feature_data.feature_type,
            data_type=feature_data.data_type,
            status=FeatureStatus.DRAFT,
            description=feature_data.description,
            owner=feature_data.owner,
            tags=feature_data.tags,
            upstream_features=feature_data.upstream_features,
            downstream_features=[],
            transformation=feature_data.transformation,
            validation_rules=feature_data.validation_rules,
            duckdb_table=feature_data.duckdb_table,
            duckdb_view=feature_data.duckdb_view,
            usage_count=0,
            last_used_at=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            deprecated_at=None,
        )

        await feature.insert()
        logger.info(f"Created feature: {feature.feature_name}")

        # 초기 버전 생성
        initial_version = FeatureVersion(
            feature_name=feature.feature_name,
            version="1.0.0",
            changelog="Initial version",
            breaking_changes=False,
            transformation_snapshot=feature.transformation,
            validation_snapshot=feature.validation_rules,
            created_by=feature.owner,
            created_at=datetime.now(UTC),
            is_rolled_back=False,
            rolled_back_at=None,
        )
        await initial_version.insert()

        return feature

    async def get_feature(self, feature_name: str) -> Optional[FeatureDefinition]:
        """피처 조회"""
        return await FeatureDefinition.find_one(
            FeatureDefinition.feature_name == feature_name
        )

    async def list_features(
        self,
        feature_type: Optional[str] = None,
        status: Optional[FeatureStatus] = None,
        owner: Optional[str] = None,
        tags: Optional[list[str]] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[FeatureDefinition], int]:
        """
        피처 목록 조회 (필터링 및 페이지네이션)

        Returns:
            tuple: (피처 목록, 전체 개수)
        """
        # 쿼리 빌드
        query_filters = []

        if feature_type:
            query_filters.append(FeatureDefinition.feature_type == feature_type)
        if status:
            query_filters.append(FeatureDefinition.status == status)
        if owner:
            query_filters.append(FeatureDefinition.owner == owner)
        if tags:
            query_filters.append(In(FeatureDefinition.tags, tags))

        # 쿼리 실행
        if query_filters:
            query = FeatureDefinition.find(*query_filters)
        else:
            query = FeatureDefinition.find_all()

        # 전체 개수
        total = await query.count()

        # 페이지네이션
        features = await query.skip(skip).limit(limit).to_list()

        return features, total

    async def update_feature(
        self, feature_name: str, update_data: FeatureUpdate
    ) -> Optional[FeatureDefinition]:
        """피처 업데이트"""
        feature = await self.get_feature(feature_name)
        if not feature:
            return None

        # 업데이트 적용
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(feature, key, value)

        feature.updated_at = datetime.now(UTC)
        await feature.save()

        logger.info(f"Updated feature: {feature_name}")
        return feature

    async def delete_feature(self, feature_name: str) -> bool:
        """피처 삭제 (소프트 삭제 - 상태를 ARCHIVED로 변경)"""
        feature = await self.get_feature(feature_name)
        if not feature:
            return False

        feature.status = FeatureStatus.ARCHIVED
        feature.updated_at = datetime.now(UTC)
        await feature.save()

        logger.info(f"Archived feature: {feature_name}")
        return True

    async def activate_feature(self, feature_name: str) -> Optional[FeatureDefinition]:
        """피처 활성화 (DRAFT/DEPRECATED → ACTIVE)"""
        feature = await self.get_feature(feature_name)
        if not feature:
            return None

        feature.status = FeatureStatus.ACTIVE
        feature.updated_at = datetime.now(UTC)
        await feature.save()

        logger.info(f"Activated feature: {feature_name}")
        return feature

    async def deprecate_feature(self, feature_name: str) -> Optional[FeatureDefinition]:
        """피처 폐기 (ACTIVE → DEPRECATED)"""
        feature = await self.get_feature(feature_name)
        if not feature:
            return None

        feature.status = FeatureStatus.DEPRECATED
        feature.deprecated_at = datetime.now(UTC)
        feature.updated_at = datetime.now(UTC)
        await feature.save()

        logger.info(f"Deprecated feature: {feature_name}")
        return feature

    # ==================== 버전 관리 ====================

    async def create_version(
        self, feature_name: str, version_data: FeatureVersionCreate
    ) -> Optional[FeatureVersion]:
        """새 피처 버전 생성"""
        feature = await self.get_feature(feature_name)
        if not feature:
            return None

        # 버전 중복 체크
        existing_version = await FeatureVersion.find_one(
            FeatureVersion.feature_name == feature_name,
            FeatureVersion.version == version_data.version,
        )
        if existing_version:
            raise ValueError(
                f"Version {version_data.version} already exists for {feature_name}"
            )

        # 버전 생성
        new_version = FeatureVersion(
            feature_name=feature_name,
            version=version_data.version,
            changelog=version_data.changelog,
            breaking_changes=version_data.breaking_changes,
            transformation_snapshot=version_data.transformation_snapshot,
            validation_snapshot=version_data.validation_snapshot,
            created_by=version_data.created_by,
            created_at=datetime.now(UTC),
            is_rolled_back=False,
            rolled_back_at=None,
        )
        await new_version.insert()

        # 피처의 current_version 업데이트
        feature.current_version = version_data.version
        feature.updated_at = datetime.now(UTC)
        await feature.save()

        logger.info(f"Created version {version_data.version} for {feature_name}")
        return new_version

    async def get_feature_versions(self, feature_name: str) -> list[FeatureVersion]:
        """피처의 모든 버전 조회 (최신순)"""
        return (
            await FeatureVersion.find(FeatureVersion.feature_name == feature_name)
            .sort(("created_at", SortDirection.DESCENDING))
            .to_list()
        )

    async def get_version(
        self, feature_name: str, version: str
    ) -> Optional[FeatureVersion]:
        """특정 버전 조회"""
        return await FeatureVersion.find_one(
            FeatureVersion.feature_name == feature_name,
            FeatureVersion.version == version,
        )

    async def rollback_version(
        self, feature_name: str, target_version: str
    ) -> Optional[FeatureDefinition]:
        """
        특정 버전으로 롤백

        Args:
            feature_name: 피처 이름
            target_version: 롤백할 버전

        Returns:
            업데이트된 피처
        """
        feature = await self.get_feature(feature_name)
        if not feature:
            return None

        # 타겟 버전 조회
        version = await self.get_version(feature_name, target_version)
        if not version:
            return None

        # 현재 버전 롤백 표시
        current_version_obj = await self.get_version(
            feature_name, feature.current_version
        )
        if current_version_obj:
            current_version_obj.is_rolled_back = True
            current_version_obj.rolled_back_at = datetime.now(UTC)
            await current_version_obj.save()

        # 피처 업데이트
        feature.current_version = target_version
        if version.transformation_snapshot:
            feature.transformation = version.transformation_snapshot
        if version.validation_snapshot:
            feature.validation_rules = version.validation_snapshot
        feature.updated_at = datetime.now(UTC)
        await feature.save()

        logger.info(f"Rolled back {feature_name} to version {target_version}")
        return feature

    # ==================== 계보 추적 ====================

    async def get_feature_lineage(
        self, feature_name: str, recursive: bool = False
    ) -> dict:
        """
        피처 계보 조회

        Args:
            feature_name: 피처 이름
            recursive: 재귀적 조회 (전체 의존성 트리)

        Returns:
            계보 정보
        """
        feature = await self.get_feature(feature_name)
        if not feature:
            return {}

        lineage = {
            "feature_name": feature_name,
            "current_version": feature.current_version,
            "upstream_features": feature.upstream_features,
            "downstream_features": feature.downstream_features,
        }

        if recursive:
            # 재귀적으로 전체 상위/하위 의존성 수집
            all_upstream = set()
            all_downstream = set()

            async def collect_upstream(name: str):
                f = await self.get_feature(name)
                if f:
                    for upstream_name in f.upstream_features:
                        if upstream_name not in all_upstream:
                            all_upstream.add(upstream_name)
                            await collect_upstream(upstream_name)

            async def collect_downstream(name: str):
                f = await self.get_feature(name)
                if f:
                    for downstream_name in f.downstream_features:
                        if downstream_name not in all_downstream:
                            all_downstream.add(downstream_name)
                            await collect_downstream(downstream_name)

            await collect_upstream(feature_name)
            await collect_downstream(feature_name)

            lineage["all_upstream"] = list(all_upstream)
            lineage["all_downstream"] = list(all_downstream)
            lineage["direct_dependents_count"] = len(feature.downstream_features)
            lineage["total_dependents_count"] = len(all_downstream)

        return lineage

    # ==================== 사용 통계 ====================

    async def record_feature_usage(
        self, usage_data: FeatureUsageCreate
    ) -> FeatureUsage:
        """피처 사용 기록"""
        usage = FeatureUsage(
            feature_name=usage_data.feature_name,
            feature_version=usage_data.feature_version,
            used_by_model=usage_data.used_by_model,
            model_version=usage_data.model_version,
            environment=usage_data.environment,
            feature_importance=usage_data.feature_importance,
            correlation_with_target=usage_data.correlation_with_target,
            execution_id=usage_data.execution_id,
            execution_duration_ms=usage_data.execution_duration_ms,
            usage_timestamp=datetime.now(UTC),
        )
        await usage.insert()

        # 피처 사용 횟수 증가
        feature = await self.get_feature(usage_data.feature_name)
        if feature:
            feature.usage_count += 1
            feature.last_used_at = datetime.now(UTC)
            await feature.save()

        logger.info(f"Recorded usage for feature: {usage_data.feature_name}")
        return usage

    async def get_feature_usage_history(
        self, feature_name: str, limit: int = 100
    ) -> list[FeatureUsage]:
        """피처 사용 히스토리 조회 (최신순)"""
        return (
            await FeatureUsage.find(FeatureUsage.feature_name == feature_name)
            .sort(("usage_timestamp", SortDirection.DESCENDING))
            .limit(limit)
            .to_list()
        )

    async def get_feature_statistics(self, feature_name: str) -> dict:
        """피처 통계 조회"""
        feature = await self.get_feature(feature_name)
        if not feature:
            return {}

        # 사용 기록 집계
        usages = await FeatureUsage.find(
            FeatureUsage.feature_name == feature_name
        ).to_list()

        if not usages:
            return {
                "feature_name": feature_name,
                "total_usage_count": 0,
                "unique_models_count": 0,
                "environments": {},
            }

        # 통계 계산
        unique_models = set()
        env_counts: dict[str, int] = {}
        importances = []
        correlations = []

        for usage in usages:
            unique_models.add(usage.used_by_model)
            env_counts[usage.environment] = env_counts.get(usage.environment, 0) + 1
            if usage.feature_importance is not None:
                importances.append(usage.feature_importance)
            if usage.correlation_with_target is not None:
                correlations.append(usage.correlation_with_target)

        return {
            "feature_name": feature_name,
            "total_usage_count": len(usages),
            "unique_models_count": len(unique_models),
            "environments": env_counts,
            "avg_feature_importance": (
                sum(importances) / len(importances) if importances else None
            ),
            "avg_correlation": (
                sum(correlations) / len(correlations) if correlations else None
            ),
            "first_used_at": min(u.usage_timestamp for u in usages) if usages else None,
            "last_used_at": max(u.usage_timestamp for u in usages) if usages else None,
        }

    # ==================== 데이터셋 관리 ====================

    async def list_datasets(self) -> list:
        """
        데이터셋 목록 조회 (MongoDB 기반)

        Returns:
            List of Dataset documents
        """
        from app.models.ml_platform.feature_store import Dataset

        datasets = (
            await Dataset.find_all()
            .sort(("created_at", SortDirection.DESCENDING))
            .to_list()
        )
        logger.info(f"Retrieved {len(datasets)} datasets")
        return datasets

    async def get_dataset(self, dataset_id: str):
        """
        데이터셋 상세 조회

        Args:
            dataset_id: Dataset ID

        Returns:
            Dataset document or None
        """
        from app.models.ml_platform.feature_store import Dataset
        from bson import ObjectId

        try:
            dataset = await Dataset.get(ObjectId(dataset_id))
            if dataset:
                logger.info(f"Retrieved dataset: {dataset.name}")
                # 마지막 접근 시간 업데이트
                dataset.last_accessed_at = datetime.now(UTC)
                await dataset.save()
            return dataset
        except Exception as e:
            logger.error(f"Error retrieving dataset {dataset_id}: {e}")
            return None
