"""
Backtest Orchestrator - Base Module
Circuit Breaker 패턴 (장애 격리)
"""

import logging
from datetime import datetime
from typing import Optional, Any, Callable


logger = logging.getLogger(__name__)


class CircuitBreaker:
    """Circuit Breaker 패턴 구현 (Phase 3.3 선행)

    장애 격리 패턴: 외부 서비스(Alpha Vantage API) 장애 시 시스템 전체 다운 방지

    동작 방식:
    - CLOSED: 정상 동작 (모든 요청 통과)
    - OPEN: 장애 감지 (모든 요청 차단, {timeout}초 대기)
    - HALF_OPEN: 복구 시도 (1개 요청만 허용하여 테스트)

    Phase 2에 포함한 이유:
    - Alpha Vantage API는 5 calls/min 제한이 있어 장애 발생 가능성 높음
    - 초기부터 안정성 확보 필요

    Attributes:
        failure_threshold: 실패 임계값 (이 횟수 이상 실패 시 OPEN 상태로 전환)
        timeout: OPEN 상태 유지 시간 (초)
        failure_count: 현재 실패 횟수
        last_failure_time: 마지막 실패 시각
        state: 현재 상태 (CLOSED, OPEN, HALF_OPEN)
    """

    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        """Circuit Breaker 초기화

        Args:
            failure_threshold: 실패 임계값 (기본: 5회)
            timeout: OPEN 상태 유지 시간 (기본: 60초)
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    async def call(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        """Circuit Breaker를 통한 비동기 함수 호출

        Args:
            func: 호출할 비동기 함수
            *args: 위치 인수
            **kwargs: 키워드 인수

        Returns:
            함수 실행 결과

        Raises:
            Exception: OPEN 상태에서 호출 시 또는 함수 실행 실패 시
        """
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
                logger.info("Circuit Breaker: OPEN -> HALF_OPEN (attempting reset)")
            else:
                raise Exception(
                    f"Circuit Breaker OPEN: {self.failure_count} failures, "
                    f"retry after {self.timeout}s"
                )

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """리셋 시도 가능 여부 확인

        Returns:
            리셋 시도 가능 여부 (timeout 시간이 경과했는지)
        """
        if self.last_failure_time is None:
            return True
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.timeout

    def _on_success(self) -> None:
        """성공 시 처리

        HALF_OPEN 상태에서 성공하면 CLOSED로 전환하고 실패 카운트 초기화
        """
        if self.state == "HALF_OPEN":
            logger.info("Circuit Breaker: HALF_OPEN -> CLOSED (reset successful)")
        self.failure_count = 0
        self.state = "CLOSED"

    def _on_failure(self) -> None:
        """실패 시 처리

        실패 카운트 증가 및 임계값 도달 시 OPEN 상태로 전환
        """
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.error(
                f"Circuit Breaker: CLOSED -> OPEN "
                f"({self.failure_count} failures reached threshold)"
            )
