"""Time-series anomaly detection helpers for the data quality sentinel."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import List, Mapping, MutableMapping, Optional, Sequence

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

from app.models.data_quality import SeverityLevel


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class AnomalyResult:
    """Container describing anomaly metrics for a single timestamp."""

    timestamp: datetime
    iso_score: float
    prophet_score: Optional[float]
    price_change_pct: float
    volume_z_score: float
    severity: SeverityLevel
    anomaly_type: str
    reasons: List[str]


class AnomalyDetectionService:
    """Applies statistical detectors to market data streams."""

    def __init__(
        self,
        contamination: float = 0.05,
        min_history: int = 30,
        prophet_window: int = 14,
    ) -> None:
        self.contamination = contamination
        self.min_history = min_history
        self.prophet_window = prophet_window
        self._prophet_available = self._check_prophet()

    def score_daily_prices(
        self,
        symbol: str,
        prices: Sequence[Mapping[str, object]] | Sequence[object],
    ) -> MutableMapping[datetime, AnomalyResult]:
        """Score a collection of daily prices for anomaly signals."""

        frame = self._to_dataframe(prices)
        if frame.empty or len(frame) < self.min_history:
            logger.debug(
                "Insufficient history for anomaly scoring: %s (%s rows)",
                symbol,
                len(frame),
            )
            return {}

        features = self._build_feature_matrix(frame)
        iso_scores = self._compute_isolation_forest(frame, features)
        prophet_scores = self._compute_prophet_scores(frame)

        results: MutableMapping[datetime, AnomalyResult] = {}
        for idx, row in frame.iterrows():
            iso_score = iso_scores.get(idx, 0.0)
            prophet_score = prophet_scores.get(idx)
            price_change_pct = float(row.get("price_change_pct", 0.0))
            volume_z = float(row.get("volume_z", 0.0))

            severity, anomaly_type, reasons = self._classify(
                iso_score=iso_score,
                prophet_score=prophet_score,
                price_change_pct=price_change_pct,
                volume_z=volume_z,
            )

            results[idx] = AnomalyResult(
                timestamp=idx,
                iso_score=iso_score,
                prophet_score=prophet_score,
                price_change_pct=price_change_pct,
                volume_z_score=volume_z,
                severity=severity,
                anomaly_type=anomaly_type,
                reasons=reasons,
            )

        return results

    def _to_dataframe(
        self, data: Sequence[Mapping[str, object]] | Sequence[object]
    ) -> pd.DataFrame:
        records: List[dict[str, object]] = []
        for item in data:
            if hasattr(item, "model_dump"):
                payload = item.model_dump()
            elif hasattr(item, "dict"):
                payload = item.dict()
            elif isinstance(item, Mapping):
                payload = dict(item)
            else:
                continue

            if "date" not in payload:
                continue

            try:
                close = float(payload.get("close") or payload.get("close_price"))
                volume = float(payload.get("volume", 0) or 0)
            except (TypeError, ValueError):
                continue

            records.append(
                {
                    "date": pd.to_datetime(payload["date"]),
                    "close": close,
                    "volume": volume,
                }
            )

        if not records:
            return pd.DataFrame()

        frame = pd.DataFrame.from_records(records).set_index("date").sort_index()
        frame["close"] = frame["close"].astype(float)
        frame["volume"] = frame["volume"].astype(float)
        frame["price_change_pct"] = frame["close"].pct_change().fillna(0.0) * 100.0

        rolling_volume = frame["volume"].rolling(window=20, min_periods=5)
        volume_mean = rolling_volume.mean()
        volume_std = rolling_volume.std().replace(0, np.nan)
        frame["volume_z"] = ((frame["volume"] - volume_mean) / volume_std).fillna(0.0)

        frame["volatility"] = (
            frame["close"]
            .pct_change()
            .rolling(window=5, min_periods=3)
            .std()
            .fillna(0.0)
        )
        return frame

    def _build_feature_matrix(self, frame: pd.DataFrame) -> np.ndarray:
        feature_cols = ["price_change_pct", "volume_z", "volatility"]
        matrix = frame[feature_cols].fillna(0.0).to_numpy()
        if not np.isfinite(matrix).all():
            matrix = np.nan_to_num(matrix, nan=0.0, posinf=0.0, neginf=0.0)
        return matrix

    def _compute_isolation_forest(
        self, frame: pd.DataFrame, features: np.ndarray
    ) -> Mapping[datetime, float]:
        if len(features) == 0:
            return {}

        forest = IsolationForest(
            contamination=self.contamination,
            random_state=42,
            n_estimators=200,
        )
        forest.fit(features)
        raw_scores = -forest.score_samples(features)
        min_score = float(np.min(raw_scores))
        max_score = float(np.max(raw_scores))
        denom = max(max_score - min_score, 1e-6)
        scaled = (raw_scores - min_score) / denom
        return {
            timestamp: float(score) for timestamp, score in zip(frame.index, scaled)
        }

    def _compute_prophet_scores(
        self, frame: pd.DataFrame
    ) -> Mapping[datetime, Optional[float]]:
        residuals: pd.Series
        if self._prophet_available and len(frame) >= self.min_history:
            try:
                from prophet import Prophet  # type: ignore

                prophet_frame = frame.reset_index()[["date", "close"]]
                prophet_frame.columns = ["ds", "y"]
                model = Prophet(
                    daily_seasonality=False,
                    weekly_seasonality=False,
                    yearly_seasonality=False,
                    seasonality_mode="additive",
                )
                model.fit(prophet_frame)
                forecast = model.predict(prophet_frame[["ds"]])
                residuals = prophet_frame["y"] - forecast["yhat"]
            except Exception as exc:  # pragma: no cover - optional dependency
                logger.debug("Prophet fallback activated: %s", exc)
                residuals = (
                    frame["close"]
                    - frame["close"]
                    .rolling(window=self.prophet_window, min_periods=5)
                    .mean()
                )
        else:
            residuals = (
                frame["close"]
                - frame["close"]
                .rolling(window=self.prophet_window, min_periods=5)
                .mean()
            )

        resid_std = residuals.rolling(window=self.prophet_window, min_periods=5).std()
        resid_std = resid_std.replace(0.0, np.nan)
        z_scores = (residuals / resid_std).fillna(0.0)

        return {
            idx: float(abs(z_scores.iloc[pos])) for pos, idx in enumerate(frame.index)
        }

    def _classify(
        self,
        *,
        iso_score: float,
        prophet_score: Optional[float],
        price_change_pct: float,
        volume_z: float,
    ) -> tuple[SeverityLevel, str, List[str]]:
        prophet_norm = min(abs(prophet_score or 0.0) / 3.0, 1.0)
        price_norm = min(abs(price_change_pct) / 5.0, 1.0)
        volume_norm = min(abs(volume_z) / 5.0, 1.0)

        severity_candidates = {
            "model_residual": prophet_norm,
            "price_jump": price_norm,
            "volume_spike": volume_norm,
            "isolation": iso_score,
        }

        primary_issue = max(severity_candidates, key=severity_candidates.get)
        severity_value = max(severity_candidates.values())

        if severity_value >= 0.85:
            severity = SeverityLevel.CRITICAL
        elif severity_value >= 0.6:
            severity = SeverityLevel.HIGH
        elif severity_value >= 0.4:
            severity = SeverityLevel.MEDIUM
        elif severity_value >= 0.2:
            severity = SeverityLevel.LOW
        else:
            severity = SeverityLevel.NORMAL

        reasons: List[str] = [
            name
            for name, value in severity_candidates.items()
            if value >= 0.4 and name != "isolation"
        ]
        if iso_score >= 0.4:
            reasons.append("isolation")

        return severity, primary_issue, reasons

    def _check_prophet(self) -> bool:
        try:
            import importlib

            importlib.import_module("prophet")
            return True
        except ModuleNotFoundError:
            logger.debug("Prophet not installed; using rolling mean fallback")
            return False


__all__ = ["AnomalyDetectionService", "AnomalyResult"]
