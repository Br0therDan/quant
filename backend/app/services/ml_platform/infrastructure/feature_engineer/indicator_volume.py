"""
Volume Indicator Calculator
Trading volume analysis indicators
"""

import numpy as np
import pandas as pd


class VolumeIndicatorCalculator:
    """Calculate volume-based indicators (Volume SMA, Volume Ratio, OBV)"""

    def __init__(self, sma_period: int = 20) -> None:
        """
        Initialize Volume Indicator calculator

        Args:
            sma_period: Period for volume SMA (default: 20)
        """
        self.sma_period = sma_period

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate volume indicators

        Args:
            df: DataFrame with 'volume' and 'close' columns

        Returns:
            DataFrame with volume indicator columns added:
            - volume_sma_20: Volume simple moving average
            - volume_ratio: Current volume / Average volume
            - obv: On-Balance Volume (cumulative)

        Formulas:
            Volume Ratio = Current Volume / Volume SMA
            OBV = Cumulative sum of signed volume based on price direction
        """
        df = df.copy()
        volume = df["volume"]

        # Volume SMA
        df[f"volume_sma_{self.sma_period}"] = volume.rolling(
            window=self.sma_period
        ).mean()

        # Volume ratio (현재 거래량 / 평균 거래량)
        df["volume_ratio"] = df["volume"] / df[f"volume_sma_{self.sma_period}"]

        # On-Balance Volume (OBV)
        df["obv"] = (
            np.where(df["close"] > df["close"].shift(1), volume, -volume)
            .cumsum()
            .astype(float)
        )

        return df
