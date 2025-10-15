from datetime import datetime, timedelta

import numpy as np

from app.models.data_quality import SeverityLevel
from app.services.ml_platform.infrastructure.anomaly_detector import (
    AnomalyDetectionService,
)


def test_anomaly_detector_flags_terminal_spike() -> None:
    """The detector should escalate large terminal spikes to high severity."""

    detector = AnomalyDetectionService(contamination=0.1, min_history=40)
    start = datetime(2024, 1, 1)

    rng = np.random.default_rng(seed=42)
    base_price = 100.0
    base_volume = 1_000.0
    records = []

    for i in range(60):
        base_price = max(10.0, base_price + float(rng.normal(0, 0.5)))
        base_volume = max(10.0, base_volume + float(rng.normal(0, 25)))

        if i == 59:
            base_price *= 1.25
            base_volume *= 5

        records.append(
            {
                "symbol": "AAPL",
                "date": start + timedelta(days=i),
                "close": base_price,
                "volume": base_volume,
            }
        )

    results = detector.score_daily_prices("AAPL", records)
    terminal_result = results[records[-1]["date"]]

    assert terminal_result.severity in {
        SeverityLevel.HIGH,
        SeverityLevel.CRITICAL,
    }
    assert terminal_result.iso_score >= 0.4 or terminal_result.price_change_pct >= 5
