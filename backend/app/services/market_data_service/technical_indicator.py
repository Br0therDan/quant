"""
Technical Indicator Service
기술적 지표 서비스 - Alpha Vantage + DuckDB 캐싱
"""

import logging
from datetime import datetime, timedelta, UTC
from typing import Optional, List, Dict, Any, Literal
from decimal import Decimal

from app.services.database_manager import DatabaseManager
from app.alpha_vantage import AlphaVantageClient
from app.models.market_data.technical_indicator import TechnicalIndicator
from app.schemas.market_data.technical_indicator import (
    IndicatorDataPoint,
    TechnicalIndicatorData,
)

logger = logging.getLogger(__name__)


class TechnicalIndicatorService:
    """기술적 지표 서비스

    Alpha Vantage API에서 기술적 지표를 가져오고 DuckDB에 캐싱합니다.
    MongoDB에는 메타데이터만 저장하고, 시계열 데이터는 DuckDB에서 관리합니다.
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
                return None  # 결과를 IndicatorDataPoint로 변환
            data_points = []
            for row in result:
                values_dict = None
                # values_json이 있으면 파싱
                if row[3]:  # values_json
                    import json

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
            import json

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

    async def get_sma(
        self,
        symbol: str,
        interval: Literal[
            "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
        ] = "daily",
        time_period: int = 20,
        series_type: Literal["close", "open", "high", "low"] = "close",
    ) -> TechnicalIndicatorData:
        """단순이동평균(SMA) 조회

        Args:
            symbol: 주식 심볼
            interval: 시간 간격
            time_period: 이동평균 기간
            series_type: 계산에 사용할 가격 데이터

        Returns:
            기술적 지표 데이터
        """
        parameters = {
            "time_period": time_period,
            "series_type": series_type,
        }

        cache_key = self._generate_cache_key(symbol, "SMA", interval, parameters)

        # 캐시 확인
        cached_data = await self._check_cache(cache_key)
        if cached_data:
            return TechnicalIndicatorData(
                symbol=symbol,
                indicator_type="SMA",
                interval=interval,
                parameters=parameters,
                data=cached_data,
                data_points_count=len(cached_data),
                latest_value=cached_data[0].value if cached_data else None,
                latest_date=(
                    cached_data[0].timestamp or cached_data[0].date
                    if cached_data
                    else None
                ),
            )

        # Alpha Vantage API 호출
        logger.info(
            f"Fetching SMA from Alpha Vantage: {symbol} {interval} {time_period}"
        )
        api_result = await self.alpha_vantage.ti.sma(
            symbol=symbol,
            interval=interval,
            time_period=time_period,
            series_type=series_type,
        )

        logger.info(
            f"API result type: {type(api_result)}, length: {len(api_result) if hasattr(api_result, '__len__') else 'N/A'}"
        )
        if api_result and len(api_result) > 0:
            logger.info(f"First item sample: {api_result[0]}")

        # 데이터 변환
        data_points = []
        for item in api_result:
            # Alpha Vantage API 응답에서 날짜 추출
            # daily/weekly/monthly는 date, intraday는 datetime 사용
            date_val = item.get("date") or item.get("time") or item.get("datetime")

            point = IndicatorDataPoint(
                date=date_val if interval in ["daily", "weekly", "monthly"] else None,
                timestamp=(
                    date_val if interval not in ["daily", "weekly", "monthly"] else None
                ),
                value=Decimal(str(item["sma"])) if item.get("sma") else None,
                values=None,
            )
            data_points.append(point)

        # DuckDB 캐싱
        await self._save_to_cache(
            cache_key, data_points, symbol, "SMA", interval, parameters
        )

        # MongoDB 메타데이터 저장
        await self._save_metadata_to_mongodb(
            symbol=symbol,
            indicator_type="SMA",
            interval=interval,
            parameters=parameters,
            data_points_count=len(data_points),
            latest_value=data_points[0].value if data_points else None,
            latest_date=(
                data_points[0].timestamp or data_points[0].date if data_points else None
            ),
        )

        return TechnicalIndicatorData(
            symbol=symbol,
            indicator_type="SMA",
            interval=interval,
            parameters=parameters,
            data=data_points,
            data_points_count=len(data_points),
            latest_value=data_points[0].value if data_points else None,
            latest_date=(
                data_points[0].timestamp or data_points[0].date if data_points else None
            ),
        )

    async def get_ema(
        self,
        symbol: str,
        interval: Literal[
            "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
        ] = "daily",
        time_period: int = 20,
        series_type: Literal["close", "open", "high", "low"] = "close",
    ) -> TechnicalIndicatorData:
        """지수이동평균(EMA) 조회

        Args:
            symbol: 주식 심볼
            interval: 시간 간격
            time_period: 이동평균 기간
            series_type: 계산에 사용할 가격 데이터

        Returns:
            기술적 지표 데이터
        """
        parameters = {
            "time_period": time_period,
            "series_type": series_type,
        }

        cache_key = self._generate_cache_key(symbol, "EMA", interval, parameters)

        # 캐시 확인
        cached_data = await self._check_cache(cache_key)
        if cached_data:
            return TechnicalIndicatorData(
                symbol=symbol,
                indicator_type="EMA",
                interval=interval,
                parameters=parameters,
                data=cached_data,
                data_points_count=len(cached_data),
                latest_value=cached_data[0].value if cached_data else None,
                latest_date=(
                    cached_data[0].timestamp or cached_data[0].date
                    if cached_data
                    else None
                ),
            )

        # Alpha Vantage API 호출
        logger.info(
            f"Fetching EMA from Alpha Vantage: {symbol} {interval} {time_period}"
        )
        api_result = await self.alpha_vantage.ti.ema(
            symbol=symbol,
            interval=interval,
            time_period=time_period,
            series_type=series_type,
        )

        # 데이터 변환
        data_points = []
        for item in api_result:
            point = IndicatorDataPoint(
                date=item.get("date"),
                timestamp=item.get("datetime"),
                value=Decimal(str(item["ema"])) if item.get("ema") else None,
                values=None,
            )
            data_points.append(point)

        # DuckDB 캐싱
        await self._save_to_cache(
            cache_key, data_points, symbol, "EMA", interval, parameters
        )

        # MongoDB 메타데이터 저장
        await self._save_metadata_to_mongodb(
            symbol=symbol,
            indicator_type="EMA",
            interval=interval,
            parameters=parameters,
            data_points_count=len(data_points),
            latest_value=data_points[0].value if data_points else None,
            latest_date=(
                data_points[0].timestamp or data_points[0].date if data_points else None
            ),
        )

        return TechnicalIndicatorData(
            symbol=symbol,
            indicator_type="EMA",
            interval=interval,
            parameters=parameters,
            data=data_points,
            data_points_count=len(data_points),
            latest_value=data_points[0].value if data_points else None,
            latest_date=(
                data_points[0].timestamp or data_points[0].date if data_points else None
            ),
        )

    async def get_rsi(
        self,
        symbol: str,
        interval: Literal[
            "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
        ] = "daily",
        time_period: int = 14,
        series_type: Literal["close", "open", "high", "low"] = "close",
    ) -> TechnicalIndicatorData:
        """상대강도지수(RSI) 조회

        Args:
            symbol: 주식 심볼
            interval: 시간 간격
            time_period: RSI 계산 기간
            series_type: 계산에 사용할 가격 데이터

        Returns:
            기술적 지표 데이터
        """
        parameters = {
            "time_period": time_period,
            "series_type": series_type,
        }

        cache_key = self._generate_cache_key(symbol, "RSI", interval, parameters)

        # 캐시 확인
        cached_data = await self._check_cache(cache_key)
        if cached_data:
            return TechnicalIndicatorData(
                symbol=symbol,
                indicator_type="RSI",
                interval=interval,
                parameters=parameters,
                data=cached_data,
                data_points_count=len(cached_data),
                latest_value=cached_data[0].value if cached_data else None,
                latest_date=(
                    cached_data[0].timestamp or cached_data[0].date
                    if cached_data
                    else None
                ),
            )

        # Alpha Vantage API 호출
        logger.info(
            f"Fetching RSI from Alpha Vantage: {symbol} {interval} {time_period}"
        )
        api_result = await self.alpha_vantage.ti.rsi(
            symbol=symbol,
            interval=interval,
            time_period=time_period,
            series_type=series_type,
        )

        # 데이터 변환
        data_points = []
        for item in api_result:
            point = IndicatorDataPoint(
                date=item.get("date"),
                timestamp=item.get("datetime"),
                value=Decimal(str(item["rsi"])) if item.get("rsi") else None,
                values=None,
            )
            data_points.append(point)

        # DuckDB 캐싱
        await self._save_to_cache(
            cache_key, data_points, symbol, "RSI", interval, parameters
        )

        # MongoDB 메타데이터 저장
        await self._save_metadata_to_mongodb(
            symbol=symbol,
            indicator_type="RSI",
            interval=interval,
            parameters=parameters,
            data_points_count=len(data_points),
            latest_value=data_points[0].value if data_points else None,
            latest_date=(
                data_points[0].timestamp or data_points[0].date if data_points else None
            ),
        )

        return TechnicalIndicatorData(
            symbol=symbol,
            indicator_type="RSI",
            interval=interval,
            parameters=parameters,
            data=data_points,
            data_points_count=len(data_points),
            latest_value=data_points[0].value if data_points else None,
            latest_date=(
                data_points[0].timestamp or data_points[0].date if data_points else None
            ),
        )

    async def get_macd(
        self,
        symbol: str,
        interval: Literal[
            "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
        ] = "daily",
        series_type: Literal["close", "open", "high", "low"] = "close",
        fastperiod: int = 12,
        slowperiod: int = 26,
        signalperiod: int = 9,
    ) -> TechnicalIndicatorData:
        """MACD 조회

        Args:
            symbol: 주식 심볼
            interval: 시간 간격
            series_type: 계산에 사용할 가격 데이터
            fastperiod: 빠른 이동평균 기간
            slowperiod: 느린 이동평균 기간
            signalperiod: 시그널 라인 기간

        Returns:
            기술적 지표 데이터
        """
        parameters = {
            "series_type": series_type,
            "fastperiod": fastperiod,
            "slowperiod": slowperiod,
            "signalperiod": signalperiod,
        }

        cache_key = self._generate_cache_key(symbol, "MACD", interval, parameters)

        # 캐시 확인
        cached_data = await self._check_cache(cache_key)
        if cached_data:
            return TechnicalIndicatorData(
                symbol=symbol,
                indicator_type="MACD",
                interval=interval,
                parameters=parameters,
                data=cached_data,
                data_points_count=len(cached_data),
                latest_value=None,  # MACD는 multi-value
                latest_date=(
                    cached_data[0].timestamp or cached_data[0].date
                    if cached_data
                    else None
                ),
            )

        # Alpha Vantage API 호출
        logger.info(f"Fetching MACD from Alpha Vantage: {symbol} {interval}")
        api_result = await self.alpha_vantage.ti.macd(
            symbol=symbol,
            interval=interval,
            series_type=series_type,
            fastperiod=fastperiod,
            slowperiod=slowperiod,
            signalperiod=signalperiod,
        )

        # 데이터 변환
        data_points = []
        for item in api_result:
            values_dict = {}
            if item.get("macd"):
                values_dict["macd"] = Decimal(str(item["macd"]))
            if item.get("macd_signal"):
                values_dict["signal"] = Decimal(str(item["macd_signal"]))
            if item.get("macd_hist"):
                values_dict["histogram"] = Decimal(str(item["macd_hist"]))

            point = IndicatorDataPoint(
                date=item.get("date"),
                timestamp=item.get("datetime"),
                value=None,  # MACD는 multi-value
                values=values_dict if values_dict else None,
            )
            data_points.append(point)

        # DuckDB 캐싱
        await self._save_to_cache(
            cache_key, data_points, symbol, "MACD", interval, parameters
        )

        # MongoDB 메타데이터 저장
        await self._save_metadata_to_mongodb(
            symbol=symbol,
            indicator_type="MACD",
            interval=interval,
            parameters=parameters,
            data_points_count=len(data_points),
            latest_value=None,
            latest_date=(
                data_points[0].timestamp or data_points[0].date if data_points else None
            ),
        )

        return TechnicalIndicatorData(
            symbol=symbol,
            indicator_type="MACD",
            interval=interval,
            parameters=parameters,
            data=data_points,
            data_points_count=len(data_points),
            latest_value=None,
            latest_date=(
                data_points[0].timestamp or data_points[0].date if data_points else None
            ),
        )

    async def get_bbands(
        self,
        symbol: str,
        interval: Literal[
            "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
        ] = "daily",
        time_period: int = 20,
        series_type: Literal["close", "open", "high", "low"] = "close",
        nbdevup: int = 2,
        nbdevdn: int = 2,
    ) -> TechnicalIndicatorData:
        """볼린저밴드(BBANDS) 조회

        Args:
            symbol: 주식 심볼
            interval: 시간 간격
            time_period: 이동평균 기간
            series_type: 계산에 사용할 가격 데이터
            nbdevup: 상단 밴드 표준편차 배수
            nbdevdn: 하단 밴드 표준편차 배수

        Returns:
            기술적 지표 데이터
        """
        parameters = {
            "time_period": time_period,
            "series_type": series_type,
            "nbdevup": nbdevup,
            "nbdevdn": nbdevdn,
        }

        cache_key = self._generate_cache_key(symbol, "BBANDS", interval, parameters)

        # 캐시 확인
        cached_data = await self._check_cache(cache_key)
        if cached_data:
            return TechnicalIndicatorData(
                symbol=symbol,
                indicator_type="BBANDS",
                interval=interval,
                parameters=parameters,
                data=cached_data,
                data_points_count=len(cached_data),
                latest_value=None,  # BBANDS는 multi-value
                latest_date=(
                    cached_data[0].timestamp or cached_data[0].date
                    if cached_data
                    else None
                ),
            )

        # Alpha Vantage API 호출
        logger.info(
            f"Fetching BBANDS from Alpha Vantage: {symbol} {interval} {time_period}"
        )
        api_result = await self.alpha_vantage.ti.bbands(
            symbol=symbol,
            interval=interval,
            time_period=time_period,
            series_type=series_type,
            nbdevup=nbdevup,
            nbdevdn=nbdevdn,
        )

        # 데이터 변환
        data_points = []
        for item in api_result:
            values_dict = {}
            if item.get("real_upper_band"):
                values_dict["upper"] = Decimal(str(item["real_upper_band"]))
            if item.get("real_middle_band"):
                values_dict["middle"] = Decimal(str(item["real_middle_band"]))
            if item.get("real_lower_band"):
                values_dict["lower"] = Decimal(str(item["real_lower_band"]))

            point = IndicatorDataPoint(
                date=item.get("date"),
                timestamp=item.get("datetime"),
                value=None,  # BBANDS는 multi-value
                values=values_dict if values_dict else None,
            )
            data_points.append(point)

        # DuckDB 캐싱
        await self._save_to_cache(
            cache_key, data_points, symbol, "BBANDS", interval, parameters
        )

        # MongoDB 메타데이터 저장
        await self._save_metadata_to_mongodb(
            symbol=symbol,
            indicator_type="BBANDS",
            interval=interval,
            parameters=parameters,
            data_points_count=len(data_points),
            latest_value=None,
            latest_date=(
                data_points[0].timestamp or data_points[0].date if data_points else None
            ),
        )

        return TechnicalIndicatorData(
            symbol=symbol,
            indicator_type="BBANDS",
            interval=interval,
            parameters=parameters,
            data=data_points,
            data_points_count=len(data_points),
            latest_value=None,
            latest_date=(
                data_points[0].timestamp or data_points[0].date if data_points else None
            ),
        )

    async def get_wma(
        self,
        symbol: str,
        interval: Literal[
            "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
        ] = "daily",
        time_period: int = 20,
        series_type: Literal["close", "open", "high", "low"] = "close",
    ) -> TechnicalIndicatorData:
        """가중이동평균(WMA) 조회

        Args:
            symbol: 주식 심볼
            interval: 시간 간격
            time_period: 이동평균 기간
            series_type: 계산에 사용할 가격 데이터

        Returns:
            기술적 지표 데이터
        """
        parameters = {
            "time_period": time_period,
            "series_type": series_type,
        }

        cache_key = self._generate_cache_key(symbol, "WMA", interval, parameters)

        # 캐시 확인
        cached_data = await self._check_cache(cache_key)
        if cached_data:
            return TechnicalIndicatorData(
                symbol=symbol,
                indicator_type="WMA",
                interval=interval,
                parameters=parameters,
                data=cached_data,
                data_points_count=len(cached_data),
                latest_value=cached_data[0].value if cached_data else None,
                latest_date=(
                    cached_data[0].timestamp or cached_data[0].date
                    if cached_data
                    else None
                ),
            )

        # Alpha Vantage API 호출
        logger.info(
            f"Fetching WMA from Alpha Vantage: {symbol} {interval} {time_period}"
        )
        api_result = await self.alpha_vantage.ti.wma(
            symbol=symbol,
            interval=interval,
            time_period=time_period,
            series_type=series_type,
        )

        # 데이터 변환
        data_points = []
        for item in api_result:
            # Alpha Vantage API 응답에서 날짜 추출
            date_val = item.get("date") or item.get("time") or item.get("datetime")

            point = IndicatorDataPoint(
                date=date_val if interval in ["daily", "weekly", "monthly"] else None,
                timestamp=(
                    date_val if interval not in ["daily", "weekly", "monthly"] else None
                ),
                value=Decimal(str(item["wma"])) if item.get("wma") else None,
                values=None,
            )
            data_points.append(point)

        # DuckDB 캐싱
        await self._save_to_cache(
            cache_key, data_points, symbol, "WMA", interval, parameters
        )

        # MongoDB 메타데이터 저장
        await self._save_metadata_to_mongodb(
            symbol=symbol,
            indicator_type="WMA",
            interval=interval,
            parameters=parameters,
            data_points_count=len(data_points),
            latest_value=data_points[0].value if data_points else None,
            latest_date=(
                data_points[0].timestamp or data_points[0].date if data_points else None
            ),
        )

        return TechnicalIndicatorData(
            symbol=symbol,
            indicator_type="WMA",
            interval=interval,
            parameters=parameters,
            data=data_points,
            data_points_count=len(data_points),
            latest_value=data_points[0].value if data_points else None,
            latest_date=(
                data_points[0].timestamp or data_points[0].date if data_points else None
            ),
        )

    async def get_dema(
        self,
        symbol: str,
        interval: Literal[
            "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
        ] = "daily",
        time_period: int = 20,
        series_type: Literal["close", "open", "high", "low"] = "close",
    ) -> TechnicalIndicatorData:
        """이중지수이동평균(DEMA) 조회

        Args:
            symbol: 주식 심볼
            interval: 시간 간격
            time_period: 이동평균 기간
            series_type: 계산에 사용할 가격 데이터

        Returns:
            기술적 지표 데이터
        """
        parameters = {
            "time_period": time_period,
            "series_type": series_type,
        }

        cache_key = self._generate_cache_key(symbol, "DEMA", interval, parameters)

        # 캐시 확인
        cached_data = await self._check_cache(cache_key)
        if cached_data:
            return TechnicalIndicatorData(
                symbol=symbol,
                indicator_type="DEMA",
                interval=interval,
                parameters=parameters,
                data=cached_data,
                data_points_count=len(cached_data),
                latest_value=cached_data[0].value if cached_data else None,
                latest_date=(
                    cached_data[0].timestamp or cached_data[0].date
                    if cached_data
                    else None
                ),
            )

        # Alpha Vantage API 호출
        logger.info(
            f"Fetching DEMA from Alpha Vantage: {symbol} {interval} {time_period}"
        )
        api_result = await self.alpha_vantage.ti.dema(
            symbol=symbol,
            interval=interval,
            time_period=time_period,
            series_type=series_type,
        )

        # 데이터 변환
        data_points = []
        for item in api_result:
            date_val = item.get("date") or item.get("time") or item.get("datetime")

            point = IndicatorDataPoint(
                date=date_val if interval in ["daily", "weekly", "monthly"] else None,
                timestamp=(
                    date_val if interval not in ["daily", "weekly", "monthly"] else None
                ),
                value=Decimal(str(item["dema"])) if item.get("dema") else None,
                values=None,
            )
            data_points.append(point)

        # DuckDB 캐싱
        await self._save_to_cache(
            cache_key, data_points, symbol, "DEMA", interval, parameters
        )

        # MongoDB 메타데이터 저장
        await self._save_metadata_to_mongodb(
            symbol=symbol,
            indicator_type="DEMA",
            interval=interval,
            parameters=parameters,
            data_points_count=len(data_points),
            latest_value=data_points[0].value if data_points else None,
            latest_date=(
                data_points[0].timestamp or data_points[0].date if data_points else None
            ),
        )

        return TechnicalIndicatorData(
            symbol=symbol,
            indicator_type="DEMA",
            interval=interval,
            parameters=parameters,
            data=data_points,
            data_points_count=len(data_points),
            latest_value=data_points[0].value if data_points else None,
            latest_date=(
                data_points[0].timestamp or data_points[0].date if data_points else None
            ),
        )

    async def get_tema(
        self,
        symbol: str,
        interval: Literal[
            "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
        ] = "daily",
        time_period: int = 20,
        series_type: Literal["close", "open", "high", "low"] = "close",
    ) -> TechnicalIndicatorData:
        """삼중지수이동평균(TEMA) 조회

        Args:
            symbol: 주식 심볼
            interval: 시간 간격
            time_period: 이동평균 기간
            series_type: 계산에 사용할 가격 데이터

        Returns:
            기술적 지표 데이터
        """
        parameters = {
            "time_period": time_period,
            "series_type": series_type,
        }

        cache_key = self._generate_cache_key(symbol, "TEMA", interval, parameters)

        # 캐시 확인
        cached_data = await self._check_cache(cache_key)
        if cached_data:
            return TechnicalIndicatorData(
                symbol=symbol,
                indicator_type="TEMA",
                interval=interval,
                parameters=parameters,
                data=cached_data,
                data_points_count=len(cached_data),
                latest_value=cached_data[0].value if cached_data else None,
                latest_date=(
                    cached_data[0].timestamp or cached_data[0].date
                    if cached_data
                    else None
                ),
            )

        # Alpha Vantage API 호출
        logger.info(
            f"Fetching TEMA from Alpha Vantage: {symbol} {interval} {time_period}"
        )
        api_result = await self.alpha_vantage.ti.tema(
            symbol=symbol,
            interval=interval,
            time_period=time_period,
            series_type=series_type,
        )

        # 데이터 변환
        data_points = []
        for item in api_result:
            date_val = item.get("date") or item.get("time") or item.get("datetime")

            point = IndicatorDataPoint(
                date=date_val if interval in ["daily", "weekly", "monthly"] else None,
                timestamp=(
                    date_val if interval not in ["daily", "weekly", "monthly"] else None
                ),
                value=Decimal(str(item["tema"])) if item.get("tema") else None,
                values=None,
            )
            data_points.append(point)

        # DuckDB 캐싱
        await self._save_to_cache(
            cache_key, data_points, symbol, "TEMA", interval, parameters
        )

        # MongoDB 메타데이터 저장
        await self._save_metadata_to_mongodb(
            symbol=symbol,
            indicator_type="TEMA",
            interval=interval,
            parameters=parameters,
            data_points_count=len(data_points),
            latest_value=data_points[0].value if data_points else None,
            latest_date=(
                data_points[0].timestamp or data_points[0].date if data_points else None
            ),
        )

        return TechnicalIndicatorData(
            symbol=symbol,
            indicator_type="TEMA",
            interval=interval,
            parameters=parameters,
            data=data_points,
            data_points_count=len(data_points),
            latest_value=data_points[0].value if data_points else None,
            latest_date=(
                data_points[0].timestamp or data_points[0].date if data_points else None
            ),
        )

    async def get_adx(
        self,
        symbol: str,
        interval: Literal[
            "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
        ] = "daily",
        time_period: int = 14,
    ) -> TechnicalIndicatorData:
        """평균방향지수(ADX) 조회

        Args:
            symbol: 주식 심볼
            interval: 시간 간격
            time_period: ADX 계산 기간

        Returns:
            기술적 지표 데이터
        """
        parameters = {
            "time_period": time_period,
        }

        cache_key = self._generate_cache_key(symbol, "ADX", interval, parameters)

        # 캐시 확인
        cached_data = await self._check_cache(cache_key)
        if cached_data:
            return TechnicalIndicatorData(
                symbol=symbol,
                indicator_type="ADX",
                interval=interval,
                parameters=parameters,
                data=cached_data,
                data_points_count=len(cached_data),
                latest_value=cached_data[0].value if cached_data else None,
                latest_date=(
                    cached_data[0].timestamp or cached_data[0].date
                    if cached_data
                    else None
                ),
            )

        # Alpha Vantage API 호출
        logger.info(
            f"Fetching ADX from Alpha Vantage: {symbol} {interval} {time_period}"
        )
        api_result = await self.alpha_vantage.ti.adx(
            symbol=symbol,
            interval=interval,
            time_period=time_period,
        )

        # 데이터 변환
        data_points = []
        for item in api_result:
            date_val = item.get("date") or item.get("time") or item.get("datetime")

            point = IndicatorDataPoint(
                date=date_val if interval in ["daily", "weekly", "monthly"] else None,
                timestamp=(
                    date_val if interval not in ["daily", "weekly", "monthly"] else None
                ),
                value=Decimal(str(item["adx"])) if item.get("adx") else None,
                values=None,
            )
            data_points.append(point)

        # DuckDB 캐싱
        await self._save_to_cache(
            cache_key, data_points, symbol, "ADX", interval, parameters
        )

        # MongoDB 메타데이터 저장
        await self._save_metadata_to_mongodb(
            symbol=symbol,
            indicator_type="ADX",
            interval=interval,
            parameters=parameters,
            data_points_count=len(data_points),
            latest_value=data_points[0].value if data_points else None,
            latest_date=(
                data_points[0].timestamp or data_points[0].date if data_points else None
            ),
        )

        return TechnicalIndicatorData(
            symbol=symbol,
            indicator_type="ADX",
            interval=interval,
            parameters=parameters,
            data=data_points,
            data_points_count=len(data_points),
            latest_value=data_points[0].value if data_points else None,
            latest_date=(
                data_points[0].timestamp or data_points[0].date if data_points else None
            ),
        )

    async def get_atr(
        self,
        symbol: str,
        interval: Literal[
            "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
        ] = "daily",
        time_period: int = 14,
    ) -> TechnicalIndicatorData:
        """평균진폭(ATR) 조회

        Args:
            symbol: 주식 심볼
            interval: 시간 간격
            time_period: ATR 계산 기간

        Returns:
            기술적 지표 데이터
        """
        parameters = {
            "time_period": time_period,
        }

        cache_key = self._generate_cache_key(symbol, "ATR", interval, parameters)

        # 캐시 확인
        cached_data = await self._check_cache(cache_key)
        if cached_data:
            return TechnicalIndicatorData(
                symbol=symbol,
                indicator_type="ATR",
                interval=interval,
                parameters=parameters,
                data=cached_data,
                data_points_count=len(cached_data),
                latest_value=cached_data[0].value if cached_data else None,
                latest_date=(
                    cached_data[0].timestamp or cached_data[0].date
                    if cached_data
                    else None
                ),
            )

        # Alpha Vantage API 호출
        logger.info(
            f"Fetching ATR from Alpha Vantage: {symbol} {interval} {time_period}"
        )
        api_result = await self.alpha_vantage.ti.atr(
            symbol=symbol,
            interval=interval,
            time_period=time_period,
        )

        # 데이터 변환
        data_points = []
        for item in api_result:
            date_val = item.get("date") or item.get("time") or item.get("datetime")

            point = IndicatorDataPoint(
                date=date_val if interval in ["daily", "weekly", "monthly"] else None,
                timestamp=(
                    date_val if interval not in ["daily", "weekly", "monthly"] else None
                ),
                value=Decimal(str(item["atr"])) if item.get("atr") else None,
                values=None,
            )
            data_points.append(point)

        # DuckDB 캐싱
        await self._save_to_cache(
            cache_key, data_points, symbol, "ATR", interval, parameters
        )

        # MongoDB 메타데이터 저장
        await self._save_metadata_to_mongodb(
            symbol=symbol,
            indicator_type="ATR",
            interval=interval,
            parameters=parameters,
            data_points_count=len(data_points),
            latest_value=data_points[0].value if data_points else None,
            latest_date=(
                data_points[0].timestamp or data_points[0].date if data_points else None
            ),
        )

        return TechnicalIndicatorData(
            symbol=symbol,
            indicator_type="ATR",
            interval=interval,
            parameters=parameters,
            data=data_points,
            data_points_count=len(data_points),
            latest_value=data_points[0].value if data_points else None,
            latest_date=(
                data_points[0].timestamp or data_points[0].date if data_points else None
            ),
        )

    async def get_stoch(
        self,
        symbol: str,
        interval: Literal[
            "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
        ] = "daily",
        fastkperiod: int = 5,
        slowkperiod: int = 3,
        slowdperiod: int = 3,
        slowkmatype: int = 0,
        slowdmatype: int = 0,
    ) -> TechnicalIndicatorData:
        """스토캐스틱 오실레이터(STOCH) 조회

        Args:
            symbol: 주식 심볼
            interval: 시간 간격
            fastkperiod: Fast K 기간
            slowkperiod: Slow K 기간
            slowdperiod: Slow D 기간
            slowkmatype: Slow K MA 타입
            slowdmatype: Slow D MA 타입

        Returns:
            기술적 지표 데이터 (slowk, slowd 값 포함)
        """
        parameters = {
            "fastkperiod": fastkperiod,
            "slowkperiod": slowkperiod,
            "slowdperiod": slowdperiod,
            "slowkmatype": slowkmatype,
            "slowdmatype": slowdmatype,
        }

        cache_key = self._generate_cache_key(symbol, "STOCH", interval, parameters)

        # 캐시 확인
        cached_data = await self._check_cache(cache_key)
        if cached_data:
            return TechnicalIndicatorData(
                symbol=symbol,
                indicator_type="STOCH",
                interval=interval,
                parameters=parameters,
                data=cached_data,
                data_points_count=len(cached_data),
                latest_value=None,  # STOCH는 multi-value
                latest_date=(
                    cached_data[0].timestamp or cached_data[0].date
                    if cached_data
                    else None
                ),
            )

        # Alpha Vantage API 호출
        logger.info(f"Fetching STOCH from Alpha Vantage: {symbol} {interval}")
        api_result = await self.alpha_vantage.ti.stoch(
            symbol=symbol,
            interval=interval,
            fastkperiod=fastkperiod,
            slowkperiod=slowkperiod,
            slowdperiod=slowdperiod,
            slowkmatype=slowkmatype,
            slowdmatype=slowdmatype,
        )

        # 데이터 변환
        data_points = []
        for item in api_result:
            date_val = item.get("date") or item.get("time") or item.get("datetime")

            values_dict = {}
            if item.get("slowk") is not None:
                values_dict["slowk"] = Decimal(str(item["slowk"]))
            if item.get("slowd") is not None:
                values_dict["slowd"] = Decimal(str(item["slowd"]))

            point = IndicatorDataPoint(
                date=date_val if interval in ["daily", "weekly", "monthly"] else None,
                timestamp=(
                    date_val if interval not in ["daily", "weekly", "monthly"] else None
                ),
                value=None,
                values=values_dict if values_dict else None,
            )
            data_points.append(point)

        # DuckDB 캐싱
        await self._save_to_cache(
            cache_key, data_points, symbol, "STOCH", interval, parameters
        )

        # MongoDB 메타데이터 저장
        await self._save_metadata_to_mongodb(
            symbol=symbol,
            indicator_type="STOCH",
            interval=interval,
            parameters=parameters,
            data_points_count=len(data_points),
            latest_value=None,
            latest_date=(
                data_points[0].timestamp or data_points[0].date if data_points else None
            ),
        )

        return TechnicalIndicatorData(
            symbol=symbol,
            indicator_type="STOCH",
            interval=interval,
            parameters=parameters,
            data=data_points,
            data_points_count=len(data_points),
            latest_value=None,
            latest_date=(
                data_points[0].timestamp or data_points[0].date if data_points else None
            ),
        )

    async def get_indicator_list(self) -> Dict[str, List[str]]:
        """지원하는 기술적 지표 목록 반환

        Returns:
            지표 카테고리별 목록
        """
        return {
            "moving_averages": [
                "SMA",
                "EMA",
                "WMA",
                "DEMA",
                "TEMA",
                "TRIMA",
                "KAMA",
                "MAMA",
                "T3",
            ],
            "oscillators": ["MACD", "RSI", "STOCH", "ADX", "CCI", "AROON"],
            "volatility": ["BBANDS", "ATR"],
            "volume": ["VWAP", "OBV"],
        }
