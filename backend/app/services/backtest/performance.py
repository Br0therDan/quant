"""
성과 분석기 - 백테스트 성과 지표 계산
"""

import logging
from typing import Any

import numpy as np

from app.models.trading.backtest import PerformanceMetrics, Trade
from app.utils.calculators.performance import PerformanceCalculator

logger = logging.getLogger(__name__)


class PerformanceAnalyzer:
    """성과 분석기

    백테스트 결과를 분석하여 다양한 성과 지표를 계산합니다.
    Phase 2에서 도입된 컴포넌트입니다.
    """

    async def calculate_metrics(
        self,
        portfolio_values: list[float],
        trades: list[Trade],
        initial_capital: float,
        benchmark_returns: list[float] | None = None,
    ) -> PerformanceMetrics:
        """성과 지표 계산

        Args:
            portfolio_values: 포트폴리오 가치 시계열
            trades: 거래 내역
            initial_capital: 초기 자본
            benchmark_returns: 벤치마크 수익률 (선택)

        Returns:
            PerformanceMetrics 객체
        """
        if not portfolio_values:
            return self._empty_metrics()

        # 수익률 계산
        returns = self._calculate_returns(portfolio_values)

        # 기본 지표
        total_return = (portfolio_values[-1] - initial_capital) / initial_capital

        # PerformanceCalculator를 사용한 지표 계산
        annualized_return = PerformanceCalculator.annualized_return(
            total_return, len(portfolio_values)
        )
        volatility = PerformanceCalculator.annualized_volatility(returns)
        sharpe_ratio = PerformanceCalculator.sharpe_ratio(returns)
        max_drawdown = PerformanceCalculator.max_drawdown(portfolio_values)

        # 거래 통계
        trade_stats = self._analyze_trades(trades)

        return PerformanceMetrics(
            total_return=round(total_return, 4),
            annualized_return=round(annualized_return, 4),
            volatility=round(volatility, 4),
            sharpe_ratio=round(sharpe_ratio, 4),
            max_drawdown=round(max_drawdown, 4),
            total_trades=trade_stats["total_trades"],
            winning_trades=trade_stats["winning_trades"],
            losing_trades=trade_stats["losing_trades"],
            win_rate=round(trade_stats["win_rate"], 4),
        )

    def _calculate_returns(self, portfolio_values: list[float]) -> np.ndarray:
        """수익률 계산

        Note: PerformanceCalculator는 pandas Series/numpy array를 받지만,
        여기서는 백테스트 특화 로직으로 유지합니다.
        """
        if len(portfolio_values) < 2:
            return np.array([])

        values = np.array(portfolio_values)
        returns = np.diff(values) / values[:-1]
        return returns

    def _analyze_trades(self, trades: list[Trade]) -> dict[str, Any]:
        """거래 통계 분석"""
        if not trades:
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
            }

        # 간단한 승/패 계산 (실제로는 매수/매도 매칭 필요)
        # 여기서는 매수를 승리, 매도를 손실로 가정 (임시)
        wins = [t for t in trades if t.trade_type.value == "BUY"]
        losses = [t for t in trades if t.trade_type.value == "SELL"]

        return {
            "total_trades": len(trades),
            "winning_trades": len(wins),
            "losing_trades": len(losses),
            "win_rate": len(wins) / len(trades) if trades else 0.0,
        }

    def _empty_metrics(self) -> PerformanceMetrics:
        """빈 메트릭 반환"""
        return PerformanceMetrics(
            total_return=0.0,
            annualized_return=0.0,
            volatility=0.0,
            sharpe_ratio=0.0,
            max_drawdown=0.0,
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            win_rate=0.0,
        )
