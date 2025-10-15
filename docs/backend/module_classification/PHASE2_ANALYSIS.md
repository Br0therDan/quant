# Phase 2 실행 계획 - 대형 파일 분석 결과

**분석일**: 2025-10-15  
**목적**: Phase 2 Step 1 우선순위 결정

---

## 대형 파일 현황 (200+ lines)

### 🔴 Critical (1000+ lines) - 최우선 분할 대상

| 파일                                         | Lines | 도메인         | 우선순위 |
| -------------------------------------------- | ----- | -------------- | -------- |
| `market_data_service/technical_indicator.py` | 1464  | Market Data    | P0       |
| `market_data_service/stock.py`               | 1241  | Market Data    | P0       |
| `market_data_service/intelligence.py`        | 1163  | Market Data    | P0       |
| `database_manager.py`                        | 1111  | Infrastructure | P1       |

### 🟠 High (600-999 lines) - 우선 분할

| 파일                                  | Lines | 도메인      | 우선순위 |
| ------------------------------------- | ----- | ----------- | -------- |
| `market_data_service/fundamental.py`  | 812   | Market Data | P1       |
| `market_data_service/base_service.py` | 664   | Market Data | P1       |
| `market_data_service/crypto.py`       | 627   | Market Data | P2       |
| `backtest/orchestrator.py`            | 608   | Trading     | P0       |

### 🟡 Medium (400-599 lines) - 선택적 분할

| 파일                                                 | Lines | 도메인      | 우선순위 |
| ---------------------------------------------------- | ----- | ----------- | -------- |
| `gen_ai/applications/strategy_builder_service.py`    | 584   | Gen AI      | P2       |
| `trading/strategy_service.py`                        | 527   | Trading     | P1       |
| `ml_platform/services/feature_store_service.py`      | 507   | ML Platform | P2       |
| `trading/optimization_service.py`                    | 490   | Trading     | P2       |
| `user/dashboard_service.py`                          | 478   | User        | P3       |
| `ml_platform/services/model_lifecycle_service.py`    | 476   | ML Platform | P1       |
| `market_data_service/economic_indicator.py`          | 446   | Market Data | P2       |
| `gen_ai/applications/narrative_report_service.py`    | 442   | Gen AI      | P3       |
| `ml_platform/services/evaluation_harness_service.py` | 428   | ML Platform | P2       |
| `ml_platform/services/ml_signal_service.py`          | 423   | ML Platform | P2       |

---

## 분할 전략

### Phase 2.1: Market Data 도메인 정리 (1주)

**이유**: 가장 큰 파일들이 집중되어 있음 (1464 + 1241 + 1163 = 3868 lines)

#### 작업 1: technical_indicator.py (1464 lines)

**현재 구조 예상**:

- 100+ 기술 지표 함수들이 한 파일에 집중

**분할 계획**:

```
market_data_service/indicators/
├── __init__.py
├── trend.py          # SMA, EMA, MACD, etc. (~200 lines)
├── momentum.py       # RSI, Stochastic, etc. (~200 lines)
├── volatility.py     # Bollinger Bands, ATR, etc. (~200 lines)
├── volume.py         # OBV, MFI, etc. (~150 lines)
└── custom.py         # Custom indicators (~150 lines)
```

#### 작업 2: stock.py (1241 lines)

**예상 문제**:

- Alpha Vantage API 호출 로직
- 데이터 변환 및 캐싱
- 여러 시간 프레임 처리

**분할 계획**:

```
market_data_service/stock/
├── __init__.py
├── fetcher.py        # API 호출 로직 (~300 lines)
├── transformer.py    # 데이터 변환 (~250 lines)
├── cache_manager.py  # 캐싱 전략 (~200 lines)
└── validator.py      # 데이터 검증 (~150 lines)
```

#### 작업 3: intelligence.py (1163 lines)

**분할 계획**:

```
market_data_service/intelligence/
├── __init__.py
├── news_analyzer.py    # 뉴스 분석 (~300 lines)
├── sentiment.py        # 감성 분석 (~250 lines)
├── topic_extractor.py  # 토픽 추출 (~200 lines)
└── aggregator.py       # 결과 집계 (~200 lines)
```

---

### Phase 2.2: Trading 도메인 정리 (3-4일)

#### 작업 4: backtest/orchestrator.py (608 lines)

**분할 계획** (이미 PHASE1_COMPLETION_SUMMARY.md에 있음):

```
backtest/
├── orchestrator.py       # 코어 오케스트레이션 (~150 lines)
├── validator.py          # 입력 검증 (~100 lines)
├── executor.py           # 실행 로직 (~150 lines)
├── calculator.py         # 성과 계산 (~100 lines)
└── reporter.py           # 결과 리포팅 (~100 lines)
```

#### 작업 5: strategy_service.py (527 lines)

**분할 계획**:

```
trading/strategy/
├── service.py           # 코어 서비스 (~150 lines)
├── validator.py         # 전략 검증 (~100 lines)
├── parameter_manager.py # 파라미터 관리 (~150 lines)
└── template_loader.py   # 템플릿 로딩 (~100 lines)
```

---

### Phase 2.3: ML Platform 도메인 정리 (2-3일)

#### 작업 6: model_lifecycle_service.py (476 lines)

**분할 계획**:

```
ml_platform/services/model_lifecycle/
├── service.py           # 코어 서비스 (~100 lines)
├── experiment_manager.py # 실험 관리 (~120 lines)
├── deployment_manager.py # 배포 관리 (~120 lines)
└── drift_monitor.py      # 드리프트 모니터 (~120 lines)
```

---

## 수정된 Phase 2 타임라인

| Week       | Task              | Files                                    | Priority |
| ---------- | ----------------- | ---------------------------------------- | -------- |
| **Week 1** | Market Data 정리  | technical_indicator, stock, intelligence | P0       |
| **Week 2** | Trading + ML 정리 | orchestrator, strategy, model_lifecycle  | P0-P1    |
| **Week 3** | 중복 코드 제거    | utils 생성, 공통 로직 추출               | P1       |
| **Week 4** | 테스트 + 문서화   | 커버리지 85%+, docstrings                | P1       |

---

## 즉시 시작 작업

### Option A: Market Data 우선 (권장)

**이유**:

- 가장 큰 파일들 (3868 lines)
- 독립적인 도메인 (의존성 낮음)
- 즉각적인 효과 (파일 크기 대폭 감소)

**시작 파일**: `technical_indicator.py` (1464 lines)

### Option B: Trading 우선 (대안)

**이유**:

- 핵심 비즈니스 로직
- Phase 1에서 이미 분석 완료 (orchestrator)
- 중요도 높음

**시작 파일**: `backtest/orchestrator.py` (608 lines)

---

## 결정 요청

어느 옵션으로 시작할까요?

1. **Option A**: Market Data 정리 (technical_indicator.py 1464 lines)
2. **Option B**: Trading 정리 (backtest/orchestrator.py 608 lines)

또는 다른 우선순위가 있으신가요?

---

**작성자**: Backend Team  
**상태**: ⏸️ 결정 대기
