"""
Economic indicator data models
경제 지표 관련 데이터 모델들
"""

from datetime import datetime
from typing import Optional
from pydantic import Field
from decimal import Decimal

from .base import BaseMarketDataDocument, DataQualityMixin


class EconomicIndicator(BaseMarketDataDocument, DataQualityMixin):
    """경제 지표 기본 모델"""

    indicator_name: str = Field(..., description="지표명")
    date: datetime = Field(..., description="기준일")
    value: Decimal = Field(..., description="지표값")
    unit: Optional[str] = Field(None, description="단위")

    # 메타데이터
    frequency: str = Field(..., description="발표 주기 (monthly, quarterly, annual)")
    country: str = Field(default="US", description="국가코드")
    data_source: str = Field(..., description="데이터 출처")

    class Settings:
        name = "economic_indicators"
        indexes = [
            [("indicator_name", 1), ("date", -1)],
            "indicator_name",
            "date",
            "country",
            "created_at",
        ]

    def calculate_quality_score(self) -> float:
        """데이터 품질 점수 계산"""
        score = 100.0

        if not self.unit:
            score -= 10
        if not self.data_source:
            score -= 15

        return max(score, 0.0)


class GDP(BaseMarketDataDocument, DataQualityMixin):
    """GDP 관련 지표 모델"""

    date: datetime = Field(..., description="기준일")
    country: str = Field(default="US", description="국가코드")

    # GDP 관련 지표들
    gdp_nominal: Optional[Decimal] = Field(None, description="명목 GDP")
    gdp_real: Optional[Decimal] = Field(None, description="실질 GDP")
    gdp_per_capita: Optional[Decimal] = Field(None, description="1인당 GDP")
    gdp_growth_rate: Optional[Decimal] = Field(None, description="GDP 성장률 (%)")
    gdp_quarterly: Optional[Decimal] = Field(None, description="분기별 GDP")

    # 관련 메타데이터
    unit: str = Field(default="Billions USD", description="단위")
    frequency: str = Field(default="quarterly", description="발표 주기")

    class Settings:
        name = "gdp_indicators"
        indexes = [
            [("country", 1), ("date", -1)],
            "country",
            "date",
            "gdp_growth_rate",
            "created_at",
        ]

    def calculate_quality_score(self) -> float:
        """데이터 품질 점수 계산"""
        score = 100.0

        # 핵심 지표 확인
        if not self.gdp_real and not self.gdp_nominal:
            score -= 40
        if not self.gdp_growth_rate:
            score -= 20

        return max(score, 0.0)


class Inflation(BaseMarketDataDocument, DataQualityMixin):
    """인플레이션 지표 모델"""

    date: datetime = Field(..., description="기준일")
    country: str = Field(default="US", description="국가코드")

    # 인플레이션 지표들
    cpi: Optional[Decimal] = Field(None, description="소비자물가지수")
    cpi_change: Optional[Decimal] = Field(None, description="CPI 변화율 (%)")
    core_cpi: Optional[Decimal] = Field(None, description="근원 CPI")
    core_cpi_change: Optional[Decimal] = Field(None, description="근원 CPI 변화율 (%)")
    ppi: Optional[Decimal] = Field(None, description="생산자물가지수")
    ppi_change: Optional[Decimal] = Field(None, description="PPI 변화율 (%)")

    class Settings:
        name = "inflation_indicators"
        indexes = [
            [("country", 1), ("date", -1)],
            "country",
            "date",
            "cpi_change",
            "core_cpi_change",
            "created_at",
        ]

    def calculate_quality_score(self) -> float:
        """데이터 품질 점수 계산"""
        score = 100.0

        if not self.cpi and not self.cpi_change:
            score -= 35
        if not self.core_cpi_change:
            score -= 25

        return max(score, 0.0)


class InterestRate(BaseMarketDataDocument, DataQualityMixin):
    """금리 지표 모델"""

    date: datetime = Field(..., description="기준일")
    country: str = Field(default="US", description="국가코드")

    # 금리 관련 지표들
    federal_funds_rate: Optional[Decimal] = Field(None, description="연방기금금리 (%)")
    discount_rate: Optional[Decimal] = Field(None, description="할인율 (%)")
    treasury_bill_3m: Optional[Decimal] = Field(None, description="3개월 국채 수익률 (%)")
    treasury_note_2y: Optional[Decimal] = Field(None, description="2년 국채 수익률 (%)")
    treasury_note_5y: Optional[Decimal] = Field(None, description="5년 국채 수익률 (%)")
    treasury_note_10y: Optional[Decimal] = Field(None, description="10년 국채 수익률 (%)")
    treasury_bond_30y: Optional[Decimal] = Field(None, description="30년 국채 수익률 (%)")

    # 스프레드 지표
    yield_spread_10y_2y: Optional[Decimal] = Field(
        None, description="10년-2년 국채 스프레드 (%)"
    )
    yield_spread_10y_3m: Optional[Decimal] = Field(
        None, description="10년-3개월 국채 스프레드 (%)"
    )

    class Settings:
        name = "interest_rate_indicators"
        indexes = [
            [("country", 1), ("date", -1)],
            "country",
            "date",
            "federal_funds_rate",
            "treasury_note_10y",
            "yield_spread_10y_2y",
            "created_at",
        ]

    def calculate_quality_score(self) -> float:
        """데이터 품질 점수 계산"""
        score = 100.0

        # 핵심 금리 지표 확인
        key_rates = [
            self.federal_funds_rate,
            self.treasury_note_10y,
            self.treasury_bill_3m,
        ]
        missing_key = sum(1 for rate in key_rates if rate is None)
        score -= missing_key * 20

        # 스프레드 계산 검증
        if (
            self.treasury_note_10y is not None
            and self.treasury_note_2y is not None
            and self.yield_spread_10y_2y is not None
        ):
            expected_spread = self.treasury_note_10y - self.treasury_note_2y
            if abs(expected_spread - self.yield_spread_10y_2y) > Decimal("0.1"):
                score -= 15

        return max(score, 0.0)


class Employment(BaseMarketDataDocument, DataQualityMixin):
    """고용 지표 모델"""

    date: datetime = Field(..., description="기준일")
    country: str = Field(default="US", description="국가코드")

    # 고용 관련 지표들
    unemployment_rate: Optional[Decimal] = Field(None, description="실업률 (%)")
    employment_rate: Optional[Decimal] = Field(None, description="고용률 (%)")
    labor_force_participation: Optional[Decimal] = Field(
        None, description="경제활동참가율 (%)"
    )
    nonfarm_payrolls: Optional[int] = Field(None, description="비농업 고용 변화")
    initial_claims: Optional[int] = Field(None, description="신규 실업수당 신청")
    continuing_claims: Optional[int] = Field(None, description="계속 실업수당 신청")

    # 세부 고용 지표
    civilian_labor_force: Optional[int] = Field(None, description="민간 노동력")
    employed_persons: Optional[int] = Field(None, description="취업자 수")
    unemployed_persons: Optional[int] = Field(None, description="실업자 수")

    class Settings:
        name = "employment_indicators"
        indexes = [
            [("country", 1), ("date", -1)],
            "country",
            "date",
            "unemployment_rate",
            "nonfarm_payrolls",
            "created_at",
        ]

    def calculate_quality_score(self) -> float:
        """데이터 품질 점수 계산"""
        score = 100.0

        # 핵심 지표 확인
        if not self.unemployment_rate:
            score -= 30
        if not self.nonfarm_payrolls:
            score -= 20
        if not self.labor_force_participation:
            score -= 15

        return max(score, 0.0)


class Manufacturing(BaseMarketDataDocument, DataQualityMixin):
    """제조업 지표 모델"""

    date: datetime = Field(..., description="기준일")
    country: str = Field(default="US", description="국가코드")

    # 제조업 관련 지표들
    pmi: Optional[Decimal] = Field(None, description="제조업 PMI")
    industrial_production: Optional[Decimal] = Field(None, description="산업생산지수")
    capacity_utilization: Optional[Decimal] = Field(None, description="설비가동률 (%)")
    new_orders: Optional[Decimal] = Field(None, description="신규 수주")
    factory_orders: Optional[Decimal] = Field(None, description="공장 수주")
    durable_goods_orders: Optional[Decimal] = Field(None, description="내구재 수주")

    class Settings:
        name = "manufacturing_indicators"
        indexes = [
            [("country", 1), ("date", -1)],
            "country",
            "date",
            "pmi",
            "industrial_production",
            "created_at",
        ]

    def calculate_quality_score(self) -> float:
        """데이터 품질 점수 계산"""
        score = 100.0

        if not self.pmi:
            score -= 25
        if not self.industrial_production:
            score -= 25
        if not self.capacity_utilization:
            score -= 20

        return max(score, 0.0)


class ConsumerSentiment(BaseMarketDataDocument, DataQualityMixin):
    """소비자 심리 지표 모델"""

    date: datetime = Field(..., description="기준일")
    country: str = Field(default="US", description="국가코드")

    # 소비자 심리 지표들
    consumer_confidence: Optional[Decimal] = Field(None, description="소비자 신뢰지수")
    consumer_sentiment: Optional[Decimal] = Field(None, description="소비자 심리지수")
    retail_sales: Optional[Decimal] = Field(None, description="소매판매 변화율 (%)")
    personal_consumption: Optional[Decimal] = Field(None, description="개인소비지출")
    personal_income: Optional[Decimal] = Field(None, description="개인소득")
    personal_saving_rate: Optional[Decimal] = Field(None, description="개인저축률 (%)")

    class Settings:
        name = "consumer_sentiment_indicators"
        indexes = [
            [("country", 1), ("date", -1)],
            "country",
            "date",
            "consumer_confidence",
            "retail_sales",
            "created_at",
        ]

    def calculate_quality_score(self) -> float:
        """데이터 품질 점수 계산"""
        score = 100.0

        if not self.consumer_confidence and not self.consumer_sentiment:
            score -= 30
        if not self.retail_sales:
            score -= 25
        if not self.personal_consumption:
            score -= 20

        return max(score, 0.0)
