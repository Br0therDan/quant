"""
MACD (Moving Average Convergence Divergence) Calculator
Trend-following momentum indicator
"""

import pandas as pd


class MACDCalculator:
    """Calculate MACD, Signal Line, and Histogram"""

    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9) -> None:
        """
        Initialize MACD calculator

        Args:
            fast: Fast EMA period (default: 12)
            slow: Slow EMA period (default: 26)
            signal: Signal line EMA period (default: 9)
        """
        self.fast = fast
        self.slow = slow
        self.signal = signal

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate MACD, Signal Line, and Histogram

        Args:
            df: DataFrame with 'close' column

        Returns:
            DataFrame with 'macd', 'macd_signal', 'macd_hist' columns added

        Formula:
            MACD = EMA(fast) - EMA(slow)
            Signal = EMA(MACD, signal_period)
            Histogram = MACD - Signal
        """
        df = df.copy()
        close = df["close"]

        ema_fast = close.ewm(span=self.fast, adjust=False).mean()
        ema_slow = close.ewm(span=self.slow, adjust=False).mean()

        df["macd"] = ema_fast - ema_slow
        df["macd_signal"] = df["macd"].ewm(span=self.signal, adjust=False).mean()
        df["macd_hist"] = df["macd"] - df["macd_signal"]

        return df
