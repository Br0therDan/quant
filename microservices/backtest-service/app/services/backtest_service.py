"""
Backtest Service Implementation
"""

import logging
import uuid
from datetime import datetime
from typing import Any

import numpy as np
from beanie import PydanticObjectId

from app.models.backtest import (
    Backtest,
    BacktestConfig,
    BacktestExecution,
    BacktestResult,
    BacktestStatus,
    PerformanceMetrics,
    Position,
    Trade,
    TradeType,
)

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

    def simulate_trades(
        self, signals: list[dict[str, Any]]
    ) -> tuple[list[float], list[Trade]]:
        """거래 시뮬레이션"""
        current_cash = self.config.initial_cash
        positions: dict[str, float] = {}  # symbol -> shares
        portfolio_values = [current_cash]
        trades: list[Trade] = []

        # 임시 가격 데이터 (실제로는 외부 데이터 소스에서 가져와야 함)
        price_data = {symbol: 100.0 for symbol in self.config.symbols}

        for _, signal in enumerate(signals):
            try:
                symbol = signal.get(
                    "symbol", self.config.symbols[0] if self.config.symbols else "AAPL"
                )
                action = signal.get("action", "BUY")
                quantity = signal.get("quantity", 10)

                # 가격 변동 시뮬레이션 (간단한 랜덤 워크)
                price_change = np.random.normal(0, 0.02)  # 2% 표준편차
                price_data[symbol] *= 1 + price_change
                current_price = price_data[symbol]

                if action == "BUY":
                    cost = quantity * current_price * (1 + self.config.commission_rate)
                    if current_cash >= cost:
                        current_cash -= cost
                        positions[symbol] = positions.get(symbol, 0) + quantity

                        # 거래 기록
                        trade = Trade(
                            symbol=symbol,
                            trade_type=TradeType.BUY,
                            quantity=quantity,
                            price=current_price,
                            timestamp=datetime.now(),
                            commission=quantity
                            * current_price
                            * self.config.commission_rate,
                        )
                        trades.append(trade)

                elif action == "SELL":
                    if positions.get(symbol, 0) >= quantity:
                        revenue = (
                            quantity * current_price * (1 - self.config.commission_rate)
                        )
                        current_cash += revenue
                        positions[symbol] -= quantity

                        # 거래 기록
                        trade = Trade(
                            symbol=symbol,
                            trade_type=TradeType.SELL,
                            quantity=quantity,
                            price=current_price,
                            timestamp=datetime.now(),
                            commission=quantity
                            * current_price
                            * self.config.commission_rate,
                        )
                        trades.append(trade)

                # 포트폴리오 가치 계산
                portfolio_value = current_cash
                for sym, shares in positions.items():
                    portfolio_value += shares * price_data[sym]

                portfolio_values.append(portfolio_value)

            except Exception as e:
                logger.error(f"거래 시뮬레이션 오류: {e}")
                continue

        return portfolio_values, trades


class BacktestService:
    """백테스트 서비스"""

    def __init__(self):
        self.performance_calculator = PerformanceCalculator()

    async def create_backtest(
        self,
        name: str,
        description: str = "",
        config: BacktestConfig = None,
    ) -> Backtest:
        """백테스트 생성"""
        backtest = Backtest(
            name=name,
            description=description,
            config=config,
            created_at=datetime.now(),
        )

        await backtest.insert()
        return backtest

    async def get_backtests(
        self,
        status: BacktestStatus | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Backtest]:
        """백테스트 목록 조회"""
        query = {}
        if status:
            query["status"] = status

        return await Backtest.find(query).skip(skip).limit(limit).to_list()

    async def get_backtest(self, backtest_id: str) -> Backtest | None:
        """백테스트 상세 조회"""
        try:
            return await Backtest.get(PydanticObjectId(backtest_id))
        except Exception:
            return None

    async def update_backtest(
        self,
        backtest_id: str,
        name: str | None = None,
        description: str | None = None,
        config: BacktestConfig | None = None,
    ) -> Backtest | None:
        """백테스트 수정"""
        backtest = await self.get_backtest(backtest_id)
        if not backtest:
            return None

        if name is not None:
            backtest.name = name
        if description is not None:
            backtest.description = description
        if config is not None:
            backtest.config = config

        backtest.updated_at = datetime.now()
        await backtest.save()
        return backtest

    async def delete_backtest(self, backtest_id: str) -> bool:
        """백테스트 삭제"""
        backtest = await self.get_backtest(backtest_id)
        if not backtest:
            return False

        await backtest.delete()
        return True

    async def execute_backtest(
        self,
        backtest_id: str,
        signals: list[dict[str, Any]],
    ) -> BacktestExecution | None:
        """백테스트 실행"""
        backtest = await self.get_backtest(backtest_id)
        if not backtest:
            return None

        execution_id = str(uuid.uuid4())
        start_time = datetime.now()

        try:
            # 백테스트 상태 업데이트
            backtest.status = BacktestStatus.RUNNING
            backtest.start_time = start_time
            await backtest.save()

            # 거래 시뮬레이션
            simulator = TradingSimulator(backtest.config)
            portfolio_values, trades = simulator.simulate_trades(signals)

            # 성과 지표 계산
            metrics = self.performance_calculator.calculate_metrics(
                portfolio_values, backtest.config.initial_cash
            )

            # 포지션 계산 (최종 상태)
            positions = {}
            for trade in trades:
                if trade.symbol not in positions:
                    positions[trade.symbol] = Position(
                        symbol=trade.symbol,
                        quantity=0,
                        average_price=0.0,
                        market_value=0.0,
                        unrealized_pnl=0.0,
                    )

                if trade.trade_type == TradeType.BUY:
                    old_qty = positions[trade.symbol].quantity
                    old_avg = positions[trade.symbol].average_price
                    new_qty = old_qty + trade.quantity
                    new_avg = (
                        ((old_qty * old_avg) + (trade.quantity * trade.price)) / new_qty
                        if new_qty > 0
                        else 0
                    )
                    positions[trade.symbol].quantity = new_qty
                    positions[trade.symbol].average_price = new_avg
                else:  # SELL
                    positions[trade.symbol].quantity -= trade.quantity

            end_time = datetime.now()

            # 백테스트 실행 기록 생성
            execution = BacktestExecution(
                backtest_id=backtest_id,
                execution_id=execution_id,
                start_time=start_time,
                end_time=end_time,
                status=BacktestStatus.COMPLETED,
                portfolio_values=portfolio_values,
                trades=trades,
                positions=positions,
                created_at=datetime.now(),
            )

            # 성과 지표 업데이트
            performance = PerformanceMetrics(
                total_return=metrics["total_return"],
                annualized_return=metrics["annualized_return"],
                volatility=metrics["volatility"],
                sharpe_ratio=metrics["sharpe_ratio"],
                max_drawdown=metrics["max_drawdown"],
                total_trades=len(trades),
                winning_trades=len(
                    [t for t in trades if t.trade_type == TradeType.BUY]
                ),
                losing_trades=len(
                    [t for t in trades if t.trade_type == TradeType.SELL]
                ),
                win_rate=(
                    len([t for t in trades if t.trade_type == TradeType.BUY])
                    / len(trades)
                    if trades
                    else 0.0
                ),
            )

            # 백테스트 완료 상태 업데이트
            backtest.status = BacktestStatus.COMPLETED
            backtest.end_time = end_time
            backtest.duration_seconds = (end_time - start_time).total_seconds()
            backtest.performance = performance
            await backtest.save()

            await execution.insert()
            return execution

        except Exception as e:
            logger.error(f"백테스트 실행 중 오류: {e}")

            # 실패 상태로 업데이트
            end_time = datetime.now()
            backtest.status = BacktestStatus.FAILED
            backtest.end_time = end_time
            backtest.duration_seconds = (end_time - start_time).total_seconds()
            await backtest.save()

            # 실패한 실행 기록
            execution = BacktestExecution(
                backtest_id=backtest_id,
                execution_id=execution_id,
                start_time=start_time,
                end_time=end_time,
                status=BacktestStatus.FAILED,
                error_message=str(e),
                created_at=datetime.now(),
            )
            await execution.insert()
            return execution

    async def get_backtest_executions(
        self,
        backtest_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[BacktestExecution]:
        """백테스트 실행 내역 조회"""
        return (
            await BacktestExecution.find(BacktestExecution.backtest_id == backtest_id)
            .skip(skip)
            .limit(limit)
            .sort([("start_time", -1)])
            .to_list()
        )

    async def get_backtest_results(
        self,
        backtest_id: str | None = None,
        execution_id: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[BacktestResult]:
        """백테스트 결과 조회"""
        query = {}
        if backtest_id:
            query["backtest_id"] = backtest_id
        if execution_id:
            query["execution_id"] = execution_id

        return await BacktestResult.find(query).skip(skip).limit(limit).to_list()

    async def create_backtest_result(
        self,
        backtest_id: str,
        execution_id: str,
        performance_metrics: PerformanceMetrics,
        portfolio_history_path: str | None = None,
        trades_history_path: str | None = None,
    ) -> BacktestResult:
        """백테스트 결과 생성"""
        result = BacktestResult(
            backtest_id=backtest_id,
            execution_id=execution_id,
            total_return=performance_metrics.total_return,
            annualized_return=performance_metrics.annualized_return,
            volatility=performance_metrics.volatility,
            sharpe_ratio=performance_metrics.sharpe_ratio,
            max_drawdown=performance_metrics.max_drawdown,
            total_trades=performance_metrics.total_trades,
            winning_trades=performance_metrics.winning_trades,
            losing_trades=performance_metrics.losing_trades,
            win_rate=performance_metrics.win_rate,
            portfolio_history_path=portfolio_history_path,
            trades_history_path=trades_history_path,
            created_at=datetime.now(),
        )

        await result.insert()
        return result
