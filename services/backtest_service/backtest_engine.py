"""
간소화된 백테스트 엔진

주요 기능만 포함한 백테스트 엔진 구현
"""

import logging
import uuid
from datetime import datetime

import numpy as np

from .models import BacktestConfig, BacktestResult
from .temp_models import DataLoader, TradingSignal

logger = logging.getLogger(__name__)


class PerformanceCalculator:
    """성과 계산기"""

    @staticmethod
    def calculate_metrics(
        daily_values: list[float], initial_value: float
    ) -> dict[str, float]:
        """성과 지표 계산"""
        if not daily_values or len(daily_values) < 2:
            return {
                "total_return": 0.0,
                "annualized_return": 0.0,
                "volatility": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0,
            }

        # 일일 수익률 계산
        daily_returns = []
        for i in range(1, len(daily_values)):
            daily_return = (daily_values[i] - daily_values[i - 1]) / daily_values[i - 1]
            daily_returns.append(daily_return)

        # 총 수익률
        total_return = (daily_values[-1] - initial_value) / initial_value

        # 연환산 수익률
        days = len(daily_values)
        annualized_return = (1 + total_return) ** (365 / days) - 1 if days > 0 else 0.0

        # 변동성
        volatility = np.std(daily_returns) * np.sqrt(252) if daily_returns else 0.0

        # 샤프 비율
        sharpe_ratio = annualized_return / volatility if volatility > 0 else 0.0

        # 최대 낙폭
        max_drawdown = PerformanceCalculator._calculate_max_drawdown(daily_values)

        return {
            "total_return": total_return,
            "annualized_return": annualized_return,
            "volatility": volatility,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
        }

    @staticmethod
    def _calculate_max_drawdown(values: list[float]) -> float:
        """최대 낙폭 계산"""
        if not values:
            return 0.0

        peak = values[0]
        max_dd = 0.0

        for value in values:
            if value > peak:
                peak = value

            drawdown = (peak - value) / peak if peak > 0 else 0.0
            if drawdown > max_dd:
                max_dd = drawdown

        return max_dd


class TradingSimulator:
    """거래 시뮬레이터"""

    def __init__(self, config: BacktestConfig):
        self.config = config
        self.portfolio_values: list[float] = []

    def simulate_trades(self, signals: list[TradingSignal]) -> list[float]:
        """거래 시뮬레이션"""
        # 간단한 시뮬레이션 구현
        current_value = self.config.initial_cash
        values = [current_value]

        for signal in signals:
            # 간단한 수익률 시뮬레이션 (실제로는 복잡한 로직 필요)
            if signal.action == "BUY":
                # 1% 수익 가정
                current_value *= 1.01
            elif signal.action == "SELL":
                # 0.5% 수익 가정
                current_value *= 1.005

            values.append(current_value)

        return values


class ResultManager:
    """결과 관리자"""

    def __init__(self):
        self.results: dict[str, BacktestResult] = {}

    def save_result(self, result: BacktestResult) -> str:
        """결과 저장"""
        self.results[result.backtest_id] = result
        logger.info(f"백테스트 결과 저장: {result.backtest_id}")
        return result.backtest_id

    def get_result(self, backtest_id: str) -> BacktestResult | None:
        """결과 조회"""
        return self.results.get(backtest_id)

    def list_results(self) -> list[BacktestResult]:
        """결과 목록 조회"""
        return list(self.results.values())


class BacktestEngine:
    """간소화된 백테스트 엔진"""

    def __init__(self, config: BacktestConfig):
        self.config = config
        self.data_loader = DataLoader()
        self.performance_calculator = PerformanceCalculator()
        self.trading_simulator = TradingSimulator(config)
        self.result_manager = ResultManager()

    async def run_backtest(self, signals: list[TradingSignal]) -> BacktestResult:
        """백테스트 실행"""
        start_time = datetime.now()
        logger.info(f"백테스트 시작: {self.config.name}")

        try:
            # 거래 시뮬레이션
            daily_values = self.trading_simulator.simulate_trades(signals)

            # 성과 계산
            metrics = self.performance_calculator.calculate_metrics(
                daily_values, self.config.initial_cash
            )

            # 결과 생성
            end_time = datetime.now()
            result = BacktestResult(
                backtest_id=str(uuid.uuid4()),
                config=self.config,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=(end_time - start_time).total_seconds(),
                total_return=metrics["total_return"],
                annualized_return=metrics["annualized_return"],
                volatility=metrics["volatility"],
                sharpe_ratio=metrics["sharpe_ratio"],
                max_drawdown=metrics["max_drawdown"],
                total_trades=len(signals),
                winning_trades=len([s for s in signals if s.action == "BUY"]),
                losing_trades=len([s for s in signals if s.action == "SELL"]),
                win_rate=(
                    len([s for s in signals if s.action == "BUY"]) / len(signals)
                    if signals
                    else 0.0
                ),
                portfolio_history_path=None,
                trades_history_path=None,
                error_message=None,
            )

            # 결과 저장
            self.result_manager.save_result(result)

            logger.info(f"백테스트 완료: {self.config.name}")
            return result

        except Exception as e:
            logger.error(f"백테스트 실행 중 오류: {e}")
            end_time = datetime.now()

            return BacktestResult(
                backtest_id=str(uuid.uuid4()),
                config=self.config,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=(end_time - start_time).total_seconds(),
                total_return=0.0,
                annualized_return=0.0,
                volatility=0.0,
                sharpe_ratio=0.0,
                max_drawdown=0.0,
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0.0,
                portfolio_history_path=None,
                trades_history_path=None,
                status="failed",
                error_message=str(e),
            )
