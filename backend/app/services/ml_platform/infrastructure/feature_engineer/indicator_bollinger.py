"""
Bollinger Bands Calculator
Volatility indicator with upper/lower bands around moving average
"""

import pandas as pd


class BollingerBandsCalculator:
    """Calculate Bollinger Bands (upper, middle, lower, width, position)"""

    def __init__(self, period: int = 20, std_dev: int = 2) -> None:
        """
        Initialize Bollinger Bands calculator

        Args:
            period: Moving average period (default: 20)
            std_dev: Number of standard deviations (default: 2)
        """
        self.period = period
        self.std_dev = std_dev

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Bollinger Bands and derived metrics

        Args:
            df: DataFrame with 'close' column

        Returns:
            DataFrame with BB columns added:
            - bb_upper: Upper band (SMA + std_dev * STD)
            - bb_middle: Middle band (SMA)
            - bb_lower: Lower band (SMA - std_dev * STD)
            - bb_width: Band width normalized by middle (volatility)
            - bb_position: Price position within bands (0-1)

        Formula:
            Middle Band = SMA(close, period)
            Upper Band = Middle + (std_dev * STD(close, period))
            Lower Band = Middle - (std_dev * STD(close, period))
        """
        df = df.copy()
        close = df["close"]

        sma = close.rolling(window=self.period).mean()
        std = close.rolling(window=self.period).std()

        df["bb_upper"] = sma + (std * self.std_dev)
        df["bb_middle"] = sma
        df["bb_lower"] = sma - (std * self.std_dev)

        # Bollinger Band Width (변동성 지표)
        df["bb_width"] = (df["bb_upper"] - df["bb_lower"]) / df["bb_middle"]

        # Price position within bands (0-1)
        df["bb_position"] = (df["close"] - df["bb_lower"]) / (
            df["bb_upper"] - df["bb_lower"]
        )

        return df
