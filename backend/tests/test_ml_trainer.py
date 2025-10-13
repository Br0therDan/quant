"""
Test MLModelTrainer - Phase 3.2 ML Integration

End-to-end test: Feature engineering → Model training → Evaluation
"""

import pandas as pd

from app.services.ml.trainer import (
    MLModelTrainer,
    generate_labels_from_returns,
)


def test_ml_model_trainer():
    """MLModelTrainer 전체 워크플로우 테스트"""
    # 1. Generate sample data (200 days with trend)
    data = {
        "open": [100 + i * 0.5 + (i % 10) * 0.3 for i in range(200)],
        "high": [102 + i * 0.5 + (i % 10) * 0.3 for i in range(200)],
        "low": [99 + i * 0.5 + (i % 10) * 0.3 for i in range(200)],
        "close": [101 + i * 0.5 + (i % 10) * 0.3 for i in range(200)],
        "volume": [1000 + i * 10 for i in range(200)],
    }
    df = pd.DataFrame(data)

    # 2. Generate labels (buy=1 if next return > 2%)
    df["signal"] = generate_labels_from_returns(df, threshold=0.02, mode="binary")

    print(f"📊 Dataset: {len(df)} days")
    print(f"Signal distribution:\n{df['signal'].value_counts()}")

    # 3. Initialize trainer
    trainer = MLModelTrainer(task="binary", test_size=0.2, random_state=42)

    # 4. Prepare data (feature engineering + split)
    X_train, X_test, y_train, y_test = trainer.prepare_data(df, target_column="signal")

    print("\n✅ Data prepared:")
    print(f"  Train: {X_train.shape[0]} samples, {X_train.shape[1]} features")
    print(f"  Test:  {X_test.shape[0]} samples")

    # 5. Train model
    print("\n🚀 Training LightGBM model...")
    _ = trainer.train(X_train, y_train, num_boost_round=50, early_stopping_rounds=10)

    print(f"✅ Training completed! Best iteration: {trainer.model.best_iteration}")  # type: ignore

    # 6. Evaluate model
    print("\n📈 Evaluating model...")
    metrics = trainer.evaluate(X_test, y_test)

    # 7. Feature importance
    print("\n🔍 Top 10 Feature Importance:")
    importance = trainer.get_feature_importance(top_n=10)
    print(importance.to_string(index=False))

    # 8. Save model (optional)
    model_path = "/Users/donghakim/quant/backend/app/data/test_model.txt"
    trainer.save_model(model_path)
    print(f"\n💾 Model saved to: {model_path}")

    # 9. Test prediction
    sample_pred = trainer.predict(X_test.head(5))
    print(f"\n🔮 Sample predictions: {sample_pred}")
    print(f"   True labels:      {y_test.head(5).values}")

    # Assertions
    assert metrics["accuracy"] > 0.5, "Model accuracy too low"
    assert trainer.model is not None
    assert len(trainer.feature_names) > 0

    print("\n✅ MLModelTrainer test passed!")


if __name__ == "__main__":
    test_ml_model_trainer()
