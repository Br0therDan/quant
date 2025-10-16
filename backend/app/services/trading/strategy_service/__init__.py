"""
Strategy Service - Main Integration
Delegation pattern으로 각 모듈 통합
"""

import logging
from typing import Any

from app.core.config import get_settings
from app.models.trading.performance import StrategyPerformance
from app.models.trading.strategy import (
    Strategy,
    StrategyExecution,
    StrategyTemplate,
    StrategyType,
    StrategyConfigUnion,
)
from .crud import StrategyCRUD
from .execution import StrategyExecutor
from .template_manager import TemplateManager
from .performance import PerformanceAnalyzer

logger = logging.getLogger(__name__)


class StrategyService:
    """통합 전략 관리 서비스 (Delegation 패턴)"""

    def __init__(self):
        self.settings = get_settings()

        # Delegate modules
        self._crud = StrategyCRUD()
        self._executor = StrategyExecutor()
        self._template_manager = TemplateManager()
        self._performance_analyzer = PerformanceAnalyzer()

    # ============================================================
    # CRUD Operations (위임 to StrategyCRUD)
    # ============================================================

    async def create_strategy(
        self,
        name: str,
        strategy_type: StrategyType,
        description: str | None = None,
        config: StrategyConfigUnion | None = None,
        tags: list[str] | None = None,
        user_id: str | None = None,
    ) -> Strategy:
        """Create a new strategy"""
        return await self._crud.create_strategy(
            name=name,
            strategy_type=strategy_type,
            description=description,
            config=config,
            tags=tags,
            user_id=user_id,
        )

    async def get_strategy(self, strategy_id: str) -> Strategy | None:
        """Get strategy by ID"""
        return await self._crud.get_strategy(strategy_id)

    async def get_strategies(
        self,
        strategy_type: StrategyType | None = None,
        is_active: bool | None = None,
        is_template: bool | None = None,
        limit: int = 50,
        user_id: str | None = None,
    ) -> list[Strategy]:
        """Get list of strategies with filters"""
        return await self._crud.get_strategies(
            strategy_type=strategy_type,
            is_active=is_active,
            is_template=is_template,
            limit=limit,
            user_id=user_id,
        )

    async def update_strategy(
        self,
        strategy_id: str,
        name: str | None = None,
        description: str | None = None,
        config: StrategyConfigUnion | None = None,
        is_active: bool | None = None,
        tags: list[str] | None = None,
    ) -> Strategy | None:
        """Update strategy"""
        return await self._crud.update_strategy(
            strategy_id=strategy_id,
            name=name,
            description=description,
            config=config,
            is_active=is_active,
            tags=tags,
        )

    async def delete_strategy(self, strategy_id: str) -> bool:
        """Delete strategy (soft delete by setting inactive)"""
        return await self._crud.delete_strategy(strategy_id)

    # ============================================================
    # Execution Operations (위임 to StrategyExecutor)
    # ============================================================

    async def execute_strategy(
        self,
        strategy_id: str,
        symbol: str,
        market_data: dict[str, Any],
    ) -> StrategyExecution | None:
        """Execute strategy and generate signals"""
        strategy = await self.get_strategy(strategy_id)
        if not strategy or not strategy.is_active:
            return None

        # config가 None이면 기본값으로 생성
        config = strategy.config
        if config is None:
            from app.strategies.configs import (
                SMACrossoverConfig,
                RSIMeanReversionConfig,
                MomentumConfig,
                BuyAndHoldConfig,
            )
            from app.schemas.enums import StrategyType

            common_defaults = {
                "lookback_period": 252,
                "min_data_points": 30,
                "max_position_size": 1.0,
            }

            if strategy.strategy_type == StrategyType.SMA_CROSSOVER:
                config = SMACrossoverConfig(
                    config_type="sma_crossover",
                    **common_defaults,
                    short_window=20,
                    long_window=50,
                )
            elif strategy.strategy_type == StrategyType.RSI_MEAN_REVERSION:
                config = RSIMeanReversionConfig(
                    config_type="rsi_mean_reversion",
                    **common_defaults,
                    rsi_period=14,
                    oversold_threshold=30,
                    overbought_threshold=70,
                )
            elif strategy.strategy_type == StrategyType.MOMENTUM:
                config = MomentumConfig(
                    config_type="momentum",
                    **common_defaults,
                    momentum_period=20,
                )
            else:
                config = BuyAndHoldConfig(
                    config_type="buy_and_hold",
                    **common_defaults,
                )

        return await self._executor.execute_strategy(
            strategy_id=strategy_id,
            strategy_name=strategy.name,
            strategy_type=strategy.strategy_type,
            config=config,
            is_active=strategy.is_active,
            symbol=symbol,
            market_data=market_data,
        )

    async def get_strategy_executions(
        self,
        strategy_id: str | None = None,
        symbol: str | None = None,
        limit: int = 100,
    ) -> list[StrategyExecution]:
        """Get strategy execution history"""
        return await self._executor.get_executions(
            strategy_id=strategy_id,
            symbol=symbol,
            limit=limit,
        )

    async def get_strategy_instance(
        self,
        strategy_type: StrategyType,
        config: StrategyConfigUnion,
    ):
        """Create type-safe strategy instance"""
        return await self._executor.get_strategy_instance(
            strategy_type=strategy_type,
            config=config,
        )

    # ============================================================
    # Template Operations (위임 to TemplateManager)
    # ============================================================

    async def create_template(
        self,
        name: str,
        strategy_type: StrategyType,
        description: str,
        default_config: StrategyConfigUnion,
        category: str = "general",
        tags: list[str] | None = None,
    ) -> StrategyTemplate:
        """Create strategy template"""
        return await self._template_manager.create_template(
            name=name,
            strategy_type=strategy_type,
            description=description,
            default_config=default_config,
            category=category,
            tags=tags,
        )

    async def get_templates(
        self,
        strategy_type: StrategyType | None = None,
    ) -> list[StrategyTemplate]:
        """Get strategy templates"""
        return await self._template_manager.get_templates(
            strategy_type=strategy_type,
        )

    async def get_template_by_id(self, template_id: str) -> StrategyTemplate | None:
        """Get template by ID"""
        return await self._template_manager.get_template_by_id(template_id)

    async def update_template(
        self,
        template_id: str,
        name: str | None = None,
        description: str | None = None,
        default_config: StrategyConfigUnion | None = None,
        category: str | None = None,
        tags: list[str] | None = None,
    ) -> StrategyTemplate | None:
        """Update template by ID"""
        return await self._template_manager.update_template(
            template_id=template_id,
            name=name,
            description=description,
            default_config=default_config,
            category=category,
            tags=tags,
        )

    async def delete_template(self, template_id: str) -> bool:
        """Delete template by ID"""
        return await self._template_manager.delete_template(template_id)

    async def create_strategy_from_template(
        self,
        template_id: str,
        name: str,
        parameter_overrides: dict[str, Any] | None = None,
        user_id: str | None = None,
    ) -> Strategy | None:
        """Create strategy instance from template"""
        # Get template first to get strategy_type
        template = await self._template_manager.get_template_by_id(template_id)
        if not template:
            return None

        return await self._template_manager.create_strategy_from_template(
            template_id=template_id,
            name=name,
            strategy_type=template.strategy_type,
            parameter_overrides=parameter_overrides,
            user_id=user_id,
            create_strategy_func=self.create_strategy,
        )

    # ============================================================
    # Performance Operations (위임 to PerformanceAnalyzer)
    # ============================================================

    async def get_strategy_performance(
        self, strategy_id: str
    ) -> StrategyPerformance | None:
        """Get strategy performance metrics"""
        return await self._performance_analyzer.get_performance(strategy_id)

    async def calculate_performance_metrics(
        self, strategy_id: str
    ) -> StrategyPerformance | None:
        """Calculate and store performance metrics for a strategy"""
        # Get strategy for name
        strategy = await self.get_strategy(strategy_id)
        if not strategy:
            return None

        # Get executions
        executions = await self.get_strategy_executions(strategy_id=strategy_id)

        return await self._performance_analyzer.calculate_metrics(
            strategy_id=strategy_id,
            user_id=strategy.user_id if strategy.user_id else "system",
            strategy_name=strategy.name,
            executions=executions,
        )
