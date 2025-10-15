# Phase 1 Step 1: Enum 통합 상세 가이드

**소요 시간**: 4시간  
**난이도**: ⭐⭐ (중간)  
**목표**: 모든 Enum을 `schemas/enums.py`로 통합하여 중복 제거

---

## 1. 현황 분석

### 1.1 현재 Enum 분포

| Enum 이름             | 정의 위치                                                    | 사용처                                | 중복 여부   |
| --------------------- | ------------------------------------------------------------ | ------------------------------------- | ----------- |
| `BacktestStatus`      | `models/backtest.py:11`                                      | models, schemas, services, routes     | ❌ 단일     |
| `TradeType`           | `models/backtest.py:19`                                      | models, schemas                       | ❌ 단일     |
| `OrderType`           | `models/backtest.py:25`                                      | models, schemas                       | ❌ 단일     |
| `SignalType`          | `models/strategy.py:37`<br/>`strategies/base_strategy.py:15` | models, schemas, strategies, services | ✅ **중복** |
| `StrategyType`        | `models/strategy.py:28`                                      | models, schemas, services, routes     | ❌ 단일     |
| `MarketRegimeType`    | `models/market_data/regime.py:14`                            | models, schemas, services             | ❌ 단일     |
| `DataInterval`        | `schemas/market_data/*.py` (분산)                            | schemas, services                     | ✅ **분산** |
| `ModelStatus`         | `models/model_lifecycle.py:20`                               | models, schemas, services             | ❌ 단일     |
| `ExperimentStatus`    | `models/model_lifecycle.py:28`                               | models, schemas, services             | ❌ 단일     |
| `DeploymentStatus`    | `models/model_lifecycle.py:36`                               | models, schemas, services             | ❌ 단일     |
| `PromptStatus`        | `models/prompt_governance.py:15`                             | models, schemas, routes               | ❌ 단일     |
| `ReportFormat`        | `schemas/narrative.py:10`                                    | schemas, services                     | ❌ 단일     |
| `ChatCommandType`     | `schemas/chatops.py:12`                                      | schemas, services                     | ❌ 단일     |
| `OptimizationStatus`  | `models/optimization.py:10`                                  | models, schemas, services             | ❌ 단일     |
| `DataQualitySeverity` | `models/data_quality.py:10`                                  | models, schemas, services             | ❌ 단일     |

**통계**:

- 총 Enum 타입: **15개**
- 중복 정의: **2개** (SignalType, DataInterval)
- 분산 위치: **8개 파일**

### 1.2 문제점

#### 문제 1: SignalType 중복

```python
# ❌ models/strategy.py (Line 37-41)
class SignalType(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"

# ❌ strategies/base_strategy.py (Line 15-19) - 동일한 정의
class SignalType(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
```

**영향**:

- 임포트 경로 혼란: `from app.models.strategy import SignalType` vs
  `from app.strategies.base_strategy import SignalType`
- 정의 변경 시 2곳 수정 필요

#### 문제 2: DataInterval 분산

```python
# schemas/market_data/stock.py (암시적)
# schemas/market_data/crypto.py (암시적)
# 각 파일에서 Literal["1min", "5min", "15min", ...] 하드코딩
```

**영향**:

- 타입 안전성 부족 (Enum 없이 문자열 직접 사용)
- 오타 발생 위험 (`"1min"` vs `"1m"`)

---

## 2. 통합 계획

### 2.1 `schemas/enums.py` 구조

```python
"""
Unified Enum definitions for all domains
모든 도메인의 Enum 타입을 통합 관리
"""

from enum import Enum


# ============================================================================
# Trading Domain Enums
# ============================================================================

class BacktestStatus(str, Enum):
    """백테스트 상태"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TradeType(str, Enum):
    """거래 타입"""
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    """주문 타입"""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"


class SignalType(str, Enum):
    """전략 신호 타입"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


class StrategyType(str, Enum):
    """지원되는 전략 타입"""
    SMA_CROSSOVER = "sma_crossover"
    RSI_MEAN_REVERSION = "rsi_mean_reversion"
    MOMENTUM = "momentum"
    BUY_AND_HOLD = "buy_and_hold"
    CUSTOM = "custom"


class OptimizationStatus(str, Enum):
    """최적화 실행 상태"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ============================================================================
# Market Data Domain Enums
# ============================================================================

class MarketRegimeType(str, Enum):
    """시장 국면 타입"""
    BULL = "bull"              # 강세장
    BEAR = "bear"              # 약세장
    SIDEWAYS = "sideways"      # 횡보장
    HIGH_VOLATILITY = "high_volatility"  # 고변동성
    LOW_VOLATILITY = "low_volatility"    # 저변동성
    CRISIS = "crisis"          # 위기


class DataInterval(str, Enum):
    """시계열 데이터 간격"""
    # Intraday
    ONE_MIN = "1min"
    FIVE_MIN = "5min"
    FIFTEEN_MIN = "15min"
    THIRTY_MIN = "30min"
    SIXTY_MIN = "60min"

    # Daily+
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class DataQualitySeverity(str, Enum):
    """데이터 품질 이슈 심각도"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# ============================================================================
# ML Platform Domain Enums
# ============================================================================

class ModelStatus(str, Enum):
    """ML 모델 상태"""
    TRAINING = "training"
    TRAINED = "trained"
    EVALUATING = "evaluating"
    REGISTERED = "registered"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class ExperimentStatus(str, Enum):
    """실험 상태"""
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DeploymentStatus(str, Enum):
    """모델 배포 상태"""
    DEPLOYING = "deploying"
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"
    ROLLBACK = "rollback"


class EvaluationMetricType(str, Enum):
    """평가 지표 타입"""
    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    AUC_ROC = "auc_roc"
    MAE = "mae"
    MSE = "mse"
    RMSE = "rmse"
    SHARPE_RATIO = "sharpe_ratio"
    SORTINO_RATIO = "sortino_ratio"


# ============================================================================
# Generative AI Domain Enums
# ============================================================================

class PromptStatus(str, Enum):
    """프롬프트 템플릿 상태"""
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class ReportFormat(str, Enum):
    """리포트 출력 형식"""
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"
    JSON = "json"


class ChatCommandType(str, Enum):
    """ChatOps 명령 타입"""
    BACKTEST = "backtest"
    STRATEGY = "strategy"
    OPTIMIZATION = "optimization"
    PORTFOLIO = "portfolio"
    MARKET_DATA = "market_data"
    HELP = "help"
    STATUS = "status"


class IntentType(str, Enum):
    """대화 의도 타입 (Strategy Builder)"""
    CREATE_STRATEGY = "create_strategy"
    MODIFY_STRATEGY = "modify_strategy"
    ADD_INDICATOR = "add_indicator"
    SET_PARAMETER = "set_parameter"
    BACKTEST = "backtest"
    OPTIMIZE = "optimize"
    HELP = "help"
    CLARIFY = "clarify"


# ============================================================================
# User Domain Enums
# ============================================================================

class WatchlistType(str, Enum):
    """워치리스트 타입"""
    STOCKS = "stocks"
    CRYPTO = "crypto"
    FOREX = "forex"
    COMMODITIES = "commodities"
    MIXED = "mixed"


class NotificationType(str, Enum):
    """알림 타입"""
    BACKTEST_COMPLETED = "backtest_completed"
    OPTIMIZATION_COMPLETED = "optimization_completed"
    SIGNAL_GENERATED = "signal_generated"
    DATA_QUALITY_ALERT = "data_quality_alert"
    SYSTEM_ALERT = "system_alert"


# ============================================================================
# System Enums
# ============================================================================

class TaskStatus(str, Enum):
    """Celery 태스크 상태"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    RETRY = "retry"
    REVOKED = "revoked"


class LogLevel(str, Enum):
    """로그 레벨"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
```

### 2.2 파일 크기 예상

- **총 라인 수**: ~200 lines
- **Enum 개수**: 20개
- **도메인 섹션**: 5개 (Trading, Market Data, ML Platform, Gen AI, User, System)

---

## 3. 마이그레이션 실행 단계

### Step 1.1: `schemas/enums.py` 생성 (30분)

```bash
# 파일 생성
touch backend/app/schemas/enums.py

# 위의 코드 복사/붙여넣기 (200 lines)
```

**체크포인트**:

```bash
# 라인 수 확인
wc -l backend/app/schemas/enums.py  # Should be ~200

# 구문 검증
cd backend && uv run python -c "from app.schemas.enums import *; print('✅ Enums loaded')"
```

---

### Step 1.2: 중복 Enum 제거 (1시간)

#### 1.2.1 Trading Domain

**파일**: `backend/app/models/backtest.py`

```python
# ❌ 삭제할 코드 (Line 11-32)
class BacktestStatus(str, Enum):
    """백테스트 상태"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TradeType(str, Enum):
    """거래 타입"""
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    """주문 타입"""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"

# ✅ 추가할 임포트 (Line 10)
from app.schemas.enums import BacktestStatus, TradeType, OrderType
```

**파일**: `backend/app/models/strategy.py`

```python
# ❌ 삭제할 코드 (Line 28-50)
class StrategyType(str, Enum):
    """지원되는 전략 타입"""
    SMA_CROSSOVER = "sma_crossover"
    RSI_MEAN_REVERSION = "rsi_mean_reversion"
    MOMENTUM = "momentum"
    BUY_AND_HOLD = "buy_and_hold"
    CUSTOM = "custom"


class SignalType(str, Enum):
    """신호 타입"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"

# ✅ 추가할 임포트 (Line 10)
from app.schemas.enums import StrategyType, SignalType
```

**파일**: `backend/app/strategies/base_strategy.py`

```python
# ❌ 삭제할 코드 (Line 15-22)
class SignalType(str, Enum):
    """신호 타입"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"

# ✅ 추가할 임포트 (Line 14)
from app.schemas.enums import SignalType
```

#### 1.2.2 Market Data Domain

**파일**: `backend/app/models/market_data/regime.py`

```python
# ❌ 삭제할 코드 (Line 14-24)
class MarketRegimeType(str, Enum):
    """Supported market regimes for classification."""
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"
    CRISIS = "crisis"

# ✅ 추가할 임포트 (Line 10)
from app.schemas.enums import MarketRegimeType
```

#### 1.2.3 ML Platform Domain

**파일**: `backend/app/models/model_lifecycle.py`

```python
# ❌ 삭제할 코드 (Line 20-50)
class ModelStatus(str, Enum):
    ...

class ExperimentStatus(str, Enum):
    ...

class DeploymentStatus(str, Enum):
    ...

# ✅ 추가할 임포트 (Line 10)
from app.schemas.enums import ModelStatus, ExperimentStatus, DeploymentStatus
```

#### 1.2.4 Gen AI Domain

**파일**: `backend/app/models/prompt_governance.py`

```python
# ❌ 삭제할 코드
class PromptStatus(str, Enum):
    ...

# ✅ 추가할 임포트
from app.schemas.enums import PromptStatus
```

**파일**: `backend/app/schemas/narrative.py`

```python
# ❌ 삭제할 코드
class ReportFormat(str, Enum):
    ...

# ✅ 추가할 임포트
from app.schemas.enums import ReportFormat
```

**파일**: `backend/app/schemas/chatops.py`

```python
# ❌ 삭제할 코드
class ChatCommandType(str, Enum):
    ...

# ✅ 추가할 임포트
from app.schemas.enums import ChatCommandType
```

---

### Step 1.3: 임포트 경로 전역 변경 (1.5시간)

#### 1.3.1 자동 검색 및 변경

```bash
# 모든 Python 파일에서 Enum 임포트 찾기
cd backend/app
grep -r "from.*models.*import.*Status" --include="*.py" | wc -l
grep -r "from.*models.*import.*Type" --include="*.py" | wc -l
```

#### 1.3.2 IDE 리팩토링 도구 활용

**VSCode**:

1. `Cmd+Shift+F` (전역 검색)
2. 검색: `from app.models.backtest import BacktestStatus`
3. 치환: `from app.schemas.enums import BacktestStatus`
4. "Replace All" 클릭

**PyCharm**:

1. `Cmd+Shift+R` (전역 치환)
2. 정규식 사용: `from app\.models\.\w+ import (BacktestStatus|TradeType|...)`
3. 치환: `from app.schemas.enums import $1`

#### 1.3.3 수동 변경 대상 파일

| 도메인          | 파일                                   | 변경 전                                                      | 변경 후                                                  |
| --------------- | -------------------------------------- | ------------------------------------------------------------ | -------------------------------------------------------- |
| **Trading**     | `services/backtest_service.py`         | `from app.models.backtest import BacktestStatus`             | `from app.schemas.enums import BacktestStatus`           |
|                 | `services/strategy_service.py`         | `from app.models.strategy import StrategyType, SignalType`   | `from app.schemas.enums import StrategyType, SignalType` |
|                 | `services/optimization_service.py`     | `from app.models.optimization import OptimizationStatus`     | `from app.schemas.enums import OptimizationStatus`       |
|                 | `api/routes/backtests.py`              | `from app.models.backtest import BacktestStatus`             | `from app.schemas.enums import BacktestStatus`           |
|                 | `api/routes/strategies/*.py`           | `from app.models.strategy import StrategyType`               | `from app.schemas.enums import StrategyType`             |
| **Market Data** | `services/market_data_service/*.py`    | `from app.models.market_data.regime import MarketRegimeType` | `from app.schemas.enums import MarketRegimeType`         |
| **ML Platform** | `services/model_lifecycle_service.py`  | `from app.models.model_lifecycle import ModelStatus, ...`    | `from app.schemas.enums import ModelStatus, ...`         |
|                 | `services/feature_store_service.py`    | (Enum 추가 필요 시)                                          | `from app.schemas.enums import ...`                      |
| **Gen AI**      | `services/narrative_report_service.py` | `from app.schemas.narrative import ReportFormat`             | `from app.schemas.enums import ReportFormat`             |
|                 | `services/chatops_advanced_service.py` | `from app.schemas.chatops import ChatCommandType`            | `from app.schemas.enums import ChatCommandType`          |

---

### Step 1.4: 테스트 파일 업데이트 (30분)

**파일**: `backend/tests/test_backtest.py`

```python
# ❌ Before
from app.models.backtest import BacktestStatus, TradeType

# ✅ After
from app.schemas.enums import BacktestStatus, TradeType
```

**전체 테스트 디렉토리 변경**:

```bash
cd backend/tests
grep -r "from app.models" --include="*.py" | grep "import.*Status\|Type"
# 모든 매칭 파일에서 임포트 경로 변경
```

---

### Step 1.5: 검증 (30분)

#### 1.5.1 구문 검증

```bash
cd backend

# 1. Python 구문 오류 확인
uv run python -m py_compile app/schemas/enums.py

# 2. 임포트 테스트
uv run python -c "
from app.schemas.enums import (
    BacktestStatus, TradeType, OrderType, SignalType, StrategyType,
    MarketRegimeType, DataInterval, ModelStatus, PromptStatus
)
print('✅ All enums imported successfully')
"

# 3. Enum 값 검증
uv run python -c "
from app.schemas.enums import BacktestStatus
assert BacktestStatus.PENDING.value == 'pending'
assert BacktestStatus.COMPLETED.value == 'completed'
print('✅ Enum values correct')
"
```

#### 1.5.2 단위 테스트

```bash
# 전체 테스트 실행
cd backend
uv run pytest tests/ -v

# 특정 테스트만 실행
uv run pytest tests/test_backtest.py -v
uv run pytest tests/test_strategy.py -v
uv run pytest tests/models/ -v
```

#### 1.5.3 통합 테스트

```bash
# 서버 시작
cd backend
uv run fastapi dev app/main.py --port 8500 &

# OpenAPI 스키마 확인
curl http://localhost:8500/openapi.json | jq '.components.schemas' | grep -i "status\|type"

# 서버 종료
kill %1
```

#### 1.5.4 Frontend 클라이언트 재생성

```bash
# OpenAPI 클라이언트 생성
pnpm gen:client

# TypeScript 타입 검증
cd frontend
grep -r "BacktestStatus\|SignalType\|StrategyType" src/client/types.gen.ts

# TypeScript 빌드
pnpm build  # Should have 0 errors
```

---

## 4. 체크리스트

### 완료 검증

- [ ] `schemas/enums.py` 생성 (200+ lines)
- [ ] Trading Domain Enum 제거 (4개 파일)
  - [ ] `models/backtest.py`: BacktestStatus, TradeType, OrderType
  - [ ] `models/strategy.py`: StrategyType, SignalType
  - [ ] `strategies/base_strategy.py`: SignalType
  - [ ] `models/optimization.py`: OptimizationStatus
- [ ] Market Data Domain Enum 제거 (1개 파일)
  - [ ] `models/market_data/regime.py`: MarketRegimeType
- [ ] ML Platform Domain Enum 제거 (1개 파일)
  - [ ] `models/model_lifecycle.py`: ModelStatus, ExperimentStatus,
        DeploymentStatus
- [ ] Gen AI Domain Enum 제거 (3개 파일)
  - [ ] `models/prompt_governance.py`: PromptStatus
  - [ ] `schemas/narrative.py`: ReportFormat
  - [ ] `schemas/chatops.py`: ChatCommandType
- [ ] 모든 임포트 경로 변경 (`from app.schemas.enums import ...`)
  - [ ] Models (9개 파일)
  - [ ] Schemas (15개 파일)
  - [ ] Services (18개 파일)
  - [ ] Routes (19개 파일)
  - [ ] Tests (30+ 파일)
- [ ] 테스트 통과
  - [ ] `pytest tests/models/` - PASSED
  - [ ] `pytest tests/schemas/` - PASSED
  - [ ] `pytest tests/services/` - PASSED
  - [ ] `pytest` (전체) - PASSED
- [ ] Frontend 빌드
  - [ ] `pnpm gen:client` - SUCCESS
  - [ ] `pnpm build` - 0 errors
- [ ] 서버 정상 실행
  - [ ] `pnpm dev` - Backend 8500, Frontend 3000 정상

---

## 5. 롤백 계획

문제 발생 시 롤백:

```bash
# Git 변경사항 확인
git status

# 특정 파일 롤백
git checkout -- backend/app/schemas/enums.py
git checkout -- backend/app/models/backtest.py

# 전체 Step 1 롤백
git reset --hard HEAD

# 브랜치 삭제 (필요 시)
git branch -D phase1-step1-enum-consolidation
```

---

## 6. 다음 단계

**Step 1 완료 후**:

- ✅ Enum 중복 제거 완료
- ✅ 임포트 경로 통합 완료
- ✅ TypeScript 0 에러 유지

**다음 작업**: [PHASE1_STEP2_MODEL_SPLIT.md](./PHASE1_STEP2_MODEL_SPLIT.md)

- 모델 파일 분리 (200+ lines → 50-100 lines)
- Trading 도메인 디렉토리 생성
- ML Platform 도메인 디렉토리 생성

---

**예상 완료 시간**: 4시간  
**실제 소요 시간**: **\_** (완료 후 기록)
