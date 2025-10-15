"""
Strategy CRUD Operations
"""

import logging
from datetime import datetime, timezone

from app.core.config import get_settings
from app.models.trading.strategy import (
    Strategy,
    StrategyType,
    StrategyConfigUnion,
)

try:
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


class StrategyCRUD:
    """Strategy CRUD operations handler"""

    def __init__(self):
        self.settings = get_settings()

    async def create_strategy(
        self,
        name: str,
        strategy_type: StrategyType,
        description: str | None = None,
        config: StrategyConfigUnion | None = None,
        tags: list[str] | None = None,
        user_id: str | None = None,
    ) -> Strategy:
        """Create a new strategy

        Args:
            name: Strategy name
            strategy_type: Type of strategy
            description: Optional description
            config: Strategy configuration (uses default if not provided)
            tags: Optional tags
            user_id: Optional user ID

        Returns:
            Created strategy
        """
        strategy = Strategy(
            name=name,
            strategy_type=strategy_type,
            description=description or "",
            config=config or self._get_default_config(strategy_type),
            tags=tags or [],
            user_id=user_id,
            created_by="system",  # 시스템 기본값
        )

        await strategy.insert()
        logger.info(f"Created strategy: {name} ({strategy_type})")
        return strategy

    def _get_default_config(self, strategy_type: StrategyType) -> StrategyConfigUnion:
        """Get default configuration for strategy type

        Args:
            strategy_type: Type of strategy

        Returns:
            Default configuration for the strategy type

        Raises:
            ValueError: If strategy type is unknown
        """
        if strategy_type == StrategyType.SMA_CROSSOVER:
            return SMACrossoverConfig(short_window=20, long_window=50)
        elif strategy_type == StrategyType.RSI_MEAN_REVERSION:
            return RSIMeanReversionConfig(
                rsi_period=14, oversold_threshold=30, overbought_threshold=70
            )
        elif strategy_type == StrategyType.MOMENTUM:
            return MomentumConfig(momentum_period=20, top_n_stocks=5)
        elif strategy_type == StrategyType.BUY_AND_HOLD:
            return BuyAndHoldConfig(allocation={})
        else:
            raise ValueError(f"Unknown strategy type: {strategy_type}")

    async def get_strategy(self, strategy_id: str) -> Strategy | None:
        """Get strategy by ID

        Args:
            strategy_id: Strategy ID

        Returns:
            Strategy if found, None otherwise
        """
        try:
            strategy = await Strategy.get(strategy_id)
            return strategy
        except Exception as e:
            logger.error(f"Failed to get strategy {strategy_id}: {e}")
            return None

    async def get_strategies(
        self,
        strategy_type: StrategyType | None = None,
        is_active: bool | None = None,
        is_template: bool | None = None,
        limit: int = 50,
        user_id: str | None = None,
    ) -> list[Strategy]:
        """Get list of strategies with filters

        Args:
            strategy_type: Filter by strategy type
            is_active: Filter by active status
            is_template: Filter by template status
            limit: Maximum number of results
            user_id: Filter by user ID

        Returns:
            List of strategies matching filters
        """
        query = {}
        if strategy_type:
            query["strategy_type"] = strategy_type
        if is_active is not None:
            query["is_active"] = is_active
        if is_template is not None:
            query["is_template"] = is_template
        if user_id:
            query["user_id"] = user_id

        strategies = await Strategy.find(query).limit(limit).to_list()
        return strategies

    async def update_strategy(
        self,
        strategy_id: str,
        name: str | None = None,
        description: str | None = None,
        config: StrategyConfigUnion | None = None,
        is_active: bool | None = None,
        tags: list[str] | None = None,
    ) -> Strategy | None:
        """Update strategy

        Args:
            strategy_id: Strategy ID
            name: Optional new name
            description: Optional new description
            config: Optional new configuration
            is_active: Optional new active status
            tags: Optional new tags

        Returns:
            Updated strategy if found, None otherwise
        """
        strategy = await self.get_strategy(strategy_id)
        if not strategy:
            return None

        if name:
            strategy.name = name
        if description is not None:
            strategy.description = description
        if config is not None:
            strategy.config = config
        if is_active is not None:
            strategy.is_active = is_active
        if tags is not None:
            strategy.tags = tags

        strategy.updated_at = datetime.now(timezone.utc)
        await strategy.save()

        logger.info(f"Updated strategy: {strategy.name}")
        return strategy

    async def delete_strategy(self, strategy_id: str) -> bool:
        """Delete strategy (soft delete by setting inactive)

        Args:
            strategy_id: Strategy ID

        Returns:
            True if deleted successfully, False otherwise
        """
        strategy = await self.get_strategy(strategy_id)
        if not strategy:
            return False

        strategy.is_active = False
        strategy.updated_at = datetime.now(timezone.utc)
        await strategy.save()

        logger.info(f"Deleted strategy: {strategy.name}")
        return True
