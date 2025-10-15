"""
Feature Engineering Pipeline for ML Models

Phase 3.2 ML Integration - Technical Indicators Calculation
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Moving Averages (SMA, EMA)
"""

import numpy as np
import pandas as pd


class FeatureEngineer:
    """
    기술적 지표를 계산하여 ML 모델 학습/추론을 위한 피처를 생성합니다.

    Features:
    - RSI: 과매수/과매도 지표 (0-100)
    - MACD: 단기/장기 이동평균 차이
    - Bollinger Bands: 가격 변동성 밴드
    - SMA: 단순 이동평균
    - EMA: 지수 이동평균
    - Volume indicators: 거래량 변화율
    """

    def __init__(self):
        """기본 파라미터 설정"""
        self.rsi_period = 14
        self.macd_fast = 12
        self.macd_slow = 26
        self.macd_signal = 9
        self.bb_period = 20
        self.bb_std = 2
        self.sma_periods = [5, 10, 20, 50]  # 200일 제거 (데이터 부족 방지)
        self.ema_periods = [12, 26]

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

        # 1. RSI (Relative Strength Index)
        df = self._calculate_rsi(df)

        # 2. MACD (Moving Average Convergence Divergence)
        df = self._calculate_macd(df)

        # 3. Bollinger Bands
        df = self._calculate_bollinger_bands(df)

        # 4. Moving Averages (SMA, EMA)
        df = self._calculate_moving_averages(df)

        # 5. Volume Indicators
        df = self._calculate_volume_indicators(df)

        # 6. Price Changes
        df = self._calculate_price_changes(df)

        # NaN 제거 (초기 계산에서 발생)
        df = df.dropna()

        return df

    def _calculate_rsi(self, df: pd.DataFrame) -> pd.DataFrame:
        """RSI (Relative Strength Index) 계산"""
        close = df["close"]
        delta = close.diff()

        # Type-safe comparison with explicit float conversion
        gain = delta.where(delta > 0.0, 0.0)  # type: ignore
        loss = -delta.where(delta < 0.0, 0.0)  # type: ignore

        avg_gain = gain.rolling(window=self.rsi_period).mean()
        avg_loss = loss.rolling(window=self.rsi_period).mean()

        rs = avg_gain / avg_loss
        df["rsi"] = 100 - (100 / (1 + rs))

        return df

    def _calculate_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        """MACD (Moving Average Convergence Divergence) 계산"""
        close = df["close"]

        ema_fast = close.ewm(span=self.macd_fast, adjust=False).mean()
        ema_slow = close.ewm(span=self.macd_slow, adjust=False).mean()

        df["macd"] = ema_fast - ema_slow
        df["macd_signal"] = df["macd"].ewm(span=self.macd_signal, adjust=False).mean()
        df["macd_hist"] = df["macd"] - df["macd_signal"]

        return df

    def _calculate_bollinger_bands(self, df: pd.DataFrame) -> pd.DataFrame:
        """Bollinger Bands 계산"""
        close = df["close"]

        sma = close.rolling(window=self.bb_period).mean()
        std = close.rolling(window=self.bb_period).std()

        df["bb_upper"] = sma + (std * self.bb_std)
        df["bb_middle"] = sma
        df["bb_lower"] = sma - (std * self.bb_std)

        # Bollinger Band Width (변동성 지표)
        df["bb_width"] = (df["bb_upper"] - df["bb_lower"]) / df["bb_middle"]

        # Price position within bands (0-1)
        df["bb_position"] = (df["close"] - df["bb_lower"]) / (
            df["bb_upper"] - df["bb_lower"]
        )

        return df

    def _calculate_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """SMA, EMA 계산"""
        close = df["close"]

        # SMA (Simple Moving Average)
        for period in self.sma_periods:
            df[f"sma_{period}"] = close.rolling(window=period).mean()

        # EMA (Exponential Moving Average)
        for period in self.ema_periods:
            df[f"ema_{period}"] = close.ewm(span=period, adjust=False).mean()

        return df

    def _calculate_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """거래량 지표 계산"""
        volume = df["volume"]

        # Volume SMA
        df["volume_sma_20"] = volume.rolling(window=20).mean()

        # Volume ratio (현재 거래량 / 평균 거래량)
        df["volume_ratio"] = df["volume"] / df["volume_sma_20"]

        # On-Balance Volume (OBV)
        df["obv"] = (
            np.where(df["close"] > df["close"].shift(1), volume, -volume)
            .cumsum()
            .astype(float)
        )

        return df

    def _calculate_price_changes(self, df: pd.DataFrame) -> pd.DataFrame:
        """가격 변화율 계산"""
        close = df["close"]

        # 일별 변화율
        df["price_change_1d"] = close.pct_change(periods=1)
        df["price_change_5d"] = close.pct_change(periods=5)
        df["price_change_20d"] = close.pct_change(periods=20)

        # High-Low range
        df["hl_range"] = (df["high"] - df["low"]) / df["close"]

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
            # Moving Averages
            *[f"sma_{p}" for p in self.sma_periods],
            *[f"ema_{p}" for p in self.ema_periods],
            # Volume
            "volume_sma_20",
            "volume_ratio",
            "obv",
            # Price Changes
            "price_change_1d",
            "price_change_5d",
            "price_change_20d",
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
