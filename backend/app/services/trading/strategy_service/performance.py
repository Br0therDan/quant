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

            # Extract performance metrics from latest execution metadata
            # (TradeEngine + PerformanceAnalyzer results are stored in metadata)
            latest_execution = executions[0]  # Most recent
            metadata = latest_execution.metadata or {}

            total_return = metadata.get("total_return", 0.0)
            win_rate = metadata.get("win_rate", 0.0)
            sharpe_ratio = metadata.get("sharpe_ratio", 0.0)
            max_drawdown = metadata.get("max_drawdown", 0.0)
            volatility = metadata.get("volatility", 0.0)

            # Calculate avg_return_per_trade from executions
            trades_executed = metadata.get("trades_executed", 0)
            avg_return_per_trade = (
                total_return / trades_executed if trades_executed > 0 else 0.0
            )

            # Calmar ratio = Total Return / Max Drawdown
            calmar_ratio = (
                abs(total_return / max_drawdown) if max_drawdown != 0 else 0.0
            )

            # Accuracy = win_rate
            accuracy = win_rate

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
                # Performance metrics from TradeEngine + PerformanceAnalyzer
                total_return=float(total_return),
                win_rate=float(win_rate),
                avg_return_per_trade=float(avg_return_per_trade),
                max_drawdown=float(max_drawdown),
                sharpe_ratio=float(sharpe_ratio),
                calmar_ratio=float(calmar_ratio),
                volatility=float(volatility),
                accuracy=float(accuracy),
                backtest_id=None,
            )

            # Check if performance record exists
            existing = await StrategyPerformance.find_one({"strategy_id": strategy_id})
            if existing:
                # Update existing record with all fields
                existing.total_signals = performance.total_signals
                existing.buy_signals = performance.buy_signals
                existing.sell_signals = performance.sell_signals
                existing.hold_signals = performance.hold_signals
                existing.avg_signal_strength = performance.avg_signal_strength
                existing.total_return = performance.total_return
                existing.win_rate = performance.win_rate
                existing.avg_return_per_trade = performance.avg_return_per_trade
                existing.max_drawdown = performance.max_drawdown
                existing.sharpe_ratio = performance.sharpe_ratio
                existing.calmar_ratio = performance.calmar_ratio
                existing.volatility = performance.volatility
                existing.accuracy = performance.accuracy
                existing.updated_at = datetime.now(timezone.utc)
                await existing.save()
                logger.info(
                    f"Updated performance for {strategy_name}: "
                    f"return={total_return:.2%}, sharpe={sharpe_ratio:.2f}, "
                    f"win_rate={win_rate:.2%}"
                )
                return existing
            else:
                # Create new record
                await performance.insert()
                logger.info(
                    f"Created performance for {strategy_name}: "
                    f"return={total_return:.2%}, sharpe={sharpe_ratio:.2f}, "
                    f"win_rate={win_rate:.2%}"
                )
                return performance

        except Exception as e:
            logger.error(f"Failed to calculate performance metrics: {e}")
            return None
