"""
Stock data service implementation
주식 데이터 서비스 구현
"""

from typing import List, Optional, cast
from datetime import datetime
from decimal import Decimal
import logging

from app.services.market_data_service.base_service import (
    BaseMarketDataService,
    DataQualityValidator,
)
from app.models.market_data.stock import DailyPrice


logger = logging.getLogger(__name__)


def safe_decimal(value) -> Decimal:
    """안전하게 Decimal로 변환하는 유틸리티 함수"""
    if value is None:
        return Decimal("0.0")

    # Decimal128 타입 처리 (MongoDB)
    if hasattr(value, "to_decimal"):
        return value.to_decimal()

    # MongoDB Decimal128 타입명 체크
    if type(value).__name__ == "Decimal128":
        return Decimal(str(value))

    # 이미 Decimal인 경우
    if isinstance(value, Decimal):
        return value

    # 문자열 또는 숫자인 경우
    try:
        return Decimal(str(value))
    except (ValueError, TypeError):
        logger.warning(
            f"Failed to convert {value} ({type(value)}) to Decimal, using 0.0"
        )
        return Decimal("0.0")


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
                            open=safe_decimal(item["open"]),
                            high=safe_decimal(item["high"]),
                            low=safe_decimal(item["low"]),
                            close=safe_decimal(item["close"]),
                            volume=int(item["volume"]),
                            adjusted_close=safe_decimal(
                                item.get("adjusted_close", item["close"])
                            ),
                            dividend_amount=safe_decimal(
                                item.get("dividend_amount", 0)
                            ),
                            split_coefficient=safe_decimal(
                                item.get("split_coefficient", 1)
                            ),
                            data_quality_score=95.0,  # 기본 품질 점수
                            source="alpha_vantage",
                            price_change=safe_decimal("0.0"),
                            price_change_percent=safe_decimal("0.0"),
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
                            open=safe_decimal(price_data["1. open"]),
                            high=safe_decimal(price_data["2. high"]),
                            low=safe_decimal(price_data["3. low"]),
                            close=safe_decimal(price_data["4. close"]),
                            volume=int(price_data["6. volume"]),
                            adjusted_close=safe_decimal(
                                price_data["5. adjusted close"]
                            ),
                            dividend_amount=safe_decimal(
                                price_data.get("7. dividend amount", 0)
                            ),
                            split_coefficient=safe_decimal(
                                price_data.get("8. split coefficient", 1)
                            ),
                            data_quality_score=quality_score.overall_score,
                            source="alpha_vantage",
                            price_change=safe_decimal("0.0"),
                            price_change_percent=safe_decimal("0.0"),
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
                                open=safe_decimal(price_data["1. open"]),
                                high=safe_decimal(price_data["2. high"]),
                                low=safe_decimal(price_data["3. low"]),
                                close=safe_decimal(price_data["4. close"]),
                                volume=int(price_data["6. volume"]),
                                adjusted_close=safe_decimal(
                                    price_data["5. adjusted close"]
                                ),
                                dividend_amount=safe_decimal(
                                    price_data.get("7. dividend amount", 0)
                                ),
                                split_coefficient=safe_decimal(
                                    price_data.get("8. split coefficient", 1)
                                ),
                                data_quality_score=95.0,  # 기본 품질 점수
                                source="alpha_vantage",
                                price_change=safe_decimal("0.0"),
                                price_change_percent=safe_decimal("0.0"),
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
        try:
            logger.info(f"Fetching real-time quote for {symbol}")

            response = await self.alpha_vantage.stock.quote(symbol=symbol)

            if isinstance(response, list) and len(response) > 0:
                response = response[0]  # type: ignore

            if not isinstance(response, dict) or "Global Quote" not in response:
                logger.warning(f"Invalid quote response for {symbol}")
                return {}

            quote_data = response["Global Quote"]

            # Alpha Vantage GLOBAL_QUOTE 응답을 표준 포맷으로 변환
            return {
                "symbol": quote_data.get("01. symbol", symbol),
                "price": float(quote_data.get("05. price", 0)),
                "change": float(quote_data.get("09. change", 0)),
                "change_percent": quote_data.get("10. change percent", "0%").replace(
                    "%", ""
                ),
                "volume": int(quote_data.get("06. volume", 0)),
                "latest_trading_day": quote_data.get("07. latest trading day"),
                "previous_close": float(quote_data.get("08. previous close", 0)),
                "open": float(quote_data.get("02. open", 0)),
                "high": float(quote_data.get("03. high", 0)),
                "low": float(quote_data.get("04. low", 0)),
                "timestamp": datetime.now().isoformat(),
                "source": "alpha_vantage",
            }

        except Exception as e:
            logger.error(f"Failed to fetch real-time quote for {symbol}: {e}")
            return {}

    async def get_intraday_data(
        self, symbol: str, interval: str = "5min", outputsize: str = "compact"
    ) -> dict:
        """실시간/인트라데이 데이터 조회 (Alpha Vantage TIME_SERIES_INTRADAY)"""
        try:
            logger.info(f"Fetching intraday data for {symbol} with {interval} interval")

            # type: ignore를 사용하여 타입 체크 우회
            response = await self.alpha_vantage.stock.intraday(  # type: ignore
                symbol=symbol,
                interval=interval,  # type: ignore
                outputsize=outputsize,  # type: ignore
            )

            if isinstance(response, list) and len(response) > 0:
                response = response[0]  # type: ignore

            if not isinstance(response, dict):
                logger.warning(f"Invalid intraday response for {symbol}")
                return {}

            # 메타데이터와 시계열 데이터 추출
            meta_data = response.get("Meta Data", {})
            time_series_key = f"Time Series ({interval})"
            time_series = response.get(time_series_key, {})

            # 최근 20개 데이터 포인트만 반환 (performance)
            recent_data = dict(list(time_series.items())[:20])

            return {
                "symbol": symbol,
                "interval": interval,
                "meta_data": {
                    "information": meta_data.get("1. Information"),
                    "symbol": meta_data.get("2. Symbol"),
                    "last_refreshed": meta_data.get("3. Last Refreshed"),
                    "interval": meta_data.get("4. Interval"),
                    "output_size": meta_data.get("5. Output Size"),
                    "time_zone": meta_data.get("6. Time Zone"),
                },
                "time_series": recent_data,
                "data_points": len(recent_data),
                "timestamp": datetime.now().isoformat(),
                "source": "alpha_vantage",
            }

        except Exception as e:
            logger.error(f"Failed to fetch intraday data for {symbol}: {e}")
            return {}

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

    async def search_symbols(self, keywords: str) -> dict:
        """심볼 검색 (간단한 검색 기능 제공)"""
        try:
            logger.info(f"Searching symbols for keywords: {keywords}")

            # Alpha Vantage search endpoint가 없는 경우 간단한 매칭 검색
            # 실제 구현에서는 데이터베이스나 캐시된 심볼 리스트 검색
            popular_symbols = [
                {
                    "symbol": "AAPL",
                    "name": "Apple Inc.",
                    "type": "Equity",
                    "region": "United States",
                },
                {
                    "symbol": "MSFT",
                    "name": "Microsoft Corporation",
                    "type": "Equity",
                    "region": "United States",
                },
                {
                    "symbol": "GOOGL",
                    "name": "Alphabet Inc.",
                    "type": "Equity",
                    "region": "United States",
                },
                {
                    "symbol": "AMZN",
                    "name": "Amazon.com Inc.",
                    "type": "Equity",
                    "region": "United States",
                },
                {
                    "symbol": "TSLA",
                    "name": "Tesla Inc.",
                    "type": "Equity",
                    "region": "United States",
                },
                {
                    "symbol": "META",
                    "name": "Meta Platforms Inc.",
                    "type": "Equity",
                    "region": "United States",
                },
                {
                    "symbol": "NVDA",
                    "name": "NVIDIA Corporation",
                    "type": "Equity",
                    "region": "United States",
                },
                {
                    "symbol": "JPM",
                    "name": "JPMorgan Chase & Co.",
                    "type": "Equity",
                    "region": "United States",
                },
                {
                    "symbol": "JNJ",
                    "name": "Johnson & Johnson",
                    "type": "Equity",
                    "region": "United States",
                },
                {
                    "symbol": "V",
                    "name": "Visa Inc.",
                    "type": "Equity",
                    "region": "United States",
                },
            ]

            # 키워드로 필터링
            keywords_lower = keywords.lower()
            matching_symbols = [
                symbol
                for symbol in popular_symbols
                if (
                    keywords_lower in symbol["symbol"].lower()
                    or keywords_lower in symbol["name"].lower()
                )
            ]

            return {
                "keywords": keywords,
                "symbols": matching_symbols,
                "count": len(matching_symbols),
                "timestamp": datetime.now().isoformat(),
                "source": "static_database",
            }

        except Exception as e:
            logger.error(f"Failed to search symbols for {keywords}: {e}")
            return {"symbols": [], "count": 0}
