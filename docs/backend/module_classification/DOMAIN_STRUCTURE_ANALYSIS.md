# Domain Structure Analysis - 중복 디렉토리 분석 및 통합 계획

**작성일**: 2025-10-15  
**목적**: services/ 및 routes/에서 중복/혼란 가능성 있는 디렉토리 구조 분석 및
개선

---

## 1. 현황 분석

### 1.1 Services Layer 디렉토리 구조

```
backend/app/services/
├── gen_ai/                    # 🔴 Gen AI 도메인 (OpenAI 기반 고급 기능)
│   ├── chatops_advanced_service.py
│   ├── narrative_report_service.py
│   └── strategy_builder_service.py
├── llm/                       # 🔴 LLM 도메인 (자체 구현 에이전트)
│   ├── chatops_agent.py
│   └── prompt_governance_service.py
├── ml/                        # 🟡 ML 핵심 엔진 (Phase 3.2)
│   ├── anomaly_detector.py
│   ├── feature_engineer.py
│   ├── model_registry.py
│   └── trainer.py
├── ml_platform/               # 🟡 ML 플랫폼 서비스 (Phase 4)
│   ├── evaluation_harness_service.py
│   ├── feature_store_service.py
│   ├── ml_signal_service.py
│   ├── model_lifecycle_service.py
│   ├── probabilistic_kpi_service.py
│   └── regime_detection_service.py
├── trading/
├── user/
└── ...
```

### 1.2 Routes Layer 디렉토리 구조

```
backend/app/api/routes/
├── gen_ai/
│   ├── chatops.py             # 🔴 기본 ChatOps (llm/chatops_agent 사용)
│   ├── chatops_advanced.py    # 🔴 고급 ChatOps (gen_ai/chatops_advanced_service 사용)
│   ├── narrative.py
│   ├── prompt_governance.py
│   └── strategy_builder.py
├── ml_platform/
│   ├── feature_store.py
│   └── ml/
│       ├── evaluation.py
│       ├── lifecycle.py
│       └── train.py           # ml/ 엔진 사용 (trainer, feature_engineer)
└── ...
```

---

## 2. 문제점 분석

### 🔴 Issue 1: `gen_ai/` vs `llm/` 중복

**현황**:

- **`services/gen_ai/`**: OpenAI API 기반 고급 기능 (Phase 3 D3)
  - `chatops_advanced_service.py`: Multi-turn 대화, 전략 비교, 자동 백테스트
  - `narrative_report_service.py`: 백테스트 결과 자연어 보고서
  - `strategy_builder_service.py`: 자연어로 전략 생성
- **`services/llm/`**: 자체 구현 에이전트 (Phase 3)
  - `chatops_agent.py`: 운영 진단 에이전트 (도구 기반, 권한 관리)
  - `prompt_governance_service.py`: 프롬프트 템플릿 관리

**문제점**:

1. **도메인 경계 불명확**: 둘 다 LLM을 사용하지만 목적이 다름
2. **의존성 혼란**:
   - `routes/gen_ai/chatops.py` → `services/llm/chatops_agent.py` 사용
   - `routes/gen_ai/chatops_advanced.py` →
     `services/gen_ai/chatops_advanced_service.py` 사용
3. **확장성 문제**: 새로운 LLM 기능을 어디에 추가해야 할지 불명확

**근본 원인**:

- `gen_ai/`: **"무엇을 제공하는가"** (기능 중심) - 자연어 기반 고급 기능
- `llm/`: **"어떻게 구현하는가"** (기술 중심) - LLM 기반 에이전트 구현

---

### 🟡 Issue 2: `ml/` vs `ml_platform/` 중복

**현황**:

- **`services/ml/`**: ML 핵심 엔진 (Phase 3.2)
  - `trainer.py`: LightGBM 모델 학습
  - `feature_engineer.py`: 기술 지표 계산
  - `model_registry.py`: 모델 버전 관리
  - `anomaly_detector.py`: 이상 탐지
- **`services/ml_platform/`**: ML 플랫폼 서비스 (Phase 4)
  - `model_lifecycle_service.py`: MLflow 기반 실험/배포 관리
  - `feature_store_service.py`: 피처 저장소
  - `ml_signal_service.py`: ML 기반 거래 신호 생성
  - `evaluation_harness_service.py`: 모델 평가 프레임워크
  - `regime_detection_service.py`: 시장 국면 탐지
  - `probabilistic_kpi_service.py`: 확률적 KPI

**문제점**:

1. **계층 혼재**:
   - `ml/`: 저수준 ML 엔진 (알고리즘, 학습)
   - `ml_platform/`: 고수준 비즈니스 서비스 (신호 생성, 국면 탐지)
2. **의존성 방향**: `ml_platform/` → `ml/` (올바름)
3. **명명 혼란**: 둘 다 "ML"을 포함하여 차이가 불명확

**근본 원인**:

- `ml/`: **"ML 알고리즘 구현"** (인프라 계층)
- `ml_platform/`: **"ML 기반 비즈니스 기능"** (서비스 계층)

---

### 🟠 Issue 3: `chatops.py` vs `chatops_advanced.py` 분리

**현황**:

- **`routes/gen_ai/chatops.py`** (30 lines):

  ```python
  @router.post("/", response_model=ChatOpsResponse)
  async def execute_chatops(request: ChatOpsRequest) -> ChatOpsResponse:
      agent = service_factory.get_chatops_agent()  # llm/chatops_agent
      result = await agent.run(request.question, request.user_roles)
      return ChatOpsResponse(...)
  ```

  - 기능: 운영 진단 (캐시 상태, 데이터 품질, 실패 분석)
  - 구현: 도구 기반 에이전트 (get_cache_status, get_data_quality 등)
  - 권한: 역할 기반 도구 접근 제어

- **`routes/gen_ai/chatops_advanced.py`** (338 lines):

  ```python
  @router.post("/chat", response_model=ChatSession)
  async def chat_with_context(request: ChatOpsRequest):
      service = service_factory.get_chatops_advanced_service()  # gen_ai/chatops_advanced
      session = await service.chat_with_context(...)
      return session

  @router.post("/compare-strategies", response_model=StrategyComparisonResult)
  async def compare_strategies(request: StrategyComparisonRequest):
      ...

  @router.post("/auto-backtest", response_model=AutoBacktestResponse)
  async def auto_backtest(request: AutoBacktestRequest, background_tasks: BackgroundTasks):
      ...
  ```

  - 기능: 대화형 전략 분석, 전략 비교, 자동 백테스트
  - 구현: OpenAI GPT 기반 멀티턴 대화
  - 세션: MongoDB 기반 대화 이력 저장

**문제점**:

1. **기능적 차이는 명확함**:
   - `chatops.py`: 시스템 운영/모니터링 (DevOps)
   - `chatops_advanced.py`: 전략 분석/백테스트 (Quant)
2. **명명 문제**: "advanced"는 기능의 차이를 표현하지 못함
3. **도메인 분리 필요**: 서로 다른 유저 페르소나

---

## 3. 개선 방안

### 3.1 Proposal A: `gen_ai/` 통합 (권장 ✅)

**구조**:

```
services/
├── gen_ai/                    # 통합: 모든 LLM 기반 기능
│   ├── agents/               # 에이전트 구현 (기존 llm/)
│   │   ├── __init__.py
│   │   ├── chatops_agent.py          # 운영 진단
│   │   └── prompt_governance.py      # 프롬프트 관리
│   ├── applications/         # 고급 애플리케이션 (기존 gen_ai/)
│   │   ├── __init__.py
│   │   ├── chatops_advanced.py       # 대화형 분석
│   │   ├── narrative_report.py
│   │   └── strategy_builder.py
│   └── __init__.py
├── ml_platform/              # 유지: ML 비즈니스 서비스
│   ├── infrastructure/       # 새 서브디렉토리: 핵심 엔진 (기존 ml/)
│   │   ├── __init__.py
│   │   ├── trainer.py
│   │   ├── feature_engineer.py
│   │   ├── model_registry.py
│   │   └── anomaly_detector.py
│   ├── services/             # 기존 서비스들
│   │   ├── __init__.py
│   │   ├── model_lifecycle.py
│   │   ├── feature_store.py
│   │   ├── ml_signal.py
│   │   ├── evaluation_harness.py
│   │   ├── regime_detection.py
│   │   └── probabilistic_kpi.py
│   └── __init__.py
└── ...
```

**Routes 구조**:

```
api/routes/
├── gen_ai/
│   ├── operations/           # 운영/모니터링 ChatOps
│   │   ├── __init__.py
│   │   └── chatops.py        # → gen_ai/agents/chatops_agent
│   ├── analytics/            # 분석/전략 ChatOps
│   │   ├── __init__.py
│   │   └── chatops.py        # → gen_ai/applications/chatops_advanced
│   ├── narrative.py
│   ├── prompt_governance.py
│   └── strategy_builder.py
└── ml_platform/
    ├── feature_store.py
    └── ml/
        ├── train.py          # → ml_platform/infrastructure/trainer
        ├── evaluation.py
        └── lifecycle.py
```

**장점**:

- ✅ 명확한 계층 구조 (`agents/` vs `applications/`)
- ✅ Gen AI 도메인 통합 (LLM 관련 모든 기능)
- ✅ ML Platform 내부 정리 (`infrastructure/` vs `services/`)
- ✅ Routes에서 기능별 분리 (`operations/` vs `analytics/`)

**단점**:

- ⚠️ 대규모 파일 이동 (10+ 파일)
- ⚠️ Import 경로 변경 필요 (테스트 포함)

---

### 3.2 Proposal B: `llm/` → `gen_ai/core/` 이동 (중간안)

**구조**:

```
services/
├── gen_ai/
│   ├── core/                 # 기존 llm/ 이동
│   │   ├── chatops_agent.py
│   │   └── prompt_governance_service.py
│   ├── chatops_advanced_service.py
│   ├── narrative_report_service.py
│   └── strategy_builder_service.py
├── ml_platform/
│   ├── core/                 # 기존 ml/ 이동
│   │   ├── trainer.py
│   │   ├── feature_engineer.py
│   │   ├── model_registry.py
│   │   └── anomaly_detector.py
│   ├── model_lifecycle_service.py
│   └── ...
```

**장점**:

- ✅ 중복 제거 (llm/, ml/ 삭제)
- ✅ 최소 변경 (기존 구조 유지)

**단점**:

- ❌ `core/` 의미 모호 (핵심? 기초?)
- ❌ Routes 분리 문제 미해결

---

### 3.3 Proposal C: 현상 유지 + 문서화 (최소 변경)

**방안**:

- `llm/` → 이름 변경 → `gen_ai_infrastructure/`
- `ml/` → 이름 변경 → `ml_core/`
- README 추가하여 목적 명시

**장점**:

- ✅ 최소 코드 변경

**단점**:

- ❌ 근본 문제 미해결
- ❌ 여전히 혼란 가능

---

## 4. 권장 사항 (Proposal A 상세)

### 4.1 Phase 2.5: Domain Consolidation (1주)

**Step 1: Gen AI 통합** (2-3일)

```bash
# 1. 새 디렉토리 생성
mkdir -p backend/app/services/gen_ai/agents
mkdir -p backend/app/services/gen_ai/applications

# 2. llm/ → gen_ai/agents/ 이동
mv backend/app/services/llm/chatops_agent.py \
   backend/app/services/gen_ai/agents/
mv backend/app/services/llm/prompt_governance_service.py \
   backend/app/services/gen_ai/agents/

# 3. gen_ai/*.py → gen_ai/applications/ 이동
mv backend/app/services/gen_ai/chatops_advanced_service.py \
   backend/app/services/gen_ai/applications/
mv backend/app/services/gen_ai/narrative_report_service.py \
   backend/app/services/gen_ai/applications/
mv backend/app/services/gen_ai/strategy_builder_service.py \
   backend/app/services/gen_ai/applications/

# 4. llm/ 디렉토리 삭제
rmdir backend/app/services/llm

# 5. Import 경로 수정 (자동화)
find backend -name "*.py" -type f -exec sed -i '' \
  's|from app.services.llm|from app.services.gen_ai.agents|g' {} +
find backend -name "*.py" -type f -exec sed -i '' \
  's|from app.services.gen_ai.chatops_advanced_service|from app.services.gen_ai.applications.chatops_advanced|g' {} +
```

**Step 2: ML Platform 통합** (2-3일)

```bash
# 1. 새 디렉토리 생성
mkdir -p backend/app/services/ml_platform/infrastructure
mkdir -p backend/app/services/ml_platform/services

# 2. ml/ → ml_platform/infrastructure/ 이동
mv backend/app/services/ml/*.py \
   backend/app/services/ml_platform/infrastructure/

# 3. 기존 서비스 → ml_platform/services/ 이동
mv backend/app/services/ml_platform/*_service.py \
   backend/app/services/ml_platform/services/

# 4. ml/ 디렉토리 삭제
rmdir backend/app/services/ml

# 5. Import 경로 수정
find backend -name "*.py" -type f -exec sed -i '' \
  's|from app.services.ml import|from app.services.ml_platform.infrastructure import|g' {} +
find backend -name "*.py" -type f -exec sed -i '' \
  's|from app.services.ml.|from app.services.ml_platform.infrastructure.|g' {} +
```

**Step 3: Routes 정리** (1-2일)

```bash
# 1. Gen AI routes 분리
mkdir -p backend/app/api/routes/gen_ai/operations
mkdir -p backend/app/api/routes/gen_ai/analytics

# 2. chatops 분리
mv backend/app/api/routes/gen_ai/chatops.py \
   backend/app/api/routes/gen_ai/operations/
mv backend/app/api/routes/gen_ai/chatops_advanced.py \
   backend/app/api/routes/gen_ai/analytics/chatops.py

# 3. Router 재구성
# (수동 작업 - routes/__init__.py 수정)
```

---

### 4.2 서비스 명명 규칙

**Gen AI Domain**:

- `agents/`: 도구 기반 에이전트 (ChatOps, Governance)
- `applications/`: 복합 애플리케이션 (Strategy Builder, Narrative)

**ML Platform Domain**:

- `infrastructure/`: ML 엔진 (Trainer, Feature Engineer, Registry)
- `services/`: 비즈니스 서비스 (Signal, Regime, KPI)

---

### 4.3 Import 패턴 정리

**Before**:

```python
# 혼란스러운 import
from app.services.llm.chatops_agent import ChatOpsAgent
from app.services.gen_ai.chatops_advanced_service import ChatOpsAdvancedService
from app.services.ml import MLModelTrainer
from app.services.ml_platform.ml_signal_service import MLSignalService
```

**After**:

```python
# 명확한 import
from app.services.gen_ai.agents.chatops_agent import ChatOpsAgent
from app.services.gen_ai.applications.chatops_advanced import ChatOpsAdvancedService
from app.services.ml_platform.infrastructure.trainer import MLModelTrainer
from app.services.ml_platform.services.ml_signal import MLSignalService
```

---

## 5. 의존성 분석

### 5.1 Gen AI 의존성 그래프

```
routes/gen_ai/operations/chatops
  └─> services/gen_ai/agents/chatops_agent
        ├─> database_manager
        ├─> market_data_service
        └─> monitoring/data_quality_sentinel

routes/gen_ai/analytics/chatops
  └─> services/gen_ai/applications/chatops_advanced
        ├─> trading/backtest_service
        └─> OpenAI API
```

**영향 범위**:

- Service files: 5개
- Route files: 5개
- Test files: 3개

---

### 5.2 ML Platform 의존성 그래프

```
routes/ml_platform/ml/train
  └─> services/ml_platform/infrastructure/trainer
        └─> services/ml_platform/infrastructure/feature_engineer

routes/ml_platform/ml/lifecycle
  └─> services/ml_platform/services/model_lifecycle
        ├─> services/ml_platform/infrastructure/model_registry
        └─> MLflow (optional)

services/ml_platform/services/ml_signal
  └─> services/ml_platform/infrastructure/trainer
```

**영향 범위**:

- Service files: 10개
- Route files: 4개
- Test files: 8개

---

## 6. 잠재적 문제 및 대응

### 6.1 Import 순환 의존성

**위험**: `gen_ai/agents/` ↔ `gen_ai/applications/` 순환 참조

**대응**:

- Agents는 Applications를 import하지 않음 (단방향)
- 필요시 Protocol/ABC로 인터페이스 분리

---

### 6.2 테스트 깨짐

**위험**: Import 경로 변경으로 테스트 실패

**대응**:

```bash
# 1. 변경 전 테스트 실행
uv run pytest

# 2. Import 경로 수정
find backend/tests -name "*.py" -exec sed -i '' \
  's|from app.services.llm|from app.services.gen_ai.agents|g' {} +

# 3. 변경 후 테스트 재실행
uv run pytest
```

---

### 6.3 Frontend 클라이언트 재생성

**위험**: Routes 변경으로 OpenAPI 스키마 변경

**대응**:

```bash
# Routes 경로만 변경 (엔드포인트 URL은 유지)
# 예: /gen_ai/chatops → /gen_ai/operations/chatops
# 또는 prefix로 통합: router.prefix = "/operations"

# 클라이언트 재생성
pnpm gen:client
```

---

## 7. 롤아웃 계획

### Phase 2.5 Timeline (1주)

| Day       | Task                                     | Validation                     |
| --------- | ---------------------------------------- | ------------------------------ |
| **Day 1** | Gen AI 통합 (llm/ → gen_ai/agents/)      | pytest (gen_ai 관련)           |
| **Day 2** | Gen AI applications/ 정리                | pytest (전체)                  |
| **Day 3** | ML Platform 통합 (ml/ → infrastructure/) | pytest (ml 관련)               |
| **Day 4** | ML Platform services/ 정리               | pytest (전체)                  |
| **Day 5** | Routes 재구성, OpenAPI 재생성            | pnpm gen:client, Frontend 빌드 |

---

### 검증 체크리스트

**Step 1 완료 후**:

- [ ] `services/llm/` 디렉토리 삭제 완료
- [ ] `services/gen_ai/agents/` 생성 및 파일 이동
- [ ] pytest (gen_ai 관련) 통과
- [ ] mypy 타입 체크 통과

**Step 2 완료 후**:

- [ ] `services/ml/` 디렉토리 삭제 완료
- [ ] `services/ml_platform/infrastructure/` 생성 및 파일 이동
- [ ] pytest (ml 관련) 통과
- [ ] Import 순환 의존성 없음

**Step 3 완료 후**:

- [ ] Routes 재구성 완료
- [ ] pnpm gen:client 성공
- [ ] Frontend 빌드 성공
- [ ] API 문서 정상 생성 (http://localhost:8500/docs)

---

## 8. 결론

### 권장 사항: Proposal A 채택

**이유**:

1. ✅ **명확한 도메인 경계**: `gen_ai/`, `ml_platform/` 단일 진입점
2. ✅ **계층 구조 명확화**: `agents/` vs `applications/`, `infrastructure/` vs
   `services/`
3. ✅ **확장성**: 새 기능 추가 시 명확한 위치
4. ✅ **일관성**: 모든 도메인에 동일한 패턴 적용

**리스크 관리**:

- 점진적 마이그레이션 (도메인별 단계적 진행)
- 각 단계마다 테스트 실행
- Git 태그로 롤백 포인트 확보

---

**다음 단계**:

1. ✅ 이 문서 리뷰 및 승인
2. 🔄 Phase 2.5 작업 시작 (Proposal A 실행)
3. 📋 완료 후 Phase 2 (Code Quality) 진행

---

**작성자**: Backend Team  
**상태**: 📋 검토 대기
