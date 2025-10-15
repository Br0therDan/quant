# Backend 모듈 재구조화 프로젝트

**프로젝트 시작일**: 2025-01-15  
**목적**: Phase 5 통합 전 백엔드 코드베이스 정리 및 MSA 전환 준비  
**상태**: 📋 계획 완료

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

| Step       | 작업                               | 소요 시간 | 상태         |
| ---------- | ---------------------------------- | --------- | ------------ |
| **Step 0** | 현황 분석 및 마스터 플랜 작성      | 2시간     | ✅ 완료      |
| **Step 1** | Enum 통합 (`schemas/enums.py`)     | 4시간     | 📋 준비 완료 |
| **Step 2** | 모델 파일 분리 (도메인별 디렉토리) | 6시간     | ⏸️ 대기      |
| **Step 3** | 스키마 재구조화 (모델과 동일 구조) | 4시간     | ⏸️ 대기      |
| **Step 4** | 서비스 & 엔드포인트 재구조화       | 12시간    | ⏸️ 대기      |
| **검증**   | 통합 테스트 + Frontend 빌드        | 2시간     | ⏸️ 대기      |

**총 예상 시간**: 30시간 (3-5 작업일)

### 주요 산출물

#### Before (현재)

```
backend/app/
├── models/            # 18개 파일 (평면 구조)
├── schemas/           # 18개 파일 (평면 구조)
├── services/          # 18개 파일 + 5개 하위 디렉토리
└── api/routes/        # 19개 파일 (불일치한 구조)
```

#### After (Phase 1 완료)

```
backend/app/
├── schemas/
│   ├── enums.py                    # ✨ 모든 Enum 통합 (200 lines)
│   ├── trading/                    # 🆕 도메인별 디렉토리
│   ├── market_data/
│   ├── ml_platform/
│   ├── gen_ai/
│   └── user/
├── models/
│   ├── trading/                    # 🆕 도메인별 디렉토리
│   ├── market_data/
│   ├── ml_platform/
│   ├── gen_ai/
│   └── user/
├── services/
│   ├── trading/                    # 🆕 도메인별 디렉토리
│   ├── market_data/
│   ├── ml_platform/
│   ├── gen_ai/
│   └── user/
└── api/routes/
    ├── system/                     # 🆕 시스템 엔드포인트
    ├── trading/                    # 🆕 도메인별 디렉토리
    ├── market_data/
    ├── ml_platform/
    ├── gen_ai/
    ├── user/
    └── admin/                      # 🆕 관리자 엔드포인트
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

## 성공 지표 (KPI)

| 지표                | 현재                       | 목표                                     | 측정 방법                               |
| ------------------- | -------------------------- | ---------------------------------------- | --------------------------------------- |
| **Enum 중복**       | 15+ 곳                     | 1곳                                      | `grep -r "class.*Type.*Enum"`           |
| **200+ lines 파일** | 8개                        | 0개                                      | `find . -name "*.py" -exec wc -l {} \;` |
| **도메인 디렉토리** | 2개 (market_data, chatops) | 4개 (trading, ml_platform, gen_ai, user) | `ls -d models/*/`                       |
| **명명 불일치**     | 5개                        | 0개                                      | 수동 검증                               |
| **TypeScript 에러** | 0개                        | 0개 (유지)                               | `pnpm build`                            |
| **Pytest 커버리지** | 80%+                       | 80%+ (유지)                              | `pytest --cov`                          |

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

## 다음 단계

### Phase 1 완료 후

**Phase 2: 레거시 통합 (1-2주)**

- Strategy ↔ ModelExperiment 관계 정의
- DataQualityMixin → DataQualityEvent 자동 생성
- 서비스 레이어 800+ lines 파일 분할

**Phase 3: MSA 전환 준비 (2-3주)**

- 도메인 간 이벤트 주도 통신 (RabbitMQ/Kafka)
- API Gateway 구성 (Kong/Nginx)
- 도메인별 독립 배포 파이프라인

**Phase 4: Production 배포**

- Kubernetes 클러스터 구성
- 서비스 메시 (Istio/Linkerd)
- 모니터링/로깅 통합 (Prometheus + Grafana)

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
