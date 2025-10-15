"""리스크 지표 계산기

VaR, CVaR, Beta, Correlation 등 리스크 관련 지표를 계산합니다.
"""

import logging

import numpy as np
import pandas as pd
from scipy import stats

logger = logging.getLogger(__name__)


class RiskCalculator:
    """리스크 지표 계산기

    VaR, CVaR, Beta, 상관계수 등 리스크 측정 지표를 제공합니다.
    """

    @staticmethod
    def value_at_risk(
        returns: pd.Series | np.ndarray | list[float],
        confidence_level: float = 0.95,
    ) -> float:
        """VaR (Value at Risk) 계산

        Args:
            returns: 일별 수익률
            confidence_level: 신뢰 수준 (기본값 95%)

        Returns:
            VaR 값 (백분율, 음수)

        Example:
            >>> returns = pd.Series([-0.02, 0.01, -0.01, 0.03])
            >>> var = RiskCalculator.value_at_risk(returns, 0.95)
            >>> print(f"VaR (95%): {var:.2%}")
            VaR (95%): -1.52%
        """
        if isinstance(returns, list):
            returns_array: np.ndarray = np.array(returns, dtype=np.float64)
        elif isinstance(returns, pd.Series):
            returns_array = np.array(returns.values, dtype=np.float64)
        else:
            returns_array = np.asarray(returns, dtype=np.float64)

        if len(returns_array) == 0:
            return 0.0

        # 퍼센타일 계산 (역수로 VaR)
        var = float(np.percentile(returns_array, (1 - confidence_level) * 100))

        return var

    @staticmethod
    def conditional_var(
        returns: pd.Series | np.ndarray | list[float],
        confidence_level: float = 0.95,
    ) -> float:
        """CVaR (Conditional Value at Risk) 계산

        VaR를 초과하는 손실의 평균값입니다.

        Args:
            returns: 일별 수익률
            confidence_level: 신뢰 수준

        Returns:
            CVaR 값 (백분율, 음수)
        """
        if isinstance(returns, list):
            returns_array: np.ndarray = np.array(returns, dtype=np.float64)
        elif isinstance(returns, pd.Series):
            returns_array = np.array(returns.values, dtype=np.float64)
        else:
            returns_array = np.asarray(returns, dtype=np.float64)

        if len(returns_array) == 0:
            return 0.0

        # VaR 계산
        var = RiskCalculator.value_at_risk(returns_array, confidence_level)

        # VaR를 초과하는 손실의 평균
        tail_losses = returns_array[returns_array <= var]

        if len(tail_losses) == 0:
            return var

        cvar = float(np.mean(tail_losses))

        return cvar

    @staticmethod
    def beta(
        returns: pd.Series | np.ndarray | list[float],
        market_returns: pd.Series | np.ndarray | list[float],
    ) -> float:
        """베타 계산

        시장 대비 민감도를 측정합니다.

        Args:
            returns: 포트폴리오 수익률
            market_returns: 시장 수익률

        Returns:
            베타 값 (1.0 = 시장과 동일한 변동성)
        """
        if isinstance(returns, list):
            returns_array: np.ndarray = np.array(returns, dtype=np.float64)
        elif isinstance(returns, pd.Series):
            returns_array = np.array(returns.values, dtype=np.float64)
        else:
            returns_array = np.asarray(returns, dtype=np.float64)

        if isinstance(market_returns, list):
            market_array: np.ndarray = np.array(market_returns, dtype=np.float64)
        elif isinstance(market_returns, pd.Series):
            market_array = np.array(market_returns.values, dtype=np.float64)
        else:
            market_array = np.asarray(market_returns, dtype=np.float64)

        if len(returns_array) == 0 or len(market_array) == 0:
            return 1.0  # 기본값

        # 공분산 / 시장 분산
        covariance = float(np.cov(returns_array, market_array)[0, 1])
        market_variance = float(np.var(market_array, ddof=1))

        if market_variance == 0:
            return 1.0

        beta_value = covariance / market_variance

        return float(beta_value)

    @staticmethod
    def correlation(
        returns_a: pd.Series | np.ndarray | list[float],
        returns_b: pd.Series | np.ndarray | list[float],
    ) -> float:
        """상관계수 계산

        Args:
            returns_a: 첫 번째 수익률 시계열
            returns_b: 두 번째 수익률 시계열

        Returns:
            상관계수 (-1.0 ~ 1.0)
        """
        if isinstance(returns_a, list):
            array_a: np.ndarray = np.array(returns_a, dtype=np.float64)
        elif isinstance(returns_a, pd.Series):
            array_a = np.array(returns_a.values, dtype=np.float64)
        else:
            array_a = np.asarray(returns_a, dtype=np.float64)

        if isinstance(returns_b, list):
            array_b: np.ndarray = np.array(returns_b, dtype=np.float64)
        elif isinstance(returns_b, pd.Series):
            array_b = np.array(returns_b.values, dtype=np.float64)
        else:
            array_b = np.asarray(returns_b, dtype=np.float64)

        if len(array_a) == 0 or len(array_b) == 0:
            return 0.0

        # 피어슨 상관계수
        corr_tuple = stats.pearsonr(array_a, array_b)
        # pearsonr returns tuple of (correlation, p-value)
        corr_value: float = corr_tuple.statistic if hasattr(corr_tuple, "statistic") else corr_tuple[0]  # type: ignore[union-attr]

        return corr_value

    @staticmethod
    def downside_deviation(
        returns: pd.Series | np.ndarray | list[float],
        target_return: float = 0.0,
    ) -> float:
        """하방 편차 계산

        목표 수익률 미만의 변동성만 측정합니다.

        Args:
            returns: 일별 수익률
            target_return: 목표 수익률 (일별)

        Returns:
            하방 편차
        """
        if isinstance(returns, list):
            returns_array: np.ndarray = np.array(returns, dtype=np.float64)
        elif isinstance(returns, pd.Series):
            returns_array = np.array(returns.values, dtype=np.float64)
        else:
            returns_array = np.asarray(returns, dtype=np.float64)

        if len(returns_array) == 0:
            return 0.0

        # 목표 수익률 미만인 수익률만 선택
        downside_returns = returns_array[returns_array < target_return]

        if len(downside_returns) == 0:
            return 0.0

        # 하방 편차
        downside_dev = float(np.std(downside_returns, ddof=1))

        return downside_dev
