"""
Base Technical Indicator Service
기술적 지표 서비스 기본 클래스 - 공통 로직 (캐싱, 파싱)
"""

import json
import logging
from datetime import datetime, timedelta, UTC
from typing import Optional, List, Dict, Any, Literal
from decimal import Decimal

from app.services.database_manager import DatabaseManager
from app.alpha_vantage import AlphaVantageClient
from app.models.market_data.technical_indicator import TechnicalIndicator
from app.schemas.market_data.technical_indicator import (
    IndicatorDataPoint,
)

logger = logging.getLogger(__name__)


class BaseIndicatorService:
    """기술적 지표 서비스 기본 클래스

    Alpha Vantage API에서 기술적 지표를 가져오고 DuckDB에 캐싱합니다.
    MongoDB에는 메타데이터만 저장하고, 시계열 데이터는 DuckDB에서 관리합니다.

    서브클래스는 이 클래스를 상속받아 각 카테고리별 지표를 구현합니다:
    - TrendIndicatorService: 추세 지표 (SMA, EMA, WMA, DEMA, TEMA)
    - MomentumIndicatorService: 모멘텀 지표 (RSI, MACD, STOCH)
    - VolatilityIndicatorService: 변동성 지표 (BBANDS, ATR, ADX)
    """

    def __init__(self, database_manager: Optional[DatabaseManager] = None):
        """서비스 초기화

        Args:
            database_manager: DuckDB 캐시 매니저 (optional)
        """
        self._alpha_vantage_client: Optional[AlphaVantageClient] = None
        self._db_manager: Optional[DatabaseManager] = database_manager
        self.cache_ttl_hours = 24  # 기본 캐시 TTL: 24시간

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

    def _generate_cache_key(
        self,
        symbol: str,
        indicator_type: str,
        interval: str,
        parameters: Dict[str, Any],
    ) -> str:
        """캐시 키 생성

        Args:
            symbol: 주식 심볼
            indicator_type: 지표 타입 (SMA, EMA, RSI, etc.)
            interval: 시간 간격
            parameters: 지표 파라미터

        Returns:
            캐시 키 문자열
        """
        # 파라미터를 정렬하여 일관된 키 생성
        param_str = "_".join(
            f"{k}={v}" for k, v in sorted(parameters.items()) if v is not None
        )
        return f"ti_{symbol}_{indicator_type}_{interval}_{param_str}"

    async def _check_cache(self, cache_key: str) -> Optional[List[IndicatorDataPoint]]:
        """DuckDB 캐시 확인

        Args:
            cache_key: 캐시 키

        Returns:
            캐시된 데이터 또는 None
        """
        try:
            if not self.db_manager.connection:
                self.db_manager.connect()

            if not self.db_manager.connection:
                logger.warning("DuckDB connection not available for cache check")
                return None

            query = """
                SELECT date, timestamp, value, values_json
                FROM technical_indicators_cache
                WHERE cache_key = ?
                AND cached_at >= ?
                ORDER BY COALESCE(timestamp, date) DESC
            """
            cutoff_time = datetime.now(UTC) - timedelta(hours=self.cache_ttl_hours)

            result = self.db_manager.connection.execute(
                query, [cache_key, cutoff_time.isoformat()]
            ).fetchall()

            if not result:
                return None

            # 결과를 IndicatorDataPoint로 변환
            data_points = []
            for row in result:
                values_dict = None
                # values_json이 있으면 파싱
                if row[3]:  # values_json
                    parsed = json.loads(row[3])
                    values_dict = {k: Decimal(str(v)) for k, v in parsed.items()}

                point = IndicatorDataPoint(
                    date=row[0],  # date
                    timestamp=row[1],  # timestamp
                    value=Decimal(str(row[2])) if row[2] else None,  # value
                    values=values_dict,
                )
                data_points.append(point)

            logger.info(f"Cache hit for {cache_key}: {len(data_points)} points")
            return data_points

        except Exception as e:
            logger.error(f"Cache check error for {cache_key}: {e}")
            return None

    async def _save_to_cache(
        self,
        cache_key: str,
        data: List[IndicatorDataPoint],
        symbol: str,
        indicator_type: str,
        interval: str,
        parameters: Dict[str, Any],
    ) -> None:
        """DuckDB에 데이터 캐싱

        Args:
            cache_key: 캐시 키
            data: 지표 데이터 포인트 리스트
            symbol: 주식 심볼
            indicator_type: 지표 타입
            interval: 시간 간격
            parameters: 지표 파라미터
        """
        try:
            if not self.db_manager.connection:
                self.db_manager.connect()

            if not self.db_manager.connection:
                logger.warning("DuckDB connection not available for caching")
                return

            # 기존 캐시 삭제
            delete_query = "DELETE FROM technical_indicators_cache WHERE cache_key = ?"
            self.db_manager.connection.execute(delete_query, [cache_key])

            # 새 데이터 삽입
            insert_query = """
                INSERT INTO technical_indicators_cache
                (cache_key, symbol, indicator_type, interval, parameters_json,
                 date, timestamp, value, values_json, cached_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            params_json = json.dumps(parameters)
            now = datetime.now(UTC).isoformat()

            for point in data:
                values_json = None
                if point.values:
                    values_json = json.dumps(
                        {k: str(v) for k, v in point.values.items()}
                    )

                # date와 timestamp 중 하나는 반드시 있어야 함
                date_str = None
                timestamp_str = None

                if point.date:
                    date_str = (
                        point.date.isoformat()
                        if hasattr(point.date, "isoformat")
                        else str(point.date)
                    )
                if point.timestamp:
                    timestamp_str = (
                        point.timestamp.isoformat()
                        if hasattr(point.timestamp, "isoformat")
                        else str(point.timestamp)
                    )

                # 둘 다 None이면 건너뛰기
                if not date_str and not timestamp_str:
                    logger.warning(
                        f"Skipping data point with no date/timestamp: {point}"
                    )
                    continue

                # DuckDB용 파라미터 준비
                params = [
                    cache_key,
                    symbol,
                    indicator_type,
                    interval,
                    params_json,
                    date_str,
                    timestamp_str,
                    float(point.value) if point.value else None,  # Decimal -> float
                    values_json,
                    now,
                ]

                self.db_manager.connection.execute(insert_query, params)

            logger.info(f"Cached {len(data)} points for {cache_key}")

        except Exception as e:
            logger.error(f"Cache save error for {cache_key}: {e}")

    async def _save_metadata_to_mongodb(
        self,
        symbol: str,
        indicator_type: str,
        interval: Literal[
            "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
        ],
        parameters: Dict[str, Any],
        data_points_count: int,
        latest_value: Optional[Decimal],
        latest_date: Optional[datetime],
    ) -> None:
        """MongoDB에 메타데이터 저장

        Args:
            symbol: 주식 심볼
            indicator_type: 지표 타입
            interval: 시간 간격
            parameters: 지표 파라미터
            data_points_count: 데이터 포인트 개수
            latest_value: 최신 값
            latest_date: 최신 날짜
        """
        try:
            # 기존 메타데이터 검색 또는 생성
            metadata = await TechnicalIndicator.find_one(
                TechnicalIndicator.symbol == symbol,
                TechnicalIndicator.indicator_type == indicator_type,
                TechnicalIndicator.interval == interval,
            )

            if metadata:
                # 업데이트
                metadata.parameters = parameters
                metadata.data_points_count = data_points_count
                metadata.latest_value = latest_value
                metadata.latest_date = latest_date
                metadata.last_fetched = datetime.now(UTC)
                await metadata.save()
            else:
                # 새로 생성
                metadata = TechnicalIndicator(
                    symbol=symbol,
                    indicator_type=indicator_type,
                    interval=interval,
                    parameters=parameters,
                    data_points_count=data_points_count,
                    latest_value=latest_value,
                    latest_date=latest_date,
                    last_fetched=datetime.now(UTC),
                    cache_ttl=self.cache_ttl_hours * 3600,
                    data_quality_score=95.0,  # Alpha Vantage 데이터 기본 품질 점수
                )
                await metadata.insert()

            logger.info(f"Saved metadata for {symbol} {indicator_type}")

        except Exception as e:
            logger.error(f"MongoDB metadata save error: {e}")
