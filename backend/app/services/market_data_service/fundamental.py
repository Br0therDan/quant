"""
Fundamental Data Service
기업 재무 데이터를 처리하는 서비스
"""

from typing import List, Optional, Dict, Any
import logging

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

    async def get_company_overview(self, symbol: str) -> Optional[CompanyOverview]:
        """기업 개요 정보 조회 (Alpha Vantage OVERVIEW API)

        Args:
            symbol: 주식 심볼

        Returns:
            기업 개요 정보
        """
        try:
            logger.info(f"Fetching company overview for {symbol}")

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

            # Alpha Vantage OVERVIEW 응답을 CompanyOverview 모델로 변환
            overview_data = {
                "symbol": data.get("Symbol", symbol),
                "name": data.get("Name", ""),
                "description": data.get("Description", ""),
                "exchange": data.get("Exchange", ""),
                "currency": data.get("Currency", "USD"),
                "country": data.get("Country", ""),
                "sector": data.get("Sector", ""),
                "industry": data.get("Industry", ""),
                "market_cap": int(data.get("MarketCapitalization", 0) or 0),
                "pe_ratio": float(data.get("PERatio", 0) or 0),
                "peg_ratio": float(data.get("PEGRatio", 0) or 0),
                "book_value": float(data.get("BookValue", 0) or 0),
                "dividend_per_share": float(data.get("DividendPerShare", 0) or 0),
                "dividend_yield": float(data.get("DividendYield", 0) or 0),
                "eps": float(data.get("EPS", 0) or 0),
                "revenue_per_share_ttm": float(data.get("RevenuePerShareTTM", 0) or 0),
                "profit_margin": float(data.get("ProfitMargin", 0) or 0),
                "operating_margin_ttm": float(data.get("OperatingMarginTTM", 0) or 0),
                "return_on_assets_ttm": float(data.get("ReturnOnAssetsTTM", 0) or 0),
                "return_on_equity_ttm": float(data.get("ReturnOnEquityTTM", 0) or 0),
                "revenue_ttm": int(data.get("RevenueTTM", 0) or 0),
                "gross_profit_ttm": int(data.get("GrossProfitTTM", 0) or 0),
                "ebitda": int(data.get("EBITDA", 0) or 0),
                "shares_outstanding": int(data.get("SharesOutstanding", 0) or 0),
                "week_52_high": float(data.get("52WeekHigh", 0) or 0),
                "week_52_low": float(data.get("52WeekLow", 0) or 0),
                "week_50_moving_average": float(data.get("50DayMovingAverage", 0) or 0),
                "week_200_moving_average": float(
                    data.get("200DayMovingAverage", 0) or 0
                ),
                "beta": float(data.get("Beta", 0) or 0),
                "address": data.get("Address", ""),
                "latest_quarter": data.get("LatestQuarter", ""),
                "fiscal_year_end": data.get("FiscalYearEnd", ""),
                "analyst_target_price": float(data.get("AnalystTargetPrice", 0) or 0),
                "trailing_pe": float(data.get("TrailingPE", 0) or 0),
                "forward_pe": float(data.get("ForwardPE", 0) or 0),
                "price_to_sales_ratio_ttm": float(
                    data.get("PriceToSalesRatioTTM", 0) or 0
                ),
                "price_to_book_ratio": float(data.get("PriceToBookRatio", 0) or 0),
                "ev_to_revenue": float(data.get("EVToRevenue", 0) or 0),
                "ev_to_ebitda": float(data.get("EVToEBITDA", 0) or 0),
            }

            # CompanyOverview 인스턴스 생성
            return CompanyOverview(**overview_data)

        except Exception as e:
            logger.error(f"Failed to get company overview for {symbol}: {e}")
            return None

    async def get_income_statement(
        self, symbol: str, period: str = "annual"
    ) -> List[IncomeStatement]:
        """손익계산서 조회 (Alpha Vantage INCOME_STATEMENT API)

        Args:
            symbol: 주식 심볼
            period: 기간 (annual, quarterly)

        Returns:
            손익계산서 데이터 리스트
        """
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
            reports_key = "annualReports" if period == "annual" else "quarterlyReports"
            reports = data.get(reports_key, [])

            income_statements = []
            for report in reports:
                income_data = {
                    "symbol": symbol,
                    "fiscal_date_ending": report.get("fiscalDateEnding", ""),
                    "reported_currency": report.get("reportedCurrency", "USD"),
                    "total_revenue": int(report.get("totalRevenue", 0) or 0),
                    "cost_of_revenue": int(report.get("costOfRevenue", 0) or 0),
                    "gross_profit": int(report.get("grossProfit", 0) or 0),
                    "operating_expenses": int(report.get("operatingExpenses", 0) or 0),
                    "operating_income": int(report.get("operatingIncome", 0) or 0),
                    "interest_income": int(report.get("interestIncome", 0) or 0),
                    "interest_expense": int(report.get("interestExpense", 0) or 0),
                    "income_before_tax": int(report.get("incomeBeforeTax", 0) or 0),
                    "income_tax_expense": int(report.get("incomeTaxExpense", 0) or 0),
                    "net_income": int(report.get("netIncome", 0) or 0),
                    "ebitda": int(report.get("ebitda", 0) or 0),
                    "eps": float(report.get("eps", 0) or 0),
                    "diluted_eps": float(report.get("dilutedEPS", 0) or 0),
                    "weighted_average_shares_outstanding": int(
                        report.get("weightedAverageSharesOutstanding", 0) or 0
                    ),
                    "weighted_average_shares_outstanding_diluted": int(
                        report.get("weightedAverageSharesOutstandingDiluted", 0) or 0
                    ),
                    "research_and_development": int(
                        report.get("researchAndDevelopment", 0) or 0
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
        """재무상태표 조회 (Alpha Vantage BALANCE_SHEET API)

        Args:
            symbol: 주식 심볼
            period: 기간 (annual, quarterly)

        Returns:
            재무상태표 데이터 리스트
        """
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
            reports_key = "annualReports" if period == "annual" else "quarterlyReports"
            reports = data.get(reports_key, [])

            balance_sheets = []
            for report in reports:
                balance_data = {
                    "symbol": symbol,
                    "fiscal_date_ending": report.get("fiscalDateEnding", ""),
                    "reported_currency": report.get("reportedCurrency", "USD"),
                    "total_assets": int(report.get("totalAssets", 0) or 0),
                    "total_current_assets": int(
                        report.get("totalCurrentAssets", 0) or 0
                    ),
                    "cash_and_cash_equivalents": int(
                        report.get("cashAndCashEquivalentsAtCarryingValue", 0) or 0
                    ),
                    "cash_and_short_term_investments": int(
                        report.get("cashAndShortTermInvestments", 0) or 0
                    ),
                    "inventory": int(report.get("inventory", 0) or 0),
                    "current_net_receivables": int(
                        report.get("currentNetReceivables", 0) or 0
                    ),
                    "total_non_current_assets": int(
                        report.get("totalNonCurrentAssets", 0) or 0
                    ),
                    "property_plant_equipment": int(
                        report.get("propertyPlantEquipment", 0) or 0
                    ),
                    "accumulated_depreciation_amortization_ppe": int(
                        report.get("accumulatedDepreciationAmortizationPPE", 0) or 0
                    ),
                    "intangible_assets": int(report.get("intangibleAssets", 0) or 0),
                    "intangible_assets_excluding_goodwill": int(
                        report.get("intangibleAssetsExcludingGoodwill", 0) or 0
                    ),
                    "goodwill": int(report.get("goodwill", 0) or 0),
                    "investments": int(report.get("investments", 0) or 0),
                    "long_term_investments": int(
                        report.get("longTermInvestments", 0) or 0
                    ),
                    "short_term_investments": int(
                        report.get("shortTermInvestments", 0) or 0
                    ),
                    "other_current_assets": int(
                        report.get("otherCurrentAssets", 0) or 0
                    ),
                    "other_non_current_assets": int(
                        report.get("otherNonCurrrentAssets", 0) or 0
                    ),
                    "total_liabilities": int(report.get("totalLiabilities", 0) or 0),
                    "total_current_liabilities": int(
                        report.get("totalCurrentLiabilities", 0) or 0
                    ),
                    "current_accounts_payable": int(
                        report.get("currentAccountsPayable", 0) or 0
                    ),
                    "deferred_revenue": int(report.get("deferredRevenue", 0) or 0),
                    "current_debt": int(report.get("currentDebt", 0) or 0),
                    "short_term_debt": int(report.get("shortTermDebt", 0) or 0),
                    "total_non_current_liabilities": int(
                        report.get("totalNonCurrentLiabilities", 0) or 0
                    ),
                    "capital_lease_obligations": int(
                        report.get("capitalLeaseObligations", 0) or 0
                    ),
                    "long_term_debt": int(report.get("longTermDebt", 0) or 0),
                    "current_long_term_debt": int(
                        report.get("currentLongTermDebt", 0) or 0
                    ),
                    "long_term_debt_noncurrent": int(
                        report.get("longTermDebtNoncurrent", 0) or 0
                    ),
                    "short_long_term_debt_total": int(
                        report.get("shortLongTermDebtTotal", 0) or 0
                    ),
                    "other_current_liabilities": int(
                        report.get("otherCurrentLiabilities", 0) or 0
                    ),
                    "other_non_current_liabilities": int(
                        report.get("otherNonCurrentLiabilities", 0) or 0
                    ),
                    "total_shareholder_equity": int(
                        report.get("totalShareholderEquity", 0) or 0
                    ),
                    "treasury_stock": int(report.get("treasuryStock", 0) or 0),
                    "retained_earnings": int(report.get("retainedEarnings", 0) or 0),
                    "common_stock": int(report.get("commonStock", 0) or 0),
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
        """현금흐름표 조회 (Alpha Vantage CASH_FLOW API)

        Args:
            symbol: 주식 심볼
            period: 기간 (annual, quarterly)

        Returns:
            현금흐름표 데이터 리스트
        """
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
            reports_key = "annualReports" if period == "annual" else "quarterlyReports"
            reports = data.get(reports_key, [])

            cash_flows = []
            for report in reports:
                cash_flow_data = {
                    "symbol": symbol,
                    "fiscal_date_ending": report.get("fiscalDateEnding", ""),
                    "reported_currency": report.get("reportedCurrency", "USD"),
                    "operating_cashflow": int(report.get("operatingCashflow", 0) or 0),
                    "payments_for_operating_activities": int(
                        report.get("paymentsForOperatingActivities", 0) or 0
                    ),
                    "proceeds_from_operating_activities": int(
                        report.get("proceedsFromOperatingActivities", 0) or 0
                    ),
                    "change_in_operating_liabilities": int(
                        report.get("changeInOperatingLiabilities", 0) or 0
                    ),
                    "change_in_operating_assets": int(
                        report.get("changeInOperatingAssets", 0) or 0
                    ),
                    "depreciation_depletion_amortization": int(
                        report.get("depreciationDepletionAndAmortization", 0) or 0
                    ),
                    "capital_expenditures": int(
                        report.get("capitalExpenditures", 0) or 0
                    ),
                    "change_in_receivables": int(
                        report.get("changeInReceivables", 0) or 0
                    ),
                    "change_in_inventory": int(report.get("changeInInventory", 0) or 0),
                    "profit_loss": int(report.get("profitLoss", 0) or 0),
                    "cashflow_from_investment": int(
                        report.get("cashflowFromInvestment", 0) or 0
                    ),
                    "cashflow_from_financing": int(
                        report.get("cashflowFromFinancing", 0) or 0
                    ),
                    "proceeds_from_repayments_of_short_term_debt": int(
                        report.get("proceedsFromRepaymentsOfShortTermDebt", 0) or 0
                    ),
                    "payments_for_repurchase_of_common_stock": int(
                        report.get("paymentsForRepurchaseOfCommonStock", 0) or 0
                    ),
                    "payments_for_repurchase_of_equity": int(
                        report.get("paymentsForRepurchaseOfEquity", 0) or 0
                    ),
                    "payments_for_repurchase_of_preferred_stock": int(
                        report.get("paymentsForRepurchaseOfPreferredStock", 0) or 0
                    ),
                    "dividend_payout": int(report.get("dividendPayout", 0) or 0),
                    "dividend_payout_common_stock": int(
                        report.get("dividendPayoutCommonStock", 0) or 0
                    ),
                    "dividend_payout_preferred_stock": int(
                        report.get("dividendPayoutPreferredStock", 0) or 0
                    ),
                    "proceeds_from_issuance_of_common_stock": int(
                        report.get("proceedsFromIssuanceOfCommonStock", 0) or 0
                    ),
                    "proceeds_from_issuance_of_long_term_debt_and_capital_securities_net": int(
                        report.get(
                            "proceedsFromIssuanceOfLongTermDebtAndCapitalSecuritiesNet",
                            0,
                        )
                        or 0
                    ),
                    "proceeds_from_issuance_of_preferred_stock": int(
                        report.get("proceedsFromIssuanceOfPreferredStock", 0) or 0
                    ),
                    "proceeds_from_repayments_of_long_term_debt": int(
                        report.get("proceedsFromRepaymentsOfLongTermDebt", 0) or 0
                    ),
                    "proceeds_from_sale_of_treasury_stock": int(
                        report.get("proceedsFromSaleOfTreasuryStock", 0) or 0
                    ),
                    "change_in_cash_and_cash_equivalents": int(
                        report.get("changeInCashAndCashEquivalents", 0) or 0
                    ),
                    "change_in_exchange_rate": int(
                        report.get("changeInExchangeRate", 0) or 0
                    ),
                    "net_income": int(report.get("netIncome", 0) or 0),
                }

                cash_flows.append(CashFlow(**cash_flow_data))

            logger.info(f"Fetched {len(cash_flows)} cash flows for {symbol}")
            return cash_flows

        except Exception as e:
            logger.error(f"Failed to get cash flow for {symbol}: {e}")
            return []

    async def get_earnings(self, symbol: str) -> List[Earnings]:
        """실적 발표 데이터 조회 (Alpha Vantage EARNINGS API)

        Args:
            symbol: 주식 심볼

        Returns:
            실적 발표 데이터 리스트
        """
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
            annual_earnings = data.get("annualEarnings", [])
            for earning in annual_earnings:
                earnings_data = {
                    "symbol": symbol,
                    "fiscal_date_ending": earning.get("fiscalDateEnding", ""),
                    "reported_eps": float(earning.get("reportedEPS", 0) or 0),
                    "period_type": "annual",
                    "reported_date": "",  # Annual earnings에는 reported date가 없음
                    "surprise": None,
                    "surprise_percentage": None,
                }
                earnings_list.append(Earnings(**earnings_data))

            # Quarterly earnings
            quarterly_earnings = data.get("quarterlyEarnings", [])
            for earning in quarterly_earnings:
                earnings_data = {
                    "symbol": symbol,
                    "fiscal_date_ending": earning.get("fiscalDateEnding", ""),
                    "reported_eps": float(earning.get("reportedEPS", 0) or 0),
                    "period_type": "quarterly",
                    "reported_date": earning.get("reportedDate", ""),
                    "estimated_eps": float(earning.get("estimatedEPS", 0) or 0),
                    "surprise": float(earning.get("surprise", 0) or 0),
                    "surprise_percentage": float(
                        earning.get("surprisePercentage", 0) or 0
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
                        "market_capitalization": self._safe_decimal(
                            data.get("MarketCapitalization")
                        ),
                        "ebitda": self._safe_decimal(data.get("EBITDA")),
                        "pe_ratio": self._safe_decimal(data.get("PERatio")),
                        "peg_ratio": self._safe_decimal(data.get("PEGRatio")),
                        "book_value": self._safe_decimal(data.get("BookValue")),
                        "dividend_per_share": self._safe_decimal(
                            data.get("DividendPerShare")
                        ),
                        "dividend_yield": self._safe_decimal(data.get("DividendYield")),
                        "eps": self._safe_decimal(data.get("EPS")),
                        "revenue_per_share_ttm": self._safe_decimal(
                            data.get("RevenuePerShareTTM")
                        ),
                        "profit_margin": self._safe_decimal(data.get("ProfitMargin")),
                        "operating_margin_ttm": self._safe_decimal(
                            data.get("OperatingMarginTTM")
                        ),
                        "return_on_assets_ttm": self._safe_decimal(
                            data.get("ReturnOnAssetsTTM")
                        ),
                        "return_on_equity_ttm": self._safe_decimal(
                            data.get("ReturnOnEquityTTM")
                        ),
                        "revenue_ttm": self._safe_decimal(data.get("RevenueTTM")),
                        "gross_profit_ttm": self._safe_decimal(
                            data.get("GrossProfitTTM")
                        ),
                        "diluted_eps_ttm": self._safe_decimal(
                            data.get("DilutedEPSTTM")
                        ),
                        "quarterly_earnings_growth_yoy": self._safe_decimal(
                            data.get("QuarterlyEarningsGrowthYOY")
                        ),
                        "quarterly_revenue_growth_yoy": self._safe_decimal(
                            data.get("QuarterlyRevenueGrowthYOY")
                        ),
                        "analyst_target_price": self._safe_decimal(
                            data.get("AnalystTargetPrice")
                        ),
                        "trailing_pe": self._safe_decimal(data.get("TrailingPE")),
                        "forward_pe": self._safe_decimal(data.get("ForwardPE")),
                        "price_to_sales_ratio_ttm": self._safe_decimal(
                            data.get("PriceToSalesRatioTTM")
                        ),
                        "price_to_book_ratio": self._safe_decimal(
                            data.get("PriceToBookRatio")
                        ),
                        "ev_to_revenue": self._safe_decimal(data.get("EVToRevenue")),
                        "ev_to_ebitda": self._safe_decimal(data.get("EVToEBITDA")),
                        "beta": self._safe_decimal(data.get("Beta")),
                        "week_52_high": self._safe_decimal(data.get("52WeekHigh")),
                        "week_52_low": self._safe_decimal(data.get("52WeekLow")),
                        "day_50_moving_average": self._safe_decimal(
                            data.get("50DayMovingAverage")
                        ),
                        "day_200_moving_average": self._safe_decimal(
                            data.get("200DayMovingAverage")
                        ),
                        "shares_outstanding": self._safe_decimal(
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

    def _safe_decimal(self, value):
        """문자열을 안전하게 Decimal로 변환"""
        if value is None or value == "None" or value == "":
            return None
        try:
            from decimal import Decimal

            return Decimal(str(value))
        except Exception:
            return None
            return None

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
