"""성과 지표 계산기

백테스트, 포트폴리오 등에서 사용하는 공통 성과 계산 로직을 제공합니다.
중복 코드 제거를 위해 Phase 2.2에서 도입되었습니다.
"""

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class PerformanceCalculator:
    """성과 지표 계산기

    샤프 비율, 소르티노 비율, 최대 낙폭 등 다양한 성과 지표를 계산합니다.
    """

    @staticmethod
    def sharpe_ratio(
        returns: pd.Series | np.ndarray | list[float],
        risk_free_rate: float = 0.02,
        periods_per_year: int = 252,
    ) -> float:
        """샤프 비율 계산

        Args:
            returns: 일별 수익률 (또는 기간별 수익률)
            risk_free_rate: 무위험 수익률 (연율, 기본값 2%)
            periods_per_year: 연간 기간 수 (기본값 252 거래일)

        Returns:
            샤프 비율

        Example:
            >>> returns = pd.Series([0.01, -0.005, 0.02, 0.015])
            >>> sharpe = PerformanceCalculator.sharpe_ratio(returns)
            >>> print(f"Sharpe Ratio: {sharpe:.2f}")
            Sharpe Ratio: 1.85
        """
        # 입력 타입 통일 (numpy array로 변환)
        if isinstance(returns, list):
            returns_array: np.ndarray = np.array(returns, dtype=np.float64)
        elif isinstance(returns, pd.Series):
            returns_array = np.array(returns.values, dtype=np.float64)
        else:
            returns_array = np.asarray(returns, dtype=np.float64)

        if len(returns_array) == 0:
            return 0.0

        # 초과 수익률 계산 (일별 무위험 수익률 차감)
        daily_rf = risk_free_rate / periods_per_year
        excess_returns = returns_array - daily_rf

        # 표준편차가 0이면 샤프 비율을 계산할 수 없음
        std = float(np.std(excess_returns, ddof=1))
        if std == 0 or np.isnan(std):
            return 0.0

        # 연율화된 샤프 비율
        mean_excess = float(np.mean(excess_returns))
        sharpe = mean_excess / std * np.sqrt(periods_per_year)

        return float(sharpe)

    @staticmethod
    def sortino_ratio(
        returns: pd.Series | np.ndarray | list[float],
        target_return: float = 0.0,
        periods_per_year: int = 252,
    ) -> float:
        """소르티노 비율 계산

        샤프 비율과 유사하지만 하방 변동성만 고려합니다.

        Args:
            returns: 일별 수익률
            target_return: 목표 수익률 (연율, 기본값 0%)
            periods_per_year: 연간 기간 수

        Returns:
            소르티노 비율
        """
        if isinstance(returns, list):
            returns_array: np.ndarray = np.array(returns, dtype=np.float64)
        elif isinstance(returns, pd.Series):
            returns_array = np.array(returns.values, dtype=np.float64)
        else:
            returns_array = np.asarray(returns, dtype=np.float64)

        if len(returns_array) == 0:
            return 0.0

        # 목표 수익률 대비 초과 수익률
        daily_target = target_return / periods_per_year
        excess_returns = returns_array - daily_target

        # 하방 편차 (downside deviation)
        downside_returns = excess_returns[excess_returns < 0]
        if len(downside_returns) == 0:
            return 0.0

        downside_std = float(np.std(downside_returns, ddof=1))
        if downside_std == 0 or np.isnan(downside_std):
            return 0.0

        # 연율화된 소르티노 비율
        mean_excess = float(np.mean(excess_returns))
        sortino = mean_excess / downside_std * np.sqrt(periods_per_year)

        return float(sortino)

    @staticmethod
    def max_drawdown(
        equity_curve: pd.Series | np.ndarray | list[float],
    ) -> float:
        """최대 낙폭 계산

        Args:
            equity_curve: 포트폴리오 가치 시계열

        Returns:
            최대 낙폭 (백분율, 음수)

        Example:
            >>> equity = [100, 110, 105, 95, 105]
            >>> mdd = PerformanceCalculator.max_drawdown(equity)
            >>> print(f"Max Drawdown: {mdd:.2%}")
            Max Drawdown: -13.64%
        """
        if isinstance(equity_curve, list):
            values: np.ndarray = np.array(equity_curve, dtype=np.float64)
        elif isinstance(equity_curve, pd.Series):
            values = np.array(equity_curve.values, dtype=np.float64)
        else:
            values = np.asarray(equity_curve, dtype=np.float64)

        if len(values) == 0:
            return 0.0

        # 누적 최대값
        cummax = np.maximum.accumulate(values)

        # 낙폭 계산
        drawdowns = (values - cummax) / cummax

        # 최대 낙폭 (음수)
        max_dd = float(np.min(drawdowns))

        return max_dd

    @staticmethod
    def calmar_ratio(
        returns: pd.Series | np.ndarray | list[float],
        equity_curve: pd.Series | np.ndarray | list[float],
        periods_per_year: int = 252,
    ) -> float:
        """칼마 비율 계산

        연율화 수익률 / 최대 낙폭 비율입니다.

        Args:
            returns: 일별 수익률
            equity_curve: 포트폴리오 가치 시계열
            periods_per_year: 연간 기간 수

        Returns:
            칼마 비율
        """
        if isinstance(returns, list):
            returns_array: np.ndarray = np.array(returns, dtype=np.float64)
        elif isinstance(returns, pd.Series):
            returns_array = np.array(returns.values, dtype=np.float64)
        else:
            returns_array = np.asarray(returns, dtype=np.float64)

        if len(returns_array) == 0:
            return 0.0

        # 연율화 수익률
        annualized_return = float(np.mean(returns_array)) * periods_per_year

        # 최대 낙폭
        max_dd = PerformanceCalculator.max_drawdown(equity_curve)

        if max_dd == 0 or max_dd >= 0:
            return 0.0

        # 칼마 비율 (양수)
        calmar = annualized_return / abs(max_dd)

        return float(calmar)

    @staticmethod
    def annualized_return(
        total_return: float,
        periods: int,
        periods_per_year: int = 252,
    ) -> float:
        """연율화 수익률 계산

        Args:
            total_return: 총 수익률 (예: 0.5 = 50%)
            periods: 총 기간 수 (거래일 수)
            periods_per_year: 연간 기간 수

        Returns:
            연율화 수익률

        Example:
            >>> total_return = 0.5  # 50%
            >>> periods = 252  # 1년
            >>> annualized = PerformanceCalculator.annualized_return(total_return, periods)
            >>> print(f"Annualized Return: {annualized:.2%}")
            Annualized Return: 50.00%
        """
        if periods <= 0:
            return 0.0

        years = periods / periods_per_year

        if years <= 0:
            return 0.0

        # 복리 계산
        annualized = (1 + total_return) ** (1 / years) - 1

        return float(annualized)

    @staticmethod
    def annualized_volatility(
        returns: pd.Series | np.ndarray | list[float],
        periods_per_year: int = 252,
    ) -> float:
        """연율화 변동성 계산

        Args:
            returns: 일별 수익률
            periods_per_year: 연간 기간 수

        Returns:
            연율화 변동성 (표준편차)
        """
        if isinstance(returns, list):
            returns_array: np.ndarray = np.array(returns, dtype=np.float64)
        elif isinstance(returns, pd.Series):
            returns_array = np.array(returns.values, dtype=np.float64)
        else:
            returns_array = np.asarray(returns, dtype=np.float64)

        if len(returns_array) == 0:
            return 0.0

        # 일별 변동성
        daily_vol = float(np.std(returns_array, ddof=1))

        # 연율화
        annualized_vol = daily_vol * np.sqrt(periods_per_year)

        return float(annualized_vol)

    @staticmethod
    def information_ratio(
        returns: pd.Series | np.ndarray | list[float],
        benchmark_returns: pd.Series | np.ndarray | list[float],
        periods_per_year: int = 252,
    ) -> float:
        """정보 비율 계산

        벤치마크 대비 초과 수익의 일관성을 측정합니다.

        Args:
            returns: 포트폴리오 일별 수익률
            benchmark_returns: 벤치마크 일별 수익률
            periods_per_year: 연간 기간 수

        Returns:
            정보 비율
        """
        if isinstance(returns, list):
            returns_array: np.ndarray = np.array(returns, dtype=np.float64)
        elif isinstance(returns, pd.Series):
            returns_array = np.array(returns.values, dtype=np.float64)
        else:
            returns_array = np.asarray(returns, dtype=np.float64)

        if isinstance(benchmark_returns, list):
            benchmark_array: np.ndarray = np.array(benchmark_returns, dtype=np.float64)
        elif isinstance(benchmark_returns, pd.Series):
            benchmark_array = np.array(benchmark_returns.values, dtype=np.float64)
        else:
            benchmark_array = np.asarray(benchmark_returns, dtype=np.float64)

        if len(returns_array) == 0 or len(benchmark_array) == 0:
            return 0.0

        # 초과 수익률
        excess_returns = returns_array - benchmark_array

        # 추적 오차 (tracking error)
        tracking_error = float(np.std(excess_returns, ddof=1))

        if tracking_error == 0 or np.isnan(tracking_error):
            return 0.0

        # 연율화된 정보 비율
        mean_excess = float(np.mean(excess_returns))
        info_ratio = mean_excess / tracking_error * np.sqrt(periods_per_year)

        return float(info_ratio)
