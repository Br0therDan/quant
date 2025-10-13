# AI Integration 통합 로드맵

**작성일**: 2025년 10월 14일  
**목적**: Strategy & Backtest Phase 3 완료 내용을 AI Integration 프로젝트에
통합하고 향후 계획 수립

---

## 📋 Executive Summary

### 현재 상태

- **Phase 3 (Strategy & Backtest) 완료**: 성능 최적화, ML 기반 시그널 생성,
  Circuit Breaker, 구조화 로깅 완료
- **AI Integration Phase 1**: ML 시그널 서비스 기본 구현 완료 (LightGBM 90.6%
  정확도)
- **AI Integration Phase 2**: 데이터 품질 센티널(D3) 가동, MarketDataService
  적재에 이상 탐지/웹훅/대시보드 연동 완료
- **Production Ready**: 현재 시스템은 프로덕션 배포 가능 상태

### 통합 전략

Phase 3의 ML Integration 성과를 AI Integration 프로젝트의 **Phase 1 (예측
인텔리전스 기초 구축)** 의 첫 번째 마일스톤으로 병합하고, 나머지 AI 기능을
단계적으로 추가합니다.

---

## ⚠️ Phase 3 미구현 기능 → AI Integration 통합 현황

### Phase 3에서 선택 사항으로 남긴 기능들의 통합 상태

| Phase 3 미구현 기능                 | 구현 필요성 | AI Integration 통합 위치                    | 우선순위 | 예상 기간   |
| ----------------------------------- | ----------- | ------------------------------------------- | -------- | ----------- |
| **Real-time Streaming (WebSocket)** | 🟡 중간     | ✅ Phase 4.1 (선택)                         | P3       | 2-3일       |
| **Multi-strategy Portfolio**        | 🟢 높음     | ✅ Phase 2 Milestone 1 (Optuna) + Phase 4.2 | P1       | 1주 + 3-5일 |
| **Advanced Risk Metrics**           | 🟢 높음     | ✅ Phase 1 Milestone 3 (VaR 예측) + Phase 2 | P1       | 3주         |

**통합 전략**:

1. **Advanced Risk Metrics** (VaR, CVaR, Sortino, Calmar)

   - ✅ Phase 1 Milestone 3: 포트폴리오 확률 예측에서 VaR/CVaR 구현
   - ✅ Phase 2: PerformanceAnalyzer에 Sortino, Calmar Ratio 추가
   - **즉시 시작 가능**: Phase 1 Milestone 2 (국면 분류) 완료 후

2. **Multi-strategy Portfolio** (Markowitz 최적화, 리밸런싱)

   - ✅ Phase 2 Milestone 1: Optuna 백테스트 옵티마이저 (전제 조건)
   - ✅ Phase 4.2: MultiStrategyOrchestrator, PortfolioOptimizer 구현
   - **의존성**: Optuna 옵티마이저 완료 필요

3. **Real-time Streaming** (WebSocket 진행률 업데이트)
   - ✅ Phase 4.1: WebSocket 엔드포인트, 진행률 이벤트
   - **우선순위**: 낮음 (polling으로 대체 가능)
   - **구현 시기**: Phase 3 완료 후 (선택 사항)

**결론**: Phase 3의 모든 미구현 기능이 AI Integration 로드맵에 **완전히
통합**되어 있으며, 우선순위와 의존성이 명확하게 정의되어 있습니다. **별도로
Phase 3 미구현 기능을 마무리할 필요 없이, AI Integration 프로젝트를 그대로
진행하면 됩니다.**

---

## 🎯 Phase 3 완료 내용 → AI Integration 매핑

### Phase 3 성과 요약

| Phase 3 항목              | 구현 내용                         | AI Integration 매핑                |
| ------------------------- | --------------------------------- | ---------------------------------- |
| **P3.0: API 중복 제거**   | 레거시 엔드포인트 3개 제거        | 기반 작업 (아키텍처 정리)          |
| **P3.1: 단위 테스트**     | 23개 테스트 케이스                | 품질 보증 (모든 AI 기능 전제 조건) |
| **P3.2: 성능 최적화**     | 병렬 데이터 수집 (3-10x 속도)     | Phase 1 - 데이터 파이프라인 최적화 |
| **P3.2: DuckDB 캐시**     | 시계열 저장 (97% 성능 향상)       | Phase 1 - 피처 스토어 기초         |
| **P3.2: ML Integration**  | LightGBM 신호 생성 (90.6% 정확도) | **Phase 1 - Milestone 1 완료** ✅  |
| **P3.3: Circuit Breaker** | Alpha Vantage API 보호            | Phase 1 - 데이터 품질 보장         |
| **P3.4: 구조화 로깅**     | BacktestMonitor 메트릭 수집       | Phase 4 - MLOps 모니터링 기초      |

### Phase 3.2 ML Integration 세부 구현

**완료된 컴포넌트**:

1. **FeatureEngineer** (`backend/app/services/ml/feature_engineer.py`)

   - 22개 기술적 지표 자동 계산
   - RSI, MACD, Bollinger Bands, SMA(5,10,20,50), EMA(12,26)
   - Volume 지표, Price changes, Momentum indicators

2. **MLModelTrainer** (`backend/app/services/ml/trainer.py`)

   - LightGBM 기반 바이너리 분류
   - Train/Test split, Feature importance 분석
   - Model save/load, Evaluation metrics

3. **ModelRegistry** (`backend/app/services/ml/model_registry.py`)

   - JSON 기반 모델 버전 관리 (v1, v2, ...)
   - Model metadata 추적
   - Model comparison & best model selection

4. **MLSignalService** (`backend/app/services/ml_signal_service.py`)

   - ML 모델 기반 신호 생성
   - Heuristic fallback 메커니즘
   - Feature importance 기반 contribution 분석

5. **ML Training API** (`backend/app/api/routes/ml/train.py`)

   - 5개 REST 엔드포인트
   - Background task 기반 비동기 학습
   - Model CRUD 및 비교 기능

6. **Integration Tests** (`backend/tests/test_ml_integration.py`)
   - E2E 워크플로우 검증
   - Model 정확도 테스트
   - ML vs Heuristic 비교

**성과 지표**:

```
Model Accuracy:          90.62%
F1 Score:                87.65%
ML vs Heuristic Diff:    65.17% (significant!)
Top Feature:             volume_ratio (importance: 215.27)
Training Samples:        369 (AAPL + MSFT)
API Response Time:       < 200ms (cached)
```

---

## 🚀 AI Integration 통합 로드맵

### Phase 1: 예측 인텔리전스 기초 구축 (진행 중)

**기간**: 2025-01-06 ~ 2025-02-14  
**상태**: 🟢 정상 진행 (35% 완료)

#### Milestone 1: ML 시그널 API ✅ **완료** (Phase 3.2)

- [x] FeatureEngineer 구현
- [x] MLModelTrainer 구현
- [x] ModelRegistry 구현
- [x] MLSignalService 통합
- [x] Training API 5개 엔드포인트
- [x] Integration tests
- [x] 90.6% 정확도 달성

**다음 개선 사항**:

- [ ] 모델 재학습 자동화 (주기적 또는 drift 감지 시)
- [ ] Multi-symbol 배치 예측 (현재는 단일 심볼)
- [ ] Feature importance 대시보드 시각화

#### Milestone 2: 시장 국면 분류 (다음 단계)

**목표**: 시장 국면(강세, 약세, 횡보, 고변동성) 자동 감지

**우선순위**: 🟢 높음 (전략 파라미터 적응형 조정 가능)

**구현 계획** (2주):

```python
# 1. RegimeDetectionService 생성
backend/app/services/ml/regime_detector.py

# 핵심 기능:
- Hidden Markov Model (HMM) 기반 국면 분류
- 4가지 국면: 강세(Bullish), 약세(Bearish), 횡보(Sideways), 고변동(HighVolatility)
- 다자산 상관관계 기반 분석

# 2. API 엔드포인트
GET /api/v1/market-data/regime
GET /api/v1/market-data/regime/history/{symbol}

# 3. MongoDB 캐시
- 일별 국면 라벨 저장
- DashboardService와 통합

# 4. 전략 통합
- StrategyExecutor가 국면별 파라미터 세트 사용
- 예: 강세장에서 공격적, 약세장에서 방어적
```

**기대 효과**:

- 시장 변화에 적응형 전략
- 리스크 관리 개선 (국면 전환 감지 시 알림)
- 백테스트 결과에 국면 컨텍스트 제공

**의존성**:

- DuckDB 다자산 데이터 (이미 구현됨)
- PerformanceAnalyzer 메트릭 (이미 구현됨)

#### Milestone 3: 포트폴리오 확률 KPI 예측 (3주차)

**목표**: 단기 포트폴리오 가치 분포 및 VaR 예측

**우선순위**: 🟡 중간 (Phase 4.3 Advanced Risk Metrics와 연계)

**구현 계획**:

```python
# 1. PortfolioForecastService 생성
backend/app/services/ml/portfolio_forecast.py

# 핵심 기능:
- Prophet 또는 GluonTS 기반 시계열 예측
- 5/95 퍼센타일 신뢰 구간
- VaR (Value at Risk) 계산

# 2. API 엔드포인트
GET /api/v1/portfolio/forecast/{days}
  → 응답: { "mean": ..., "percentile_5": ..., "percentile_95": ... }

# 3. DuckDB 저장
- 예측 분포 히스토리 저장
- 실제 값 vs 예측 값 비교 (백테스트)
```

**Phase 4.3 연계**:

- VaR/CVaR 계산과 통합
- Sortino/Calmar Ratio와 결합

---

### Phase 2: 자동화 및 최적화 루프

**기간**: 2025-02-17 ~ 2025-03-28 **상태**: 🟡 위험 완화 (D3 센티널 완료, D1/D2
대기)

#### Milestone 1: Optuna 백테스트 옵티마이저 (Phase 4 통합)

**목표**: 전략 파라미터 자동 튜닝

**우선순위**: 🟢 높음 (Phase 4.2 Multi-strategy Portfolio의 전제 조건)

**구현 계획** (1주):

```python
# 1. OptimizationService 생성
backend/app/services/backtest/optimization_service.py

# 핵심 기능:
- Optuna Study 관리
- 병렬 백테스트 실행 (asyncio)
- MongoDB에 실험 메타데이터 저장

# 2. API 엔드포인트
POST /api/v1/backtests/optimize
  Body: {
    "strategy_id": "...",
    "param_space": { "rsi_period": [10, 30], ... },
    "n_trials": 100,
    "objective": "sharpe_ratio"
  }
  → 비동기 작업 시작, task_id 반환

GET /api/v1/backtests/optimize/{task_id}
  → 진행 상황 및 최적 파라미터

# 3. 시각화
- DashboardService에 최적화 히스토리 차트
- 파라미터 중요도 분석 (Optuna visualization)
```

**기대 효과**:

- 수동 그리드 서치 제거
- 신규 전략 가치 실현 시간 단축 (2주 → 2일)
- 파라미터 최신성 유지

**Phase 4.2 연계**:

- Multi-strategy Portfolio 최적화 시 사용
- 전략 간 상관관계 고려한 자본 배분

#### Milestone 2: 강화학습 실행기 (선택 사항)

**목표**: RL 기반 포지션 사이징 및 타이밍

**우선순위**: 🔴 낮음 (컴퓨트 리소스 제약)

**상태**: 차단됨 (GPU 용량 산정 필요)

**구현 계획** (Phase 3 이후로 연기):

```python
# TradingSimulator를 OpenAI Gym 환경으로 래핑
# Stable-Baselines3 PPO/A2C 정책 학습
# 체크포인트 저장 및 백테스트 평가
```

**연기 사유**:

- 학습 시간 과다 (수 시간 ~ 수일)
- 현재 ML 시그널로 충분한 성과
- Phase 4 이후 재평가

#### Milestone 3: 데이터 품질 센티널

**목표**: 이상 데이터 자동 탐지 및 격리

**상태**: ✅ 완료 (2025-10-14)

**구현 결과**:

- `DataQualitySentinel`이 일별 주가를 스코어링하며 `DailyPrice`에 이상 지표를
  주입하고, 비정상 케이스는 `DataQualityEvent` 컬렉션으로 영속화
- Isolation Forest, Prophet 기반 잔차, 거래량 Z-Score를 결합해 심각도를 산출하고
  HIGH 이상은 환경 변수 기반 웹훅으로 통지
- DashboardService가 `DataQualitySummary` 응답으로 24시간 요약과 최근 경보를
  노출, MarketDataService 적재 루틴과 ServiceFactory 레지스트리가 센티널을 공유

**후속 과제**:

- RL/Optuna 실행 결과에 데이터 품질 지표를 결합하여 Phase 2 전체 자동화 루프에
  위험 신호를 연결
- 알림 확인 워크플로우와 대시보드 필터를 Phase 3 ChatOps 통합 시 확장

---

### Phase 3: 생성형 인사이트 & ChatOps

**기간**: 2025-03-31 ~ 2025-05-09  
**상태**: 🟢 정상 진행 (65% 완료)

#### Milestone 1: 내러티브 리포트 생성기 ✅ **완료 (90%)** (2025-10-14)

**목표**: 백테스트 결과를 자연어 요약으로 자동 생성

**우선순위**: � 높음 (임원 보고용)

**완료 상태** (2025-10-14):

- ✅ NarrativeReportService 구현 (439 lines)
- ✅ OpenAI GPT-4 통합
- ✅ API 엔드포인트 완료
- ✅ Fact checking 완료
- ⏳ Unit tests 보류

#### Milestone 2: 대화형 전략 빌더 ✅ **완료 (Core 80%)** (2025-10-14)

**목표**: 자연어 → 전략 파라미터 변환

**우선순위**: � 높음 (사용자 온보딩)

**구현 계획** (1.5주):

```python
# 1. StrategyBuilderService 생성
backend/app/services/llm/strategy_builder.py

# 핵심 기능:
- 사용자 의도를 기존 전략 템플릿으로 매핑
- Sentence Transformers 임베딩 유사도 검색
- LLM이 파라미터 제안

# 2. API 엔드포인트
POST /api/v1/strategies/generative-builder
  Body: { "description": "RSI가 30 이하일 때 매수하고 70 이상일 때 매도" }
  → 응답: {
    "strategy_type": "RSI_STRATEGY",
    "parameters": { "buy_threshold": 30, "sell_threshold": 70 },
    "confidence": 0.92
  }

# 3. 검증
- StrategyService의 Pydantic 스키마로 검증
- 유효하지 않은 파라미터는 기본값으로 대체
```

**기대 효과**:

- 비프로그래머도 전략 생성 가능
- 온보딩 시간 단축 (1시간 → 5분)
- 전략 템플릿 접근성 민주화

#### Milestone 3: ChatOps 운영 에이전트

**목표**: 시스템 상태 모니터링 대화형 봇

**우선순위**: 🟡 중간 (운영 효율성 개선)

**구현 계획** (1주):

```python
# 1. ChatOpsAgent 생성
backend/app/services/llm/chatops_agent.py

# 핵심 기능:
- Function calling 기반 LLM 에이전트
- MarketDataService.health_check() 등 기존 API 호출
- RBAC 권한 검사

# 2. 도구 함수 등록
tools = [
  "get_cache_status",      # DuckDB 캐시 상태
  "list_recent_failures",  # 최근 실패한 백테스트
  "check_alpha_vantage",   # Alpha Vantage API 상태
  "get_model_metrics",     # ML 모델 성능
]

# 3. 배포 옵션
- FastAPI 엔드포인트: POST /api/v1/chatops
- Slack 봇 통합 (선택)
```

**사용 예시**:

```
사용자: "현재 DuckDB 캐시 적중률은?"
봇:    "DuckDB 캐시 적중률: 97.3% (지난 24시간)"

사용자: "최근 실패한 백테스트 목록"
봇:    "최근 3건의 실패:
       - Backtest #123: Alpha Vantage rate limit
       - Backtest #124: Invalid strategy parameter
       - Backtest #125: Symbol not found"
```

**진행 상황 (2025-10-14):** FastAPI `/api/v1/chatops` 라우트와 `ChatOpsAgent`가
데이터 품질 센티널 요약, DuckDB/MongoDB 캐시 상태, Alpha Vantage 헬스체크를 RBAC
기반으로 응답하도록 배포되었습니다.

---

### Phase 4: MLOps 플랫폼 가동

**기간**: 2025-05-12 ~ 2025-06-20  
**상태**: 🔵 기획 중

#### Milestone 1: 피처 스토어 거버넌스

**목표**: DuckDB 기반 중앙화된 피처 저장소

**우선순위**: 🟢 높음 (모든 ML 모델의 기반)

**구현 계획** (2주):

```python
# 1. FeatureStore 서비스
backend/app/services/ml/feature_store.py

# 핵심 기능:
- DuckDB 뷰로 피처 정의
- 버전 관리 (v1, v2, ...)
- 피처 메타데이터 추적 (생성 일시, 계산 로직, 의존성)

# 2. 표준화된 피처 뷰
CREATE VIEW feature_store_v1 AS
SELECT
  symbol,
  date,
  -- OHLCV
  open, high, low, close, volume,
  -- Technical Indicators (FeatureEngineer 출력)
  rsi_14, macd, macd_signal, bb_upper, bb_lower,
  sma_5, sma_10, sma_20, sma_50,
  ema_12, ema_26,
  volume_ratio, volume_sma_20,
  price_change_1d, price_change_5d,
  -- Regime Labels
  market_regime
FROM market_data_enriched;

# 3. API 엔드포인트
GET /api/v1/features/{version}/{symbol}
GET /api/v1/features/metadata
```

**기대 효과**:

- ML 모델 간 피처 재사용
- 피처 계산 중복 제거
- 일관성 보장 (모든 모델이 동일한 피처 사용)

#### Milestone 2: 모델 레지스트리 확장

**목표**: MLflow/W&B 통합

**우선순위**: 🟢 높음 (모델 거버넌스)

**구현 계획** (1.5주):

```python
# 1. MLflow 통합
backend/app/services/ml/mlflow_registry.py

# 핵심 기능:
- MLflow Tracking Server 연동
- 실험 로그 자동화 (하이퍼파라미터, 메트릭, 아티팩트)
- MongoDB에 모델 메타데이터 동기화

# 2. 모델 재학습 파이프라인
- Celery 작업으로 주기적 재학습 (주간/월간)
- Drift 감지 시 자동 재학습
- A/B 테스트 프레임워크 (새 모델 vs 기존 모델)

# 3. API 확장
GET /api/v1/ml/experiments
GET /api/v1/ml/models/{model_name}/compare
  → 여러 버전의 모델 성능 비교
```

**기대 효과**:

- 실험 추적성 확보
- 모델 성능 드리프트 감지
- 롤백 기능 (버전 관리)

#### Milestone 3: 평가 하니스

**목표**: AI 컴포넌트 검증 및 벤치마크

**우선순위**: 🟡 중간 (컴플라이언스)

**구현 계획** (1주):

```python
# 1. EvaluationHarness 생성
backend/app/services/ml/evaluation_harness.py

# 핵심 기능:
- 과거 기간 재생 백테스트
- 기준 전략과 비교 (Buy & Hold, SMA Crossover 등)
- 설명 가능성 산출물 (SHAP values, Feature importance)

# 2. 벤치마크 스위트
- 2008 금융위기, 2020 코로나 급락 등 주요 이벤트 시뮬레이션
- ML 시그널 vs Heuristic 비교
- 국면별 성과 분석

# 3. 리포트 생성
- HTML 리포트 (모델 성능, 리스크 지표, 설명 가능성)
- PDF 내보내기 (규제 제출용)
```

**기대 효과**:

- 리스크 및 컴플라이언스 요구 충족
- 모델 신뢰성 검증
- 투명성 확보 (설명 가능한 AI)

---

## 📊 통합 우선순위 매트릭스

| 에픽                     | Phase | 비즈니스 가치 | 구현 복잡도 | 의존성      | 우선순위 | 예상 기간          |
| ------------------------ | ----- | ------------- | ----------- | ----------- | -------- | ------------------ |
| **ML 시그널 API**        | 1     | 매우 높음     | 중간        | 없음        | P0       | ✅ 완료            |
| **시장 국면 분류**       | 1     | 높음          | 중간        | DuckDB      | P1       | 2주                |
| **데이터 품질 센티널**   | 2     | 높음          | 낮음        | 없음        | P1       | ✅ 완료            |
| **Optuna 옵티마이저**    | 2     | 매우 높음     | 중간        | Phase 1     | P1       | 1주                |
| **피처 스토어**          | 4     | 매우 높음     | 중간        | Phase 1     | P1       | 2주                |
| **모델 레지스트리 확장** | 4     | 높음          | 중간        | 피처 스토어 | P2       | 1.5주              |
| **포트폴리오 예측**      | 1     | 중간          | 높음        | Phase 1     | P2       | 3주                |
| **내러티브 리포트**      | 3     | 높음          | 낮음        | Phase 1     | P2       | ✅ 완료            |
| **대화형 전략 빌더**     | 3     | 높음          | 중간        | 없음        | P2       | ✅ 완료 (Core 80%) |
| **ChatOps 에이전트**     | 3     | 중간          | 낮음        | Phase 1     | P3       | ✅ 완료            |
| **평가 하니스**          | 4     | 중간          | 낮음        | Phase 1     | P3       | 1주                |
| **강화학습 실행기**      | 2     | 낮음          | 매우 높음   | GPU         | P4       | 차단됨             |

### 우선순위 정의

- **P0**: 이미 완료된 항목
- **P1**: 즉시 시작 권장 (다른 기능의 전제 조건 또는 높은 비즈니스 가치)
- **P2**: Phase 1 완료 후 시작
- **P3**: Phase 2 완료 후 시작 (선택 사항)
- **P4**: 리소스 제약으로 연기

---

## 🗓️ 단계별 실행 계획

### Q1 2025 (1-3월): Phase 1 완료

**주요 목표**: 예측 인텔리전스 기초 완성

**Week 1-2**:

- [x] ML 시그널 API 완료 (Phase 3.2에서 완료)
- [ ] 시장 국면 분류 구현
- [x] 데이터 품질 센티널 구현 (완료)

**Week 3-5**:

- [ ] 포트폴리오 확률 예측 구현
- [ ] Phase 1 통합 테스트
- [ ] 문서화 및 API 가이드

**산출물**:

- ML 시그널 API (완료)
- 시장 국면 감지 API
- 데이터 품질 모니터링 대시보드 (운영 중)
- 포트폴리오 예측 API

### Q2 2025 (4-6월): Phase 2 + Phase 4 기초

**주요 목표**: 자동화 최적화 + MLOps 기반 구축

**Week 1-2**:

- [ ] Optuna 백테스트 옵티마이저
- [ ] 피처 스토어 구현

**Week 3-4**:

- [ ] 모델 레지스트리 MLflow 통합
- [ ] 자동 재학습 파이프라인

**Week 5-6**:

- [ ] Phase 2 통합 테스트
- [ ] 성능 벤치마크

**산출물**:

- 백테스트 옵티마이저 API
- 중앙화된 피처 스토어
- MLflow 모델 레지스트리

### Q3 2025 (7-9월): Phase 3 완료 + Phase 4 시작

**주요 목표**: 생성형 AI 완성 + MLOps 플랫폼

**Week 1-3**:

- [x] 내러티브 리포트 생성기 (완료)
- [x] 대화형 전략 빌더 (Core 완료)
- [x] ChatOps 에이전트 (완료)

**Week 4-6** (예정):

- [ ] 임베딩 인덱스 확장 (30+ 지표)
- [ ] MongoDB 승인 로그 저장
- [ ] 평가 하니스
- [ ] 벤치마크 스위트
- [ ] 최종 통합 테스트

**산출물**:

- ✅ LLM 기반 리포트 생성 API
- ✅ 자연어 전략 빌더 (Core)
- ✅ ChatOps 운영 봇 (FastAPI 기반)
- ⏳ 평가 하니스 및 벤치마크 (계획)

---

## 🎯 Phase 3 → AI Integration 병합 작업

### 즉시 수행 작업

1. **문서 통합**

   - [x] `PHASE_3_4_STATUS.md` 생성 완료
   - [x] `PHASE_3_2_ML_INTEGRATION_COMPLETE.md` 생성 완료
   - [ ] 이 문서를 `MASTER_PLAN.md`와 병합
   - [ ] `PROJECT_DASHBOARD.md` 업데이트 (Phase 1 Milestone 1 완료 표시)

2. **코드 정리**

   - [ ] ML 서비스를 `backend/app/services/ml/` 디렉터리에 통합 (완료)
   - [ ] API 라우트 문서화 (`/docs` 엔드포인트)
   - [ ] OpenAPI 스키마 업데이트 (`pnpm gen:client`)

3. **테스트 강화**

   - [ ] ML Integration 테스트에 국면 분류 시나리오 추가
   - [ ] 데이터 품질 센티널 테스트 작성
   - [ ] E2E 테스트: 데이터 수집 → ML 시그널 → 백테스트

4. **모니터링**
   - [ ] ML 모델 성능 메트릭 대시보드
   - [ ] Feature importance 시각화
   - [ ] 모델 drift 알림 설정

---

## 📈 성공 지표 (KPI)

### Phase 1 (예측 인텔리전스)

| 지표                | 목표    | 현재    | 상태         |
| ------------------- | ------- | ------- | ------------ |
| ML 시그널 정확도    | > 85%   | 90.6%   | ✅ 초과 달성 |
| 국면 분류 정확도    | > 80%   | TBD     | 🟡 진행 중   |
| 포트폴리오 예측 MAE | < 5%    | TBD     | ⚪ 미시작    |
| API 응답 시간       | < 200ms | < 200ms | ✅ 달성      |

### Phase 2 (자동화 최적화)

| 지표               | 목표                 | 현재               | 상태       |
| ------------------ | -------------------- | ------------------ | ---------- |
| 최적화 수렴 시간   | < 1시간 (100 trials) | TBD                | ⚪ 미시작  |
| 데이터 이상 감지율 | > 95%                | 초기 24h 통계 수집 | 🟡 측정 중 |
| 파라미터 튜닝 ROI  | Sharpe +20%          | TBD                | ⚪ 미시작  |

### Phase 3 (생성형 AI)

| 지표                | 목표   | 현재                  | 상태       |
| ------------------- | ------ | --------------------- | ---------- |
| 리포트 생성 시간    | < 10초 | TBD                   | ⚪ 미시작  |
| 전략 빌더 신뢰도    | > 90%  | TBD                   | ⚪ 미시작  |
| ChatOps 응답 정확도 | > 95%  | 초기 룰 기반 에이전트 | 🟡 진행 중 |

### Phase 4 (MLOps)

| 지표             | 목표     | 현재 | 상태      |
| ---------------- | -------- | ---- | --------- |
| 피처 재사용률    | > 80%    | TBD  | ⚪ 미시작 |
| 모델 재학습 주기 | 주간     | TBD  | ⚪ 미시작 |
| Drift 감지 속도  | < 24시간 | TBD  | ⚪ 미시작 |

---

## 🚨 위험 및 완화 전략

### 기술 위험

| 위험                         | 영향                | 가능성 | 완화 전략                                         |
| ---------------------------- | ------------------- | ------ | ------------------------------------------------- |
| **Alpha Vantage Rate Limit** | ML 학습 데이터 부족 | 높음   | DuckDB 캐시 + Circuit Breaker (이미 구현됨)       |
| **ML 모델 Drift**            | 예측 정확도 하락    | 중간   | 데이터 품질 센티널 + 주기적 재학습                |
| **LLM 환각**                 | 잘못된 리포트 생성  | 중간   | 구조화된 프롬프트 + Pydantic 검증 + KPI 교차 확인 |
| **컴퓨트 리소스 부족**       | RL 학습 불가        | 높음   | RL은 Phase 4 이후로 연기, GPU 버스트 용량 계획    |

### 프로젝트 위험

| 위험                      | 영향           | 가능성 | 완화 전략                               |
| ------------------------- | -------------- | ------ | --------------------------------------- |
| **Phase 간 의존성**       | 블로킹         | 중간   | 명확한 인터페이스 정의 + Stub 구현      |
| **범위 확장**             | 일정 지연      | 높음   | MVP 우선, 선택 기능은 Phase 3/4로 연기  |
| **ServiceFactory 복잡도** | 통합 속도 저하 | 낮음   | 서비스 등록 템플릿 표준화 (이미 구현됨) |

---

## 📚 참조 문서

### 기존 문서

- **Phase 3 완료 보고서**: `docs/backend/PHASE_3_4_STATUS.md`
- **ML Integration 보고서**: `docs/backend/PHASE_3_2_ML_INTEGRATION_COMPLETE.md`
- **Strategy & Backtest 아키텍처**:
  `docs/backend/strategy_backtest/ARCHITECTURE.md`
- **AI Integration Master Plan**: `docs/backend/ai_integration/MASTER_PLAN.md`
- **Project Dashboard**: `docs/backend/ai_integration/PROJECT_DASHBOARD.md`

### 코드 참조

- **ML 서비스**: `backend/app/services/ml/`
- **ML API**: `backend/app/api/routes/ml/`
- **ML 테스트**: `backend/tests/test_ml_*.py`
- **Orchestrator**: `backend/app/services/backtest/orchestrator.py`

---

## 🎉 결론

### 현재 상태 요약

✅ **Phase 3 완료**: 성능 최적화, ML Integration, Circuit Breaker, 구조화 로깅  
🟢 **AI Integration Phase 1 (35% 완료)**: ML 시그널 API 구현 완료, 국면 분류
다음 단계 🟡 **AI Integration Phase 2 (30% 완료)**: 데이터 품질 센티널 가동,
Optuna/RL 대기 다음 단계  
🚀 **Production Ready**: 현재 시스템은 프로덕션 배포 가능

### 다음 단계 (즉시 시작 가능)

1. **시장 국면 분류 구현** (2주) - Phase 1 Milestone 2
2. **데이터 품질 센티널 운영 지표 정착** (1주) - 경보 튜닝 및 테스트 커버리지
   확장
3. **문서 및 대시보드 업데이트** - 진행 상황 추적

### 장기 비전

- **Q1 2025**: 예측 인텔리전스 완성 (ML 시그널, 국면 분류, 포트폴리오 예측)
- **Q2 2025**: 자동화 최적화 + MLOps 기반 (Optuna, 피처 스토어, 모델 레지스트리)
- **Q3 2025**: 생성형 AI + 평가 하니스 (내러티브 리포트, 전략 빌더, ChatOps)

**Phase 3의 ML Integration 성과를 기반으로, 이제 전체 AI Integration 프로젝트를
단계적으로 완성해 나갈 준비가 완료되었습니다!** 🚀
