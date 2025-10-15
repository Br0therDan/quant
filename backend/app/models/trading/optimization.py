"""Optimization study and trial models for Optuna-based parameter tuning."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Dict, Optional

from beanie import Document
from pydantic import Field


class OptimizationStudy(Document):
    """Optuna optimization study metadata stored in MongoDB."""

    study_name: str = Field(..., description="Unique study identifier")
    symbol: str = Field(..., description="Symbol being optimized")
    strategy_name: str = Field(..., description="Strategy template name")

    # Search configuration
    search_space: Dict[str, Dict[str, Any]] = Field(
        ..., description="Parameter search space definition"
    )
    n_trials: int = Field(..., description="Target number of trials")
    direction: str = Field(
        default="maximize", description="Optimization direction (maximize/minimize)"
    )
    sampler: str = Field(default="TPE", description="Optuna sampler algorithm")

    # Execution state
    status: str = Field(
        default="pending",
        description="Study status: pending/running/completed/failed/cancelled",
    )
    started_at: Optional[datetime] = Field(
        default=None, description="Study start timestamp"
    )
    completed_at: Optional[datetime] = Field(
        default=None, description="Study completion timestamp"
    )

    # Results
    best_params: Optional[Dict[str, Any]] = Field(
        default=None, description="Best parameter set found"
    )
    best_value: Optional[float] = Field(
        default=None, description="Best objective value achieved"
    )
    trials_completed: int = Field(default=0, description="Number of completed trials")

    # Context
    backtest_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Backtest configuration (start_date, end_date, etc.)",
    )
    created_by: str = Field(default="system", description="User or system identifier")
    notes: Optional[str] = Field(default=None, description="Study notes or comments")

    # Metadata
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Last update timestamp"
    )

    class Settings:
        name = "optimization_studies"
        indexes = [
            "study_name",
            "symbol",
            "strategy_name",
            "status",
            [("symbol", 1), ("strategy_name", 1), ("created_at", -1)],
            [("status", 1), ("created_at", -1)],
        ]


class OptimizationTrial(Document):
    """Individual optimization trial result."""

    study_name: str = Field(..., description="Parent study identifier")
    trial_number: int = Field(..., description="Trial sequence number within study")

    # Parameters and result
    params: Dict[str, Any] = Field(..., description="Parameter values tested")
    value: float = Field(..., description="Objective function value")
    state: str = Field(
        ..., description="Trial state: COMPLETE/FAIL/PRUNED/RUNNING/WAITING"
    )

    # Backtest reference
    backtest_id: Optional[str] = Field(
        default=None, description="Associated backtest document ID"
    )

    # Performance metrics (for quick filtering)
    sharpe_ratio: Optional[float] = Field(
        default=None, description="Sharpe ratio from backtest"
    )
    total_return: Optional[float] = Field(
        default=None, description="Total return percentage"
    )
    max_drawdown: Optional[float] = Field(
        default=None, description="Maximum drawdown percentage"
    )
    win_rate: Optional[float] = Field(default=None, description="Win rate percentage")

    # Timing
    started_at: datetime = Field(..., description="Trial start timestamp")
    completed_at: Optional[datetime] = Field(
        default=None, description="Trial completion timestamp"
    )
    duration_seconds: Optional[float] = Field(
        default=None, description="Trial execution duration"
    )

    # Metadata
    user_attrs: Dict[str, Any] = Field(
        default_factory=dict, description="User-defined attributes"
    )
    system_attrs: Dict[str, Any] = Field(
        default_factory=dict, description="System-defined attributes"
    )

    class Settings:
        name = "optimization_trials"
        indexes = [
            "study_name",
            "trial_number",
            "state",
            [("study_name", 1), ("trial_number", 1)],
            [("study_name", 1), ("value", -1)],  # Best trials first
            [("study_name", 1), ("state", 1), ("value", -1)],
        ]


__all__ = ["OptimizationStudy", "OptimizationTrial"]
