"""
Momentum Technical Indicators
모멘텀 지표 서비스 - RSI, MACD, STOCH
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


class MomentumIndicatorService(BaseIndicatorService):
    """모멘텀 지표 서비스

    가격 모멘텀 기반 지표들을 제공합니다:
    - RSI: 상대강도지수
    - MACD: 이동평균 수렴/확산
    - STOCH: 스토캐스틱 오실레이터
    """

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
            values_dict = {}
            if item.get("slowk") is not None:
                values_dict["slowk"] = Decimal(str(item["slowk"]))
            if item.get("slowd") is not None:
                values_dict["slowd"] = Decimal(str(item["slowd"]))

            point = IndicatorDataPoint(
                date=item.get("date"),
                timestamp=item.get("datetime"),
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
