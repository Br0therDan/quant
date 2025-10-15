"""전략 검증기

전략 파라미터, 신호 검증 로직을 제공합니다.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class StrategyValidator:
    """전략 검증기

    전략 설정 및 신호의 유효성을 검증합니다.
    """

    @staticmethod
    def validate_strategy_params(params: dict[str, Any]) -> dict[str, Any]:
        """전략 파라미터 검증

        Args:
            params: 전략 파라미터 딕셔너리

        Returns:
            검증된 파라미터

        Raises:
            ValueError: 파라미터가 유효하지 않을 때
        """
        if not params:
            raise ValueError("Strategy parameters cannot be empty")

        # 필수 파라미터 검증 (전략별로 다를 수 있음)
        required_params = ["symbols"]  # 최소 필수 항목

        for param in required_params:
            if param not in params:
                raise ValueError(f"Missing required parameter: {param}")

        # symbols 검증
        if "symbols" in params:
            symbols = params["symbols"]
            if not symbols:
                raise ValueError("Symbols list cannot be empty")

            if not isinstance(symbols, list):
                raise ValueError("Symbols must be a list")

            if len(symbols) > 100:
                logger.warning(
                    f"Strategy has many symbols: {len(symbols)}. "
                    "This may slow down backtesting."
                )

        return params

    @staticmethod
    def validate_signal_strength(signal: float) -> float:
        """신호 강도 검증

        Args:
            signal: 신호 강도 (-1.0 ~ 1.0)

        Returns:
            검증된 신호 강도

        Raises:
            ValueError: 신호가 유효하지 않을 때
        """
        if not -1.0 <= signal <= 1.0:
            raise ValueError(
                f"Signal strength must be between -1.0 and 1.0, got {signal}"
            )

        return signal

    @staticmethod
    def validate_indicator_period(period: int, min_period: int = 1) -> int:
        """기술 지표 기간 검증

        Args:
            period: 지표 계산 기간 (예: 20일 이동평균)
            min_period: 최소 허용 기간 (기본값 1)

        Returns:
            검증된 기간

        Raises:
            ValueError: 기간이 유효하지 않을 때
        """
        if period < min_period:
            raise ValueError(f"Period must be at least {min_period}, got {period}")

        if period > 500:
            logger.warning(
                f"Indicator period is very long: {period}. "
                "This may require more historical data."
            )

        return period
