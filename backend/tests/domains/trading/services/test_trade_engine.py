"""
TradeEngine 테스트
"""

from datetime import datetime
from app.services.backtest.trade_engine import TradeEngine, Portfolio, TradeCosts
from app.models.backtest import BacktestConfig, TradeType, OrderType


def test_portfolio_initialization():
    """포트폴리오 초기화 테스트"""
    # Given
    initial_cash = 100000.0

    # When
    portfolio = Portfolio(initial_cash=initial_cash)

    # Then
    assert portfolio.cash == initial_cash
    assert portfolio.initial_cash == initial_cash
    assert portfolio.total_value == initial_cash
    assert len(portfolio.positions) == 0


def test_buy_order_execution():
    """매수 주문 실행 테스트"""
    # Given
    config = BacktestConfig(
        name="test",
        symbols=["AAPL"],
        start_date=datetime.now(),
        end_date=datetime.now(),
        initial_cash=100000.0,
        commission_rate=0.001,
        slippage_rate=0.0005,
        rebalance_frequency=None,
    )
    trade_engine = TradeEngine(config)
    initial_cash = trade_engine.portfolio.cash

    # When
    trade = trade_engine.execute_order(
        symbol="AAPL",
        quantity=10,
        price=150.0,
        order_type=OrderType.MARKET,
        trade_type=TradeType.BUY,
        timestamp=datetime.now(),
    )

    # Then
    assert trade is not None
    assert trade.symbol == "AAPL"
    assert trade.quantity == 10
    assert trade_engine.portfolio.cash < initial_cash
    assert trade_engine.portfolio.positions["AAPL"] == 10


def test_insufficient_cash():
    """자금 부족 시 거래 실패 테스트"""
    # Given
    config = BacktestConfig(
        name="test",
        symbols=["AAPL"],
        start_date=datetime.now(),
        end_date=datetime.now(),
        initial_cash=1000.0,  # 적은 자금
        commission_rate=0.001,
        slippage_rate=0.0005,
        rebalance_frequency=None,
    )
    trade_engine = TradeEngine(config)

    # When
    trade = trade_engine.execute_order(
        symbol="AAPL",
        quantity=100,  # 큰 수량
        price=150.0,
        order_type=OrderType.MARKET,
        trade_type=TradeType.BUY,
        timestamp=datetime.now(),
    )

    # Then
    assert trade is None  # 거래 실패
    assert trade_engine.portfolio.cash == 1000.0  # 잔액 변동 없음


def test_sell_order_execution():
    """매도 주문 실행 테스트"""
    # Given
    config = BacktestConfig(
        name="test",
        symbols=["AAPL"],
        start_date=datetime.now(),
        end_date=datetime.now(),
        initial_cash=100000.0,
        commission_rate=0.001,
        slippage_rate=0.0005,
        rebalance_frequency=None,
    )
    trade_engine = TradeEngine(config)

    # 먼저 매수
    trade_engine.execute_order(
        symbol="AAPL",
        quantity=10,
        price=150.0,
        order_type=OrderType.MARKET,
        trade_type=TradeType.BUY,
        timestamp=datetime.now(),
    )

    initial_cash = trade_engine.portfolio.cash

    # When
    trade = trade_engine.execute_order(
        symbol="AAPL",
        quantity=5,
        price=160.0,
        order_type=OrderType.MARKET,
        trade_type=TradeType.SELL,
        timestamp=datetime.now(),
    )

    # Then
    assert trade is not None
    assert trade_engine.portfolio.cash > initial_cash  # 현금 증가
    assert trade_engine.portfolio.positions["AAPL"] == 5  # 포지션 감소


def test_trade_costs_calculation():
    """거래 비용 계산 테스트"""
    # Given
    costs = TradeCosts(commission_rate=0.001, slippage_rate=0.0005)

    # When
    result = costs.calculate(price=100.0, quantity=10, is_buy=True)

    # Then
    assert result["commission"] > 0
    assert result["slippage"] > 0
    assert result["execution_price"] > 100.0  # 매수는 슬리피지로 가격 상승
    assert result["total_cost"] > 1000.0


def test_execute_signal():
    """전략 신호 실행 테스트"""
    # Given
    config = BacktestConfig(
        name="test",
        symbols=["AAPL"],
        start_date=datetime.now(),
        end_date=datetime.now(),
        initial_cash=100000.0,
        commission_rate=0.001,
        slippage_rate=0.0005,
        rebalance_frequency=None,
    )
    trade_engine = TradeEngine(config)

    # When
    trade = trade_engine.execute_signal(
        symbol="AAPL",
        action="BUY",
        quantity=10,
        price=150.0,
        timestamp=datetime.now(),
    )

    # Then
    assert trade is not None
    assert trade.trade_type == TradeType.BUY
