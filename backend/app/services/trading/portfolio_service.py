"""Portfolio service for managing user portfolios and performance tracking."""

from datetime import datetime, timedelta
from typing import List, Optional, TYPE_CHECKING
from app.services.database_manager import DatabaseManager
from app.schemas.user.dashboard import (
    PortfolioSummary,
    PortfolioPerformance,
    PortfolioDataPoint,
    PortfolioPerformanceSummary,
    TradeItem,
    TradeSide,
)
from app.schemas.ml_platform.predictive import PortfolioForecastDistribution
import random


if TYPE_CHECKING:
    from app.services.ml_platform.probabilistic_kpi_service import (
        ProbabilisticKPIService,
    )


class PortfolioService:
    """포트폴리오 관리 서비스."""

    def __init__(
        self,
        database_manager: DatabaseManager,
        probabilistic_service: Optional["ProbabilisticKPIService"] = None,
    ):
        """포트폴리오 서비스 초기화.

        Args:
            database_manager: 데이터베이스 매니저
        """
        self.db_manager = database_manager
        self.probabilistic_service = probabilistic_service

    async def get_portfolio_summary(self, user_id: str) -> PortfolioSummary:
        """사용자의 포트폴리오 요약 정보를 조회합니다.

        Args:
            user_id: 사용자 ID

        Returns:
            포트폴리오 요약 정보
        """
        try:
            # TODO: 실제 데이터베이스에서 포트폴리오 데이터 조회
            # 현재는 모의 데이터 반환
            return PortfolioSummary(
                total_value=125340.50,
                total_pnl=15340.50,
                total_pnl_percentage=12.5,
                daily_pnl=2450.30,
                daily_pnl_percentage=1.98,
            )
        except Exception as e:
            raise Exception(f"포트폴리오 요약 조회 실패: {str(e)}")

    async def get_portfolio_performance(
        self, user_id: str, period: str = "1M", granularity: str = "day"
    ) -> PortfolioPerformance:
        """포트폴리오 성과 데이터를 조회합니다.

        Args:
            user_id: 사용자 ID
            period: 조회 기간 (1D, 1W, 1M, 3M, 6M, 1Y)
            granularity: 데이터 간격 (hour, day, week)

        Returns:
            포트폴리오 성과 데이터
        """
        try:
            # 기간별 데이터 포인트 생성 (모의 데이터)
            data_points = await self._generate_performance_data(period, granularity)

            # 성과 요약 계산
            summary = self._calculate_performance_summary(data_points)

            return PortfolioPerformance(
                period=period, data_points=data_points, summary=summary
            )
        except Exception as e:
            raise Exception(f"포트폴리오 성과 조회 실패: {str(e)}")

    async def get_recent_trades(
        self, user_id: str, limit: int = 20, days: int = 7
    ) -> List[TradeItem]:
        """최근 거래 내역을 조회합니다.

        Args:
            user_id: 사용자 ID
            limit: 조회할 거래 수
            days: 조회할 일수

        Returns:
            최근 거래 목록
        """
        try:
            # TODO: 실제 데이터베이스에서 거래 내역 조회
            # 현재는 모의 데이터 반환
            trades = []
            symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA"]

            for i in range(min(limit, 10)):
                trades.append(
                    TradeItem(
                        trade_id=f"trade_{i + 1}",
                        symbol=random.choice(symbols),
                        side=random.choice([TradeSide.BUY, TradeSide.SELL]),
                        quantity=random.randint(1, 100),
                        price=round(random.uniform(100, 400), 2),
                        value=round(random.uniform(1000, 40000), 2),
                        pnl=round(random.uniform(-1000, 3000), 2),
                        strategy_name=f"Strategy_{random.randint(1, 5)}",
                        timestamp=datetime.now()
                        - timedelta(hours=random.randint(1, 168)),
                    )
                )

            return trades
        except Exception as e:
            raise Exception(f"최근 거래 조회 실패: {str(e)}")

    async def get_probabilistic_forecast(
        self, user_id: str, horizon_days: int = 30
    ) -> PortfolioForecastDistribution:
        """포트폴리오 확률적 KPI 예측을 생성합니다."""

        if not self.probabilistic_service:
            raise RuntimeError("Probabilistic KPI service is not configured")

        performance = await self.get_portfolio_performance(
            user_id, period="3M", granularity="day"
        )
        return await self.probabilistic_service.forecast_from_history(
            performance.data_points, horizon_days=horizon_days
        )

    async def _generate_performance_data(
        self, period: str, granularity: str
    ) -> List[PortfolioDataPoint]:
        """성과 데이터 생성 (모의 데이터).

        Args:
            period: 기간
            granularity: 간격

        Returns:
            포트폴리오 데이터 포인트 목록
        """
        # 기간별 데이터 포인트 수 결정
        period_map = {
            "1D": 24 if granularity == "hour" else 1,
            "1W": 7,
            "1M": 30,
            "3M": 90,
            "6M": 180,
            "1Y": 365,
        }

        points_count = period_map.get(period, 30)
        data_points = []

        base_value = 110000.0
        current_time = datetime.now()

        for i in range(points_count):
            # 시간 계산
            if granularity == "hour":
                timestamp = current_time - timedelta(hours=points_count - i)
            else:
                timestamp = current_time - timedelta(days=points_count - i)

            # 포트폴리오 가치 계산 (랜덤 변동)
            value_change = random.uniform(-0.02, 0.03) * base_value
            portfolio_value = base_value + value_change

            pnl = portfolio_value - base_value
            pnl_percentage = (pnl / base_value) * 100

            data_points.append(
                PortfolioDataPoint(
                    timestamp=timestamp,
                    portfolio_value=round(portfolio_value, 2),
                    pnl=round(pnl, 2),
                    pnl_percentage=round(pnl_percentage, 4),
                    benchmark_value=round(base_value * 1.001, 2),  # 벤치마크는 약간의 성장
                )
            )

            base_value = portfolio_value  # 다음 포인트의 기준값으로 사용

        return data_points

    def _calculate_performance_summary(
        self, data_points: List[PortfolioDataPoint]
    ) -> PortfolioPerformanceSummary:
        """성과 요약 계산.

        Args:
            data_points: 포트폴리오 데이터 포인트들

        Returns:
            성과 요약 데이터
        """
        if not data_points:
            return PortfolioPerformanceSummary(
                total_return=0.0, volatility=0.0, sharpe_ratio=0.0, max_drawdown=0.0
            )

        # 총 수익률 계산
        initial_value = data_points[0].portfolio_value
        final_value = data_points[-1].portfolio_value
        total_return = ((final_value - initial_value) / initial_value) * 100

        # 변동성 계산 (일간 수익률의 표준편차)
        daily_returns = []
        for i in range(1, len(data_points)):
            prev_value = data_points[i - 1].portfolio_value
            curr_value = data_points[i].portfolio_value
            daily_return = (curr_value - prev_value) / prev_value
            daily_returns.append(daily_return)

        if daily_returns:
            avg_return = sum(daily_returns) / len(daily_returns)
            variance = sum((r - avg_return) ** 2 for r in daily_returns) / len(
                daily_returns
            )
            volatility = (variance**0.5) * 100  # 백분율로 변환
        else:
            volatility = 0.0

        # 샤프 비율 (간단한 계산)
        risk_free_rate = 0.02  # 2% 가정
        sharpe_ratio = (
            (total_return - risk_free_rate) / volatility if volatility > 0 else 0.0
        )

        # 최대 낙폭 계산
        max_value = initial_value
        max_drawdown = 0.0

        for point in data_points:
            if point.portfolio_value > max_value:
                max_value = point.portfolio_value
            else:
                drawdown = ((max_value - point.portfolio_value) / max_value) * 100
                max_drawdown = max(max_drawdown, drawdown)

        return PortfolioPerformanceSummary(
            total_return=round(total_return, 2),
            volatility=round(volatility, 2),
            sharpe_ratio=round(sharpe_ratio, 2),
            max_drawdown=round(max_drawdown, 2),
        )

    async def get_portfolio_forecast(
        self, user_id: str, horizon_days: int = 30
    ) -> PortfolioForecastDistribution:
        """포트폴리오 확률적 예측을 생성합니다.

        Args:
            user_id: 사용자 ID
            horizon_days: 예측 기간 (일)

        Returns:
            백분위 예측 분포

        Raises:
            Exception: probabilistic_service가 주입되지 않은 경우
            ValueError: 포트폴리오 히스토리가 없는 경우
        """
        if self.probabilistic_service is None:
            raise Exception(
                "ProbabilisticKPIService가 주입되지 않았습니다. "
                "ServiceFactory를 통해 PortfolioService를 생성하세요."
            )

        try:
            # 최근 포트폴리오 성과 데이터 조회 (6개월)
            performance = await self.get_portfolio_performance(
                user_id=user_id, period="6M", granularity="day"
            )

            if not performance.data_points:
                raise ValueError(f"사용자 {user_id}의 포트폴리오 히스토리가 없습니다")

            # ProbabilisticKPIService로 예측 생성
            forecast = await self.probabilistic_service.forecast_from_history(
                data_points=performance.data_points, horizon_days=horizon_days
            )

            return forecast

        except ValueError:
            raise
        except Exception as e:
            raise Exception(f"포트폴리오 예측 생성 실패: {str(e)}")
