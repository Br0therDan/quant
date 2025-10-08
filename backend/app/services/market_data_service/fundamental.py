"""
Fundamental Data Service
기업 재무 데이터를 처리하는 서비스
"""

from typing import List, Optional, Dict, Any
import logging
from decimal import Decimal

from .base_service import BaseMarketDataService
from app.models.market_data.fundamental import (
    CompanyOverview,
    IncomeStatement,
    BalanceSheet,
    CashFlow,
    Earnings,
)


logger = logging.getLogger(__name__)


class FundamentalService(BaseMarketDataService):
    """기업 재무 데이터 서비스

    기업의 재무제표, 실적, 개요 등의 펀더멘털 데이터를 처리합니다.
    """

    @staticmethod
    def _to_decimal(value):
        """API 응답값을 Decimal로 안전하게 변환"""
        if not value or value in ("", "None", "N/A"):
            return None
        try:
            return Decimal(str(value))
        except Exception as e:
            logger.error(f"Error converting to Decimal: {e}")
            return None

    async def get_company_overview(self, symbol: str) -> Optional[CompanyOverview]:
        """기업 개요 정보 조회 (통합 캐시 우선, Alpha Vantage fallback)

        Args:
            symbol: 주식 심볼

        Returns:
            기업 개요 정보
        """
        try:
            logger.info(f"Fetching company overview for {symbol}")

            cache_key = f"company_overview_{symbol.upper()}"

            async def refresh_overview_data():
                overview_data = await self._fetch_overview_from_alpha_vantage(symbol)
                return [overview_data] if overview_data else []

            data = await self.get_data_with_unified_cache(
                cache_key=cache_key,
                model_class=CompanyOverview,
                data_type="fundamental_overview",
                symbol=symbol.upper(),
                refresh_callback=refresh_overview_data,
                ttl_hours=24,  # 기업 개요는 24시간 TTL
            )

            if isinstance(data, list) and len(data) > 0:
                first_item = data[0]
                if isinstance(first_item, CompanyOverview):
                    return first_item
                else:
                    logger.warning(f"Invalid data type in cache for {symbol}")
                    return None
            elif isinstance(data, CompanyOverview):
                return data
            else:
                logger.warning(f"No valid company overview data found for {symbol}")
                return None

        except Exception as e:
            logger.error(f"Failed to get company overview for {symbol}: {e}")
            return None

    async def _fetch_overview_from_alpha_vantage(
        self, symbol: str
    ) -> Optional[CompanyOverview]:
        """Alpha Vantage에서 기업 개요 데이터를 가져와서 CompanyOverview 모델로 변환"""
        try:
            response = await self.alpha_vantage.fundamental.overview(symbol=symbol)

            if isinstance(response, list) and len(response) > 0:
                data = response[0]  # type: ignore
            elif isinstance(response, dict):
                data = response
            else:
                logger.warning(f"Invalid overview response for {symbol}")
                return None

            if not data:
                logger.warning(f"Empty overview response for {symbol}")
                return None

            # Alpha Vantage 클라이언트에서 이미 파싱된 응답을 CompanyOverview 모델로 변환
            # 클라이언트에서 이미 필드명이 변환되어 있음
            overview_data = {
                "symbol": data.get("symbol", symbol),
                "name": data.get("name", ""),
                "description": data.get("description", ""),
                "exchange": data.get("exchange", ""),
                "currency": data.get("currency", "USD"),
                "country": data.get("country", ""),
                "sector": data.get("sector", ""),
                "industry": data.get("industry", ""),
                "market_capitalization": self._to_decimal(
                    data.get("market_capitalization")
                ),
                "pe_ratio": self._to_decimal(data.get("pe_ratio")),
                "peg_ratio": self._to_decimal(data.get("peg_ratio")),
                "book_value": self._to_decimal(data.get("book_value")),
                "dividend_per_share": self._to_decimal(data.get("dividend_per_share")),
                "dividend_yield": self._to_decimal(data.get("dividend_yield")),
                "eps": self._to_decimal(data.get("eps")),
                "revenue_per_share_ttm": self._to_decimal(
                    data.get("revenue_per_share_ttm")
                ),
                "profit_margin": self._to_decimal(data.get("profit_margin")),
                "operating_margin_ttm": self._to_decimal(
                    data.get("operating_margin_ttm")
                ),
                "return_on_assets_ttm": self._to_decimal(
                    data.get("return_on_assets_ttm")
                ),
                "return_on_equity_ttm": self._to_decimal(
                    data.get("return_on_equity_ttm")
                ),
                "revenue_ttm": self._to_decimal(data.get("revenue_ttm")),
                "gross_profit_ttm": self._to_decimal(data.get("gross_profit_ttm")),
                "ebitda": self._to_decimal(data.get("ebitda")),
                "shares_outstanding": int(data.get("shares_outstanding", 0) or 0),
                "fifty_two_week_high": self._to_decimal(data.get("52_week_high")),
                "fifty_two_week_low": self._to_decimal(data.get("52_week_low")),
                "fifty_day_moving_average": self._to_decimal(
                    data.get("50_day_moving_average")
                ),
                "two_hundred_day_moving_average": self._to_decimal(
                    data.get("200_day_moving_average")
                ),
                "beta": self._to_decimal(data.get("beta")),
                "fiscal_year_end": data.get("fiscal_year_end", ""),
                "analyst_target_price": self._to_decimal(
                    data.get("analyst_target_price")
                ),
            }

            # CompanyOverview 인스턴스 생성
            return CompanyOverview(**overview_data)

        except Exception as e:
            logger.error(
                f"Failed to fetch overview from Alpha Vantage for {symbol}: {e}"
            )
            return None

    async def get_income_statement(
        self, symbol: str, period: str = "annual"
    ) -> List[IncomeStatement]:
        """손익계산서 조회 (통합 캐시 우선, Alpha Vantage fallback)

        Args:
            symbol: 주식 심볼
            period: 기간 (annual, quarterly)

        Returns:
            손익계산서 데이터 리스트
        """
        cache_key = f"income_statement_{symbol.upper()}_{period}"

        async def refresh_callback():
            return await self._fetch_income_statement_from_alpha_vantage(symbol, period)

        data = await self.get_data_with_unified_cache(
            cache_key=cache_key,
            model_class=IncomeStatement,
            data_type="fundamental_income",
            symbol=symbol.upper(),
            refresh_callback=refresh_callback,
            ttl_hours=72,  # 재무제표는 72시간 TTL
        )

        return data if isinstance(data, list) else []

    async def _fetch_income_statement_from_alpha_vantage(
        self, symbol: str, period: str = "annual"
    ) -> List[IncomeStatement]:
        """Alpha Vantage에서 손익계산서 데이터를 가져와서 IncomeStatement 모델로 변환"""
        try:
            logger.info(f"Fetching income statement for {symbol} ({period})")

            response = await self.alpha_vantage.fundamental.income_statement(
                symbol=symbol
            )

            if isinstance(response, list) and len(response) > 0:
                data = response[0]  # type: ignore
            elif isinstance(response, dict):
                data = response
            else:
                logger.warning(f"Invalid income statement response for {symbol}")
                return []

            if not data:
                logger.warning(f"Empty income statement response for {symbol}")
                return []

            # Annual 또는 Quarterly 리포트 선택
            reports_key = (
                "annual_reports" if period == "annual" else "quarterly_reports"
            )
            reports = data.get(reports_key, [])

            income_statements = []
            for report in reports:
                income_data = {
                    "symbol": symbol,
                    "fiscal_date_ending": report.get("fiscalDateEnding", ""),
                    "reported_currency": report.get("reportedCurrency", "USD"),
                    "total_revenue": self._to_decimal(report.get("totalRevenue")),
                    "cost_of_revenue": self._to_decimal(report.get("costOfRevenue")),
                    "gross_profit": self._to_decimal(report.get("grossProfit")),
                    "operating_expenses": self._to_decimal(
                        report.get("operatingExpenses")
                    ),
                    "operating_income": self._to_decimal(report.get("operatingIncome")),
                    "interest_income": self._to_decimal(report.get("interestIncome")),
                    "interest_expense": self._to_decimal(report.get("interestExpense")),
                    "income_before_tax": self._to_decimal(
                        report.get("incomeBeforeTax")
                    ),
                    "income_tax_expense": self._to_decimal(
                        report.get("incomeTaxExpense")
                    ),
                    "net_income": self._to_decimal(report.get("netIncome")),
                    "basic_eps": self._to_decimal(report.get("eps")),
                    "diluted_eps": self._to_decimal(report.get("dilutedEPS")),
                    "research_and_development": self._to_decimal(
                        report.get("researchAndDevelopment")
                    ),
                }

                income_statements.append(IncomeStatement(**income_data))

            logger.info(
                f"Fetched {len(income_statements)} income statements for {symbol}"
            )
            return income_statements

        except Exception as e:
            logger.error(f"Failed to get income statement for {symbol}: {e}")
            return []

    async def get_balance_sheet(
        self, symbol: str, period: str = "annual"
    ) -> List[BalanceSheet]:
        """재무상태표 조회 (통합 캐시 우선, Alpha Vantage fallback)

        Args:
            symbol: 주식 심볼
            period: 기간 (annual, quarterly)

        Returns:
            재무상태표 데이터 리스트
        """
        cache_key = f"balance_sheet_{symbol.upper()}_{period}"

        async def refresh_callback():
            return await self._fetch_balance_sheet_from_alpha_vantage(symbol, period)

        data = await self.get_data_with_unified_cache(
            cache_key=cache_key,
            model_class=BalanceSheet,
            data_type="fundamental_balance",
            symbol=symbol.upper(),
            refresh_callback=refresh_callback,
            ttl_hours=72,  # 재무제표는 72시간 TTL
        )

        return data if isinstance(data, list) else []

    async def _fetch_balance_sheet_from_alpha_vantage(
        self, symbol: str, period: str = "annual"
    ) -> List[BalanceSheet]:
        """Alpha Vantage에서 재무상태표 데이터를 가져와서 BalanceSheet 모델로 변환"""
        try:
            logger.info(f"Fetching balance sheet for {symbol} ({period})")

            response = await self.alpha_vantage.fundamental.balance_sheet(symbol=symbol)

            if isinstance(response, list) and len(response) > 0:
                data = response[0]  # type: ignore
            elif isinstance(response, dict):
                data = response
            else:
                logger.warning(f"Invalid balance sheet response for {symbol}")
                return []

            if not data:
                logger.warning(f"Empty balance sheet response for {symbol}")
                return []

            # Annual 또는 Quarterly 리포트 선택
            reports_key = (
                "annual_reports" if period == "annual" else "quarterly_reports"
            )
            reports = data.get(reports_key, [])

            balance_sheets = []
            for report in reports:
                balance_data = {
                    "symbol": symbol,
                    "fiscal_date_ending": report.get("fiscalDateEnding", ""),
                    "reported_currency": report.get("reportedCurrency", "USD"),
                    "total_assets": self._to_decimal(report.get("totalAssets")),
                    "total_current_assets": self._to_decimal(
                        report.get("totalCurrentAssets")
                    ),
                    "cash_and_cash_equivalents": self._to_decimal(
                        report.get("cashAndCashEquivalentsAtCarryingValue")
                    ),
                    "cash_and_short_term_investments": self._to_decimal(
                        report.get("cashAndShortTermInvestments")
                    ),
                    "inventory": self._to_decimal(report.get("inventory")),
                    "current_net_receivables": self._to_decimal(
                        report.get("currentNetReceivables")
                    ),
                    "property_plant_equipment": self._to_decimal(
                        report.get("propertyPlantEquipment")
                    ),
                    "goodwill": self._to_decimal(report.get("goodwill")),
                    "intangible_assets": self._to_decimal(
                        report.get("intangibleAssets")
                    ),
                    "total_liabilities": self._to_decimal(
                        report.get("totalLiabilities")
                    ),
                    "total_current_liabilities": self._to_decimal(
                        report.get("totalCurrentLiabilities")
                    ),
                    "current_accounts_payable": self._to_decimal(
                        report.get("currentAccountsPayable")
                    ),
                    "deferred_revenue": self._to_decimal(report.get("deferredRevenue")),
                    "current_debt": self._to_decimal(report.get("currentDebt")),
                    "long_term_debt": self._to_decimal(report.get("longTermDebt")),
                    "total_shareholder_equity": self._to_decimal(
                        report.get("totalShareholderEquity")
                    ),
                    "treasury_stock": self._to_decimal(report.get("treasuryStock")),
                    "retained_earnings": self._to_decimal(
                        report.get("retainedEarnings")
                    ),
                    "common_stock": self._to_decimal(report.get("commonStock")),
                    "common_stock_shares_outstanding": int(
                        report.get("commonStockSharesOutstanding", 0) or 0
                    ),
                }

                balance_sheets.append(BalanceSheet(**balance_data))

            logger.info(f"Fetched {len(balance_sheets)} balance sheets for {symbol}")
            return balance_sheets

        except Exception as e:
            logger.error(f"Failed to get balance sheet for {symbol}: {e}")
            return []

    async def get_cash_flow(
        self, symbol: str, period: str = "annual"
    ) -> List[CashFlow]:
        """현금흐름표 조회 (통합 캐시 우선, Alpha Vantage fallback)

        Args:
            symbol: 주식 심볼
            period: 기간 (annual, quarterly)

        Returns:
            현금흐름표 데이터 리스트
        """
        cache_key = f"cash_flow_{symbol.upper()}_{period}"

        async def refresh_callback():
            return await self._fetch_cash_flow_from_alpha_vantage(symbol, period)

        data = await self.get_data_with_unified_cache(
            cache_key=cache_key,
            model_class=CashFlow,
            data_type="fundamental_cashflow",
            symbol=symbol.upper(),
            refresh_callback=refresh_callback,
            ttl_hours=72,  # 재무제표는 72시간 TTL
        )

        return data if isinstance(data, list) else []

    async def _fetch_cash_flow_from_alpha_vantage(
        self, symbol: str, period: str = "annual"
    ) -> List[CashFlow]:
        """Alpha Vantage에서 현금흐름표 데이터를 가져와서 CashFlow 모델로 변환"""
        try:
            logger.info(f"Fetching cash flow for {symbol} ({period})")

            response = await self.alpha_vantage.fundamental.cash_flow(symbol=symbol)

            if isinstance(response, list) and len(response) > 0:
                data = response[0]  # type: ignore
            elif isinstance(response, dict):
                data = response
            else:
                logger.warning(f"Invalid cash flow response for {symbol}")
                return []

            if not data:
                logger.warning(f"Empty cash flow response for {symbol}")
                return []

            # Annual 또는 Quarterly 리포트 선택
            reports_key = (
                "annual_reports" if period == "annual" else "quarterly_reports"
            )
            reports = data.get(reports_key, [])

            cash_flows = []
            for report in reports:
                cash_flow_data = {
                    "symbol": symbol,
                    "fiscal_date_ending": report.get("fiscalDateEnding", ""),
                    "reported_currency": report.get("reportedCurrency", "USD"),
                    "operating_cashflow": self._to_decimal(
                        report.get("operatingCashflow")
                    ),
                    "payments_for_operating_activities": self._to_decimal(
                        report.get("paymentsForOperatingActivities")
                    ),
                    "proceeds_from_operating_activities": self._to_decimal(
                        report.get("proceedsFromOperatingActivities")
                    ),
                    "capital_expenditures": self._to_decimal(
                        report.get("capitalExpenditures")
                    ),
                    "cashflow_from_investment": self._to_decimal(
                        report.get("cashflowFromInvestment")
                    ),
                    "cashflow_from_financing": self._to_decimal(
                        report.get("cashflowFromFinancing")
                    ),
                    "dividend_payments": self._to_decimal(report.get("dividendPayout")),
                    "payments_for_repurchase_of_common_stock": self._to_decimal(
                        report.get("paymentsForRepurchaseOfCommonStock")
                    ),
                    "payments_for_repurchase_of_equity": self._to_decimal(
                        report.get("paymentsForRepurchaseOfEquity")
                    ),
                    "change_in_cash_and_cash_equivalents": self._to_decimal(
                        report.get("changeInCashAndCashEquivalents")
                    ),
                }

                cash_flows.append(CashFlow(**cash_flow_data))

            logger.info(f"Fetched {len(cash_flows)} cash flows for {symbol}")
            return cash_flows

        except Exception as e:
            logger.error(f"Failed to get cash flow for {symbol}: {e}")
            return []

    async def get_earnings(self, symbol: str) -> List[Earnings]:
        """실적 발표 데이터 조회 (통합 캐시 우선, Alpha Vantage fallback)

        Args:
            symbol: 주식 심볼

        Returns:
            실적 발표 데이터 리스트
        """
        cache_key = f"earnings_{symbol.upper()}"

        async def refresh_callback():
            return await self._fetch_earnings_from_alpha_vantage(symbol)

        data = await self.get_data_with_unified_cache(
            cache_key=cache_key,
            model_class=Earnings,
            data_type="fundamental_earnings",
            symbol=symbol.upper(),
            refresh_callback=refresh_callback,
            ttl_hours=24,  # 실적 데이터는 24시간 TTL
        )

        return data if isinstance(data, list) else []

    async def _fetch_earnings_from_alpha_vantage(self, symbol: str) -> List[Earnings]:
        """Alpha Vantage에서 실적 발표 데이터를 가져와서 Earnings 모델로 변환"""
        try:
            logger.info(f"Fetching earnings for {symbol}")

            response = await self.alpha_vantage.fundamental.earnings(symbol=symbol)

            if isinstance(response, list) and len(response) > 0:
                data = response[0]  # type: ignore
            elif isinstance(response, dict):
                data = response
            else:
                logger.warning(f"Invalid earnings response for {symbol}")
                return []

            if not data:
                logger.warning(f"Empty earnings response for {symbol}")
                return []

            earnings_list = []

            # Annual earnings
            annual_earnings = data.get("annual_earnings", [])
            for earning in annual_earnings:
                earnings_data = {
                    "symbol": symbol,
                    "fiscal_date_ending": earning.get("fiscalDateEnding", ""),
                    "reported_eps": self._to_decimal(earning.get("reportedEPS")),
                    "reported_date": earning.get("reportedDate", ""),
                    "estimated_eps": None,
                    "surprise": None,
                    "surprise_percentage": None,
                }
                earnings_list.append(Earnings(**earnings_data))

            # Quarterly earnings
            quarterly_earnings = data.get("quarterly_earnings", [])
            for earning in quarterly_earnings:
                earnings_data = {
                    "symbol": symbol,
                    "fiscal_date_ending": earning.get("fiscalDateEnding", ""),
                    "reported_eps": self._to_decimal(earning.get("reportedEPS")),
                    "reported_date": earning.get("reportedDate", ""),
                    "estimated_eps": self._to_decimal(earning.get("estimatedEPS")),
                    "surprise": self._to_decimal(earning.get("surprise")),
                    "surprise_percentage": self._to_decimal(
                        earning.get("surprisePercentage")
                    ),
                }
                earnings_list.append(Earnings(**earnings_data))

            logger.info(f"Fetched {len(earnings_list)} earnings records for {symbol}")
            return earnings_list

        except Exception as e:
            logger.error(f"Failed to get earnings for {symbol}: {e}")
            return []

    async def calculate_financial_ratios(self, symbol: str) -> Dict[str, float]:
        """재무 비율 계산

        Args:
            symbol: 주식 심볼

        Returns:
            계산된 재무 비율들

        Note:
            주요 재무 비율들을 계산합니다.
            - P/E, P/B, ROE, ROA 등 주요 비율
            - 수익성, 안정성, 성장성 지표
        """
        logger.info(f"Calculating financial ratios for {symbol}")

        try:
            # 기업 개요 데이터 가져오기
            overview = await self.get_company_overview(symbol)
            if not overview:
                logger.warning(f"No overview data available for {symbol}")
                return {}

            # 기본 비율들 (Alpha Vantage에서 제공)
            ratios = {
                "pe_ratio": float(overview.pe_ratio or 0),
                "peg_ratio": float(overview.peg_ratio or 0),
                "book_value": float(overview.book_value or 0),
                "dividend_yield": float(overview.dividend_yield or 0),
                "eps": float(overview.eps or 0),
                "profit_margin": float(overview.profit_margin or 0),
                "operating_margin_ttm": float(overview.operating_margin_ttm or 0),
                "return_on_assets_ttm": float(overview.return_on_assets_ttm or 0),
                "return_on_equity_ttm": float(overview.return_on_equity_ttm or 0),
                "revenue_per_share_ttm": float(overview.revenue_per_share_ttm or 0),
                "beta": float(overview.beta or 0),
            }

            # 추가 계산 비율들
            if overview.market_capitalization and overview.revenue_ttm:
                ratios["price_to_sales"] = float(
                    overview.market_capitalization
                ) / float(overview.revenue_ttm)

            if (
                overview.market_capitalization
                and overview.book_value
                and overview.shares_outstanding
            ):
                book_value_total = float(overview.book_value) * float(
                    overview.shares_outstanding
                )
                if book_value_total > 0:
                    ratios["price_to_book"] = (
                        float(overview.market_capitalization) / book_value_total
                    )

            # 0인 값들 제거
            ratios = {k: v for k, v in ratios.items() if v != 0}

            logger.info(f"Calculated {len(ratios)} financial ratios for {symbol}")
            return ratios

        except Exception as e:
            logger.error(f"Failed to calculate financial ratios for {symbol}: {e}")
            return {}

    # BaseMarketDataService 추상 메서드 구현
    async def _fetch_from_source(self, **kwargs) -> Any:
        """AlphaVantage에서 펀더멘털 데이터 가져오기"""
        try:
            method = kwargs.get("method", "overview")
            symbol = kwargs.get("symbol")

            if not symbol:
                raise ValueError("Symbol is required for fundamental data")

            if method == "overview":
                return await self.alpha_vantage.fundamental.overview(symbol=symbol)
            elif method == "income_statement":
                return await self.alpha_vantage.fundamental.income_statement(
                    symbol=symbol
                )
            elif method == "balance_sheet":
                return await self.alpha_vantage.fundamental.balance_sheet(symbol=symbol)
            elif method == "cash_flow":
                return await self.alpha_vantage.fundamental.cash_flow(symbol=symbol)
            elif method == "earnings":
                return await self.alpha_vantage.fundamental.earnings(symbol=symbol)
            else:
                raise ValueError(f"Unknown fundamental method: {method}")

        except Exception as e:
            logger.error(f"Error fetching fundamental data from source: {e}")
            raise

    async def _save_to_cache(self, data: Any, **kwargs) -> bool:
        """펀더멘털 데이터를 캐시에 저장"""
        try:
            cache_key = kwargs.get("cache_key", "fundamental_data")
            symbol = kwargs.get("symbol", "UNKNOWN")

            # 데이터를 CompanyOverview 모델로 변환
            if isinstance(data, dict):
                try:
                    # CompanyOverview 모델 데이터 구성
                    overview_data = {
                        "symbol": symbol,
                        "asset_type": data.get("AssetType", "Common Stock"),
                        "name": data.get("Name", ""),
                        "description": data.get("Description", ""),
                        "cik": data.get("CIK", ""),
                        "exchange": data.get("Exchange", ""),
                        "currency": data.get("Currency", "USD"),
                        "country": data.get("Country", "USA"),
                        "sector": data.get("Sector", ""),
                        "industry": data.get("Industry", ""),
                        "address": data.get("Address", ""),
                        "fiscal_year_end": data.get("FiscalYearEnd", ""),
                        "latest_quarter": data.get("LatestQuarter", ""),
                        "market_capitalization": self._to_decimal(
                            data.get("MarketCapitalization")
                        ),
                        "ebitda": self._to_decimal(data.get("EBITDA")),
                        "pe_ratio": self._to_decimal(data.get("PERatio")),
                        "peg_ratio": self._to_decimal(data.get("PEGRatio")),
                        "book_value": self._to_decimal(data.get("BookValue")),
                        "dividend_per_share": self._to_decimal(
                            data.get("DividendPerShare")
                        ),
                        "dividend_yield": self._to_decimal(data.get("DividendYield")),
                        "eps": self._to_decimal(data.get("EPS")),
                        "revenue_per_share_ttm": self._to_decimal(
                            data.get("RevenuePerShareTTM")
                        ),
                        "profit_margin": self._to_decimal(data.get("ProfitMargin")),
                        "operating_margin_ttm": self._to_decimal(
                            data.get("OperatingMarginTTM")
                        ),
                        "return_on_assets_ttm": self._to_decimal(
                            data.get("ReturnOnAssetsTTM")
                        ),
                        "return_on_equity_ttm": self._to_decimal(
                            data.get("ReturnOnEquityTTM")
                        ),
                        "revenue_ttm": self._to_decimal(data.get("RevenueTTM")),
                        "gross_profit_ttm": self._to_decimal(
                            data.get("GrossProfitTTM")
                        ),
                        "diluted_eps_ttm": self._to_decimal(data.get("DilutedEPSTTM")),
                        "quarterly_earnings_growth_yoy": self._to_decimal(
                            data.get("QuarterlyEarningsGrowthYOY")
                        ),
                        "quarterly_revenue_growth_yoy": self._to_decimal(
                            data.get("QuarterlyRevenueGrowthYOY")
                        ),
                        "analyst_target_price": self._to_decimal(
                            data.get("AnalystTargetPrice")
                        ),
                        "trailing_pe": self._to_decimal(data.get("TrailingPE")),
                        "forward_pe": self._to_decimal(data.get("ForwardPE")),
                        "price_to_sales_ratio_ttm": self._to_decimal(
                            data.get("PriceToSalesRatioTTM")
                        ),
                        "price_to_book_ratio": self._to_decimal(
                            data.get("PriceToBookRatio")
                        ),
                        "ev_to_revenue": self._to_decimal(data.get("EVToRevenue")),
                        "ev_to_ebitda": self._to_decimal(data.get("EVToEBITDA")),
                        "beta": self._to_decimal(data.get("Beta")),
                        "week_52_high": self._to_decimal(data.get("52WeekHigh")),
                        "week_52_low": self._to_decimal(data.get("52WeekLow")),
                        "day_50_moving_average": self._to_decimal(
                            data.get("50DayMovingAverage")
                        ),
                        "day_200_moving_average": self._to_decimal(
                            data.get("200DayMovingAverage")
                        ),
                        "shares_outstanding": self._to_decimal(
                            data.get("SharesOutstanding")
                        ),
                        "dividend_date": data.get("DividendDate", ""),
                        "ex_dividend_date": data.get("ExDividendDate", ""),
                    }

                    from app.models.market_data.fundamental import CompanyOverview

                    overview = CompanyOverview(**overview_data)

                    # DuckDB 캐시에 저장
                    success = await self._store_to_duckdb_cache(
                        cache_key=cache_key,
                        data=[overview],
                        table_name="fundamental_cache",
                    )

                    if success:
                        logger.info(
                            f"Fundamental data cached successfully: {cache_key}"
                        )
                    return success

                except Exception as model_error:
                    logger.warning(
                        f"Failed to create CompanyOverview model: {model_error}"
                    )
                    # 원본 데이터를 딕셔너리로 저장
                    if self._db_manager:
                        return self._db_manager.store_cache_data(
                            cache_key=cache_key,
                            data=[data],
                            table_name="fundamental_cache",
                        )

            logger.info(f"No valid fundamental data to cache for: {cache_key}")
            return True

        except Exception as e:
            logger.error(f"Error saving fundamental data to cache: {e}")
            return False

    # Removed duplicate and incorrect _to_decimal method

    async def _get_from_cache(self, **kwargs) -> Optional[List[Any]]:
        """캐시에서 펀더멘털 데이터 조회"""
        try:
            cache_key = kwargs.get("cache_key", "fundamental_data")

            # DuckDB 캐시에서 데이터 조회
            cached_data = await self._get_from_duckdb_cache(
                cache_key=cache_key,
                start_date=kwargs.get("start_date"),
                end_date=kwargs.get("end_date"),
                ignore_ttl=kwargs.get("ignore_ttl", False),
            )

            if cached_data:
                logger.info(
                    f"Fundamental cache hit: {cache_key} ({len(cached_data)} items)"
                )
                return cached_data
            else:
                logger.debug(f"Fundamental cache miss: {cache_key}")
                return None

        except Exception as e:
            logger.error(f"Error getting fundamental data from cache: {e}")
            return None

    async def refresh_data_from_source(self, **kwargs) -> List[CompanyOverview]:
        """베이스 클래스의 추상 메서드 구현"""
        # 이 메서드는 더 이상 직접 사용되지 않으므로 빈 구현
        return []
