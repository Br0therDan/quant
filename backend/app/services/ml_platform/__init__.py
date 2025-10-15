"""
ML Platform Domain Services

Organized into:
- infrastructure/: Core ML algorithms and engines (Trainer, Feature Engineer, Registry, Anomaly Detection)
- services/: Business-level ML features (Signal Generation, Model Lifecycle, Regime Detection, KPI)
"""

# Infrastructure (formerly ml/)
from .infrastructure import (
    MLModelTrainer,
    generate_labels_from_returns,
    FeatureEngineer,
    ModelRegistry,
    AnomalyDetectionService,
    AnomalyResult,
)

# Services (business features)
from .services import (
    ModelLifecycleService,
    FeatureStoreService,
    MLSignalService,
    EvaluationHarnessService,
    RegimeDetectionService,
    ProbabilisticKPIService,
)

__all__ = [
    # Infrastructure
    "MLModelTrainer",
    "generate_labels_from_returns",
    "FeatureEngineer",
    "ModelRegistry",
    "AnomalyDetectionService",
    "AnomalyResult",
    # Services
    "ModelLifecycleService",
    "FeatureStoreService",
    "MLSignalService",
    "EvaluationHarnessService",
    "RegimeDetectionService",
    "ProbabilisticKPIService",
]
