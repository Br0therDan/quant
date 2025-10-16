"""
Stock Service Package
주식 서비스 - Modular Architecture

구현 완료:
- ✅ base.py: BaseStockService (공통 로직)
- ✅ fetcher.py: StockFetcher (Alpha Vantage API 호출)
- ✅ storage.py: StockStorage (MongoDB 저장)
- ✅ coverage.py: CoverageManager (Coverage 메타데이터)
- ✅ cache.py: StockCacheManager (DuckDB 캐싱)
- ✅ __init__.py: StockService (Full delegation pattern)
"""

from typing import List, Literal, Optional, cast
from datetime import datetime, timezone
import logging

from app.services.database_manager import DatabaseManager
from app.services.monitoring.data_quality_sentinel import DataQualitySentinel
from app.models.market_data.stock import (
    DailyPrice,
    WeeklyPrice,
    MonthlyPrice,
)
from app.schemas.market_data.stock import QuoteData

from .base import BaseStockService
from .fetcher import StockFetcher
from .storage import StockStorage
from .coverage import CoverageManager
from .cache import StockCacheManager

logger = logging.getLogger(__name__)


class StockService(BaseStockService):
    """주식 데이터 서비스 (Modular Architecture)

    Delegation Pattern으로 각 모듈에 책임 분리:
    - fetcher: Alpha Vantage API 호출
    - storage: MongoDB 저장
    - coverage: Coverage 메타데이터 관리
    - cache: DuckDB 캐싱
    """

    def __init__(
        self,
        database_manager: Optional[DatabaseManager] = None,
        data_quality_sentinel: Optional[DataQualitySentinel] = None,
    ) -> None:
        """서비스 초기화

        Args:
            database_manager: DuckDB 캐시 매니저
            data_quality_sentinel: 데이터 품질 센티널
        """
        super().__init__(database_manager, data_quality_sentinel)

        # 모듈 초기화 (delegation)
        self._fetcher = StockFetcher(database_manager, data_quality_sentinel)
        self._storage = StockStorage(self._fetcher, data_quality_sentinel)
        self._coverage = CoverageManager(database_manager, data_quality_sentinel)
        self._cache = StockCacheManager(database_manager)

    # ==================== Public API Methods ====================

    async def get_daily_prices(
        self,
        symbol: str,
        outputsize: str = "compact",
        adjusted: bool = True,
    ) -> List[DailyPrice]:
        """일일 주가 데이터 조회 (Coverage 기반 캐싱)

        Args:
            symbol: 종목 심볼
            outputsize: 'compact' (최근 100개) 또는 'full' (전체 데이터)
            adjusted: True면 adjusted prices (현재는 항상 adjusted)

        Returns:
            DailyPrice 리스트
        """
        # Coverage 확인
        coverage = await self._coverage.get_or_create_coverage(symbol, "daily")

        # Full update가 필요한지 확인 (최초 또는 7일 이상 경과)
        needs_full_update = (
            coverage.last_full_update is None
            or (datetime.now(timezone.utc) - coverage.last_full_update).days >= 7
        )

        # MongoDB에서 기존 데이터 조회
        existing_prices = (
            await DailyPrice.find({"symbol": symbol}).sort("-date").to_list()
        )

        # 데이터가 없거나 Full update가 필요한 경우만 API 호출
        if not existing_prices or needs_full_update:
            logger.info(
                f"🔄 Performing full update for {symbol} daily prices "
                f"(existing: {len(existing_prices)}, needs_full: {needs_full_update})"
            )

            # Storage 모듈로 fetch & store
            prices = await self._storage.store_daily_prices(
                symbol, adjusted=adjusted, is_full=True
            )

            # Coverage 업데이트
            if prices:
                await self._coverage.update_coverage(
                    coverage=coverage, data_records=prices, update_type="full"
                )
            return prices or []
        else:
            logger.info(
                f"✅ Using cached data for {symbol} daily prices "
                f"({len(existing_prices)} records, last_update: {coverage.last_full_update})"
            )
            return existing_prices

    async def get_weekly_prices(
        self,
        symbol: str,
        outputsize: str = "full",  # outputsize는 사용되지 않음 (항상 full)
        adjusted: bool = True,
    ) -> List[WeeklyPrice]:
        """주간 주가 데이터 조회 (Coverage 기반 캐싱)

        Args:
            symbol: 종목 심볼
            outputsize: 사용되지 않음 (항상 full)
            adjusted: True면 adjusted prices (현재는 항상 adjusted)

        Returns:
            WeeklyPrice 리스트
        """
        # Coverage 확인
        coverage = await self._coverage.get_or_create_coverage(symbol, "weekly")

        # Full update가 필요한지 확인 (최초 또는 30일 이상 경과)
        needs_full_update = (
            coverage.last_full_update is None
            or (datetime.now(timezone.utc) - coverage.last_full_update).days >= 30
        )

        if needs_full_update:
            logger.info(f"🔄 Performing full update for {symbol} weekly prices")

            # Storage 모듈로 fetch & store
            prices = await self._storage.store_weekly_prices(symbol, adjusted=adjusted)

            # Coverage 업데이트
            if prices:
                await self._coverage.update_coverage(coverage, prices, "full")
        else:
            logger.info(
                f"✅ Using cached data for {symbol} weekly prices "
                f"(last_update: {coverage.last_full_update})"
            )
            prices = await WeeklyPrice.find({"symbol": symbol}).sort("-date").to_list()

        return prices or []

    async def get_monthly_prices(
        self,
        symbol: str,
        outputsize: str = "full",  # outputsize는 사용되지 않음 (항상 full)
        adjusted: bool = True,
    ) -> List[MonthlyPrice]:
        """월간 주가 데이터 조회 (Coverage 기반 캐싱)

        Args:
            symbol: 종목 심볼
            outputsize: 사용되지 않음 (항상 full)
            adjusted: True면 adjusted prices (현재는 항상 adjusted)

        Returns:
            MonthlyPrice 리스트
        """
        # Coverage 확인
        coverage = await self._coverage.get_or_create_coverage(symbol, "monthly")

        # Full update가 필요한지 확인 (최초 또는 60일 이상 경과)
        needs_full_update = (
            coverage.last_full_update is None
            or (datetime.now(timezone.utc) - coverage.last_full_update).days >= 60
        )

        if needs_full_update:
            logger.info(f"🔄 Performing full update for {symbol} monthly prices")

            # Storage 모듈로 fetch & store
            prices = await self._storage.store_monthly_prices(symbol, adjusted=adjusted)

            # Coverage 업데이트
            if prices:
                await self._coverage.update_coverage(coverage, prices, "full")
        else:
            logger.info(
                f"✅ Using cached data for {symbol} monthly prices "
                f"(last_update: {coverage.last_full_update})"
            )
            prices = await MonthlyPrice.find({"symbol": symbol}).sort("-date").to_list()

        return prices or []

    async def get_real_time_quote(
        self, symbol: str, force_refresh: bool = False
    ) -> QuoteData:
        """실시간 주식 호가 조회 (Alpha Vantage GLOBAL_QUOTE)

        Args:
            symbol: 주식 심볼
            force_refresh: True인 경우 캐시 무시하고 실시간 데이터 조회

        Returns:
            QuoteData: 실시간 호가 정보 객체
        """
        if force_refresh:
            logger.info(f"Force refresh requested for {symbol} quote")
            return await self._fetcher.fetch_quote(symbol)

        # 매우 짧은 TTL로 캐시 적용
        cache_key = f"realtime_quote_{symbol.upper()}"

        async def refresh_callback():
            return [await self._fetcher.fetch_quote(symbol)]

        try:
            # 실시간 데이터는 리스트 형태로 캐시 저장
            results = await self.get_data_with_unified_cache(
                cache_key=cache_key,
                model_class=dict,
                data_type="realtime_quote",
                symbol=symbol,
                refresh_callback=refresh_callback,
                ttl_hours=1,
            )

            # 첫 번째 요소 반환 (단일 호가 데이터)
            if results and len(results) > 0:
                result = results[0]
                # dict인 경우 QuoteData로 변환
                if isinstance(result, dict):
                    return QuoteData(**result)
                return result
            else:
                return await self._fetcher.fetch_quote(symbol)

        except Exception as e:
            logger.warning(f"Error with cached quote for {symbol}: {e}")
            return await self._fetcher.fetch_quote(symbol)

    async def get_intraday_data(
        self,
        symbol: str,
        interval: Literal["1min", "5min", "15min", "30min", "60min"] = "15min",
        adjusted: bool = False,
        extended_hours: bool = False,
        outputsize: Literal["compact", "full"] | None = "full",
        month: Optional[str] = None,
    ) -> List[DailyPrice]:
        """실시간/인트라데이 데이터 조회 (Alpha Vantage TIME_SERIES_INTRADAY)

        Args:
            symbol: 주식 심볼
            interval: 데이터 간격 (1min, 5min, 15min, 30min, 60min)
            adjusted: 조정된 가격 사용 여부
            extended_hours: 장외 시간 포함 여부
            outputsize: 출력 크기 (compact: 100 data points, full: 30 days or full month)
            month: 조회할 월 (YYYY-MM 형식, Premium plan only)

        Returns:
            인트라데이 가격 데이터 리스트
        """
        # 인터벌에 따른 적절한 TTL 설정
        interval_ttl_mapping = {
            "1min": 1,
            "5min": 2,
            "15min": 4,
            "30min": 6,
            "60min": 12,
        }

        ttl_hours = interval_ttl_mapping.get(interval, 4)
        cache_key = f"intraday_{symbol}_{interval}_{adjusted}_{extended_hours}_{outputsize}_{month or 'latest'}"

        async def refresh_callback():
            return await self._fetcher.fetch_intraday(
                symbol, interval, adjusted, extended_hours, outputsize, month
            )

        results = await self.get_data_with_unified_cache(
            cache_key=cache_key,
            model_class=DailyPrice,
            data_type="stock_intraday",
            symbol=symbol,
            refresh_callback=refresh_callback,
            ttl_hours=ttl_hours,
        )

        return cast(List[DailyPrice], results)

    async def get_historical_data(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> dict:
        """장기 히스토리 데이터 조회 (Alpha Vantage TIME_SERIES_DAILY_ADJUSTED)

        Args:
            symbol: 주식 심볼
            start_date: 시작 날짜
            end_date: 종료 날짜

        Returns:
            히스토리 데이터 딕셔너리
        """
        return await self._fetcher.fetch_historical(symbol, start_date, end_date)

    async def search_symbols(self, keywords: str) -> dict:
        """심볼 검색 (Alpha Vantage SYMBOL_SEARCH API 호출)

        Args:
            keywords: 검색 키워드

        Returns:
            검색 결과 딕셔너리 ({"bestMatches": [...]})
        """
        return await self._fetcher.search_symbols(keywords)

    # ==================== BaseMarketDataService 추상 메서드 구현 ====================

    async def refresh_data_from_source(self, **kwargs) -> List[DailyPrice]:
        """베이스 클래스의 추상 메서드 구현 (deprecated)"""
        logger.warning("refresh_data_from_source is deprecated, use specific methods")
        return []

    async def _fetch_from_source(self, **kwargs):
        """Alpha Vantage에서 주식 데이터 가져오기 (CacheManager로 위임)"""
        return await self._cache._fetch_from_source(**kwargs)

    async def _save_to_cache(self, data, **kwargs) -> bool:
        """주식 데이터를 캐시에 저장 (CacheManager로 위임)"""
        return await self._cache._save_to_cache(data, **kwargs)

    async def _get_from_cache(self, **kwargs):
        """캐시에서 주식 데이터 조회 (CacheManager로 위임)"""
        return await self._cache._get_from_cache(**kwargs)


__all__ = [
    "StockService",
    "BaseStockService",
    "StockFetcher",
    "StockStorage",
    "CoverageManager",
    "StockCacheManager",
]
