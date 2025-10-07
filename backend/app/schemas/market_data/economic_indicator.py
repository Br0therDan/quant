"""
Economic indicator data API schemas
경제 지표 데이터 API 스키마들
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from decimal import Decimal

from .base import (
    DataResponse,
    BulkDataResponse,
    PaginatedResponse,
    DateRangeParams,
    SortParams,
)


# Request Schemas
class EconomicIndicatorRequest(DateRangeParams, SortParams):
    """경제 지표 요청 스키마"""

    indicator_name: str = Field(..., description="지표명")
    country: str = Field("US", description="국가코드")
    frequency: Optional[str] = Field(None, description="발표 주기 필터")


class BulkEconomicIndicatorRequest(DateRangeParams):
    """대량 경제 지표 요청 스키마"""

    indicators: List[str] = Field(..., description="지표명 목록")
    countries: List[str] = Field(["US"], description="국가 목록")


class GDPRequest(DateRangeParams, SortParams):
    """GDP 지표 요청 스키마"""

    country: str = Field("US", description="국가코드")
    include_growth_rate: bool = Field(True, description="성장률 포함 여부")


class InflationRequest(DateRangeParams, SortParams):
    """인플레이션 지표 요청 스키마"""

    country: str = Field("US", description="국가코드")
    include_core: bool = Field(True, description="근원 인플레이션 포함 여부")


class InterestRateRequest(DateRangeParams, SortParams):
    """금리 지표 요청 스키마"""

    country: str = Field("US", description="국가코드")
    rate_types: List[str] = Field(["federal_funds"], description="금리 유형 목록")


# Response Data Models
class EconomicIndicatorData(BaseModel):
    """경제 지표 응답 모델"""

    indicator_name: str = Field(..., description="지표명")
    date: datetime = Field(..., description="기준일")
    value: Decimal = Field(..., description="지표값")
    unit: Optional[str] = Field(None, description="단위")
    frequency: str = Field(..., description="발표 주기")
    country: str = Field(..., description="국가코드")
    data_source: str = Field(..., description="데이터 출처")


class GDPData(BaseModel):
    """GDP 지표 응답 모델"""

    date: datetime = Field(..., description="기준일")
    country: str = Field(..., description="국가코드")

    gdp_nominal: Optional[Decimal] = Field(None, description="명목 GDP")
    gdp_real: Optional[Decimal] = Field(None, description="실질 GDP")
    gdp_per_capita: Optional[Decimal] = Field(None, description="1인당 GDP")
    gdp_growth_rate: Optional[Decimal] = Field(None, description="GDP 성장률 (%)")
    gdp_quarterly: Optional[Decimal] = Field(None, description="분기별 GDP")

    unit: str = Field(default="Billions USD", description="단위")
    frequency: str = Field(default="quarterly", description="발표 주기")


class InflationData(BaseModel):
    """인플레이션 지표 응답 모델"""

    date: datetime = Field(..., description="기준일")
    country: str = Field(..., description="국가코드")

    cpi: Optional[Decimal] = Field(None, description="소비자물가지수")
    cpi_change: Optional[Decimal] = Field(None, description="CPI 변화율 (%)")
    core_cpi: Optional[Decimal] = Field(None, description="근원 CPI")
    core_cpi_change: Optional[Decimal] = Field(None, description="근원 CPI 변화율 (%)")
    ppi: Optional[Decimal] = Field(None, description="생산자물가지수")
    ppi_change: Optional[Decimal] = Field(None, description="PPI 변화율 (%)")


class InterestRateData(BaseModel):
    """금리 지표 응답 모델"""

    date: datetime = Field(..., description="기준일")
    country: str = Field(..., description="국가코드")

    federal_funds_rate: Optional[Decimal] = Field(None, description="연방기금금리 (%)")
    discount_rate: Optional[Decimal] = Field(None, description="할인율 (%)")
    treasury_bill_3m: Optional[Decimal] = Field(None, description="3개월 국채 수익률 (%)")
    treasury_note_2y: Optional[Decimal] = Field(None, description="2년 국채 수익률 (%)")
    treasury_note_5y: Optional[Decimal] = Field(None, description="5년 국채 수익률 (%)")
    treasury_note_10y: Optional[Decimal] = Field(None, description="10년 국채 수익률 (%)")
    treasury_bond_30y: Optional[Decimal] = Field(None, description="30년 국채 수익률 (%)")

    yield_spread_10y_2y: Optional[Decimal] = Field(
        None, description="10년-2년 국채 스프레드 (%)"
    )
    yield_spread_10y_3m: Optional[Decimal] = Field(
        None, description="10년-3개월 국채 스프레드 (%)"
    )


class EmploymentData(BaseModel):
    """고용 지표 응답 모델"""

    date: datetime = Field(..., description="기준일")
    country: str = Field(..., description="국가코드")

    unemployment_rate: Optional[Decimal] = Field(None, description="실업률 (%)")
    employment_rate: Optional[Decimal] = Field(None, description="고용률 (%)")
    labor_force_participation: Optional[Decimal] = Field(
        None, description="경제활동참가율 (%)"
    )
    nonfarm_payrolls: Optional[int] = Field(None, description="비농업 고용 변화")
    initial_claims: Optional[int] = Field(None, description="신규 실업수당 신청")
    continuing_claims: Optional[int] = Field(None, description="계속 실업수당 신청")


class ManufacturingData(BaseModel):
    """제조업 지표 응답 모델"""

    date: datetime = Field(..., description="기준일")
    country: str = Field(..., description="국가코드")

    pmi: Optional[Decimal] = Field(None, description="제조업 PMI")
    industrial_production: Optional[Decimal] = Field(None, description="산업생산지수")
    capacity_utilization: Optional[Decimal] = Field(None, description="설비가동률 (%)")
    new_orders: Optional[Decimal] = Field(None, description="신규 수주")
    factory_orders: Optional[Decimal] = Field(None, description="공장 수주")
    durable_goods_orders: Optional[Decimal] = Field(None, description="내구재 수주")


class ConsumerSentimentData(BaseModel):
    """소비자 심리 지표 응답 모델"""

    date: datetime = Field(..., description="기준일")
    country: str = Field(..., description="국가코드")

    consumer_confidence: Optional[Decimal] = Field(None, description="소비자 신뢰지수")
    consumer_sentiment: Optional[Decimal] = Field(None, description="소비자 심리지수")
    retail_sales: Optional[Decimal] = Field(None, description="소매판매 변화율 (%)")
    personal_consumption: Optional[Decimal] = Field(None, description="개인소비지출")
    personal_income: Optional[Decimal] = Field(None, description="개인소득")
    personal_saving_rate: Optional[Decimal] = Field(None, description="개인저축률 (%)")


# Response Schemas
class EconomicIndicatorListResponse(PaginatedResponse[EconomicIndicatorData]):
    """경제 지표 목록 응답 스키마"""

    pass


class GDPListResponse(BulkDataResponse[GDPData]):
    """GDP 지표 목록 응답 스키마"""

    pass


class InflationListResponse(BulkDataResponse[InflationData]):
    """인플레이션 지표 목록 응답 스키마"""

    pass


class InterestRateListResponse(BulkDataResponse[InterestRateData]):
    """금리 지표 목록 응답 스키마"""

    pass


class EmploymentListResponse(BulkDataResponse[EmploymentData]):
    """고용 지표 목록 응답 스키마"""

    pass


class ManufacturingListResponse(BulkDataResponse[ManufacturingData]):
    """제조업 지표 목록 응답 스키마"""

    pass


class ConsumerSentimentListResponse(BulkDataResponse[ConsumerSentimentData]):
    """소비자 심리 지표 목록 응답 스키마"""

    pass


# 종합 경제 분석 스키마
class EconomicOverviewData(BaseModel):
    """경제 종합 분석 데이터"""

    country: str = Field(..., description="국가코드")
    analysis_date: datetime = Field(..., description="분석 날짜")

    # 핵심 지표
    gdp_growth_rate: Optional[Decimal] = Field(None, description="GDP 성장률 (%)")
    inflation_rate: Optional[Decimal] = Field(None, description="인플레이션율 (%)")
    unemployment_rate: Optional[Decimal] = Field(None, description="실업률 (%)")
    interest_rate: Optional[Decimal] = Field(None, description="기준금리 (%)")

    # 경제 상태 평가
    economic_status: Optional[str] = Field(
        None, description="경제 상태 (expansion, recession, recovery)"
    )
    recession_probability: Optional[Decimal] = Field(None, description="경기침체 확률 (%)")

    # 전월 대비 변화
    gdp_change_mom: Optional[Decimal] = Field(None, description="GDP 전월 대비 변화 (%)")
    inflation_change_mom: Optional[Decimal] = Field(
        None, description="인플레이션 전월 대비 변화 (%)"
    )
    unemployment_change_mom: Optional[Decimal] = Field(
        None, description="실업률 전월 대비 변화 (%)"
    )


class EconomicOverviewResponse(DataResponse[EconomicOverviewData]):
    """경제 종합 분석 응답 스키마"""

    pass
