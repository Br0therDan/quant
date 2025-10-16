"""
Stock Data Fetcher
Alpha Vantage API 호출 로직
"""

from typing import List, Literal, Optional, cast
from datetime import datetime
from decimal import Decimal
import logging

from app.models.market_data.stock import DailyPrice, WeeklyPrice, MonthlyPrice
from app.services.market_data.base_service import DataQualityValidator
from app.schemas.market_data.stock import QuoteData
from .base import BaseStockService

logger = logging.getLogger(__name__)


class StockFetcher(BaseStockService):
    """Alpha Vantage API 호출 클래스

    Methods:
        - fetch_daily_prices: Daily price 조회
        - fetch_weekly_prices: Weekly price 조회
        - fetch_monthly_prices: Monthly price 조회
        - fetch_quote: Real-time quote 조회
        - fetch_intraday: Intraday data 조회
        - search_symbols: Symbol 검색
    """

    async def refresh_data_from_source(self, **kwargs) -> List[DailyPrice]:
        """베이스 클래스 추상 메서드 구현 (deprecated)"""
        logger.warning("refresh_data_from_source is deprecated in StockFetcher")
        return []

    async def fetch_daily_prices(
        self, symbol: str, outputsize: str = "compact"
    ) -> List[DailyPrice]:
        """Alpha Vantage에서 일일 주가 데이터 가져오기

        Args:
            symbol: 주식 심볼
            outputsize: 'compact' (최근 100개) 또는 'full' (전체)

        Returns:
            DailyPrice 리스트 (dict 형태 포함)
        """
        try:
            # 심볼 유효성 검사
            symbol = self._validate_symbol(symbol)

            if outputsize not in ["compact", "full"]:
                outputsize = "compact"

            logger.info(f"Alpha Vantage API 호출 시작: {symbol}, outputsize={outputsize}")

            response = await self.alpha_vantage.stock.daily_adjusted(
                symbol=symbol,
                outputsize=outputsize,  # type: ignore
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

                        # dict로 저장 (Beanie 모델 초기화 문제 회피)
                        daily_price_dict = {
                            "symbol": symbol,
                            "date": date_obj,
                            "open": Decimal(str(item["open"])),
                            "high": Decimal(str(item["high"])),
                            "low": Decimal(str(item["low"])),
                            "close": Decimal(str(item["close"])),
                            "volume": int(item["volume"]),
                            "adjusted_close": Decimal(
                                str(item.get("adjusted_close", item["close"]))
                            ),
                            "dividend_amount": Decimal(
                                str(item.get("dividend_amount", 0))
                            ),
                            "split_coefficient": Decimal(
                                str(item.get("split_coefficient", 1))
                            ),
                            "data_quality_score": 95.0,
                            "source": "alpha_vantage",
                            "price_change": Decimal("0.0"),
                            "price_change_percent": Decimal("0.0"),
                        }
                        daily_prices.append(daily_price_dict)

                    except (ValueError, KeyError) as e:
                        logger.warning(f"Failed to parse daily price data: {e}")
                        continue

                logger.info(f"Fetched {len(daily_prices)} daily prices for {symbol}")
                return daily_prices  # type: ignore

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
                            # Provide default anomaly-related fields required by the model
                            iso_anomaly_score=0.0,
                            prophet_anomaly_score=0.0,
                            volume_z_score=0.0,
                            anomaly_severity=None,
                            anomaly_reasons=[],
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
            import traceback

            logger.error(f"Failed to fetch daily prices from Alpha Vantage: {e}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []

    async def fetch_weekly_prices(
        self, symbol: str, outputsize: str = "full"
    ) -> List[WeeklyPrice]:
        """Alpha Vantage에서 주간 주가 데이터 가져오기

        Args:
            symbol: 주식 심볼
            outputsize: 'compact' 또는 'full' (기본: full)

        Returns:
            WeeklyPrice 리스트
        """
        try:
            symbol = self._validate_symbol(symbol)

            if outputsize not in ["compact", "full"]:
                outputsize = "full"

            response = await self.alpha_vantage.stock.weekly_adjusted(
                symbol=symbol, outputsize=cast(Literal["compact", "full"], outputsize)
            )

            if isinstance(response, list):
                logger.info(f"Response is list with {len(response)} items")
                weekly_prices = []

                for item in response:
                    if not isinstance(item, dict):
                        continue

                    try:
                        required_fields = [
                            "date",
                            "open",
                            "high",
                            "low",
                            "close",
                            "volume",
                        ]
                        if not all(field in item for field in required_fields):
                            continue

                        # date 처리
                        date_value = item["date"]
                        if isinstance(date_value, str):
                            date_obj = datetime.strptime(date_value, "%Y-%m-%d")
                        elif isinstance(date_value, datetime):
                            date_obj = date_value
                        else:
                            continue

                        weekly_price = WeeklyPrice(
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
                        )
                        weekly_prices.append(weekly_price)

                    except (ValueError, KeyError) as e:
                        logger.warning(f"Failed to parse weekly price data: {e}")
                        continue

                logger.info(f"Fetched {len(weekly_prices)} weekly prices for {symbol}")
                return weekly_prices

            else:
                logger.warning(
                    f"Unexpected response type for {symbol}: {type(response)}"
                )
                return []

        except Exception as e:
            logger.error(f"Failed to fetch weekly prices from Alpha Vantage: {e}")
            return []

    async def fetch_monthly_prices(
        self, symbol: str, outputsize: str = "full"
    ) -> List[MonthlyPrice]:
        """Alpha Vantage에서 월간 주가 데이터 가져오기

        Args:
            symbol: 주식 심볼
            outputsize: 'compact' 또는 'full' (기본: full)

        Returns:
            MonthlyPrice 리스트
        """
        try:
            symbol = self._validate_symbol(symbol)

            if outputsize not in ["compact", "full"]:
                outputsize = "full"

            response = await self.alpha_vantage.stock.monthly_adjusted(
                symbol=symbol, outputsize=cast(Literal["compact", "full"], outputsize)
            )

            if isinstance(response, list):
                logger.info(f"Response is list with {len(response)} items")
                monthly_prices = []

                for item in response:
                    if not isinstance(item, dict):
                        continue

                    try:
                        required_fields = [
                            "date",
                            "open",
                            "high",
                            "low",
                            "close",
                            "volume",
                        ]
                        if not all(field in item for field in required_fields):
                            continue

                        # date 처리
                        date_value = item["date"]
                        if isinstance(date_value, str):
                            date_obj = datetime.strptime(date_value, "%Y-%m-%d")
                        elif isinstance(date_value, datetime):
                            date_obj = date_value
                        else:
                            continue

                        monthly_price = MonthlyPrice(
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
                        )
                        monthly_prices.append(monthly_price)

                    except (ValueError, KeyError) as e:
                        logger.warning(f"Failed to parse monthly price data: {e}")
                        continue

                logger.info(
                    f"Fetched {len(monthly_prices)} monthly prices for {symbol}"
                )
                return monthly_prices

            else:
                logger.warning(
                    f"Unexpected response type for {symbol}: {type(response)}"
                )
                return []

        except Exception as e:
            logger.error(f"Failed to fetch monthly prices from Alpha Vantage: {e}")
            return []

    async def fetch_quote(self, symbol: str) -> QuoteData:
        """Alpha Vantage에서 실시간 호가 데이터 가져오기

        Args:
            symbol: 주식 심볼

        Returns:
            QuoteData 객체

        Raises:
            ValueError: Invalid quote response
        """
        try:
            symbol = self._validate_symbol(symbol)
            logger.info(f"Fetching real-time quote for {symbol} from Alpha Vantage")

            response = await self.alpha_vantage.stock.quote(symbol=symbol)

            if isinstance(response, dict):
                logger.info(
                    f"Successfully fetched quote for {symbol}: price={response.get('price', 'N/A')}"
                )
                return self._dict_to_quote_data(response)
            else:
                logger.warning(
                    f"Unexpected quote response type for {symbol}: {type(response)}"
                )
                raise ValueError(f"Invalid quote response for {symbol}")

        except Exception as e:
            logger.error(f"Failed to fetch quote from Alpha Vantage for {symbol}: {e}")
            raise

    async def fetch_intraday(
        self,
        symbol: str,
        interval: Literal["1min", "5min", "15min", "30min", "60min"] = "15min",
        adjusted: bool = False,
        extended_hours: bool = False,
        outputsize: Literal["compact", "full"] | None = "full",
        month: Optional[str] = None,
    ) -> List[DailyPrice]:
        """Alpha Vantage에서 인트라데이 데이터 가져오기

        Args:
            symbol: 주식 심볼
            interval: 데이터 간격
            adjusted: 조정된 가격 사용 여부
            extended_hours: 장외 시간 포함 여부
            outputsize: 출력 크기
            month: 조회할 월 (YYYY-MM 형식, Premium plan only)

        Returns:
            DailyPrice 리스트 (dict 형태)
        """
        try:
            symbol = self._validate_symbol(symbol)
            logger.info(
                f"📊 Fetching intraday data for {symbol} ({interval}, month={month or 'latest'}) from Alpha Vantage"
            )

            # month 파라미터를 datetime으로 변환 (YYYY-MM -> datetime)
            month_dt = None
            if month:
                try:
                    # "2025-01" -> datetime(2025, 1, 1)
                    year, month_num = month.split("-")
                    month_dt = datetime(int(year), int(month_num), 1)
                except ValueError:
                    logger.warning(f"Invalid month format: {month}. Expected YYYY-MM.")

            # Alpha Vantage API 호출 (리스트 반환)
            response = await self.alpha_vantage.stock.intraday(
                symbol=symbol,
                interval=interval,
                adjusted=adjusted,
                extended_hours=extended_hours,
                outputsize=outputsize,
                month=month_dt,  # Premium plan only
            )

            if not isinstance(response, list):
                logger.warning(
                    f"⚠️ Unexpected intraday response type for {symbol}: {type(response)}"
                )
                return []

            if not response:
                logger.warning(f"⚠️ No intraday data returned for {symbol}")
                return []

            logger.info(f"✅ Fetched {len(response)} intraday records for {symbol}")

            # DailyPrice 모델로 변환 (datetime 필드 포함)
            intraday_prices = []
            for item in response:
                try:
                    # datetime 또는 date 필드 확인
                    date_value = item.get("datetime") or item.get("date")
                    if not date_value:
                        logger.warning(
                            f"⚠️ Missing datetime/date field in item: {item}"
                        )
                        continue

                    # datetime 객체로 변환
                    if isinstance(date_value, str):
                        # "2025-01-11 09:30:00" 형식 파싱
                        try:
                            date_obj = datetime.strptime(
                                date_value, "%Y-%m-%d %H:%M:%S"
                            )
                        except ValueError:
                            # "2025-01-11" 형식 폴백
                            date_obj = datetime.strptime(date_value, "%Y-%m-%d")
                    elif isinstance(date_value, datetime):
                        date_obj = date_value
                    else:
                        logger.warning(f"⚠️ Unexpected date type: {type(date_value)}")
                        continue

                    # DailyPrice 모델로 변환 (dict 형태)
                    price_dict = {
                        "symbol": symbol.upper(),
                        "date": date_obj,
                        "open": Decimal(str(item.get("open", 0))),
                        "high": Decimal(str(item.get("high", 0))),
                        "low": Decimal(str(item.get("low", 0))),
                        "close": Decimal(str(item.get("close", 0))),
                        "volume": int(item.get("volume", 0)),
                        "adjusted_close": Decimal(
                            str(item.get("adjusted_close", item.get("close", 0)))
                        ),
                        "dividend_amount": Decimal(str(item.get("dividend_amount", 0))),
                        "split_coefficient": Decimal(
                            str(item.get("split_coefficient", 1))
                        ),
                        "data_quality_score": 95.0,
                        "source": "alpha_vantage",
                        "price_change": Decimal("0.0"),
                        "price_change_percent": Decimal("0.0"),
                    }

                    intraday_prices.append(price_dict)  # type: ignore

                except (ValueError, KeyError) as e:
                    logger.warning(f"⚠️ Failed to parse intraday data: {e}")
                    continue

            logger.info(f"✅ Parsed {len(intraday_prices)} intraday prices for {symbol}")
            return intraday_prices  # type: ignore

        except Exception as e:
            logger.error(
                f"❌ Failed to fetch intraday data from Alpha Vantage for {symbol}: {e}",
                exc_info=True,
            )
            return []

    async def search_symbols(self, keywords: str) -> dict:
        """심볼 검색 (Alpha Vantage SYMBOL_SEARCH API 호출)

        Args:
            keywords: 검색 키워드

        Returns:
            {"bestMatches": [...]} 형태의 검색 결과
        """
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

    async def fetch_historical(
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
        try:
            logger.info(f"Fetching historical data for {symbol}")

            # Alpha Vantage daily adjusted 데이터 호출 (full outputsize)
            response = await self.alpha_vantage.stock.daily_adjusted(
                symbol=symbol,
                outputsize="full",  # type: ignore
            )

            # mysingle_quant 클라이언트가 이미 파싱된 리스트를 반환하는 경우
            if isinstance(response, list):
                logger.info(
                    f"Received {len(response)} parsed records from Alpha Vantage"
                )

                # 날짜 범위 필터링
                filtered_records = []
                for item in response:
                    if not isinstance(item, dict):
                        continue

                    # 날짜 파싱
                    date_value = item.get("date")
                    if isinstance(date_value, str):
                        try:
                            date_obj = datetime.strptime(date_value, "%Y-%m-%d")
                        except ValueError:
                            continue
                    elif isinstance(date_value, datetime):
                        date_obj = date_value
                    else:
                        continue

                    # 날짜 범위 필터링
                    if start_date and date_obj < start_date:
                        continue
                    if end_date and date_obj > end_date:
                        continue

                    filtered_records.append(item)

                logger.info(
                    f"Filtered to {len(filtered_records)} records for date range"
                )

                # DataProcessor가 기대하는 형태로 반환
                return {
                    "symbol": symbol,
                    "records": filtered_records,  # 리스트 형태
                    "data_points": len(filtered_records),
                    "timestamp": datetime.now().isoformat(),
                    "source": "alpha_vantage",
                }

            # 기존 딕셔너리 구조 처리 (fallback)
            elif isinstance(response, dict) and "Time Series (Daily)" in response:
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

            else:
                logger.warning(
                    f"Unexpected response format for {symbol}: {type(response)}"
                )
                return {}

        except Exception as e:
            logger.error(f"Failed to fetch historical data for {symbol}: {e}")
            return {}
