"""
Feature Engineering Pipeline for ML Models

Delegates to specialized indicator calculators:
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Moving Averages (SMA, EMA)
- Volume Indicators
- Price Change Indicators
"""

from __future__ import annotations

import pandas as pd

from .indicator_bollinger import BollingerBandsCalculator
from .indicator_macd import MACDCalculator
from .indicator_ma import MovingAverageCalculator
from .indicator_price import PriceChangeCalculator
from .indicator_rsi import RSICalculator
from .indicator_volume import VolumeIndicatorCalculator

__all__ = ["FeatureEngineer"]


class FeatureEngineer:
    """
    기술적 지표를 계산하여 ML 모델 학습/추론을 위한 피처를 생성합니다.

    Delegates to specialized calculators:
    - RSICalculator: 과매수/과매도 지표 (0-100)
    - MACDCalculator: 단기/장기 이동평균 차이
    - BollingerBandsCalculator: 가격 변동성 밴드
    - MovingAverageCalculator: SMA, EMA
    - VolumeIndicatorCalculator: 거래량 변화율
    - PriceChangeCalculator: 가격 변화율
    """

    def __init__(self) -> None:
        """Initialize with default indicator calculators"""
        self.rsi_calc = RSICalculator(period=14)
        self.macd_calc = MACDCalculator(fast=12, slow=26, signal=9)
        self.bb_calc = BollingerBandsCalculator(period=20, std_dev=2)
        self.ma_calc = MovingAverageCalculator(
            sma_periods=[5, 10, 20, 50], ema_periods=[12, 26]
        )
        self.volume_calc = VolumeIndicatorCalculator(sma_period=20)
        self.price_calc = PriceChangeCalculator(periods=[1, 5, 20])

    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        시계열 데이터에 모든 기술적 지표를 계산하여 추가합니다.

        Args:
            df: OHLCV 데이터프레임 (columns: open, high, low, close, volume)

        Returns:
            기술적 지표가 추가된 데이터프레임

        Example:
            >>> df = pd.DataFrame({
            ...     'open': [100, 101, 102],
            ...     'high': [105, 106, 107],
            ...     'low': [99, 100, 101],
            ...     'close': [102, 103, 104],
            ...     'volume': [1000, 1100, 1200]
            ... })
            >>> fe = FeatureEngineer()
            >>> result = fe.calculate_technical_indicators(df)
            >>> print(result.columns)
        """
        df = df.copy()

        # 필수 컬럼 검증
        required_cols = ["open", "high", "low", "close", "volume"]
        if not all(col in df.columns for col in required_cols):
            msg = f"Missing required columns. Need: {required_cols}"
            raise ValueError(msg)

        # Delegate to specialized calculators
        df = self.rsi_calc.calculate(df)
        df = self.macd_calc.calculate(df)
        df = self.bb_calc.calculate(df)
        df = self.ma_calc.calculate(df)
        df = self.volume_calc.calculate(df)
        df = self.price_calc.calculate(df)

        # NaN 제거 (초기 계산에서 발생)
        df = df.dropna()

        return df

    def get_feature_columns(self) -> list[str]:
        """
        ML 모델에 사용할 피처 컬럼 목록을 반환합니다.

        Returns:
            피처 컬럼명 리스트
        """
        features = [
            # RSI
            "rsi",
            # MACD
            "macd",
            "macd_signal",
            "macd_hist",
            # Bollinger Bands
            "bb_upper",
            "bb_middle",
            "bb_lower",
            "bb_width",
            "bb_position",
            # Moving Averages - SMA
            *[f"sma_{p}" for p in self.ma_calc.sma_periods],
            # Moving Averages - EMA
            *[f"ema_{p}" for p in self.ma_calc.ema_periods],
            # Volume
            f"volume_sma_{self.volume_calc.sma_period}",
            "volume_ratio",
            "obv",
            # Price Changes
            *[f"price_change_{p}d" for p in self.price_calc.periods],
            "hl_range",
        ]
        return features

    def prepare_training_data(
        self, df: pd.DataFrame, target_column: str = "signal"
    ) -> tuple[pd.DataFrame, pd.Series | None]:
        """
        학습 데이터를 피처(X)와 타겟(y)으로 분리합니다.

        Args:
            df: 기술적 지표가 계산된 데이터프레임
            target_column: 타겟 컬럼명 (기본: 'signal')

        Returns:
            (X, y) 튜플 - 피처 데이터프레임, 타겟 시리즈 (타겟이 없으면 None)

        Example:
            >>> fe = FeatureEngineer()
            >>> df_with_features = fe.calculate_technical_indicators(df)
            >>> df_with_features['signal'] = generate_labels(df_with_features)
            >>> X, y = fe.prepare_training_data(df_with_features)
        """
        feature_cols = self.get_feature_columns()

        # 피처 컬럼이 데이터프레임에 존재하는지 확인
        available_features = [col for col in feature_cols if col in df.columns]

        if not available_features:
            msg = "No feature columns found in dataframe"
            raise ValueError(msg)

        X = df[available_features]
        y = df[target_column] if target_column in df.columns else None

        return X, y
