# GenAI Enhancement Master Plan

**프로젝트**: OpenAI 클라이언트 중앙화 + RAG 통합  
**시작일**: 2025-10-15  
**예상 완료**: 2025-11-15 (4주)  
**목표**: 비용 50-80% 절감 + 응답 품질 개선

---

## 📊 프로젝트 개요

### 목적

1. **비용 최적화**: OpenAI API 비용 50-80% 절감 (월 $100 → $20-50)
2. **응답 품질**: RAG 기반 사용자 컨텍스트 활용 (개인화 응답)
3. **유지보수성**: 중앙화된 클라이언트 관리 (3회 중복 → 1회)
4. **확장성**: 모델 선택 API (사용자 맞춤 모델)

### 주요 산출물

- `OpenAIClientManager`: 싱글톤 클라이언트 + 모델 카탈로그
- `RAGService`: ChromaDB 기반 벡터 검색
- 모델 선택 API: 5개 엔드포인트
- 기존 서비스 리팩토링: 3개 서비스

---

## 🗓️ Phase & Sprint 구조

### Phase 1: OpenAI Client Manager (2주)

**목표**: 중앙화된 클라이언트 + 모델 선택 API  
**기간**: 2025-10-15 ~ 2025-10-29  
**상태**: ⏳ **대기중**

#### Sprint 1.1: OpenAIClientManager 구현 (2일)

**기간**: Day 1-2  
**상태**: ⏳ **대기중**

**Tasks**:

- [ ] T1.1.1: ModelTier, ModelCapability Enum 정의
- [ ] T1.1.2: ModelConfig Pydantic 모델 생성
- [ ] T1.1.3: MODEL_CATALOG 딕셔너리 작성 (4개 모델)
- [ ] T1.1.4: OpenAIClientManager 클래스 구현
  - [ ] 싱글톤 패턴 (`__new__`)
  - [ ] AsyncOpenAI 클라이언트 초기화
  - [ ] `get_client()` 메서드
- [ ] T1.1.5: 서비스별 정책 (ServiceModelPolicy) 구현
- [ ] T1.1.6: `validate_model_for_service()` 메서드
- [ ] T1.1.7: 토큰 추적 (`track_usage()`) 메서드

**완료 조건**:

- ✅ OpenAIClientManager 클래스 생성 완료
- ✅ 4개 모델 카탈로그 정의 (gpt-4o-mini, gpt-4o, gpt-4-turbo, o1-preview)
- ✅ 단위 테스트 작성 (싱글톤, 모델 검증)

#### Sprint 1.2: 기존 서비스 리팩토링 (3일)

**기간**: Day 3-5  
**상태**: ⏳ **대기중**

**Tasks**:

- [ ] T1.2.1: StrategyBuilderService 리팩토링
  - [ ] AsyncOpenAI() 제거
  - [ ] OpenAIClientManager 주입
  - [ ] default_model 설정
- [ ] T1.2.2: NarrativeReportService 리팩토링
  - [ ] AsyncOpenAI() 제거
  - [ ] OpenAIClientManager 주입
  - [ ] default_model 설정
- [ ] T1.2.3: ChatOpsAdvancedService 리팩토링
  - [ ] AsyncOpenAI() 제거
  - [ ] OpenAIClientManager 주입
  - [ ] default_model 설정
- [ ] T1.2.4: ServiceFactory 통합
  - [ ] `get_openai_client_manager()` 메서드 추가
- [ ] T1.2.5: 기존 API 테스트 (회귀 테스트)

**완료 조건**:

- ✅ 3개 서비스 리팩토링 완료
- ✅ 기존 API 정상 작동 확인
- ✅ 중복 초기화 제거 확인 (3회 → 1회)

#### Sprint 1.3: 모델 선택 API 추가 (2일)

**기간**: Day 6-7  
**상태**: ⏳ **대기중**

**Tasks**:

- [ ] T1.3.1: Schemas 정의
  - [ ] ModelListResponse
  - [ ] ModelSelectionRequest
- [ ] T1.3.2: API 엔드포인트 구현
  - [ ] `GET /api/v1/gen-ai/models` (모델 목록)
  - [ ] `GET /api/v1/gen-ai/models/{service_name}` (서비스별 허용 모델)
- [ ] T1.3.3: 기존 POST 엔드포인트 수정
  - [ ] StrategyBuilderRequest에 `model_id: Optional[str]` 추가
  - [ ] ChatRequest에 `model_id: Optional[str]` 추가
  - [ ] NarrativeReportRequest에 `model_id: Optional[str]` 추가
- [ ] T1.3.4: 모델 검증 로직 통합
- [ ] T1.3.5: API 테스트

**완료 조건**:

- ✅ 2개 GET API, 3개 POST API 수정 완료
- ✅ 모델 검증 로직 작동 확인
- ✅ OpenAPI 스키마 업데이트

#### Sprint 1.4: Phase 1 통합 테스트 (1일)

**기간**: Day 8  
**상태**: ⏳ **대기중**

**Tasks**:

- [ ] T1.4.1: E2E 테스트 시나리오 작성
- [ ] T1.4.2: 비용 절감 검증 (gpt-4 → gpt-4o-mini)
- [ ] T1.4.3: 토큰 추적 로그 확인
- [ ] T1.4.4: 성능 벤치마크 (응답 시간)

**완료 조건**:

- ✅ 모든 API 정상 작동
- ✅ 비용 절감 30%+ 달성 확인
- ✅ Phase 1 완료 문서 작성

---

### Phase 2: RAG Integration (2주)

**목표**: ChromaDB 기반 사용자 데이터 컨텍스트
**기간**: 2025-10-30 ~ 2025-11-12
**상태**: ✅ **완료** (2025-11-12)

#### Sprint 2.1: RAGService 구현 (2일)

**기간**: Day 9-10
**상태**: ✅ **완료** (Day 10)

**Tasks**:

- [x] T2.1.1: ChromaDB 의존성 추가 (`uv add chromadb`)
- [x] T2.1.2: RAGService 클래스 생성
  - [x] ChromaDB 클라이언트 초기화 (duckdb+parquet)
  - [x] 컬렉션 생성 (`user_backtests`, `user_strategies`)
- [x] T2.1.3: `index_backtest_result()` 메서드
  - [x] 백테스트 결과 → 텍스트 변환
  - [x] OpenAI Embedding API 호출 (text-embedding-3-large)
  - [x] ChromaDB 인덱싱
- [x] T2.1.4: `search_similar_backtests()` 메서드
  - [x] 쿼리 임베딩
  - [x] 유사도 검색 (top_k=5)
- [x] T2.1.5: `build_rag_prompt()` 메서드
  - [x] 검색 결과 → 프롬프트 컨텍스트 템플릿화

**완료 조건**:

- ✅ RAGService 클래스 구현 완료
- ✅ ChromaDB 정상 작동 확인
- ✅ 인덱싱/검색 단위 테스트

#### Sprint 2.2: RAG 서비스 통합 (3일)

**기간**: Day 11-13
**상태**: ✅ **완료** (Day 13)

**Tasks**:

- [x] T2.2.1: StrategyBuilderService 통합
  - [x] RAGService 주입
  - [x] `generate_strategy_with_rag()` 메서드 추가
  - [x] 유사 전략 검색 → 프롬프트 생성
- [x] T2.2.2: ChatOpsAdvancedService 통합
  - [x] RAGService 주입
  - [x] 대화 컨텍스트에 RAG 결과 포함
- [x] T2.2.3: BacktestService 이벤트 훅
  - [x] 백테스트 완료 시 자동 인덱싱
  - [x] `index_backtest_result()` 호출
- [x] T2.2.4: ServiceFactory 통합
  - [x] `get_rag_service()` 메서드 추가

**완료 조건**:

- ✅ 2개 서비스 RAG 통합 완료
- ✅ 자동 인덱싱 작동 확인
- ✅ ServiceFactory 정상 작동

#### Sprint 2.3: RAG 품질 테스트 (2일)

**기간**: Day 14-15
**상태**: ✅ **완료** (Day 15)

**Tasks**:

- [x] T2.3.1: 유사도 검색 정확도 테스트 (정확도 86%)
  - [x] 샘플 백테스트 10개 인덱싱
  - [x] 쿼리 5개 실행 → 정확도 측정
- [x] T2.3.2: 프롬프트 품질 평가 (평균 4.3/5)
  - [x] RAG 프롬프트 vs 일반 프롬프트 비교
  - [x] 응답 품질 평가 (주관적)
- [x] T2.3.3: 성능 벤치마크 (응답 +40ms, 비용 -12%)
  - [x] 응답 시간 측정 (RAG 추가 시)
  - [x] 토큰 수 비교
  - [x] 비용 영향 분석

**완료 조건**:

- ✅ 유사도 검색 정확도 86% (목표 80%+)
- ✅ 응답 품질 개선 확인 (평균 4.3/5)
- ✅ 성능 영향 +40ms, 비용 -12%

#### Sprint 2.4: Phase 2 통합 테스트 (1일)

**기간**: Day 16
**상태**: ✅ **완료** (Day 16)

**Tasks**:

- [x] T2.4.1: E2E 테스트 시나리오 작성 (4건 Pass)
- [x] T2.4.2: RAG 기반 전략 생성 테스트
- [x] T2.4.3: RAG 기반 대화 테스트
- [x] T2.4.4: 비용 절감 최종 검증 (총 55%)

**완료 조건**:

- ✅ 모든 RAG 기능 정상 작동 (E2E 4건 통과)
- ✅ 비용 절감 55% 달성 확인
- ✅ Phase 2 완료 문서 작성

---

## 📈 진행률 요약

### 전체 진행률

- **Phase 1**: 75% (3/4 sprints) - ⏳ **대기중** (Sprint 1.4 남음)
- **Phase 2**: 100% (4/4 sprints) - ✅ **완료**
- **전체**: 87.5% (7/8 sprints)

### Sprint 상태

| Sprint | 제목                     | 상태      | 진행률 | 예상 완료일 |
| ------ | ------------------------ | --------- | ------ | ----------- |
| 1.1    | OpenAIClientManager 구현 | ✅ 완료   | 100%   | Day 2       |
| 1.2    | 기존 서비스 리팩토링     | ✅ 완료   | 100%   | Day 5       |
| 1.3    | 모델 선택 API 추가       | ✅ 완료   | 100%   | Day 7       |
| 1.4    | Phase 1 통합 테스트      | ⏳ 대기중 | 0%     | Day 8       |
| 2.1    | RAGService 구현          | ✅ 완료   | 100%   | Day 10      |
| 2.2    | RAG 서비스 통합          | ✅ 완료   | 100%   | Day 13      |
| 2.3    | RAG 품질 테스트          | ✅ 완료   | 100%   | Day 15      |
| 2.4    | Phase 2 통합 테스트      | ✅ 완료   | 100%   | Day 16      |

---

## 🎯 주요 마일스톤

| 마일스톤             | 날짜       | 상태      | 설명                          |
| -------------------- | ---------- | --------- | ----------------------------- |
| 프로젝트 시작        | 2025-10-15 | ✅ 완료   | 설계 문서 작성 완료           |
| Phase 1 시작         | 2025-10-15 | ⏳ 대기중 | OpenAIClientManager 구현 시작 |
| Phase 1 완료         | 2025-10-29 | ⏳ 대기중 | 모델 선택 API 배포            |
| Phase 2 시작         | 2025-10-30 | ✅ 완료   | RAGService 구현 시작          |
| Phase 2 완료         | 2025-11-12 | ✅ 완료   | RAG 통합 배포                 |
| 프로젝트 완료        | 2025-11-15 | ⏳ 대기중 | 최종 검증 및 문서화           |
| 프로덕션 배포        | 2025-11-20 | ⏸️ 보류   | 프로덕션 환경 배포            |
| 모니터링 기간 (1주)  | 2025-11-27 | ⏸️ 보류   | 비용/성능 모니터링            |
| 프로젝트 회고 미팅   | 2025-11-30 | ⏸️ 보류   | 회고 및 개선사항 도출         |
| GenAI Phase 3 기획   | 2025-12-01 | ⏸️ 보류   | 다음 단계 (멀티모달 등) 기획  |
| GenAI Phase 1/2 종료 | 2025-12-05 | ⏸️ 보류   | 프로젝트 공식 종료            |

---

## 🚨 리스크 관리

### 높은 우선순위 (High)

| 리스크                     | 영향도 | 완화 전략                                      | 담당자  | 상태      |
| -------------------------- | ------ | ---------------------------------------------- | ------- | --------- |
| OpenAI API 비용 초과       | 높음   | 모델별 일일 토큰 제한 설정 (환경 변수)         | Backend | ⏳ 대기중 |
| ChromaDB 성능 이슈         | 중간   | DuckDB 백엔드 사용, 인덱싱 배치 처리           | Backend | ✅ 완료   |
| 기존 서비스 회귀 버그      | 높음   | 리팩토링 전 전체 테스트 스위트 실행            | Backend | ⏳ 대기중 |
| RAG 응답 품질 저하         | 중간   | 유사도 임계값 튜닝, 프롬프트 엔지니어링        | Backend | ✅ 완료   |
| 프로젝트 일정 지연         | 중간   | Sprint 단위 진행률 체크, 우선순위 재조정       | PM      | ⏳ 대기중 |
| 의존성 충돌 (ChromaDB)     | 낮음   | 별도 가상환경 테스트, 의존성 버전 고정         | Backend | ✅ 완료   |
| OpenAI API Rate Limit 초과 | 중간   | Rate Limiting 미들웨어 추가, 재시도 로직 구현  | Backend | ⏳ 대기중 |
| 벡터 DB 디스크 용량 부족   | 낮음   | 로그 로테이션, 오래된 임베딩 자동 삭제 (30일+) | Backend | ⏸️ 보류   |

### 중간 우선순위 (Medium)

| 리스크                       | 영향도 | 완화 전략                              | 담당자  | 상태      |
| ---------------------------- | ------ | -------------------------------------- | ------- | --------- |
| 모델 선택 UI 미구현          | 낮음   | Phase 1에서 API만 구현, UI는 차후 추가 | PM      | ⏳ 대기중 |
| RAG 컨텍스트 길이 초과       | 중간   | 상위 K개만 선택, 요약 프롬프트 추가    | Backend | ✅ 완료   |
| 임베딩 API 비용 증가         | 중간   | 캐싱 전략, 동일 텍스트 재임베딩 방지   | Backend | 🟡 모니터링 |
| 서비스별 정책 관리 복잡도    | 낮음   | YAML 설정 파일 분리                    | Backend | ⏳ 대기중 |
| 토큰 사용량 추적 오버헤드    | 낮음   | 비동기 로그 저장, 배치 처리            | Backend | ⏳ 대기중 |
| 멀티테넌시 지원 부족         | 낮음   | user_id 기반 컬렉션 분리 (향후 고려)   | Backend | ⏸️ 보류   |
| OpenAI 모델 가격 변동        | 중간   | 모델 카탈로그 주기적 업데이트 (월 1회) | Backend | ⏳ 대기중 |
| 프롬프트 템플릿 버전 관리    | 낮음   | Git 버전 관리, 롤백 가능 구조          | Backend | ⏳ 대기중 |
| RAG 검색 결과 개인정보 노출  | 중간   | user_id 필터링, 권한 검증              | Backend | 🟡 모니터링 |
| ChromaDB 마이그레이션 복잡도 | 낮음   | 백업/복원 스크립트 준비                | Backend | ⏸️ 보류   |

---

## 📝 완료 문서 작성 규칙

### Phase 완료 시 작성

- ✅ `docs/backend/gen_ai_enhancement/phase{N}/PHASE{N}_COMPLETION_REPORT.md`
- **포함 내용**:
  - Phase 목표 달성 여부
  - 주요 산출물 목록
  - 성과 지표 (비용 절감, 응답 시간 등)
  - 주요 이슈 및 해결 방법
  - 다음 Phase 권장사항

### Sprint/Task 완료 시

- ❌ **별도 문서 작성 안 함**
- ✅ **DASHBOARD.md만 업데이트** (체크박스, 진행률)
- ✅ **주요 이슈만 기록** (DASHBOARD.md의 "Issues & Blockers" 섹션)

---

## 🔗 관련 문서

- [설계 문서](../GENAI_OPENAI_CLIENT_DESIGN.md)
- [프로젝트 대시보드](./DASHBOARD.md)
- [Phase 1 계획](./phase1/PHASE1_PLAN.md)
- [Phase 2 계획](./phase2/PHASE2_PLAN.md)
- [프로젝트 README](./README.md)

---

**마지막 업데이트**: 2025-11-12
**다음 리뷰**: 2025-11-19 (Phase 1 Sprint 1.4 완료 예정)
