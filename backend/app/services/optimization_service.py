"""Optimization service using Optuna for hyperparameter tuning."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import List, Optional
from uuid import uuid4

import optuna
from optuna.samplers import TPESampler, RandomSampler, CmaEsSampler

from app.models.optimization import OptimizationStudy, OptimizationTrial
from app.schemas.optimization import (
    OptimizationRequest,
    OptimizationProgress,
    OptimizationResult,
    TrialResult,
    StudyListItem,
)

logger = logging.getLogger(__name__)


class OptimizationService:
    """Orchestrates Optuna-based hyperparameter optimization for backtest strategies."""

    def __init__(self, backtest_service, strategy_service):
        """Initialize optimization service with required dependencies.

        Args:
            backtest_service: BacktestService instance for running backtests
            strategy_service: StrategyService instance for strategy management
        """
        self.backtest_service = backtest_service
        self.strategy_service = strategy_service

    async def create_study(self, request: OptimizationRequest) -> str:
        """Create a new optimization study.

        Args:
            request: Optimization configuration

        Returns:
            study_name: Unique study identifier
        """
        # Generate study name if not provided
        study_name = request.study_name or self._generate_study_name(
            request.symbol, request.strategy_name
        )

        # Create study document
        study = OptimizationStudy(
            study_name=study_name,
            symbol=request.symbol,
            strategy_name=request.strategy_name,
            search_space={
                name: space.model_dump() for name, space in request.search_space.items()
            },
            n_trials=request.n_trials,
            direction=request.direction,
            sampler=request.sampler,
            status="pending",
            backtest_config={
                "start_date": request.start_date,
                "end_date": request.end_date,
                "initial_capital": request.initial_capital,
                "objective_metric": request.objective_metric,
            },
            notes=request.notes,
        )

        await study.insert()
        logger.info(f"Created optimization study: {study_name}")

        return study_name

    async def run_study(self, study_name: str) -> OptimizationResult:
        """Execute optimization study using Optuna.

        Args:
            study_name: Study identifier

        Returns:
            OptimizationResult with best parameters and summary
        """
        # Load study document
        study_doc = await OptimizationStudy.find_one(
            OptimizationStudy.study_name == study_name
        )
        if not study_doc:
            raise ValueError(f"Study not found: {study_name}")

        # Update status
        study_doc.status = "running"
        study_doc.started_at = datetime.now(UTC)
        await study_doc.save()

        try:
            # Create Optuna study
            sampler = self._create_sampler(study_doc.sampler)
            direction = "maximize" if study_doc.direction == "maximize" else "minimize"

            optuna_study = optuna.create_study(
                study_name=study_name, direction=direction, sampler=sampler
            )

            # Define objective function
            async def objective(trial: optuna.Trial) -> float:
                return await self._objective_function(trial, study_doc)

            # Run optimization (convert async to sync for Optuna)
            for _ in range(study_doc.n_trials):
                trial = optuna_study.ask()
                value = await objective(trial)
                optuna_study.tell(trial, value)

                # Update progress
                study_doc.trials_completed += 1
                if (
                    study_doc.best_value is None
                    or (direction == "maximize" and value > study_doc.best_value)
                    or (direction == "minimize" and value < study_doc.best_value)
                ):
                    study_doc.best_value = value
                    study_doc.best_params = trial.params
                study_doc.updated_at = datetime.now(UTC)
                await study_doc.save()

            # Mark as completed
            study_doc.status = "completed"
            study_doc.completed_at = datetime.now(UTC)
            await study_doc.save()

            # Get top trials
            top_trials = await self._get_top_trials(study_name, limit=5)

            # Calculate duration
            duration = (study_doc.completed_at - study_doc.started_at).total_seconds()

            # Get best trial details
            best_trial_doc = await OptimizationTrial.find_one(
                OptimizationTrial.study_name == study_name,
                OptimizationTrial.value == study_doc.best_value,
            )

            result = OptimizationResult(
                study_name=study_name,
                symbol=study_doc.symbol,
                strategy_name=study_doc.strategy_name,
                best_params=study_doc.best_params or {},
                best_value=study_doc.best_value or 0.0,
                best_trial_number=best_trial_doc.trial_number if best_trial_doc else 0,
                trials_completed=study_doc.trials_completed,
                n_trials=study_doc.n_trials,
                direction=study_doc.direction,
                objective_metric=study_doc.backtest_config.get(
                    "objective_metric", "sharpe_ratio"
                ),
                sharpe_ratio=best_trial_doc.sharpe_ratio if best_trial_doc else None,
                total_return=best_trial_doc.total_return if best_trial_doc else None,
                max_drawdown=best_trial_doc.max_drawdown if best_trial_doc else None,
                win_rate=best_trial_doc.win_rate if best_trial_doc else None,
                started_at=study_doc.started_at,
                completed_at=study_doc.completed_at,
                total_duration_seconds=duration,
                top_trials=top_trials,
            )

            logger.info(
                f"Optimization study completed: {study_name}, best_value={study_doc.best_value}"
            )

            return result

        except Exception as e:
            study_doc.status = "failed"
            study_doc.completed_at = datetime.now(UTC)
            await study_doc.save()
            logger.error(f"Optimization study failed: {study_name}", exc_info=e)
            raise

    async def get_study_progress(self, study_name: str) -> OptimizationProgress:
        """Get current progress of an optimization study.

        Args:
            study_name: Study identifier

        Returns:
            OptimizationProgress with current status
        """
        study = await OptimizationStudy.find_one(
            OptimizationStudy.study_name == study_name
        )
        if not study:
            raise ValueError(f"Study not found: {study_name}")

        # Get recent trials
        recent_trials = await self._get_recent_trials(study_name, limit=10)

        # Estimate completion time
        estimated_completion = None
        if study.started_at and study.trials_completed > 0:
            elapsed = (datetime.now(UTC) - study.started_at).total_seconds()
            avg_trial_time = elapsed / study.trials_completed
            remaining_trials = study.n_trials - study.trials_completed
            remaining_seconds = avg_trial_time * remaining_trials
            estimated_completion = datetime.now(UTC).timestamp() + remaining_seconds
            estimated_completion = datetime.fromtimestamp(estimated_completion, tz=UTC)

        return OptimizationProgress(
            study_name=study_name,
            status=study.status,
            trials_completed=study.trials_completed,
            n_trials=study.n_trials,
            best_value=study.best_value,
            best_params=study.best_params,
            started_at=study.started_at,
            estimated_completion=estimated_completion,
            recent_trials=recent_trials,
        )

    async def get_study_result(self, study_name: str) -> OptimizationResult:
        """Get final result of a completed optimization study.

        Args:
            study_name: Study identifier

        Returns:
            OptimizationResult with best parameters and summary
        """
        study = await OptimizationStudy.find_one(
            OptimizationStudy.study_name == study_name
        )
        if not study:
            raise ValueError(f"Study not found: {study_name}")

        if study.status != "completed":
            raise ValueError(f"Study not completed yet: {study_name}")

        if not study.completed_at or not study.started_at:
            raise ValueError(f"Study timestamps missing: {study_name}")

        # Get top trials
        top_trials = await self._get_top_trials(study_name, limit=5)

        # Get best trial details
        best_trial = await OptimizationTrial.find_one(
            OptimizationTrial.study_name == study_name,
            OptimizationTrial.value == study.best_value,
        )

        duration = (study.completed_at - study.started_at).total_seconds()

        return OptimizationResult(
            study_name=study_name,
            symbol=study.symbol,
            strategy_name=study.strategy_name,
            best_params=study.best_params or {},
            best_value=study.best_value or 0.0,
            best_trial_number=best_trial.trial_number if best_trial else 0,
            trials_completed=study.trials_completed,
            n_trials=study.n_trials,
            direction=study.direction,
            objective_metric=study.backtest_config.get(
                "objective_metric", "sharpe_ratio"
            ),
            sharpe_ratio=best_trial.sharpe_ratio if best_trial else None,
            total_return=best_trial.total_return if best_trial else None,
            max_drawdown=best_trial.max_drawdown if best_trial else None,
            win_rate=best_trial.win_rate if best_trial else None,
            started_at=study.started_at,
            completed_at=study.completed_at,
            total_duration_seconds=duration,
            top_trials=top_trials,
        )

    async def list_studies(
        self,
        symbol: Optional[str] = None,
        strategy_name: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> List[StudyListItem]:
        """List optimization studies with optional filters.

        Args:
            symbol: Filter by symbol
            strategy_name: Filter by strategy name
            status: Filter by status
            limit: Maximum number of studies to return

        Returns:
            List of StudyListItem summaries
        """
        query = {}
        if symbol:
            query["symbol"] = symbol
        if strategy_name:
            query["strategy_name"] = strategy_name
        if status:
            query["status"] = status

        studies = (
            await OptimizationStudy.find(query)
            .sort("-created_at")
            .limit(limit)
            .to_list()
        )

        return [
            StudyListItem(
                study_name=s.study_name,
                symbol=s.symbol,
                strategy_name=s.strategy_name,
                status=s.status,
                trials_completed=s.trials_completed,
                n_trials=s.n_trials,
                best_value=s.best_value,
                created_at=s.created_at,
                completed_at=s.completed_at,
            )
            for s in studies
        ]

    # Private helper methods

    async def _objective_function(
        self, trial: optuna.Trial, study: OptimizationStudy
    ) -> float:
        """Objective function for Optuna optimization.

        Args:
            trial: Optuna trial object
            study: Study document

        Returns:
            Objective value (e.g., Sharpe ratio)
        """
        # Sample parameters from search space
        params = {}
        for param_name, param_space in study.search_space.items():
            if param_space["type"] == "int":
                params[param_name] = trial.suggest_int(
                    param_name,
                    param_space["low"],
                    param_space["high"],
                    step=param_space.get("step", 1),
                    log=param_space.get("log", False),
                )
            elif param_space["type"] == "float":
                params[param_name] = trial.suggest_float(
                    param_name,
                    param_space["low"],
                    param_space["high"],
                    step=param_space.get("step"),
                    log=param_space.get("log", False),
                )
            elif param_space["type"] == "categorical":
                params[param_name] = trial.suggest_categorical(
                    param_name, param_space["choices"]
                )

        # Record trial start
        trial_doc = OptimizationTrial(
            study_name=study.study_name,
            trial_number=trial.number,
            params=params,
            value=0.0,  # Will be updated after backtest
            state="RUNNING",
            started_at=datetime.now(UTC),
        )
        await trial_doc.insert()

        try:
            # Run backtest with sampled parameters
            backtest_result = await self.backtest_service.run_backtest(
                symbol=study.symbol,
                strategy_name=study.strategy_name,
                params=params,
                start_date=study.backtest_config["start_date"],
                end_date=study.backtest_config["end_date"],
                initial_capital=study.backtest_config.get("initial_capital", 100000.0),
            )

            # Extract objective metric
            objective_metric = study.backtest_config.get(
                "objective_metric", "sharpe_ratio"
            )
            value = getattr(backtest_result.performance_metrics, objective_metric, 0.0)

            # Update trial with results
            trial_doc.value = value
            trial_doc.state = "COMPLETE"
            trial_doc.completed_at = datetime.now(UTC)
            trial_doc.duration_seconds = (
                trial_doc.completed_at - trial_doc.started_at
            ).total_seconds()
            trial_doc.backtest_id = str(backtest_result.id)
            trial_doc.sharpe_ratio = backtest_result.performance_metrics.sharpe_ratio
            trial_doc.total_return = backtest_result.performance_metrics.total_return
            trial_doc.max_drawdown = backtest_result.performance_metrics.max_drawdown
            trial_doc.win_rate = backtest_result.performance_metrics.win_rate
            await trial_doc.save()

            logger.debug(
                f"Trial {trial.number} completed: params={params}, value={value}"
            )

            return value

        except Exception as e:
            trial_doc.state = "FAIL"
            trial_doc.completed_at = datetime.now(UTC)
            await trial_doc.save()
            logger.error(f"Trial {trial.number} failed: {e}", exc_info=e)
            raise

    async def _get_top_trials(
        self, study_name: str, limit: int = 5
    ) -> List[TrialResult]:
        """Get top trials sorted by value."""
        trials = (
            await OptimizationTrial.find(
                OptimizationTrial.study_name == study_name,
                OptimizationTrial.state == "COMPLETE",
            )
            .sort("-value")
            .limit(limit)
            .to_list()
        )

        return [
            TrialResult(
                trial_number=t.trial_number,
                params=t.params,
                value=t.value,
                state=t.state,
                sharpe_ratio=t.sharpe_ratio,
                total_return=t.total_return,
                max_drawdown=t.max_drawdown,
                duration_seconds=t.duration_seconds,
            )
            for t in trials
        ]

    async def _get_recent_trials(
        self, study_name: str, limit: int = 10
    ) -> List[TrialResult]:
        """Get most recent trials."""
        trials = (
            await OptimizationTrial.find(OptimizationTrial.study_name == study_name)
            .sort("-started_at")
            .limit(limit)
            .to_list()
        )

        return [
            TrialResult(
                trial_number=t.trial_number,
                params=t.params,
                value=t.value,
                state=t.state,
                sharpe_ratio=t.sharpe_ratio,
                total_return=t.total_return,
                max_drawdown=t.max_drawdown,
                duration_seconds=t.duration_seconds,
            )
            for t in trials
        ]

    def _create_sampler(self, sampler_name: str) -> optuna.samplers.BaseSampler:
        """Create Optuna sampler from name."""
        samplers = {
            "TPE": TPESampler,
            "Random": RandomSampler,
            "CmaEs": CmaEsSampler,
        }

        sampler_class = samplers.get(sampler_name, TPESampler)
        return sampler_class()

    def _generate_study_name(self, symbol: str, strategy_name: str) -> str:
        """Generate unique study name."""
        timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid4())[:8]
        return f"{symbol}_{strategy_name}_{timestamp}_{unique_id}"


__all__ = ["OptimizationService"]
