"""
Fundamental analysis data API schemas
기업 기본 분석 데이터 API 스키마들
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from decimal import Decimal

from .base import (
    DataResponse,
    BulkDataResponse,
    PaginatedResponse,
    SymbolParams,
    DateRangeParams,
    SortParams,
)


# Request Schemas
class CompanyOverviewRequest(SymbolParams):
    """기업 개요 요청 스키마"""

    include_metrics: bool = Field(True, description="기본 메트릭 포함 여부")
    include_technicals: bool = Field(False, description="기술적 지표 포함 여부")


class FinancialStatementRequest(SymbolParams, SortParams):
    """재무제표 요청 스키마"""

    period: str = Field(
        "annual", pattern="^(annual|quarterly)$", description="기간 (연간/분기)"
    )
    limit: int = Field(5, ge=1, le=20, description="결과 수 제한")


class EarningsRequest(SymbolParams, DateRangeParams, SortParams):
    """실적 발표 요청 스키마"""

    include_estimates: bool = Field(True, description="예상치 포함 여부")


class BulkFundamentalRequest(BaseModel):
    """대량 기업 분석 데이터 요청"""

    symbols: List[str] = Field(..., description="주식 심볼 목록")
    data_types: List[str] = Field(..., description="요청할 데이터 유형")
    period: str = Field("annual", pattern="^(annual|quarterly|ttm)$", description="기간")


# Response Data Models
class CompanyOverviewData(BaseModel):
    """기업 개요 응답 모델"""

    symbol: str = Field(..., description="주식 심볼")
    name: str = Field(..., description="회사명")
    exchange: str = Field(..., description="거래소")
    sector: Optional[str] = Field(None, description="섹터")
    industry: Optional[str] = Field(None, description="산업")
    description: Optional[str] = Field(None, description="회사 설명")

    # 기본 정보
    currency: str = Field(default="USD", description="통화")
    country: Optional[str] = Field(None, description="국가")
    fiscal_year_end: Optional[str] = Field(None, description="회계연도 종료월")
    latest_quarter: Optional[datetime] = Field(None, description="최근 분기")

    # 기본 메트릭
    market_capitalization: Optional[Decimal] = Field(None, description="시가총액")
    ebitda: Optional[Decimal] = Field(None, description="EBITDA")
    pe_ratio: Optional[Decimal] = Field(None, description="PER")
    peg_ratio: Optional[Decimal] = Field(None, description="PEG 비율")
    book_value: Optional[Decimal] = Field(None, description="장부가치")
    dividend_per_share: Optional[Decimal] = Field(None, description="주당 배당금")
    dividend_yield: Optional[Decimal] = Field(None, description="배당 수익률 (%)")
    eps: Optional[Decimal] = Field(None, description="주당 순이익")

    # 수익성 지표
    revenue_per_share_ttm: Optional[Decimal] = Field(None, description="주당 매출(TTM)")
    profit_margin: Optional[Decimal] = Field(None, description="순이익률 (%)")
    operating_margin_ttm: Optional[Decimal] = Field(None, description="영업이익률(TTM) (%)")
    return_on_assets_ttm: Optional[Decimal] = Field(None, description="총자산수익률(TTM) (%)")
    return_on_equity_ttm: Optional[Decimal] = Field(
        None, description="자기자본수익률(TTM) (%)"
    )
    revenue_ttm: Optional[Decimal] = Field(None, description="매출(TTM)")
    gross_profit_ttm: Optional[Decimal] = Field(None, description="매출총이익(TTM)")

    # 기술적 지표
    fifty_two_week_high: Optional[Decimal] = Field(None, description="52주 최고가")
    fifty_two_week_low: Optional[Decimal] = Field(None, description="52주 최저가")
    fifty_day_moving_average: Optional[Decimal] = Field(None, description="50일 이동평균")
    two_hundred_day_moving_average: Optional[Decimal] = Field(
        None, description="200일 이동평균"
    )
    shares_outstanding: Optional[int] = Field(None, description="발행주식수")
    beta: Optional[Decimal] = Field(None, description="베타")
    analyst_target_price: Optional[Decimal] = Field(None, description="목표 주가")


class IncomeStatementData(BaseModel):
    """손익계산서 응답 모델"""

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

    # 세전/세후 이익
    income_before_tax: Optional[Decimal] = Field(None, description="세전이익")
    income_tax_expense: Optional[Decimal] = Field(None, description="법인세비용")
    net_income: Optional[Decimal] = Field(None, description="순이익")

    # 주당 지표
    basic_shares_outstanding: Optional[int] = Field(None, description="기본 주식수")
    diluted_shares_outstanding: Optional[int] = Field(None, description="희석 주식수")
    basic_eps: Optional[Decimal] = Field(None, description="기본 주당순이익")
    diluted_eps: Optional[Decimal] = Field(None, description="희석 주당순이익")


class BalanceSheetData(BaseModel):
    """재무상태표 응답 모델"""

    symbol: str = Field(..., description="주식 심볼")
    fiscal_date_ending: datetime = Field(..., description="회계연도 종료일")
    reported_currency: str = Field(default="USD", description="보고 통화")

    # 자산
    total_assets: Optional[Decimal] = Field(None, description="총자산")
    total_current_assets: Optional[Decimal] = Field(None, description="총 유동자산")
    cash_and_cash_equivalents: Optional[Decimal] = Field(None, description="현금 및 현금성자산")
    inventory: Optional[Decimal] = Field(None, description="재고자산")
    current_net_receivables: Optional[Decimal] = Field(None, description="유동 순매출채권")
    property_plant_equipment: Optional[Decimal] = Field(None, description="유형자산")
    goodwill: Optional[Decimal] = Field(None, description="영업권")
    intangible_assets: Optional[Decimal] = Field(None, description="무형자산")

    # 부채
    total_liabilities: Optional[Decimal] = Field(None, description="총부채")
    total_current_liabilities: Optional[Decimal] = Field(None, description="총 유동부채")
    current_accounts_payable: Optional[Decimal] = Field(None, description="유동 매입채무")
    current_debt: Optional[Decimal] = Field(None, description="유동부채")
    long_term_debt: Optional[Decimal] = Field(None, description="장기부채")

    # 자기자본
    total_shareholder_equity: Optional[Decimal] = Field(None, description="총 자기자본")
    retained_earnings: Optional[Decimal] = Field(None, description="이익잉여금")
    common_stock: Optional[Decimal] = Field(None, description="보통주")
    treasury_stock: Optional[Decimal] = Field(None, description="자기주식")
    common_stock_shares_outstanding: Optional[int] = Field(
        None, description="보통주 발행주식수"
    )


class CashFlowData(BaseModel):
    """현금흐름표 응답 모델"""

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
    cashflow_from_investment: Optional[Decimal] = Field(None, description="투자활동 현금흐름")

    # 재무활동 현금흐름
    cashflow_from_financing: Optional[Decimal] = Field(None, description="재무활동 현금흐름")
    dividend_payments: Optional[Decimal] = Field(None, description="배당금 지급")
    payments_for_repurchase_of_common_stock: Optional[Decimal] = Field(
        None, description="자기주식 취득지출"
    )

    # 순현금흐름
    change_in_cash_and_cash_equivalents: Optional[Decimal] = Field(
        None, description="현금 및 현금성자산 변동"
    )


class EarningsData(BaseModel):
    """실적 발표 응답 모델"""

    symbol: str = Field(..., description="주식 심볼")
    fiscal_date_ending: datetime = Field(..., description="회계연도 종료일")
    reported_date: datetime = Field(..., description="발표일")

    # 실적 데이터
    reported_eps: Optional[Decimal] = Field(None, description="발표 EPS")
    estimated_eps: Optional[Decimal] = Field(None, description="예상 EPS")
    surprise: Optional[Decimal] = Field(None, description="서프라이즈")
    surprise_percentage: Optional[Decimal] = Field(None, description="서프라이즈 비율 (%)")


# 종합 분석 데이터 모델
class FundamentalAnalysisData(BaseModel):
    """종합 기본 분석 데이터"""

    symbol: str = Field(..., description="주식 심볼")
    analysis_date: datetime = Field(..., description="분석 날짜")

    # 밸류에이션 지표
    pe_ratio: Optional[Decimal] = Field(None, description="PER")
    pb_ratio: Optional[Decimal] = Field(None, description="PBR")
    ps_ratio: Optional[Decimal] = Field(None, description="PSR")
    ev_ebitda: Optional[Decimal] = Field(None, description="EV/EBITDA")

    # 수익성 지표
    roe: Optional[Decimal] = Field(None, description="자기자본수익률 (%)")
    roa: Optional[Decimal] = Field(None, description="총자산수익률 (%)")
    gross_margin: Optional[Decimal] = Field(None, description="매출총이익률 (%)")
    operating_margin: Optional[Decimal] = Field(None, description="영업이익률 (%)")
    net_margin: Optional[Decimal] = Field(None, description="순이익률 (%)")

    # 성장성 지표
    revenue_growth_yoy: Optional[Decimal] = Field(None, description="매출 전년대비 성장률 (%)")
    eps_growth_yoy: Optional[Decimal] = Field(None, description="EPS 전년대비 성장률 (%)")

    # 안정성 지표
    debt_to_equity: Optional[Decimal] = Field(None, description="부채비율")
    current_ratio: Optional[Decimal] = Field(None, description="유동비율")
    quick_ratio: Optional[Decimal] = Field(None, description="당좌비율")

    # 배당 관련
    dividend_yield: Optional[Decimal] = Field(None, description="배당 수익률 (%)")
    payout_ratio: Optional[Decimal] = Field(None, description="배당성향 (%)")

    pass


class BalanceSheetListResponse(BulkDataResponse[BalanceSheetData]):
    """재무상태표 목록 응답 스키마"""

    pass


class CashFlowListResponse(BulkDataResponse[CashFlowData]):
    """현금흐름표 목록 응답 스키마"""

    pass


class EarningsListResponse(PaginatedResponse[EarningsData]):
    """실적 발표 목록 응답 스키마"""

    pass


class FundamentalAnalysisResponse(DataResponse[FundamentalAnalysisData]):
    """종합 기본 분석 응답 스키마"""

    pass


# 비교 분석을 위한 스키마들
class PeerComparisonRequest(BaseModel):
    """동종업계 비교 분석 요청"""

    symbol: str = Field(..., description="기준 주식 심볼")
    comparison_metrics: List[str] = Field(..., description="비교할 메트릭 목록")
    include_sector_average: bool = Field(True, description="섹터 평균 포함 여부")
    limit: int = Field(10, ge=1, le=50, description="비교 대상 수 제한")


class PeerComparisonData(BaseModel):
    """동종업계 비교 데이터"""

    base_symbol: str = Field(..., description="기준 심볼")
    peer_symbol: str = Field(..., description="비교 대상 심볼")
    peer_name: str = Field(..., description="비교 대상 회사명")
    similarity_score: float = Field(..., description="유사도 점수", ge=0, le=1)

    # 비교 메트릭들 (동적으로 추가)
    metrics: dict = Field(..., description="비교 메트릭 데이터")


class PeerComparisonResponse(BulkDataResponse[PeerComparisonData]):
    """동종업계 비교 분석 응답 스키마"""

    pass


class SectorAnalysisData(BaseModel):
    """섹터 분석 데이터"""

    sector: str = Field(..., description="섹터명")
    analysis_date: datetime = Field(..., description="분석 날짜")

    # 섹터 통계
    total_companies: int = Field(..., description="총 기업 수")
    average_market_cap: Optional[Decimal] = Field(None, description="평균 시가총액")
    median_pe_ratio: Optional[Decimal] = Field(None, description="PER 중간값")
    average_dividend_yield: Optional[Decimal] = Field(None, description="평균 배당수익률")

    # 성과 지표
    sector_return_ytd: Optional[Decimal] = Field(None, description="섹터 연초 대비 수익률 (%)")
    sector_return_1m: Optional[Decimal] = Field(None, description="섹터 1개월 수익률 (%)")
    sector_return_3m: Optional[Decimal] = Field(None, description="섹터 3개월 수익률 (%)")
    sector_return_1y: Optional[Decimal] = Field(None, description="섹터 1년 수익률 (%)")


class SectorAnalysisResponse(DataResponse[SectorAnalysisData]):
    """섹터 분석 응답 스키마"""

    pass


# API Response Models
class CompanyOverviewResponse(DataResponse[CompanyOverviewData]):
    """기업 개요 조회 응답 스키마"""

    pass


class IncomeStatementResponse(BulkDataResponse[IncomeStatementData]):
    """손익계산서 조회 응답 스키마"""

    pass


class BalanceSheetResponse(BulkDataResponse[BalanceSheetData]):
    """재무상태표 조회 응답 스키마"""

    pass


class CashFlowResponse(BulkDataResponse[CashFlowData]):
    """현금흐름표 조회 응답 스키마"""

    pass


class EarningsResponse(BulkDataResponse[EarningsData]):
    """실적 데이터 조회 응답 스키마"""

    pass
