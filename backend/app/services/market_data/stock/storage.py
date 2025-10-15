"""
Stock Data Storage
MongoDB 저장 로직
"""

from typing import List, Optional
import logging

from app.models.market_data.stock import DailyPrice, WeeklyPrice, MonthlyPrice
from app.services.monitoring.data_quality_sentinel import DataQualitySentinel
from .base import BaseStockService
from .fetcher import StockFetcher

logger = logging.getLogger(__name__)


class StockStorage(BaseStockService):
    """MongoDB 저장 클래스

    Methods:
        - store_daily_prices: Daily price 저장
        - store_weekly_prices: Weekly price 저장
        - store_monthly_prices: Monthly price 저장
    """

    def __init__(
        self,
        fetcher: StockFetcher,
        data_quality_sentinel: Optional[DataQualitySentinel] = None,
    ) -> None:
        """스토리지 초기화

        Args:
            fetcher: StockFetcher 인스턴스 (API 호출용)
            data_quality_sentinel: 데이터 품질 센티널 (optional)
        """
        super().__init__(data_quality_sentinel=data_quality_sentinel)
        self.fetcher = fetcher

    async def refresh_data_from_source(self, **kwargs) -> List[DailyPrice]:
        """베이스 클래스 추상 메서드 구현 (deprecated)"""
        logger.warning("refresh_data_from_source is deprecated in StockStorage")
        return []

    async def store_daily_prices(
        self, symbol: str, adjusted: bool = True, is_full: bool = True
    ) -> List[DailyPrice]:
        """
        Alpha Vantage에서 Daily Prices를 가져와 MongoDB에 저장

        Args:
            symbol: 종목 심볼
            adjusted: True면 adjusted prices 사용 (현재는 항상 adjusted)
            is_full: True면 전체 데이터 (full), False면 최근 데이터 (compact)

        Returns:
            저장된 DailyPrice 리스트
        """
        outputsize = "full" if is_full else "compact"

        # Alpha Vantage API 호출 (fetcher 사용)
        prices = await self.fetcher.fetch_daily_prices(symbol, outputsize=outputsize)

        if not prices:
            logger.warning(f"No daily prices fetched for {symbol}")
            return []

        # MongoDB에 저장 (기존 데이터는 삭제 후 재저장)
        if is_full:
            # Full update: 기존 데이터 삭제
            delete_result = await DailyPrice.find({"symbol": symbol}).delete()
            logger.info(
                f"Deleted {delete_result.deleted_count if delete_result else 0} existing daily prices for {symbol}"
            )

        # DailyPrice 객체로 변환
        price_objects: list[DailyPrice] = []
        for price_data in prices:
            if isinstance(price_data, dict):
                price_obj = DailyPrice(**price_data)
            else:
                price_obj = price_data
            price_objects.append(price_obj)

        # 데이터 품질 센티널 실행 (가능한 경우)
        if self.data_quality_sentinel:
            try:
                await self.data_quality_sentinel.evaluate_daily_prices(
                    symbol, price_objects, source="alpha_vantage"
                )
                logger.info(
                    f"Data quality evaluation completed for {symbol} ({len(price_objects)} prices)"
                )
            except Exception as exc:
                logger.warning(
                    f"Data quality sentinel evaluation failed for {symbol}: {exc}"
                )

        # MongoDB에 Upsert (symbol + date로 unique)
        saved_prices: list[DailyPrice] = []
        for price_obj in price_objects:
            existing = await DailyPrice.find_one(
                {"symbol": price_obj.symbol, "date": price_obj.date}
            )

            if existing:
                # 기존 레코드 업데이트
                existing.open = price_obj.open
                existing.high = price_obj.high
                existing.low = price_obj.low
                existing.close = price_obj.close
                existing.volume = price_obj.volume
                existing.adjusted_close = price_obj.adjusted_close
                existing.dividend_amount = price_obj.dividend_amount
                existing.split_coefficient = price_obj.split_coefficient
                existing.data_quality_score = price_obj.data_quality_score
                existing.iso_anomaly_score = price_obj.iso_anomaly_score
                existing.prophet_anomaly_score = price_obj.prophet_anomaly_score
                existing.volume_z_score = price_obj.volume_z_score
                existing.anomaly_severity = price_obj.anomaly_severity
                existing.anomaly_reasons = price_obj.anomaly_reasons
                await existing.save()
                saved_prices.append(existing)
            else:
                # 신규 레코드 저장
                await price_obj.insert()
                saved_prices.append(price_obj)

        logger.info(
            f"✅ Stored {len(saved_prices)} daily prices for {symbol} "
            f"(adjusted={adjusted}, full={is_full})"
        )

        return saved_prices

    async def store_weekly_prices(
        self, symbol: str, adjusted: bool = True
    ) -> List[WeeklyPrice]:
        """
        Alpha Vantage에서 Weekly Prices를 가져와 MongoDB에 저장

        Args:
            symbol: 종목 심볼
            adjusted: True면 adjusted prices 사용 (현재는 항상 adjusted)

        Returns:
            저장된 WeeklyPrice 리스트
        """
        # Alpha Vantage API 호출 (항상 full)
        prices = await self.fetcher.fetch_weekly_prices(symbol, outputsize="full")

        if not prices:
            logger.warning(f"No weekly prices fetched for {symbol}")
            return []

        # MongoDB에 저장 (기존 데이터 삭제 후 재저장)
        delete_result = await WeeklyPrice.find({"symbol": symbol}).delete()
        logger.info(
            f"Deleted {delete_result.deleted_count if delete_result else 0} existing weekly prices for {symbol}"
        )

        # WeeklyPrice 객체로 변환 및 저장
        saved_prices = []
        for price_data in prices:
            if isinstance(price_data, dict):
                price_obj = WeeklyPrice(**price_data)
            else:
                price_obj = price_data

            await price_obj.insert()
            saved_prices.append(price_obj)

        logger.info(f"✅ Stored {len(saved_prices)} weekly prices for {symbol}")
        return saved_prices

    async def store_monthly_prices(
        self, symbol: str, adjusted: bool = True
    ) -> List[MonthlyPrice]:
        """
        Alpha Vantage에서 Monthly Prices를 가져와 MongoDB에 저장

        Args:
            symbol: 종목 심볼
            adjusted: True면 adjusted prices 사용 (현재는 항상 adjusted)

        Returns:
            저장된 MonthlyPrice 리스트
        """
        # Alpha Vantage API 호출 (항상 full)
        prices = await self.fetcher.fetch_monthly_prices(symbol, outputsize="full")

        if not prices:
            logger.warning(f"No monthly prices fetched for {symbol}")
            return []

        # MongoDB에 저장 (기존 데이터 삭제 후 재저장)
        delete_result = await MonthlyPrice.find({"symbol": symbol}).delete()
        logger.info(
            f"Deleted {delete_result.deleted_count if delete_result else 0} existing monthly prices for {symbol}"
        )

        # MonthlyPrice 객체로 변환 및 저장
        saved_prices = []
        for price_data in prices:
            if isinstance(price_data, dict):
                price_obj = MonthlyPrice(**price_data)
            else:
                price_obj = price_data

            await price_obj.insert()
            saved_prices.append(price_obj)

        logger.info(f"✅ Stored {len(saved_prices)} monthly prices for {symbol}")
        return saved_prices
