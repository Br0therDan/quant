"""
ML Model Training API - Phase 3.2 ML Integration

Endpoints for training, evaluating, and managing ML models.
"""

import asyncio
import logging
from pathlib import Path

import pandas as pd
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

from app.services.database_manager import DatabaseManager
from app.services.ml_platform.infrastructure import (
    MLModelTrainer,
    ModelRegistry,
    generate_labels_from_returns,
)
from app.services.service_factory import service_factory

logger = logging.getLogger(__name__)

router = APIRouter()


# ==================== Request/Response Models ====================


class TrainModelRequest(BaseModel):
    """Request schema for model training."""

    symbols: list[str] = Field(
        ...,
        description="List of stock symbols to train on",
        min_length=1,
        max_length=100,
    )
    lookback_days: int = Field(
        default=500,
        description="Number of days of historical data to use",
        ge=100,
        le=2000,
    )
    test_size: float = Field(default=0.2, description="Test set ratio", ge=0.1, le=0.5)
    num_boost_round: int = Field(
        default=100, description="Number of boosting iterations", ge=10, le=1000
    )
    threshold: float = Field(
        default=0.02,
        description="Return threshold for buy signal (2% = 0.02)",
        ge=0.001,
        le=0.5,
    )


class TrainModelResponse(BaseModel):
    """Response schema for model training."""

    status: str = Field(..., description="Training status")
    message: str = Field(..., description="Status message")
    task_id: str | None = Field(None, description="Background task ID")


class ModelInfoResponse(BaseModel):
    """Response schema for model info."""

    version: str
    model_type: str
    created_at: str
    metrics: dict[str, float]
    feature_count: int
    num_iterations: int
    feature_names: list[str]


class ModelListResponse(BaseModel):
    """Response schema for model list."""

    models: list[ModelInfoResponse]
    total: int
    latest_version: str | None


# ==================== Training Helper ====================


async def _train_model_background(
    symbols: list[str],
    lookback_days: int,
    test_size: float,
    num_boost_round: int,
    threshold: float,
    model_dir: Path,
) -> None:
    """
    Background task for model training.

    Args:
        symbols: List of stock symbols
        lookback_days: Historical data window
        test_size: Test set ratio
        num_boost_round: Boosting iterations
        threshold: Return threshold for labels
        model_dir: Model storage directory
    """
    try:
        logger.info(
            f"Starting model training with {len(symbols)} symbols, "
            f"{lookback_days} days lookback"
        )

        # 1. Load data from DuckDB
        db_manager = service_factory.get_database_manager()
        conn = db_manager.duckdb_conn

        all_data = []
        for symbol in symbols:
            query = """
                SELECT date, open, high, low, close, volume
                FROM daily_prices
                WHERE symbol = ?
                ORDER BY date DESC
                LIMIT ?
            """
            df = await asyncio.to_thread(
                conn.execute(query, [symbol, lookback_days + 50]).fetch_df
            )

            if not df.empty:
                df["date"] = pd.to_datetime(df["date"])
                df = df.sort_values("date").set_index("date")
                df = df[df["close"].notna()]

                if len(df) >= 100:  # Minimum data requirement
                    all_data.append(df)
                    logger.info(f"Loaded {len(df)} rows for {symbol}")
                else:
                    logger.warning(f"Insufficient data for {symbol}: {len(df)} rows")

        if not all_data:
            logger.error("No valid data loaded for training")
            return

        # 2. Combine all symbol data
        combined_df = pd.concat(all_data, ignore_index=False)
        logger.info(f"Combined dataset: {len(combined_df)} rows")

        # 3. Generate labels (buy/hold signals)
        combined_df["signal"] = generate_labels_from_returns(
            combined_df, threshold=threshold, mode="binary"
        )

        logger.info(f"Signal distribution:\n{combined_df['signal'].value_counts()}")

        # 4. Initialize trainer
        trainer = MLModelTrainer(task="binary", test_size=test_size, random_state=42)

        # 5. Prepare data (feature engineering + split)
        X_train, X_test, y_train, y_test = trainer.prepare_data(
            combined_df, target_column="signal"
        )

        logger.info(
            f"Training set: {X_train.shape[0]} samples, " f"{X_train.shape[1]} features"
        )
        logger.info(f"Test set: {X_test.shape[0]} samples")

        # 6. Train model
        logger.info("Training LightGBM model...")
        _ = trainer.train(
            X_train,
            y_train,
            num_boost_round=num_boost_round,
            early_stopping_rounds=10,
        )

        logger.info(
            f"Training completed! Best iteration: "
            f"{trainer.model.best_iteration if trainer.model else 'N/A'}"  # type: ignore
        )

        # 7. Evaluate model
        metrics = trainer.evaluate(X_test, y_test)
        logger.info(f"Model accuracy: {metrics['accuracy']:.4f}")

        # 8. Save model to registry
        registry = ModelRegistry(base_dir=model_dir)
        version = registry.save_model(
            model=trainer.model,  # type: ignore
            model_type="signal",
            metrics=metrics,
            feature_names=trainer.feature_names,
            training_params={
                "symbols": symbols,
                "lookback_days": lookback_days,
                "test_size": test_size,
                "num_boost_round": num_boost_round,
                "threshold": threshold,
            },
        )

        logger.info(f"Model saved as {version} with accuracy {metrics['accuracy']:.4f}")

        # 9. Log feature importance
        importance = trainer.get_feature_importance(top_n=10)
        logger.info(f"Top 10 features:\n{importance.to_string(index=False)}")

    except Exception as e:
        logger.error(f"Model training failed: {e}", exc_info=True)
        raise


# ==================== API Endpoints ====================


@router.post("/train", response_model=TrainModelResponse)
async def train_model(
    request: TrainModelRequest, background_tasks: BackgroundTasks
) -> TrainModelResponse:
    """
    Train a new ML model for signal prediction.

    This endpoint trains a LightGBM model on historical price data
    and saves it to the model registry. Training runs in the background.

    **Training Process:**
    1. Load historical data for specified symbols
    2. Calculate technical indicators (RSI, MACD, etc.)
    3. Generate buy/hold labels based on future returns
    4. Train LightGBM classifier
    5. Evaluate on test set
    6. Save to model registry with versioning

    **Example:**
    ```json
    {
        "symbols": ["AAPL", "MSFT", "GOOGL"],
        "lookback_days": 500,
        "test_size": 0.2,
        "num_boost_round": 100,
        "threshold": 0.02
    }
    ```
    """
    try:
        # Validate symbols exist in database
        db_manager: DatabaseManager = service_factory.get_database_manager()
        conn = db_manager.duckdb_conn

        for symbol in request.symbols:
            result = conn.execute(
                "SELECT COUNT(*) as cnt FROM daily_prices WHERE symbol = ?",
                [symbol],
            ).fetchone()

            if result[0] == 0:  # type: ignore
                raise HTTPException(
                    status_code=404,
                    detail=f"No data found for symbol: {symbol}",
                )

        # Schedule background training
        model_dir = Path("app/data/models")
        background_tasks.add_task(
            _train_model_background,
            symbols=request.symbols,
            lookback_days=request.lookback_days,
            test_size=request.test_size,
            num_boost_round=request.num_boost_round,
            threshold=request.threshold,
            model_dir=model_dir,
        )

        return TrainModelResponse(
            status="started",
            message=f"Training started for {len(request.symbols)} symbols. "
            f"Check logs for progress.",
            task_id=None,  # TODO: Implement task tracking
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start training: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/models", response_model=ModelListResponse)
async def list_models(model_type: str = "signal") -> ModelListResponse:
    """
    List all trained models.

    Returns a list of all models with their metadata including
    version, accuracy, creation date, and feature information.
    """
    try:
        registry = ModelRegistry(base_dir="app/data/models")
        models_data = registry.list_models(model_type=model_type)
        latest = registry.get_latest_version(model_type=model_type)

        models = [
            ModelInfoResponse(
                version=m["version"],
                model_type=m["model_type"],
                created_at=m["created_at"],
                metrics=m["metrics"],
                feature_count=m["feature_count"],
                num_iterations=m["num_iterations"],
                feature_names=m.get("feature_names", []),
            )
            for m in models_data
        ]

        return ModelListResponse(
            models=models, total=len(models), latest_version=latest
        )

    except Exception as e:
        logger.error(f"Failed to list models: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/models/{version}", response_model=ModelInfoResponse)
async def get_model_info(version: str) -> ModelInfoResponse:
    """
    Get detailed information about a specific model version.

    Returns metadata including accuracy, training parameters,
    feature names, and creation date.
    """
    try:
        registry = ModelRegistry(base_dir="app/data/models")
        info = registry.get_model_info(version)

        return ModelInfoResponse(
            version=info["version"],
            model_type=info["model_type"],
            created_at=info["created_at"],
            metrics=info["metrics"],
            feature_count=info["feature_count"],
            num_iterations=info["num_iterations"],
            feature_names=info.get("feature_names", []),
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Failed to get model info: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete("/models/{version}")
async def delete_model(version: str) -> dict[str, str]:
    """
    Delete a specific model version.

    **Warning:** This action cannot be undone.
    """
    try:
        registry = ModelRegistry(base_dir="app/data/models")
        registry.delete_model(version)

        return {
            "status": "success",
            "message": f"Model {version} deleted successfully",
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Failed to delete model: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/models/compare/{metric}")
async def compare_models(
    metric: str = "accuracy",
    versions: str = "",  # Comma-separated versions
) -> dict[str, float]:
    """
    Compare multiple model versions by a specific metric.

    **Supported metrics:**
    - accuracy
    - precision
    - recall
    - f1_score

    **Example:**
    ```
    GET /api/v1/ml/models/compare/accuracy?versions=v1,v2,v3
    ```
    """
    try:
        if not versions:
            raise HTTPException(status_code=400, detail="No versions specified")

        version_list = [v.strip() for v in versions.split(",")]
        registry = ModelRegistry(base_dir="app/data/models")
        comparison = registry.compare_models(version_list, metric=metric)

        return comparison

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to compare models: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e
