# Phase 1: OpenAI Client Manager

**목표**: 중앙화된 OpenAI 클라이언트 + 모델 선택 API  
**기간**: 2025-10-15 ~ 2025-10-29 (2주, 8일)  
**상태**: ⏳ **대기중**

---

## 🎯 Phase 목표

### 주요 목표

1. **중앙화**: AsyncOpenAI 클라이언트 싱글톤 관리
2. **모델 카탈로그**: 4개 모델 (gpt-4o-mini, gpt-4o, gpt-4-turbo, o1-preview)
3. **비용 최적화**: 서비스별 적절한 모델 선택 (30%+ 비용 절감)
4. **사용자 선택**: 모델 선택 API (2개 GET, 3개 POST 수정)
5. **토큰 추적**: 사용량 모니터링 기반 구축

### 완료 기준 (Definition of Done)

- ✅ OpenAIClientManager 구현 완료
- ✅ 3개 서비스 리팩토링 (중복 제거)
- ✅ 모델 선택 API 구현 (5개 엔드포인트)
- ✅ 단위 테스트 80%+ 커버리지
- ✅ 통합 테스트 통과 (회귀 테스트)
- ✅ 비용 절감 30%+ 검증
- ✅ Phase 1 완료 문서 작성

---

## 📅 Sprint 계획

### Sprint 1.1: OpenAIClientManager 구현 (2일)

**기간**: Day 1-2  
**목표**: 중앙화된 클라이언트 관리 구조 구축

#### Tasks

**T1.1.1: Enum 정의** (1시간)

- [ ] `ModelTier` Enum 생성 (MINI, STANDARD, ADVANCED, PREMIUM)
- [ ] `ModelCapability` Enum 생성 (CHAT, CODE_GENERATION, ANALYSIS, REASONING,
      VISION, FUNCTION_CALLING)

**T1.1.2: ModelConfig Pydantic 모델** (1시간)

- [ ] `ModelConfig` BaseModel 생성
  - `model_id: str`
  - `tier: ModelTier`
  - `capabilities: List[ModelCapability]`
  - `input_price_per_1m: float`
  - `output_price_per_1m: float`
  - `max_tokens: int`
  - `supports_rag: bool`
  - `description: str`

**T1.1.3: MODEL_CATALOG 작성** (2시간)

- [ ] `gpt-4o-mini` 설정 ($0.15/$0.60)
- [ ] `gpt-4o` 설정 ($2.50/$10.00)
- [ ] `gpt-4-turbo` 설정 ($10.00/$30.00)
- [ ] `o1-preview` 설정 ($15.00/$60.00)

**T1.1.4: OpenAIClientManager 클래스** (3시간)

- [ ] 싱글톤 패턴 구현 (`__new__`)
- [ ] AsyncOpenAI 클라이언트 초기화
- [ ] `get_client() -> AsyncOpenAI` 메서드
- [ ] `get_model_config(model_id: str) -> ModelConfig` 메서드

**T1.1.5: ServiceModelPolicy 구현** (2시간)

- [ ] `ServiceModelPolicy` Pydantic 모델
  - `service_name: str`
  - `allowed_tiers: List[ModelTier]`
  - `default_model: str`
  - `required_capabilities: List[ModelCapability]`
- [ ] 서비스별 정책 정의 (StrategyBuilder, NarrativeReport, ChatOpsAdvanced)

**T1.1.6: validate_model_for_service() 메서드** (2시간)

- [ ] 모델 ID 유효성 검증
- [ ] Tier 허용 여부 확인
- [ ] Capability 요구사항 확인
- [ ] 예외 처리 (InvalidModelError)

**T1.1.7: track_usage() 메서드** (2시간)

- [ ] 토큰 사용량 기록 (input_tokens, output_tokens)
- [ ] 비용 계산 (model_config 기반)
- [ ] 로그 저장 (structlog)
- [ ] (향후) MongoDB 저장 준비

#### 완료 조건

- ✅ `app/services/gen_ai/core/openai_client_manager.py` 생성
- ✅ 4개 모델 카탈로그 완성
- ✅ 단위 테스트 작성 (싱글톤, 모델 검증, 정책)

---

### Sprint 1.2: 기존 서비스 리팩토링 (3일)

**기간**: Day 3-5  
**목표**: 중복 AsyncOpenAI 초기화 제거

#### Tasks

**T1.2.1: StrategyBuilderService 리팩토링** (1일)

- [ ] `AsyncOpenAI()` 제거
- [ ] `OpenAIClientManager` 주입 (ServiceFactory)
- [ ] `self.client = self.openai_manager.get_client()`
- [ ] `default_model = "gpt-4o-mini"` 설정
- [ ] 기존 메서드 수정 (`build_strategy()`)
- [ ] 단위 테스트 수정

**T1.2.2: NarrativeReportService 리팩토링** (1일)

- [ ] `AsyncOpenAI()` 제거
- [ ] `OpenAIClientManager` 주입
- [ ] `self.client = self.openai_manager.get_client()`
- [ ] `default_model = "gpt-4o"` 설정
- [ ] 기존 메서드 수정 (`generate_report()`)
- [ ] 단위 테스트 수정

**T1.2.3: ChatOpsAdvancedService 리팩토링** (1일)

- [ ] `AsyncOpenAI()` 제거
- [ ] `OpenAIClientManager` 주입
- [ ] `self.client = self.openai_manager.get_client()`
- [ ] `default_model = "gpt-4o"` 설정
- [ ] 기존 메서드 수정 (`chat()`, `compare_strategies()`)
- [ ] 단위 테스트 수정

**T1.2.4: ServiceFactory 통합** (2시간)

- [ ] `get_openai_client_manager()` 메서드 추가
- [ ] 싱글톤 인스턴스 캐싱
- [ ] 기존 서비스에 주입 로직 추가

**T1.2.5: 회귀 테스트** (2시간)

- [ ] 전체 테스트 스위트 실행
- [ ] API 엔드포인트 테스트 (Postman/curl)
- [ ] 응답 검증 (기존과 동일)

#### 완료 조건

- ✅ 3개 서비스 리팩토링 완료
- ✅ 중복 초기화 제거 (3회 → 1회)
- ✅ 모든 기존 테스트 통과
- ✅ API 응답 정상 작동

---

### Sprint 1.3: 모델 선택 API 추가 (2일)

**기간**: Day 6-7  
**목표**: 사용자 모델 선택 기능 구현

#### Tasks

**T1.3.1: Schemas 정의** (2시간)

- [ ] `ModelInfo` Pydantic 모델
  - `model_id: str`
  - `tier: str`
  - `capabilities: List[str]`
  - `input_price_per_1m: float`
  - `output_price_per_1m: float`
  - `description: str`
- [ ] `ModelListResponse` Pydantic 모델
  - `models: List[ModelInfo]`
  - `total: int`
- [ ] `ServiceModelPolicyResponse` Pydantic 모델
  - `service_name: str`
  - `allowed_models: List[ModelInfo]`
  - `default_model: str`

**T1.3.2: GET API 구현** (3시간)

- [ ] `GET /api/v1/gen-ai/models` - 전체 모델 목록
  - 쿼리 파라미터: `tier: Optional[str]`
  - 응답: `ModelListResponse`
- [ ] `GET /api/v1/gen-ai/models/{service_name}` - 서비스별 허용 모델
  - 경로 파라미터: `service_name: str`
  - 응답: `ServiceModelPolicyResponse`

**T1.3.3: POST API 수정** (4시간)

- [ ] `StrategyBuilderRequest`에 `model_id: Optional[str]` 추가
- [ ] `ChatRequest`에 `model_id: Optional[str]` 추가
- [ ] `NarrativeReportRequest`에 `model_id: Optional[str]` 추가
- [ ] 각 엔드포인트에 모델 검증 로직 추가

**T1.3.4: 모델 검증 로직 통합** (2시간)

- [ ] `validate_model_for_service()` 호출
- [ ] 유효하지 않은 모델 시 400 에러
- [ ] 에러 메시지 명확화 ("Model X not allowed for service Y")

**T1.3.5: API 테스트** (2시간)

- [ ] Postman 컬렉션 업데이트
- [ ] 각 API 엔드포인트 테스트
- [ ] OpenAPI 스키마 검증 (`pnpm gen:client`)

#### 완료 조건

- ✅ 2개 GET API 구현
- ✅ 3개 POST API 수정
- ✅ 모델 검증 로직 작동
- ✅ OpenAPI 스키마 업데이트

---

### Sprint 1.4: Phase 1 통합 테스트 (1일)

**기간**: Day 8  
**목표**: 전체 Phase 1 검증

#### Tasks

**T1.4.1: E2E 테스트 시나리오** (2시간)

- [ ] 시나리오 1: 모델 목록 조회 → gpt-4o-mini 선택 → 전략 생성
- [ ] 시나리오 2: 잘못된 모델 선택 → 400 에러 확인
- [ ] 시나리오 3: 서비스별 허용 모델 조회 → 검증

**T1.4.2: 비용 절감 검증** (2시간)

- [ ] gpt-4 사용 시나리오 (기존)
- [ ] gpt-4o-mini 사용 시나리오 (개선)
- [ ] 비용 계산 (토큰 추적 로그 기반)
- [ ] 30%+ 절감 확인

**T1.4.3: 토큰 추적 로그 확인** (1시간)

- [ ] 로그 출력 확인 (structlog)
- [ ] input_tokens, output_tokens 정확성
- [ ] 비용 계산 정확성
- [ ] (향후) MongoDB 저장 준비

**T1.4.4: 성능 벤치마크** (2시간)

- [ ] API 응답 시간 측정 (100회 평균)
- [ ] OpenAI API 호출 시간
- [ ] 오버헤드 < 10ms 확인

#### 완료 조건

- ✅ E2E 테스트 통과
- ✅ 비용 절감 30%+ 달성
- ✅ 토큰 추적 정확도 95%+
- ✅ 성능 저하 < 10ms

---

## 📦 산출물 (Deliverables)

### 코드

- [ ] `backend/app/services/gen_ai/core/openai_client_manager.py` (500+ lines)
- [ ] `backend/app/services/gen_ai/core/__init__.py` (exports)
- [ ] `backend/app/services/gen_ai/strategy_builder.py` (리팩토링)
- [ ] `backend/app/services/gen_ai/narrative_report.py` (리팩토링)
- [ ] `backend/app/services/gen_ai/chatops_advanced.py` (리팩토링)
- [ ] `backend/app/api/routes/gen_ai/models.py` (신규, 2개 GET API)
- [ ] `backend/app/schemas/gen_ai/models.py` (신규, 모델 관련 스키마)

### 테스트

- [ ] `backend/tests/services/gen_ai/test_openai_client_manager.py` (단위)
- [ ] `backend/tests/api/test_gen_ai_models.py` (통합)
- [ ] `backend/tests/integration/test_phase1_e2e.py` (E2E)

### 문서

- [ ] `docs/backend/gen_ai_enhancement/phase1/PHASE1_COMPLETION_REPORT.md`
- [ ] API 문서 업데이트 (OpenAPI 스키마)

---

## 🚨 리스크 및 완화 전략

| 리스크                    | 완화 전략                          | 담당자  |
| ------------------------- | ---------------------------------- | ------- |
| 기존 서비스 회귀 버그     | 리팩토링 전 전체 테스트 실행       | Backend |
| OpenAI API Rate Limit     | Rate Limiting 미들웨어 추가        | Backend |
| 토큰 추적 정확도 낮음     | OpenAI 응답 `usage` 필드 검증      | Backend |
| 모델 선택 UI 미구현       | Phase 1에서 API만 구현 (UI는 차후) | PM      |
| 서비스별 정책 관리 복잡도 | YAML 설정 파일 분리 (향후 고려)    | Backend |

---

## 🔗 관련 문서

- [Master Plan](../MASTER_PLAN.md)
- [Dashboard](../DASHBOARD.md)
- [설계 문서](../../GENAI_OPENAI_CLIENT_DESIGN.md)

---

**마지막 업데이트**: 2025-10-15
