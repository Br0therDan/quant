"""
Strategy Execution and Signal Generation
"""

import logging
from datetime import datetime, timezone
from typing import Any

from app.core.config import get_settings
from app.models.trading.strategy import (
    SignalType,
    StrategyExecution,
    StrategyType,
    StrategyConfigUnion,
)
from app.utils.validators.strategy import StrategyValidator

try:
    from app.strategies.buy_and_hold import BuyAndHoldStrategy
    from app.strategies.momentum import MomentumStrategy
    from app.strategies.rsi_mean_reversion import RSIMeanReversionStrategy
    from app.strategies.sma_crossover import SMACrossoverStrategy
    from app.strategies.configs import (
        SMACrossoverConfig,
        RSIMeanReversionConfig,
        MomentumConfig,
        BuyAndHoldConfig,
    )

    STRATEGY_IMPORTS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Strategy imports not available: {e}")
    STRATEGY_IMPORTS_AVAILABLE = False

logger = logging.getLogger(__name__)


class StrategyExecutor:
    """Strategy execution and signal generation handler"""

    def __init__(self):
        self.settings = get_settings()
        self.strategy_classes = self._initialize_strategy_classes()

    def _initialize_strategy_classes(self) -> dict:
        """Initialize strategy class mapping

        Returns:
            Dictionary mapping StrategyType to strategy class
        """
        if not STRATEGY_IMPORTS_AVAILABLE:
            return {}

        return {
            StrategyType.BUY_AND_HOLD: BuyAndHoldStrategy,
            StrategyType.MOMENTUM: MomentumStrategy,
            StrategyType.RSI_MEAN_REVERSION: RSIMeanReversionStrategy,
            StrategyType.SMA_CROSSOVER: SMACrossoverStrategy,
        }

    async def execute_strategy(
        self,
        strategy_id: str,
        strategy_name: str,
        strategy_type: StrategyType,
        is_active: bool,
        symbol: str,
        market_data: dict[str, Any],
    ) -> StrategyExecution | None:
        """Execute strategy and generate signals

        Args:
            strategy_id: Strategy ID
            strategy_name: Strategy name
            strategy_type: Strategy type
            is_active: Whether strategy is active
            symbol: Trading symbol
            market_data: Market data for signal generation

        Returns:
            StrategyExecution if successful, None otherwise
        """
        if not is_active:
            return None

        if not STRATEGY_IMPORTS_AVAILABLE:
            logger.warning("Strategy execution not available - imports missing")
            return None

        try:
            # Get strategy class
            strategy_class = self.strategy_classes.get(strategy_type)
            if not strategy_class:
                logger.error(f"Strategy class not found for type: {strategy_type}")
                return None

            # Mock signal generation (would use real market data in production)
            signal_type = SignalType.HOLD  # Default
            signal_strength = 0.5

            # 신호 강도 검증
            signal_strength = StrategyValidator.validate_signal_strength(
                signal_strength
            )

            execution = StrategyExecution(
                strategy_id=strategy_id,
                strategy_name=strategy_name,
                symbol=symbol,
                signal_type=signal_type,
                signal_strength=signal_strength,
                price=market_data.get("close", 100.0),  # Mock price
                timestamp=datetime.now(timezone.utc),
                metadata=market_data,
                backtest_id=None,  # 단독 실행의 경우 None
            )

            await execution.insert()
            logger.info(f"Executed strategy {strategy_name} for {symbol}")
            return execution

        except Exception as e:
            logger.error(f"Failed to execute strategy {strategy_name}: {e}")
            return None

    async def get_executions(
        self,
        strategy_id: str | None = None,
        symbol: str | None = None,
        limit: int = 100,
    ) -> list[StrategyExecution]:
        """Get strategy execution history

        Args:
            strategy_id: Filter by strategy ID
            symbol: Filter by symbol
            limit: Maximum number of results

        Returns:
            List of strategy executions
        """
        query = {}
        if strategy_id:
            query["strategy_id"] = strategy_id
        if symbol:
            query["symbol"] = symbol

        executions = (
            await StrategyExecution.find(query)
            .sort("-timestamp")
            .limit(limit)
            .to_list()
        )
        return executions

    async def get_strategy_instance(
        self,
        strategy_type: StrategyType,
        config: StrategyConfigUnion,
    ):
        """Create type-safe strategy instance

        Args:
            strategy_type: Type of strategy
            config: Type-safe strategy configuration

        Returns:
            Strategy instance or None

        Raises:
            TypeError: If config type doesn't match strategy type
        """
        if not STRATEGY_IMPORTS_AVAILABLE:
            logger.error("Strategy classes not available")
            return None

        if strategy_type not in self.strategy_classes:
            logger.error(f"Unknown strategy type: {strategy_type}")
            return None

        try:
            strategy_class = self.strategy_classes[strategy_type]

            # Config type validation
            expected_configs = {
                StrategyType.SMA_CROSSOVER: SMACrossoverConfig,
                StrategyType.RSI_MEAN_REVERSION: RSIMeanReversionConfig,
                StrategyType.MOMENTUM: MomentumConfig,
                StrategyType.BUY_AND_HOLD: BuyAndHoldConfig,
            }

            expected_config_type = expected_configs.get(strategy_type)
            if expected_config_type and not isinstance(config, expected_config_type):
                raise TypeError(
                    f"Invalid config type for {strategy_type}: "
                    f"expected {expected_config_type.__name__}, "
                    f"got {type(config).__name__}"
                )

            # Create strategy instance
            instance = strategy_class(config=config)

            logger.info(f"Created strategy instance: {strategy_type}")
            return instance

        except Exception as e:
            logger.error(f"Failed to create strategy instance {strategy_type}: {e}")
            return None
