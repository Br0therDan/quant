"""
Volatility Technical Indicators
변동성 지표 서비스 - BBANDS, ATR, ADX
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


class VolatilityIndicatorService(BaseIndicatorService):
    """변동성 지표 서비스

    가격 변동성 기반 지표들을 제공합니다:
    - BBANDS: 볼린저밴드
    - ATR: 평균진폭
    - ADX: 평균방향지수
    """

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
            point = IndicatorDataPoint(
                date=item.get("date"),
                timestamp=item.get("datetime"),
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
            point = IndicatorDataPoint(
                date=item.get("date"),
                timestamp=item.get("datetime"),
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
