"""
Market intelligence and sentiment data API schemas
시장 인텔리전스 및 감정 분석 데이터 API 스키마들
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
class NewsSentimentRequest(SymbolParams, DateRangeParams):
    """뉴스 감정 분석 요청 스키마"""

    sentiment_threshold: Optional[Decimal] = Field(None, description="감정 점수 임계값")
    relevance_threshold: Optional[Decimal] = Field(None, description="관련성 점수 임계값")


class NewsArticleRequest(SymbolParams, DateRangeParams, SortParams):
    """뉴스 기사 요청 스키마"""

    sources: Optional[List[str]] = Field(None, description="뉴스 소스 필터")
    sentiment_filter: Optional[str] = Field(
        None, description="감정 필터 (positive, negative, neutral)"
    )
    limit: int = Field(50, ge=1, le=500, description="결과 수 제한")


class AnalystRatingRequest(SymbolParams, DateRangeParams, SortParams):
    """애널리스트 평가 요청 스키마"""

    firms: Optional[List[str]] = Field(None, description="평가 기관 필터")
    rating_filter: Optional[str] = Field(None, description="평가 등급 필터")
    include_price_targets: bool = Field(True, description="목표 가격 포함 여부")


class SocialSentimentRequest(SymbolParams, DateRangeParams):
    """소셜 미디어 감정 분석 요청 스키마"""

    platforms: List[str] = Field(["reddit", "twitter"], description="플랫폼 목록")
    min_mentions: Optional[int] = Field(None, description="최소 언급 수")


class MarketMoodRequest(DateRangeParams):
    """시장 심리 요청 스키마"""

    market: str = Field("US", description="시장 코드")
    include_sector_breakdown: bool = Field(False, description="섹터별 분석 포함 여부")


class OptionFlowRequest(SymbolParams, DateRangeParams):
    """옵션 플로우 요청 스키마"""

    min_volume: Optional[int] = Field(None, description="최소 거래량")
    unusual_activity_only: bool = Field(False, description="비정상 활동만 포함")


# Response Data Models
class NewsSentimentData(BaseModel):
    """뉴스 감정 분석 응답 모델"""

    symbol: str = Field(..., description="주식 심볼")
    time_from: datetime = Field(..., description="분석 시작 시간")
    time_to: datetime = Field(..., description="분석 종료 시간")

    sentiment_score_definition: str = Field(..., description="감정 점수 정의")
    relevance_score_definition: str = Field(..., description="관련성 점수 정의")

    overall_sentiment_score: Optional[Decimal] = Field(None, description="전체 감정 점수")
    overall_sentiment_label: Optional[str] = Field(None, description="전체 감정 라벨")

    article_count: int = Field(..., description="분석된 기사 수")
    positive_count: int = Field(..., description="긍정 기사 수")
    negative_count: int = Field(..., description="부정 기사 수")
    neutral_count: int = Field(..., description="중립 기사 수")


class NewsArticleData(BaseModel):
    """뉴스 기사 응답 모델"""

    symbol: str = Field(..., description="주식 심볼")
    title: str = Field(..., description="기사 제목")
    url: str = Field(..., description="기사 URL")
    time_published: datetime = Field(..., description="발행 시간")

    news_source: Optional[str] = Field(None, description="출처")
    source_domain: Optional[str] = Field(None, description="출처 도메인")
    authors: Optional[List[str]] = Field(None, description="작성자 목록")
    summary: Optional[str] = Field(None, description="요약")
    banner_image: Optional[str] = Field(None, description="배너 이미지 URL")

    overall_sentiment_score: Optional[Decimal] = Field(None, description="전체 감정 점수")
    overall_sentiment_label: Optional[str] = Field(None, description="전체 감정 라벨")
    relevance_score: Optional[Decimal] = Field(None, description="관련성 점수")

    topics: Optional[List[str]] = Field(None, description="주제 태그")


class AnalystRatingData(BaseModel):
    """애널리스트 평가 응답 모델"""

    symbol: str = Field(..., description="주식 심볼")
    date: datetime = Field(..., description="평가 날짜")

    firm_name: str = Field(..., description="평가 기관명")
    firm_display_name: Optional[str] = Field(None, description="평가 기관 표시명")
    analyst_name: Optional[str] = Field(None, description="애널리스트명")

    rating_current: str = Field(..., description="현재 평가 등급")
    rating_previous: Optional[str] = Field(None, description="이전 평가 등급")
    action: Optional[str] = Field(None, description="평가 액션")

    price_target_current: Optional[Decimal] = Field(None, description="현재 목표 가격")
    price_target_previous: Optional[Decimal] = Field(None, description="이전 목표 가격")

    currency: str = Field(default="USD", description="통화")
    notes: Optional[str] = Field(None, description="평가 노트")


class SocialSentimentData(BaseModel):
    """소셜 미디어 감정 분석 응답 모델"""

    symbol: str = Field(..., description="주식 심볼")
    date: datetime = Field(..., description="분석 날짜")
    platform: str = Field(..., description="플랫폼")

    sentiment_score: Optional[Decimal] = Field(None, description="감정 점수 (-1 ~ 1)")
    sentiment_label: Optional[str] = Field(None, description="감정 라벨")

    mention_count: Optional[int] = Field(None, description="언급 횟수")
    positive_mentions: Optional[int] = Field(None, description="긍정 언급")
    negative_mentions: Optional[int] = Field(None, description="부정 언급")
    neutral_mentions: Optional[int] = Field(None, description="중립 언급")

    engagement_score: Optional[Decimal] = Field(None, description="참여도 점수")
    reach_estimate: Optional[int] = Field(None, description="도달 추정치")
    influence_score: Optional[Decimal] = Field(None, description="영향력 점수")


class MarketMoodData(BaseModel):
    """시장 심리 응답 모델"""

    date: datetime = Field(..., description="분석 날짜")
    market: str = Field(..., description="시장")

    overall_sentiment: Optional[Decimal] = Field(None, description="전체 시장 심리 (-1 ~ 1)")
    fear_greed_index: Optional[Decimal] = Field(None, description="공포탐욕지수 (0 ~ 100)")
    volatility_index: Optional[Decimal] = Field(None, description="변동성 지수 (VIX)")

    tech_sentiment: Optional[Decimal] = Field(None, description="기술주 심리")
    financial_sentiment: Optional[Decimal] = Field(None, description="금융주 심리")
    healthcare_sentiment: Optional[Decimal] = Field(None, description="헬스케어 심리")
    energy_sentiment: Optional[Decimal] = Field(None, description="에너지 심리")

    bullish_percentage: Optional[Decimal] = Field(None, description="강세 비율 (%)")
    bearish_percentage: Optional[Decimal] = Field(None, description="약세 비율 (%)")
    neutral_percentage: Optional[Decimal] = Field(None, description="중립 비율 (%)")

    put_call_ratio: Optional[Decimal] = Field(None, description="풋콜 비율")
    insider_trading_sentiment: Optional[Decimal] = Field(None, description="내부자 거래 심리")
    institutional_flow: Optional[Decimal] = Field(None, description="기관 자금 흐름")


class OptionFlowData(BaseModel):
    """옵션 플로우 응답 모델"""

    symbol: str = Field(..., description="주식 심볼")
    date: datetime = Field(..., description="거래일")

    total_volume: Optional[int] = Field(None, description="총 옵션 거래량")
    call_volume: Optional[int] = Field(None, description="콜옵션 거래량")
    put_volume: Optional[int] = Field(None, description="풋옵션 거래량")
    put_call_ratio: Optional[Decimal] = Field(None, description="풋콜 비율")

    total_open_interest: Optional[int] = Field(None, description="총 미결제약정")
    call_open_interest: Optional[int] = Field(None, description="콜 미결제약정")
    put_open_interest: Optional[int] = Field(None, description="풋 미결제약정")

    call_premium: Optional[Decimal] = Field(None, description="콜옵션 프리미엄")
    put_premium: Optional[Decimal] = Field(None, description="풋옵션 프리미엄")
    unusual_activity: Optional[bool] = Field(None, description="비정상 거래 활동")

    options_sentiment: Optional[str] = Field(None, description="옵션 감정")
    flow_score: Optional[Decimal] = Field(None, description="플로우 점수 (-1 ~ 1)")


# Response Schemas
class NewsSentimentResponse(DataResponse[NewsSentimentData]):
    """뉴스 감정 분석 응답 스키마"""

    pass


class NewsArticleListResponse(PaginatedResponse[NewsArticleData]):
    """뉴스 기사 목록 응답 스키마"""

    pass


class AnalystRatingListResponse(PaginatedResponse[AnalystRatingData]):
    """애널리스트 평가 목록 응답 스키마"""

    pass


class SocialSentimentListResponse(BulkDataResponse[SocialSentimentData]):
    """소셜 미디어 감정 분석 목록 응답 스키마"""

    pass


class MarketMoodResponse(DataResponse[MarketMoodData]):
    """시장 심리 응답 스키마"""

    pass


class OptionFlowListResponse(BulkDataResponse[OptionFlowData]):
    """옵션 플로우 목록 응답 스키마"""

    pass


# 종합 인텔리전스 분석 스키마
class IntelligenceOverviewData(BaseModel):
    """인텔리전스 종합 분석 데이터"""

    symbol: str = Field(..., description="주식 심볼")
    analysis_date: datetime = Field(..., description="분석 날짜")

    # 종합 감정 점수
    overall_sentiment: Decimal = Field(..., description="종합 감정 점수 (-1 ~ 1)")
    sentiment_strength: str = Field(..., description="감정 강도 (weak, moderate, strong)")

    # 각 채널별 감정
    news_sentiment: Optional[Decimal] = Field(None, description="뉴스 감정")
    social_sentiment: Optional[Decimal] = Field(None, description="소셜 감정")
    analyst_sentiment: Optional[Decimal] = Field(None, description="애널리스트 감정")
    options_sentiment: Optional[Decimal] = Field(None, description="옵션 감정")

    # 신뢰도 및 메타데이터
    confidence_score: Decimal = Field(..., description="신뢰도 점수 (0-1)")
    data_freshness: str = Field(..., description="데이터 신선도 (fresh, stale, outdated)")
    coverage_score: Decimal = Field(..., description="커버리지 점수 (0-1)")

    # 추천 액션
    recommended_action: Optional[str] = Field(
        None, description="추천 액션 (buy, hold, sell)"
    )
    risk_level: Optional[str] = Field(None, description="위험 수준 (low, medium, high)")


class IntelligenceOverviewResponse(DataResponse[IntelligenceOverviewData]):
    """인텔리전스 종합 분석 응답 스키마"""

    pass


# 알림 및 경고 스키마
class SentimentAlertRequest(BaseModel):
    """감정 분석 알림 요청"""

    symbol: str = Field(..., description="주식 심볼")
    alert_type: str = Field(
        ...,
        pattern="^(sentiment_change|volume_spike|unusual_activity)$",
        description="알림 유형",
    )
    threshold: Decimal = Field(..., description="임계값")
    notification_method: str = Field(
        "email", pattern="^(email|webhook|both)$", description="알림 방법"
    )


class SentimentAlertData(BaseModel):
    """감정 분석 알림 데이터"""

    alert_id: str = Field(..., description="알림 ID")
    symbol: str = Field(..., description="주식 심볼")
    alert_type: str = Field(..., description="알림 유형")
    triggered_at: datetime = Field(..., description="발생 시간")

    current_value: Decimal = Field(..., description="현재 값")
    threshold_value: Decimal = Field(..., description="임계값")
    change_magnitude: Decimal = Field(..., description="변화량")

    description: str = Field(..., description="알림 설명")
    severity: str = Field(..., description="심각도 (low, medium, high, critical)")


class SentimentAlertResponse(DataResponse[SentimentAlertData]):
    """감정 분석 알림 응답 스키마"""

    pass
