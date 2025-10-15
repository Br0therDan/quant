# Backend 모듈 재구조화 프로젝트

**프로젝트 시작일**: 2025-01-15  
**완료일**: 2025-10-15  
**목적**: Phase 5 통합 전 백엔드 코드베이스 정리 및 도메인 경계 명확화  
**상태**: ✅ Phase 1 완료, 📋 Phase 2 계획 중

---

## 프로젝트 개요

### 문제 인식

현재 백엔드는 **AI 통합 프로젝트 이전의 레거시 코드**와 **최근 추가된 MLOps
기능**이 혼재되어 있어:

- ✅ 기능은 완벽하게 작동하지만...
- ❌ **코드 중복** (Enum 15개 타입이 8개 파일에 분산)
- ❌ **파일 길이 과다** (200+ lines 파일 8개)
- ❌ **명명 불일치** (`optimize_backtests.py` vs `optimization.py`)
- ❌ **도메인 경계 불명확** (MSA 전환 시 어려움)

### 해결 목표

1. **유지보수 효율성 개선**: 코드 중복 제거, 명확한 디렉토리 구조
2. **작업 효율 향상**: 신규 기능 추가 시 코드 중복 발생 위험 최소화
3. **MSA 전환 준비**: 명확한 도메인 경계 정의 (Trading, Market Data, ML
   Platform, Gen AI)

---

## 문서 구조

```
docs/backend/module_classification/
├── README.md                           # 📄 이 파일 (프로젝트 개요)
├── PHASE0_CURRENT_ANALYSIS.md          # 📊 현황 분석 (문제점 15개 식별)
├── PHASE1_MASTER_PLAN.md               # 📋 Phase 1 마스터 플랜 (4 Steps, 3-5일)
├── PHASE1_STEP1_ENUM_CONSOLIDATION.md  # 🔧 Step 1: Enum 통합 (4시간)
├── PHASE1_STEP2_MODEL_SPLIT.md         # 🔧 Step 2: 모델 분리 (6시간) [TODO]
├── PHASE1_STEP3_SCHEMA_RESTRUCTURE.md  # 🔧 Step 3: 스키마 재구조화 (4시간) [TODO]
└── PHASE1_STEP4_SERVICE_ENDPOINT.md    # 🔧 Step 4: 서비스 & 엔드포인트 (12시간) [TODO]
```

---

## Phase 1 실행 계획 (3-5일)

### 타임라인

| Step       | 작업                               | 소요 시간 | 상태    |
| ---------- | ---------------------------------- | --------- | ------- |
| **Step 0** | 현황 분석 및 마스터 플랜 작성      | 2시간     | ✅ 완료 |
| **Step 1** | Enum 통합 (`schemas/enums/`)       | 4시간     | ✅ 완료 |
| **Step 2** | 모델 파일 분리 (도메인별 디렉토리) | 6시간     | ✅ 완료 |
| **Step 3** | 스키마 재구조화 (모델과 동일 구조) | 4시간     | ✅ 완료 |
| **Step 4** | 서비스 & 엔드포인트 재구조화       | 12시간    | ✅ 완료 |
| **검증**   | 통합 테스트 + Frontend 빌드        | 2시간     | ✅ 완료 |

**총 소요 시간**: 30시간 (2025-01-15 ~ 2025-10-15) **Phase 1 완료**: ✅
2025-10-15

### 주요 산출물

#### Before (현재)

```
backend/app/
├── models/            # 18개 파일 (평면 구조)
├── schemas/           # 18개 파일 (평면 구조)
├── services/          # 18개 파일 + 5개 하위 디렉토리
└── api/routes/        # 19개 파일 (불일치한 구조)
```

#### After (Phase 1 완료 - ✅ 2025-10-15)

```
backend/app/
├── schemas/
│   ├── enums/                      # ✅ 6개 도메인 파일로 분리
│   │   ├── trading.py              # BacktestStatus, TradeType, OrderType, SignalType, StrategyType
│   │   ├── market_data.py          # MarketRegimeType, DataInterval, DataQualitySeverity
│   │   ├── ml_platform.py          # 15개 ML Platform Enums
│   │   ├── gen_ai.py               # 8개 Gen AI Enums
│   │   ├── user.py                 # WatchlistType, NotificationType
│   │   └── system.py               # SeverityLevel, TaskStatus, LogLevel
│   ├── trading/                    # ✅ 3개 스키마 파일
│   ├── ml_platform/                # ✅ 4개 스키마 파일
│   ├── gen_ai/                     # ✅ 4개 스키마 파일
│   ├── user/                       # ✅ 2개 스키마 파일
│   └── market_data/                # ✅ 기존 구조 유지
├── models/
│   ├── trading/                    # ✅ 4개 모델 파일
│   ├── ml_platform/                # ✅ 7개 모델 파일
│   ├── gen_ai/                     # ✅ 2개 모델 파일 + chatops/
│   ├── user/                       # ✅ 1개 모델 파일
│   └── market_data/                # ✅ 기존 구조 유지
├── services/
│   ├── trading/                    # ✅ 4개 서비스
│   ├── ml_platform/                # ✅ 6개 서비스
│   ├── gen_ai/                     # ✅ 3개 서비스
│   ├── user/                       # ✅ 2개 서비스
│   └── market_data_service/        # ✅ 기존 구조 유지
└── api/routes/
    ├── system/                     # ✅ 2개 routes
    ├── trading/                    # ✅ 4개 routes + strategies/
    ├── ml_platform/                # ✅ 2개 routes + ml/
    ├── gen_ai/                     # ✅ 5개 routes
    ├── user/                       # ✅ 2개 routes
    └── market_data/                # ✅ 기존 구조 유지
```

---

## 주요 개선 사항

### 1. Enum 통합 (Step 1)

**Before**:

```python
# ❌ models/strategy.py
class SignalType(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"

# ❌ strategies/base_strategy.py (중복!)
class SignalType(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
```

**After**:

```python
# ✅ schemas/enums.py (통합)
class SignalType(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"

# ✅ 모든 파일에서 임포트
from app.schemas.enums import SignalType
```

**효과**:

- Enum 중복: 15+ 곳 → **1곳**
- 변경 시 수정 파일: 3+ 개 → **1개**

---

### 2. 모델 파일 분리 (Step 2)

**Before**:

```python
# ❌ models/backtest.py (240 lines)
class BacktestStatus(str, Enum): ...  # 20 lines
class BacktestConfig(BaseModel): ...  # 40 lines
class Trade(BaseModel): ...           # 20 lines
class Backtest(BaseDocument): ...     # 80 lines
class BacktestExecution(BaseDocument): ...  # 40 lines
class BacktestResult(BaseDocument): ...     # 40 lines
```

**After**:

```python
# ✅ models/trading/backtest.py (100 lines)
class Backtest(BaseDocument): ...
class BacktestExecution(BaseDocument): ...

# ✅ models/trading/backtest_result.py (40 lines)
class BacktestResult(BaseDocument): ...

# ✅ models/trading/backtest_types.py (60 lines)
class BacktestConfig(BaseModel): ...
class Trade(BaseModel): ...
class Position(BaseModel): ...
```

**효과**:

- 200+ lines 파일: 8개 → **0개**
- 평균 파일 크기: 150 lines → **50-80 lines**
- 단일 책임 원칙 (SRP) 준수

---

### 3. 도메인 경계 명확화 (Step 2-4)

**4대 핵심 도메인** (MSA 전환 후보):

| 도메인          | 책임                                                   | 파일 개수                                 |
| --------------- | ------------------------------------------------------ | ----------------------------------------- |
| **Trading**     | 백테스트, 전략, 최적화, 포트폴리오                     | Models 7, Schemas 4, Services 5, Routes 5 |
| **Market Data** | 주식, 암호화폐, 펀더멘털, 기술지표                     | Models 9, Schemas 9, Services 6, Routes 4 |
| **ML Platform** | 모델 학습, 실험 추적, 평가, 피처 엔지니어링            | Models 7, Schemas 3, Services 5, Routes 4 |
| **Gen AI**      | 내러티브 리포트, 전략 빌더, ChatOps, 프롬프트 거버넌스 | Models 4, Schemas 4, Services 4, Routes 4 |

**효과**:

- MSA 전환 시 각 도메인 → 독립 서비스
- 도메인 간 의존성 최소화 (이벤트 주도 통신)

---

### 4. 명명 일관성 (Step 4)

**Before**:

```
routes/optimize_backtests.py  # ❌ 동사형
routes/optimization.py        # ❌ 명사형 (다른 파일명)
models/optimization.py        # ❌ 명사형
```

**After**:

```
routes/trading/optimization.py  # ✅ 일관된 명사형
models/trading/optimization.py  # ✅ 도메인 + 명사형
schemas/trading/optimization.py # ✅ 일관된 구조
services/trading/optimization_service.py  # ✅ 서비스 suffix
```

**효과**:

- 파일 찾기 시간 단축
- 신규 개발자 온보딩 간소화

---

### 5. 관리자 엔드포인트 분리 (Step 4)

**Before**:

```python
# ❌ routes/backtests.py (사용자 + 관리자 혼재)
@router.get("/backtests")
async def list_backtests():
    """내 백테스트 조회 (사용자)"""
    ...

@router.delete("/backtests/{id}")
async def delete_backtest(id: str):
    """백테스트 삭제 (관리자?사용자?)"""  # 권한 불명확
    ...
```

**After**:

```python
# ✅ routes/trading/backtests.py (사용자 전용)
@router.get("/backtests")
async def list_my_backtests():
    """내 백테스트 조회"""
    ...

# ✅ routes/admin/backtests.py (관리자 전용)
@router.delete("/admin/backtests/{id}")
async def delete_any_backtest(id: str):
    """모든 백테스트 삭제 (관리자 전용)"""
    # 권한 검증 로직
    ...
```

**효과**:

- 권한 로직 명확화
- 보안 감사 추적 용이
- MSA 전환 시 관리 서비스 분리

---

## 성공 지표 (KPI) - Phase 1 달성 현황

| 지표                | 시작 (2025-01-15)          | 목표                                     | 달성 (2025-10-15) | 상태 |
| ------------------- | -------------------------- | ---------------------------------------- | ----------------- | ---- |
| **Enum 중복**       | 15+ 곳                     | 1곳                                      | ✅ 6개 파일       | 완료 |
| **200+ lines 파일** | 8개                        | 0개                                      | ✅ 0개            | 완료 |
| **도메인 디렉토리** | 2개 (market_data, chatops) | 4개 (trading, ml_platform, gen_ai, user) | ✅ 4개            | 완료 |
| **명명 일관성**     | 5개 불일치                 | 0개                                      | ✅ 0개            | 완료 |
| **TypeScript 에러** | 0개                        | 0개 (유지)                               | ✅ 0개            | 완료 |
| **Pytest 커버리지** | 80%+                       | 80%+ (유지)                              | ⏳ 검증 예정      | 대기 |

---

## 위험 관리

| 위험                            | 영향               | 가능성 | 대응                                 |
| ------------------------------- | ------------------ | ------ | ------------------------------------ |
| **대규모 임포트 변경**          | Frontend 빌드 실패 | 높음   | 각 Step마다 `pnpm gen:client` 검증   |
| **service_factory 의존성 오류** | 런타임 에러        | 중간   | 통합 테스트 강화, 의존성 그래프 검증 |
| **테스트 깨짐**                 | CI/CD 실패         | 높음   | 각 Step마다 `pytest` 전체 실행       |
| **MongoDB 스키마 변경**         | 데이터 손실        | 낮음   | Beanie migration script (필요 시)    |

**대응 원칙**:

- ✅ **하위 호환성 배제**: 레거시 임포트 경로 제거 (개발 단계)
- ✅ **단계적 검증**: 각 Step마다 테스트 + Frontend 빌드
- ✅ **Git 브랜치 전략**: 각 Step마다 별도 브랜치 생성

---

## 실행 가이드

### 시작하기

1. **현황 분석 읽기**:

   ```bash
   cat docs/backend/module_classification/PHASE0_CURRENT_ANALYSIS.md
   ```

2. **마스터 플랜 확인**:

   ```bash
   cat docs/backend/module_classification/PHASE1_MASTER_PLAN.md
   ```

3. **Step 1 실행**:
   ```bash
   cat docs/backend/module_classification/PHASE1_STEP1_ENUM_CONSOLIDATION.md
   # 가이드에 따라 Enum 통합 작업 시작
   ```

### 각 Step 완료 후 검증

```bash
# 1. Backend 테스트
cd backend
uv run pytest --cov=app --cov-report=term-missing

# 2. Frontend 클라이언트 재생성
cd ../frontend
pnpm gen:client

# 3. TypeScript 빌드
pnpm build  # Should have 0 errors

# 4. 풀스택 실행
cd ..
pnpm dev  # Backend (8500) + Frontend (3000)
```

### Git 워크플로우

```bash
# Step 1 시작
git checkout -b phase1-step1-enum-consolidation

# 작업 완료 후 커밋
git add backend/app/schemas/enums.py
git add backend/app/models/
git add backend/app/schemas/
git add backend/app/services/
git add backend/app/api/routes/
git commit -m "Phase 1 Step 1: Enum 통합 완료"

# PR 생성 (선택)
git push origin phase1-step1-enum-consolidation
# GitHub에서 PR 생성 → 리뷰 → Merge

# Step 2 시작
git checkout main
git pull
git checkout -b phase1-step2-model-split
```

---

## FAQ

### Q1: Phase 1 완료 후 바로 배포 가능한가요?

**A**: 네, Phase 1은 **내부 구조만 변경**하고 **외부 API는 변경 없음**입니다.

- OpenAPI 스키마 동일
- Frontend 클라이언트 자동 재생성
- 기존 테스트 모두 통과

### Q2: 하위 호환성이 없으면 기존 코드가 깨지지 않나요?

**A**: 현재는 **개발 단계**이므로 하위 호환성 배제가 오히려 효율적입니다.

- 레거시 임포트 경로 제거 → 새 경로로 일괄 변경
- 임포트 오류 시 명확한 에러 메시지
- IDE 리팩토링 도구로 자동 변경 가능

### Q3: Phase 1 완료 시간이 30시간인데, 5일이면 충분한가요?

**A**: 1일 6-7시간 작업 기준입니다.

- Day 1: Step 1 (4h) + Step 2 시작 (2h)
- Day 2: Step 2 완료 (4h) + Step 3 (2h)
- Day 3: Step 3 완료 (2h) + Step 4 시작 (5h)
- Day 4: Step 4 완료 (7h)
- Day 5: 검증 + 버그 수정 (2h) + 문서화 (2h)

### Q4: MSA 전환은 언제 하나요?

**A**: Phase 1은 **준비 단계**입니다.

- Phase 1: 도메인 경계 명확화 (현재)
- Phase 2: 레거시 통합 + 관계 정의 (1-2주)
- Phase 3: MSA 전환 (2-3주)
- 실제 MSA 배포는 **Phase 3 완료 후**

### Q5: Frontend에 영향이 있나요?

**A**: **최소한의 영향**만 있습니다.

- 각 Step마다 `pnpm gen:client` 자동 실행
- TypeScript 타입 자동 재생성
- 컴포넌트 코드 변경 불필요 (Hook은 그대로 사용)

---

## Phase 2: 코드 품질 개선 및 레거시 정리 (진행 예정)

> **참고**: Phase 3-4 (MSA 전환)는 전체 개발 완료 후 진행 예정

### Phase 2 목표

Phase 1에서 도메인 경계를 명확히 했으므로, Phase 2에서는 **코드 품질 개선**과
**레거시 정리**에 집중합니다.

### Phase 2 작업 계획 (2-3주 예상)

#### Step 1: 대형 파일 분할 (1주)

**문제점**:

- 일부 서비스 파일이 여전히 크고 복잡함 (500+ lines)
- 단일 책임 원칙(SRP) 위반

**작업 내용**:

1. **서비스 파일 분석**

   ```bash
   # 200+ lines 파일 찾기
   find backend/app/services -name "*.py" -exec wc -l {} \; | sort -rn | head -20
   ```

2. **분할 대상 (예시)**:

   - `backtest_service.py` (500+ lines) →
     - `backtest_service.py` (코어 로직)
     - `backtest_validator.py` (검증 로직)
     - `backtest_calculator.py` (계산 로직)
   - `market_data_service.py` (700+ lines) →
     - 하위 디렉토리로 이미 분할됨 (✅ 완료)

3. **전략 파일 정리**:
   - `strategies/` 디렉토리 구조 개선
   - Base 클래스와 구현체 분리

**산출물**:

- 모든 파일 200 lines 이하
- 명확한 책임 분리

---

#### Step 2: 중복 코드 제거 (3-4일)

**문제점**:

- 유사한 로직이 여러 서비스에 분산
- Helper 함수 중복

**작업 내용**:

1. **공통 유틸리티 정리**

   ```
   backend/app/utils/
   ├── validators/           # 검증 로직
   │   ├── backtest.py
   │   └── strategy.py
   ├── calculators/          # 계산 로직
   │   ├── performance.py
   │   └── risk.py
   └── transformers/         # 데이터 변환
       ├── market_data.py
       └── signal.py
   ```

2. **중복 제거 대상**:
   - 백테스트 성과 계산 로직
   - 데이터 검증 로직
   - Signal 변환 로직

**산출물**:

- 중복 코드 80% 이상 제거
- 재사용 가능한 유틸리티 모듈

---

#### Step 3: 테스트 커버리지 개선 (3-4일)

**문제점**:

- 일부 신규 기능에 테스트 부족
- 통합 테스트 부족

**작업 내용**:

1. **커버리지 측정**

   ```bash
   cd backend
   uv run pytest --cov=app --cov-report=html
   # 목표: 85%+ 커버리지
   ```

2. **테스트 추가 우선순위**:

   - Phase 1에서 이동한 파일들 (서비스, 라우트)
   - 복잡한 비즈니스 로직
   - Edge cases

3. **통합 테스트 강화**:
   - E2E 백테스트 시나리오
   - ML Pipeline 테스트
   - API 통합 테스트

**산출물**:

- 테스트 커버리지 85%+
- 통합 테스트 30+ 개

---

#### Step 4: 문서화 및 타입 안정성 (2-3일)

**문제점**:

- 일부 함수에 타입 힌트 부족
- Docstring 불완전

**작업 내용**:

1. **타입 힌트 완성**

   ```bash
   # mypy strict mode 적용
   uv run mypy app/ --strict
   ```

2. **Docstring 표준화**

   - Google Style Docstring
   - 파라미터, 리턴값, 예외 명시

3. **API 문서 개선**
   - OpenAPI 스키마 description 추가
   - Examples 추가

**산출물**:

- mypy strict mode 통과
- 모든 public 함수 docstring 완비

---

### Phase 2 성공 지표

| 지표                      | 현재 (Phase 1 완료) | 목표 (Phase 2 완료) | 측정 방법       |
| ------------------------- | ------------------- | ------------------- | --------------- |
| **200+ lines 파일**       | 0개                 | 0개 (유지)          | `wc -l`         |
| **100+ lines 함수**       | 5+                  | 0개                 | `radon cc`      |
| **중복 코드 (CPD)**       | 15%                 | 5% 이하             | `pmd cpd`       |
| **테스트 커버리지**       | 80%                 | 85%+                | `pytest --cov`  |
| **타입 힌트 커버리지**    | 70%                 | 95%+                | `mypy --strict` |
| **Cyclomatic Complexity** | 평균 15             | 평균 10 이하        | `radon cc`      |

---

### Phase 2 실행 가이드

#### 시작 전 준비

```bash
# 1. 현재 상태 스냅샷
cd backend
uv run pytest --cov=app --cov-report=html
uv run radon cc app/ -a
uv run mypy app/ --strict | tee mypy_baseline.txt

# 2. Phase 2 브랜치 생성
git checkout -b phase2-code-quality-improvement
```

#### Step별 검증

**Step 1 완료 후**:

```bash
# 파일 크기 확인
find app -name "*.py" -exec wc -l {} \; | sort -rn | head -20

# 테스트 통과
uv run pytest

# OpenAPI 재생성
cd ../frontend && pnpm gen:client
```

**Step 2 완료 후**:

```bash
# 중복 코드 확인
pmd cpd --minimum-tokens 50 --files app/

# 유틸리티 모듈 임포트 확인
grep -r "from app.utils" app/ | wc -l
```

**Step 3 완료 후**:

```bash
# 커버리지 확인
uv run pytest --cov=app --cov-report=term-missing

# 통합 테스트 실행
uv run pytest tests/ -m e2e
```

**Step 4 완료 후**:

```bash
# mypy strict mode
uv run mypy app/ --strict

# Docstring 확인
pydocstyle app/
```

---

### Phase 2 위험 관리

| 위험                      | 영향 | 가능성 | 대응                             |
| ------------------------- | ---- | ------ | -------------------------------- |
| **리팩토링 중 버그 유입** | 높음 | 중간   | 각 Step마다 전체 테스트 실행     |
| **테스트 작성 시간 초과** | 중간 | 높음   | 핵심 로직 우선, 80% 달성 후 중단 |
| **타입 힌트 적용 어려움** | 낮음 | 중간   | strict mode는 점진적 적용        |
| **팀원 코드 리뷰 부담**   | 중간 | 낮음   | PR 단위 작게 분할                |

---

### Phase 2와 Phase 3-4의 차이

| 항목          | Phase 2 (진행 예정)         | Phase 3-4 (전체 개발 완료 후) |
| ------------- | --------------------------- | ----------------------------- |
| **목표**      | 코드 품질 개선, 레거시 정리 | MSA 전환, 인프라 구축         |
| **범위**      | 모노리스 내부 리팩토링      | 서비스 분리, 배포 파이프라인  |
| **변경 수준** | 내부 구조만 변경 (API 불변) | 외부 아키텍처 변경            |
| **배포 영향** | 없음 (기존 배포 방식 유지)  | 큼 (Kubernetes, Gateway 필요) |
| **소요 시간** | 2-3주                       | 2-3개월                       |
| **선행 조건** | Phase 1 완료                | 전체 기능 개발 완료           |

**Phase 2는 개발 진행 중에도 가능**, Phase 3-4는 **전체 개발 완료 후**
진행합니다.

---

## 참고 자료

### 내부 문서

- [PHASE0_CURRENT_ANALYSIS.md](./PHASE0_CURRENT_ANALYSIS.md): 현황 분석
- [PHASE1_MASTER_PLAN.md](./PHASE1_MASTER_PLAN.md): 마스터 플랜
- [PHASE1_STEP1_ENUM_CONSOLIDATION.md](./PHASE1_STEP1_ENUM_CONSOLIDATION.md):
  Step 1 가이드

### 외부 참고

- [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html) -
  Martin Fowler
- [Microservices Patterns](https://microservices.io/patterns/index.html) - Chris
  Richardson
- [Beanie ODM Docs](https://beanie-odm.dev/) - MongoDB ODM
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/bigger-applications/) -
  FastAPI 공식 문서

---

**프로젝트 Owner**: Backend 리드  
**문서 작성일**: 2025-01-15  
**최종 업데이트**: 2025-01-15
