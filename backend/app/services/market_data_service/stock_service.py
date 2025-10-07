"""
Stock data service implementation
주식 데이터 서비스 구현
"""

from datetime import datetime
from typing import List, cast
from decimal import Decimal
import logging

from app.services.market_data_service.base_service import BaseMarketDataService
from app.models.market_data.stock import DailyPrice


logger = logging.getLogger(__name__)


class StockService(BaseMarketDataService):
    """주식 데이터 서비스"""

    async def get_daily_prices(
        self,
        symbol: str,
        outputsize: str = "compact",
    ) -> List[DailyPrice]:
        """일일 주가 데이터 조회"""
        cache_key = f"daily_stock_{symbol}_{outputsize}"

        async def refresh_callback():
            return await self._fetch_daily_prices_from_alpha_vantage(symbol, outputsize)

        results = await self.get_data_with_fallback(
            cache_key=cache_key,
            model_class=DailyPrice,
            refresh_callback=refresh_callback,
        )

        # 타입 캐스팅 (실제로는 DailyPrice 객체들이 반환됨)
        return cast(List[DailyPrice], results)

    # Alpha Vantage API 호출 메서드들
    async def _fetch_daily_prices_from_alpha_vantage(
        self, symbol: str, outputsize: str = "compact"
    ) -> List[DailyPrice]:
        """Alpha Vantage에서 일일 주가 데이터 가져오기"""
        try:
            # mysingle_quant의 AlphaVantageClient 사용
            if outputsize not in ["compact", "full"]:
                outputsize = "compact"

            response = await self.alpha_vantage.stock.daily_adjusted(
                symbol=symbol,
                outputsize=outputsize,  # type: ignore
            )

            # 응답이 리스트인 경우 처리
            if isinstance(response, list) and len(response) > 0:
                response = response[0]

            # 응답 데이터를 DailyPrice 모델로 변환
            daily_prices = []
            time_series = (
                response.get("Time Series (Daily)", {})
                if isinstance(response, dict)
                else {}
            )

            for date_str, price_data in time_series.items():
                try:
                    # 데이터 품질 검증
                    quality_score = self.quality_validator.validate_price_data(
                        price_data
                    )

                    daily_price = DailyPrice(
                        symbol=symbol,
                        date=datetime.strptime(date_str, "%Y-%m-%d"),
                        open=Decimal(str(price_data["1. open"])),
                        high=Decimal(str(price_data["2. high"])),
                        low=Decimal(str(price_data["3. low"])),
                        close=Decimal(str(price_data["4. close"])),
                        volume=int(price_data["6. volume"]),
                        adjusted_close=Decimal(str(price_data["5. adjusted close"])),
                        dividend_amount=Decimal(
                            str(price_data.get("7. dividend amount", 0))
                        ),
                        split_coefficient=Decimal(
                            str(price_data.get("8. split coefficient", 1))
                        ),
                        data_quality_score=quality_score.overall_score,
                        source="alpha_vantage",
                        # 가격 변동은 나중에 계산하거나 기본값 설정
                        price_change=Decimal("0.0"),
                        price_change_percent=Decimal("0.0"),
                    )
                    daily_prices.append(daily_price)
                except (ValueError, KeyError) as e:
                    logger.warning(
                        f"Failed to parse daily price data for {date_str}: {e}"
                    )
                    continue

            logger.info(f"Fetched {len(daily_prices)} daily prices for {symbol}")
            return daily_prices

        except Exception as e:
            logger.error(f"Failed to fetch daily prices from Alpha Vantage: {e}")
            return []

    async def refresh_data_from_source(self, **kwargs) -> List[DailyPrice]:
        """베이스 클래스의 추상 메서드 구현"""
        # 이 메서드는 더 이상 직접 사용되지 않으므로 빈 구현
        return []
