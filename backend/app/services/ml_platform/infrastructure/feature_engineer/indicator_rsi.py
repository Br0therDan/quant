"""
RSI (Relative Strength Index) Calculator
Oscillator indicating overbought/oversold conditions (0-100 range)
"""

import pandas as pd


class RSICalculator:
    """Calculate Relative Strength Index (RSI) indicator"""

    def __init__(self, period: int = 14) -> None:
        """
        Initialize RSI calculator

        Args:
            period: Number of periods for RSI calculation (default: 14)
        """
        self.period = period

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate RSI and add to dataframe

        Args:
            df: DataFrame with 'close' column

        Returns:
            DataFrame with 'rsi' column added

        Formula:
            RSI = 100 - (100 / (1 + RS))
            RS = Average Gain / Average Loss
        """
        df = df.copy()
        close = df["close"]
        delta = close.diff()

        # Type-safe comparison with explicit float conversion
        gain = delta.where(delta > 0.0, 0.0)  # type: ignore
        loss = -delta.where(delta < 0.0, 0.0)  # type: ignore

        avg_gain = gain.rolling(window=self.period).mean()
        avg_loss = loss.rolling(window=self.period).mean()

        rs = avg_gain / avg_loss
        df["rsi"] = 100 - (100 / (1 + rs))

        return df
