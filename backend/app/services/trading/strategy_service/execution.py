"""
Strategy Execution and Signal Generation
"""

import logging
from datetime import datetime, timezone
from typing import Any

import pandas as pd

from app.core.config import get_settings
from app.models.trading.strategy import (
    SignalType,
    StrategyExecution,
    StrategyType,
    StrategyConfigUnion,
)
from app.models.trading.backtest import BacktestConfig, Trade, TradeType, OrderType
from app.utils.validators.strategy import StrategyValidator
from app.services.backtest.trade_engine import TradeEngine
from app.services.backtest.performance import PerformanceAnalyzer

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
        config: StrategyConfigUnion,
        is_active: bool,
        symbol: str,
        market_data: dict[str, Any],
    ) -> StrategyExecution | None:
        """Execute strategy and generate signals

        Args:
            strategy_id: Strategy ID
            strategy_name: Strategy name
            strategy_type: Strategy type
            config: Strategy configuration
            is_active: Whether strategy is active
            symbol: Trading symbol
            market_data: Market data dict with start_date, end_date

        Returns:
            StrategyExecution if successful, None otherwise
        """
        if not is_active:
            return None

        if not STRATEGY_IMPORTS_AVAILABLE:
            logger.warning("Strategy execution not available - imports missing")
            return None

        try:
            # Get strategy instance
            strategy_instance = await self.get_strategy_instance(
                strategy_type=strategy_type,
                config=config,
            )

            if not strategy_instance:
                logger.error(f"Failed to create strategy instance for {strategy_type}")
                return None

            # Fetch market data from MarketDataService
            from app.services.service_factory import service_factory

            market_data_service = service_factory.get_market_data_service()
            stock_service = market_data_service.stock

            start_date_str = market_data.get("start_date")
            end_date_str = market_data.get("end_date")

            if not start_date_str or not end_date_str:
                logger.error(
                    f"Missing start_date or end_date in market_data. "
                    f"Received: {market_data}"
                )
                return None

            # Parse dates (ensure timezone-naive by extracting date part only)
            # Extract YYYY-MM-DD only (ignore time and timezone)
            start_date_only = (
                start_date_str.split("T")[0]
                if "T" in start_date_str
                else start_date_str[:10]
            )
            end_date_only = (
                end_date_str.split("T")[0] if "T" in end_date_str else end_date_str[:10]
            )

            # Parse as naive datetime
            start_date = datetime.strptime(start_date_only, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_only, "%Y-%m-%d")

            # Fetch stock data
            stock_data = await stock_service.get_daily_prices(
                symbol=symbol,
                outputsize="full",  # Get all available data
                adjusted=True,
            )

            if not stock_data or len(stock_data) == 0:
                logger.error(f"No market data available for {symbol}")
                return None

            # Convert to DataFrame - normalize ALL datetimes to strings immediately
            # This completely avoids any timezone issues
            records = []
            for d in stock_data:
                try:
                    # Extract date as YYYY-MM-DD string (no datetime objects at all)
                    if isinstance(d.date, str):
                        date_str = d.date[:10]
                    else:
                        # Handle both timezone-aware and naive datetimes
                        # by converting to date() first, then string
                        if hasattr(d.date, "date"):
                            date_str = d.date.date().isoformat()  # YYYY-MM-DD
                        else:
                            date_str = str(d.date)[:10]

                    records.append(
                        {
                            "date": date_str,  # Keep as string
                            "open": float(d.open),
                            "high": float(d.high),
                            "low": float(d.low),
                            "close": float(d.close),
                            "volume": int(d.volume),
                            "symbol": symbol,
                        }
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to convert data point: {d}, "
                        f"date type: {type(d.date)}, "
                        f"error: {e}"
                    )
                    continue  # Skip this data point

            # Create DataFrame with date as string
            df = pd.DataFrame(records)

            if df.empty:
                logger.error(f"Failed to create DataFrame for {symbol}")
                return None

            # Filter by date range using STRING comparison (completely timezone-safe)
            df = df[(df["date"] >= start_date_only) & (df["date"] <= end_date_only)]

            if df.empty:
                logger.warning(
                    f"No data in date range for {symbol}: {start_date_only} to {end_date_only}"
                )
                # Don't return None, use available data
                df = pd.DataFrame(records)  # Use all data

            # Convert to datetime for strategy (after filtering)
            try:
                df["timestamp"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
                df = df.drop(columns=["date"])
            except Exception as e:
                logger.error(f"Failed to convert dates to timestamp: {e}")
                raise

            # Set timestamp as index
            df.set_index("timestamp", inplace=True)
            df.sort_index(inplace=True)

            # ============================================================
            # STEP 1: Generate signals using strategy
            # ============================================================
            signals = strategy_instance.generate_signals(df)

            if not signals or len(signals) == 0:
                logger.warning(f"No signals generated for {symbol}")
                # Return HOLD signal
                signal_type = SignalType.HOLD
                signal_strength = 0.5
                price = float(df["close"].iloc[-1]) if not df.empty else 100.0
            else:
                # Use the latest signal
                latest_signal = signals[-1]
                signal_type = latest_signal.signal_type
                signal_strength = latest_signal.strength
                price = float(latest_signal.price)

            # ============================================================
            # STEP 2: TradeEngine - Simulate trades based on signals
            # ============================================================
            trade_engine_config = BacktestConfig(
                name=f"Strategy Execution - {strategy_name}",
                start_date=start_date,
                end_date=end_date,
                symbols=[symbol],
                initial_cash=100000.0,  # 기본 초기 자금
                commission_rate=0.001,  # 0.1% 수수료
                slippage_rate=0.0005,  # 0.05% 슬리피지
                rebalance_frequency=None,
            )
            trade_engine = TradeEngine(config=trade_engine_config)

            executed_trades: list[Trade] = []
            portfolio_values: list[float] = [trade_engine_config.initial_cash]

            # 신호 기반 거래 시뮬레이션
            for idx, signal in enumerate(signals):
                if signal.signal_type == SignalType.BUY and signal.strength > 0.6:
                    # 매수 신호 (강도 > 0.6)
                    # 사용 가능 자금의 일정 비율 투자
                    investment_ratio = signal.strength  # 신호 강도만큼 투자
                    max_investment = trade_engine.portfolio.cash * investment_ratio
                    quantity = max_investment / signal.price * 0.95  # 수수료 고려

                    trade = trade_engine.execute_order(
                        symbol=symbol,
                        quantity=quantity,
                        price=signal.price,
                        order_type=OrderType.MARKET,
                        trade_type=TradeType.BUY,
                        timestamp=signal.timestamp,
                        signal_id=f"{strategy_id}_{idx}",
                    )
                    if trade:
                        executed_trades.append(trade)

                elif signal.signal_type == SignalType.SELL and signal.strength > 0.6:
                    # 매도 신호 (강도 > 0.6)
                    current_position = trade_engine.portfolio.positions.get(symbol, 0.0)
                    if current_position > 0:
                        sell_quantity = current_position * signal.strength  # 신호 강도만큼 매도

                        trade = trade_engine.execute_order(
                            symbol=symbol,
                            quantity=sell_quantity,
                            price=signal.price,
                            order_type=OrderType.MARKET,
                            trade_type=TradeType.SELL,
                            timestamp=signal.timestamp,
                            signal_id=f"{strategy_id}_{idx}",
                        )
                        if trade:
                            executed_trades.append(trade)

                # 포트폴리오 가치 기록
                current_value = trade_engine.portfolio.cash
                for (
                    pos_symbol,
                    pos_quantity,
                ) in trade_engine.portfolio.positions.items():
                    if pos_symbol == symbol:
                        current_value += pos_quantity * signal.price
                portfolio_values.append(current_value)

            # ============================================================
            # STEP 3: PerformanceAnalyzer - Calculate performance metrics
            # ============================================================
            performance_analyzer = PerformanceAnalyzer()
            performance_metrics = await performance_analyzer.calculate_metrics(
                portfolio_values=portfolio_values,
                trades=executed_trades,
                initial_capital=trade_engine_config.initial_cash,
                benchmark_returns=None,
            )

            # ============================================================
            # STEP 4: RiskAnalyzer - Analyze risk (basic implementation)
            # ============================================================
            # 간단한 리스크 지표 계산
            max_drawdown = performance_metrics.max_drawdown
            volatility = performance_metrics.volatility
            sharpe_ratio = performance_metrics.sharpe_ratio

            risk_assessment = (
                "LOW"
                if max_drawdown < 0.1
                else "MEDIUM"
                if max_drawdown < 0.2
                else "HIGH"
            )

            # 신호 강도 검증
            signal_strength = StrategyValidator.validate_signal_strength(
                signal_strength
            )

            # ============================================================
            # STEP 5: Save execution result with performance metrics
            # ============================================================
            execution = StrategyExecution(
                strategy_id=strategy_id,
                strategy_name=strategy_name,
                symbol=symbol,
                signal_type=signal_type,
                signal_strength=signal_strength,
                price=price,  # Latest signal price
                timestamp=datetime.now(timezone.utc),
                metadata={
                    "start_date": start_date_str,
                    "end_date": end_date_str,
                    "data_points": len(df),
                    "signal_count": len(signals) if signals else 0,
                    # TradeEngine 결과
                    "trades_executed": len(executed_trades),
                    "final_portfolio_value": (
                        portfolio_values[-1] if portfolio_values else 0.0
                    ),
                    # PerformanceAnalyzer 결과
                    "total_return": float(performance_metrics.total_return),
                    "sharpe_ratio": float(sharpe_ratio) if sharpe_ratio else 0.0,
                    "max_drawdown": float(max_drawdown) if max_drawdown else 0.0,
                    "volatility": float(volatility) if volatility else 0.0,
                    "win_rate": (
                        float(performance_metrics.win_rate)
                        if performance_metrics.win_rate
                        else 0.0
                    ),
                    # RiskAnalyzer 결과
                    "risk_assessment": risk_assessment,
                },
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
            return instance

        except Exception as e:
            logger.error(f"Failed to create strategy instance {strategy_type}: {e}")
            return None
