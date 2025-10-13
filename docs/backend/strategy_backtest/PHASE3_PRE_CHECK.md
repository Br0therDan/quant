# Phase 3 작업 전 점검 보고서

> **작성일**: 2025-01-13 19:40  
> **목적**: Phase 3 작업 진행 전 현재 상태 점검 및 개선 사항 도출

## 📋 점검 항목

1. [Phase 1-2 작업 완료 상태 검증](#1-phase-1-2-작업-완료-상태-검증)
2. [API 엔드포인트 구성 분석](#2-api-엔드포인트-구성-분석)
3. [누락/미스매치 사항](#3-누락미스매치-사항)
4. [개선 권장 사항](#4-개선-권장-사항)

---

## 1. Phase 1-2 작업 완료 상태 검증

### ✅ Phase 1 완료 사항 (계획 대비)

| 작업                        | 계획                        | 실제 구현                            | 상태 |
| --------------------------- | --------------------------- | ------------------------------------ | ---- |
| **P1.1 의존성 주입 개선**   | BacktestService 생성자 수정 | ✅ 완료                              | ✅   |
| - ServiceFactory 업데이트   | ✅                          | ✅ service_factory.py                | ✅   |
| - 완전한 초기화 보장        | ✅                          | ✅ 모든 의존성 생성 시 주입          | ✅   |
| **P1.2 TradeEngine 통합**   | 중복 거래 로직 제거         | ✅ 완료                              | ✅   |
| - TradeEngine 클래스 생성   | ✅                          | ✅ services/backtest/trade_engine.py | ✅   |
| - IntegratedExecutor 제거   | ✅                          | ✅ 238 lines 제거                    | ✅   |
| **P1.3 Config 타입 안전성** | Pydantic Config 클래스      | ✅ 완료                              | ✅   |
| - 전략별 Config 정의        | ✅                          | ✅ strategies/configs.py             | ✅   |
| - 파라미터 검증 로직        | ✅                          | ✅ Pydantic validators               | ✅   |

**Phase 1 결론**: ✅ **계획 대비 100% 완료**

---

### ✅ Phase 2 완료 사항 (계획 대비)

| 작업                          | 계획            | 실제 구현                        | 상태 |
| ----------------------------- | --------------- | -------------------------------- | ---- |
| **P2.1 BacktestOrchestrator** | 워크플로우 조율 | ✅ 완료                          | ✅   |
| - 파이프라인 관리             | ✅              | ✅ orchestrator.py (300 lines)   | ✅   |
| - 상태 추적                   | ✅              | ✅ \_update_status() 메서드      | ✅   |
| - 에러 처리                   | ✅              | ✅ try/except + 상태 업데이트    | ✅   |
| **P2.2 StrategyExecutor**     | 전략 실행 분리  | ✅ 완료                          | ✅   |
| - 신호 생성 로직              | ✅              | ✅ executor.py (150 lines)       | ✅   |
| - 전략 로딩                   | ✅              | ✅ strategy_service 연동         | ✅   |
| **P2.3 PerformanceAnalyzer**  | 성과 분석 분리  | ✅ 완료                          | ✅   |
| - 지표 계산 통합              | ✅              | ✅ performance.py (200 lines)    | ✅   |
| - Sharpe, Sortino 등          | ✅              | ✅ 8개 지표 구현                 | ✅   |
| **P2.4 DataProcessor**        | 데이터 전처리   | ✅ 완료                          | ✅   |
| - 데이터 정제                 | ✅              | ✅ data_processor.py (150 lines) | ✅   |
| - 검증 로직                   | ✅              | ✅ validate_data() 메서드        | ✅   |
| **BacktestService 축소**      | CRUD only       | ✅ 완료                          | ✅   |
| - 700 → 200 lines             | ✅              | ✅ 실행 로직 제거                | ✅   |

**Phase 2 결론**: ✅ **계획 대비 100% 완료**

---

### 🔍 미스매치/누락 사항

#### 1. ❌ DuckDB 저장 로직 미구현

**계획**: Phase 2에서 DuckDB 저장 구현  
**현재**: `_save_to_duckdb()` 메서드 빈 구현 (pass)

```python
# orchestrator.py:335
async def _save_to_duckdb(self, result, trades, portfolio_history):
    """DuckDB에 결과 저장 (구현 필요)"""
    pass  # ❌ 미구현
```

**영향도**: 중간 - MongoDB 저장은 동작하지만 DuckDB 분석 기능 미사용  
**우선순위**: Phase 3에서 구현

#### 2. ⚠️ 테스트 파일 불완전

**계획**: Phase 2 완료 후 통합 테스트  
**현재**:

- ✅ `test_orchestrator_integration.py` (10 passed)
- ✅ `test_strategy_executor.py` (5 passed)
- ❌ `test_data_processor.py` 확장 필요 (기본 테스트만 존재)
- ❌ E2E 테스트 미작성

**영향도**: 낮음 - 핵심 컴포넌트 테스트는 완료  
**우선순위**: Phase 3 P3.1에서 완성

#### 3. ⚠️ 병렬 데이터 수집 미구현

**계획**: Phase 2에서 asyncio.gather 활용  
**현재**: 순차적 데이터 수집

```python
# orchestrator.py:273
async def _collect_market_data(self, backtest: Backtest) -> dict:
    # 순차 처리 (병렬 아님)
    for symbol in backtest.config.symbols:
        data[symbol] = await self.market_data.get_historical_data(...)
```

**영향도**: 중간 - 다중 심볼 백테스트 시 속도 저하  
**우선순위**: Phase 3 P3.2에서 구현

---

## 2. API 엔드포인트 구성 분석

### 2.1 Backtests API (13개 엔드포인트)

| 엔드포인트                     | 메서드 | 용도             | 평가      | 권장 조치                |
| ------------------------------ | ------ | ---------------- | --------- | ------------------------ |
| `/`                            | POST   | 백테스트 생성    | ✅ 필수   | 유지                     |
| `/`                            | GET    | 백테스트 목록    | ✅ 필수   | 유지                     |
| `/{id}`                        | GET    | 백테스트 상세    | ✅ 필수   | 유지                     |
| `/{id}`                        | PUT    | 백테스트 수정    | ✅ 필수   | 유지                     |
| `/{id}`                        | DELETE | 백테스트 삭제    | ✅ 필수   | 유지                     |
| `/{id}/execute`                | POST   | 백테스트 실행    | ✅ 핵심   | 유지 (Orchestrator 사용) |
| `/{id}/executions`             | GET    | 실행 기록 조회   | ✅ 필수   | 유지                     |
| `/results/duckdb`              | GET    | DuckDB 결과 조회 | ⚠️ 미구현 | **제거 또는 구현**       |
| `/integrated`                  | POST   | 통합 백테스트    | ❌ 중복   | **제거 권장**            |
| `/health`                      | GET    | 상태 확인        | ✅ 유용   | 유지                     |
| `/analytics/performance-stats` | GET    | 성과 분석        | ✅ 유용   | 유지                     |
| `/analytics/trades`            | GET    | 거래 분석        | ✅ 유용   | 유지                     |
| `/analytics/summary`           | GET    | 요약 분석        | ⚠️ 중복   | **통합 권장**            |

#### 🔴 문제점 및 권장 조치

**1. `/results/duckdb` 엔드포인트 (Line 318)**

- **문제**: DuckDB 저장 미구현인데 엔드포인트 존재
- **현재 동작**: MongoDB 데이터 반환 (DuckDB 아님)
- **권장**:
  - Option A: DuckDB 저장 구현 후 실제 DuckDB 쿼리
  - Option B: 엔드포인트 제거, `/results` 하나로 통합

**2. `/integrated` 엔드포인트 (Line 379)**

- **문제**: `POST /{id}/execute`와 기능 중복
- **차이점**: 백테스트 생성 + 실행을 한 번에 처리
- **권장**:
  - Option A: **제거** - 프론트엔드에서 2단계 호출 (생성 → 실행)
  - Option B: 유지하되 문서화 강화 (편의 기능으로)

**3. `/analytics/*` 3개 엔드포인트**

- **문제**: `/performance-stats`, `/trades`, `/summary` 기능 중복
- **권장**: `/analytics` 단일 엔드포인트로 통합
  - Query parameter로 분석 타입 선택 (`?type=performance|trades|summary`)

---

### 2.2 Strategies API (8개 엔드포인트)

| 엔드포인트          | 메서드 | 용도           | 평가    | 권장 조치  |
| ------------------- | ------ | -------------- | ------- | ---------- |
| `/`                 | POST   | 전략 생성      | ✅ 필수 | 유지       |
| `/`                 | GET    | 전략 목록      | ✅ 필수 | 유지       |
| `/{id}`             | GET    | 전략 상세      | ✅ 필수 | 유지       |
| `/{id}`             | PUT    | 전략 수정      | ✅ 필수 | 유지       |
| `/{id}`             | DELETE | 전략 삭제      | ✅ 필수 | 유지       |
| `/{id}/execute`     | POST   | 전략 단독 실행 | ⚠️ 혼동 | **재검토** |
| `/{id}/executions`  | GET    | 실행 기록 조회 | ✅ 유용 | 유지       |
| `/{id}/performance` | GET    | 성과 조회      | ✅ 유용 | 유지       |

#### 🟡 개선 권장 사항

**1. `/{id}/execute` 엔드포인트 (Line 248)**

- **문제**: 백테스트 없이 전략만 실행하는 것이 혼동 유발
- **질문**: 전략 단독 실행 vs 백테스트 실행의 차이는?
- **권장**:
  - Option A: **제거** - 모든 실행은 백테스트를 통해서만
  - Option B: 명확한 구분 - "전략 검증"으로 용도 제한 (간단한 신호 생성 테스트)

**2. 전략 템플릿 엔드포인트 부재**

- **누락**: 전략 템플릿 관리 엔드포인트 없음
- **현재**: `strategies/template.py` 파일은 존재하나 라우터 미등록
- **권장**: `/templates` 엔드포인트 추가
  - `GET /strategies/templates` - 템플릿 목록
  - `POST /strategies/templates/{template_id}/clone` - 템플릿에서 전략 생성

---

## 3. 누락/미스매치 사항 종합

### 🔴 Critical (즉시 해결)

1. **DuckDB 저장 로직 미구현**

   - 파일: `orchestrator.py:335`
   - 조치: Phase 3 P3.2에서 구현 또는 `/results/duckdb` 엔드포인트 제거

2. **중복 엔드포인트 정리**
   - `/integrated` (백테스트) - 제거 또는 문서화
   - `/analytics/*` 3개 - 통합 고려

### 🟡 Important (Phase 3 진행 전 해결)

3. **전략 단독 실행 엔드포인트 재검토**

   - `POST /strategies/{id}/execute` 용도 명확화 또는 제거

4. **전략 템플릿 API 추가**

   - `/strategies/templates` 엔드포인트 구현

5. **테스트 커버리지 확대**
   - `test_data_processor.py` 확장
   - E2E 테스트 작성

### 🟢 Nice to Have (Phase 3 중 개선)

6. **병렬 데이터 수집**

   - `orchestrator.py` asyncio.gather 활용

7. **에러 처리 강화**
   - 재시도 로직 (tenacity)
   - Circuit breaker 패턴

---

## 4. 개선 권장 사항

### 4.1 즉시 조치 (Phase 3 시작 전)

#### Action 1: 중복 엔드포인트 제거

```python
# backend/app/api/routes/backtests.py

# ❌ 제거 대상
@router.post("/integrated", ...)  # Line 379 - POST /{id}/execute와 중복

@router.get("/analytics/summary", ...)  # Line 573 - performance-stats와 통합
```

**이유**:

- 클라이언트 혼동 방지
- API 유지보수 복잡도 감소
- RESTful 원칙 준수

#### Action 2: DuckDB 엔드포인트 정리

**Option A (권장)**: DuckDB 저장 구현 후 실제 활용

```python
# Phase 3 P3.2에서 구현
async def _save_to_duckdb(self, result, trades, portfolio_history):
    # DuckDB에 실제 저장
    ...
```

**Option B**: 엔드포인트 제거

```python
# ❌ 제거
@router.get("/results/duckdb", ...)  # Line 318
```

#### Action 3: 전략 템플릿 API 추가

```python
# backend/app/api/routes/strategies/template.py 활성화

@router.get("/templates", response_model=TemplateListResponse)
async def get_templates():
    """전략 템플릿 목록 조회"""
    ...

@router.post("/templates/{template_id}/clone", response_model=StrategyResponse)
async def clone_template(template_id: str):
    """템플릿에서 전략 생성"""
    ...
```

---

### 4.2 API 구조 개선안

#### 개선된 Backtests API (13 → 10개)

```
✅ 유지 (7개)
POST   /                          # 생성
GET    /                          # 목록
GET    /{id}                      # 상세
PUT    /{id}                      # 수정
DELETE /{id}                      # 삭제
POST   /{id}/execute              # 실행 (Orchestrator)
GET    /{id}/executions           # 실행 기록

✅ 유지 (3개 - 유틸리티)
GET    /health                    # 상태 확인
GET    /analytics/performance     # 성과 분석
GET    /analytics/trades          # 거래 분석

❌ 제거 (3개)
POST   /integrated                # → POST / + POST /{id}/execute 사용
GET    /results/duckdb            # → DuckDB 구현 후 재추가 또는 완전 제거
GET    /analytics/summary         # → /analytics/performance에 통합
```

#### 개선된 Strategies API (8 → 9개)

```
✅ 유지 (5개 - CRUD)
POST   /                          # 생성
GET    /                          # 목록
GET    /{id}                      # 상세
PUT    /{id}                      # 수정
DELETE /{id}                      # 삭제

✅ 유지 (2개 - 실행/조회)
GET    /{id}/executions           # 실행 기록
GET    /{id}/performance          # 성과

⚠️  재검토 (1개)
POST   /{id}/execute              # 용도 명확화 필요

➕ 추가 (2개 - 템플릿)
GET    /templates                 # 템플릿 목록
POST   /templates/{id}/clone      # 템플릿 복제
```

---

### 4.3 Phase 3 작업 우선순위 조정

기존 Phase 3 계획에 다음 작업 추가:

**P3.0 API 정리 (신규)** - 1일

- [ ] 중복 엔드포인트 제거 (`/integrated`, `/analytics/summary`)
- [ ] DuckDB 엔드포인트 결정 (구현 or 제거)
- [ ] 전략 템플릿 API 추가
- [ ] API 문서 업데이트

**P3.1 통합 테스트** - 3일

- [x] BacktestOrchestrator 테스트 (완료)
- [x] StrategyExecutor 테스트 (완료)
- [ ] DataProcessor 테스트 확장
- [ ] E2E 테스트 작성
- [ ] 테스트 유틸리티 작성

**P3.2 성능 최적화** - 3일

- [ ] 병렬 데이터 수집 (asyncio.gather)
- [ ] DuckDB 저장 구현
- [ ] 캐싱 전략 개선
- [ ] 배치 처리

**P3.3 에러 처리** - 2일

- [ ] 재시도 로직 (tenacity)
- [ ] 상세한 에러 메시지
- [ ] Circuit breaker 패턴

**P3.4 모니터링** - 2일

- [ ] 구조화된 로깅
- [ ] 메트릭 수집

**총 예상 기간**: 11일 (기존 10일 + 1일 API 정리)

---

## 5. 점검 결론

### ✅ 긍정적 발견

1. **Phase 1-2 계획 대비 100% 완료**

   - 의존성 주입, TradeEngine, Orchestrator 모두 구현
   - 코드 71% 축소 달성 (700 → 200 lines)

2. **핵심 기능 정상 동작**

   - 백테스트 생성/실행/조회 완료
   - 10개 통합 테스트 통과
   - Orchestrator 패턴 정착

3. **API 구조 대체로 합리적**
   - RESTful 원칙 준수
   - CRUD 완성도 높음

### ⚠️ 개선 필요 사항

1. **DuckDB 저장 미구현** (중간 우선순위)
2. **중복 엔드포인트 정리** (즉시 조치)
3. **전략 템플릿 API 추가** (Phase 3 추가)
4. **테스트 커버리지 확대** (Phase 3 진행)

### 📝 최종 권장 조치

**Phase 3 시작 전 (1일)**:

1. ❌ `/integrated` 엔드포인트 제거
2. ❌ `/analytics/summary` 제거 (performance에 통합)
3. ❌ `/results/duckdb` 제거 또는 주석 처리 (구현 시까지)
4. ➕ `/strategies/templates` 추가

**Phase 3 진행 중**: 5. DuckDB 저장 구현 (P3.2) 6. 병렬 데이터 수집 (P3.2) 7.
테스트 완성 (P3.1) 8. 에러 처리 강화 (P3.3)

---

**다음 단계**: 위 권장 조치 승인 후 Phase 3 본격 진행 🚀
