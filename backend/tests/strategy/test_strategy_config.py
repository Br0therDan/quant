"""
전략 설정 타입 안전성 테스트
"""

import pytest
from pydantic import ValidationError
from app.strategies.configs import SMACrossoverConfig, RSIMeanReversionConfig


def test_sma_config_validation():
    """SMA 설정 검증 테스트"""
    # ✅ 유효한 설정
    config = SMACrossoverConfig(
        short_window=10,
        long_window=30,
    )
    assert config.short_window == 10
    assert config.long_window == 30

    # ❌ 잘못된 설정 (long < short)
    with pytest.raises(ValidationError) as exc_info:
        SMACrossoverConfig(
            short_window=30,
            long_window=10,
        )
    assert "long_window" in str(exc_info.value)


def test_rsi_config_validation():
    """RSI 설정 검증 테스트"""
    # ✅ 유효한 설정
    config = RSIMeanReversionConfig(
        rsi_period=14,
        oversold_threshold=30.0,
        overbought_threshold=70.0,
    )
    assert config.oversold_threshold < config.overbought_threshold

    # ❌ 잘못된 임계값
    with pytest.raises(ValidationError):
        RSIMeanReversionConfig(
            oversold_threshold=70.0,
            overbought_threshold=30.0,  # 역전
        )


def test_config_default_values():
    """Config 기본값 테스트"""
    config = SMACrossoverConfig()

    assert config.short_window == 10
    assert config.long_window == 30
    assert config.min_crossover_strength == 0.01
    assert config.lookback_period == 252
    assert config.max_position_size == 1.0
