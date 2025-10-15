"""
Trend Technical Indicators
추세 지표 서비스 - SMA, EMA, WMA, DEMA, TEMA
"""

import logging
from typing import Literal
from decimal import Decimal

from app.schemas.market_data.technical_indicator import (
    IndicatorDataPoint,
    TechnicalIndicatorData,
)
from .base import BaseIndicatorService

logger = logging.getLogger(__name__)


class TrendIndicatorService(BaseIndicatorService):
    """추세 지표 서비스

    이동평균 기반 추세 지표들을 제공합니다:
    - SMA: 단순이동평균
    - EMA: 지수이동평균
    - WMA: 가중이동평균
    - DEMA: 이중지수이동평균
    - TEMA: 삼중지수이동평균
    """

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
            point = IndicatorDataPoint(
                date=item.get("date"),
                timestamp=item.get("datetime"),
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
            point = IndicatorDataPoint(
                date=item.get("date"),
                timestamp=item.get("datetime"),
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
            point = IndicatorDataPoint(
                date=item.get("date"),
                timestamp=item.get("datetime"),
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
            point = IndicatorDataPoint(
                date=item.get("date"),
                timestamp=item.get("datetime"),
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
