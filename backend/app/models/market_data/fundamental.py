"""
Fundamental analysis data models
기업 기본 분석 관련 데이터 모델들
"""

from datetime import datetime
from typing import Optional
from pydantic import Field
from decimal import Decimal

from .base import BaseMarketDataDocument, DataQualityMixin


class CompanyOverview(BaseMarketDataDocument, DataQualityMixin):
    """기업 개요 모델"""

    symbol: str = Field(..., description="주식 심볼")
    name: str = Field(..., description="회사명")
    exchange: str = Field(..., description="거래소")
    sector: Optional[str] = Field(None, description="섹터")
    industry: Optional[str] = Field(None, description="산업")

    # 기본 정보
    description: Optional[str] = Field(None, description="회사 설명")
    cik: Optional[str] = Field(None, description="CIK 번호")
    fiscal_year_end: Optional[str] = Field(None, description="회계연도 종료월")
    latest_quarter: Optional[datetime] = Field(None, description="최근 분기")

    # 거래 정보
    currency: str = Field(default="USD", description="통화")
    country: Optional[str] = Field(None, description="국가")

    # 기본 메트릭
    market_capitalization: Optional[Decimal] = Field(None, description="시가총액", ge=0)
    ebitda: Optional[Decimal] = Field(None, description="EBITDA")
    pe_ratio: Optional[Decimal] = Field(None, description="PER", ge=0)
    peg_ratio: Optional[Decimal] = Field(None, description="PEG 비율")
    book_value: Optional[Decimal] = Field(None, description="장부가치")
    dividend_per_share: Optional[Decimal] = Field(None, description="주당 배당금")
    dividend_yield: Optional[Decimal] = Field(None, description="배당 수익률 (%)", ge=0)

    # 거래량 및 베타
    eps: Optional[Decimal] = Field(None, description="주당 순이익")
    revenue_per_share_ttm: Optional[Decimal] = Field(None, description="주당 매출(TTM)")
    profit_margin: Optional[Decimal] = Field(None, description="순이익률 (%)")
    operating_margin_ttm: Optional[Decimal] = Field(None, description="영업이익률(TTM) (%)")
    return_on_assets_ttm: Optional[Decimal] = Field(None, description="총자산수익률(TTM) (%)")
    return_on_equity_ttm: Optional[Decimal] = Field(
        None, description="자기자본수익률(TTM) (%)"
    )
    revenue_ttm: Optional[Decimal] = Field(None, description="매출(TTM)", ge=0)
    gross_profit_ttm: Optional[Decimal] = Field(None, description="매출총이익(TTM)")

    # 기술적 지표
    fifty_two_week_high: Optional[Decimal] = Field(None, description="52주 최고가", gt=0)
    fifty_two_week_low: Optional[Decimal] = Field(None, description="52주 최저가", gt=0)
    fifty_day_moving_average: Optional[Decimal] = Field(
        None, description="50일 이동평균", gt=0
    )
    two_hundred_day_moving_average: Optional[Decimal] = Field(
        None, description="200일 이동평균", gt=0
    )
    shares_outstanding: Optional[int] = Field(None, description="발행주식수", ge=0)
    shares_float: Optional[int] = Field(None, description="유통주식수", ge=0)
    shares_short: Optional[int] = Field(None, description="공매도 주식수", ge=0)
    short_ratio: Optional[Decimal] = Field(None, description="공매도 비율", ge=0)
    short_percent_outstanding: Optional[Decimal] = Field(
        None, description="공매도 비율 (%)", ge=0
    )
    short_percent_float: Optional[Decimal] = Field(
        None, description="유통주식 공매도 비율 (%)", ge=0
    )

    # 베타 및 기타
    beta: Optional[Decimal] = Field(None, description="베타")
    analyst_target_price: Optional[Decimal] = Field(None, description="목표 주가", gt=0)

    class Settings:
        name = "company_overviews"
        indexes = [
            "symbol",
            "exchange",
            "sector",
            "industry",
            "market_capitalization",
            "created_at",
        ]

    def calculate_quality_score(self) -> float:
        """데이터 품질 점수 계산"""
        score = 100.0
        required_fields = ["name", "exchange", "sector", "industry"]
        missing_required = sum(
            1 for field in required_fields if not getattr(self, field)
        )
        score -= missing_required * 20

        # 기본 메트릭이 있는지 확인
        if not self.market_capitalization:
            score -= 10
        if not self.pe_ratio:
            score -= 10
        if not self.eps:
            score -= 10

        return max(score, 0.0)


class IncomeStatement(BaseMarketDataDocument, DataQualityMixin):
    """손익계산서 모델"""

    symbol: str = Field(..., description="주식 심볼")
    fiscal_date_ending: datetime = Field(..., description="회계연도 종료일")
    reported_currency: str = Field(default="USD", description="보고 통화")

    # 매출 관련
    total_revenue: Optional[Decimal] = Field(None, description="총 매출")
    cost_of_revenue: Optional[Decimal] = Field(None, description="매출원가")
    gross_profit: Optional[Decimal] = Field(None, description="매출총이익")

    # 운영비용
    research_and_development: Optional[Decimal] = Field(None, description="연구개발비")
    selling_general_administrative: Optional[Decimal] = Field(None, description="판매관리비")
    operating_expenses: Optional[Decimal] = Field(None, description="영업비용")
    operating_income: Optional[Decimal] = Field(None, description="영업이익")

    # 기타 수익/비용
    interest_income: Optional[Decimal] = Field(None, description="이자수익")
    interest_expense: Optional[Decimal] = Field(None, description="이자비용")
    total_other_income_expense_net: Optional[Decimal] = Field(None, description="기타손익")

    # 세전/세후 이익
    income_before_tax: Optional[Decimal] = Field(None, description="세전이익")
    income_tax_expense: Optional[Decimal] = Field(None, description="법인세비용")
    net_income: Optional[Decimal] = Field(None, description="순이익")

    # 주당 지표
    basic_shares_outstanding: Optional[int] = Field(None, description="기본 주식수", ge=0)
    diluted_shares_outstanding: Optional[int] = Field(None, description="희석 주식수", ge=0)
    basic_eps: Optional[Decimal] = Field(None, description="기본 주당순이익")
    diluted_eps: Optional[Decimal] = Field(None, description="희석 주당순이익")

    class Settings:
        name = "income_statements"
        indexes = [
            [("symbol", 1), ("fiscal_date_ending", -1)],
            "symbol",
            "fiscal_date_ending",
            "total_revenue",
            "net_income",
            "created_at",
        ]

    def calculate_quality_score(self) -> float:
        """데이터 품질 점수 계산"""
        score = 100.0
        core_fields = ["total_revenue", "operating_income", "net_income"]
        missing_core = sum(1 for field in core_fields if getattr(self, field) is None)
        score -= missing_core * 25

        # 데이터 일관성 검증
        if self.total_revenue and self.cost_of_revenue and self.gross_profit:
            expected_gross = self.total_revenue - self.cost_of_revenue
            if abs(expected_gross - self.gross_profit) > abs(
                self.gross_profit * Decimal("0.01")
            ):
                score -= 15

        return max(score, 0.0)


class BalanceSheet(BaseMarketDataDocument, DataQualityMixin):
    """재무상태표 모델"""

    symbol: str = Field(..., description="주식 심볼")
    fiscal_date_ending: datetime = Field(..., description="회계연도 종료일")
    reported_currency: str = Field(default="USD", description="보고 통화")

    # 유동자산
    total_current_assets: Optional[Decimal] = Field(None, description="총 유동자산")
    cash_and_cash_equivalents: Optional[Decimal] = Field(None, description="현금 및 현금성자산")
    cash_and_short_term_investments: Optional[Decimal] = Field(
        None, description="현금 및 단기투자"
    )
    inventory: Optional[Decimal] = Field(None, description="재고자산")
    current_net_receivables: Optional[Decimal] = Field(None, description="유동 순매출채권")

    # 총자산
    total_assets: Optional[Decimal] = Field(None, description="총자산")
    property_plant_equipment: Optional[Decimal] = Field(None, description="유형자산")
    goodwill: Optional[Decimal] = Field(None, description="영업권")
    intangible_assets: Optional[Decimal] = Field(None, description="무형자산")

    # 유동부채
    total_current_liabilities: Optional[Decimal] = Field(None, description="총 유동부채")
    current_accounts_payable: Optional[Decimal] = Field(None, description="유동 매입채무")
    deferred_revenue: Optional[Decimal] = Field(None, description="이연수익")
    current_debt: Optional[Decimal] = Field(None, description="유동부채")

    # 총부채
    total_liabilities: Optional[Decimal] = Field(None, description="총부채")
    total_non_current_liabilities: Optional[Decimal] = Field(
        None, description="총 비유동부채"
    )
    capital_lease_obligations: Optional[Decimal] = Field(None, description="자본리스의무")
    long_term_debt: Optional[Decimal] = Field(None, description="장기부채")

    # 자기자본
    total_shareholder_equity: Optional[Decimal] = Field(None, description="총 자기자본")
    treasury_stock: Optional[Decimal] = Field(None, description="자기주식")
    retained_earnings: Optional[Decimal] = Field(None, description="이익잉여금")
    common_stock: Optional[Decimal] = Field(None, description="보통주")
    common_stock_shares_outstanding: Optional[int] = Field(
        None, description="보통주 발행주식수", ge=0
    )

    class Settings:
        name = "balance_sheets"
        indexes = [
            [("symbol", 1), ("fiscal_date_ending", -1)],
            "symbol",
            "fiscal_date_ending",
            "total_assets",
            "total_liabilities",
            "total_shareholder_equity",
            "created_at",
        ]

    def calculate_quality_score(self) -> float:
        """데이터 품질 점수 계산"""
        score = 100.0

        # 핵심 필드 검증
        core_fields = ["total_assets", "total_liabilities", "total_shareholder_equity"]
        missing_core = sum(1 for field in core_fields if getattr(self, field) is None)
        score -= missing_core * 30

        # 회계 등식 검증: 자산 = 부채 + 자본
        if (
            self.total_assets is not None
            and self.total_liabilities is not None
            and self.total_shareholder_equity is not None
        ):
            assets = self.total_assets
            liabilities_equity = self.total_liabilities + self.total_shareholder_equity
            if abs(assets - liabilities_equity) > abs(assets * Decimal("0.01")):
                score -= 25

        return max(score, 0.0)


class CashFlow(BaseMarketDataDocument, DataQualityMixin):
    """현금흐름표 모델"""

    symbol: str = Field(..., description="주식 심볼")
    fiscal_date_ending: datetime = Field(..., description="회계연도 종료일")
    reported_currency: str = Field(default="USD", description="보고 통화")

    # 영업활동 현금흐름
    operating_cashflow: Optional[Decimal] = Field(None, description="영업활동 현금흐름")
    payments_for_operating_activities: Optional[Decimal] = Field(
        None, description="영업활동 현금지출"
    )
    proceeds_from_operating_activities: Optional[Decimal] = Field(
        None, description="영업활동 현금수입"
    )

    # 투자활동 현금흐름
    capital_expenditures: Optional[Decimal] = Field(None, description="자본적지출")
    proceeds_from_investment_activities: Optional[Decimal] = Field(
        None, description="투자활동 현금수입"
    )
    payments_for_investment_activities: Optional[Decimal] = Field(
        None, description="투자활동 현금지출"
    )
    cashflow_from_investment: Optional[Decimal] = Field(None, description="투자활동 현금흐름")

    # 재무활동 현금흐름
    cashflow_from_financing: Optional[Decimal] = Field(None, description="재무활동 현금흐름")
    proceeds_from_repayments_of_short_term_debt: Optional[Decimal] = Field(
        None, description="단기부채 상환수익"
    )
    payments_for_repurchase_of_common_stock: Optional[Decimal] = Field(
        None, description="자기주식 취득지출"
    )
    payments_for_repurchase_of_equity: Optional[Decimal] = Field(
        None, description="지분 재매입지출"
    )
    dividend_payments: Optional[Decimal] = Field(None, description="배당금 지급")

    # 순현금흐름
    change_in_cash_and_cash_equivalents: Optional[Decimal] = Field(
        None, description="현금 및 현금성자산 변동"
    )

    class Settings:
        name = "cash_flows"
        indexes = [
            [("symbol", 1), ("fiscal_date_ending", -1)],
            "symbol",
            "fiscal_date_ending",
            "operating_cashflow",
            "created_at",
        ]

    def calculate_quality_score(self) -> float:
        """데이터 품질 점수 계산"""
        score = 100.0

        # 핵심 필드 검증
        core_fields = [
            "operating_cashflow",
            "cashflow_from_investment",
            "cashflow_from_financing",
        ]
        missing_core = sum(1 for field in core_fields if getattr(self, field) is None)
        score -= missing_core * 25

        # 현금흐름 일관성 검증
        if (
            self.operating_cashflow is not None
            and self.cashflow_from_investment is not None
            and self.cashflow_from_financing is not None
            and self.change_in_cash_and_cash_equivalents is not None
        ):
            expected_change = (
                self.operating_cashflow
                + self.cashflow_from_investment
                + self.cashflow_from_financing
            )
            actual_change = self.change_in_cash_and_cash_equivalents
            if abs(expected_change - actual_change) > abs(
                actual_change * Decimal("0.05")
            ):
                score -= 20

        return max(score, 0.0)


class Earnings(BaseMarketDataDocument, DataQualityMixin):
    """실적 발표 모델"""

    symbol: str = Field(..., description="주식 심볼")
    fiscal_date_ending: datetime = Field(..., description="회계연도 종료일")
    reported_date: datetime = Field(..., description="발표일")

    # 실적 데이터
    reported_eps: Optional[Decimal] = Field(None, description="발표 EPS")
    estimated_eps: Optional[Decimal] = Field(None, description="예상 EPS")
    surprise: Optional[Decimal] = Field(None, description="서프라이즈")
    surprise_percentage: Optional[Decimal] = Field(None, description="서프라이즈 비율 (%)")

    class Settings:
        name = "earnings"
        indexes = [
            [("symbol", 1), ("fiscal_date_ending", -1)],
            [("symbol", 1), ("reported_date", -1)],
            "symbol",
            "fiscal_date_ending",
            "reported_date",
            "created_at",
        ]

    def calculate_quality_score(self) -> float:
        """데이터 품질 점수 계산"""
        score = 100.0

        if not self.reported_eps:
            score -= 40
        if not self.estimated_eps:
            score -= 20

        # 서프라이즈 계산 일관성 검증
        if self.reported_eps and self.estimated_eps and self.surprise:
            expected_surprise = self.reported_eps - self.estimated_eps
            if abs(expected_surprise - self.surprise) > abs(
                self.surprise * Decimal("0.01")
            ):
                score -= 20

        return max(score, 0.0)
