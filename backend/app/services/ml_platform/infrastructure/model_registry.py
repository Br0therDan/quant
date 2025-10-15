"""
Model Registry - Phase 3.2 ML Integration

Manages ML model lifecycle:
- Model versioning (v1, v2, v3, ...)
- Metadata storage (accuracy, training date, features)
- Model save/load operations
- Model history tracking
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import lightgbm as lgb


class ModelRegistry:
    """
    ML 모델 버전 관리 및 저장/로드를 담당합니다.

    Features:
    - Model versioning (automatic v1, v2, ...)
    - Metadata tracking (metrics, training info)
    - Latest model retrieval
    - Model listing and history
    """

    def __init__(self, base_dir: Path | str = "app/data/models"):
        """
        Args:
            base_dir: Base directory for model storage
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.base_dir / "registry.json"
        self.metadata: dict[str, Any] = self._load_metadata()

    def _load_metadata(self) -> dict[str, Any]:
        """메타데이터 파일 로드"""
        if self.metadata_file.exists():
            with open(self.metadata_file) as f:
                return json.load(f)
        return {"models": {}, "latest_version": 0}

    def _save_metadata(self) -> None:
        """메타데이터 파일 저장"""
        with open(self.metadata_file, "w") as f:
            json.dump(self.metadata, indent=2, fp=f)

    def save_model(
        self,
        model: lgb.Booster,
        model_type: str = "signal",
        metrics: dict[str, float] | None = None,
        feature_names: list[str] | None = None,
        training_params: dict[str, Any] | None = None,
    ) -> str:
        """
        새 버전의 모델을 저장합니다.

        Args:
            model: LightGBM Booster object
            model_type: Model type identifier (e.g., 'signal', 'regime')
            metrics: Evaluation metrics (accuracy, f1_score, etc.)
            feature_names: List of feature names
            training_params: Training hyperparameters

        Returns:
            Model version string (e.g., 'v1', 'v2')

        Example:
            >>> registry = ModelRegistry()
            >>> version = registry.save_model(
            ...     model,
            ...     model_type='signal',
            ...     metrics={'accuracy': 0.85, 'f1_score': 0.83}
            ... )
            >>> print(f"Saved as {version}")
        """
        # Generate new version
        version_num = self.metadata["latest_version"] + 1
        version = f"v{version_num}"

        # Model filename
        model_filename = f"{model_type}_{version}.txt"
        model_path = self.base_dir / model_filename

        # Save model
        model.save_model(str(model_path))

        # Save metadata
        model_metadata = {
            "version": version,
            "model_type": model_type,
            "filename": model_filename,
            "path": str(model_path),
            "created_at": datetime.now().isoformat(),
            "metrics": metrics or {},
            "feature_names": feature_names or [],
            "training_params": training_params or {},
            "num_iterations": model.num_trees(),
            "feature_count": model.num_feature(),
        }

        # Update registry
        self.metadata["models"][version] = model_metadata
        self.metadata["latest_version"] = version_num

        # Mark as latest for this model type
        self.metadata[f"latest_{model_type}"] = version

        self._save_metadata()

        return version

    def load_model(
        self, version: str | None = None, model_type: str = "signal"
    ) -> tuple[lgb.Booster, dict[str, Any]]:
        """
        특정 버전의 모델을 로드합니다.

        Args:
            version: Model version (e.g., 'v1', 'v2'). If None, loads latest.
            model_type: Model type identifier

        Returns:
            (model, metadata) tuple

        Example:
            >>> registry = ModelRegistry()
            >>> model, metadata = registry.load_model()  # Latest version
            >>> model, metadata = registry.load_model(version='v2')
        """
        # Use latest version if not specified
        if version is None:
            version = self.get_latest_version(model_type)
            if version is None:
                msg = f"No models found for type '{model_type}'"
                raise ValueError(msg)

        # Get model metadata
        if version not in self.metadata["models"]:
            msg = f"Model version '{version}' not found"
            raise ValueError(msg)

        metadata = self.metadata["models"][version]
        model_path = Path(metadata["path"])

        if not model_path.exists():
            msg = f"Model file not found: {model_path}"
            raise FileNotFoundError(msg)

        # Load model
        model = lgb.Booster(model_file=str(model_path))

        return model, metadata

    def get_latest_version(self, model_type: str = "signal") -> str | None:
        """
        특정 모델 타입의 최신 버전을 반환합니다.

        Args:
            model_type: Model type identifier

        Returns:
            Latest version string or None if no models exist
        """
        latest_key = f"latest_{model_type}"
        return self.metadata.get(latest_key)

    def list_models(self, model_type: str | None = None) -> list[dict[str, Any]]:
        """
        저장된 모델 목록을 반환합니다.

        Args:
            model_type: Filter by model type (optional)

        Returns:
            List of model metadata dicts
        """
        models = list(self.metadata["models"].values())

        if model_type:
            models = [m for m in models if m["model_type"] == model_type]

        # Sort by version (descending)
        models.sort(key=lambda x: int(x["version"].replace("v", "")), reverse=True)

        return models

    def get_model_info(self, version: str) -> dict[str, Any]:
        """
        특정 버전의 메타데이터를 반환합니다.

        Args:
            version: Model version

        Returns:
            Model metadata dict
        """
        if version not in self.metadata["models"]:
            msg = f"Model version '{version}' not found"
            raise ValueError(msg)

        return self.metadata["models"][version]

    def delete_model(self, version: str) -> None:
        """
        특정 버전의 모델을 삭제합니다.

        Args:
            version: Model version to delete
        """
        if version not in self.metadata["models"]:
            msg = f"Model version '{version}' not found"
            raise ValueError(msg)

        metadata = self.metadata["models"][version]
        model_path = Path(metadata["path"])

        # Delete model file
        if model_path.exists():
            model_path.unlink()

        # Remove from registry
        del self.metadata["models"][version]
        self._save_metadata()

    def compare_models(
        self, versions: list[str], metric: str = "accuracy"
    ) -> dict[str, float]:
        """
        여러 모델 버전의 성능을 비교합니다.

        Args:
            versions: List of model versions to compare
            metric: Metric name to compare (e.g., 'accuracy', 'f1_score')

        Returns:
            Dict mapping version to metric value

        Example:
            >>> registry = ModelRegistry()
            >>> comparison = registry.compare_models(['v1', 'v2', 'v3'])
            >>> print(comparison)
            {'v1': 0.82, 'v2': 0.85, 'v3': 0.87}
        """
        results = {}
        for version in versions:
            if version not in self.metadata["models"]:
                continue

            metrics = self.metadata["models"][version].get("metrics", {})
            results[version] = metrics.get(metric, 0.0)

        return results

    def get_best_model(
        self, model_type: str = "signal", metric: str = "accuracy"
    ) -> str | None:
        """
        특정 메트릭 기준으로 최고 성능 모델을 반환합니다.

        Args:
            model_type: Model type identifier
            metric: Metric to optimize (e.g., 'accuracy', 'f1_score')

        Returns:
            Best model version or None if no models exist
        """
        models = self.list_models(model_type=model_type)

        if not models:
            return None

        # Find model with highest metric
        best_model = max(
            models,
            key=lambda m: m.get("metrics", {}).get(metric, 0.0),
        )

        return best_model["version"]
