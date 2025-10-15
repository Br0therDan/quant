"""
Price Change Calculator
Price momentum and volatility indicators
"""

import pandas as pd


class PriceChangeCalculator:
    """Calculate price change rates and high-low range"""

    def __init__(self, periods: list[int] | None = None) -> None:
        """
        Initialize Price Change calculator

        Args:
            periods: List of periods for price change calculation (default: [1, 5, 20])
        """
        self.periods = periods or [1, 5, 20]

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate price change rates and volatility metrics

        Args:
            df: DataFrame with 'open', 'high', 'low', 'close' columns

        Returns:
            DataFrame with price change columns added:
            - price_change_{period}d: Percentage change over period
            - hl_range: (High - Low) / Close ratio

        Formula:
            Price Change = (Close[t] - Close[t-period]) / Close[t-period]
            HL Range = (High - Low) / Close
        """
        df = df.copy()
        close = df["close"]

        # Price change rates for multiple periods
        for period in self.periods:
            df[f"price_change_{period}d"] = close.pct_change(periods=period)

        # High-Low range (intraday volatility)
        df["hl_range"] = (df["high"] - df["low"]) / df["close"]

        return df
