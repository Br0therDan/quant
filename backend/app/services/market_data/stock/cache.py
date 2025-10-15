"""
Stock Data Cache Manager
DuckDB 캐싱 로직 (BaseMarketDataService 추상 메서드 구현)
"""

from typing import Any, Optional
from datetime import datetime
from decimal import Decimal
import logging

from app.models.market_data.stock import DailyPrice
from app.services.database_manager import DatabaseManager
from .base import BaseStockService

logger = logging.getLogger(__name__)


class StockCacheManager(BaseStockService):
    """DuckDB 캐시 관리 클래스

    BaseMarketDataService의 추상 메서드 구현:
        - refresh_data_from_source: Deprecated
        - _fetch_from_source: Alpha Vantage API 호출
        - _save_to_cache: DuckDB에 저장
        - _get_from_cache: DuckDB에서 조회
    """

    def __init__(self, database_manager: Optional[DatabaseManager] = None) -> None:
        """캐시 매니저 초기화

        Args:
            database_manager: DuckDB 캐시 매니저
        """
        super().__init__(database_manager=database_manager)

    async def refresh_data_from_source(self, **kwargs) -> list[DailyPrice]:
        """베이스 클래스 추상 메서드 구현 (deprecated)"""
        logger.warning("refresh_data_from_source is deprecated in StockCacheManager")
        return []

    async def _fetch_from_source(self, **kwargs) -> Any:
        """Alpha Vantage에서 주식 데이터 가져오기 (BaseMarketDataService 구현)

        Args:
            **kwargs: API 호출 파라미터
                - method: API 메서드 (daily, quote, intraday)
                - symbol: 종목 심볼
                - outputsize: 출력 크기 (compact, full)
                - interval: 인트라데이 간격 (1min, 5min, etc.)

        Returns:
            Alpha Vantage API 응답 데이터

        Raises:
            ValueError: symbol이 없거나 method가 유효하지 않을 때
        """
        try:
            method = kwargs.get("method", "daily")
            symbol = kwargs.get("symbol")

            if not symbol:
                raise ValueError("Symbol is required for stock data")

            if method == "daily":
                outputsize = kwargs.get("outputsize", "compact")
                return await self.alpha_vantage.stock.daily_adjusted(
                    symbol=symbol, outputsize=outputsize
                )
            elif method == "quote":
                return await self.alpha_vantage.stock.quote(symbol=symbol)
            elif method == "intraday":
                interval = kwargs.get("interval", "5min")
                outputsize = kwargs.get("outputsize", "compact")
                return await self.alpha_vantage.stock.intraday(
                    symbol=symbol, interval=interval, outputsize=outputsize
                )
            else:
                raise ValueError(f"Unknown stock method: {method}")

        except Exception as e:
            logger.error(f"Error fetching stock data from source: {e}")
            raise

    async def _save_to_cache(self, data: Any, **kwargs) -> bool:
        """주식 데이터를 DuckDB 캐시에 저장 (BaseMarketDataService 구현)

        Args:
            data: 저장할 데이터 (Alpha Vantage 응답)
            **kwargs: 캐시 저장 옵션
                - cache_key: 캐시 키
                - method: API 메서드
                - symbol: 종목 심볼

        Returns:
            성공 여부
        """
        try:
            cache_key = kwargs.get("cache_key", "stock_data")
            method = kwargs.get("method", "daily")
            symbol = kwargs.get("symbol", "UNKNOWN")

            # 데이터를 DailyPrice 모델로 변환 (daily 메서드만 지원)
            if isinstance(data, dict) and method == "daily":
                try:
                    # Alpha Vantage 응답에서 Time Series 추출
                    time_series = data.get("Time Series (Daily)", {})
                    if not time_series:
                        logger.warning(f"No time series data found for {symbol}")
                        return True

                    daily_prices = []
                    for date_str, price_data in time_series.items():
                        try:
                            # date 객체를 datetime으로 변환
                            date_obj = datetime.strptime(date_str, "%Y-%m-%d")

                            daily_price = DailyPrice(
                                symbol=symbol,
                                date=date_obj,
                                open=Decimal(str(price_data["1. open"])),
                                high=Decimal(str(price_data["2. high"])),
                                low=Decimal(str(price_data["3. low"])),
                                close=Decimal(str(price_data["4. close"])),
                                volume=int(price_data["6. volume"]),
                                adjusted_close=Decimal(
                                    str(price_data["5. adjusted close"])
                                ),
                                dividend_amount=Decimal(
                                    str(price_data.get("7. dividend amount", 0))
                                ),
                                split_coefficient=Decimal(
                                    str(price_data.get("8. split coefficient", 1))
                                ),
                                data_quality_score=95.0,  # 기본 품질 점수
                                source="alpha_vantage",
                                price_change=Decimal("0.0"),
                                price_change_percent=Decimal("0.0"),
                                # Anomaly 필드 (기본값)
                                iso_anomaly_score=0.0,
                                prophet_anomaly_score=0.0,
                                volume_z_score=0.0,
                                anomaly_severity=None,
                                anomaly_reasons=[],
                            )
                            daily_prices.append(daily_price)
                        except (ValueError, KeyError) as parse_error:
                            logger.warning(
                                f"Failed to parse price data for {date_str}: {parse_error}"
                            )
                            continue

                    if daily_prices:
                        # DuckDB 캐시에 저장
                        success = await self._store_to_duckdb_cache(
                            cache_key=cache_key,
                            data=daily_prices,
                            table_name="stock_cache",
                        )

                        if success:
                            logger.info(
                                f"Stock data cached successfully: {cache_key} ({len(daily_prices)} items)"
                            )
                        return success

                except Exception as model_error:
                    logger.warning(f"Failed to create DailyPrice models: {model_error}")
                    # 원본 데이터를 딕셔너리로 저장
                    if self._db_manager:
                        return self._db_manager.store_cache_data(
                            cache_key=cache_key, data=[data], table_name="stock_cache"
                        )

            logger.debug(f"No valid stock data to cache for: {cache_key}")
            return True

        except Exception as e:
            logger.error(f"Error saving stock data to cache: {e}")
            return False

    async def _get_from_cache(self, **kwargs) -> Optional[Any]:
        """DuckDB 캐시에서 주식 데이터 조회 (BaseMarketDataService 구현)

        Args:
            **kwargs: 캐시 조회 옵션
                - cache_key: 캐시 키
                - start_date: 시작 날짜
                - end_date: 종료 날짜
                - ignore_ttl: TTL 무시 여부

        Returns:
            캐시된 데이터 (없으면 None)
        """
        try:
            cache_key = kwargs.get("cache_key", "stock_data")

            # DuckDB 캐시에서 데이터 조회
            cached_data = await self._get_from_duckdb_cache(
                cache_key=cache_key,
                start_date=kwargs.get("start_date"),
                end_date=kwargs.get("end_date"),
                ignore_ttl=kwargs.get("ignore_ttl", False),
            )

            if cached_data:
                logger.info(f"Stock cache hit: {cache_key} ({len(cached_data)} items)")
                return cached_data
            else:
                logger.debug(f"Stock cache miss: {cache_key}")
                return None

        except Exception as e:
            logger.error(f"Error getting stock data from cache: {e}")
            return None
