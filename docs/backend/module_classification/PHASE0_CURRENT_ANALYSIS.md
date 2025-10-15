# Backend 모듈 재구조화 - Phase 0: 현황 분석

**작성일**: 2025-01-15  
**목적**: Phase 5 통합 전 백엔드 디렉토리 구조 개선 및 코드 중복 제거

---

## 1. 현재 구조 분석

### 1.1 디렉토리 구조 개요

```
backend/app/
├── models/                    # 18개 파일 (모델 + 스키마 혼재)
│   ├── base_model.py         # BaseDocument (Beanie)
│   ├── backtest.py           # 240 lines (Enum 4개 + Model 3개)
│   ├── strategy.py           # 155 lines (Enum 2개 + Model 3개)
│   ├── performance.py        # 80 lines
│   ├── data_quality.py
│   ├── optimization.py
│   ├── feature_store.py
│   ├── model_lifecycle.py
│   ├── evaluation.py
│   ├── benchmark.py
│   ├── abtest.py
│   ├── fairness.py
│   ├── prompt_governance.py
│   ├── watchlist.py
│   ├── market_data/          # 9개 파일 (하위 도메인)
│   │   ├── base.py
│   │   ├── stock.py
│   │   ├── crypto.py
│   │   ├── fundamental.py
│   │   ├── economic_indicator.py
│   │   ├── intelligence.py
│   │   ├── technical_indicator.py
│   │   └── regime.py
│   └── chatops/
│       └── session.py
│
├── schemas/                   # 18개 파일 (Pydantic BaseModel)
│   ├── base_schema.py        # BaseSchema
│   ├── backtest.py           # Request/Response schemas
│   ├── strategy.py
│   ├── optimization.py
│   ├── predictive.py
│   ├── narrative.py
│   ├── strategy_builder.py
│   ├── chatops.py
│   ├── evaluation_harness.py
│   ├── feature_store.py
│   ├── model_lifecycle.py
│   ├── prompt_governance.py
│   ├── dashboard.py
│   ├── watchlist.py
│   └── market_data/
│       └── (individual schemas)
│
├── services/                  # 18개 파일 (비즈니스 로직)
│   ├── service_factory.py    # ✅ 싱글톤 팩토리
│   ├── database_manager.py   # ✅ DB 연결 관리
│   ├── backtest_service.py
│   ├── strategy_service.py
│   ├── optimization_service.py
│   ├── regime_detection_service.py
│   ├── portfolio_service.py
│   ├── ml_signal_service.py
│   ├── narrative_report_service.py
│   ├── strategy_builder_service.py
│   ├── chatops_advanced_service.py
│   ├── evaluation_harness_service.py
│   ├── feature_store_service.py
│   ├── model_lifecycle_service.py
│   ├── watchlist_service.py
│   ├── dashboard_service.py
│   ├── probabilistic_kpi_service.py
│   ├── backtest/             # 백테스트 하위 서비스
│   ├── market_data_service/  # 시장 데이터 하위 서비스
│   ├── ml/                   # ML 모델 서비스
│   ├── llm/                  # LLM 서비스
│   └── monitoring/           # 모니터링 서비스
│
└── api/routes/                # 19개 엔드포인트 파일
    ├── health.py             # ✅ 시스템 엔드포인트
    ├── tasks.py              # ✅ 시스템 엔드포인트
    ├── backtests.py
    ├── strategies/
    │   ├── strategy.py
    │   └── template.py
    ├── optimize_backtests.py
    ├── signals.py
    ├── dashboard.py
    ├── narrative.py
    ├── strategy_builder.py
    ├── chatops.py
    ├── chatops_advanced.py
    ├── feature_store.py
    ├── prompt_governance.py
    ├── watchlists.py
    ├── market_data/
    │   └── (individual endpoints)
    └── ml/
        ├── train.py
        ├── lifecycle.py
        └── evaluation.py
```

---

## 2. 주요 문제점

### 2.1 **모델과 스키마 혼재**

#### 문제

- `models/backtest.py`: **Beanie Document (DB)** + **Pydantic Enum (Schema)**
- `schemas/backtest.py`: **Request/Response (API)**
- **중복**: `SignalType`, `StrategyType` 등 Enum이 여러 곳에 정의

#### 예시

```python
# ❌ models/strategy.py (Line 28-35)
class StrategyType(str, Enum):
    SMA_CROSSOVER = "sma_crossover"
    RSI_MEAN_REVERSION = "rsi_mean_reversion"
    ...

# ❌ models/strategy.py (Line 37-41)
class SignalType(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"

# ❌ strategies/base_strategy.py (Line 15-19)
class SignalType(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
```

#### 영향

- Enum 정의 3곳 이상 중복
- 임포트 경로 불명확 (`from models import SignalType` vs
  `from strategies import SignalType`)
- 스키마 변경 시 여러 파일 수정 필요

---

### 2.2 **도메인별 파일 길이 과다**

#### 문제

| 파일                           | 라인 수 | 내용                                    |
| ------------------------------ | ------- | --------------------------------------- |
| `models/backtest.py`           | 240+    | Enum 4개 + BaseModel 4개 + Document 3개 |
| `models/strategy.py`           | 155+    | Enum 2개 + BaseModel 1개 + Document 3개 |
| `models/market_data/base.py`   | 150+    | BaseDocument + Mixin + MarketData       |
| `services/backtest_service.py` | 800+    | CRUD + 백테스트 실행 + 최적화           |

#### 영향

- 코드 네비게이션 어려움
- 한 파일에 여러 책임 (SRP 위반)
- 테스트 작성 복잡도 증가

---

### 2.3 **모듈 명명 불일치**

#### 문제

| 도메인      | Models               | Schemas              | Services                     | Routes                   |
| ----------- | -------------------- | -------------------- | ---------------------------- | ------------------------ |
| 백테스트    | `backtest.py`        | `backtest.py`        | `backtest_service.py`        | `backtests.py`           |
| 전략        | `strategy.py`        | `strategy.py`        | `strategy_service.py`        | `strategies/strategy.py` |
| 최적화      | `optimization.py`    | `optimization.py`    | `optimization_service.py`    | `optimize_backtests.py`  |
| 시장 데이터 | `market_data/`       | `market_data/`       | `market_data_service/`       | `market_data/`           |
| ML 모델     | `model_lifecycle.py` | `model_lifecycle.py` | `model_lifecycle_service.py` | `ml/lifecycle.py`        |

#### 영향

- `optimize_backtests.py` vs `optimization.py` (명명 불일치)
- 엔드포인트 구조 예측 어려움
- MSA 전환 시 모듈 경계 불명확

---

### 2.4 **레거시 vs AI 통합 코드 충돌**

#### 문제: 중복 모델

```python
# ❌ models/strategy.py (레거시)
class Strategy(BaseDocument):
    strategy_type: StrategyType
    config: StrategyConfigUnion  # Union 타입
    is_active: bool

# ❌ models/model_lifecycle.py (AI 통합 프로젝트)
class ModelExperiment(BaseDocument):
    model_id: str
    experiment_name: str
    hyperparameters: dict
    metrics: dict
```

**Strategy vs ModelExperiment 관계 부재**

- 전략 백테스트 → ML 모델 실험 연결 불가
- 성과 지표 중복 (PerformanceMetrics vs ExperimentMetrics)

#### 문제: 데이터 품질 로직 분산

```python
# ❌ models/market_data/base.py
class DataQualityMixin:
    def calculate_quality_score(self) -> float:
        ...

# ❌ models/data_quality.py
class DataQualityEvent(BaseDocument):
    symbol: str
    severity: str
    anomaly_type: str
```

**연결 부재**:

- Mixin의 품질 점수 → Event 생성 로직 없음
- 품질 모니터링 엔드포인트가 Event만 조회 (실시간 점수 미활용)

---

### 2.5 **관리자/시스템 엔드포인트 혼재**

#### 문제

```python
# ✅ 시스템 엔드포인트 (OK)
routes/health.py       # 헬스 체크
routes/tasks.py        # Celery 태스크 관리

# ❌ 사용자 + 관리자 혼재 (BAD)
routes/backtests.py
- GET /backtests          # 사용자: 내 백테스트 조회
- DELETE /backtests/{id}  # 관리자: 모든 백테스트 삭제

routes/ml/lifecycle.py
- GET /experiments        # 사용자: 내 실험 조회
- POST /experiments/{id}/deploy  # 관리자: 프로덕션 배포
```

#### 영향

- 권한 검증 로직 엔드포인트마다 중복
- MSA 전환 시 관리 서비스 분리 어려움
- 보안 감사 추적 복잡

---

## 3. 도메인 경계 분석 (MSA 전환 준비)

### 3.1 핵심 도메인 (Bounded Contexts)

| 도메인                  | 책임                                                   | 현재 파일                                                                         | MSA 후보                   |
| ----------------------- | ------------------------------------------------------ | --------------------------------------------------------------------------------- | -------------------------- |
| **Trading Engine**      | 백테스트 실행, 전략 관리, 포트폴리오 최적화            | `backtest.py`, `strategy.py`, `optimization.py`, `performance.py`                 | ✅ 1순위                   |
| **Market Data**         | 시장 데이터 수집/저장/캐싱 (주식, 암호화폐, 펀더멘털)  | `market_data/` (9개 파일)                                                         | ✅ 1순위                   |
| **ML Platform**         | 모델 학습, 실험 추적, 배포, 평가                       | `model_lifecycle.py`, `evaluation.py`, `benchmark.py`, `abtest.py`, `fairness.py` | ✅ 1순위                   |
| **Feature Engineering** | 피처 생성, 버전 관리, 데이터셋                         | `feature_store.py`                                                                | ⚠️ ML Platform과 통합 가능 |
| **Data Quality**        | 데이터 품질 모니터링, 이상 탐지                        | `data_quality.py`                                                                 | ⚠️ Market Data와 통합 가능 |
| **Generative AI**       | 내러티브 리포트, 전략 빌더, ChatOps, 프롬프트 거버넌스 | `narrative.py`, `strategy_builder.py`, `chatops.py`, `prompt_governance.py`       | ✅ 2순위                   |
| **User Management**     | 워치리스트, 대시보드, 알림                             | `watchlist.py`, `dashboard.py`                                                    | ⚠️ Trading Engine과 통합   |

### 3.2 공유 컴포넌트

| 컴포넌트             | 현재 위치                                        | 역할                                        |
| -------------------- | ------------------------------------------------ | ------------------------------------------- |
| **Enum Types**       | `models/*.py` (분산)                             | SignalType, StrategyType, BacktestStatus 등 |
| **Base Classes**     | `models/base_model.py`, `schemas/base_schema.py` | BaseDocument, BaseSchema                    |
| **Service Factory**  | `services/service_factory.py`                    | ✅ 의존성 주입                              |
| **Database Manager** | `services/database_manager.py`                   | ✅ DuckDB + MongoDB 연결                    |

---

## 4. 재구조화 목표

### 4.1 즉시 해결 (Phase 1)

1. ✅ **Enum 통합**: 모든 Enum을 `schemas/enums.py`로 이동
2. ✅ **모델 파일 분리**: 200+ lines 파일을 50-100 lines로 분할
3. ✅ **명명 일관성**: `optimize_backtests.py` → `optimization.py`
4. ✅ **관리자 엔드포인트 분리**: `api/routes/admin/` 생성

### 4.2 중기 개선 (Phase 2)

1. ⚠️ **레거시 통합**: Strategy ↔ ModelExperiment 관계 정의
2. ⚠️ **데이터 품질 연결**: DataQualityMixin → DataQualityEvent 자동 생성
3. ⚠️ **서비스 레이어 리팩토링**: 800+ lines 서비스를 하위 클래스로 분할

### 4.3 장기 전환 (Phase 3 - MSA)

1. 🔮 **도메인 모듈 패키징**: `trading/`, `market_data/`, `ml_platform/`,
   `gen_ai/`
2. 🔮 **이벤트 주도 통신**: 도메인 간 메시지 큐 (RabbitMQ/Kafka)
3. 🔮 **API Gateway**: Kong/Nginx로 라우팅 통합

---

## 5. 다음 단계

### Phase 1 상세 계획 문서 작성

- `PHASE1_SCHEMA_CONSOLIDATION.md`: Enum 통합 계획
- `PHASE1_MODEL_RESTRUCTURE.md`: 모델 파일 분리 계획
- `PHASE1_SERVICE_REFACTOR.md`: 서비스 레이어 개선
- `PHASE1_ENDPOINT_ALIGNMENT.md`: 엔드포인트 구조 정리

### 예상 타임라인

- **Phase 1 (긴급)**: 3-5일 (Enum 통합 + 파일 분리 + 명명 일관성)
- **Phase 2 (중기)**: 1-2주 (레거시 통합 + 관계 정의)
- **Phase 3 (장기)**: 2-3주 (MSA 준비)

---

## 6. 위험 및 대응

| 위험                      | 영향                | 가능성 | 대응                                                  |
| ------------------------- | ------------------- | ------ | ----------------------------------------------------- |
| 임포트 경로 대규모 변경   | Frontend 빌드 실패  | 높음   | `pnpm gen:client` 자동화, 단계적 마이그레이션         |
| 테스트 깨짐               | CI/CD 실패          | 높음   | 각 Phase마다 pytest 전체 실행, 스냅샷 테스트          |
| 서비스 팩토리 의존성 오류 | 런타임 에러         | 중간   | 의존성 그래프 검증, 통합 테스트 강화                  |
| 데이터 마이그레이션 필요  | MongoDB 스키마 변경 | 낮음   | Beanie migration script, 하위 호환성 배제 (개발 단계) |

---

**다음 문서**: `PHASE1_MASTER_PLAN.md` (재구조화 마스터 플랜)
