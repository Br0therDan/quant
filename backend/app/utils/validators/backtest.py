"""백테스트 검증기

백테스트 설정, 파라미터 검증 로직을 제공합니다.
"""

import logging

logger = logging.getLogger(__name__)


class BacktestValidator:
    """백테스트 검증기

    백테스트 설정의 유효성을 검증합니다.
    """

    @staticmethod
    def validate_initial_capital(capital: float) -> float:
        """초기 자본 검증

        Args:
            capital: 초기 자본 (USD)

        Returns:
            검증된 자본

        Raises:
            ValueError: 자본이 유효하지 않을 때
        """
        if capital <= 0:
            raise ValueError("Initial capital must be positive")

        if capital < 1000:
            logger.warning(
                f"Initial capital is very low: ${capital:.2f}. "
                "Consider using at least $10,000 for realistic backtesting."
            )

        if capital > 100_000_000:
            raise ValueError(
                f"Initial capital is too high: ${capital:,.2f}. "
                "Maximum allowed: $100,000,000"
            )

        return capital

    @staticmethod
    def validate_commission(commission: float) -> float:
        """수수료 검증

        Args:
            commission: 거래 수수료 비율 (0.001 = 0.1%)

        Returns:
            검증된 수수료

        Raises:
            ValueError: 수수료가 유효하지 않을 때
        """
        if commission < 0:
            raise ValueError("Commission cannot be negative")

        if commission > 0.1:
            raise ValueError(
                f"Commission is too high: {commission*100:.2f}%. "
                "Maximum allowed: 10%"
            )

        if commission > 0.01:
            logger.warning(
                f"Commission is very high: {commission*100:.2f}%. "
                "Typical values are 0.1%-0.5%."
            )

        return commission

    @staticmethod
    def validate_slippage(slippage: float) -> float:
        """슬리피지 검증

        Args:
            slippage: 슬리피지 비율 (0.001 = 0.1%)

        Returns:
            검증된 슬리피지

        Raises:
            ValueError: 슬리피지가 유효하지 않을 때
        """
        if slippage < 0:
            raise ValueError("Slippage cannot be negative")

        if slippage > 0.05:
            raise ValueError(
                f"Slippage is too high: {slippage*100:.2f}%. " "Maximum allowed: 5%"
            )

        if slippage > 0.01:
            logger.warning(
                f"Slippage is very high: {slippage*100:.2f}%. "
                "Typical values are 0.1%-0.5%."
            )

        return slippage

    @staticmethod
    def validate_position_size(
        position_size: float,
        max_position: float = 1.0,
    ) -> float:
        """포지션 크기 검증

        Args:
            position_size: 포지션 크기 (자본의 비율, 1.0 = 100%)
            max_position: 최대 허용 포지션 (기본값 100%)

        Returns:
            검증된 포지션 크기

        Raises:
            ValueError: 포지션 크기가 유효하지 않을 때
        """
        if position_size <= 0:
            raise ValueError("Position size must be positive")

        if position_size > max_position:
            raise ValueError(
                f"Position size ({position_size*100:.1f}%) exceeds "
                f"maximum allowed ({max_position*100:.1f}%)"
            )

        if position_size > 0.5:
            logger.warning(
                f"Position size is very large: {position_size*100:.1f}%. "
                "Consider diversifying to reduce risk."
            )

        return position_size
