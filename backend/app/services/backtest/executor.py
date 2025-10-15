"""
전략 실행기 - 전략 신호 생성 담당
"""

import logging
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from app.services.trading.strategy_service import StrategyService

from app.strategies.base_strategy import BaseStrategy

logger = logging.getLogger(__name__)


class StrategyExecutor:
    """전략 실행기

    전략 인스턴스를 생성하고 시장 데이터를 기반으로 매매 신호를 생성합니다.
    Phase 2에서 도입된 컴포넌트입니다.
    """

    def __init__(self, strategy_service: "StrategyService"):
        self.strategy_service = strategy_service

    async def generate_signals(
        self,
        strategy_id: str,
        market_data: dict[str, Any],
        config: Any,
    ) -> list[dict[str, Any]]:
        """전략 신호 생성

        Args:
            strategy_id: 전략 ID
            market_data: 시장 데이터 딕셔너리
            config: 백테스트 설정

        Returns:
            생성된 신호 리스트
        """
        # 1. 전략 조회
        strategy = await self.strategy_service.get_strategy(strategy_id)
        if not strategy:
            raise ValueError(f"Strategy not found: {strategy_id}")

        # 2. 전략 인스턴스 생성
        strategy_instance = await self.strategy_service.get_strategy_instance(
            strategy_type=strategy.strategy_type,
            config=strategy.config,
        )

        if not strategy_instance:
            raise ValueError(
                f"Failed to create strategy instance: {strategy.strategy_type}"
            )

        # 3. 전략 초기화
        strategy_instance.initialize(market_data)

        # 4. 지표 계산 (내부적으로 처리됨)
        _ = await self._calculate_indicators(strategy_instance, market_data)

        # 5. 신호 생성
        signals = strategy_instance.generate_signals(market_data)

        logger.info(
            f"Generated {len(signals)} signals for strategy {strategy.name} "
            f"({strategy.strategy_type})"
        )

        return signals

    async def _calculate_indicators(
        self,
        strategy: BaseStrategy,
        market_data: dict[str, Any],
    ) -> dict[str, Any]:
        """기술적 지표 계산

        전략에 필요한 지표를 계산합니다.
        """
        indicators = {}

        try:
            # 전략별 지표 계산
            # market_data를 DataFrame으로 변환하여 전달
            # 현재는 전략 내부에서 처리하므로 스킵
            pass

        except Exception as e:
            logger.error(f"Failed to calculate indicators: {e}")
            raise

        return indicators

    async def validate_signals(
        self,
        signals: list[dict[str, Any]],
        market_data: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """신호 검증

        생성된 신호를 검증하고 필터링합니다.
        """
        valid_signals = []

        for signal in signals:
            # 기본 검증
            if not all(k in signal for k in ["symbol", "signal_type", "price"]):
                logger.warning(f"Invalid signal format: {signal}")
                continue

            # 가격 검증
            if signal["price"] <= 0:
                logger.warning(f"Invalid price in signal: {signal}")
                continue

            valid_signals.append(signal)

        logger.info(f"Validated {len(valid_signals)}/{len(signals)} signals")
        return valid_signals
