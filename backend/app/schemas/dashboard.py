"""Dashboard response schemas."""

from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class TradeSide(str, Enum):
    """거래 방향."""

    BUY = "buy"
    SELL = "sell"


class StrategyStatus(str, Enum):
    """전략 상태."""

    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"


class SentimentType(str, Enum):
    """감정 분석 유형."""

    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class ImportanceLevel(str, Enum):
    """중요도 레벨."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DataQualitySeverity(str, Enum):
    """데이터 품질 이상 심각도."""

    NORMAL = "normal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Portfolio Models
class PortfolioSummary(BaseModel):
    """포트폴리오 요약 정보."""

    total_value: float = Field(..., description="총 포트폴리오 가치")
    total_pnl: float = Field(..., description="총 손익")
    total_pnl_percentage: float = Field(..., description="총 손익률")
    daily_pnl: float = Field(..., description="일일 손익")
    daily_pnl_percentage: float = Field(..., description="일일 손익률")


class StrategySummary(BaseModel):
    """전략 요약 정보."""

    active_count: int = Field(..., description="활성 전략 수")
    total_count: int = Field(..., description="총 전략 수")
    avg_success_rate: float = Field(..., description="평균 성공률")
    best_performing: Optional[str] = Field(None, description="최고 성과 전략 ID")


class RecentActivity(BaseModel):
    """최근 활동 정보."""

    trades_count_today: int = Field(..., description="오늘 거래 수")
    backtests_count_week: int = Field(..., description="이번 주 백테스트 수")
    last_login: Optional[datetime] = Field(None, description="마지막 로그인")


class DataQualityAlert(BaseModel):
    """데이터 품질 이상 알림."""

    symbol: str = Field(..., description="심볼")
    data_type: str = Field(..., description="데이터 타입")
    occurred_at: datetime = Field(..., description="이상 발생 시각")
    severity: DataQualitySeverity = Field(..., description="심각도")
    iso_score: float = Field(..., description="Isolation Forest 점수")
    prophet_score: Optional[float] = Field(None, description="Prophet 기반 잔차 점수")
    price_change_pct: float = Field(..., description="전일 대비 변동률")
    volume_z_score: float = Field(..., description="거래량 Z-Score")
    message: str = Field(..., description="알림 메시지")


class DataQualitySummary(BaseModel):
    """데이터 품질 센티널 요약."""

    total_alerts: int = Field(..., description="총 이상 건수")
    severity_breakdown: Dict[DataQualitySeverity, int] = Field(
        ..., description="심각도별 건수"
    )
    last_updated: datetime = Field(..., description="마지막 업데이트 시각")
    recent_alerts: List[DataQualityAlert] = Field(
        default_factory=list, description="최근 이상 목록"
    )


class DashboardSummary(BaseModel):
    """대시보드 요약 데이터."""

    user_id: str = Field(..., description="사용자 ID")
    portfolio: PortfolioSummary = Field(..., description="포트폴리오 정보")
    strategies: StrategySummary = Field(..., description="전략 정보")
    recent_activity: RecentActivity = Field(..., description="최근 활동")
    data_quality: Optional[DataQualitySummary] = Field(
        None, description="데이터 품질 센티널 요약"
    )


class PortfolioDataPoint(BaseModel):
    """포트폴리오 데이터 포인트."""

    timestamp: datetime = Field(..., description="시간")
    portfolio_value: float = Field(..., description="포트폴리오 가치")
    pnl: float = Field(..., description="손익")
    pnl_percentage: float = Field(..., description="손익률")
    benchmark_value: Optional[float] = Field(None, description="벤치마크 가치")


class PortfolioPerformanceSummary(BaseModel):
    """포트폴리오 성과 요약."""

    total_return: float = Field(..., description="총 수익률")
    volatility: float = Field(..., description="변동성")
    sharpe_ratio: float = Field(..., description="샤프 비율")
    max_drawdown: float = Field(..., description="최대 낙폭")


class PortfolioPerformance(BaseModel):
    """포트폴리오 성과 데이터."""

    period: str = Field(..., description="기간")
    data_points: List[PortfolioDataPoint] = Field(..., description="데이터 포인트들")
    summary: PortfolioPerformanceSummary = Field(..., description="성과 요약")


# Strategy Models
class StrategyPerformanceItem(BaseModel):
    """전략 성과 항목."""

    strategy_id: str = Field(..., description="전략 ID")
    name: str = Field(..., description="전략 이름")
    type: str = Field(..., description="전략 타입")
    total_return: float = Field(..., description="총 수익률")
    win_rate: float = Field(..., description="승률")
    sharpe_ratio: float = Field(..., description="샤프 비율")
    trades_count: int = Field(..., description="거래 수")
    last_execution: Optional[datetime] = Field(None, description="마지막 실행")
    status: StrategyStatus = Field(..., description="상태")


class StrategyComparison(BaseModel):
    """전략 비교 데이터."""

    strategies: List[StrategyPerformanceItem] = Field(..., description="전략 목록")


# Trade Models
class TradeItem(BaseModel):
    """거래 항목."""

    trade_id: str = Field(..., description="거래 ID")
    symbol: str = Field(..., description="심볼")
    side: TradeSide = Field(..., description="거래 방향")
    quantity: int = Field(..., description="수량")
    price: float = Field(..., description="가격")
    value: float = Field(..., description="거래 금액")
    pnl: float = Field(..., description="손익")
    strategy_name: str = Field(..., description="전략 이름")
    timestamp: datetime = Field(..., description="거래 시간")


class TradesSummary(BaseModel):
    """거래 요약."""

    total_trades: int = Field(..., description="총 거래 수")
    winning_trades: int = Field(..., description="수익 거래 수")
    total_pnl: float = Field(..., description="총 손익")


class RecentTrades(BaseModel):
    """최근 거래 데이터."""

    trades: List[TradeItem] = Field(..., description="거래 목록")
    summary: TradesSummary = Field(..., description="거래 요약")


# Watchlist Models
class WatchlistQuoteItem(BaseModel):
    """관심종목 시세 항목."""

    symbol: str = Field(..., description="심볼")
    name: str = Field(..., description="회사명")
    current_price: float = Field(..., description="현재가")
    change: float = Field(..., description="변화량")
    change_percentage: float = Field(..., description="변화율")
    volume: int = Field(..., description="거래량")
    market_cap: Optional[float] = Field(None, description="시가총액")


class WatchlistQuotes(BaseModel):
    """관심종목 시세 데이터."""

    symbols: List[WatchlistQuoteItem] = Field(..., description="심볼 목록")
    last_updated: datetime = Field(..., description="마지막 업데이트")


# News Models
class NewsArticle(BaseModel):
    """뉴스 기사."""

    title: str = Field(..., description="제목")
    summary: str = Field(..., description="요약")
    source: str = Field(..., description="출처")
    url: str = Field(..., description="URL")
    published_at: datetime = Field(..., description="발행 시간")
    sentiment: SentimentType = Field(..., description="감정")
    relevance_score: float = Field(..., description="관련도 점수")
    symbols: List[str] = Field(..., description="관련 심볼들")


class NewsFeed(BaseModel):
    """뉴스 피드."""

    articles: List[NewsArticle] = Field(..., description="기사 목록")


# Economic Calendar Models
class EconomicEvent(BaseModel):
    """경제 이벤트."""

    event_name: str = Field(..., description="이벤트명")
    country: str = Field(..., description="국가")
    importance: ImportanceLevel = Field(..., description="중요도")
    actual: Optional[float] = Field(None, description="실제값")
    forecast: Optional[float] = Field(None, description="예상값")
    previous: Optional[float] = Field(None, description="이전값")
    release_time: datetime = Field(..., description="발표 시간")
    currency: str = Field(..., description="통화")


class EconomicCalendar(BaseModel):
    """경제 캘린더."""

    events: List[EconomicEvent] = Field(..., description="이벤트 목록")


# Response Models
class DashboardSummaryResponse(BaseModel):
    """대시보드 요약 응답."""

    data: DashboardSummary = Field(..., description="대시보드 데이터")
    message: str = Field("대시보드 요약 조회 성공", description="응답 메시지")


class PortfolioPerformanceResponse(BaseModel):
    """포트폴리오 성과 응답."""

    data: PortfolioPerformance = Field(..., description="포트폴리오 성과")
    message: str = Field("포트폴리오 성과 조회 성공", description="응답 메시지")


class StrategyComparisonResponse(BaseModel):
    """전략 비교 응답."""

    data: StrategyComparison = Field(..., description="전략 비교 데이터")
    message: str = Field("전략 비교 조회 성공", description="응답 메시지")


class RecentTradesResponse(BaseModel):
    """최근 거래 응답."""

    data: RecentTrades = Field(..., description="최근 거래 데이터")
    message: str = Field("최근 거래 조회 성공", description="응답 메시지")


class WatchlistQuotesResponse(BaseModel):
    """관심종목 시세 응답."""

    data: WatchlistQuotes = Field(..., description="관심종목 시세")
    message: str = Field("관심종목 시세 조회 성공", description="응답 메시지")


class NewsFeedResponse(BaseModel):
    """뉴스 피드 응답."""

    data: NewsFeed = Field(..., description="뉴스 피드")
    message: str = Field("뉴스 피드 조회 성공", description="응답 메시지")


class EconomicCalendarResponse(BaseModel):
    """경제 캘린더 응답."""

    data: EconomicCalendar = Field(..., description="경제 캘린더")
    message: str = Field("경제 캘린더 조회 성공", description="응답 메시지")
