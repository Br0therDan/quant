# Strategy & Backtest 리팩토링 Phase 3

> **Phase 3 구현 가이드**: 테스트 & 최적화 (1-2주)  
> **상태**: 🚧 진행 중 (P3.0 완료)  
> **목표**: 통합 테스트 작성, 성능 최적화, 운영 개선

## 📋 목차

1. [P3.0 API 정리](#p30-api-정리) ✅
2. [P3.1 통합 테스트 작성](#p31-통합-테스트-작성)
3. [P3.2 성능 최적화](#p32-성능-최적화)
4. [P3.3 에러 처리 강화](#p33-에러-처리-강화)
5. [P3.4 모니터링 개선](#p34-모니터링-개선)
6. [배포 체크리스트](#배포-체크리스트)

---

## 개요

### Phase 1-2 완료 사항 (기반) ✅

- ✅ Phase 1: TradeEngine, 의존성 주입, Config 타입 안전성
- ✅ Phase 2: 레이어드 아키텍처, 레거시 제거, 코드 71% 축소

### Phase 3 목표 🎯

- 🎯 **API 정리**: 중복 엔드포인트 제거 ✅
- 🎯 **테스트 커버리지**: 통합 테스트 + E2E 테스트 작성
- 🎯 **성능 최적화**: 병렬 처리, 캐싱 전략
- 🎯 **안정성 강화**: 에러 처리, 재시도 로직
- 🎯 **운영 개선**: 로깅, 모니터링, 알림

### 현재 상태

```
Phase 2 완료:
✅ BacktestOrchestrator (워크플로우)
✅ StrategyExecutor (전략 실행)
✅ PerformanceAnalyzer (성과 분석)
✅ DataProcessor (데이터 전처리)
✅ TradeEngine (거래 실행)

Phase 3 진행:
✅ P3.0 API 정리 (완료)
   - 중복 엔드포인트 3개 제거
   - 13개 → 10개 API
⏸️ P3.1 통합 테스트 (40% 완료)
⏸️ P3.2 성능 최적화 (0/3 완료)
⏸️ P3.3 에러 처리 (0/4 완료)
⏸️ P3.4 모니터링 (0/2 완료)
```

---

## P3.0 API 정리 ✅ **완료**

### 목표 ✅

중복 및 미구현 엔드포인트 정리로 API 구조 개선

### 완료 사항 ✅

#### 제거된 엔드포인트 (3개)

1. ✅ **POST `/integrated`**

   - 이유: POST `/` + POST `/{id}/execute`와 중복
   - 조치: 완전 제거
   - 문서: [P3.0_API_CLEANUP.md](./P3.0_API_CLEANUP.md)

2. ✅ **GET `/results/duckdb`**

   - 이유: DuckDB 저장 미구현
   - 조치: 주석 처리 (P3.2 구현 후 재활성화)

3. ✅ **GET `/analytics/summary`**
   - 이유: `/analytics/performance-stats`와 중복
   - 조치: 완전 제거

#### 템플릿 API 확인 ✅

- ✅ `/strategies/templates` 이미 구현됨
- ✅ 라우터 등록 확인

### 결과

- **Backtests API**: 13개 → 10개 (23% 감소)
- **Strategies API**: 9개 (템플릿 포함)
- **린트 검사**: ✅ 통과
- **문서화**: ✅ 완료

---

## P3.1 통합 테스트 작성

### 목표

Phase 2 컴포넌트의 통합 테스트 및 E2E 테스트 작성

### 작업 항목

#### Step 1: BacktestOrchestrator 통합 테스트

**파일**: `backend/tests/test_orchestrator_integration.py` (NEW)

**테스트 케이스**:

- 전체 백테스트 파이프라인 성공 시나리오
- 데이터 수집 실패 시 복구
- 전략 실행 중 오류 처리
- 성과 분석 결과 검증
- MongoDB + DuckDB 저장 검증

**의존성**:

- pytest-asyncio
- pytest-mock
- 테스트용 MongoDB 데이터베이스

#### Step 2: StrategyExecutor 테스트

**파일**: `backend/tests/test_strategy_executor.py` (NEW)

**테스트 케이스**:

- 다양한 전략 타입별 신호 생성
- 잘못된 파라미터 처리
- 전략 로딩 실패 처리
- 신호 포맷 검증

#### Step 3: DataProcessor 테스트

**파일**: `backend/tests/test_data_processor.py` (이미 존재, 확장)

**추가 테스트**:

- 대용량 데이터 처리 (10,000+ rows)
- 결측치 처리 전략
- 데이터 정규화 검증
- 멀티 심볼 데이터 병합

#### Step 4: E2E 테스트

**파일**: `backend/tests/test_backtest_e2e.py` (NEW)

**시나리오**:

- API 엔드포인트 → Orchestrator → DB 저장 (전체 흐름)
- 실제 시장 데이터 기반 백테스트
- 성능 벤치마크 (100회 반복)

#### Step 5: 테스트 유틸리티

**파일**: `backend/tests/utils/backtest_fixtures.py` (NEW)

**내용**:

- 테스트용 백테스트 설정 픽스처
- Mock 데이터 생성기
- 공통 assertion 헬퍼

---

## P3.2 성능 최적화

### 목표

백테스트 실행 속도 개선 및 리소스 효율화

### 작업 항목

#### Step 1: 병렬 데이터 수집

**파일**: `backend/app/services/backtest/orchestrator.py` (수정)

**최적화**:

- `_collect_data()` 메서드를 asyncio.gather로 병렬화
- 여러 심볼 데이터 동시 수집
- 타임아웃 설정 (30초)

**예상 개선**: 5개 심볼 × 5초 = 25초 → 5초 (80% 감소)

#### Step 2: 캐싱 전략 개선

**파일**: `backend/app/services/backtest/data_processor.py` (수정)

**최적화**:

- 전처리된 데이터 Redis 캐싱 (1시간 TTL)
- 동일 기간/심볼 재사용
- LRU 캐시 데코레이터 추가

**예상 개선**: 중복 요청 90% 캐시 히트

#### Step 3: 배치 처리

**파일**: `backend/app/services/backtest/orchestrator.py` (수정)

**최적화**:

- 여러 백테스트 큐잉 및 배치 실행
- 백그라운드 작업 큐 도입 (Celery 또는 ARQ)
- 우선순위 기반 스케줄링

**예상 개선**: 동시 실행 10개 → 처리량 5배 증가

---

## P3.3 에러 처리 강화

### 목표

장애 복구력 및 사용자 피드백 개선

### 작업 항목

#### Step 1: 재시도 로직

**파일**: `backend/app/services/backtest/orchestrator.py` (수정)

**개선 사항**:

- Alpha Vantage API 실패 시 3회 재시도 (지수 백오프)
- MongoDB 연결 실패 재시도
- 트랜잭션 롤백 처리

**라이브러리**: `tenacity`

#### Step 2: 상세한 에러 메시지

**파일**: `backend/app/schemas/backtest.py` (수정)

**개선 사항**:

- 에러 타입별 상세 메시지
- 사용자 조치 가이드 포함
- 에러 코드 체계 도입 (BT001, BT002 등)

#### Step 3: 부분 실패 처리

**파일**: `backend/app/services/backtest/orchestrator.py` (수정)

**개선 사항**:

- 일부 심볼 데이터 수집 실패 시 계속 진행
- 실패 이유 기록 및 사용자 알림
- 부분 결과 저장 옵션

#### Step 4: Circuit Breaker 패턴

**파일**: `backend/app/services/market_data_service.py` (수정)

**개선 사항**:

- Alpha Vantage API 연속 실패 시 일시 중단
- 자동 복구 메커니즘 (5분 후)
- 대체 데이터 소스 폴백 (향후)

---

## P3.4 모니터링 개선

### 목표

실시간 모니터링 및 알림 체계 구축

### 작업 항목

#### Step 1: 구조화된 로깅

**파일**: `backend/app/core/logging_config.py` (수정)

**개선 사항**:

- JSON 포맷 로깅 (structlog)
- 요청 ID 추적
- 성능 메트릭 자동 기록

**로그 레벨**:

- INFO: 백테스트 시작/완료
- WARNING: 재시도 발생
- ERROR: 실패 케이스

#### Step 2: 메트릭 수집

**파일**: `backend/app/services/backtest/metrics.py` (NEW)

**메트릭**:

- 백테스트 실행 시간 (histogram)
- 성공/실패 비율 (counter)
- 데이터 수집 지연 (gauge)
- 메모리 사용량 (gauge)

**도구**: Prometheus + Grafana (선택적)

---

## 배포 체크리스트

### Phase 3 완료 조건

- [ ] **테스트**: 통합 테스트 5개 모두 통과
- [ ] **성능**: 백테스트 실행 시간 50% 단축
- [ ] **에러 처리**: 재시도 로직 3개 API 적용
- [ ] **모니터링**: 구조화된 로깅 적용
- [ ] **문서**: API 문서 업데이트 (OpenAPI)
- [ ] **코드 리뷰**: 팀 리뷰 완료

### 검증 스크립트

**파일**: `backend/scripts/verify_phase3.py` (NEW)

**검증 항목**:

- 테스트 커버리지 80% 이상
- 통합 테스트 100% 통과
- 성능 벤치마크 기준 충족
- 에러 시나리오 모두 처리

### 롤백 계획

**조건**: 프로덕션 에러율 5% 초과 시

**절차**:

1. Phase 2 코드로 롤백 (git revert)
2. 데이터베이스 마이그레이션 롤백 (없음)
3. 캐시 클리어 (Redis)
4. 헬스체크 확인

---

## 📊 Phase 3 진행 상황

### 우선순위

| 작업             | 우선순위 | 예상 시간 | 상태       | 완료율    |
| ---------------- | -------- | --------- | ---------- | --------- |
| P3.1 통합 테스트 | HIGH     | 3일       | ✅ 진행 중 | 40% (2/5) |
| P3.2 병렬 처리   | HIGH     | 2일       | ⏸️ 대기    | 0%        |
| P3.3 재시도 로직 | MEDIUM   | 1일       | ⏸️ 대기    | 0%        |
| P3.4 로깅 개선   | MEDIUM   | 1일       | ⏸️ 대기    | 0%        |
| P3.2 캐싱        | LOW      | 2일       | ⏸️ 대기    | 0%        |
| P3.4 메트릭 수집 | LOW      | 2일       | ⏸️ 대기    | 0%        |

### P3.1 통합 테스트 진척도

- ✅ Step 1: BacktestOrchestrator 테스트 (5/5 통과)

  - `test_orchestrator_integration.py` 생성 완료
  - 5개 단위 테스트 통과
  - 통합 테스트 1개 (DB 연결 필요, 스킵)

- ✅ Step 2: StrategyExecutor 테스트 (5/5 통과)
  - `test_strategy_executor.py` 생성 완료
  - 5개 테스트 모두 통과
- ⏸️ Step 3: DataProcessor 테스트 확장 (대기)
- ⏸️ Step 4: E2E 테스트 (대기)
- ⏸️ Step 5: 테스트 유틸리티 (대기)

**총 테스트**: 10 passed, 1 skipped

### 예상 일정

- **Week 1**: P3.1 (테스트) ✅ 40% 완료 + P3.2 (병렬 처리)
- **Week 2**: P3.3 (에러 처리) + P3.4 (모니터링)

### 완료 기준

✅ Phase 3 완료 = 모든 HIGH 우선순위 작업 완료 + 테스트 통과

---

## 🎯 현재 작업 상태

**최근 완료**:

- ✅ `test_orchestrator_integration.py` (5개 테스트 통과)
- ✅ `test_strategy_executor.py` (5개 테스트 통과)
- ✅ REFACTORING_PHASE3.md 문서 작성

**다음 단계**: P3.2 병렬 처리 구현

---

## 🚀 즉시 실행 가능한 작업

### 1단계: 통합 테스트 작성 (우선)

```bash
# 테스트 파일 생성
touch backend/tests/test_orchestrator_integration.py
touch backend/tests/test_strategy_executor.py
touch backend/tests/test_backtest_e2e.py
touch backend/tests/utils/backtest_fixtures.py

# 테스트 실행
cd backend
uv run pytest tests/ -v --cov=app/services/backtest
```

### 2단계: 병렬 처리 구현

**수정 파일**: `backend/app/services/backtest/orchestrator.py`

- `_collect_data()` 메서드 asyncio.gather 적용

### 3단계: 재시도 로직 추가

**설치**: `uv add tenacity`  
**수정 파일**: `backend/app/services/backtest/orchestrator.py`

- `@retry` 데코레이터 추가

---

## 📝 참고사항

### 테스트 전략

- **Unit Tests**: 각 컴포넌트 독립 테스트 (Phase 1-2 완료)
- **Integration Tests**: 컴포넌트 간 상호작용 테스트 (Phase 3)
- **E2E Tests**: 전체 워크플로우 테스트 (Phase 3)

### 성능 목표

- 백테스트 실행 시간: 30초 → 15초 (50% 감소)
- 동시 처리: 1개 → 10개 (10배 증가)
- 메모리 사용: 500MB → 300MB (40% 감소)

### 호환성

- Python 3.12+
- MongoDB 6.0+
- DuckDB 0.9+
- Redis 7.0+ (캐싱용, 선택적)

---

## 다음 단계

1. **P3.1 시작**: 통합 테스트 작성부터 시작
2. **검증**: 각 Step마다 테스트 실행 및 검증
3. **문서화**: 성능 개선 결과 기록
4. **배포**: Phase 3 완료 후 프로덕션 배포

**현재 작업**: P3.1 Step 1 - BacktestOrchestrator 통합 테스트 작성 🚧
