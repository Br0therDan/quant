"""
백테스트 모니터링 및 메트릭 수집 (P3.4)

구조화 로깅과 성능 메트릭 수집
"""

import time
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from collections import defaultdict
import structlog

# 구조화 로거 설정
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


class BacktestMetrics:
    """백테스트 메트릭 수집기 (P3.4)"""

    def __init__(self):
        self.metrics: Dict[str, Any] = defaultdict(lambda: defaultdict(int))
        self.timers: Dict[str, float] = {}

    def increment(
        self, metric_name: str, value: int = 1, labels: Dict[str, str] | None = None
    ):
        """카운터 메트릭 증가"""
        key = self._build_key(metric_name, labels)
        self.metrics["counters"][key] += value
        logger.info(
            "metric_incremented",
            metric=metric_name,
            value=value,
            labels=labels,
            total=self.metrics["counters"][key],
        )

    def record_value(
        self, metric_name: str, value: float, labels: Dict[str, str] | None = None
    ):
        """값 기록 (gauge)"""
        key = self._build_key(metric_name, labels)
        self.metrics["gauges"][key] = value
        logger.info(
            "metric_recorded",
            metric=metric_name,
            value=value,
            labels=labels,
        )

    def start_timer(self, timer_name: str):
        """타이머 시작"""
        self.timers[timer_name] = time.time()
        logger.debug("timer_started", timer=timer_name)

    def stop_timer(
        self, timer_name: str, labels: Dict[str, str] | None = None
    ) -> float:
        """타이머 종료 및 기록"""
        if timer_name not in self.timers:
            logger.warning("timer_not_found", timer=timer_name)
            return 0.0

        start_time = self.timers[timer_name]
        elapsed = time.time() - start_time
        del self.timers[timer_name]

        key = self._build_key(f"{timer_name}_duration", labels)
        if key not in self.metrics["histograms"]:
            self.metrics["histograms"][key] = []
        self.metrics["histograms"][key].append(elapsed)

        logger.info(
            "timer_stopped",
            timer=timer_name,
            duration_seconds=elapsed,
            labels=labels,
        )
        return elapsed

    def get_metrics(self) -> Dict[str, Any]:
        """모든 메트릭 조회"""
        return dict(self.metrics)

    def reset(self):
        """메트릭 초기화"""
        self.metrics.clear()
        self.timers.clear()
        logger.info("metrics_reset")

    def _build_key(self, metric_name: str, labels: Dict[str, str] | None) -> str:
        """메트릭 키 생성"""
        if not labels:
            return metric_name
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{metric_name}{{{label_str}}}"


class BacktestMonitor:
    """백테스트 모니터링 컨텍스트 매니저 (P3.4)"""

    def __init__(
        self,
        backtest_id: str,
        operation: str,
        metrics_collector: Optional[BacktestMetrics] = None,
    ):
        self.backtest_id = backtest_id
        self.operation = operation
        self.metrics = metrics_collector or BacktestMetrics()
        self.start_time: Optional[float] = None
        self.logger = structlog.get_logger(__name__)

    def __enter__(self):
        """모니터링 시작"""
        self.start_time = time.time()
        self.logger.info(
            "operation_started",
            backtest_id=self.backtest_id,
            operation=self.operation,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self.metrics.increment(
            "backtest_operations_total",
            labels={"operation": self.operation, "status": "started"},
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """모니터링 종료"""
        if self.start_time is None:
            return

        duration = time.time() - self.start_time
        status = "failed" if exc_type else "success"

        self.logger.info(
            "operation_completed",
            backtest_id=self.backtest_id,
            operation=self.operation,
            duration_seconds=duration,
            status=status,
            error=str(exc_val) if exc_val else None,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        self.metrics.increment(
            "backtest_operations_total",
            labels={"operation": self.operation, "status": status},
        )
        self.metrics.record_value(
            "backtest_operation_duration_seconds",
            duration,
            labels={"operation": self.operation},
        )

        # 에러 발생 시 에러 카운트
        if exc_type:
            self.metrics.increment(
                "backtest_errors_total",
                labels={
                    "operation": self.operation,
                    "error_type": exc_type.__name__,
                },
            )


# 전역 메트릭 수집기
_global_metrics = BacktestMetrics()


def get_global_metrics() -> BacktestMetrics:
    """전역 메트릭 수집기 조회"""
    return _global_metrics


def log_backtest_event(
    event: str,
    backtest_id: str,
    **kwargs: Any,
):
    """백테스트 이벤트 로깅 (P3.4)"""
    logger.info(
        event,
        backtest_id=backtest_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
        **kwargs,
    )


def log_error(
    error: Exception,
    backtest_id: str,
    operation: str,
    **kwargs: Any,
):
    """에러 로깅 (P3.4)"""
    logger.error(
        "backtest_error",
        backtest_id=backtest_id,
        operation=operation,
        error_type=type(error).__name__,
        error_message=str(error),
        timestamp=datetime.now(timezone.utc).isoformat(),
        **kwargs,
    )
    _global_metrics.increment(
        "backtest_errors_total",
        labels={
            "operation": operation,
            "error_type": type(error).__name__,
        },
    )
