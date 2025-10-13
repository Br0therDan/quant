"""
Test FeatureEngineer - Phase 3.2 ML Integration

Quick test to verify technical indicator calculations
"""

import pandas as pd

from app.services.ml import FeatureEngineer


def test_feature_engineer():
    """FeatureEngineer 기본 기능 테스트"""
    # Sample OHLCV data (100 days)
    data = {
        "open": [100 + i * 0.5 for i in range(100)],
        "high": [102 + i * 0.5 for i in range(100)],
        "low": [99 + i * 0.5 for i in range(100)],
        "close": [101 + i * 0.5 for i in range(100)],
        "volume": [1000 + i * 10 for i in range(100)],
    }
    df = pd.DataFrame(data)

    # Initialize FeatureEngineer
    fe = FeatureEngineer()

    # Calculate technical indicators
    result = fe.calculate_technical_indicators(df)

    # Verify all expected columns exist
    expected_features = fe.get_feature_columns()
    for feature in expected_features:
        assert feature in result.columns, f"Missing feature column: {feature}"

    print(f"\n📊 Result shape: {result.shape}")
    print(f"RSI stats: min={result['rsi'].min():.2f}, max={result['rsi'].max():.2f}")
    print(f"NaN count in RSI: {result['rsi'].isna().sum()}")

    # Verify RSI is in valid range (0-100)
    assert result["rsi"].min() >= 0, "RSI below 0"
    assert result["rsi"].max() <= 100, "RSI above 100"

    # Verify MACD columns exist
    assert "macd" in result.columns
    assert "macd_signal" in result.columns
    assert "macd_hist" in result.columns

    # Verify Bollinger Bands
    assert (result["bb_upper"] >= result["bb_middle"]).all()
    assert (result["bb_middle"] >= result["bb_lower"]).all()

    # Verify no NaN in final result (all dropped)
    assert not result.isnull().any().any(), "NaN values found in result"

    print("✅ FeatureEngineer test passed!")
    print(f"Input shape: {df.shape}")
    print(f"Output shape: {result.shape}")
    print(f"Features calculated: {len(expected_features)}")
    print("\nSample features:")
    print(result[["rsi", "macd", "bb_width", "volume_ratio"]].tail())


if __name__ == "__main__":
    test_feature_engineer()
