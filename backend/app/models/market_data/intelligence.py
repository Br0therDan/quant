"""
Market intelligence and sentiment data models
시장 인텔리전스 및 감정 분석 관련 데이터 모델들
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from decimal import Decimal

from .base import BaseMarketDataDocument, DataQualityMixin


class NewsSentiment(BaseMarketDataDocument, DataQualityMixin):
    """뉴스 감정 분석 모델"""

    symbol: str = Field(..., description="주식 심볼")
    time_from: datetime = Field(..., description="분석 시작 시간")
    time_to: datetime = Field(..., description="분석 종료 시간")

    # 감정 점수
    sentiment_score_definition: str = Field(..., description="감정 점수 정의")
    relevance_score_definition: str = Field(..., description="관련성 점수 정의")

    # 전체 감정 통계
    overall_sentiment_score: Optional[Decimal] = Field(None, description="전체 감정 점수")
    overall_sentiment_label: Optional[str] = Field(None, description="전체 감정 라벨")

    class Settings:
        name = "intelligence_news_sentiments"
        indexes = [
            [("symbol", 1), ("time_from", -1)],
            "symbol",
            "time_from",
            "overall_sentiment_score",
            "created_at",
        ]

    def calculate_quality_score(self) -> float:
        """데이터 품질 점수 계산"""
        score = 100.0

        if not self.overall_sentiment_score:
            score -= 30
        if not self.overall_sentiment_label:
            score -= 20
        if not self.sentiment_score_definition:
            score -= 25

        return max(score, 0.0)


class NewsArticle(BaseModel):
    """개별 뉴스 기사 모델 (Pydantic)"""

    symbol: str = Field(..., description="주식 심볼")
    title: str = Field(..., description="기사 제목")
    url: str = Field(..., description="기사 URL")
    time_published: datetime = Field(..., description="발행 시간")

    # 기사 메타데이터
    news_source: Optional[str] = Field(None, description="출처")
    source_domain: Optional[str] = Field(None, description="출처 도메인")
    authors: Optional[List[str]] = Field(None, description="작성자 목록")
    summary: Optional[str] = Field(None, description="요약")
    banner_image: Optional[str] = Field(None, description="배너 이미지 URL")

    # 감정 분석 결과
    overall_sentiment_score: Optional[Decimal] = Field(None, description="전체 감정 점수")
    overall_sentiment_label: Optional[str] = Field(None, description="전체 감정 라벨")
    relevance_score: Optional[Decimal] = Field(None, description="관련성 점수")

    # 분류 정보
    topics: Optional[List[str]] = Field(None, description="주제 태그")
    category_within_source: Optional[str] = Field(None, description="출처 내 카테고리")

    # 품질 점수 (자동 계산)
    data_quality_score: Optional[float] = Field(None, description="데이터 품질 점수 (0-100)")

    def model_post_init(self, __context) -> None:
        """모델 생성 후 품질 점수 자동 계산"""
        if self.data_quality_score is None:
            self.data_quality_score = self.calculate_quality_score()

    def calculate_quality_score(self) -> float:
        """데이터 품질 점수 계산"""
        score = 100.0

        if not self.title:
            score -= 25
        if not self.summary:
            score -= 15
        if not self.overall_sentiment_score:
            score -= 20
        if not self.relevance_score:
            score -= 15

        return max(score, 0.0)


class SentimentAnalysis(BaseModel):
    """감정 분석 결과 모델 (Pydantic)"""

    symbol: str = Field(..., description="주식 심볼")
    timeframe: str = Field(..., description="분석 기간")
    time_from: str = Field(..., description="분석 시작 시간")
    time_to: str = Field(..., description="분석 종료 시간")
    overall_sentiment_score: float = Field(..., description="전체 감정 점수")
    overall_sentiment_label: str = Field(..., description="전체 감정 라벨")
    article_count: int = Field(..., description="분석된 기사 수")
    positive_count: int = Field(..., description="긍정 기사 수")
    negative_count: int = Field(..., description="부정 기사 수")
    neutral_count: int = Field(..., description="중립 기사 수")
    sentiment_score_definition: str = Field(..., description="감정 점수 정의")
    relevance_score_definition: str = Field(..., description="관련성 점수 정의")

    # 품질 점수 (자동 계산)
    data_quality_score: Optional[float] = Field(
        default=None, description="데이터 품질 점수 (0-100)"
    )

    def model_post_init(self, __context) -> None:
        """모델 생성 후 품질 점수 자동 계산"""
        if self.data_quality_score is None:
            self.data_quality_score = self.calculate_quality_score()

    def calculate_quality_score(self) -> float:
        """데이터 품질 점수 계산"""
        score = 100.0

        if self.article_count < 5:
            score -= 30  # 분석 기사가 너무 적음
        elif self.article_count < 20:
            score -= 15

        if abs(self.overall_sentiment_score) < 0.01:
            score -= 20  # 감정 점수가 너무 중립적

        if not self.overall_sentiment_label:
            score -= 25

        return max(score, 0.0)


class AnalystRating(BaseMarketDataDocument, DataQualityMixin):
    """애널리스트 평가 모델"""

    symbol: str = Field(..., description="주식 심볼")
    date: datetime = Field(..., description="평가 날짜")

    # 평가 기관 정보
    firm_name: str = Field(..., description="평가 기관명")
    firm_display_name: Optional[str] = Field(None, description="평가 기관 표시명")
    analyst_name: Optional[str] = Field(None, description="애널리스트명")

    # 평가 내용
    rating_current: str = Field(..., description="현재 평가 등급")
    rating_previous: Optional[str] = Field(None, description="이전 평가 등급")
    action: Optional[str] = Field(
        None, description="평가 액션 (upgrade, downgrade, maintain)"
    )

    # 목표 가격
    price_target_current: Optional[Decimal] = Field(None, description="현재 목표 가격", gt=0)
    price_target_previous: Optional[Decimal] = Field(None, description="이전 목표 가격", gt=0)

    # 메타데이터
    currency: str = Field(default="USD", description="통화")
    notes: Optional[str] = Field(None, description="평가 노트")

    class Settings:
        name = "intelligence_analyst_ratings"
        indexes = [
            [("symbol", 1), ("date", -1)],
            [("symbol", 1), ("firm_name", 1), ("date", -1)],
            "symbol",
            "date",
            "firm_name",
            "rating_current",
            "price_target_current",
            "created_at",
        ]

    def calculate_quality_score(self) -> float:
        """데이터 품질 점수 계산"""
        score = 100.0

        if not self.firm_name:
            score -= 25
        if not self.rating_current:
            score -= 30
        if not self.price_target_current:
            score -= 20

        return max(score, 0.0)


class SocialSentiment(BaseMarketDataDocument, DataQualityMixin):
    """소셜 미디어 감정 분석 모델"""

    symbol: str = Field(..., description="주식 심볼")
    date: datetime = Field(..., description="분석 날짜")
    platform: str = Field(..., description="플랫폼 (reddit, twitter, stocktwits, etc)")

    # 감정 지표
    sentiment_score: Optional[Decimal] = Field(None, description="감정 점수 (-1 ~ 1)")
    sentiment_label: Optional[str] = Field(None, description="감정 라벨")

    # 활동 지표
    mention_count: Optional[int] = Field(None, description="언급 횟수", ge=0)
    positive_mentions: Optional[int] = Field(None, description="긍정 언급", ge=0)
    negative_mentions: Optional[int] = Field(None, description="부정 언급", ge=0)
    neutral_mentions: Optional[int] = Field(None, description="중립 언급", ge=0)

    # 추가 메트릭
    engagement_score: Optional[Decimal] = Field(None, description="참여도 점수")
    reach_estimate: Optional[int] = Field(None, description="도달 추정치", ge=0)
    influence_score: Optional[Decimal] = Field(None, description="영향력 점수")

    class Settings:
        name = "intelligence_social_sentiments"
        indexes = [
            [("symbol", 1), ("platform", 1), ("date", -1)],
            "symbol",
            "date",
            "platform",
            "sentiment_score",
            "mention_count",
            "created_at",
        ]

    def calculate_quality_score(self) -> float:
        """데이터 품질 점수 계산"""
        score = 100.0

        if not self.sentiment_score:
            score -= 25
        if not self.mention_count:
            score -= 20
        if not self.platform:
            score -= 15

        # 언급 수 일관성 검증
        if (
            self.mention_count
            and self.positive_mentions is not None
            and self.negative_mentions is not None
            and self.neutral_mentions is not None
        ):
            total_mentions = (
                self.positive_mentions + self.negative_mentions + self.neutral_mentions
            )
            if abs(total_mentions - self.mention_count) > self.mention_count * 0.05:
                score -= 20

        return max(score, 0.0)


class MarketMood(BaseMarketDataDocument, DataQualityMixin):
    """전체 시장 심리 모델"""

    date: datetime = Field(..., description="분석 날짜")
    market: str = Field(default="US", description="시장 (US, KR, EU, etc)")

    # 시장 심리 지표
    overall_sentiment: Optional[Decimal] = Field(None, description="전체 시장 심리 (-1 ~ 1)")
    fear_greed_index: Optional[Decimal] = Field(None, description="공포탐욕지수 (0 ~ 100)")
    volatility_index: Optional[Decimal] = Field(None, description="변동성 지수 (VIX)")

    # 섹터별 심리
    tech_sentiment: Optional[Decimal] = Field(None, description="기술주 심리")
    financial_sentiment: Optional[Decimal] = Field(None, description="금융주 심리")
    healthcare_sentiment: Optional[Decimal] = Field(None, description="헬스케어 심리")
    energy_sentiment: Optional[Decimal] = Field(None, description="에너지 심리")

    # 트렌드 지표
    bullish_percentage: Optional[Decimal] = Field(
        None, description="강세 비율 (%)", ge=0, le=100
    )
    bearish_percentage: Optional[Decimal] = Field(
        None, description="약세 비율 (%)", ge=0, le=100
    )
    neutral_percentage: Optional[Decimal] = Field(
        None, description="중립 비율 (%)", ge=0, le=100
    )

    # 추가 지표
    put_call_ratio: Optional[Decimal] = Field(None, description="풋콜 비율")
    insider_trading_sentiment: Optional[Decimal] = Field(None, description="내부자 거래 심리")
    institutional_flow: Optional[Decimal] = Field(None, description="기관 자금 흐름")

    class Settings:
        name = "intelligence_market_moods"
        indexes = [
            [("market", 1), ("date", -1)],
            "market",
            "date",
            "overall_sentiment",
            "fear_greed_index",
            "volatility_index",
            "created_at",
        ]

    def calculate_quality_score(self) -> float:
        """데이터 품질 점수 계산"""
        score = 100.0

        if not self.overall_sentiment:
            score -= 25
        if not self.fear_greed_index:
            score -= 20
        if not self.volatility_index:
            score -= 15

        # 비율 합계 검증
        percentages = [
            self.bullish_percentage,
            self.bearish_percentage,
            self.neutral_percentage,
        ]
        if all(p is not None for p in percentages):
            total = sum(p for p in percentages if p is not None)
            if abs(total - Decimal("100")) > Decimal("2"):  # 2% 오차 허용
                score -= 20

        return max(score, 0.0)


class OptionFlow(BaseMarketDataDocument, DataQualityMixin):
    """옵션 플로우 데이터 모델"""

    symbol: str = Field(..., description="주식 심볼")
    date: datetime = Field(..., description="거래일")

    # 옵션 거래 데이터
    total_volume: Optional[int] = Field(None, description="총 옵션 거래량", ge=0)
    call_volume: Optional[int] = Field(None, description="콜옵션 거래량", ge=0)
    put_volume: Optional[int] = Field(None, description="풋옵션 거래량", ge=0)
    put_call_ratio: Optional[Decimal] = Field(None, description="풋콜 비율")

    # 미결제약정
    total_open_interest: Optional[int] = Field(None, description="총 미결제약정", ge=0)
    call_open_interest: Optional[int] = Field(None, description="콜 미결제약정", ge=0)
    put_open_interest: Optional[int] = Field(None, description="풋 미결제약정", ge=0)

    # 프리미엄 및 거래 패턴
    call_premium: Optional[Decimal] = Field(None, description="콜옵션 프리미엄")
    put_premium: Optional[Decimal] = Field(None, description="풋옵션 프리미엄")
    unusual_activity: Optional[bool] = Field(None, description="비정상 거래 활동")

    # 감정 지표
    options_sentiment: Optional[str] = Field(
        None, description="옵션 감정 (bullish, bearish, neutral)"
    )
    flow_score: Optional[Decimal] = Field(None, description="플로우 점수 (-1 ~ 1)")

    class Settings:
        name = "intelligence_option_flows"
        indexes = [
            [("symbol", 1), ("date", -1)],
            "symbol",
            "date",
            "put_call_ratio",
            "total_volume",
            "created_at",
        ]

    def calculate_quality_score(self) -> float:
        """데이터 품질 점수 계산"""
        score = 100.0

        if not self.total_volume:
            score -= 25
        if not self.put_call_ratio:
            score -= 20

        # 거래량 일관성 검증
        if (
            self.total_volume
            and self.call_volume is not None
            and self.put_volume is not None
        ):
            if (
                abs(self.total_volume - (self.call_volume + self.put_volume))
                > self.total_volume * 0.05
            ):
                score -= 20

        return max(score, 0.0)
