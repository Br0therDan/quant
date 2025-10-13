"""Schemas for optimization-related requests and responses."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ParameterSpace(BaseModel):
    """Search space definition for a single parameter."""

    type: str = Field(..., description="Parameter type: int, float, categorical")
    low: Optional[float] = Field(None, description="Lower bound for numeric types")
    high: Optional[float] = Field(None, description="Upper bound for numeric types")
    step: Optional[float] = Field(None, description="Step size for discrete sampling")
    choices: Optional[List[Any]] = Field(None, description="Choices for categorical")
    log: bool = Field(default=False, description="Use log scale for sampling")


class OptimizationRequest(BaseModel):
    """Request to start a new optimization study."""

    symbol: str = Field(..., description="Symbol to optimize (e.g., AAPL)")
    strategy_name: str = Field(..., description="Strategy template name (e.g., RSI)")
    search_space: Dict[str, ParameterSpace] = Field(
        ..., description="Parameter search space"
    )

    # Optimization settings
    n_trials: int = Field(default=100, ge=1, le=1000, description="Number of trials")
    direction: str = Field(
        default="maximize", description="Optimization direction (maximize/minimize)"
    )
    sampler: str = Field(
        default="TPE", description="Optuna sampler: TPE/Random/Grid/CMA-ES"
    )
    objective_metric: str = Field(
        default="sharpe_ratio",
        description="Metric to optimize: sharpe_ratio/return/...",
    )

    # Backtest configuration
    start_date: str = Field(..., description="Backtest start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="Backtest end date (YYYY-MM-DD)")
    initial_capital: float = Field(default=100000.0, description="Starting capital")

    # Metadata
    study_name: Optional[str] = Field(
        None, description="Custom study name (auto-generated if not provided)"
    )
    notes: Optional[str] = Field(None, description="Study description or notes")


class TrialResult(BaseModel):
    """Individual trial result summary."""

    trial_number: int
    params: Dict[str, Any]
    value: float
    state: str
    sharpe_ratio: Optional[float] = None
    total_return: Optional[float] = None
    max_drawdown: Optional[float] = None
    duration_seconds: Optional[float] = None


class OptimizationProgress(BaseModel):
    """Current optimization study progress."""

    study_name: str
    status: str
    trials_completed: int
    n_trials: int
    best_value: Optional[float] = None
    best_params: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    recent_trials: List[TrialResult] = Field(default_factory=list)


class OptimizationResult(BaseModel):
    """Completed optimization study result."""

    study_name: str
    symbol: str
    strategy_name: str

    # Best result
    best_params: Dict[str, Any]
    best_value: float
    best_trial_number: int

    # Summary statistics
    trials_completed: int
    n_trials: int
    direction: str
    objective_metric: str

    # Performance metrics of best trial
    sharpe_ratio: Optional[float] = None
    total_return: Optional[float] = None
    max_drawdown: Optional[float] = None
    win_rate: Optional[float] = None

    # Timing
    started_at: datetime
    completed_at: datetime
    total_duration_seconds: float

    # Top trials
    top_trials: List[TrialResult] = Field(
        default_factory=list, description="Top 5 trials"
    )


class OptimizationResponse(BaseModel):
    """Response from optimization endpoint."""

    status: str = Field(..., description="success/error")
    study_name: str
    message: str
    data: Optional[OptimizationProgress | OptimizationResult] = None


class StudyListItem(BaseModel):
    """Summary of an optimization study for listing."""

    study_name: str
    symbol: str
    strategy_name: str
    status: str
    trials_completed: int
    n_trials: int
    best_value: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class StudyListResponse(BaseModel):
    """Response for study listing."""

    status: str
    total: int
    studies: List[StudyListItem]


__all__ = [
    "ParameterSpace",
    "OptimizationRequest",
    "TrialResult",
    "OptimizationProgress",
    "OptimizationResult",
    "OptimizationResponse",
    "StudyListItem",
    "StudyListResponse",
]
