"""
Stock data service implementation
주식 데이터 서비스 구현
"""

from typing import List, Literal, Optional, cast
from datetime import datetime
from decimal import Decimal
import logging

from app.services.market_data_service.base_service import (
    BaseMarketDataService,
    DataQualityValidator,
)
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
                symbol=symbol, outputsize=outputsize  # type: ignore
            )

            # 응답 데이터 구조 로깅
            logger.info(f"Alpha Vantage response type: {type(response)}")

            # mysingle_quant 클라이언트가 이미 파싱된 리스트를 반환하는 경우
            if isinstance(response, list):
                logger.info(f"Response is list with {len(response)} items")
                daily_prices = []

                for item in response:
                    if not isinstance(item, dict):
                        continue

                    try:
                        # 데이터 품질 확인 (간단한 검증)
                        required_fields = [
                            "date",
                            "open",
                            "high",
                            "low",
                            "close",
                            "volume",
                        ]
                        if not all(field in item for field in required_fields):
                            logger.warning(
                                f"Missing required fields in item: {item.keys()}"
                            )
                            continue

                        # date 처리 - 문자열 또는 datetime 객체 모두 처리
                        date_value = item["date"]
                        if isinstance(date_value, str):
                            date_obj = datetime.strptime(date_value, "%Y-%m-%d")
                        elif isinstance(date_value, datetime):
                            date_obj = date_value
                        else:
                            logger.warning(f"Unexpected date type: {type(date_value)}")
                            continue

                        daily_price = DailyPrice(
                            symbol=symbol,
                            date=date_obj,
                            open=Decimal(str(item["open"])),
                            high=Decimal(str(item["high"])),
                            low=Decimal(str(item["low"])),
                            close=Decimal(str(item["close"])),
                            volume=int(item["volume"]),
                            adjusted_close=Decimal(
                                str(item.get("adjusted_close", item["close"]))
                            ),
                            dividend_amount=Decimal(
                                str(item.get("dividend_amount", 0))
                            ),
                            split_coefficient=Decimal(
                                str(item.get("split_coefficient", 1))
                            ),
                            data_quality_score=95.0,
                            source="alpha_vantage",
                            price_change=Decimal("0.0"),
                            price_change_percent=Decimal("0.0"),
                        )
                        daily_prices.append(daily_price)

                    except (ValueError, KeyError) as e:
                        logger.warning(f"Failed to parse daily price data: {e}")
                        continue

                logger.info(f"Fetched {len(daily_prices)} daily prices for {symbol}")
                return daily_prices

            # 기존 딕셔너리 구조 처리 (fallback)
            elif isinstance(response, dict):
                logger.info(f"Response is dict with keys: {list(response.keys())}")

                # Time Series 키를 확인
                available_keys = list(response.keys())
                time_series_key = None
                for key in available_keys:
                    if "time series" in key.lower() or "daily" in key.lower():
                        time_series_key = key
                        break

                if not time_series_key:
                    logger.warning(
                        f"No time series data found for {symbol}. Available keys: {available_keys}"
                    )
                    return []

                time_series = response.get(time_series_key, {})
                if not isinstance(time_series, dict):
                    logger.warning(
                        f"Invalid time series data type: {type(time_series)}"
                    )
                    return []

                daily_prices = []

                # 타입 캐스팅을 통해 타입 체크 우회
                time_series_dict = cast(dict, time_series)
                for date_str, price_data in time_series_dict.items():
                    try:
                        # 데이터 품질 확인
                        quality_score = DataQualityValidator.validate_price_data(
                            price_data
                        )

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
                            data_quality_score=quality_score.overall_score,
                            source="alpha_vantage",
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

            else:
                logger.warning(
                    f"Unexpected response type for {symbol}: {type(response)}"
                )
                return []

        except Exception as e:
            logger.error(f"Failed to fetch daily prices from Alpha Vantage: {e}")
            return []

    async def refresh_data_from_source(self, **kwargs) -> List[DailyPrice]:
        """베이스 클래스의 추상 메서드 구현"""
        # 이 메서드는 더 이상 직접 사용되지 않으므로 빈 구현
        return []

    # BaseMarketDataService 추상 메서드 구현
    async def _fetch_from_source(self, **kwargs):
        """Alpha Vantage에서 주식 데이터 가져오기"""
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

    async def _save_to_cache(self, data, **kwargs) -> bool:
        """주식 데이터를 캐시에 저장"""
        try:
            cache_key = kwargs.get("cache_key", "stock_data")
            method = kwargs.get("method", "daily")
            symbol = kwargs.get("symbol", "UNKNOWN")

            # 데이터를 DailyPrice 모델로 변환
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

            logger.info(f"No valid stock data to cache for: {cache_key}")
            return True

        except Exception as e:
            logger.error(f"Error saving stock data to cache: {e}")
            return False

    async def _get_from_cache(self, **kwargs):
        """캐시에서 주식 데이터 조회"""
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

    async def get_real_time_quote(self, symbol: str) -> dict:
        """실시간 주식 호가 조회 (Alpha Vantage GLOBAL_QUOTE)"""

        response = await self.alpha_vantage.stock.quote(symbol=symbol)
        """
        TODO: Duckdb 캐싱적용
        응답예시
        {
            "symbol": "IBM",
            "open": 295.55,
            "high": 301.0425,
            "low": 293.285,
            "price": 293.87,
            "volume": 7190126,
            "latest_trading_day": "2025-10-07",
            "previous_close": 289.42,
            "change": 4.45,
            "change_percent": "1.5376%"
        }
        """
        return response

    async def get_intraday_data(
        self,
        symbol: str,
        interval: Literal["1min", "5min", "15min", "30min", "60min"] = "15min",
        adjusted: bool = False,
        extended_hours: bool = False,
        outputsize: Literal["compact", "full"] | None = "full",
    ):
        """실시간/인트라데이 데이터 조회 (Alpha Vantage TIME_SERIES_INTRADAY)"""
        response = await self.alpha_vantage.stock.intraday(
            symbol=symbol,
            interval=interval,
            adjusted=adjusted,
            extended_hours=extended_hours,
            outputsize=outputsize,
        )
        return response

    async def get_historical_data(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> dict:
        """장기 히스토리 데이터 조회 (Alpha Vantage TIME_SERIES_DAILY_ADJUSTED)"""
        try:
            logger.info(f"Fetching historical data for {symbol}")

            # Alpha Vantage daily adjusted 데이터 호출 (full outputsize)
            response = await self.alpha_vantage.stock.daily_adjusted(
                symbol=symbol, outputsize="full"  # type: ignore
            )

            if isinstance(response, list) and len(response) > 0:
                response = response[0]  # type: ignore

            if not isinstance(response, dict) or "Time Series (Daily)" not in response:
                logger.warning(f"Invalid historical response for {symbol}")
                return {}

            meta_data = response.get("Meta Data", {})
            time_series = response.get("Time Series (Daily)", {})

            # 날짜 필터링 (start_date, end_date가 주어진 경우)
            filtered_data = {}
            for date_str, data in time_series.items():
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")

                    # 날짜 범위 필터링
                    if start_date and date_obj < start_date:
                        continue
                    if end_date and date_obj > end_date:
                        continue

                    filtered_data[date_str] = data

                except ValueError:
                    continue

            return {
                "symbol": symbol,
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
                "meta_data": {
                    "information": meta_data.get("1. Information"),
                    "symbol": meta_data.get("2. Symbol"),
                    "last_refreshed": meta_data.get("3. Last Refreshed"),
                    "output_size": meta_data.get("4. Output Size"),
                    "time_zone": meta_data.get("5. Time Zone"),
                },
                "time_series": filtered_data,
                "data_points": len(filtered_data),
                "timestamp": datetime.now().isoformat(),
                "source": "alpha_vantage",
            }

        except Exception as e:
            logger.error(f"Failed to fetch historical data for {symbol}: {e}")
            return {}

    async def search_symbols(self, keywords: str):
        """심볼 검색 (Alpha Vantage SYMBOL_SEARCH API 호출)"""
        try:
            logger.info(f"Searching symbols for keywords: {keywords}")

            # Alpha Vantage SYMBOL_SEARCH API 호출
            response = await self.alpha_vantage.stock.search(keywords=keywords)

            # 응답 데이터 로깅
            logger.info(f"Search response type: {type(response)}")

            # Alpha Vantage 응답은 {"bestMatches": [...]} 형태
            if isinstance(response, dict) and "bestMatches" in response:
                best_matches = response.get("bestMatches", [])
                logger.info(f"Found {len(best_matches)} search results")
                return response
            else:
                logger.warning(f"Unexpected response format: {response}")
                return {"bestMatches": []}

        except Exception as e:
            logger.error(f"Failed to search symbols for {keywords}: {e}")
            return {"bestMatches": []}

    # async def get_available_symbols(self) -> List[str]:
    #     try:
    #         response = self.db_manager.get_available_symbols()
    #         return response
    #     except Exception as e:
    #         logger.error(f"Failed to get available symbols: {e}")
    #         return []
