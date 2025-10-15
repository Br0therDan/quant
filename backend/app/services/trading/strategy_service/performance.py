"""
Strategy Performance Analysis
"""

import logging
from datetime import datetime, timezone

from app.core.config import get_settings
from app.models.trading.performance import StrategyPerformance
from app.models.trading.strategy import SignalType, StrategyExecution

logger = logging.getLogger(__name__)


class PerformanceAnalyzer:
    """Strategy performance analysis handler"""

    def __init__(self):
        self.settings = get_settings()

    async def get_performance(self, strategy_id: str) -> StrategyPerformance | None:
        """Get strategy performance metrics

        Args:
            strategy_id: Strategy ID

        Returns:
            StrategyPerformance if found, None otherwise
        """
        try:
            performance = await StrategyPerformance.find_one(
                {"strategy_id": strategy_id}
            )
            return performance
        except Exception as e:
            logger.error(f"Failed to get performance for strategy {strategy_id}: {e}")
            return None

    async def calculate_metrics(
        self,
        strategy_id: str,
        strategy_name: str,
        executions: list[StrategyExecution],
    ) -> StrategyPerformance | None:
        """Calculate and store performance metrics for a strategy

        Args:
            strategy_id: Strategy ID
            strategy_name: Strategy name
            executions: List of strategy executions

        Returns:
            StrategyPerformance if successful, None otherwise
        """
        try:
            if not executions:
                return None

            # Calculate basic metrics
            total_signals = len(executions)
            buy_signals = sum(1 for e in executions if e.signal_type == SignalType.BUY)
            sell_signals = sum(
                1 for e in executions if e.signal_type == SignalType.SELL
            )
            hold_signals = sum(
                1 for e in executions if e.signal_type == SignalType.HOLD
            )

            avg_signal_strength = (
                sum(e.signal_strength for e in executions) / total_signals
            )

            # Create or update performance record
            performance = StrategyPerformance(
                strategy_id=strategy_id,
                strategy_name=strategy_name,
                total_signals=total_signals,
                buy_signals=buy_signals,
                sell_signals=sell_signals,
                hold_signals=hold_signals,
                avg_signal_strength=avg_signal_strength,
                start_date=executions[-1].timestamp if executions else None,
                end_date=executions[0].timestamp if executions else None,
                # Required fields with default values
                total_return=0.0,
                win_rate=0.0,
                avg_return_per_trade=0.0,
                max_drawdown=0.0,
                sharpe_ratio=0.0,
                calmar_ratio=0.0,
                volatility=0.0,
                backtest_id=None,
                accuracy=0.0,
            )

            # Check if performance record exists
            existing = await StrategyPerformance.find_one({"strategy_id": strategy_id})
            if existing:
                # Update existing record
                existing.total_signals = performance.total_signals
                existing.buy_signals = performance.buy_signals
                existing.sell_signals = performance.sell_signals
                existing.hold_signals = performance.hold_signals
                existing.avg_signal_strength = performance.avg_signal_strength
                existing.updated_at = datetime.now(timezone.utc)
                await existing.save()
                return existing
            else:
                # Create new record
                await performance.insert()
                return performance

        except Exception as e:
            logger.error(f"Failed to calculate performance metrics: {e}")
            return None
