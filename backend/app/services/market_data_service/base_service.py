from abc import ABC, abstractmethod
from datetime import datetime, timedelta, UTC
from typing import Any, Dict, List, Optional, Type
from decimal import Decimal
import asyncio
import logging
from dataclasses import dataclass
from enum import Enum

from mysingle_quant import AlphaVantageClient
from app.services.database_manager import DatabaseManager
from app.models.market_data.base import BaseMarketDataDocument, DataQualityScore


logger = logging.getLogger(__name__)


@dataclass
class CacheResult:
    """캐시 조회 결과"""

    hit: bool
    data: Optional[Any]
    source: str  # "duckdb", "mongodb", "none"


class DataCoverage(Enum):
    """데이터 커버리지 레벨"""

    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class CacheStrategy:
    """캐싱 전략 설정 클래스"""

    def __init__(
        self,
        duckdb_ttl_hours: int = 24,
        mongodb_ttl_hours: int = 168,  # 1 week
        force_refresh_threshold_hours: int = 72,  # 3 days
        max_cache_miss_retries: int = 3,
    ):
        self.duckdb_ttl = timedelta(hours=duckdb_ttl_hours)
        self.mongodb_ttl = timedelta(hours=mongodb_ttl_hours)
        self.force_refresh_threshold = timedelta(hours=force_refresh_threshold_hours)
        self.max_retries = max_cache_miss_retries


class DataQualityValidator:
    """데이터 품질 검증 클래스"""

    @staticmethod
    def validate_price_data(data: Dict[str, Any]) -> DataQualityScore:
        """주가 데이터 품질 검증"""
        score = 100.0
        issues = []

        # 필수 필드 확인
        required_fields = ["open", "high", "low", "close", "volume"]
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            score -= len(missing_fields) * 20
            issues.extend([f"Missing field: {field}" for field in missing_fields])

        # 논리적 일관성 확인
        if all(data.get(field) for field in ["open", "high", "low", "close"]):
            high = Decimal(str(data["high"]))
            low = Decimal(str(data["low"]))
            open_price = Decimal(str(data["open"]))
            close = Decimal(str(data["close"]))

            if high < low:
                score -= 30
                issues.append("High < Low")

            if open_price > high or open_price < low:
                score -= 20
                issues.append("Open price out of High-Low range")

            if close > high or close < low:
                score -= 20
                issues.append("Close price out of High-Low range")

        # 볼륨 확인
        if data.get("volume"):
            try:
                volume = int(data["volume"])
                if volume < 0:
                    score -= 15
                    issues.append("Negative volume")
            except (ValueError, TypeError):
                score -= 10
                issues.append("Invalid volume format")

        return DataQualityScore(
            overall_score=max(0.0, score),
            completeness_score=max(0.0, 100 - len(missing_fields) * 20),
            accuracy_score=max(0.0, score),
            consistency_score=max(0.0, score),
            timeliness_score=100.0,  # 실시간 데이터로 간주
            issues=issues,
        )


class BaseMarketDataService(ABC):
    """시장 데이터 서비스 베이스 클래스"""

    def __init__(self, database_manager: Optional[DatabaseManager] = None):
        self._alpha_vantage_client: Optional[AlphaVantageClient] = None
        self._db_manager: Optional[DatabaseManager] = database_manager
        self.cache_strategy = CacheStrategy()
        self.quality_validator = DataQualityValidator()

    @property
    def alpha_vantage(self) -> AlphaVantageClient:
        """AlphaVantage 클라이언트 lazy loading"""
        if self._alpha_vantage_client is None:
            self._alpha_vantage_client = AlphaVantageClient()
        return self._alpha_vantage_client

    @property
    def db_manager(self) -> DatabaseManager:
        """데이터베이스 매니저 lazy loading"""
        if self._db_manager is None:
            self._db_manager = DatabaseManager()
        return self._db_manager

    async def get_cached_data(
        self,
        cache_key: str,
        model_class: Type[BaseMarketDataDocument],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Optional[List[BaseMarketDataDocument]]:
        """
        캐시된 데이터 조회 (DuckDB -> MongoDB 순서)

        Args:
            cache_key: 캐시 키
            model_class: 데이터 모델 클래스
            start_date: 시작 날짜 (선택사항)
            end_date: 종료 날짜 (선택사항)

        Returns:
            캐시된 데이터 리스트 또는 None
        """
        try:
            # 1. DuckDB 캐시 확인 (고속)
            duckdb_data = await self._get_from_duckdb_cache(
                cache_key, start_date, end_date
            )
            if duckdb_data:
                logger.info(f"Cache HIT (DuckDB): {cache_key}")
                return [model_class(**item) for item in duckdb_data]

            # 2. MongoDB 캐시 확인 (보조)
            mongodb_data = await self._get_from_mongodb_cache(
                model_class, cache_key, start_date, end_date
            )
            if mongodb_data:
                logger.info(f"Cache HIT (MongoDB): {cache_key}")
                # MongoDB 데이터를 DuckDB에 백업
                await self._store_to_duckdb_cache(cache_key, mongodb_data)
                return mongodb_data

            logger.info(f"Cache MISS: {cache_key}")
            return None

        except Exception as e:
            logger.error(f"Cache lookup error: {e}")
            return None

    async def store_data(
        self,
        cache_key: str,
        data: List[BaseMarketDataDocument],
        table_name: str = "market_data",
    ) -> bool:
        """
        데이터를 캐시에 저장 (DuckDB + MongoDB)

        Args:
            cache_key: 캐시 키
            data: 저장할 데이터
            table_name: DuckDB 테이블명

        Returns:
            저장 성공 여부
        """
        try:
            if not data:
                return True

            # 병렬 저장
            tasks = [
                self._store_to_duckdb_cache(cache_key, data, table_name),
                self._store_to_mongodb_cache(data),
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # 에러 확인
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    cache_type = "DuckDB" if i == 0 else "MongoDB"
                    logger.error(f"{cache_type} storage failed: {result}")

            return True

        except Exception as e:
            logger.error(f"Data storage error: {e}")
            return False

    async def _get_from_duckdb_cache(
        self,
        cache_key: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        ignore_ttl: bool = False,
    ) -> Optional[List[Dict[str, Any]]]:
        """DuckDB 캐시에서 데이터 조회"""
        try:
            if not self._db_manager:
                return None

            # TTL 설정 (ignore_ttl이 True면 매우 긴 시간으로 설정)
            ttl_hours = (
                999999
                if ignore_ttl
                else self.cache_strategy.duckdb_ttl.total_seconds() // 3600
            )

            # DuckDB에서 캐시 데이터 조회
            cached_data = self._db_manager.get_cache_data(
                cache_key=cache_key,
                table_name="market_data_cache",
                ttl_hours=int(ttl_hours),
            )

            if cached_data:
                # 날짜 범위 필터링
                if start_date or end_date:
                    filtered_data = []
                    for item in cached_data:
                        item_date = None
                        # 날짜 필드 추출 (다양한 필드명 지원)
                        for date_field in ["date", "timestamp", "time", "datetime"]:
                            if date_field in item:
                                try:
                                    item_date = datetime.fromisoformat(
                                        str(item[date_field]).replace("Z", "+00:00")
                                    )
                                    break
                                except (ValueError, TypeError):
                                    continue

                        if item_date:
                            if start_date and item_date < start_date:
                                continue
                            if end_date and item_date > end_date:
                                continue

                        filtered_data.append(item)

                    logger.info(
                        f"DuckDB cache hit: {cache_key} ({len(filtered_data)} items after filtering)"
                    )
                    return filtered_data
                else:
                    logger.info(
                        f"DuckDB cache hit: {cache_key} ({len(cached_data)} items)"
                    )
                    return cached_data

            logger.debug(f"DuckDB cache miss: {cache_key}")
            return None

        except Exception as e:
            logger.error(f"DuckDB cache lookup error: {e}")
            return None

    async def _get_from_mongodb_cache(
        self,
        model_class: Type[BaseMarketDataDocument],
        cache_key: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Optional[List[BaseMarketDataDocument]]:
        """MongoDB 캐시에서 데이터 조회"""
        try:
            # MongoDB 쿼리 구성
            query_filter: Dict[str, Any] = {"cache_key": cache_key}

            if start_date or end_date:
                date_filter: Dict[str, datetime] = {}
                if start_date:
                    date_filter["$gte"] = start_date
                if end_date:
                    date_filter["$lte"] = end_date
                query_filter["date"] = date_filter

            # TTL 확인
            ttl_filter: Dict[str, Any] = {
                "updated_at": {
                    "$gte": datetime.now(UTC) - self.cache_strategy.mongodb_ttl
                }
            }
            query_filter.update(ttl_filter)

            # 데이터 조회
            documents = await model_class.find(query_filter).to_list()
            return documents if documents else None

        except Exception as e:
            logger.error(f"MongoDB cache lookup error: {e}")
            return None

    async def _store_to_duckdb_cache(
        self,
        cache_key: str,
        data: List[BaseMarketDataDocument],
        table_name: str = "market_data_cache",
    ) -> bool:
        """DuckDB 캐시에 데이터 저장"""
        try:
            if not data or not self._db_manager:
                return True

            # 데이터 변환
            records = []
            for item in data:
                record = item.dict()
                # 날짜 필드가 datetime 객체면 ISO 문자열로 변환
                for key, value in record.items():
                    if isinstance(value, datetime):
                        record[key] = value.isoformat()
                records.append(record)

            # DuckDB에 저장
            success = self._db_manager.store_cache_data(
                cache_key=cache_key, data=records, table_name=table_name
            )

            if success:
                logger.info(
                    f"DuckDB cache stored: {cache_key} ({len(records)} records)"
                )
            else:
                logger.error(f"Failed to store DuckDB cache: {cache_key}")

            return success

        except Exception as e:
            logger.error(f"DuckDB cache storage error: {e}")
            return False

    async def _store_to_mongodb_cache(self, data: List[BaseMarketDataDocument]) -> bool:
        """MongoDB 캐시에 데이터 저장"""
        try:
            if not data:
                return True

            # 타임스탬프 업데이트
            for item in data:
                item.updated_at = datetime.now(UTC)

            # MongoDB에 저장 (upsert 사용)
            for item in data:
                await item.save()

            logger.info(f"Stored {len(data)} records to MongoDB cache")
            return True

        except Exception as e:
            logger.error(f"MongoDB cache storage error: {e}")
            return False

    @abstractmethod
    async def refresh_data_from_source(self, **kwargs) -> List[BaseMarketDataDocument]:
        """
        외부 소스에서 데이터 갱신 (구현 필요)

        Returns:
            갱신된 데이터 리스트
        """
        pass

    async def get_data_with_fallback(
        self,
        cache_key: str,
        model_class: Type[BaseMarketDataDocument],
        refresh_callback,
        **refresh_kwargs,
    ) -> List[BaseMarketDataDocument]:
        """
        캐시 우선 데이터 조회 (캐시 미스 시 자동 갱신)

        Args:
            cache_key: 캐시 키
            model_class: 데이터 모델 클래스
            refresh_callback: 데이터 갱신 콜백 함수
            **refresh_kwargs: 갱신 함수에 전달할 인자들

        Returns:
            데이터 리스트
        """
        # 1. 캐시 확인
        cached_data = await self.get_cached_data(cache_key, model_class)
        if cached_data:
            return cached_data

        # 2. 캐시 미스 시 외부 소스에서 갱신
        try:
            fresh_data = await refresh_callback(**refresh_kwargs)
            if fresh_data:
                # 캐시에 저장
                table_name = getattr(model_class, "__tablename__", "market_data")
                await self.store_data(cache_key, fresh_data, table_name)
                return fresh_data
            else:
                logger.warning(f"No data received from source for {cache_key}")
                return []

        except Exception as e:
            logger.error(f"Data refresh failed for {cache_key}: {e}")
            # 최후의 수단으로 오래된 캐시라도 반환
            stale_data = await self._get_from_duckdb_cache(cache_key, ignore_ttl=True)
            if stale_data:
                return [model_class(**item) for item in stale_data]
            return []

    async def close(self) -> None:
        """서비스 종료 및 리소스 정리"""
        try:
            # Alpha Vantage 클라이언트 세션 종료
            if self._alpha_vantage_client and hasattr(
                self._alpha_vantage_client, "close"
            ):
                await self._alpha_vantage_client.close()

            # 데이터베이스 연결 종료
            if self._db_manager and hasattr(self._db_manager, "close"):
                self._db_manager.close()

            logger.info(f"{self.__class__.__name__} service closed successfully")

        except Exception as e:
            logger.error(f"Error closing {self.__class__.__name__} service: {e}")
