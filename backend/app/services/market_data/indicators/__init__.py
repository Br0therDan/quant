"""
Technical Indicator Service Package
기술적 지표 서비스 패키지 - 통합 인터페이스

이 패키지는 기술적 지표를 카테고리별로 분리하여 관리합니다:
- base: 공통 로직 (캐싱, 메타데이터 저장)
- trend: 추세 지표 (SMA, EMA, WMA, DEMA, TEMA)
- momentum: 모멘텀 지표 (RSI, MACD, STOCH)
- volatility: 변동성 지표 (BBANDS, ATR, ADX)

TechnicalIndicatorService 클래스는 모든 지표를 통합하여 제공하며,
기존 코드와 100% 호환됩니다 (delegation pattern).
"""

from typing import Optional, Dict, List, Literal

from app.services.database_manager import DatabaseManager
from app.schemas.market_data.technical_indicator import TechnicalIndicatorData

from .trend import TrendIndicatorService
from .momentum import MomentumIndicatorService
from .volatility import VolatilityIndicatorService


class TechnicalIndicatorService:
    """기술적 지표 서비스 통합 인터페이스

    기존 technical_indicator.py와 100% 호환되는 인터페이스를 제공합니다.
    내부적으로 카테고리별 서비스로 위임(delegation)하여 처리합니다.

    Usage:
        service = TechnicalIndicatorService()
        sma_data = await service.get_sma("AAPL", interval="daily", time_period=20)
        rsi_data = await service.get_rsi("AAPL", interval="daily", time_period=14)
    """

    def __init__(self, database_manager: Optional[DatabaseManager] = None):
        """서비스 초기화

        Args:
            database_manager: DuckDB 캐시 매니저 (optional)
        """
        self._trend_service = TrendIndicatorService(database_manager)
        self._momentum_service = MomentumIndicatorService(database_manager)
        self._volatility_service = VolatilityIndicatorService(database_manager)

    # ========== Trend Indicators (추세 지표) ==========

    async def get_sma(
        self,
        symbol: str,
        interval: Literal[
            "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
        ] = "daily",
        time_period: int = 20,
        series_type: Literal["close", "open", "high", "low"] = "close",
    ) -> TechnicalIndicatorData:
        """단순이동평균(SMA) 조회"""
        return await self._trend_service.get_sma(
            symbol, interval, time_period, series_type
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
        """지수이동평균(EMA) 조회"""
        return await self._trend_service.get_ema(
            symbol, interval, time_period, series_type
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
        """가중이동평균(WMA) 조회"""
        return await self._trend_service.get_wma(
            symbol, interval, time_period, series_type
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
        """이중지수이동평균(DEMA) 조회"""
        return await self._trend_service.get_dema(
            symbol, interval, time_period, series_type
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
        """삼중지수이동평균(TEMA) 조회"""
        return await self._trend_service.get_tema(
            symbol, interval, time_period, series_type
        )

    # ========== Momentum Indicators (모멘텀 지표) ==========

    async def get_rsi(
        self,
        symbol: str,
        interval: Literal[
            "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
        ] = "daily",
        time_period: int = 14,
        series_type: Literal["close", "open", "high", "low"] = "close",
    ) -> TechnicalIndicatorData:
        """상대강도지수(RSI) 조회"""
        return await self._momentum_service.get_rsi(
            symbol, interval, time_period, series_type
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
        """MACD 조회"""
        return await self._momentum_service.get_macd(
            symbol, interval, series_type, fastperiod, slowperiod, signalperiod
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
        """스토캐스틱 오실레이터(STOCH) 조회"""
        return await self._momentum_service.get_stoch(
            symbol,
            interval,
            fastkperiod,
            slowkperiod,
            slowdperiod,
            slowkmatype,
            slowdmatype,
        )

    # ========== Volatility Indicators (변동성 지표) ==========

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
        """볼린저밴드(BBANDS) 조회"""
        return await self._volatility_service.get_bbands(
            symbol, interval, time_period, series_type, nbdevup, nbdevdn
        )

    async def get_atr(
        self,
        symbol: str,
        interval: Literal[
            "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
        ] = "daily",
        time_period: int = 14,
    ) -> TechnicalIndicatorData:
        """평균진폭(ATR) 조회"""
        return await self._volatility_service.get_atr(symbol, interval, time_period)

    async def get_adx(
        self,
        symbol: str,
        interval: Literal[
            "1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"
        ] = "daily",
        time_period: int = 14,
    ) -> TechnicalIndicatorData:
        """평균방향지수(ADX) 조회"""
        return await self._volatility_service.get_adx(symbol, interval, time_period)

    # ========== Utility Methods ==========

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


# Export for backward compatibility
__all__ = [
    "TechnicalIndicatorService",
    "TrendIndicatorService",
    "MomentumIndicatorService",
    "VolatilityIndicatorService",
]
