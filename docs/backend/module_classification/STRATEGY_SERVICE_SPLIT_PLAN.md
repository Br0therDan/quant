# Phase 2.1e: strategy_service.py 모듈 분할 계획

## 현재 상태 분석

**파일**: `backend/app/services/trading/strategy_service.py`
**라인 수**: 527 lines (1 class: StrategyService)

### 메서드 분류 (23개 메서드)

#### 1. Strategy CRUD (6 메서드, ~140 lines)
- `create_strategy()` - 전략 생성
- `get_strategy()` - 전략 조회 (ID)
- `get_strategies()` - 전략 목록 조회 (필터링)
- `update_strategy()` - 전략 업데이트
- `delete_strategy()` - 전략 소프트 삭제
- `_get_default_config()` - 기본 설정 생성 (private)

#### 2. Strategy Execution (3 메서드, ~90 lines)
- `execute_strategy()` - 전략 실행 및 신호 생성
- `get_strategy_executions()` - 실행 이력 조회
- `get_strategy_instance()` - 전략 인스턴스 생성 (타입 안전)

#### 3. Template Management (5 메서드, ~120 lines)
- `create_template()` - 템플릿 생성
- `get_templates()` - 템플릿 목록 조회
- `get_template_by_id()` - 템플릿 조회 (ID)
- `update_template()` - 템플릿 업데이트
- `delete_template()` - 템플릿 삭제
- `create_strategy_from_template()` - 템플릿에서 전략 생성

#### 4. Performance Analysis (2 메서드, ~80 lines)
- `get_strategy_performance()` - 성과 조회
- `calculate_performance_metrics()` - 성과 지표 계산

#### 5. Initialization (1 메서드, ~20 lines)
- `__init__()` - 전략 클래스 매핑 초기화

## 분할 전략

### 원칙
1. **Domain 분리**: CRUD, Execution, Template, Performance 각각 독립 모듈
2. **단일 책임**: 각 모듈은 하나의 책임만 담당
3. **타입 안전성**: 모든 메서드 타입 힌트 유지
4. **기존 API 호환**: ServiceFactory 패턴 유지

### 모듈 구조 (5개 파일)

```
backend/app/services/trading/strategy_service/
├── __init__.py              # StrategyService 통합 클래스 (230 lines)
├── crud.py                  # CRUD 작업 (145 lines)
├── execution.py             # 전략 실행 (100 lines)
├── template_manager.py      # 템플릿 관리 (135 lines)
└── performance.py           # 성과 분석 (90 lines)
```

**Total**: 700 lines (+33% for clarity, 코멘트 및 타입 힌트 강화)

---

## 모듈별 상세 설계

### 1. crud.py (145 lines)
**책임**: Strategy CRUD 작업

```python
"""Strategy CRUD Operations"""

class StrategyCRUD:
    def __init__(self):
        self.settings = get_settings()
    
    async def create_strategy(...) -> Strategy:
        """전략 생성"""
    
    async def get_strategy(strategy_id: str) -> Strategy | None:
        """전략 조회 (ID)"""
    
    async def get_strategies(...) -> list[Strategy]:
        """전략 목록 조회 (필터링)"""
    
    async def update_strategy(...) -> Strategy | None:
        """전략 업데이트"""
    
    async def delete_strategy(strategy_id: str) -> bool:
        """전략 소프트 삭제"""
    
    def _get_default_config(strategy_type: StrategyType) -> StrategyConfigUnion:
        """기본 설정 생성 (private helper)"""
```

**특징**:
- Beanie ODM 기반 CRUD
- 필터링 쿼리 지원 (strategy_type, is_active, is_template, user_id)
- Soft delete 패턴

---

### 2. execution.py (100 lines)
**책임**: 전략 실행 및 신호 생성

```python
"""Strategy Execution and Signal Generation"""

class StrategyExecutor:
    def __init__(self):
        self.settings = get_settings()
        self.strategy_classes = self._initialize_strategy_classes()
    
    def _initialize_strategy_classes(self) -> dict:
        """전략 클래스 매핑 초기화"""
        # BuyAndHoldStrategy, MomentumStrategy, etc.
    
    async def execute_strategy(...) -> StrategyExecution | None:
        """전략 실행 및 신호 생성"""
    
    async def get_executions(...) -> list[StrategyExecution]:
        """실행 이력 조회"""
    
    async def get_strategy_instance(...):
        """타입 안전 전략 인스턴스 생성"""
```

**특징**:
- Strategy class mapping (BuyAndHold, Momentum, RSI, SMA)
- 타입 안전 인스턴스 생성 (Config 타입 검증)
- StrategyExecution 이력 관리

---

### 3. template_manager.py (135 lines)
**책임**: 전략 템플릿 관리

```python
"""Strategy Template Management"""

class TemplateManager:
    def __init__(self):
        self.settings = get_settings()
    
    async def create_template(...) -> StrategyTemplate:
        """템플릿 생성"""
    
    async def get_templates(...) -> list[StrategyTemplate]:
        """템플릿 목록 조회"""
    
    async def get_template_by_id(template_id: str) -> StrategyTemplate | None:
        """템플릿 조회 (ID)"""
    
    async def update_template(...) -> StrategyTemplate | None:
        """템플릿 업데이트"""
    
    async def delete_template(template_id: str) -> bool:
        """템플릿 삭제"""
    
    async def create_strategy_from_template(...) -> Strategy | None:
        """템플릿에서 전략 생성 (usage_count 증가)"""
```

**특징**:
- 템플릿 기반 전략 생성
- Parameter override 지원 (Pydantic model_copy)
- usage_count 추적

---

### 4. performance.py (90 lines)
**책임**: 전략 성과 분석

```python
"""Strategy Performance Analysis"""

class PerformanceAnalyzer:
    def __init__(self):
        self.settings = get_settings()
    
    async def get_performance(strategy_id: str) -> StrategyPerformance | None:
        """성과 조회"""
    
    async def calculate_metrics(strategy_id: str) -> StrategyPerformance | None:
        """성과 지표 계산 및 저장"""
        # - total_signals, buy_signals, sell_signals, hold_signals
        # - avg_signal_strength
        # - start_date, end_date
        # - total_return, win_rate, sharpe_ratio 등 (기본값)
```

**특징**:
- StrategyPerformance 생성/업데이트
- 신호 통계 계산
- 백테스트 성과 메트릭 (추후 확장)

---

### 5. __init__.py (230 lines)
**책임**: Delegation 패턴으로 통합

```python
"""Strategy Service - Main Integration"""

class StrategyService:
    """통합 전략 관리 서비스 (Delegation 패턴)"""
    
    def __init__(self):
        self.settings = get_settings()
        
        # Delegate modules
        self._crud = StrategyCRUD()
        self._executor = StrategyExecutor()
        self._template_manager = TemplateManager()
        self._performance_analyzer = PerformanceAnalyzer()
    
    # CRUD 위임
    async def create_strategy(self, ...) -> Strategy:
        return await self._crud.create_strategy(...)
    
    async def get_strategy(self, strategy_id: str) -> Strategy | None:
        return await self._crud.get_strategy(strategy_id)
    
    async def get_strategies(self, ...) -> list[Strategy]:
        return await self._crud.get_strategies(...)
    
    async def update_strategy(self, ...) -> Strategy | None:
        return await self._crud.update_strategy(...)
    
    async def delete_strategy(self, strategy_id: str) -> bool:
        return await self._crud.delete_strategy(strategy_id)
    
    # Execution 위임
    async def execute_strategy(self, ...) -> StrategyExecution | None:
        return await self._executor.execute_strategy(...)
    
    async def get_strategy_executions(self, ...) -> list[StrategyExecution]:
        return await self._executor.get_executions(...)
    
    async def get_strategy_instance(self, ...):
        return await self._executor.get_strategy_instance(...)
    
    # Template 위임
    async def create_template(self, ...) -> StrategyTemplate:
        return await self._template_manager.create_template(...)
    
    async def get_templates(self, ...) -> list[StrategyTemplate]:
        return await self._template_manager.get_templates(...)
    
    async def get_template_by_id(self, template_id: str) -> StrategyTemplate | None:
        return await self._template_manager.get_template_by_id(template_id)
    
    async def update_template(self, ...) -> StrategyTemplate | None:
        return await self._template_manager.update_template(...)
    
    async def delete_template(self, template_id: str) -> bool:
        return await self._template_manager.delete_template(template_id)
    
    async def create_strategy_from_template(self, ...) -> Strategy | None:
        return await self._template_manager.create_strategy_from_template(...)
    
    # Performance 위임
    async def get_strategy_performance(self, strategy_id: str) -> StrategyPerformance | None:
        return await self._performance_analyzer.get_performance(strategy_id)
    
    async def calculate_performance_metrics(self, strategy_id: str) -> StrategyPerformance | None:
        return await self._performance_analyzer.calculate_metrics(strategy_id)
```

**특징**:
- Delegation 패턴 (Phase 2.1a/b/c/d와 동일)
- 기존 API 100% 호환
- 각 모듈 독립 테스트 가능

---

## 구현 순서

1. **crud.py 생성** (145 lines)
   - StrategyCRUD 클래스
   - 6개 메서드 + _get_default_config

2. **execution.py 생성** (100 lines)
   - StrategyExecutor 클래스
   - Strategy class mapping
   - 3개 메서드 (execute, get_executions, get_instance)

3. **template_manager.py 생성** (135 lines)
   - TemplateManager 클래스
   - 6개 메서드 (CRUD + from_template)

4. **performance.py 생성** (90 lines)
   - PerformanceAnalyzer 클래스
   - 2개 메서드 (get, calculate)

5. **__init__.py 완성** (230 lines)
   - StrategyService 통합 클래스
   - 23개 메서드 위임

6. **검증**
   - get_errors로 타입 에러 확인
   - Import 순환 의존성 검사

7. **레거시 백업**
   - strategy_service.py → strategy_service_legacy.py

8. **OpenAPI 클라이언트 재생성**
   - `pnpm gen:client`

9. **Git commit**
   - Phase 2.1e 완료

---

## 기존 API 호환성

```python
# ✅ 기존 코드 그대로 작동
from app.services.service_factory import service_factory
strategy_service = service_factory.get_strategy_service()

# All existing methods work exactly the same
strategy = await strategy_service.create_strategy(...)
template = await strategy_service.create_template(...)
execution = await strategy_service.execute_strategy(...)
performance = await strategy_service.get_strategy_performance(...)
```

---

## 타입 안전성 강화

- **StrategyConfigUnion**: SMACrossoverConfig | RSIMeanReversionConfig | MomentumConfig | BuyAndHoldConfig
- **get_strategy_instance()**: Config 타입 검증 (TypeError 발생)
- **모든 메서드**: 반환 타입 명시 (Strategy | None, list[Strategy], etc.)

---

## Phase 2.1 완료 후 상태

**Phase 2.1 Progress: 100% Complete (5/5)**

- ✅ Phase 2.1a: technical_indicator.py (1464 → 5 files)
- ✅ Phase 2.1b: stock.py (1241 → 6 files)
- ✅ Phase 2.1c: intelligence.py (1163 → 6 files)
- ✅ Phase 2.1d: orchestrator.py (608 → 6 files)
- 🔄 Phase 2.1e: strategy_service.py (527 → 5 files) ← **현재 작업**

**다음 단계**: Phase 2.2 (ML Platform Domain 모듈화)
