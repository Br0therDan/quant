"""
ML Services - Phase 3.2 ML Integration

Machine Learning components for quantitative trading:
- FeatureEngineer: Technical indicator calculation
- MLModelTrainer: LightGBM model training
- ModelRegistry: Model versioning and management
"""

from .anomaly_detector import AnomalyDetectionService, AnomalyResult
from .feature_engineer import FeatureEngineer
from .model_registry import ModelRegistry
from .trainer import (
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
