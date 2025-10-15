"""Dashboard service for aggregating user dashboard data."""

import logging
import random
from datetime import UTC, datetime, timedelta
from typing import List, Optional, TYPE_CHECKING

from app.schemas.user.dashboard import (
    DashboardSummary,
    StrategySummary,
    RecentActivity,
    PortfolioPerformance,
    StrategyComparison,
    StrategyPerformanceItem,
    StrategyStatus,
    RecentTrades,
    TradesSummary,
    WatchlistQuotes,
    WatchlistQuoteItem,
    NewsFeed,
    NewsArticle,
    SentimentType,
    EconomicCalendar,
    EconomicEvent,
    ImportanceLevel,
    DataQualitySummary,
    DataQualityAlert,
    DataQualitySeverity,
)
from app.schemas.ml_platform.predictive import PredictiveDashboardInsights
from app.services.database_manager import DatabaseManager
from app.services.trading.portfolio_service import PortfolioService
from app.services.trading.strategy_service import StrategyService
from app.services.trading.backtest_service import BacktestService
from app.services.market_data_service import MarketDataService
from app.services.user.watchlist_service import WatchlistService
from app.services.monitoring.data_quality_sentinel import DataQualitySentinel


if TYPE_CHECKING:
    from app.services.ml_platform.services.ml_signal_service import MLSignalService
    from app.services.ml_platform.services.regime_detection_service import (
        RegimeDetectionService,
    )
    from app.services.ml_platform.services.probabilistic_kpi_service import (
        ProbabilisticKPIService,
    )


logger = logging.getLogger(__name__)


class DashboardService:
    """대시보드 데이터 통합 서비스."""

    def __init__(
        self,
        database_manager: DatabaseManager,
        portfolio_service: PortfolioService,
        strategy_service: StrategyService,
        backtest_service: BacktestService,
        market_data_service: MarketDataService,
        watchlist_service: WatchlistService,
        ml_signal_service: "MLSignalService",
        regime_service: "RegimeDetectionService",
        probabilistic_service: "ProbabilisticKPIService",
        data_quality_sentinel: Optional[DataQualitySentinel] = None,
    ):
        """대시보드 서비스 초기화.

        Args:
            database_manager: 데이터베이스 매니저
            portfolio_service: 포트폴리오 서비스
            strategy_service: 전략 서비스
            backtest_service: 백테스트 서비스
            market_data_service: 시장 데이터 서비스
            watchlist_service: 관심종목 서비스
            ml_signal_service: ML 시그널 서비스
            regime_service: 시장 레짐 감지 서비스
            probabilistic_service: 확률 KPI 서비스
            data_quality_sentinel: 데이터 품질 센티널 서비스
        """
        self.db_manager = database_manager
        self.portfolio_service = portfolio_service
        self.strategy_service = strategy_service
        self.backtest_service = backtest_service
        self.market_data_service = market_data_service
        self.watchlist_service = watchlist_service
        self.ml_signal_service = ml_signal_service
        self.regime_service = regime_service
        self.probabilistic_service = probabilistic_service
        self.data_quality_sentinel = data_quality_sentinel

    async def get_dashboard_summary(self, user_id: str) -> DashboardSummary:
        """대시보드 요약 데이터를 조회합니다.

        Args:
            user_id: 사용자 ID

        Returns:
            대시보드 요약 데이터
        """
        try:
            # 각 서비스에서 데이터 수집
            portfolio_summary = await self.portfolio_service.get_portfolio_summary(
                user_id
            )
            strategies_summary = await self._get_strategies_summary(user_id)
            recent_activity = await self._get_recent_activity(user_id)
            data_quality = await self._get_data_quality_summary()

            return DashboardSummary(
                user_id=user_id,
                portfolio=portfolio_summary,
                strategies=strategies_summary,
                recent_activity=recent_activity,
                data_quality=data_quality,
            )
        except Exception as e:
            raise Exception(f"대시보드 요약 조회 실패: {str(e)}")

    async def _get_data_quality_summary(self) -> Optional[DataQualitySummary]:
        """최근 데이터 품질 이상 요약을 조회합니다."""

        if not self.data_quality_sentinel:
            return None

        try:
            snapshot = await self.data_quality_sentinel.get_recent_summary()
        except Exception as exc:
            logger.warning("Failed to load data quality summary: %s", exc)
            return None

        severity_breakdown = {
            DataQualitySeverity(level.value): count
            for level, count in snapshot.severity_breakdown.items()
        }
        alerts = [
            DataQualityAlert(
                symbol=alert.symbol,
                data_type=alert.data_type,
                occurred_at=alert.occurred_at,
                severity=DataQualitySeverity(alert.severity.value),
                iso_score=alert.iso_score,
                prophet_score=alert.prophet_score,
                price_change_pct=alert.price_change_pct,
                volume_z_score=alert.volume_z_score,
                message=alert.message,
            )
            for alert in snapshot.recent_alerts
        ]

        return DataQualitySummary(
            total_alerts=snapshot.total_alerts,
            severity_breakdown=severity_breakdown,
            last_updated=snapshot.last_updated,
            recent_alerts=alerts,
        )

    async def get_portfolio_performance(
        self, user_id: str, period: str = "1M", granularity: str = "day"
    ) -> PortfolioPerformance:
        """포트폴리오 성과 데이터를 조회합니다.

        Args:
            user_id: 사용자 ID
            period: 조회 기간
            granularity: 데이터 간격

        Returns:
            포트폴리오 성과 데이터
        """
        return await self.portfolio_service.get_portfolio_performance(
            user_id, period, granularity
        )

    async def get_strategy_comparison(
        self, user_id: str, limit: int = 10, sort_by: str = "return"
    ) -> StrategyComparison:
        """전략 성과 비교 데이터를 조회합니다.

        Args:
            user_id: 사용자 ID
            limit: 조회할 전략 수
            sort_by: 정렬 기준

        Returns:
            전략 비교 데이터
        """
        try:
            # TODO: 실제 전략 데이터 조회
            # 현재는 모의 데이터 반환
            strategies = []
            strategy_types = ["RSI", "SMA", "Bollinger", "MACD", "Momentum"]

            for i in range(min(limit, 5)):
                strategies.append(
                    StrategyPerformanceItem(
                        strategy_id=f"strategy_{i + 1}",
                        name=f"{random.choice(strategy_types)}_Strategy_{i + 1}",
                        type=random.choice(strategy_types),
                        total_return=round(random.uniform(-5, 25), 2),
                        win_rate=round(random.uniform(45, 85), 1),
                        sharpe_ratio=round(random.uniform(0.5, 2.5), 2),
                        trades_count=random.randint(50, 500),
                        last_execution=datetime.now()
                        - timedelta(hours=random.randint(1, 72)),
                        status=random.choice(
                            [StrategyStatus.ACTIVE, StrategyStatus.PAUSED]
                        ),
                    )
                )

            # 정렬
            if sort_by == "return":
                strategies.sort(key=lambda x: x.total_return, reverse=True)
            elif sort_by == "sharpe":
                strategies.sort(key=lambda x: x.sharpe_ratio, reverse=True)
            elif sort_by == "win_rate":
                strategies.sort(key=lambda x: x.win_rate, reverse=True)

            return StrategyComparison(strategies=strategies)
        except Exception as e:
            raise Exception(f"전략 비교 조회 실패: {str(e)}")

    async def get_recent_trades(
        self, user_id: str, limit: int = 20, days: int = 7
    ) -> RecentTrades:
        """최근 거래 내역을 조회합니다.

        Args:
            user_id: 사용자 ID
            limit: 조회할 거래 수
            days: 조회할 일수

        Returns:
            최근 거래 데이터
        """
        try:
            trades = await self.portfolio_service.get_recent_trades(
                user_id, limit, days
            )

            # 거래 요약 계산
            total_trades = len(trades)
            winning_trades = sum(1 for trade in trades if trade.pnl > 0)
            total_pnl = sum(trade.pnl for trade in trades)

            summary = TradesSummary(
                total_trades=total_trades,
                winning_trades=winning_trades,
                total_pnl=round(total_pnl, 2),
            )

            return RecentTrades(trades=trades, summary=summary)
        except Exception as e:
            raise Exception(f"최근 거래 조회 실패: {str(e)}")

    async def get_watchlist_quotes(self, user_id: str) -> WatchlistQuotes:
        """관심종목 현재가를 조회합니다.

        Args:
            user_id: 사용자 ID

        Returns:
            관심종목 시세 데이터
        """
        try:
            # TODO: 실제 관심종목 및 시세 데이터 조회
            # 현재는 모의 데이터 반환
            symbols_data = [
                {"symbol": "AAPL", "name": "Apple Inc.", "price": 180.50},
                {"symbol": "GOOGL", "name": "Alphabet Inc.", "price": 145.30},
                {"symbol": "MSFT", "name": "Microsoft Corp.", "price": 380.75},
                {"symbol": "TSLA", "name": "Tesla Inc.", "price": 195.25},
                {"symbol": "NVDA", "name": "NVIDIA Corp.", "price": 875.40},
            ]

            quotes = []
            for data in symbols_data:
                change = round(random.uniform(-10, 15), 2)
                change_percentage = round((change / data["price"]) * 100, 2)

                quotes.append(
                    WatchlistQuoteItem(
                        symbol=data["symbol"],
                        name=data["name"],
                        current_price=data["price"],
                        change=change,
                        change_percentage=change_percentage,
                        volume=random.randint(1000000, 50000000),
                        market_cap=random.randint(100, 3000) * 1e9,  # Billions
                    )
                )

            return WatchlistQuotes(symbols=quotes, last_updated=datetime.now())
        except Exception as e:
            raise Exception(f"관심종목 시세 조회 실패: {str(e)}")

    async def get_news_feed(
        self,
        user_id: str,
        limit: int = 10,
        symbols: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
    ) -> NewsFeed:
        """뉴스 피드를 조회합니다.

        Args:
            user_id: 사용자 ID
            limit: 조회할 뉴스 수
            symbols: 관련 심볼 필터
            categories: 카테고리 필터

        Returns:
            뉴스 피드 데이터
        """
        try:
            # TODO: 실제 뉴스 API 연동
            # 현재는 모의 데이터 반환
            articles = []
            news_templates = [
                {"title": "Apple Reports Strong Q4 Earnings", "source": "MarketWatch"},
                {
                    "title": "Tesla Delivers Record Number of Vehicles",
                    "source": "Reuters",
                },
                {
                    "title": "Fed Announces Interest Rate Decision",
                    "source": "Bloomberg",
                },
                {"title": "Tech Stocks Rally on AI News", "source": "CNBC"},
                {
                    "title": "Market Volatility Expected This Week",
                    "source": "Financial Times",
                },
            ]

            for i, template in enumerate(news_templates[:limit]):
                articles.append(
                    NewsArticle(
                        title=template["title"],
                        summary=f"Summary of {template['title']}...",
                        source=template["source"],
                        url=f"https://example.com/news/{i + 1}",
                        published_at=datetime.now()
                        - timedelta(hours=random.randint(1, 24)),
                        sentiment=random.choice(
                            [
                                SentimentType.POSITIVE,
                                SentimentType.NEUTRAL,
                                SentimentType.NEGATIVE,
                            ]
                        ),
                        relevance_score=round(random.uniform(0.5, 1.0), 2),
                        symbols=symbols or ["AAPL", "TSLA", "GOOGL"],
                    )
                )

            return NewsFeed(articles=articles)
        except Exception as e:
            raise Exception(f"뉴스 피드 조회 실패: {str(e)}")

    async def get_economic_calendar(
        self, user_id: str, days: int = 7, importance: Optional[List[str]] = None
    ) -> EconomicCalendar:
        """경제 캘린더를 조회합니다.

        Args:
            user_id: 사용자 ID
            days: 조회할 일수
            importance: 중요도 필터

        Returns:
            경제 캘린더 데이터
        """
        try:
            # TODO: 실제 경제 지표 API 연동
            # 현재는 모의 데이터 반환
            events = []
            economic_events = [
                {"name": "Non-Farm Payrolls", "country": "US", "currency": "USD"},
                {"name": "CPI Inflation Rate", "country": "US", "currency": "USD"},
                {"name": "GDP Growth Rate", "country": "US", "currency": "USD"},
                {"name": "Interest Rate Decision", "country": "US", "currency": "USD"},
                {"name": "Unemployment Rate", "country": "US", "currency": "USD"},
            ]

            for event in economic_events:
                events.append(
                    EconomicEvent(
                        event_name=event["name"],
                        country=event["country"],
                        importance=random.choice(
                            [
                                ImportanceLevel.HIGH,
                                ImportanceLevel.MEDIUM,
                                ImportanceLevel.LOW,
                            ]
                        ),
                        actual=(
                            round(random.uniform(1, 10), 1)
                            if random.choice([True, False])
                            else None
                        ),
                        forecast=round(random.uniform(1, 10), 1),
                        previous=round(random.uniform(1, 10), 1),
                        release_time=datetime.now()
                        + timedelta(days=random.randint(0, days)),
                        currency=event["currency"],
                    )
                )

            return EconomicCalendar(events=events)
        except Exception as e:
            raise Exception(f"경제 캘린더 조회 실패: {str(e)}")

    async def get_predictive_snapshot(
        self, user_id: str, symbol: str, horizon_days: int = 30
    ) -> PredictiveDashboardInsights:
        """ML 시그널, 레짐, 확률 KPI를 묶어서 제공합니다."""

        signal = await self.ml_signal_service.score_symbol(symbol)

        regime = await self.regime_service.get_latest_regime(symbol)
        if not regime or (datetime.now(UTC) - regime.as_of).days > 1:
            regime = await self.regime_service.refresh_regime(symbol)

        forecast = await self.portfolio_service.get_probabilistic_forecast(
            user_id, horizon_days=horizon_days
        )

        return PredictiveDashboardInsights(
            signal=signal,
            regime=regime,
            forecast=forecast,
        )

    async def _get_strategies_summary(self, user_id: str) -> StrategySummary:
        """전략 요약 정보를 조회합니다.

        Args:
            user_id: 사용자 ID

        Returns:
            전략 요약 데이터
        """
        try:
            # TODO: 실제 전략 데이터 조회
            # 현재는 모의 데이터 반환
            return StrategySummary(
                active_count=7,
                total_count=12,
                avg_success_rate=68.5,
                best_performing="strategy_1",
            )
        except Exception as e:
            raise Exception(f"전략 요약 조회 실패: {str(e)}")

    async def _get_recent_activity(self, user_id: str) -> RecentActivity:
        """최근 활동 정보를 조회합니다.

        Args:
            user_id: 사용자 ID

        Returns:
            최근 활동 데이터
        """
        try:
            # TODO: 실제 활동 데이터 조회
            # 현재는 모의 데이터 반환
            return RecentActivity(
                trades_count_today=15,
                backtests_count_week=3,
                last_login=datetime.now() - timedelta(hours=2),
            )
        except Exception as e:
            raise Exception(f"최근 활동 조회 실패: {str(e)}")
