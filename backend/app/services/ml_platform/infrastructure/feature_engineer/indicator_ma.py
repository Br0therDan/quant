"""
Moving Average Calculator (SMA & EMA)
Trend-following indicators
"""

import pandas as pd


class MovingAverageCalculator:
    """Calculate Simple Moving Average (SMA) and Exponential Moving Average (EMA)"""

    def __init__(
        self, sma_periods: list[int] | None = None, ema_periods: list[int] | None = None
    ) -> None:
        """
        Initialize Moving Average calculator

        Args:
            sma_periods: List of periods for SMA (default: [5, 10, 20, 50])
            ema_periods: List of periods for EMA (default: [12, 26])
        """
        self.sma_periods = sma_periods or [5, 10, 20, 50]
        self.ema_periods = ema_periods or [12, 26]

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate SMA and EMA for multiple periods

        Args:
            df: DataFrame with 'close' column

        Returns:
            DataFrame with moving average columns added:
            - sma_{period}: Simple moving average
            - ema_{period}: Exponential moving average

        Formula:
            SMA = Sum(close, period) / period
            EMA = weighted average with more weight on recent prices
        """
        df = df.copy()
        close = df["close"]

        # SMA (Simple Moving Average)
        for period in self.sma_periods:
            df[f"sma_{period}"] = close.rolling(window=period).mean()

        # EMA (Exponential Moving Average)
        for period in self.ema_periods:
            df[f"ema_{period}"] = close.ewm(span=period, adjust=False).mean()

        return df
