# Phase 2.1d: Orchestrator.py 모듈 분할 계획

## 현황 분석

- **파일**: `backend/app/services/backtest/orchestrator.py`
- **크기**: 608 라인
- **클래스**: 2개 (CircuitBreaker, BacktestOrchestrator)
- **메서드**: 10개 (public 1개, private 5개 + CircuitBreaker 5개)

## 분할 전략: 기능별 모듈화 (5 files)

### 1. `base.py` (60 라인)
**책임**: Circuit Breaker 패턴 (장애 격리)

```python
class CircuitBreaker:
    """Circuit Breaker 패턴 구현 (Phase 3.3 선행)
    
    장애 격리: Alpha Vantage API 장애 시 시스템 전체 다운 방지
    상태: CLOSED (정상) → OPEN (차단) → HALF_OPEN (복구 시도)
    """
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60)
    async def call(self, func, *args, **kwargs)
    def _should_attempt_reset(self) -> bool
    def _on_success(self)
    def _on_failure(self)
```

**의존성**:
- `datetime`
- `logging`

---

### 2. `initialization.py` (~80 라인)
**책임**: 백테스트 초기화 및 종료 처리

**메서드**:
- `_init_execution()` - BacktestExecution 생성 및 상태 업데이트 (18 라인)
- `_complete()` - 백테스트 완료 처리 (19 라인)
- `_fail()` - 백테스트 실패 처리 (23 라인)

**클래스 구조**:
```python
class BacktestInitializer:
    """백테스트 초기화 및 종료 처리"""
    
    async def init_execution(
        self, backtest: Backtest, execution_id: str
    ) -> BacktestExecution:
        """백테스트 실행 초기화"""
        
    async def complete(
        self,
        backtest: Backtest,
        execution: BacktestExecution,
        performance: PerformanceMetrics,
    ) -> None:
        """백테스트 완료 처리"""
        
    async def fail(
        self,
        backtest: Optional[Backtest],
        execution: Optional[BacktestExecution],
        error_message: str,
    ) -> None:
        """백테스트 실패 처리"""
```

**의존성**:
- `app.models.trading.backtest` (Backtest, BacktestExecution, BacktestStatus, PerformanceMetrics)
- `datetime`, `uuid`

---

### 3. `data_collection.py` (~100 라인)
**책임**: 병렬 데이터 수집 (Phase 3.2 선행 기능)

**메서드**:
- `_collect_data()` - asyncio.gather 병렬 수집 (60 라인)

**클래스 구조**:
```python
class DataCollector:
    """병렬 데이터 수집 (Phase 3.2 선행 구현)
    
    개선 사항:
    - asyncio.gather로 병렬 처리 (10x 성능 향상)
    - Retry 로직 (일시적 네트워크 오류 대응)
    - Circuit Breaker 적용 (장애 격리)
    """
    
    def __init__(
        self,
        market_data_service: MarketDataService,
        circuit_breaker: CircuitBreaker,
    ):
        self.market_data_service = market_data_service
        self.circuit_breaker = circuit_breaker
    
    async def collect_data(
        self, symbols: list[str], start_date: Any, end_date: Any
    ) -> dict:
        """병렬 데이터 수집 with Retry + Circuit Breaker"""
```

**의존성**:
- `asyncio`
- `tenacity` (retry, stop_after_attempt, wait_exponential 등)
- `MarketDataService`
- `CircuitBreaker`

---

### 4. `simulation.py` (~60 라인)
**책임**: 백테스트 시뮬레이션 실행

**메서드**:
- `_simulate()` - TradeEngine으로 신호 실행 (32 라인)

**클래스 구조**:
```python
class SimulationRunner:
    """백테스트 시뮬레이션 실행"""
    
    def simulate(
        self, backtest: Backtest, signals: list[dict[str, Any]]
    ) -> tuple[list, list[float]]:
        """TradeEngine으로 신호 실행 → 거래 + 포트폴리오 값 반환"""
```

**의존성**:
- `app.services.backtest.trade_engine.TradeEngine`
- `app.models.trading.backtest.Backtest`

---

### 5. `result_storage.py` (~120 라인)
**책임**: 백테스트 결과 저장 (MongoDB + DuckDB)

**메서드**:
- `_save_results()` - BacktestResult 저장 + DuckDB 저장 (109 라인)

**클래스 구조**:
```python
class ResultStorage:
    """백테스트 결과 저장 (MongoDB + DuckDB)
    
    저장 위치:
    1. MongoDB: 메타데이터 및 성과 지표
    2. DuckDB: 포트폴리오 히스토리, 거래 내역 (Phase 3.2 선행)
    """
    
    def __init__(self, database_manager: DatabaseManager):
        self.database_manager = database_manager
    
    async def save_results(
        self,
        backtest: Backtest,
        execution: BacktestExecution,
        performance: PerformanceMetrics,
        trades: list,
        portfolio_values: list[float],
    ) -> BacktestResult:
        """결과를 MongoDB + DuckDB에 저장"""
```

**의존성**:
- `app.models.trading.backtest` (Backtest, BacktestExecution, BacktestResult, PerformanceMetrics)
- `DatabaseManager`
- `datetime`

---

### 6. `__init__.py` (~250 라인 예상)
**책임**: 통합 BacktestOrchestrator (Delegation 패턴)

**구조**:
```python
class BacktestOrchestrator:
    """백테스트 워크플로우 조율자
    
    Phase 2 구현: 레이어드 아키텍처 + Orchestrator 패턴
    Phase 3 선행 기능: 병렬 데이터 수집, Circuit Breaker, 모니터링, DuckDB 저장
    """
    
    def __init__(
        self,
        market_data_service: MarketDataService,
        strategy_service: StrategyService,
        database_manager: DatabaseManager,
        ml_signal_service: MLSignalService | None = None,
    ):
        super().__init__()
        
        # Phase 2 핵심 컴포넌트
        self.data_processor = DataProcessor()
        self.strategy_executor = StrategyExecutor(strategy_service)
        self.performance_analyzer = PerformanceAnalyzer()
        
        # Phase 3 선행 구현: Circuit Breaker
        self.circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60)
        
        # 모듈 인스턴스 생성 (Delegation)
        self._initializer = BacktestInitializer()
        self._data_collector = DataCollector(market_data_service, self.circuit_breaker)
        self._simulator = SimulationRunner()
        self._storage = ResultStorage(database_manager)
        
        # Phase 3 선행 구현: 모니터링
        self.metrics = get_global_metrics()
    
    async def execute_backtest(self, backtest_id: str) -> Optional[BacktestResult]:
        """백테스트 실행 (메인 워크플로우)
        
        1. 초기화: _initializer.init_execution()
        2. 데이터 수집: _data_collector.collect_data() (병렬)
        3. 데이터 전처리: data_processor.process_market_data()
        4. 신호 생성: strategy_executor.generate_signals()
        5. 시뮬레이션: _simulator.simulate()
        6. 성과 분석: performance_analyzer.calculate_metrics()
        7. 결과 저장: _storage.save_results()
        8. 완료/실패: _initializer.complete() or _initializer.fail()
        """
        # 기존 execute_backtest() 로직 유지 (160 라인)
        # 각 단계는 위임된 모듈로 처리
```

---

## 최종 파일 구조

```
backend/app/services/backtest/orchestrator/
├── __init__.py           (250 lines) - BacktestOrchestrator 통합
├── base.py               (60 lines)  - CircuitBreaker
├── initialization.py     (80 lines)  - BacktestInitializer
├── data_collection.py    (100 lines) - DataCollector (병렬 수집)
├── simulation.py         (60 lines)  - SimulationRunner
└── result_storage.py     (120 lines) - ResultStorage (MongoDB + DuckDB)
-----------------------------------------------------------
Total:                    670 lines (vs. 원본 608 lines, +10% for clarity)
```

---

## 장점 분석

### 1. 단일 책임 원칙 (SRP)
- **base.py**: Circuit Breaker 패턴만 담당
- **initialization.py**: 초기화/종료 로직만 담당
- **data_collection.py**: 병렬 데이터 수집만 담당
- **simulation.py**: 시뮬레이션 실행만 담당
- **result_storage.py**: 결과 저장만 담당

### 2. 테스트 용이성
```python
# Circuit Breaker 단위 테스트
from app.services.backtest.orchestrator.base import CircuitBreaker
breaker = CircuitBreaker(failure_threshold=3, timeout=30)
# 실패 시나리오 테스트 가능

# 데이터 수집 단위 테스트
from app.services.backtest.orchestrator.data_collection import DataCollector
collector = DataCollector(mock_market_data, mock_breaker)
data = await collector.collect_data(["AAPL", "MSFT"], start, end)
assert len(data) == 2
```

### 3. 확장성
- 새로운 데이터 소스 추가 시 `data_collection.py`만 수정
- 결과 저장 포맷 변경 시 `result_storage.py`만 수정
- Circuit Breaker 전략 변경 시 `base.py`만 수정

### 4. 기존 API 호환성 유지
```python
# ✅ 기존 코드 그대로 작동
from app.services.service_factory import service_factory
orchestrator = service_factory.get_backtest_orchestrator()
result = await orchestrator.execute_backtest(backtest_id)
```

---

## 구현 순서 (Phase 2.1d)

1. **Step 1**: `base.py` 생성 (CircuitBreaker 클래스)
2. **Step 2**: `initialization.py` 생성 (BacktestInitializer)
3. **Step 3**: `data_collection.py` 생성 (DataCollector)
4. **Step 4**: `simulation.py` 생성 (SimulationRunner)
5. **Step 5**: `result_storage.py` 생성 (ResultStorage)
6. **Step 6**: `__init__.py` 생성 (전체 위임 로직)
7. **Step 7**: `orchestrator.py` → `orchestrator_legacy.py` 백업
8. **Step 8**: Import 검증 (get_errors)
9. **Step 9**: OpenAPI 클라이언트 재생성 (`pnpm gen:client`)
10. **Step 10**: Git commit (Phase 2.1d 완료)

---

## 잠재적 이슈 및 해결책

### Issue 1: CircuitBreaker 공유 인스턴스
**문제**: DataCollector가 CircuitBreaker 인스턴스를 받아야 하는데, 순환 의존성 발생 가능

**해결책**:
```python
# __init__.py
class BacktestOrchestrator:
    def __init__(self, ...):
        # Circuit Breaker를 먼저 생성
        self.circuit_breaker = CircuitBreaker()
        
        # DataCollector에 주입
        self._data_collector = DataCollector(
            market_data_service, 
            self.circuit_breaker  # 공유 인스턴스
        )
```

### Issue 2: 모니터링 메트릭 접근
**문제**: 각 모듈에서 self.metrics 접근 필요

**해결책**:
```python
# 전역 metrics는 __init__.py에서만 사용
# 서브 모듈은 메트릭 없이 순수 로직만 처리
# 필요 시 메트릭을 파라미터로 전달
```

### Issue 3: TYPE_CHECKING import
**문제**: MarketDataService 등 타입 힌트용 import가 순환 의존성 유발 가능

**해결책**:
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.services.market_data import MarketDataService
    from app.services.trading.strategy_service import StrategyService
```

---

## 성공 기준

- ✅ 608 라인 → 6개 파일 (평균 112 라인)
- ✅ 각 파일이 단일 책임 원칙 준수
- ✅ 기존 API 엔드포인트 호환성 유지
- ✅ 타입 에러 0개 (mypy 검증)
- ✅ OpenAPI 클라이언트 생성 성공
- ✅ Git commit 성공

---

## 참고 문서

- Phase 2.1a 완료: `docs/backend/module_classification/PHASE2.1A_COMPLETION.md`
- Phase 2.1b 완료: `docs/backend/module_classification/PHASE2.1B_COMPLETION.md`
- Phase 2.1c 완료 (intelligence): commit `70b6d7f`
- Stock 모듈 패턴: `backend/app/services/market_data/stock/__init__.py`
