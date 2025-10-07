"""
Economic Indicator Service
경제 지표 데이터를 처리하는 서비스
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from .base_service import BaseMarketDataService
from app.models.market_data.economic_indicator import (
    GDP,
    Inflation,
    InterestRate,
    Employment,
)


logger = logging.getLogger(__name__)


class EconomicIndicatorService(BaseMarketDataService):
    """경제 지표 서비스

    GDP, 인플레이션, 금리 등의 거시경제 지표를 처리합니다.
    """

    async def get_gdp_data(
        self, country: str = "USA", period: str = "quarterly"
    ) -> List[GDP]:
        """경제 성장률 데이터 조회 (Alpha Vantage REAL_GDP API)

        Args:
            country: 국가 코드
            period: 기간 (quarterly, annual)

        Returns:
            GDP 데이터 리스트
        """
        try:
            logger.info(f"Fetching GDP data for {country} ({period})")

            # Alpha Vantage REAL_GDP API 호출
            interval_param = "quarterly" if period == "quarterly" else "annual"
            response = await self.alpha_vantage.economic_indicators.real_gdp(
                interval=interval_param  # type: ignore
            )

            if isinstance(response, list) and len(response) > 0:
                data = response[0]  # type: ignore
            elif isinstance(response, dict):
                data = response
            else:
                logger.warning(f"Invalid GDP response for {country}")
                return []

            if not data:
                logger.warning(f"Empty GDP response for {country}")
                return []

            # Alpha Vantage REAL_GDP 응답 처리
            gdp_data_list = data.get("data", [])

            gdp_records = []
            for gdp_entry in gdp_data_list:
                try:
                    gdp_data = {
                        "country": country,
                        "date": gdp_entry.get("date", ""),
                        "value": float(gdp_entry.get("value", 0) or 0),
                        "unit": "billions_usd",
                        "period_type": period,
                        "adjustment": "real",  # Real GDP
                        "frequency": period,
                        "source": "bureau_of_economic_analysis",
                        "notes": f"Real GDP data from Alpha Vantage ({period})",
                    }

                    gdp_records.append(GDP(**gdp_data))

                except Exception as e:
                    logger.warning(f"Failed to parse GDP data: {e}")
                    continue

            logger.info(f"Fetched {len(gdp_records)} GDP data points")
            return gdp_records

        except Exception as e:
            logger.error(f"Failed to get GDP data for {country}: {e}")
            return []

    async def get_inflation_data(
        self, country: str = "USA", indicator_type: str = "CPI"
    ) -> List[Inflation]:
        """인플레이션 지표 조회 (Alpha Vantage INFLATION API)

        Args:
            country: 국가 코드
            indicator_type: 지표 유형 (CPI, PPI, PCE)

        Returns:
            인플레이션 데이터 리스트
        """
        try:
            logger.info(f"Fetching inflation data for {country} ({indicator_type})")

            # Alpha Vantage INFLATION API 호출
            response = await self.alpha_vantage.economic_indicators.inflation()

            if isinstance(response, list) and len(response) > 0:
                data = response[0]  # type: ignore
            elif isinstance(response, dict):
                data = response
            else:
                logger.warning(f"Invalid inflation response for {country}")
                return []

            if not data:
                logger.warning(f"Empty inflation response for {country}")
                return []

            # Alpha Vantage INFLATION 응답 처리
            inflation_data_list = data.get("data", [])

            inflation_records = []
            for inflation_entry in inflation_data_list:
                try:
                    inflation_data = {
                        "country": country,
                        "date": inflation_entry.get("date", ""),
                        "value": float(inflation_entry.get("value", 0) or 0),
                        "indicator_type": "Consumer Price Index",
                        "unit": "percent",
                        "frequency": "annual",
                        "base_year": None,  # API에서 제공하지 않음
                        "seasonal_adjustment": None,  # API에서 제공하지 않음
                        "source": "bureau_of_labor_statistics",
                        "notes": "Inflation rate data from Alpha Vantage (consumer price index)",
                    }

                    inflation_records.append(Inflation(**inflation_data))

                except Exception as e:
                    logger.warning(f"Failed to parse inflation data: {e}")
                    continue

            logger.info(f"Fetched {len(inflation_records)} inflation data points")
            return inflation_records

        except Exception as e:
            logger.error(f"Failed to get inflation data for {country}: {e}")
            return []

    async def get_interest_rates(
        self, country: str = "USA", rate_type: str = "FEDERAL_FUNDS_RATE"
    ) -> List[InterestRate]:
        """금리 데이터 조회 (Alpha Vantage FEDERAL_FUNDS_RATE API)

        Args:
            country: 국가 코드
            rate_type: 금리 유형

        Returns:
            금리 데이터 리스트
        """
        try:
            logger.info(f"Fetching interest rates for {country} ({rate_type})")

            response = await self.alpha_vantage.economic_indicators.federal_funds_rate()

            if isinstance(response, list) and len(response) > 0:
                data = response[0]  # type: ignore
            elif isinstance(response, dict):
                data = response
            else:
                logger.warning(f"Invalid interest rates response for {country}")
                return []

            if not data:
                logger.warning(f"Empty interest rates response for {country}")
                return []

            # Alpha Vantage FEDERAL_FUNDS_RATE 응답 처리
            rates_data = data.get("data", [])

            interest_rates = []
            for rate_entry in rates_data:
                try:
                    rate_data = {
                        "country": country,
                        "rate_type": rate_type,
                        "date": rate_entry.get("date", ""),
                        "value": float(rate_entry.get("value", 0) or 0),
                        "unit": "percent",
                        "frequency": "monthly",
                        "source": "federal_reserve",
                        "notes": "Federal Funds Rate data from Alpha Vantage",
                    }

                    interest_rates.append(InterestRate(**rate_data))

                except Exception as e:
                    logger.warning(f"Failed to parse interest rate data: {e}")
                    continue

            logger.info(f"Fetched {len(interest_rates)} interest rate data points")
            return interest_rates

        except Exception as e:
            logger.error(f"Failed to get interest rates for {country}: {e}")
            return []

    async def get_employment_data(self, country: str = "USA") -> List[Employment]:
        """고용 지표 조회 (Alpha Vantage UNEMPLOYMENT API)

        Args:
            country: 국가 코드

        Returns:
            고용 데이터 리스트
        """
        try:
            logger.info(f"Fetching employment data for {country}")

            response = await self.alpha_vantage.economic_indicators.unemployment()

            if isinstance(response, list) and len(response) > 0:
                data = response[0]  # type: ignore
            elif isinstance(response, dict):
                data = response
            else:
                logger.warning(f"Invalid employment response for {country}")
                return []

            if not data:
                logger.warning(f"Empty employment response for {country}")
                return []

            # Alpha Vantage UNEMPLOYMENT 응답 처리
            employment_data_list = data.get("data", [])

            employment_records = []
            for emp_entry in employment_data_list:
                try:
                    employment_data = {
                        "country": country,
                        "date": emp_entry.get("date", ""),
                        "unemployment_rate": float(emp_entry.get("value", 0) or 0),
                        "employment_rate": None,  # Not provided by Alpha Vantage
                        "labor_force_participation_rate": None,  # Not provided by Alpha Vantage
                        "nonfarm_payrolls": None,  # Not provided by this endpoint
                        "unit": "percent",
                        "frequency": "monthly",
                        "source": "bureau_of_labor_statistics",
                        "notes": "Unemployment rate data from Alpha Vantage",
                    }

                    employment_records.append(Employment(**employment_data))

                except Exception as e:
                    logger.warning(f"Failed to parse employment data: {e}")
                    continue

            logger.info(f"Fetched {len(employment_records)} employment data points")
            return employment_records

        except Exception as e:
            logger.error(f"Failed to get employment data for {country}: {e}")
            return []

    async def get_economic_calendar(
        self, start_date: datetime, end_date: datetime, importance: str = "high"
    ) -> List[Dict[str, Any]]:
        """경제 캘린더 조회

        Args:
            start_date: 시작 날짜
            end_date: 종료 날짜
            importance: 중요도 필터

        Returns:
            경제 이벤트 리스트

        TODO: 구현 예정
        1. 경제 지표 발표 일정
        2. 중앙은행 회의 일정
        3. 중요도별 필터링
        """
        logger.info(f"Getting economic calendar from {start_date} to {end_date}")

        # TODO: 실제 구현
        return []

    # BaseMarketDataService 추상 메서드 구현
    async def _fetch_from_source(self, **kwargs) -> Any:
        """AlphaVantage에서 경제 지표 데이터 가져오기"""
        # TODO: 구현
        pass

    async def _save_to_cache(self, data: Any, **kwargs) -> bool:
        """경제 지표 데이터를 캐시에 저장"""
        # TODO: 구현
        return False

    async def _get_from_cache(self, **kwargs) -> Optional[List[Any]]:
        """캐시에서 경제 지표 데이터 조회"""
        # TODO: 구현
        return None

    async def refresh_data_from_source(self, **kwargs) -> List[GDP]:
        """베이스 클래스의 추상 메서드 구현"""
        # 이 메서드는 더 이상 직접 사용되지 않으므로 빈 구현
        return []
