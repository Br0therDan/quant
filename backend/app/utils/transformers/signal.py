"""신호 변환기

전략 신호를 거래 신호로 변환하는 로직을 제공합니다.
"""

import logging

logger = logging.getLogger(__name__)


class SignalTransformer:
    """신호 변환기

    전략 신호 (-1.0 ~ 1.0)를 구체적인 거래 신호로 변환합니다.
    """

    @staticmethod
    def to_trade_action(
        signal: float,
        buy_threshold: float = 0.5,
        sell_threshold: float = -0.5,
    ) -> str:
        """신호를 거래 액션으로 변환

        Args:
            signal: 신호 강도 (-1.0 ~ 1.0)
            buy_threshold: 매수 임계값 (기본값 0.5)
            sell_threshold: 매도 임계값 (기본값 -0.5)

        Returns:
            거래 액션 ("BUY", "SELL", "HOLD")

        Example:
            >>> action = SignalTransformer.to_trade_action(0.8)
            >>> print(action)
            BUY
        """
        if signal >= buy_threshold:
            return "BUY"
        if signal <= sell_threshold:
            return "SELL"
        return "HOLD"

    @staticmethod
    def to_position_size(
        signal: float,
        available_capital: float,
        max_position_size: float = 1.0,
    ) -> float:
        """신호 강도에 따른 포지션 크기 계산

        Args:
            signal: 신호 강도 (-1.0 ~ 1.0)
            available_capital: 가용 자본
            max_position_size: 최대 포지션 크기 (자본의 비율)

        Returns:
            포지션 크기 (USD)

        Example:
            >>> size = SignalTransformer.to_position_size(0.75, 100000.0, 0.5)
            >>> print(f"Position size: ${size:,.2f}")
            Position size: $37,500.00
        """
        # 신호 강도를 절대값으로 변환 (0.0 ~ 1.0)
        signal_strength = abs(signal)

        # 포지션 크기 계산
        position_size = available_capital * max_position_size * signal_strength

        return position_size

    @staticmethod
    def combine_signals(
        signals: dict[str, float],
        weights: dict[str, float] | None = None,
    ) -> float:
        """여러 신호를 가중 평균으로 결합

        Args:
            signals: 신호 딕셔너리 {신호명: 강도}
            weights: 가중치 딕셔너리 {신호명: 가중치} (선택, 기본값 균등 가중)

        Returns:
            결합된 신호 (-1.0 ~ 1.0)

        Example:
            >>> signals = {"RSI": 0.6, "MACD": 0.4, "SMA": -0.2}
            >>> combined = SignalTransformer.combine_signals(signals)
            >>> print(f"Combined signal: {combined:.2f}")
            Combined signal: 0.27
        """
        if not signals:
            return 0.0

        # 가중치가 없으면 균등 가중
        if weights is None:
            weights = {name: 1.0 / len(signals) for name in signals}

        # 가중 평균 계산
        total_weight = sum(weights.values())
        if total_weight == 0:
            return 0.0

        weighted_sum = sum(signals[name] * weights.get(name, 0.0) for name in signals)
        combined_signal = weighted_sum / total_weight

        # 범위 제한 (-1.0 ~ 1.0)
        combined_signal = max(-1.0, min(1.0, combined_signal))

        return combined_signal

    @staticmethod
    def normalize_signal(
        raw_signal: float,
        min_value: float,
        max_value: float,
    ) -> float:
        """원시 신호를 -1.0 ~ 1.0 범위로 정규화

        Args:
            raw_signal: 원시 신호 값
            min_value: 최소값
            max_value: 최대값

        Returns:
            정규화된 신호 (-1.0 ~ 1.0)

        Example:
            >>> # RSI 값 (0 ~ 100)을 신호로 변환
            >>> rsi_signal = SignalTransformer.normalize_signal(70, 0, 100)
            >>> print(f"RSI signal: {rsi_signal:.2f}")
            RSI signal: 0.40
        """
        if max_value == min_value:
            return 0.0

        # 0 ~ 1 범위로 정규화
        normalized = (raw_signal - min_value) / (max_value - min_value)

        # -1 ~ 1 범위로 변환
        signal = (normalized * 2) - 1

        # 범위 제한
        signal = max(-1.0, min(1.0, signal))

        return signal
