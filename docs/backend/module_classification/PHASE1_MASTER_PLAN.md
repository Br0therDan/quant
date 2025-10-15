# Backend 모듈 재구조화 - Phase 1 마스터 플랜

**작성일**: 2025-01-15  
**기간**: 3-5일 (긴급 개선)  
**목표**: 코드 중복 제거 + 유지보수성 개선 + MSA 전환 준비

---

## 1. Phase 1 목표

### 1.1 핵심 성과 지표 (KPI)

| 지표                  | 현재            | 목표                       | 측정 방법                               |
| --------------------- | --------------- | -------------------------- | --------------------------------------- | --------------- |
| **Enum 중복**         | 15+ 곳          | 1곳 (`schemas/enums.py`)   | `grep -r "class.*Type.*Enum"`           |
| **200+ lines 파일**   | 8개             | 0개                        | `find . -name "\*.py" -exec wc -l {} \; | awk '$1 > 200'` |
| **명명 불일치**       | 5개             | 0개                        | 수동 검증                               |
| **관리자 엔드포인트** | 혼재 (12개)     | 분리 (`api/routes/admin/`) | 디렉토리 카운트                         |
| **TypeScript 에러**   | 0개 (현재 유지) | 0개                        | `pnpm build`                            |

### 1.2 비기능적 요구사항

- ✅ **하위 호환성 배제**: 레거시 임포트 경로 제거
- ✅ **자동 테스트**: 모든 변경 후 `pytest` 통과
- ✅ **Frontend 빌드**: 각 단계마다 `pnpm gen:client` 실행

---

## 2. 재구조화 대상 디렉토리

### 2.1 최종 디렉토리 구조 (Target State)

```
backend/app/
├── schemas/                           # ✅ 통합된 스키마 (Pydantic)
│   ├── __init__.py
│   ├── enums.py                      # 🆕 모든 Enum 통합
│   ├── base.py                       # 🆕 BaseSchema (renamed from base_schema.py)
│   │
│   ├── trading/                      # 🆕 트레이딩 도메인
│   │   ├── __init__.py
│   │   ├── backtest.py               # Request/Response
│   │   ├── strategy.py
│   │   ├── optimization.py
│   │   └── performance.py
│   │
│   ├── market_data/                  # ✅ 기존 유지
│   │   ├── __init__.py
│   │   ├── stock.py
│   │   ├── crypto.py
│   │   ├── fundamental.py
│   │   └── ...
│   │
│   ├── ml_platform/                  # 🆕 ML 도메인
│   │   ├── __init__.py
│   │   ├── model_lifecycle.py
│   │   ├── feature_store.py
│   │   ├── evaluation.py             # evaluation_harness.py 통합
│   │   └── data_quality.py
│   │
│   ├── gen_ai/                       # 🆕 생성형 AI 도메인
│   │   ├── __init__.py
│   │   ├── narrative.py
│   │   ├── strategy_builder.py
│   │   ├── chatops.py
│   │   └── prompt_governance.py
│   │
│   └── user/                         # 🆕 사용자 도메인
│       ├── __init__.py
│       ├── watchlist.py
│       └── dashboard.py
│
├── models/                            # ✅ DB 모델 (Beanie Document)
│   ├── __init__.py
│   ├── base.py                       # 🆕 BaseDocument (renamed from base_model.py)
│   │
│   ├── trading/                      # 🆕 트레이딩 도메인
│   │   ├── __init__.py
│   │   ├── backtest.py               # Backtest, BacktestExecution
│   │   ├── backtest_result.py        # 🆕 BacktestResult 분리
│   │   ├── strategy.py               # Strategy, StrategyTemplate
│   │   ├── strategy_execution.py     # 🆕 StrategyExecution 분리
│   │   ├── optimization.py           # OptimizationRun, OptimizationTrial
│   │   └── performance.py            # StrategyPerformance
│   │
│   ├── market_data/                  # ✅ 기존 구조 유지 (잘 설계됨)
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── stock.py
│   │   ├── crypto.py
│   │   └── ...
│   │
│   ├── ml_platform/                  # 🆕 ML 도메인
│   │   ├── __init__.py
│   │   ├── feature.py                # Feature (from feature_store.py)
│   │   ├── feature_version.py        # 🆕 FeatureVersion 분리
│   │   ├── experiment.py             # ModelExperiment
│   │   ├── model_registry.py         # 🆕 RegisteredModel 분리
│   │   ├── deployment.py             # 🆕 ModelDeployment 분리
│   │   ├── evaluation.py             # Benchmark, ABTest, FairnessAudit
│   │   └── data_quality.py           # DataQualityEvent
│   │
│   ├── gen_ai/                       # 🆕 생성형 AI 도메인
│   │   ├── __init__.py
│   │   ├── narrative_report.py       # NarrativeReport
│   │   ├── strategy_code.py          # 🆕 StrategyCode 분리
│   │   ├── chatops_session.py        # ChatSession
│   │   └── prompt_template.py        # PromptTemplate
│   │
│   └── user/                         # 🆕 사용자 도메인
│       ├── __init__.py
│       └── watchlist.py              # Watchlist
│
├── services/                          # ✅ 비즈니스 로직
│   ├── __init__.py
│   ├── service_factory.py            # ✅ 유지
│   ├── database_manager.py           # ✅ 유지
│   │
│   ├── trading/                      # 🆕 트레이딩 서비스
│   │   ├── __init__.py
│   │   ├── backtest_service.py
│   │   ├── backtest_executor.py      # 🆕 실행 로직 분리
│   │   ├── strategy_service.py
│   │   ├── optimization_service.py
│   │   └── portfolio_service.py
│   │
│   ├── market_data/                  # ✅ 기존 유지
│   │   ├── __init__.py
│   │   ├── base_service.py
│   │   ├── stock_service.py
│   │   └── ...
│   │
│   ├── ml_platform/                  # 🆕 ML 서비스
│   │   ├── __init__.py
│   │   ├── feature_store_service.py
│   │   ├── model_lifecycle_service.py
│   │   ├── evaluation_service.py     # 🆕 evaluation_harness_service.py 이동
│   │   ├── ml_signal_service.py      # 🆕 이동
│   │   ├── regime_detection_service.py # 🆕 이동
│   │   └── data_quality_service.py   # 🆕 신규 생성
│   │
│   ├── gen_ai/                       # 🆕 생성형 AI 서비스
│   │   ├── __init__.py
│   │   ├── narrative_service.py      # 🆕 narrative_report_service.py 이동
│   │   ├── strategy_builder_service.py
│   │   ├── chatops_service.py        # 🆕 chatops_advanced_service.py 통합
│   │   ├── prompt_governance_service.py # 🆕 신규 생성
│   │   └── llm/                      # ✅ 기존 유지
│   │
│   └── user/                         # 🆕 사용자 서비스
│       ├── __init__.py
│       ├── watchlist_service.py
│       └── dashboard_service.py
│
└── api/routes/                        # ✅ API 엔드포인트
    ├── __init__.py
    ├── system/                       # 🆕 시스템 엔드포인트
    │   ├── __init__.py
    │   ├── health.py
    │   └── tasks.py
    │
    ├── trading/                      # 🆕 트레이딩 엔드포인트
    │   ├── __init__.py
    │   ├── backtests.py
    │   ├── strategies.py             # 🆕 strategies/strategy.py 통합
    │   ├── strategy_templates.py     # 🆕 strategies/template.py 이동
    │   ├── optimization.py           # 🆕 optimize_backtests.py 이름 변경
    │   └── signals.py
    │
    ├── market_data/                  # ✅ 기존 유지
    │   ├── __init__.py
    │   └── ...
    │
    ├── ml_platform/                  # 🆕 ML 엔드포인트
    │   ├── __init__.py
    │   ├── features.py               # 🆕 feature_store.py 이동
    │   ├── experiments.py            # 🆕 ml/lifecycle.py 이동
    │   ├── models.py                 # 🆕 ml/train.py 통합
    │   └── evaluations.py            # 🆕 ml/evaluation.py 이동
    │
    ├── gen_ai/                       # 🆕 생성형 AI 엔드포인트
    │   ├── __init__.py
    │   ├── narratives.py             # 🆕 narrative.py 이동
    │   ├── strategy_builder.py
    │   ├── chatops.py                # 🆕 chatops.py + chatops_advanced.py 통합
    │   └── prompts.py                # 🆕 prompt_governance.py 이동
    │
    ├── user/                         # 🆕 사용자 엔드포인트
    │   ├── __init__.py
    │   ├── watchlists.py
    │   └── dashboard.py
    │
    └── admin/                        # 🆕 관리자 엔드포인트
        ├── __init__.py
        ├── system.py                 # 전체 시스템 상태, DB 백업 등
        ├── users.py                  # 사용자 관리
        ├── backtests.py              # 모든 백테스트 관리
        └── models.py                 # 모든 ML 모델 관리
```

---

## 3. Phase 1 작업 단계 (4 Steps)

### Step 1: Enum 통합 (Day 1 - 4시간)

**목표**: 모든 Enum을 `schemas/enums.py`로 통합

**작업 내용**:

1. `schemas/enums.py` 생성

   ```python
   # Trading Domain
   class BacktestStatus(str, Enum): ...
   class TradeType(str, Enum): ...
   class OrderType(str, Enum): ...
   class SignalType(str, Enum): ...
   class StrategyType(str, Enum): ...

   # Market Data Domain
   class MarketRegimeType(str, Enum): ...
   class DataInterval(str, Enum): ...

   # ML Platform Domain
   class ModelStatus(str, Enum): ...
   class ExperimentStatus(str, Enum): ...
   class DeploymentStatus(str, Enum): ...

   # Gen AI Domain
   class PromptStatus(str, Enum): ...
   class ReportFormat(str, Enum): ...
   ```

2. **중복 Enum 제거**:

   - `models/backtest.py`: BacktestStatus, TradeType, OrderType 삭제
   - `models/strategy.py`: SignalType, StrategyType 삭제
   - `strategies/base_strategy.py`: SignalType 삭제
   - `models/market_data/regime.py`: MarketRegimeType 삭제

3. **임포트 경로 변경**:

   ```python
   # ❌ Before
   from app.models.backtest import BacktestStatus
   from app.models.strategy import SignalType

   # ✅ After
   from app.schemas.enums import BacktestStatus, SignalType
   ```

4. **검증**:

   ```bash
   # 중복 확인
   grep -r "class BacktestStatus" backend/app/

   # 테스트 실행
   cd backend && uv run pytest

   # Frontend 클라이언트 재생성
   pnpm gen:client
   ```

**산출물**: `schemas/enums.py` (200+ lines)

---

### Step 2: 모델 파일 분리 (Day 1-2 - 6시간)

**목표**: 200+ lines 파일을 50-100 lines로 분할

#### 2.1 Trading 도메인 분리

**현재**: `models/backtest.py` (240 lines)

```python
# Enums (4개) - Step 1에서 이미 제거됨
# BaseModel (4개): BacktestConfig, Trade, Position, PerformanceMetrics
# Document (3개): Backtest, BacktestExecution, BacktestResult
```

**분리 후**:

```
models/trading/
├── __init__.py               # 통합 export
├── backtest.py              # Backtest, BacktestExecution (100 lines)
├── backtest_result.py       # BacktestResult (40 lines)
├── backtest_types.py        # 🆕 BacktestConfig, Trade, Position (60 lines)
├── performance.py           # PerformanceMetrics (기존 파일 이동)
├── strategy.py              # Strategy, StrategyTemplate (80 lines)
├── strategy_execution.py    # StrategyExecution (40 lines)
└── optimization.py          # OptimizationRun, OptimizationTrial (기존 파일 이동)
```

#### 2.2 ML Platform 도메인 분리

**현재**: `models/model_lifecycle.py` (200+ lines)

```python
# Document (4개): ModelExperiment, RegisteredModel, ModelDeployment, ModelMetrics
```

**분리 후**:

```
models/ml_platform/
├── __init__.py
├── experiment.py            # ModelExperiment (60 lines)
├── model_registry.py        # RegisteredModel (50 lines)
├── deployment.py            # ModelDeployment (50 lines)
├── feature.py               # Feature (from feature_store.py)
├── feature_version.py       # FeatureVersion (40 lines)
├── evaluation.py            # Benchmark, ABTest, FairnessAudit (기존 파일들 통합)
└── data_quality.py          # DataQualityEvent (기존 파일 이동)
```

#### 2.3 Gen AI 도메인 분리

**분리 후**:

```
models/gen_ai/
├── __init__.py
├── narrative_report.py      # NarrativeReport
├── strategy_code.py         # 🆕 StrategyCode (strategy_builder에서 분리)
├── chatops_session.py       # ChatSession (chatops/session.py 이동)
└── prompt_template.py       # PromptTemplate (기존 파일 이동)
```

**검증**:

```bash
# 파일 라인 수 확인
find backend/app/models -name "*.py" -exec wc -l {} \; | awk '$1 > 200'

# 테스트 실행
cd backend && uv run pytest tests/models/
```

**산출물**: 25+ 모델 파일 (평균 50-80 lines)

---

### Step 3: 스키마 파일 재구조화 (Day 2 - 4시간)

**목표**: 모델과 동일한 디렉토리 구조 적용

**작업 내용**:

1. **디렉토리 생성**:

   ```bash
   mkdir -p backend/app/schemas/{trading,ml_platform,gen_ai,user}
   ```

2. **파일 이동**:

   ```
   schemas/backtest.py → schemas/trading/backtest.py
   schemas/strategy.py → schemas/trading/strategy.py
   schemas/optimization.py → schemas/trading/optimization.py
   schemas/predictive.py → schemas/trading/predictive.py (포트폴리오 예측)

   schemas/feature_store.py → schemas/ml_platform/feature_store.py
   schemas/model_lifecycle.py → schemas/ml_platform/model_lifecycle.py
   schemas/evaluation_harness.py → schemas/ml_platform/evaluation.py

   schemas/narrative.py → schemas/gen_ai/narrative.py
   schemas/strategy_builder.py → schemas/gen_ai/strategy_builder.py
   schemas/chatops.py → schemas/gen_ai/chatops.py
   schemas/prompt_governance.py → schemas/gen_ai/prompt_governance.py

   schemas/watchlist.py → schemas/user/watchlist.py
   schemas/dashboard.py → schemas/user/dashboard.py
   ```

3. **`schemas/__init__.py` 업데이트**:

   ```python
   # Trading
   from .trading.backtest import *
   from .trading.strategy import *
   from .trading.optimization import *

   # ML Platform
   from .ml_platform.feature_store import *
   from .ml_platform.model_lifecycle import *
   from .ml_platform.evaluation import *

   # Gen AI
   from .gen_ai.narrative import *
   from .gen_ai.strategy_builder import *
   from .gen_ai.chatops import *
   from .gen_ai.prompt_governance import *

   # User
   from .user.watchlist import *
   from .user.dashboard import *

   # Enums (공통)
   from .enums import *
   ```

**검증**:

```bash
# 임포트 경로 변경 확인
grep -r "from app.schemas import" backend/app/

# 테스트 실행
cd backend && uv run pytest tests/schemas/
```

**산출물**: 도메인별 스키마 디렉토리 (trading, ml_platform, gen_ai, user)

---

### Step 4: 서비스 & 엔드포인트 재구조화 (Day 3-4 - 12시간)

#### 4.1 서비스 레이어 재구조화

**작업 내용**:

1. **디렉토리 생성**:

   ```bash
   mkdir -p backend/app/services/{trading,ml_platform,gen_ai,user}
   ```

2. **파일 이동 + 이름 변경**:

   ```
   services/backtest_service.py → services/trading/backtest_service.py
   services/backtest/ → services/trading/backtest/ (하위 디렉토리 유지)
   services/strategy_service.py → services/trading/strategy_service.py
   services/optimization_service.py → services/trading/optimization_service.py
   services/portfolio_service.py → services/trading/portfolio_service.py
   services/probabilistic_kpi_service.py → services/trading/kpi_service.py

   services/feature_store_service.py → services/ml_platform/feature_store_service.py
   services/model_lifecycle_service.py → services/ml_platform/model_lifecycle_service.py
   services/evaluation_harness_service.py → services/ml_platform/evaluation_service.py
   services/ml_signal_service.py → services/ml_platform/ml_signal_service.py
   services/regime_detection_service.py → services/ml_platform/regime_detection_service.py
   services/ml/ → services/ml_platform/ml/ (하위 디렉토리 이동)

   services/narrative_report_service.py → services/gen_ai/narrative_service.py
   services/strategy_builder_service.py → services/gen_ai/strategy_builder_service.py
   services/chatops_advanced_service.py → services/gen_ai/chatops_service.py
   services/llm/ → services/gen_ai/llm/ (하위 디렉토리 이동)

   services/watchlist_service.py → services/user/watchlist_service.py
   services/dashboard_service.py → services/user/dashboard_service.py
   ```

3. **service_factory.py 업데이트**:

   ```python
   # Trading Services
   def get_backtest_service(self):
       from app.services.trading.backtest_service import BacktestService
       ...

   # ML Platform Services
   def get_feature_store_service(self):
       from app.services.ml_platform.feature_store_service import FeatureStoreService
       ...

   # Gen AI Services
   def get_narrative_service(self):
       from app.services.gen_ai.narrative_service import NarrativeService
       ...
   ```

#### 4.2 엔드포인트 재구조화

**작업 내용**:

1. **디렉토리 생성**:

   ```bash
   mkdir -p backend/app/api/routes/{system,trading,ml_platform,gen_ai,user,admin}
   ```

2. **파일 이동 + 이름 변경**:

   ```
   # System
   routes/health.py → routes/system/health.py
   routes/tasks.py → routes/system/tasks.py

   # Trading
   routes/backtests.py → routes/trading/backtests.py
   routes/strategies/strategy.py → routes/trading/strategies.py
   routes/strategies/template.py → routes/trading/strategy_templates.py
   routes/optimize_backtests.py → routes/trading/optimization.py (⚠️ 이름 변경)
   routes/signals.py → routes/trading/signals.py

   # ML Platform
   routes/feature_store.py → routes/ml_platform/features.py (⚠️ 이름 변경)
   routes/ml/train.py → routes/ml_platform/models.py (⚠️ 통합)
   routes/ml/lifecycle.py → routes/ml_platform/experiments.py (⚠️ 이름 변경)
   routes/ml/evaluation.py → routes/ml_platform/evaluations.py

   # Gen AI
   routes/narrative.py → routes/gen_ai/narratives.py
   routes/strategy_builder.py → routes/gen_ai/strategy_builder.py
   routes/chatops.py + routes/chatops_advanced.py → routes/gen_ai/chatops.py (⚠️ 통합)
   routes/prompt_governance.py → routes/gen_ai/prompts.py (⚠️ 이름 변경)

   # User
   routes/watchlists.py → routes/user/watchlists.py
   routes/dashboard.py → routes/user/dashboard.py
   ```

3. **태그 정리 (OpenAPI/Client 생성)**:

   ```python
   # ✅ Before (중복 태그)
   @router.get(..., tags=["ML"])          # routes/ml/train.py
   @router.get(..., tags=["ML"])          # routes/ml/lifecycle.py
   # → Client: class MLService (모든 엔드포인트 혼재)

   # ✅ After (고유 태그)
   @router.get(..., tags=["ML Models"])   # routes/ml_platform/models.py
   @router.get(..., tags=["ML Experiments"]) # routes/ml_platform/experiments.py
   # → Client: class MlModelsService, class MlExperimentsService
   ```

4. **관리자 엔드포인트 분리**:

   ```python
   # routes/admin/backtests.py
   router = APIRouter(prefix="/admin/backtests", tags=["Admin Backtests"])

   @router.delete("/{backtest_id}")
   async def delete_any_backtest(backtest_id: str):
       """관리자 전용: 모든 백테스트 삭제"""
       # 권한 검증 로직
       ...

   @router.get("/all")
   async def list_all_backtests():
       """관리자 전용: 모든 사용자의 백테스트 조회"""
       ...
   ```

5. **`api/routes/__init__.py` 업데이트**:

   ```python
   from fastapi import APIRouter

   # System
   from .system import health, tasks

   # Trading
   from .trading import backtests, strategies, strategy_templates, optimization, signals

   # ML Platform
   from .ml_platform import features, models, experiments, evaluations

   # Gen AI
   from .gen_ai import narratives, strategy_builder, chatops, prompts

   # User
   from .user import watchlists, dashboard

   # Admin
   from .admin import system as admin_system, users, backtests as admin_backtests, models as admin_models

   api_router = APIRouter()

   # System routes
   api_router.include_router(health.router, prefix="/health", tags=["System"])
   api_router.include_router(tasks.router, prefix="/tasks", tags=["System"])

   # Trading routes
   api_router.include_router(backtests.router, prefix="/backtests", tags=["Backtests"])
   api_router.include_router(strategies.router, prefix="/strategies", tags=["Strategies"])
   api_router.include_router(strategy_templates.router, prefix="/strategy-templates", tags=["Strategy Templates"])
   api_router.include_router(optimization.router, prefix="/optimization", tags=["Optimization"])
   api_router.include_router(signals.router, prefix="/signals", tags=["Signals"])

   # ML Platform routes
   api_router.include_router(features.router, prefix="/features", tags=["Features"])
   api_router.include_router(models.router, prefix="/ml/models", tags=["ML Models"])
   api_router.include_router(experiments.router, prefix="/ml/experiments", tags=["ML Experiments"])
   api_router.include_router(evaluations.router, prefix="/ml/evaluations", tags=["ML Evaluations"])

   # Gen AI routes
   api_router.include_router(narratives.router, prefix="/narratives", tags=["Narratives"])
   api_router.include_router(strategy_builder.router, prefix="/strategy-builder", tags=["Strategy Builder"])
   api_router.include_router(chatops.router, prefix="/chatops", tags=["ChatOps"])
   api_router.include_router(prompts.router, prefix="/prompts", tags=["Prompt Governance"])

   # User routes
   api_router.include_router(watchlists.router, prefix="/watchlists", tags=["Watchlists"])
   api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])

   # Admin routes
   api_router.include_router(admin_system.router, prefix="/admin/system", tags=["Admin System"])
   api_router.include_router(users.router, prefix="/admin/users", tags=["Admin Users"])
   api_router.include_router(admin_backtests.router, prefix="/admin/backtests", tags=["Admin Backtests"])
   api_router.include_router(admin_models.router, prefix="/admin/models", tags=["Admin Models"])
   ```

**검증**:

```bash
# 서버 시작
cd backend && uv run fastapi dev app/main.py --port 8500

# OpenAPI 스키마 확인
curl http://localhost:8500/openapi.json | jq '.tags'

# Frontend 클라이언트 재생성
pnpm gen:client

# TypeScript 빌드
cd frontend && pnpm build

# 테스트 실행
cd backend && uv run pytest
```

**산출물**:

- 도메인별 서비스 디렉토리: `services/{trading,ml_platform,gen_ai,user}/`
- 도메인별 엔드포인트 디렉토리:
  `api/routes/{trading,ml_platform,gen_ai,user,admin}/`
- 업데이트된 `service_factory.py`
- 업데이트된 `api/routes/__init__.py`

---

## 4. 마이그레이션 체크리스트

### 4.1 각 Step 완료 후 검증

**Step 1 (Enum 통합) 체크리스트**:

- [ ] `schemas/enums.py` 생성 (200+ lines)
- [ ] 중복 Enum 제거 (models/backtest.py, models/strategy.py 등)
- [ ] 모든 임포트 경로 변경 (`from app.schemas.enums import ...`)
- [ ] `pytest` 전체 통과
- [ ] `pnpm gen:client` 실행
- [ ] Frontend TypeScript 0 에러

**Step 2 (모델 분리) 체크리스트**:

- [ ] `models/trading/` 디렉토리 생성 (7개 파일)
- [ ] `models/ml_platform/` 디렉토리 생성 (7개 파일)
- [ ] `models/gen_ai/` 디렉토리 생성 (4개 파일)
- [ ] `models/user/` 디렉토리 생성 (1개 파일)
- [ ] 모든 파일 200 lines 미만
- [ ] `models/__init__.py` 업데이트
- [ ] `pytest tests/models/` 통과

**Step 3 (스키마 재구조화) 체크리스트**:

- [ ] `schemas/trading/` 디렉토리 생성 (4개 파일)
- [ ] `schemas/ml_platform/` 디렉토리 생성 (3개 파일)
- [ ] `schemas/gen_ai/` 디렉토리 생성 (4개 파일)
- [ ] `schemas/user/` 디렉토리 생성 (2개 파일)
- [ ] `schemas/__init__.py` 업데이트
- [ ] `pytest tests/schemas/` 통과
- [ ] `pnpm gen:client` 실행

**Step 4 (서비스 & 엔드포인트) 체크리스트**:

- [ ] `services/trading/` 디렉토리 생성 (5개 파일)
- [ ] `services/ml_platform/` 디렉토리 생성 (5개 파일)
- [ ] `services/gen_ai/` 디렉토리 생성 (4개 파일)
- [ ] `services/user/` 디렉토리 생성 (2개 파일)
- [ ] `service_factory.py` 업데이트 (모든 서비스 경로 변경)
- [ ] `api/routes/system/` 디렉토리 생성 (2개 파일)
- [ ] `api/routes/trading/` 디렉토리 생성 (5개 파일)
- [ ] `api/routes/ml_platform/` 디렉토리 생성 (4개 파일)
- [ ] `api/routes/gen_ai/` 디렉토리 생성 (4개 파일)
- [ ] `api/routes/user/` 디렉토리 생성 (2개 파일)
- [ ] `api/routes/admin/` 디렉토리 생성 (4개 파일)
- [ ] `api/routes/__init__.py` 업데이트 (모든 라우터 재등록)
- [ ] 태그 중복 제거 (OpenAPI 스키마 검증)
- [ ] `pytest` 전체 통과
- [ ] `pnpm gen:client` 실행
- [ ] Frontend TypeScript 0 에러
- [ ] `pnpm dev` 정상 실행

### 4.2 최종 검증 (Phase 1 완료)

```bash
# 1. Backend 테스트
cd backend
uv run pytest --cov=app --cov-report=term-missing

# 2. 파일 라인 수 검증
find app/models -name "*.py" -exec wc -l {} \; | awk '$1 > 200 {print "❌ " $2 " has " $1 " lines"}'
find app/schemas -name "*.py" -exec wc -l {} \; | awk '$1 > 200 {print "❌ " $2 " has " $1 " lines"}'

# 3. Enum 중복 검증
grep -r "class.*Type.*Enum" app/ | wc -l  # Should be <= 20 (schemas/enums.py only)

# 4. OpenAPI 스키마 검증
uv run python -c "from app.main import create_fastapi_app; import json; app = create_fastapi_app(); print(json.dumps(app.openapi(), indent=2))" > openapi.json
jq '.tags | length' openapi.json  # Should be ~20 (unique tags)

# 5. Frontend 클라이언트 재생성
cd ../frontend
pnpm gen:client

# 6. TypeScript 빌드
pnpm build  # Should have 0 errors

# 7. 풀스택 실행
cd ..
pnpm dev  # Backend (8500) + Frontend (3000) 정상 실행
```

---

## 5. 위험 관리

| 위험                            | 영향         | 대응                                                 |
| ------------------------------- | ------------ | ---------------------------------------------------- |
| **대규모 임포트 변경**          | 빌드 실패    | IDE 리팩토링 도구 활용 (PyCharm/VSCode), 단계별 검증 |
| **service_factory 의존성 깨짐** | 런타임 에러  | 각 Step마다 `pytest` 실행, 의존성 그래프 시각화      |
| **Frontend API 호출 실패**      | 404/500 에러 | 각 Step마다 `pnpm gen:client` + `pnpm build` 검증    |
| **DB 모델 변경**                | 데이터 손실  | Beanie 마이그레이션 스크립트 작성 (필요시)           |
| **테스트 깨짐**                 | CI/CD 실패   | 각 Step마다 `pytest --cov` 실행, 커버리지 80% 유지   |

---

## 6. 성공 기준

### 6.1 정량적 목표

- ✅ Enum 중복: 15+ 곳 → **1곳** (`schemas/enums.py`)
- ✅ 200+ lines 파일: 8개 → **0개**
- ✅ 도메인 디렉토리: 0개 → **4개** (trading, ml_platform, gen_ai, user)
- ✅ 관리자 엔드포인트: 혼재 → **분리** (`api/routes/admin/`)
- ✅ TypeScript 에러: **0개 유지**
- ✅ Pytest 커버리지: **80%+ 유지**

### 6.2 정성적 목표

- ✅ 코드 네비게이션 개선 (도메인별 디렉토리)
- ✅ MSA 전환 준비 완료 (명확한 도메인 경계)
- ✅ 신규 개발자 온보딩 시간 단축 (일관된 구조)

---

## 7. 다음 Phase (Phase 2 준비)

**Phase 2 목표**: 레거시 통합 + 관계 정의

- Strategy ↔ ModelExperiment 관계 정의
- DataQualityMixin → DataQualityEvent 자동 생성
- 서비스 레이어 800+ lines 파일 분할

**Phase 3 목표**: MSA 전환 준비

- 도메인 간 이벤트 주도 통신 (Message Queue)
- API Gateway 구성
- 도메인별 독립 배포 파이프라인

---

**다음 문서**:

- `PHASE1_STEP1_ENUM_CONSOLIDATION.md` (Enum 통합 상세 가이드)
- `PHASE1_STEP2_MODEL_SPLIT.md` (모델 분리 상세 가이드)
- `PHASE1_STEP3_SCHEMA_RESTRUCTURE.md` (스키마 재구조화 가이드)
- `PHASE1_STEP4_SERVICE_ENDPOINT.md` (서비스 & 엔드포인트 가이드)
