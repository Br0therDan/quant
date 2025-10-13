"""
ML Model Trainer - Phase 3.2 ML Integration

LightGBM-based trading signal prediction model:
- Binary classification (buy=1, hold/sell=0) or Multi-class (buy/hold/sell)
- Feature engineering pipeline integration
- Train/validation/test split
- Hyperparameter tuning with Optuna (optional)
- Model evaluation metrics
"""

from pathlib import Path
from typing import Literal

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split

from app.services.ml.feature_engineer import FeatureEngineer


class MLModelTrainer:
    """
    LightGBM 모델 학습 및 평가를 담당합니다.

    Features:
    - Binary/Multi-class classification
    - Train/validation/test split
    - Feature importance analysis
    - Model evaluation metrics
    """

    def __init__(
        self,
        task: Literal["binary", "multiclass"] = "binary",
        test_size: float = 0.2,
        val_size: float = 0.1,
        random_state: int = 42,
    ):
        """
        Args:
            task: 'binary' (buy vs not-buy) or 'multiclass' (buy/hold/sell)
            test_size: Test set ratio (0.2 = 20%)
            val_size: Validation set ratio from training data
            random_state: Random seed for reproducibility
        """
        self.task = task
        self.test_size = test_size
        self.val_size = val_size
        self.random_state = random_state
        self.feature_engineer = FeatureEngineer()
        self.model: lgb.Booster | None = None
        self.feature_names: list[str] = []

    def prepare_data(
        self, df: pd.DataFrame, target_column: str = "signal"
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """
        데이터를 학습/테스트 세트로 분리합니다.

        Args:
            df: OHLCV + signal 데이터프레임
            target_column: 타겟 컬럼명

        Returns:
            (X_train, X_test, y_train, y_test)
        """
        # 1. Calculate technical indicators
        df_features = self.feature_engineer.calculate_technical_indicators(df)

        # 2. Prepare training data
        X, y = self.feature_engineer.prepare_training_data(df_features, target_column)

        if y is None:
            msg = f"Target column '{target_column}' not found in dataframe"
            raise ValueError(msg)

        # 3. Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_size, random_state=self.random_state
        )

        self.feature_names = list(X.columns)

        return X_train, X_test, y_train, y_test

    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: pd.DataFrame | None = None,
        y_val: pd.Series | None = None,
        params: dict | None = None,
        num_boost_round: int = 100,
        early_stopping_rounds: int = 10,
    ) -> dict:
        """
        LightGBM 모델을 학습합니다.

        Args:
            X_train: Training features
            y_train: Training labels
            X_val: Validation features (optional)
            y_val: Validation labels (optional)
            params: LightGBM parameters (optional)
            num_boost_round: Number of boosting iterations
            early_stopping_rounds: Early stopping patience

        Returns:
            Training history dict
        """
        # Default LightGBM parameters
        default_params = {
            "objective": ("binary" if self.task == "binary" else "multiclass"),
            "metric": "binary_logloss" if self.task == "binary" else "multi_logloss",
            "boosting_type": "gbdt",
            "num_leaves": 31,
            "learning_rate": 0.05,
            "feature_fraction": 0.9,
            "bagging_fraction": 0.8,
            "bagging_freq": 5,
            "verbose": -1,
        }

        if self.task == "multiclass":
            # Determine number of classes
            num_classes = len(y_train.unique())
            default_params["num_class"] = num_classes

        # Override with user params
        if params:
            default_params.update(params)

        # Create LightGBM datasets
        train_data = lgb.Dataset(X_train, label=y_train)
        valid_sets = [train_data]
        valid_names = ["train"]

        if X_val is not None and y_val is not None:
            val_data = lgb.Dataset(X_val, label=y_val, reference=train_data)
            valid_sets.append(val_data)
            valid_names.append("valid")

        # Train model
        evals_result: dict = {}
        self.model = lgb.train(
            default_params,
            train_data,
            num_boost_round=num_boost_round,
            valid_sets=valid_sets,
            valid_names=valid_names,
            callbacks=[
                lgb.early_stopping(
                    stopping_rounds=early_stopping_rounds, verbose=False
                ),
                lgb.record_evaluation(evals_result),
            ],
        )

        return evals_result

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        모델로 예측을 수행합니다.

        Args:
            X: Feature dataframe

        Returns:
            Predicted labels (0/1 for binary, 0/1/2 for multiclass)
        """
        if self.model is None:
            msg = "Model not trained yet. Call train() first."
            raise ValueError(msg)

        # Get raw prediction (may be ndarray, list, or sparse matrix-like)
        y_pred_proba = self.model.predict(X)

        # Ensure numpy array and normalize shape for comparisons
        y_pred_proba = np.asarray(y_pred_proba)
        if y_pred_proba.ndim == 2 and y_pred_proba.shape[1] == 1:
            # Convert (n,1) -> (n,)
            y_pred_proba = y_pred_proba.ravel()

        if self.task == "binary":
            # Binary: threshold at 0.5
            return (y_pred_proba > 0.5).astype(int)

        # Multiclass: argmax
        return np.argmax(y_pred_proba, axis=1)

    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> dict[str, float]:
        """
        모델 성능을 평가합니다.

        Args:
            X_test: Test features
            y_test: True labels

        Returns:
            Evaluation metrics dict
        """
        y_pred = self.predict(X_test)

        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(
                y_test, y_pred, average="weighted", zero_division=0
            ),
            "recall": recall_score(y_test, y_pred, average="weighted", zero_division=0),
            "f1_score": f1_score(y_test, y_pred, average="weighted", zero_division=0),
        }

        # Print detailed report
        print("\n=== Model Evaluation ===")
        print(f"Accuracy: {metrics['accuracy']:.4f}")
        print(f"Precision: {metrics['precision']:.4f}")
        print(f"Recall: {metrics['recall']:.4f}")
        print(f"F1 Score: {metrics['f1_score']:.4f}")

        print("\n=== Classification Report ===")
        print(classification_report(y_test, y_pred, zero_division=0))

        print("\n=== Confusion Matrix ===")
        print(confusion_matrix(y_test, y_pred))

        return metrics

    def get_feature_importance(self, top_n: int = 20) -> pd.DataFrame:
        """
        피처 중요도를 반환합니다.

        Args:
            top_n: Top N features to return

        Returns:
            Feature importance dataframe
        """
        if self.model is None:
            msg = "Model not trained yet"
            raise ValueError(msg)

        importance = self.model.feature_importance(importance_type="gain")
        feature_importance = pd.DataFrame(
            {
                "feature": self.feature_names,
                "importance": importance,
            }
        ).sort_values("importance", ascending=False)

        return feature_importance.head(top_n)

    def save_model(self, path: Path | str) -> None:
        """
        모델을 파일로 저장합니다.

        Args:
            path: Model save path (.txt format)
        """
        if self.model is None:
            msg = "No model to save"
            raise ValueError(msg)

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.model.save_model(str(path))

    def load_model(self, path: Path | str) -> None:
        """
        저장된 모델을 로드합니다.

        Args:
            path: Model file path
        """
        path = Path(path)
        if not path.exists():
            msg = f"Model file not found: {path}"
            raise FileNotFoundError(msg)

        self.model = lgb.Booster(model_file=str(path))


def generate_labels_from_returns(
    df: pd.DataFrame, threshold: float = 0.02, mode: str = "binary"
) -> pd.Series:
    """
    미래 수익률을 기반으로 매매 신호를 생성합니다.

    Args:
        df: OHLCV 데이터프레임
        threshold: Buy/sell threshold (default: 2% = 0.02)
        mode: 'binary' (buy=1, else=0) or 'multiclass' (buy=2, hold=1, sell=0)

    Returns:
        Signal series (0/1 or 0/1/2)

    Example:
        >>> df['signal'] = generate_labels_from_returns(df, threshold=0.02)
    """
    # Calculate next day return
    df = df.copy()
    df["next_return"] = df["close"].pct_change().shift(-1)

    if mode == "binary":
        # Buy if next return > threshold, else hold/sell
        signals = (df["next_return"] > threshold).astype(int)
    else:
        # Multiclass: buy(2), hold(1), sell(0)
        signals = pd.Series(1, index=df.index)  # Default: hold
        signals[df["next_return"] > threshold] = 2  # Buy
        signals[df["next_return"] < -threshold] = 0  # Sell

    return signals
