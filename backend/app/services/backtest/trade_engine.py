"""
통합 거래 실행 엔진
"""

import logging
import uuid
from datetime import datetime
from typing import Optional

from app.models.backtest import (
    BacktestConfig,
    Trade,
    TradeType,
    OrderType,
)

logger = logging.getLogger(__name__)


class Portfolio:
    """포트폴리오 상태 관리"""

    def __init__(self, initial_cash: float):
        self.cash = initial_cash
        self.initial_cash = initial_cash
        self.positions: dict[str, float] = {}  # symbol -> quantity
        self.position_costs: dict[str, float] = {}  # symbol -> avg_cost

    @property
    def total_value(self) -> float:
        """총 포트폴리오 가치"""
        return self.cash + sum(
            qty * self.position_costs.get(symbol, 0.0)
            for symbol, qty in self.positions.items()
        )

    def update_position(
        self,
        symbol: str,
        quantity: float,
        price: float,
        is_buy: bool,
    ) -> None:
        """포지션 업데이트"""
        current_qty = self.positions.get(symbol, 0.0)

        if is_buy:
            # 매수: 포지션 증가
            new_qty = current_qty + quantity
            # 평균 단가 계산
            if current_qty > 0:
                current_cost = self.position_costs.get(symbol, 0.0)
                total_cost = (current_cost * current_qty) + (price * quantity)
                avg_cost = total_cost / new_qty
            else:
                avg_cost = price

            self.positions[symbol] = new_qty
            self.position_costs[symbol] = avg_cost
        else:
            # 매도: 포지션 감소
            new_qty = current_qty - quantity
            if new_qty <= 0:
                # 포지션 청산
                self.positions.pop(symbol, None)
                self.position_costs.pop(symbol, None)
            else:
                self.positions[symbol] = new_qty
                # 평균 단가 유지


class TradeCosts:
    """거래 비용 계산"""

    def __init__(self, commission_rate: float, slippage_rate: float):
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate

    def calculate(
        self,
        price: float,
        quantity: float,
        is_buy: bool = True,
    ) -> dict[str, float]:
        """거래 비용 계산

        Args:
            price: 거래 가격
            quantity: 거래 수량
            is_buy: 매수 여부

        Returns:
            dict: {
                'commission': 수수료,
                'slippage': 슬리피지,
                'total_cost': 총 비용,
                'execution_price': 실제 체결 가격
            }
        """
        # 슬리피지 적용 (매수: +, 매도: -)
        slippage_amount = price * self.slippage_rate
        execution_price = price + slippage_amount if is_buy else price - slippage_amount

        # 수수료 계산
        commission = execution_price * quantity * self.commission_rate

        # 총 비용
        total_cost = (execution_price * quantity) + commission

        return {
            "commission": commission,
            "slippage": slippage_amount * quantity,
            "total_cost": total_cost,
            "execution_price": execution_price,
        }


class TradeEngine:
    """통합 거래 실행 엔진"""

    def __init__(self, config: BacktestConfig):
        self.config = config
        self.portfolio = Portfolio(config.initial_cash)
        self.trade_costs = TradeCosts(
            commission_rate=config.commission_rate,
            slippage_rate=getattr(config, "slippage_rate", 0.0),
        )

    def execute_order(
        self,
        symbol: str,
        quantity: float,
        price: float,
        order_type: OrderType,
        trade_type: TradeType,
        timestamp: datetime,
        signal_id: Optional[str] = None,
    ) -> Optional[Trade]:
        """주문 실행

        Args:
            symbol: 종목 심볼
            quantity: 수량
            price: 가격
            order_type: 주문 타입
            trade_type: 거래 타입 (BUY/SELL)
            timestamp: 거래 시각
            signal_id: 전략 신호 ID

        Returns:
            Trade: 거래 객체 (실패 시 None)
        """
        is_buy = trade_type == TradeType.BUY

        # 거래 비용 계산
        costs = self.trade_costs.calculate(price, quantity, is_buy)

        # 매수 가능 여부 확인
        if is_buy:
            if self.portfolio.cash < costs["total_cost"]:
                logger.warning(
                    f"자금 부족: 필요={costs['total_cost']:.2f}, "
                    f"보유={self.portfolio.cash:.2f}"
                )
                return None
            self.portfolio.cash -= costs["total_cost"]
        else:
            # 매도 가능 수량 확인
            current_position = self.portfolio.positions.get(symbol, 0.0)
            if current_position < quantity:
                logger.warning(f"포지션 부족: 필요={quantity}, 보유={current_position}")
                return None
            revenue = costs["execution_price"] * quantity - costs["commission"]
            self.portfolio.cash += revenue

        # 포지션 업데이트
        self.portfolio.update_position(
            symbol=symbol,
            quantity=quantity,
            price=costs["execution_price"],
            is_buy=is_buy,
        )

        # 거래 기록 생성
        trade = Trade(
            trade_id=str(uuid.uuid4()),
            symbol=symbol,
            trade_type=trade_type,
            quantity=quantity,
            price=costs["execution_price"],
            timestamp=timestamp,
            commission=costs["commission"],
            strategy_signal_id=signal_id,
            notes=f"Order: {order_type.value}, Slippage: {costs['slippage']:.4f}",
        )

        logger.debug(
            f"거래 실행: {trade_type.value} {symbol} "
            f"{quantity}주 @ {costs['execution_price']:.2f}"
        )

        return trade

    def execute_signal(
        self,
        symbol: str,
        action: str,
        quantity: float,
        price: float,
        timestamp: datetime,
    ) -> Optional[Trade]:
        """전략 신호 기반 주문 실행

        Args:
            symbol: 종목 심볼
            action: 거래 동작 ('BUY'/'SELL')
            quantity: 수량
            price: 가격
            timestamp: 거래 시각

        Returns:
            Trade: 거래 객체
        """
        trade_type = TradeType.BUY if action.upper() == "BUY" else TradeType.SELL

        return self.execute_order(
            symbol=symbol,
            quantity=quantity,
            price=price,
            order_type=OrderType.MARKET,
            trade_type=trade_type,
            timestamp=timestamp,
        )
