# Phase 1 기존 훅 통합 계획

**작성일**: 2025-01-16  
**작성자**: GitHub Copilot  
**작업 범위**: Phase 1 완료 후 기존 훅에 AI 데이터 통합

---

## Executive Summary

Phase 1에서 생성한 3개 AI 훅(useMLModel, useRegimeDetection,
usePortfolioForecast)을 기존 훅(useBacktest, useStrategy, useMarketData)에
통합하여 AI 기능을 자연스럽게 연결합니다.

- **작업 시점**: Backend API 구현 완료 후
- **예상 소요**: 2-3일
- **통합 대상**: 3개 기존 훅
- **추가 기능**: 6개 (각 훅당 2개)

---

## 통합 타이밍 및 전제조건

### Phase 1 완료 상태

```
✅ useMLModel (297 lines, 9개 함수)
✅ useRegimeDetection (314 lines, 7개 함수)
✅ usePortfolioForecast (350 lines, 13개 함수)
✅ 총 12개 UI 컴포넌트 (ML 4개, Regime 4개, Forecast 4개)
```

### Backend API 요구사항

```
⏸️ GET /api/v1/ml/models/*                    # ML 모델 API
⏸️ GET /api/v1/ml/regime/detect               # 시장 국면 API
⏸️ GET /api/v1/dashboard/portfolio/forecast   # 포트폴리오 예측 API
```

### 통합 시작 조건

1. **Backend API 100% 구현 완료**
2. **API 응답 데이터 구조 검증**
3. **Frontend-Backend 연동 테스트 통과**

---

## 통합 대상 훅

### 1. useBacktest 확장 (ML 신호 통합)

**현재 상태**:

```typescript
// frontend/src/hooks/useBacktests.ts
export function useBacktest(backtestId: string) {
  const backtestQuery = useQuery({
    queryKey: backtestQueryKeys.detail(backtestId),
    queryFn: async () =>
      (await BacktestService.getBacktest({ path: { backtest_id: backtestId } }))
        .data,
  });

  return {
    backtest: backtestQuery.data,
    isLoading: backtestQuery.isLoading,
    error: backtestQuery.error,
  };
}
```

**통합 후**:

```typescript
export function useBacktest(backtestId: string, options?: { includeMLSignals?: boolean }) {
  const backtestQuery = useQuery({ ... });

  // ML 신호 조회 (옵션)
  const { modelList } = useMLModel({
    enabled: options?.includeMLSignals ?? false,
  });

  // ML 신호 필터링 (백테스트와 관련된 모델만)
  const mlSignals = useMemo(() => {
    if (!backtestQuery.data || !modelList) return [];
    const strategySymbols = backtestQuery.data.strategy?.symbols || [];
    return modelList.filter(model =>
      strategySymbols.some(symbol => model.symbol === symbol)
    );
  }, [backtestQuery.data, modelList]);

  return {
    backtest: backtestQuery.data,
    mlSignals, // 새로 추가
    isLoading: backtestQuery.isLoading || mlSignalsLoading,
    error: backtestQuery.error,
  };
}
```

**추가 기능**:

- `mlSignals`: 백테스트와 관련된 ML 모델 신호
- `includeMLSignals` 옵션: ML 신호 조회 활성화 여부

**사용 예시**:

```typescript
const { backtest, mlSignals } = useBacktest("bt123", {
  includeMLSignals: true,
});

if (mlSignals.length > 0) {
  console.log("ML 신호:", mlSignals[0].predictions);
}
```

---

### 2. useStrategy 확장 (국면 감지 통합)

**현재 상태**:

```typescript
// frontend/src/hooks/useStrategies.ts
export function useStrategy(strategyId: string) {
  const strategyQuery = useQuery({
    queryKey: strategyQueryKeys.detail(strategyId),
    queryFn: async () =>
      (await StrategyService.getStrategy({ path: { strategy_id: strategyId } }))
        .data,
  });

  return {
    strategy: strategyQuery.data,
    isLoading: strategyQuery.isLoading,
    error: strategyQuery.error,
  };
}
```

**통합 후**:

```typescript
export function useStrategy(strategyId: string, options?: { includeRegime?: boolean }) {
  const strategyQuery = useQuery({ ... });

  // 전략 심볼 추출
  const primarySymbol = strategyQuery.data?.symbols?.[0];

  // 시장 국면 조회 (옵션)
  const { currentRegime } = useRegimeDetection({
    symbol: primarySymbol,
    enabled: (options?.includeRegime ?? false) && !!primarySymbol,
  });

  // 국면별 전략 추천
  const regimeBasedRecommendations = useMemo(() => {
    if (!currentRegime) return null;

    const recommendations = {
      bullish: ["추세 추종 전략 강화", "레버리지 고려"],
      bearish: ["방어적 포지션", "헤지 전략 활성화"],
      volatile: ["변동성 돌파 전략", "스톱로스 강화"],
      sideways: ["레인지 트레이딩", "옵션 전략"],
    };

    return recommendations[currentRegime.regime];
  }, [currentRegime]);

  return {
    strategy: strategyQuery.data,
    currentRegime, // 새로 추가
    regimeBasedRecommendations, // 새로 추가
    isLoading: strategyQuery.isLoading,
    error: strategyQuery.error,
  };
}
```

**추가 기능**:

- `currentRegime`: 전략 심볼의 현재 시장 국면
- `regimeBasedRecommendations`: 국면별 전략 추천 (4가지)

**사용 예시**:

```typescript
const { strategy, currentRegime, regimeBasedRecommendations } = useStrategy(
  "st123",
  { includeRegime: true }
);

if (currentRegime?.regime === "bearish") {
  console.log("추천:", regimeBasedRecommendations); // ["방어적 포지션", "헤지 전략 활성화"]
}
```

---

### 3. useMarketData 확장 (예측 데이터 통합)

**현재 상태**:

```typescript
// frontend/src/hooks/useMarketData.ts
export function useMarketData(symbol: string) {
  const marketDataQuery = useQuery({
    queryKey: marketDataQueryKeys.detail(symbol),
    queryFn: async () =>
      (await MarketDataService.getStockData({ path: { symbol } })).data,
  });

  return {
    marketData: marketDataQuery.data,
    isLoading: marketDataQuery.isLoading,
    error: marketDataQuery.error,
  };
}
```

**통합 후**:

```typescript
export function useMarketData(symbol: string, options?: { includeForecast?: boolean; horizonDays?: number }) {
  const marketDataQuery = useQuery({ ... });

  // 포트폴리오 예측 조회 (옵션)
  const { forecastData, scenarios } = usePortfolioForecast({
    horizonDays: options?.horizonDays ?? 30,
    enabled: options?.includeForecast ?? false,
  });

  // 심볼별 예측 필터링 (향후 Backend API 지원 시)
  const symbolForecast = useMemo(() => {
    if (!forecastData) return null;
    // 현재는 포트폴리오 전체 예측만 지원
    // 향후 심볼별 예측 API 추가 시 필터링 로직 구현
    return forecastData;
  }, [forecastData]);

  // 예측 기반 투자 인사이트
  const forecastInsights = useMemo(() => {
    if (!scenarios || scenarios.length === 0) return null;

    const baseScenario = scenarios.find(s => s.scenario === "base");
    if (!baseScenario) return null;

    return {
      expectedReturn: baseScenario.returnPct,
      riskLevel: baseScenario.returnPct > 10 ? "high" : baseScenario.returnPct > 5 ? "medium" : "low",
      recommendation: baseScenario.returnPct > 0 ? "매수 고려" : "관망",
    };
  }, [scenarios]);

  return {
    marketData: marketDataQuery.data,
    symbolForecast, // 새로 추가
    forecastInsights, // 새로 추가
    scenarios, // 새로 추가
    isLoading: marketDataQuery.isLoading,
    error: marketDataQuery.error,
  };
}
```

**추가 기능**:

- `symbolForecast`: 심볼별 포트폴리오 예측 데이터
- `forecastInsights`: 예측 기반 투자 인사이트 (예상 수익률, 리스크, 추천)
- `scenarios`: 시나리오 분석 (Bull/Base/Bear)

**사용 예시**:

```typescript
const { marketData, symbolForecast, forecastInsights } = useMarketData("AAPL", {
  includeForecast: true,
  horizonDays: 30,
});

if (forecastInsights) {
  console.log("예상 수익률:", forecastInsights.expectedReturn); // 5.2%
  console.log("추천:", forecastInsights.recommendation); // "매수 고려"
}
```

---

## 통합 작업 체크리스트

### Phase 1.5: Backend API 구현 (Backend 팀)

- [ ] **ML 모델 API** (3개 엔드포인트)

  - [ ] GET `/api/v1/ml/models` (모델 목록)
  - [ ] GET `/api/v1/ml/models/{version}` (모델 상세)
  - [ ] POST `/api/v1/ml/models/train` (모델 학습)

- [ ] **시장 국면 API** (1개 엔드포인트)

  - [ ] GET `/api/v1/ml/regime/detect?symbol={symbol}&lookback_days={days}`
        (국면 감지)

- [ ] **포트폴리오 예측 API** (1개 엔드포인트)
  - [ ] GET `/api/v1/dashboard/portfolio/forecast?horizon_days={days}` (예측)

### Phase 1.6: Frontend-Backend 연동 테스트

- [ ] **useMLModel 테스트**

  - [ ] 모델 목록 조회 성공
  - [ ] 모델 상세 조회 성공
  - [ ] 모델 학습 트리거 성공
  - [ ] 에러 핸들링 검증

- [ ] **useRegimeDetection 테스트**

  - [ ] 국면 감지 조회 성공
  - [ ] 다양한 lookback_days 테스트
  - [ ] 에러 핸들링 검증

- [ ] **usePortfolioForecast 테스트**
  - [ ] 예측 조회 성공
  - [ ] 다양한 horizon_days 테스트 (7/14/30/60/90)
  - [ ] 시나리오 분석 정상 동작
  - [ ] 에러 핸들링 검증

### Phase 1.7: 기존 훅 통합 (Frontend)

- [ ] **useBacktest 확장** (예상 1일)

  - [ ] `includeMLSignals` 옵션 추가
  - [ ] `mlSignals` 필드 추가
  - [ ] ML 신호 필터링 로직 구현
  - [ ] Unit Test 작성
  - [ ] 백테스트 상세 페이지에서 ML 신호 표시 검증

- [ ] **useStrategy 확장** (예상 1일)

  - [ ] `includeRegime` 옵션 추가
  - [ ] `currentRegime` 필드 추가
  - [ ] `regimeBasedRecommendations` 필드 추가
  - [ ] 국면별 전략 추천 로직 구현
  - [ ] Unit Test 작성
  - [ ] 전략 상세 페이지에서 국면 정보 표시 검증

- [ ] **useMarketData 확장** (예상 1일)
  - [ ] `includeForecast` 옵션 추가
  - [ ] `symbolForecast` 필드 추가
  - [ ] `forecastInsights` 필드 추가
  - [ ] `scenarios` 필드 추가
  - [ ] 예측 기반 인사이트 로직 구현
  - [ ] Unit Test 작성
  - [ ] 마켓 데이터 페이지에서 예측 정보 표시 검증

### Phase 1.8: E2E 테스트

- [ ] **백테스트 + ML 신호 통합 시나리오**

  - [ ] 백테스트 생성 → ML 신호 자동 조회 → 결과 표시
  - [ ] 성능 검증: 전체 흐름 < 5초

- [ ] **전략 + 국면 감지 통합 시나리오**

  - [ ] 전략 조회 → 국면 자동 감지 → 추천 표시
  - [ ] 성능 검증: 전체 흐름 < 3초

- [ ] **마켓 데이터 + 예측 통합 시나리오**
  - [ ] 심볼 조회 → 예측 자동 조회 → 인사이트 표시
  - [ ] 성능 검증: 전체 흐름 < 4초

---

## 통합 후 기대 효과

### 1. 사용자 경험 개선

- **백테스트**: ML 신호를 함께 보며 전략 성과 분석 가능
- **전략**: 현재 시장 국면에 맞는 전략 추천 자동 제공
- **마켓 데이터**: 예측 기반 투자 인사이트 즉시 확인

### 2. 개발자 경험 개선

- **단일 Hook**: 여러 Hook을 조합할 필요 없이 하나의 Hook으로 AI 데이터 접근
- **옵션 기반**: `includeMLSignals`, `includeRegime`, `includeForecast` 옵션으로
  필요한 데이터만 조회
- **타입 안전성**: TypeScript로 AI 데이터 타입 보장

### 3. 성능 최적화

- **조건부 조회**: 옵션이 true일 때만 AI API 호출 (불필요한 네트워크 요청 방지)
- **병렬 조회**: TanStack Query의 병렬 처리로 전체 로딩 시간 단축
- **캐싱**: AI 데이터도 Query Cache 활용

---

## 예상 타임라인

```
2025-01-16 (Today)     Phase 1 완료 ✅
    ↓
2025-01-17 ~ 01-23     Phase 1.5: Backend API 구현 (Backend 팀, 1주)
    ↓
2025-01-24 ~ 01-25     Phase 1.6: Frontend-Backend 연동 테스트 (2일)
    ↓
2025-01-26 ~ 01-28     Phase 1.7: 기존 훅 통합 (Frontend, 3일)
    ↓
2025-01-29 ~ 01-30     Phase 1.8: E2E 테스트 (2일)
    ↓
2025-01-31             Phase 1 전체 완료 🎉
```

**총 예상 소요**: 2주 (Backend 1주 + Frontend 1주)

---

## 결론

기존 훅 통합은 **Backend API 구현 완료 후** 진행하는 것이 가장 효율적입니다.

**이유**:

1. API 응답 데이터 구조를 정확히 알아야 통합 가능
2. 실제 데이터로 테스트하며 통합해야 안정적
3. Mock 데이터로 먼저 통합하면 나중에 재작업 발생

**현재 우선순위**:

1. **Backend API 구현** (가장 중요!)
2. Frontend-Backend 연동 테스트
3. 기존 훅 통합

Phase 1 Frontend 작업은 100% 완료되었으므로, Backend 팀이 API를 구현하는 동안
Phase 2 준비 또는 다른 작업을 진행할 수 있습니다.

---

**작성자**: GitHub Copilot  
**작성일**: 2025-01-16  
**버전**: 1.0
