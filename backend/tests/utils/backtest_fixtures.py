"""
백테스트 테스트용 픽스처 및 헬퍼 함수

P3.1 Step 5: 테스트 유틸리티
재사용 가능한 Mock 데이터 생성, Assertion 헬퍼, 공통 픽스처
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any
import pandas as pd
import numpy as np

from app.models.trading.backtest import Backtest, BacktestConfig, BacktestStatus
from app.models.trading.strategy import Strategy, StrategyType


def create_mock_backtest(
    name: str = "Test Backtest",
    symbols: List[str] | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    initial_cash: float = 100000.0,
    **kwargs: Any,
) -> Backtest:
    """Mock Backtest 객체 생성

    Args:
        name: 백테스트 이름
        symbols: 심볼 리스트 (기본값: ["AAPL"])
        start_date: 시작일 (기본값: 90일 전)
        end_date: 종료일 (기본값: 오늘)
        initial_cash: 초기 자본 (기본값: 100,000)
        **kwargs: 추가 설정 파라미터

    Returns:
        Mock Backtest 객체
    """
    if symbols is None:
        symbols = ["AAPL"]
    if start_date is None:
        start_date = datetime.now() - timedelta(days=90)
    if end_date is None:
        end_date = datetime.now()

    config = BacktestConfig(
        name=f"{name} Config",
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        initial_cash=initial_cash,
        commission_rate=kwargs.get("commission_rate", 0.001),
        rebalance_frequency=kwargs.get("rebalance_frequency"),
    )

    backtest = Backtest(
        name=name,
        description=kwargs.get("description", f"{name} description"),
        config=config,
        status=kwargs.get("status", BacktestStatus.PENDING),
        user_id=kwargs.get("user_id", "test-user-123"),
        created_by=kwargs.get("created_by", "test-user-123"),
        start_time=kwargs.get("start_time", start_date),
        end_time=kwargs.get("end_time", end_date),
        duration_seconds=kwargs.get("duration_seconds", 0.0),
        performance=kwargs.get("performance", {}),
        portfolio_history_path=kwargs.get("portfolio_history_path", ""),
        trades_history_path=kwargs.get("trades_history_path", ""),
        error_message=kwargs.get("error_message", None),
    )

    return backtest


def create_mock_market_data(
    symbols: List[str],
    start_date: datetime,
    end_date: datetime,
    price_range: tuple[float, float] = (100, 200),
    volume_range: tuple[int, int] = (1000000, 10000000),
    trend: str = "random",  # "random", "upward", "downward", "sideways"
) -> Dict[str, pd.DataFrame]:
    """Mock 시장 데이터 생성 (OHLCV)

    Args:
        symbols: 심볼 리스트
        start_date: 시작일
        end_date: 종료일
        price_range: 가격 범위 (min, max)
        volume_range: 거래량 범위 (min, max)
        trend: 가격 추세 ("random", "upward", "downward", "sideways")

    Returns:
        {symbol: DataFrame} 딕셔너리
    """
    market_data = {}
    date_range = pd.date_range(start=start_date, end=end_date, freq="D")

    for symbol in symbols:
        n_days = len(date_range)

        # 추세에 따른 가격 생성
        if trend == "upward":
            base_prices = np.linspace(price_range[0], price_range[1], n_days)
            noise = np.random.normal(0, 5, n_days)
            close_prices = base_prices + noise
        elif trend == "downward":
            base_prices = np.linspace(price_range[1], price_range[0], n_days)
            noise = np.random.normal(0, 5, n_days)
            close_prices = base_prices + noise
        elif trend == "sideways":
            mean_price = (price_range[0] + price_range[1]) / 2
            close_prices = np.random.normal(mean_price, 10, n_days)
        else:  # random
            close_prices = np.random.uniform(price_range[0], price_range[1], n_days)

        # OHLC 생성
        df = pd.DataFrame(
            {
                "open": close_prices + np.random.uniform(-2, 2, n_days),
                "high": close_prices + np.random.uniform(1, 5, n_days),
                "low": close_prices - np.random.uniform(1, 5, n_days),
                "close": close_prices,
                "volume": np.random.randint(volume_range[0], volume_range[1], n_days),
            },
            index=date_range,
        )

        # 가격이 음수가 되지 않도록 조정
        df = df.clip(lower=1.0)

        market_data[symbol] = df

    return market_data


def create_mock_strategy(
    name: str = "Test Strategy",
    strategy_type: str = "momentum",
    parameters: Dict[str, Any] | None = None,
) -> Strategy:
    """Mock Strategy 객체 생성

    Args:
        name: 전략 이름
        strategy_type: 전략 타입
        parameters: 전략 파라미터

    Returns:
        Mock Strategy 객체
    """
    if parameters is None:
        parameters = {
            "lookback_period": 20,
            "entry_threshold": 0.02,
            "exit_threshold": -0.01,
        }

    # StrategyConfigUnion is a typing.Union and cannot be called directly;
    # provide a plain dict so Pydantic can validate/construct the appropriate union member.
    config = {
        "name": f"{name} Config",
        "parameters": parameters,
    }

    # Ensure we pass the Enum value expected by the model
    strategy = Strategy(
        name=name,
        description=f"{name} description",
        strategy_type=StrategyType(strategy_type),
        config=config,  # type: ignore TODO: 정상화 필요
        created_by="test-user-123",
    )

    return strategy


def assert_backtest_result(
    result: Dict[str, Any],
    expected_status: BacktestStatus = BacktestStatus.COMPLETED,
    min_total_return: float | None = None,
    max_total_return: float | None = None,
    min_sharpe_ratio: float | None = None,
) -> None:
    """백테스트 결과 검증

    Args:
        result: 백테스트 실행 결과
        expected_status: 예상 상태
        min_total_return: 최소 총 수익률 (%)
        max_total_return: 최대 총 수익률 (%)
        min_sharpe_ratio: 최소 샤프 비율

    Raises:
        AssertionError: 검증 실패 시
    """
    assert result is not None, "Result should not be None"
    assert (
        result.get("status") == expected_status.value
    ), f"Expected status {expected_status.value}, got {result.get('status')}"

    if "metrics" in result:
        metrics = result["metrics"]

        if min_total_return is not None:
            actual_return = metrics.get("total_return_pct", 0)
            assert (
                actual_return >= min_total_return
            ), f"Total return {actual_return}% is less than minimum {min_total_return}%"

        if max_total_return is not None:
            actual_return = metrics.get("total_return_pct", 0)
            assert (
                actual_return <= max_total_return
            ), f"Total return {actual_return}% exceeds maximum {max_total_return}%"

        if min_sharpe_ratio is not None:
            actual_sharpe = metrics.get("sharpe_ratio", 0)
            assert (
                actual_sharpe >= min_sharpe_ratio
            ), f"Sharpe ratio {actual_sharpe} is less than minimum {min_sharpe_ratio}"


def assert_performance_metrics(
    metrics: Dict[str, Any],
    check_fields: List[str] | None = None,
    non_negative_fields: List[str] | None = None,
) -> None:
    """성능 지표 검증

    Args:
        metrics: 성능 지표 딕셔너리
        check_fields: 필수 필드 리스트
        non_negative_fields: 음수가 되면 안 되는 필드 리스트

    Raises:
        AssertionError: 검증 실패 시
    """
    if check_fields is None:
        check_fields = [
            "total_return",
            "total_return_pct",
            "max_drawdown",
            "sharpe_ratio",
            "total_trades",
        ]

    if non_negative_fields is None:
        non_negative_fields = ["total_trades", "win_trades", "loss_trades"]

    # 필수 필드 존재 확인
    for field in check_fields:
        assert field in metrics, f"Missing required field: {field}"

    # 음수 검증
    for field in non_negative_fields:
        if field in metrics:
            assert (
                metrics[field] >= 0
            ), f"Field {field} should be non-negative, got {metrics[field]}"

    # 승률 범위 검증 (0-100%)
    if "win_rate" in metrics:
        win_rate = metrics["win_rate"]
        assert 0 <= win_rate <= 100, f"Win rate should be 0-100%, got {win_rate}"

    # 최대 낙폭은 음수 또는 0
    if "max_drawdown" in metrics:
        max_dd = metrics["max_drawdown"]
        assert max_dd <= 0, f"Max drawdown should be non-positive, got {max_dd}"


# from datetime import datetime, timedelta
# from typing import Dict, List, Any
# from decimal import Decimal
# import pandas as pd
# import numpy as np

# from app.models.trading.backtest import Backtest, BacktestConfig, BacktestStatus
# from app.models.strategy import Strategy


# def create_mock_backtest(
#     name: str = "Test Backtest",
#     symbols: List[str] = None,
#     start_date: datetime = None,
#     end_date: datetime = None,
#     initial_cash: float = 100000.0,
#     **kwargs,
# ) -> Backtest:
#     """Mock Backtest 객체 생성

#     Args:
#         name: 백테스트 이름
#         symbols: 심볼 리스트 (기본값: ["AAPL"])
#         start_date: 시작일 (기본값: 90일 전)
#         end_date: 종료일 (기본값: 오늘)
#         initial_cash: 초기 자본 (기본값: 100,000)
#         **kwargs: 추가 설정 파라미터

#     Returns:
#         Mock Backtest 객체
#     """
#     if symbols is None:
#         symbols = ["AAPL"]
#     if start_date is None:
#         start_date = datetime.now() - timedelta(days=90)
#     if end_date is None:
#         end_date = datetime.now()

#     config = BacktestConfig(
#         name=f"{name} Config",
#         symbols=symbols,
#         start_date=start_date,
#         end_date=end_date,
#         initial_cash=initial_cash,
#         commission_rate=kwargs.get("commission_rate", 0.001),
#         rebalance_frequency=kwargs.get("rebalance_frequency"),
#     )

#     backtest = Backtest(
#         name=name,
#         description=kwargs.get("description", f"{name} description"),
#         config=config,
#         status=kwargs.get("status", BacktestStatus.PENDING),
#         user_id=kwargs.get("user_id", "test-user-123"),
#     )

#     return backtest


# def create_mock_market_data(
#     symbols: List[str],
#     start_date: datetime,
#     end_date: datetime,
#     price_range: tuple = (100, 200),
#     volume_range: tuple = (1000000, 10000000),
#     trend: str = "random",  # "random", "upward", "downward", "sideways"
# ) -> Dict[str, pd.DataFrame]:
#     """Mock 시장 데이터 생성 (OHLCV)

#     Args:
#         symbols: 심볼 리스트
#         start_date: 시작일
#         end_date: 종료일
#         price_range: 가격 범위 (min, max)
#         volume_range: 거래량 범위 (min, max)
#         trend: 가격 추세 ("random", "upward", "downward", "sideways")

#     Returns:
#         {symbol: DataFrame} 딕셔너리
#     """
#     market_data = {}
#     date_range = pd.date_range(start=start_date, end=end_date, freq="D")

#     for symbol in symbols:
#         n_days = len(date_range)

#         # 추세에 따른 가격 생성
#         if trend == "upward":
#             base_prices = np.linspace(price_range[0], price_range[1], n_days)
#             noise = np.random.normal(0, 5, n_days)
#             close_prices = base_prices + noise
#         elif trend == "downward":
#             base_prices = np.linspace(price_range[1], price_range[0], n_days)
#             noise = np.random.normal(0, 5, n_days)
#             close_prices = base_prices + noise
#         elif trend == "sideways":
#             mean_price = (price_range[0] + price_range[1]) / 2
#             close_prices = np.random.normal(mean_price, 10, n_days)
#         else:  # random
#             close_prices = np.random.uniform(price_range[0], price_range[1], n_days)

#         # OHLC 생성
#         df = pd.DataFrame(
#             {
#                 "open": close_prices + np.random.uniform(-2, 2, n_days),
#                 "high": close_prices + np.random.uniform(1, 5, n_days),
#                 "low": close_prices - np.random.uniform(1, 5, n_days),
#                 "close": close_prices,
#                 "volume": np.random.randint(volume_range[0], volume_range[1], n_days),
#             },
#             index=date_range,
#         )

#         # 가격이 음수가 되지 않도록 조정
#         df = df.clip(lower=1.0)

#         market_data[symbol] = df

#     return market_data


# def create_mock_strategy(
#     name: str = "Test Strategy",
#     strategy_type: str = "momentum",
#     parameters: Dict[str, Any] = None,
# ) -> Strategy:
#     """Mock Strategy 객체 생성

#     Args:
#         name: 전략 이름
#         strategy_type: 전략 타입
#         parameters: 전략 파라미터

#     Returns:
#         Mock Strategy 객체
#     """
#     if parameters is None:
#         parameters = {
#             "lookback_period": 20,
#             "entry_threshold": 0.02,
#             "exit_threshold": -0.01,
#         }

#     strategy = Strategy(
#         name=name,
#         description=f"{name} description",
#         strategy_type=strategy_type,
#         parameters=[
#             StrategyParameter(
#                 name=key,
#                 value=str(value),
#                 parameter_type=type(value).__name__,
#             )
#             for key, value in parameters.items()
#         ],
#     )

#     return strategy


# def create_test_portfolio_state(
#     cash: float = 100000.0,
#     positions: Dict[str, Dict[str, float]] = None,
#     trades: List[Dict[str, Any]] = None,
# ) -> PortfolioState:
#     """테스트용 PortfolioState 생성

#     Args:
#         cash: 현금 잔액
#         positions: {"symbol": {"quantity": 100, "avg_price": 150.0}}
#         trades: [{"symbol": "AAPL", "side": "buy", ...}]

#     Returns:
#         PortfolioState 객체
#     """
#     if positions is None:
#         positions = {}
#     if trades is None:
#         trades = []

#     position_objects = [
#         Position(
#             symbol=symbol,
#             quantity=Decimal(str(data["quantity"])),
#             average_price=Decimal(str(data["avg_price"])),
#             current_price=Decimal(str(data.get("current_price", data["avg_price"]))),
#         )
#         for symbol, data in positions.items()
#     ]

#     trade_objects = [
#         Trade(
#             timestamp=trade.get("timestamp", datetime.now()),
#             symbol=trade["symbol"],
#             side=trade["side"],
#             quantity=Decimal(str(trade["quantity"])),
#             price=Decimal(str(trade["price"])),
#             commission=Decimal(str(trade.get("commission", 0))),
#         )
#         for trade in trades
#     ]

#     portfolio_state = PortfolioState(
#         timestamp=datetime.now(),
#         cash=Decimal(str(cash)),
#         positions=position_objects,
#         trades=trade_objects,
#     )

#     return portfolio_state


# def assert_backtest_result(
#     result: Dict[str, Any],
#     expected_status: BacktestStatus = BacktestStatus.COMPLETED,
#     min_total_return: float = None,
#     max_total_return: float = None,
#     min_sharpe_ratio: float = None,
# ):
#     """백테스트 결과 검증

#     Args:
#         result: 백테스트 실행 결과
#         expected_status: 예상 상태
#         min_total_return: 최소 총 수익률 (%)
#         max_total_return: 최대 총 수익률 (%)
#         min_sharpe_ratio: 최소 샤프 비율

#     Raises:
#         AssertionError: 검증 실패 시
#     """
#     assert result is not None, "Result should not be None"
#     assert (
#         result.get("status") == expected_status.value
#     ), f"Expected status {expected_status.value}, got {result.get('status')}"

#     if "metrics" in result:
#         metrics = result["metrics"]

#         if min_total_return is not None:
#             actual_return = metrics.get("total_return_pct", 0)
#             assert (
#                 actual_return >= min_total_return
#             ), f"Total return {actual_return}% is less than minimum {min_total_return}%"

#         if max_total_return is not None:
#             actual_return = metrics.get("total_return_pct", 0)
#             assert (
#                 actual_return <= max_total_return
#             ), f"Total return {actual_return}% exceeds maximum {max_total_return}%"

#         if min_sharpe_ratio is not None:
#             actual_sharpe = metrics.get("sharpe_ratio", 0)
#             assert (
#                 actual_sharpe >= min_sharpe_ratio
#             ), f"Sharpe ratio {actual_sharpe} is less than minimum {min_sharpe_ratio}"


# def assert_performance_metrics(
#     metrics: Dict[str, Any],
#     check_fields: List[str] = None,
#     non_negative_fields: List[str] = None,
# ):
#     """성능 지표 검증

#     Args:
#         metrics: 성능 지표 딕셔너리
#         check_fields: 필수 필드 리스트
#         non_negative_fields: 음수가 되면 안 되는 필드 리스트

#     Raises:
#         AssertionError: 검증 실패 시
#     """
#     if check_fields is None:
#         check_fields = [
#             "total_return",
#             "total_return_pct",
#             "max_drawdown",
#             "sharpe_ratio",
#             "total_trades",
#         ]

#     if non_negative_fields is None:
#         non_negative_fields = ["total_trades", "win_trades", "loss_trades"]

#     # 필수 필드 존재 확인
#     for field in check_fields:
#         assert field in metrics, f"Missing required field: {field}"

#     # 음수 검증
#     for field in non_negative_fields:
#         if field in metrics:
#             assert (
#                 metrics[field] >= 0
#             ), f"Field {field} should be non-negative, got {metrics[field]}"

#     # 승률 범위 검증 (0-100%)
#     if "win_rate" in metrics:
#         win_rate = metrics["win_rate"]
#         assert 0 <= win_rate <= 100, f"Win rate should be 0-100%, got {win_rate}"

#     # 최대 낙폭은 음수 또는 0
#     if "max_drawdown" in metrics:
#         max_dd = metrics["max_drawdown"]
#         assert max_dd <= 0, f"Max drawdown should be non-positive, got {max_dd}"
