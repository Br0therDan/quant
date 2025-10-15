"""
Test ModelRegistry - Phase 3.2 ML Integration

Test model versioning, save/load, and metadata management
"""

import shutil
from pathlib import Path

import pandas as pd

from app.services.ml_platform.infrastructure import (
    MLModelTrainer,
    generate_labels_from_returns,
)
from app.services.ml_platform.infrastructure.model_registry import ModelRegistry


def test_model_registry():
    """ModelRegistry 전체 기능 테스트"""
    # Setup: Clean test directory
    test_dir = Path("/Users/donghakim/quant/backend/app/data/test_registry")
    if test_dir.exists():
        shutil.rmtree(test_dir)

    # 1. Initialize registry
    registry = ModelRegistry(base_dir=test_dir)
    print("✅ ModelRegistry initialized")

    # 2. Train a sample model
    data = {
        "open": [100 + i * 0.5 + (i % 10) * 0.3 for i in range(200)],
        "high": [102 + i * 0.5 + (i % 10) * 0.3 for i in range(200)],
        "low": [99 + i * 0.5 + (i % 10) * 0.3 for i in range(200)],
        "close": [101 + i * 0.5 + (i % 10) * 0.3 for i in range(200)],
        "volume": [1000 + i * 10 for i in range(200)],
    }
    df = pd.DataFrame(data)
    df["signal"] = generate_labels_from_returns(df, threshold=0.02)

    trainer = MLModelTrainer(task="binary", test_size=0.2)
    X_train, X_test, y_train, y_test = trainer.prepare_data(df)
    trainer.train(X_train, y_train, num_boost_round=50)
    metrics = trainer.evaluate(X_test, y_test)

    print(f"✅ Model trained with accuracy: {metrics['accuracy']:.4f}")

    # 3. Save model (v1)
    version1 = registry.save_model(
        model=trainer.model,  # type: ignore
        model_type="signal",
        metrics=metrics,
        feature_names=trainer.feature_names,
        training_params={"num_boost_round": 50},
    )
    print(f"✅ Model saved as {version1}")

    # 4. Train another model (v2)
    trainer2 = MLModelTrainer(task="binary", test_size=0.2)
    X_train2, X_test2, y_train2, y_test2 = trainer2.prepare_data(df)
    trainer2.train(X_train2, y_train2, num_boost_round=100)
    metrics2 = trainer2.evaluate(X_test2, y_test2)

    version2 = registry.save_model(
        model=trainer2.model,  # type: ignore
        model_type="signal",
        metrics=metrics2,
        feature_names=trainer2.feature_names,
    )
    print(f"✅ Model saved as {version2}")

    # 5. List all models
    print("\n📋 All models:")
    models = registry.list_models()
    for model in models:
        print(
            f"  {model['version']}: "
            f"accuracy={model['metrics'].get('accuracy', 0):.4f}, "
            f"created={model['created_at']}"
        )

    # 6. Load latest model
    latest_version = registry.get_latest_version(model_type="signal")
    print(f"\n📥 Latest version: {latest_version}")

    loaded_model, loaded_metadata = registry.load_model(model_type="signal")
    print(
        f"✅ Loaded model {loaded_metadata['version']} "
        f"with {loaded_model.num_trees()} trees"
    )

    # 7. Load specific version
    loaded_model_v1, _ = registry.load_model(version="v1")
    print(f"✅ Loaded v1 with {loaded_model_v1.num_trees()} trees")

    # 8. Compare models
    comparison = registry.compare_models(["v1", "v2"], metric="accuracy")
    print(f"\n📊 Model comparison (accuracy): {comparison}")

    # 9. Get best model
    best_version = registry.get_best_model(model_type="signal", metric="accuracy")
    print(f"🏆 Best model: {best_version}")

    # 10. Get model info
    info = registry.get_model_info(version="v1")
    print("\n📝 v1 info:")
    print(f"  Features: {len(info['feature_names'])}")
    print(f"  Trees: {info['num_iterations']}")
    print(f"  Accuracy: {info['metrics'].get('accuracy', 0):.4f}")

    # Assertions
    assert version1 == "v1"
    assert version2 == "v2"
    assert latest_version == "v2"
    assert len(models) == 2
    assert loaded_model.num_trees() > 0

    print("\n✅ ModelRegistry test passed!")


if __name__ == "__main__":
    test_model_registry()
