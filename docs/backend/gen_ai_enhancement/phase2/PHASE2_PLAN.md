# Phase 2: RAG Integration

**목표**: ChromaDB 기반 사용자 데이터 컨텍스트 활용  
**기간**: 2025-10-30 ~ 2025-11-12 (2주, 8일)  
**상태**: ⏸️ **보류** (Phase 1 완료 필요)

---

## 🎯 Phase 목표

### 주요 목표

1. **RAG 구현**: ChromaDB 기반 벡터 검색 시스템
2. **사용자 컨텍스트**: 백테스트 결과 자동 인덱싱
3. **응답 품질**: 유사 백테스트 기반 개인화 응답
4. **성능**: 검색 시간 < 100ms, 응답 시간 < 500ms
5. **비용 최적화**: RAG 도입으로 50%+ 비용 절감

### 완료 기준 (Definition of Done)

- ✅ RAGService 구현 완료
- ✅ ChromaDB 설정 및 컬렉션 생성
- ✅ 2개 서비스 RAG 통합 (StrategyBuilder, ChatOpsAdvanced)
- ✅ 백테스트 자동 인덱싱 훅 구현
- ✅ 유사도 검색 정확도 80%+
- ✅ 응답 품질 개선 확인
- ✅ Phase 2 완료 문서 작성

---

## 📅 Sprint 계획

### Sprint 2.1: RAGService 구현 (2일)

**기간**: Day 9-10  
**목표**: ChromaDB 기반 벡터 검색 서비스 구축

#### Tasks

**T2.1.1: ChromaDB 의존성 추가** (30분)

- [ ] `uv add chromadb` 실행
- [ ] 의존성 충돌 확인
- [ ] 환경 변수 설정 (`CHROMADB_PATH`)

**T2.1.2: RAGService 클래스 생성** (2시간)

- [ ] `app/services/gen_ai/core/rag_service.py` 생성
- [ ] ChromaDB 클라이언트 초기화
  - `chroma_db_impl='duckdb+parquet'`
  - `persist_directory='./data/chromadb'`
- [ ] 컬렉션 생성
  - `user_backtests` (백테스트 결과)
  - `user_strategies` (전략 코드)
- [ ] 싱글톤 패턴 적용

**T2.1.3: index_backtest_result() 메서드** (3시간)

- [ ] 입력: `BacktestResult` 객체
- [ ] 텍스트 변환 (성과 지표, 거래 요약)
- [ ] OpenAI Embedding API 호출 (`text-embedding-ada-002`)
- [ ] ChromaDB 인덱싱 (user_id, backtest_id 메타데이터)
- [ ] 에러 처리 (API 실패, 디스크 부족 등)

**T2.1.4: search_similar_backtests() 메서드** (2시간)

- [ ] 입력: 쿼리 텍스트 (자연어)
- [ ] 쿼리 임베딩 생성
- [ ] ChromaDB 유사도 검색 (top_k=5)
- [ ] 결과 필터링 (user_id 일치)
- [ ] 응답: `List[BacktestContext]`

**T2.1.5: build_rag_prompt() 메서드** (2시간)

- [ ] 입력: 원본 프롬프트 + 검색 결과
- [ ] 프롬프트 템플릿 작성

  ```
  사용자의 이전 백테스트 결과:
  1. [전략명] - 수익률: X%, Sharpe: Y
  2. ...

  사용자 요청: [원본 프롬프트]
  ```

- [ ] 토큰 길이 제한 (최대 2000 tokens)
- [ ] 응답: 증강된 프롬프트

#### 완료 조건

- ✅ `app/services/gen_ai/core/rag_service.py` 생성
- ✅ ChromaDB 정상 작동 확인
- ✅ 인덱싱/검색 단위 테스트 작성
- ✅ 임베딩 캐싱 로직 구현

---

### Sprint 2.2: RAG 서비스 통합 (3일)

**기간**: Day 11-13  
**목표**: 기존 서비스에 RAG 기능 추가

#### Tasks

**T2.2.1: StrategyBuilderService 통합** (1.5일)

- [ ] RAGService 주입 (ServiceFactory)
- [ ] `generate_strategy_with_rag()` 메서드 추가
  - [ ] 유사 전략 검색 (`search_similar_backtests`)
  - [ ] 프롬프트 증강 (`build_rag_prompt`)
  - [ ] LLM 호출 (OpenAIClientManager)
  - [ ] 토큰 추적 (`track_usage`)
- [ ] 기존 `build_strategy()` 메서드와 분리 유지
- [ ] API 엔드포인트 추가: `POST /api/v1/strategy-builder/generate-with-rag`

**T2.2.2: ChatOpsAdvancedService 통합** (1.5일)

- [ ] RAGService 주입
- [ ] `chat()` 메서드 수정
  - [ ] 대화 컨텍스트 분석
  - [ ] 유사 백테스트 검색 (필요 시)
  - [ ] 프롬프트 증강
  - [ ] LLM 호출
- [ ] RAG 활성화 플래그 (`use_rag: bool`)
- [ ] ChatRequest에 `use_rag: Optional[bool]` 추가

**T2.2.3: BacktestService 이벤트 훅** (0.5일)

- [ ] `BacktestOrchestrator.execute_backtest()` 수정
- [ ] 백테스트 완료 후 자동 인덱싱
  ```python
  if result:
      rag_service = service_factory.get_rag_service()
      await rag_service.index_backtest_result(result)
  ```
- [ ] 에러 처리 (인덱싱 실패 시 로그만 남김)

**T2.2.4: ServiceFactory 통합** (0.5일)

- [ ] `get_rag_service()` 메서드 추가
- [ ] 싱글톤 인스턴스 캐싱
- [ ] 기존 서비스에 주입 로직 추가

#### 완료 조건

- ✅ 2개 서비스 RAG 통합 완료
- ✅ 자동 인덱싱 작동 확인
- ✅ RAG 활성화/비활성화 선택 가능
- ✅ 통합 테스트 통과

---

### Sprint 2.3: RAG 품질 테스트 (2일)

**기간**: Day 14-15  
**목표**: RAG 시스템 품질 검증

#### Tasks

**T2.3.1: 유사도 검색 정확도 테스트** (1일)

- [ ] 샘플 백테스트 10개 인덱싱
  - RSI 전략 3개
  - MACD 전략 3개
  - Bollinger Bands 전략 2개
  - 기타 전략 2개
- [ ] 쿼리 5개 실행
  - "RSI 전략 백테스트 결과"
  - "Sharpe Ratio가 높은 전략"
  - "최근 1개월 수익률이 좋은 전략"
  - "손실이 적은 전략"
  - "AAPL 종목 백테스트"
- [ ] 정확도 측정 (관련 결과 비율)
- [ ] 목표: 80%+ 정확도

**T2.3.2: 프롬프트 품질 평가** (0.5일)

- [ ] RAG 프롬프트 vs 일반 프롬프트 비교
- [ ] 동일 요청 5회 반복
- [ ] 응답 품질 평가 (주관적)
  - 관련성 (5점 척도)
  - 구체성 (5점 척도)
  - 실용성 (5점 척도)
- [ ] 목표: RAG 응답 평균 4.0/5 이상

**T2.3.3: 성능 벤치마크** (0.5일)

- [ ] 응답 시간 측정 (100회 평균)
  - RAG 미사용: 기준값
  - RAG 사용: 증가량
- [ ] 토큰 수 비교
  - 프롬프트 토큰 증가량
  - 응답 토큰 변화
- [ ] 비용 영향 분석
  - 임베딩 API 비용
  - 증가된 프롬프트 토큰 비용
  - 전체 비용 변화
- [ ] 목표: 응답 시간 < 500ms, 비용 증가 < 10%

#### 완료 조건

- ✅ 유사도 검색 정확도 80%+
- ✅ 응답 품질 개선 확인 (4.0/5+)
- ✅ 성능 영향 < 500ms
- ✅ 비용 증가 < 10% (또는 전체 50%+ 절감 유지)

---

### Sprint 2.4: Phase 2 통합 테스트 (1일)

**기간**: Day 16  
**목표**: 전체 Phase 2 검증

#### Tasks

**T2.4.1: E2E 테스트 시나리오** (2시간)

- [ ] 시나리오 1: 백테스트 실행 → 자동 인덱싱 → RAG 검색
- [ ] 시나리오 2: RAG 기반 전략 생성 → 유사 전략 활용 확인
- [ ] 시나리오 3: RAG 기반 대화 → 사용자 컨텍스트 반영 확인
- [ ] 시나리오 4: RAG 비활성화 → 기존 동작 유지

**T2.4.2: RAG 기반 전략 생성 테스트** (2시간)

- [ ] "RSI 전략 만들어줘" 요청
- [ ] 유사 전략 검색 결과 확인
- [ ] 생성된 전략 파라미터 검증
- [ ] 이전 백테스트 결과 반영 여부 확인

**T2.4.3: RAG 기반 대화 테스트** (2시간)

- [ ] ChatOps 멀티턴 대화
- [ ] 사용자 이전 백테스트 참조 확인
- [ ] 컨텍스트 유지 확인
- [ ] 응답 품질 평가

**T2.4.4: 비용 절감 최종 검증** (2시간)

- [ ] Phase 1 비용 절감 (gpt-4 → gpt-4o-mini): 30%+
- [ ] Phase 2 RAG 도입: 추가 20%+ 절감
  - 프롬프트 최적화 (컨텍스트 활용)
  - 응답 길이 감소 (관련성 높은 정보)
- [ ] 전체 비용 절감: 50%+ 달성 확인
- [ ] 월 $100 → $50 이하 확인

#### 완료 조건

- ✅ E2E 테스트 통과
- ✅ RAG 기능 정상 작동
- ✅ 비용 절감 50%+ 달성
- ✅ Phase 2 완료 문서 작성

---

## 📦 산출물 (Deliverables)

### 코드

- [ ] `backend/app/services/gen_ai/core/rag_service.py` (600+ lines)
- [ ] `backend/app/services/gen_ai/strategy_builder.py` (RAG 통합)
- [ ] `backend/app/services/gen_ai/chatops_advanced.py` (RAG 통합)
- [ ] `backend/app/services/trading/orchestrator.py` (자동 인덱싱 훅)
- [ ] `backend/app/api/routes/gen_ai/strategy_builder.py` (신규 엔드포인트)
- [ ] `backend/app/schemas/gen_ai/rag.py` (신규, RAG 관련 스키마)

### 테스트

- [ ] `backend/tests/services/gen_ai/test_rag_service.py` (단위)
- [ ] `backend/tests/integration/test_rag_integration.py` (통합)
- [ ] `backend/tests/integration/test_phase2_e2e.py` (E2E)

### 문서

- [ ] `docs/backend/gen_ai_enhancement/phase2/PHASE2_COMPLETION_REPORT.md`
- [ ] API 문서 업데이트 (OpenAPI 스키마)

---

## 🚨 리스크 및 완화 전략

| 리스크                   | 완화 전략                                 | 담당자  |
| ------------------------ | ----------------------------------------- | ------- |
| ChromaDB 성능 이슈       | DuckDB 백엔드 사용, 배치 처리             | Backend |
| RAG 응답 품질 저하       | 유사도 임계값 튜닝, 프롬프트 엔지니어링   | Backend |
| 임베딩 API 비용 증가     | 캐싱 전략, 동일 텍스트 재임베딩 방지      | Backend |
| 벡터 DB 디스크 용량 부족 | 오래된 임베딩 자동 삭제 (30일+)           | Backend |
| RAG 컨텍스트 길이 초과   | 상위 K개만 선택, 요약 프롬프트            | Backend |
| 의존성 충돌 (ChromaDB)   | 별도 가상환경 테스트, 버전 고정           | Backend |
| 유사도 검색 정확도 낮음  | 임베딩 모델 업그레이드, 메타데이터 필터링 | Backend |
| 사용자 데이터 개인정보   | user_id 필터링, 권한 검증                 | Backend |

---

## 🔗 관련 문서

- [Master Plan](../MASTER_PLAN.md)
- [Dashboard](../DASHBOARD.md)
- [설계 문서](../../GENAI_OPENAI_CLIENT_DESIGN.md)
- [Phase 1 Plan](../phase1/PHASE1_PLAN.md)

---

**마지막 업데이트**: 2025-10-15  
**시작 조건**: Phase 1 완료 (OpenAIClientManager 구현)
