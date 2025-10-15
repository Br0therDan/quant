"""
Strategy Management Service Layer
"""

import logging
from datetime import datetime, timezone
from typing import Any

from app.core.config import get_settings
from app.models.trading.performance import StrategyPerformance
from app.models.trading.strategy import (
    SignalType,
    Strategy,
    StrategyExecution,
    StrategyTemplate,
    StrategyType,
    StrategyConfigUnion,
)

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


class StrategyService:
    """Service for managing trading strategies"""

    def __init__(self):
        self.settings = get_settings()

        # Strategy class mapping
        self.strategy_classes = {}
        if STRATEGY_IMPORTS_AVAILABLE:
            self.strategy_classes = {
                StrategyType.BUY_AND_HOLD: BuyAndHoldStrategy,
                StrategyType.MOMENTUM: MomentumStrategy,
                StrategyType.RSI_MEAN_REVERSION: RSIMeanReversionStrategy,
                StrategyType.SMA_CROSSOVER: SMACrossoverStrategy,
            }

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
        """전략 타입에 맞는 기본 설정 반환"""
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
        """Get strategy by ID"""
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
        """Get list of strategies with filters"""

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
        """Update strategy"""

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
        """Delete strategy (soft delete by setting inactive)"""

        strategy = await self.get_strategy(strategy_id)
        if not strategy:
            return False

        strategy.is_active = False
        strategy.updated_at = datetime.now(timezone.utc)
        await strategy.save()

        logger.info(f"Deleted strategy: {strategy.name}")
        return True

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

        if not STRATEGY_IMPORTS_AVAILABLE:
            logger.warning("Strategy execution not available - imports missing")
            return None

        try:
            # Get strategy class
            strategy_class = self.strategy_classes.get(strategy.strategy_type)
            if not strategy_class:
                logger.error(
                    f"Strategy class not found for type: {strategy.strategy_type}"
                )
                return None

            # Create strategy instance (simplified - would need proper config mapping)
            # This is a simplified implementation - real implementation would need
            # proper configuration object creation based on strategy type
            mock_config = type(
                "Config", (), {"name": strategy.name, **strategy.parameters}
            )

            _ = strategy_class(mock_config)  # Create instance but don't use it

            # Mock signal generation (would use real market data in production)
            signal_type = SignalType.HOLD  # Default
            signal_strength = 0.5

            execution = StrategyExecution(
                strategy_id=strategy_id,
                strategy_name=strategy.name,
                symbol=symbol,
                signal_type=signal_type,
                signal_strength=signal_strength,
                price=market_data.get("close", 100.0),  # Mock price
                timestamp=datetime.now(timezone.utc),
                metadata=market_data,
                backtest_id=None,  # 단독 실행의 경우 None
            )

            await execution.insert()
            logger.info(f"Executed strategy {strategy.name} for {symbol}")
            return execution

        except Exception as e:
            logger.error(f"Failed to execute strategy {strategy.name}: {e}")
            return None

    async def get_strategy_executions(
        self,
        strategy_id: str | None = None,
        symbol: str | None = None,
        limit: int = 100,
    ) -> list[StrategyExecution]:
        """Get strategy execution history"""

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

    # Template management methods
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

        template = StrategyTemplate(
            name=name,
            strategy_type=strategy_type,
            description=description,
            default_config=default_config,
            category=category,
            tags=tags or [],
        )

        await template.insert()
        logger.info(f"Created template: {name}")
        return template

    async def get_templates(
        self,
        strategy_type: StrategyType | None = None,
    ) -> list[StrategyTemplate]:
        """Get strategy templates"""

        query = {}
        if strategy_type:
            query["strategy_type"] = strategy_type

        templates = await StrategyTemplate.find(query).to_list()
        return templates

    async def get_template_by_id(self, template_id: str) -> StrategyTemplate | None:
        """Get template by ID"""
        try:
            template = await StrategyTemplate.get(template_id)
            return template
        except Exception as e:
            logger.error(f"Failed to get template {template_id}: {e}")
            return None

    async def delete_template(self, template_id: str) -> bool:
        """Delete template by ID"""
        try:
            template = await StrategyTemplate.get(template_id)
            if not template:
                return False

            await template.delete()
            logger.info(f"Template {template_id} deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to delete template {template_id}: {e}")
            return False

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
        try:
            template = await StrategyTemplate.get(template_id)
            if not template:
                return None

            # Update fields if provided
            if name is not None:
                template.name = name
            if description is not None:
                template.description = description
            if default_config is not None:
                template.default_config = default_config
            if category is not None:
                template.category = category
            if tags is not None:
                template.tags = tags

            # Update timestamp
            template.updated_at = datetime.now()
            await template.save()

            logger.info(f"Template {template_id} updated successfully")
            return template
        except Exception as e:
            logger.error(f"Failed to update template {template_id}: {e}")
            return None

    async def create_strategy_from_template(
        self,
        template_id: str,
        name: str,
        parameter_overrides: dict[str, Any] | None = None,
        user_id: str | None = None,
    ) -> Strategy | None:
        """Create strategy instance from template"""

        try:
            template = await StrategyTemplate.get(template_id)
            if not template:
                return None

            # Use template config or merge with overrides
            config = template.default_config
            if parameter_overrides:
                # parameter_overrides가 딕셔너리라면 config를 업데이트
                # Pydantic model_copy를 사용하여 업데이트
                config = template.default_config.model_copy(update=parameter_overrides)

            # Increment template usage
            template.usage_count += 1
            await template.save()

            # Create strategy
            strategy = await self.create_strategy(
                name=name,
                strategy_type=template.strategy_type,
                description=f"Created from template: {template.name}",
                config=config,
                tags=template.tags,
                user_id=user_id,
            )

            return strategy

        except Exception as e:
            logger.error(f"Failed to create strategy from template: {e}")
            return None

    async def get_strategy_performance(
        self, strategy_id: str
    ) -> StrategyPerformance | None:
        """Get strategy performance metrics"""

        try:
            performance = await StrategyPerformance.find_one(
                {"strategy_id": strategy_id}
            )
            return performance
        except Exception as e:
            logger.error(f"Failed to get performance for strategy {strategy_id}: {e}")
            return None

    async def calculate_performance_metrics(
        self, strategy_id: str
    ) -> StrategyPerformance | None:
        """Calculate and store performance metrics for a strategy"""

        try:
            executions = await self.get_strategy_executions(strategy_id=strategy_id)

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

            strategy = await self.get_strategy(strategy_id)

            # Create or update performance record
            performance = StrategyPerformance(
                strategy_id=strategy_id,
                strategy_name=strategy.name if strategy else "Unknown",
                total_signals=total_signals,
                buy_signals=buy_signals,
                sell_signals=sell_signals,
                hold_signals=hold_signals,
                avg_signal_strength=avg_signal_strength,
                start_date=executions[-1].timestamp if executions else None,
                end_date=executions[0].timestamp if executions else None,
                # 필수 필드 기본값 설정
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

    async def get_strategy_instance(
        self,
        strategy_type: StrategyType,
        config: StrategyConfigUnion,
    ):
        """전략 타입과 Config로 전략 인스턴스 생성

        Args:
            strategy_type: 전략 타입
            config: 타입 안전한 전략 설정 (SMACrossoverConfig, RSIMeanReversionConfig, etc.)

        Returns:
            전략 인스턴스 또는 None
        """
        if not STRATEGY_IMPORTS_AVAILABLE:
            logger.error("Strategy classes not available")
            return None

        if strategy_type not in self.strategy_classes:
            logger.error(f"Unknown strategy type: {strategy_type}")
            return None

        try:
            strategy_class = self.strategy_classes[strategy_type]

            # Config 타입 검증
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

            # 전략 인스턴스 생성
            instance = strategy_class(config=config)

            logger.info(f"Created strategy instance: {strategy_type}")
            return instance

        except Exception as e:
            logger.error(f"Failed to create strategy instance {strategy_type}: {e}")
            return None
