# Phase 1: 핵심 AI 기능 구현 계획

> **기간**: 2025-10-15 ~ 2025-10-28 (2주)  
> **우선순위**: 🔴 최우선  
> **목표**: ML 시그널, 시장 국면, 포트폴리오 예측 UI 구축  
> **Backend API**: 8개 엔드포인트 (100% 완료)

---

## 📋 Phase 1 개요

### 비즈니스 가치

사용자가 **ML 기반 트레이딩 신호**, **시장 국면 분석**, **포트폴리오 확률
예측**을 직관적인 UI에서 활용하여, 기존 휴리스틱 전략 대비 향상된 수익률을
달성하고 리스크를 정량적으로 관리할 수 있습니다.

### 주요 산출물

- ✅ **3개 신규 Custom Hooks**: useMLModel, useRegimeDetection,
  usePortfolioForecast
- ✅ **12개 UI 컴포넌트**: 각 기능별 4개씩
- ✅ **8개 API 엔드포인트 연동**: ML 모델 5개, 시장 국면 2개, 예측 1개
- ✅ **2개 신규 페이지**: `/ml/models`, `/market/regime`
- ✅ **기존 훅 통합**: useBacktest에 ML 신호, 국면, 예측 데이터 연동

### 성공 지표 (KPI)

**기술 메트릭**:

- API 엔드포인트 연동: **8/32** (Phase 1 완료 시)
- Custom Hooks: **3/13**
- UI 컴포넌트: **12/60**
- TypeScript/ESLint 에러: **0개**

**성능 메트릭**:

- ML 모델 목록 조회: **< 1초**
- 시장 국면 감지: **< 2초**
- 포트폴리오 예측 (90일): **< 3초**

**비즈니스 메트릭**:

- ML 신호 기반 백테스트: **> 20건/월** (Phase 1 종료 시)

---

## 📅 Sprint 계획

### Sprint 1 (Week 1: 2025-10-15 ~ 2025-10-21)

#### Day 1 (2025-10-15): 환경 설정 🚀

**목표**: OpenAPI 클라이언트 재생성, 필수 라이브러리 설치, 프로젝트 구조 준비

**작업 항목**:

- [ ] `pnpm gen:client` 실행 (Backend 32개 API 타입 생성)
- [ ] 필수 라이브러리 설치:
  ```bash
  cd frontend
  pnpm add recharts d3 lodash date-fns
  pnpm add -D @types/lodash @types/d3
  ```
- [ ] 디렉토리 구조 생성:
  ```bash
  mkdir -p src/hooks src/components/ml-models src/components/market-regime src/components/portfolio-forecast
  touch src/hooks/useMLModel.ts
  touch src/hooks/useRegimeDetection.ts
  touch src/hooks/usePortfolioForecast.ts
  ```
- [ ] TypeScript 빌드 검증 (`pnpm build`)
- [ ] ESLint 검증 (`pnpm lint`)

**예상 소요 시간**: 2시간  
**담당자**: Frontend 엔지니어  
**블로커**: Backend API가 포트 8500에서 실행 중이어야 함

---

#### Day 2-3 (2025-10-16 ~ 2025-10-17): useMLModel 훅 구현

**목표**: ML 모델 조회, 상세, 비교, 학습, 삭제 기능 구현

**작업 항목**:

**Day 2 (훅 인터페이스)**:

- [ ] `useMLModel.ts` 파일 생성
- [ ] Query Key 정의:
  ```typescript
  export const mlModelQueryKeys = {
    all: ["ml-models"] as const,
    lists: () => [...mlModelQueryKeys.all, "list"] as const,
    detail: (version: string) =>
      [...mlModelQueryKeys.all, "detail", version] as const,
    comparison: (metric: string) =>
      [...mlModelQueryKeys.all, "comparison", metric] as const,
  };
  ```
- [ ] `useQuery` 구현 (models, modelDetail, compareModels)
- [ ] `useMutation` 구현 (trainModel, deleteModel)
- [ ] 타입 안전성 검증 (OpenAPI 클라이언트 타입 사용)

**Day 3 (에러 처리 & 테스트)**:

- [ ] Snackbar 통합 (showSuccess, showError)
- [ ] Query 무효화 로직 (invalidateQueries)
- [ ] Loading/Error 상태 처리
- [ ] Unit Test 작성 (Jest + React Testing Library)
  - [ ] models 조회 성공
  - [ ] trainModel 성공 → Query 무효화
  - [ ] API 에러 처리

**예상 소요 시간**: 16시간 (2일)  
**담당자**: Frontend 엔지니어  
**참고 문서**:
[AI_INTEGRATION_USER_STORIES.md - US-6](../AI_INTEGRATION_USER_STORIES.md#us-6)

---

#### Day 4-5 (2025-10-18 ~ 2025-10-19): ML 모델 컴포넌트 4개

**목표**: MLModelList, MLModelDetail, MLModelComparison, MLTrainingDialog 구현

**작업 항목**:

**Day 4 (List & Detail)**:

- [ ] `MLModelList.tsx`:
  - [ ] Material-UI Grid 레이아웃 (size prop)
  - [ ] 모델 카드 (버전, 정확도, 생성일)
  - [ ] 정렬/필터 기능 (최신순, 정확도순)
  - [ ] 빈 상태 (Empty State)
- [ ] `MLModelDetail.tsx`:
  - [ ] 성능 메트릭 차트 (Recharts - LineChart)
  - [ ] 정확도, Precision, Recall, F1 Score
  - [ ] Feature Importance 막대 차트
  - [ ] 모델 삭제 버튼

**Day 5 (Comparison & Training)**:

- [ ] `MLModelComparison.tsx`:
  - [ ] 여러 모델 선택 UI (Checkbox)
  - [ ] 비교 테이블 (메트릭별 컬럼)
  - [ ] 시각화 차트 (Recharts - BarChart)
- [ ] `MLTrainingDialog.tsx`:
  - [ ] 학습 파라미터 폼 (react-hook-form)
  - [ ] 검증 로직 (Pydantic 스키마 대응)
  - [ ] 진행 상태 표시 (isTraining)
  - [ ] 성공/실패 알림

**예상 소요 시간**: 16시간 (2일)  
**담당자**: Frontend 엔지니어  
**UI/UX 리뷰**: Day 5 종료 시

---

#### Day 6-7 (2025-10-20 ~ 2025-10-21): useRegimeDetection 훅 + 컴포넌트 4개

**목표**: 시장 국면 분석 UI 구축

**작업 항목**:

**Day 6 (훅 구현)**:

- [ ] `useRegimeDetection.ts` 파일 생성
- [ ] Query Key 정의
- [ ] `useQuery` 구현:
  - [ ] currentRegime (현재 국면)
  - [ ] regimeHistory (시계열)
- [ ] 타입: `BULL | BEAR | SIDEWAYS | HIGH_VOLATILITY`
- [ ] Unit Test 작성

**Day 7 (컴포넌트 4개)**:

- [ ] `RegimeIndicator.tsx`:
  - [ ] 현재 국면 배지 (색상 코딩: 🟢 BULL, 🔴 BEAR, 🟡 SIDEWAYS, 🟠
        HIGH_VOLATILITY)
  - [ ] 신뢰도 퍼센트 (Chip)
- [ ] `RegimeHistoryChart.tsx`:
  - [ ] 시계열 영역 차트 (Recharts - AreaChart)
  - [ ] 국면 변화 표시 (색상 전환)
- [ ] `RegimeComparison.tsx`:
  - [ ] 여러 심볼 국면 비교 테이블
- [ ] `RegimeStrategyRecommendation.tsx`:
  - [ ] 국면별 추천 전략 카드

**예상 소요 시간**: 12시간 (1.5일 × 2)  
**담당자**: Frontend 엔지니어  
**참고 문서**:
[AI_INTEGRATION_USER_STORIES.md - US-7](../AI_INTEGRATION_USER_STORIES.md#us-7)

---

### Sprint 2 (Week 2: 2025-10-22 ~ 2025-10-28)

#### Day 8-10 (2025-10-22 ~ 2025-10-24): usePortfolioForecast 훅 + 컴포넌트 4개

**목표**: 포트폴리오 확률 예측 UI 구축

**작업 항목**:

**Day 8 (훅 구현)**:

- [ ] `usePortfolioForecast.ts` 파일 생성
- [ ] Query Key 정의 (days 파라미터 포함)
- [ ] `useQuery` 구현:
  - [ ] forecast (중위값, 상한/하한)
  - [ ] scenarios (베어/베이스/불)
  - [ ] riskMetrics (VaR, CVaR)
- [ ] `useState` 구현 (forecastDays, setForecastDays)
- [ ] Unit Test 작성

**Day 9-10 (컴포넌트 4개)**:

- [ ] `ForecastChart.tsx`:
  - [ ] 시계열 차트 (Recharts - LineChart + Area)
  - [ ] 신뢰 구간 (상한/하한 음영)
  - [ ] 툴팁 (날짜, 금액)
- [ ] `ScenarioAnalysis.tsx`:
  - [ ] 시나리오 카드 (베어 -20%, 베이스 +5%, 불 +15%)
  - [ ] 확률 퍼센트 (Chip)
- [ ] `RiskMetricsPanel.tsx`:
  - [ ] VaR, CVaR 지표 (숫자 + 막대)
  - [ ] 드로다운 예측
- [ ] `ForecastControls.tsx`:
  - [ ] 예측 기간 선택 (30, 60, 90일)
  - [ ] 새로고침 버튼

**예상 소요 시간**: 20시간 (2.5일 훅 + 1.5일 컴포넌트)  
**담당자**: Frontend 엔지니어  
**참고 문서**:
[AI_INTEGRATION_USER_STORIES.md - US-8](../AI_INTEGRATION_USER_STORIES.md#us-8)

---

#### Day 11-12 (2025-10-26 ~ 2025-10-27): 기존 훅 통합

**목표**: useBacktest, useStrategy, useMarketData에 ML 신호, 국면, 예측 데이터
연동

**작업 항목**:

**Day 11 (useBacktest 확장)**:

- [ ] `useBacktest.ts` 업데이트:
  - [ ] ML 신호 포함 여부 옵션 추가
  - [ ] 백테스트 결과에 `ml_signals` 필드 추가
  - [ ] 국면 데이터 연동
- [ ] BacktestDetail 페이지 업데이트:
  - [ ] ML vs Heuristic 성과 비교 섹션
  - [ ] 국면별 성과 분석
- [ ] 타입 안전성 검증

**Day 12 (테스트 & 통합 검증)**:

- [ ] E2E 테스트 (Playwright):
  - [ ] ML 모델 조회 < 1초
  - [ ] 시장 국면 감지 < 2초
  - [ ] 포트폴리오 예측 < 3초
  - [ ] 백테스트 생성 (ML 신호 포함)
- [ ] 성능 프로파일링 (Chrome DevTools)
- [ ] 코드 리뷰

**예상 소요 시간**: 16시간 (2일)  
**담당자**: Frontend 엔지니어 + QA

---

#### Day 13 (2025-10-28): Phase 1 완료 및 리뷰

**목표**: Phase 1 산출물 검증, KPI 평가, Phase 2 착수 준비

**작업 항목**:

- [ ] **체크리스트 검증**:
  - [ ] 3개 신규 훅 완성 ✅
  - [ ] 12개 UI 컴포넌트 완성 ✅
  - [ ] 8개 API 엔드포인트 연동 ✅
  - [ ] TypeScript/ESLint 에러 0개 ✅
  - [ ] Unit Test 커버리지 70%+ ✅
  - [ ] E2E 테스트 통과 ✅
- [ ] **KPI 평가**:
  - [ ] ML 모델 조회 < 1초 ✅
  - [ ] 시장 국면 감지 < 2초 ✅
  - [ ] 포트폴리오 예측 < 3초 ✅
- [ ] **Phase 1 리뷰 미팅** (오후 2시, 1시간):
  - [ ] 데모 (ML 모델 조회, 국면 분석, 예측)
  - [ ] KPI 결과 공유
  - [ ] 피드백 수집
  - [ ] Phase 2 착수 승인
- [ ] **문서 업데이트**:
  - [ ] PROJECT_DASHBOARD.md (진행률 업데이트)
  - [ ] Phase 1 완료 리포트 작성

**예상 소요 시간**: 8시간 (1일)  
**담당자**: 전체 팀

---

## 🛠️ 기술 스택 (Phase 1)

### 필수 라이브러리

| 라이브러리            | 버전     | 용도                                     |
| --------------------- | -------- | ---------------------------------------- |
| recharts              | ^2.10.0  | ML 메트릭 차트, 국면 히스토리, 예측 차트 |
| d3                    | ^7.9.0   | 고급 데이터 시각화 (Feature Importance)  |
| lodash                | ^4.17.21 | 유틸리티 (groupBy, sortBy, debounce)     |
| date-fns              | ^3.0.0   | 날짜 포맷팅 (국면 히스토리, 예측 날짜)   |
| @tanstack/react-query | ^5.0.0   | 서버 상태 관리 (이미 설치됨)             |
| @mui/material         | ^6.0.0   | UI 컴포넌트 (이미 설치됨)                |

### 설치 명령어

```bash
cd frontend
pnpm add recharts d3 lodash date-fns
pnpm add -D @types/lodash @types/d3
```

---

## 📊 Backend API 명세 (Phase 1)

### ML 모델 API (5개)

| 메서드 | 엔드포인트                           | 설명                   | 응답 시간 목표 |
| ------ | ------------------------------------ | ---------------------- | -------------- |
| GET    | `/api/v1/ml/models`                  | 모델 목록 조회         | < 1초          |
| GET    | `/api/v1/ml/models/{version}`        | 모델 상세 조회         | < 1초          |
| GET    | `/api/v1/ml/models/compare/{metric}` | 모델 비교              | < 1.5초        |
| POST   | `/api/v1/ml/train`                   | 모델 학습 (Background) | 즉시 반환      |
| DELETE | `/api/v1/ml/models/{version}`        | 모델 삭제              | < 0.5초        |

### 시장 국면 API (2개)

| 메서드 | 엔드포인트                                    | 설명          | 응답 시간 목표 |
| ------ | --------------------------------------------- | ------------- | -------------- |
| GET    | `/api/v1/market-data/regime`                  | 현재 국면     | < 2초          |
| GET    | `/api/v1/market-data/regime/history/{symbol}` | 국면 히스토리 | < 2.5초        |

### 포트폴리오 예측 API (1개)

| 메서드 | 엔드포인트                             | 설명            | 응답 시간 목표 |
| ------ | -------------------------------------- | --------------- | -------------- |
| GET    | `/api/v1/dashboard/portfolio/forecast` | 포트폴리오 예측 | < 3초          |

**총 8개 API 엔드포인트**

---

## 🎯 Custom Hooks 상세 명세

### 1. useMLModel

```typescript
export const useMLModel = (version?: string) => {
  const queryClient = useQueryClient();
  const { showSuccess, showError } = useSnackbar();

  // 모델 목록
  const modelsQuery = useQuery({
    queryKey: mlModelQueryKeys.lists(),
    queryFn: async () => (await MLService.getModels()).data,
    staleTime: 1000 * 60 * 5, // 5분
  });

  // 모델 상세
  const modelDetailQuery = useQuery({
    queryKey: mlModelQueryKeys.detail(version!),
    queryFn: async () => (await MLService.getModel({ version: version! })).data,
    enabled: !!version,
  });

  // 모델 비교
  const compareModelsQuery = useQuery({
    queryKey: mlModelQueryKeys.comparison("f1_score"),
    queryFn: async () =>
      (await MLService.compareModels({ metric: "f1_score" })).data,
  });

  // 모델 학습
  const trainMutation = useMutation({
    mutationFn: (config: MLTrainConfig) =>
      MLService.trainModel({ body: config }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: mlModelQueryKeys.lists() });
      showSuccess("모델 학습이 시작되었습니다");
    },
    onError: () => showError("모델 학습 실패"),
  });

  // 모델 삭제
  const deleteMutation = useMutation({
    mutationFn: (version: string) => MLService.deleteModel({ version }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: mlModelQueryKeys.lists() });
      showSuccess("모델이 삭제되었습니다");
    },
  });

  return {
    models: modelsQuery.data ?? [],
    modelDetail: modelDetailQuery.data,
    compareModels: compareModelsQuery.data,
    trainModel: trainMutation.mutate,
    deleteModel: deleteMutation.mutate,
    isTraining: trainMutation.isPending,
    isLoading: modelsQuery.isLoading,
    error: modelsQuery.error,
  };
};
```

### 2. useRegimeDetection

```typescript
export const useRegimeDetection = (symbol: string = "AAPL") => {
  const currentRegimeQuery = useQuery({
    queryKey: regimeQueryKeys.current(symbol),
    queryFn: async () =>
      (await MarketDataService.getCurrentRegime({ symbol })).data,
    staleTime: 1000 * 60 * 1, // 1분
  });

  const regimeHistoryQuery = useQuery({
    queryKey: regimeQueryKeys.history(symbol),
    queryFn: async () =>
      (await MarketDataService.getRegimeHistory({ symbol })).data,
    staleTime: 1000 * 60 * 5, // 5분
  });

  return {
    currentRegime: currentRegimeQuery.data?.regime,
    regimeConfidence: currentRegimeQuery.data?.confidence,
    regimeHistory: regimeHistoryQuery.data ?? [],
    loading: currentRegimeQuery.isLoading || regimeHistoryQuery.isLoading,
    error: currentRegimeQuery.error || regimeHistoryQuery.error,
  };
};
```

### 3. usePortfolioForecast

```typescript
export const usePortfolioForecast = (initialDays: number = 90) => {
  const [forecastDays, setForecastDays] = useState(initialDays);

  const forecastQuery = useQuery({
    queryKey: portfolioForecastQueryKeys.forecast(forecastDays),
    queryFn: async () =>
      (await DashboardService.getPortfolioForecast({ days: forecastDays }))
        .data,
    staleTime: 1000 * 60 * 10, // 10분
  });

  return {
    forecast: forecastQuery.data?.forecast,
    scenarios: forecastQuery.data?.scenarios,
    riskMetrics: forecastQuery.data?.risk_metrics,
    forecastDays,
    setForecastDays,
    loading: forecastQuery.isLoading,
    error: forecastQuery.error,
  };
};
```

---

## 🧪 테스트 전략

### Unit Tests (Jest + React Testing Library)

**useMLModel.test.ts**:

- [ ] models 조회 성공
- [ ] modelDetail 조회 성공 (version 제공 시)
- [ ] compareModels 조회 성공
- [ ] trainModel 성공 → invalidateQueries 호출
- [ ] deleteModel 성공 → invalidateQueries 호출
- [ ] API 에러 처리 (showError 호출)

**MLModelList.test.tsx**:

- [ ] 모델 목록 렌더링
- [ ] 빈 상태 표시 (models.length === 0)
- [ ] 정렬 기능 (최신순, 정확도순)

### E2E Tests (Playwright)

**ml-models.spec.ts**:

```typescript
test("ML 모델 목록 조회 및 상세 페이지 이동", async ({ page }) => {
  await page.goto("/ml/models");
  await expect(page.locator("h1")).toContainText("ML 모델 목록");

  // 성능 검증
  const startTime = Date.now();
  await page.waitForSelector('[data-testid="ml-model-card"]');
  const loadTime = Date.now() - startTime;
  expect(loadTime).toBeLessThan(1000); // < 1초

  // 상세 페이지 이동
  await page.click('[data-testid="ml-model-card"]:first-child');
  await expect(page).toHaveURL(/\/ml\/models\/v.*/);
  await expect(page.locator('[data-testid="model-accuracy"]')).toBeVisible();
});
```

---

## 🚨 위험 및 대응

| 위험                           | 영향                   | 가능성 | 대응 전략                                              |
| ------------------------------ | ---------------------- | ------ | ------------------------------------------------------ |
| Backend API 응답 지연 (> 3초)  | UX 저하, KPI 미달성    | 중간   | React Query staleTime 활용, 로딩 스피너, 에러 바운더리 |
| recharts 차트 렌더링 느림      | 페이지 로딩 지연       | 낮음   | 데이터 페이지네이션, 가상화 (react-window)             |
| OpenAPI 클라이언트 타입 불일치 | 빌드 에러, 런타임 에러 | 낮음   | `pnpm gen:client` 자동화, TypeScript strict 모드       |
| ML 모델 학습 중 UI 응답 없음   | 사용자 혼란            | 중간   | isTraining 상태 표시, 진행 바, 백그라운드 작업 알림    |

---

## 📚 참고 문서

- **유저 스토리**:
  [AI_INTEGRATION_USER_STORIES.md](../AI_INTEGRATION_USER_STORIES.md) (US-6,
  US-7, US-8)
- **Master Plan**: [MASTER_PLAN.md](../MASTER_PLAN.md)
- **프로젝트 대시보드**: [PROJECT_DASHBOARD.md](../PROJECT_DASHBOARD.md)
- **Backend API 문서**: [http://localhost:8500/docs](http://localhost:8500/docs)

---

**작성자**: Frontend Team  
**승인자**: 퀀트 플랫폼 프론트엔드 리드  
**최종 업데이트**: 2025-10-14  
**다음 리뷰**: Phase 1 완료 시 (2025-10-28)
