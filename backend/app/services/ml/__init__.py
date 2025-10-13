"""
ML Services - Phase 3.2 ML Integration

Machine Learning components for quantitative trading:
- FeatureEngineer: Technical indicator calculation
- MLModelTrainer: LightGBM model training
- ModelRegistry: Model versioning and management
"""

from app.services.ml.anomaly_detector import AnomalyDetectionService, AnomalyResult
from app.services.ml.feature_engineer import FeatureEngineer
from app.services.ml.model_registry import ModelRegistry
from app.services.ml.trainer import (
    MLModelTrainer,
    generate_labels_from_returns,
)

__all__ = [
    "FeatureEngineer",
    "MLModelTrainer",
    "ModelRegistry",
    "generate_labels_from_returns",
    "AnomalyDetectionService",
    "AnomalyResult",
]
