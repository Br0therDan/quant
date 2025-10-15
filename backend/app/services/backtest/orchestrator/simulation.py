"""
Backtest Orchestrator - Simulation Module
백테스트 시뮬레이션 실행
"""

import logging
from datetime import datetime
from typing import Any

from app.models.trading.backtest import Backtest
from app.services.backtest.trade_engine import TradeEngine


logger = logging.getLogger(__name__)


class SimulationRunner:
    """백테스트 시뮬레이션 실행

    책임:
    - TradeEngine을 사용하여 신호를 거래로 변환
    - 포트폴리오 가치 추적
    """

    def simulate(
        self, backtest: Backtest, signals: list[dict[str, Any]]
    ) -> tuple[list, list[float]]:
        """TradeEngine으로 신호 실행 → 거래 + 포트폴리오 값 반환

        Args:
            backtest: 백테스트 모델
            signals: 트레이딩 신호 리스트

        Returns:
            (거래 리스트, 포트폴리오 가치 리스트) 튜플
        """
        trade_engine = TradeEngine(backtest.config)
        trades = []
        portfolio_values = [backtest.config.initial_cash]

        for signal in signals:
            symbol = signal.get("symbol")
            action = signal.get("action")
            quantity = signal.get("quantity", 0)
            price = signal.get("price", 0)
            timestamp = signal.get("timestamp", datetime.now())

            if not symbol or not action or quantity <= 0 or price <= 0:
                continue

            trade = trade_engine.execute_signal(
                symbol=symbol,
                action=action,
                quantity=quantity,
                price=price,
                timestamp=timestamp,
            )

            if trade:
                trades.append(trade)

            portfolio_values.append(trade_engine.portfolio.total_value)

        return trades, portfolio_values
