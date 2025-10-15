# Phase 2.1 완료 후 레거시 파일 및 중복 서비스 정리 보고서

**분석 날짜**: 2025년 10월 15일  
**대상**: Phase 2.1 완료 후 레거시 파일 3개 및 서비스 중복 확인

---

## 1. 레거시 파일 분석

### 1.1 orchestrator_legacy.py ✅ **제거 가능**

**위치**: `backend/app/services/backtest/orchestrator_legacy.py`

**현황**:

- ✅ 새 모듈로 완전 대체됨: `backend/app/services/backtest/orchestrator/`
- ✅ 코드베이스에서 참조 없음 (검색 결과: 0건)
- ✅ Import 없음: `from.*orchestrator_legacy` 검색 결과 없음

**새 모듈 구조** (Phase 2.1d 완료):

```
orchestrator/
├── __init__.py          # BacktestOrchestrator (282 lines, Delegation 패턴)
├── base.py              # CircuitBreaker (115 lines)
├── initialization.py    # BacktestInitializer (112 lines)
├── data_collection.py   # DataCollector (121 lines)
├── simulation.py        # SimulationRunner (64 lines)
└── result_storage.py    # ResultStorage (156 lines)
```

**실제 사용처**:

```python
# service_factory.py
from .backtest.orchestrator import BacktestOrchestrator  # ✅ 새 모듈 사용

# api/routes/trading/backtests/backtests.py
from app.services.backtest import BacktestOrchestrator  # ✅ 새 모듈 사용
```

**결론**: **즉시 제거 가능** - 완전히 대체됨, 참조 없음

---

### 1.2 intelligence_legacy.py ✅ **제거 가능**

**위치**: `backend/app/services/market_data/intelligence_legacy.py`

**현황**:

- ✅ 새 모듈로 완전 대체됨: `backend/app/services/market_data/intelligence/`
- ✅ 코드베이스에서 참조 없음 (검색 결과: 0건)
- ✅ Import 없음: `from.*intelligence_legacy` 검색 결과 없음

**새 모듈 구조** (Phase 2.1c 완료):

```
intelligence/
├── __init__.py               # IntelligenceService (280 lines)
├── news.py                   # NewsCollector (250 lines)
├── sentiment.py              # SentimentAnalyzer (210 lines)
├── social.py                 # SocialSentimentTracker (180 lines)
├── analyst.py                # AnalystRecommendationCollector (150 lines)
├── market_buzz.py            # MarketBuzzTracker (120 lines)
└── consumer_sentiment.py     # ConsumerSentimentAnalyzer (163 lines)
```

**실제 사용처**:

```python
# service_factory.py
from .market_data.intelligence import IntelligenceService  # ✅ 새 모듈 사용

# market_data/__init__.py
from .intelligence import IntelligenceService  # ✅ 새 모듈 사용
```

**결론**: **즉시 제거 가능** - 완전히 대체됨, 참조 없음

---

### 1.3 strategy_service_legacy.py ✅ **제거 가능**

**위치**: `backend/app/services/trading/strategy_service_legacy.py`

**현황**:

- ✅ 새 모듈로 완전 대체됨: `backend/app/services/trading/strategy_service/`
- ✅ 코드베이스에서 참조 없음 (검색 결과: 0건)
- ✅ Import 없음: `from.*strategy_service_legacy` 검색 결과 없음

**새 모듈 구조** (Phase 2.1e 완료):

```
strategy_service/
├── __init__.py           # StrategyService (260 lines, Delegation)
├── crud.py               # StrategyCRUD (208 lines)
├── execution.py          # StrategyExecutor (202 lines)
├── template_manager.py   # TemplateManager (221 lines)
└── performance.py        # PerformanceAnalyzer (115 lines)
```

**실제 사용처** (9건 모두 새 모듈):

```python
# service_factory.py
from .trading.strategy_service import StrategyService  # ✅

# backtest/executor.py, orchestrator/__init__.py
from app.services.trading.strategy_service import StrategyService  # ✅

# api/routes/trading/strategies/*.py
from app.services.trading.strategy_service import StrategyService  # ✅
```

**결론**: **즉시 제거 가능** - 완전히 대체됨, 참조 없음

---

## 2. 서비스 중복 분석

### 2.1 `services/backtest` vs `services/trading/backtest_service.py`

**분석 결과**: ❌ **중복 아님 - 역할 분리**

#### 2.1.1 `services/backtest/` (실행 엔진)

**책임**: 백테스트 **실행** 로직 (Phase 2 레이어드 아키텍처)

**구성 요소**:

```
backtest/
├── orchestrator/         # 워크플로우 조율 (Phase 2.1d 모듈화 완료)
│   ├── __init__.py      # BacktestOrchestrator
│   ├── base.py          # CircuitBreaker
│   ├── initialization.py
│   ├── data_collection.py
│   ├── simulation.py
│   └── result_storage.py
├── executor.py           # StrategyExecutor (신호 생성)
├── trade_engine.py       # TradeEngine (거래 시뮬레이션)
├── performance.py        # PerformanceAnalyzer (성과 분석)
├── data_processor.py     # DataProcessor (전처리)
└── monitoring.py         # BacktestMonitor (모니터링)
```

**핵심 클래스**:

- `BacktestOrchestrator`: 8단계 워크플로우 조율
- `StrategyExecutor`: 전략 신호 생성
- `TradeEngine`: 거래 실행 시뮬레이션
- `PerformanceAnalyzer`: 성과 지표 계산

**API 엔드포인트**:

```python
# POST /api/v1/trading/backtests/{backtest_id}/execute
async def execute_backtest(
    backtest_id: str,
    orchestrator: BacktestOrchestrator = Depends(get_orchestrator),
):
    return await orchestrator.execute_backtest(backtest_id)
```

---

#### 2.1.2 `services/trading/backtest_service.py` (CRUD 서비스)

**책임**: 백테스트 **CRUD** 작업 (Phase 2 단순화)

**파일**: 217 lines (Phase 2에서 700 → 217 lines 축소)

**핵심 메서드**:

```python
class BacktestService:
    async def create_backtest(...)      # 백테스트 생성
    async def get_backtests(...)        # 목록 조회
    async def get_backtest(...)         # 상세 조회
    async def update_backtest(...)      # 수정
    async def delete_backtest(...)      # 삭제
    async def get_backtest_executions(...)  # 실행 내역 조회
    async def get_backtest_results(...)     # 결과 조회
    async def create_backtest_result(...)   # 결과 생성
```

**특징**:

- ✅ 순수 CRUD (Create, Read, Update, Delete)
- ✅ 실행 로직 없음 (Phase 2에서 제거됨)
- ✅ MongoDB Beanie ODM 사용
- ✅ 기본 전략 자동 생성 (Buy & Hold)

**API 엔드포인트**:

```python
# GET /api/v1/trading/backtests
async def get_backtests(
    service: BacktestService = Depends(get_backtest_service),
):
    return await service.get_backtests()

# POST /api/v1/trading/backtests
async def create_backtest(
    service: BacktestService = Depends(get_backtest_service),
):
    return await service.create_backtest(...)
```

---

#### 2.1.3 역할 분리 (Phase 2 아키텍처)

```
┌─────────────────────────────────────────────────────────┐
│  API Layer                                              │
│  ├── GET/POST /backtests (CRUD)                        │
│  └── POST /backtests/{id}/execute (Execute)            │
└────────────┬─────────────────────┬──────────────────────┘
             │                     │
             ▼                     ▼
┌────────────────────────┐  ┌──────────────────────────┐
│ BacktestService        │  │ BacktestOrchestrator     │
│ (CRUD Only)            │  │ (Execution Engine)       │
│                        │  │                          │
│ - create_backtest      │  │ - execute_backtest       │
│ - get_backtests        │  │   ├── DataCollector     │
│ - update_backtest      │  │   ├── StrategyExecutor  │
│ - delete_backtest      │  │   ├── TradeEngine       │
│ - get_results          │  │   ├── PerformanceAnalyzer│
│                        │  │   └── ResultStorage     │
└────────────────────────┘  └──────────────────────────┘
```

**결론**: **중복 아님** - 명확한 역할 분리 (CRUD vs Execution)

---

## 3. 정리 권고사항

### 3.1 즉시 제거 가능 (3개 파일)

```bash
# 1. orchestrator_legacy.py
rm backend/app/services/backtest/orchestrator_legacy.py

# 2. intelligence_legacy.py
rm backend/app/services/market_data/intelligence_legacy.py

# 3. strategy_service_legacy.py
rm backend/app/services/trading/strategy_service_legacy.py
```

**제거 근거**:

- ✅ 새 모듈로 100% 대체 완료
- ✅ 코드베이스 참조 0건
- ✅ Import 문 없음
- ✅ Phase 2.1a/b/c/d/e 완료로 불필요

---

### 3.2 유지 필요 (역할 분리)

**BacktestService (CRUD)** ← 유지  
**services/backtest/ (Execution)** ← 유지

**이유**:

1. **단일 책임 원칙 (SRP)**

   - BacktestService: 데이터베이스 CRUD만 담당
   - BacktestOrchestrator: 백테스트 실행만 담당

2. **API 설계**

   - CRUD 엔드포인트: `/api/v1/trading/backtests` (목록, 생성, 수정, 삭제)
   - 실행 엔드포인트: `/api/v1/trading/backtests/{id}/execute`

3. **의존성 방향**

   - BacktestOrchestrator는 BacktestService를 사용하지 않음
   - 각자 독립적으로 Backtest 모델에 접근

4. **Phase 2 아키텍처 준수**
   - 레이어드 아키텍처: CRUD Layer ↔ Execution Layer 분리
   - 마이크로서비스 패턴 (Single Responsibility)

---

## 4. Git 정리 작업

### 4.1 커밋 메시지

```bash
git rm backend/app/services/backtest/orchestrator_legacy.py
git rm backend/app/services/market_data/intelligence_legacy.py
git rm backend/app/services/trading/strategy_service_legacy.py

git commit -m "chore: Phase 2.1 완료 후 레거시 파일 제거

Phase 2.1a/b/c/d/e 모듈화 완료로 레거시 파일 제거:

- orchestrator_legacy.py → orchestrator/ (6 modules)
- intelligence_legacy.py → intelligence/ (7 modules)
- strategy_service_legacy.py → strategy_service/ (5 modules)

검증:
- ✅ 코드베이스 참조 0건
- ✅ Import 문 없음
- ✅ 새 모듈로 100% 대체 완료

관련 커밋:
- Phase 2.1d: orchestrator.py 모듈화 (commit 21dc3a9)
- Phase 2.1c: intelligence.py 모듈화 (commit 70b6d7f)
- Phase 2.1e: strategy_service.py 모듈화 (commit ba871dc)"
```

---

## 5. 요약

### 5.1 레거시 파일 처리

| 파일                       | 상태         | 조치     | 새 모듈                     |
| -------------------------- | ------------ | -------- | --------------------------- |
| orchestrator_legacy.py     | ✅ 대체 완료 | **제거** | orchestrator/ (6 files)     |
| intelligence_legacy.py     | ✅ 대체 완료 | **제거** | intelligence/ (7 files)     |
| strategy_service_legacy.py | ✅ 대체 완료 | **제거** | strategy_service/ (5 files) |

### 5.2 중복 서비스 검증

| 서비스                               | 역할      | 상태    | 조치     |
| ------------------------------------ | --------- | ------- | -------- |
| services/backtest/                   | 실행 엔진 | ✅ 필요 | **유지** |
| services/trading/backtest_service.py | CRUD      | ✅ 필요 | **유지** |

**중복 아님**: 명확한 역할 분리 (Separation of Concerns)

---

## 6. Phase 2.2 준비 완료

✅ **레거시 파일 제거 완료 후 Phase 2.2 진행 가능**

**다음 단계**: Phase 2.2 - ML Platform Domain 모듈화

- model_lifecycle_service.py (476 lines)
- feature_engineer.py (350+ lines)
- ml_trainer.py (300+ lines)
- anomaly_detector.py (250+ lines)
