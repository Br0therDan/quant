# Phase 2: 최적화 & 모니터링 구현 계획

> **기간**: 2025-10-29 ~ 2025-11-04 (1주)  
> **우선순위**: 🟠 높음  
> **목표**: 백테스트 자동 최적화 + 데이터 품질 대시보드  
> **Backend API**: 5개 엔드포인트 (100% 완료)

---

## 📋 Phase 2 개요

### 비즈니스 가치

사용자가 **Optuna 기반 백테스트 자동 최적화**로 최적 파라미터를 탐색하고,
**데이터 품질 센티널**을 통해 이상 데이터를 조기 감지하여 투자 전략의 신뢰도를
향상시킵니다.

### 주요 산출물

- ✅ **2개 신규 Custom Hooks**: useOptimization, useDataQuality
- ✅ **8개 UI 컴포넌트**: 최적화 4개, 데이터 품질 4개
- ✅ **5개 API 엔드포인트 연동**: 최적화 4개, 데이터 품질 1개
- ✅ **2개 신규 페이지**: `/backtests/optimize`, `/dashboard/data-quality`

### 성공 지표 (KPI)

**기술 메트릭**:

- API 엔드포인트 연동: **13/32** (Phase 1 + Phase 2 완료 시)
- Custom Hooks: **5/13**
- UI 컴포넌트: **20/60**

**성능 메트릭**:

- 최적화 진행률 폴링: **5초 간격**
- 데이터 품질 요약 조회: **< 2초**

**비즈니스 메트릭**:

- 자동 최적화 실행: **> 10건/월** (Phase 2 종료 시)

---

## 📅 Sprint 계획

### Sprint 3 (Week 3: 2025-10-29 ~ 2025-11-04)

#### Day 13-15 (2025-10-29 ~ 2025-10-31): useOptimization 훅 + 컴포넌트 4개

**목표**: 백테스트 자동 최적화 UI 구축

**작업 항목**:

**Day 13 (훅 구현 - Part 1)**:

- [ ] `useOptimization.ts` 파일 생성
- [ ] Query Key 정의:
  ```typescript
  export const optimizationQueryKeys = {
    all: ["optimization"] as const,
    studies: () => [...optimizationQueryKeys.all, "studies"] as const,
    study: (name: string) =>
      [...optimizationQueryKeys.all, "study", name] as const,
    progress: (name: string) =>
      [...optimizationQueryKeys.all, "progress", name] as const,
    result: (name: string) =>
      [...optimizationQueryKeys.all, "result", name] as const,
  };
  ```
- [ ] `useQuery` 구현:
  - [ ] studies (목록 조회)
  - [ ] studyDetail (상세 조회)
  - [ ] progress (진행률 조회 - 5초 폴링)
  - [ ] result (결과 조회)

**Day 14 (훅 구현 - Part 2)**:

- [ ] `useMutation` 구현:
  - [ ] startOptimization (최적화 시작)
- [ ] 폴링 로직 구현:
  ```typescript
  const progressQuery = useQuery({
    queryKey: optimizationQueryKeys.progress(studyName!),
    queryFn: async () =>
      (await OptimizationService.getProgress({ studyName: studyName! })).data,
    enabled: !!studyName && isOptimizing,
    refetchInterval: 5000, // 5초 간격
  });
  ```
- [ ] 폴링 중단 로직 (상태가 'completed' 또는 'failed'일 때)
- [ ] Unit Test 작성

**Day 15 (컴포넌트 4개)**:

- [ ] `OptimizationWizard.tsx`:
  - [ ] react-hook-form 통합
  - [ ] Step 1: 전략 선택
  - [ ] Step 2: 파라미터 범위 입력
  - [ ] Step 3: 최적화 설정 (trials, sampler)
  - [ ] 검증 로직
- [ ] `OptimizationProgress.tsx`:
  - [ ] 진행률 표시 (LinearProgress)
  - [ ] 현재 Trial 정보
  - [ ] 경과 시간
  - [ ] 중단 버튼
- [ ] `TrialHistoryChart.tsx`:
  - [ ] Recharts LineChart (Trial별 목표 함수 값)
  - [ ] Best Value 강조
- [ ] `BestParamsPanel.tsx`:
  - [ ] 최적 파라미터 테이블
  - [ ] 백테스트 실행 버튼 (최적 파라미터 적용)

**예상 소요 시간**: 20시간 (2.5일)  
**담당자**: Frontend 엔지니어  
**참고 문서**:
[AI_INTEGRATION_USER_STORIES.md - US-9](../AI_INTEGRATION_USER_STORIES.md#us-9)

---

#### Day 16-17 (2025-11-02 ~ 2025-11-03): useDataQuality 훅 + 컴포넌트 4개

**목표**: 데이터 품질 모니터링 대시보드 구축

**작업 항목**:

**Day 16 (훅 구현)**:

- [ ] `useDataQuality.ts` 파일 생성
- [ ] Query Key 정의
- [ ] `useQuery` 구현:
  - [ ] qualitySummary (데이터 품질 요약)
  - [ ] recentAlerts (최근 알림 목록)
  - [ ] severityStats (심각도 통계)
  - [ ] anomalyDetails (이상 징후 상세)
- [ ] 자동 새로고침 (refetchInterval: 60000 - 1분)
- [ ] Unit Test 작성

**Day 17 (컴포넌트 4개)**:

- [ ] `DataQualityDashboard.tsx`:
  - [ ] Material-UI Grid 레이아웃
  - [ ] 주요 지표 카드 (총 이벤트, 심각도별 카운트)
  - [ ] 최근 알림 타임라인
- [ ] `AlertTimeline.tsx`:
  - [ ] Timeline 컴포넌트 (MUI Timeline)
  - [ ] 심각도별 색상 (HIGH 🔴, MEDIUM 🟡, LOW 🟢)
  - [ ] 클릭 시 상세 모달
- [ ] `SeverityPieChart.tsx`:
  - [ ] Recharts PieChart
  - [ ] 심각도별 비율
  - [ ] 범례 (Legend)
- [ ] `AnomalyDetailTable.tsx`:
  - [ ] Material-UI DataGrid
  - [ ] 컬럼: 날짜, 심볼, 유형, 점수, 액션
  - [ ] 필터/정렬 기능

**예상 소요 시간**: 12시간 (1.5일 + 1일)  
**담당자**: Frontend 엔지니어  
**참고 문서**:
[AI_INTEGRATION_USER_STORIES.md - US-10](../AI_INTEGRATION_USER_STORIES.md#us-10)

---

#### Day 18 (2025-11-04): Phase 2 완료 및 리뷰

**목표**: Phase 2 산출물 검증, KPI 평가, Phase 3 착수 준비

**작업 항목**:

- [ ] **체크리스트 검증**:
  - [ ] 2개 신규 훅 완성 ✅
  - [ ] 8개 UI 컴포넌트 완성 ✅
  - [ ] 5개 API 엔드포인트 연동 ✅
  - [ ] TypeScript/ESLint 에러 0개 ✅
  - [ ] Unit Test 커버리지 75%+ ✅
- [ ] **KPI 평가**:
  - [ ] 최적화 진행률 폴링 5초 간격 ✅
  - [ ] 데이터 품질 요약 < 2초 ✅
- [ ] **Phase 2 리뷰 미팅** (오후 2시, 1시간):
  - [ ] 데모 (최적화 마법사, 데이터 품질 대시보드)
  - [ ] KPI 결과 공유
  - [ ] 피드백 수집
  - [ ] Phase 3 착수 승인
- [ ] **문서 업데이트**:
  - [ ] PROJECT_DASHBOARD.md (진행률 업데이트)
  - [ ] Phase 2 완료 리포트 작성

**예상 소요 시간**: 8시간 (1일)  
**담당자**: 전체 팀

---

## 🛠️ 기술 스택 (Phase 2)

### 필수 라이브러리

| 라이브러리      | 버전    | 용도                                  |
| --------------- | ------- | ------------------------------------- |
| react-hook-form | ^7.49.0 | 최적화 마법사 폼 관리                 |
| zustand         | ^4.4.0  | 최적화 폴링 상태 관리 (전역)          |
| recharts        | ^2.10.0 | Trial 히스토리 차트, 심각도 파이 차트 |
| date-fns        | ^3.0.0  | 알림 타임라인 날짜 포맷팅             |

### 설치 명령어

```bash
cd frontend
pnpm add react-hook-form zustand
# recharts, date-fns는 Phase 1에서 이미 설치됨
```

---

## 📊 Backend API 명세 (Phase 2)

### 최적화 API (4개)

| 메서드 | 엔드포인트                                       | 설명             | 응답 시간 목표 |
| ------ | ------------------------------------------------ | ---------------- | -------------- |
| POST   | `/api/v1/backtests/optimize/`                    | 최적화 시작      | 즉시 반환      |
| GET    | `/api/v1/backtests/optimize/{study_name}`        | 스터디 상세 조회 | < 1초          |
| GET    | `/api/v1/backtests/optimize/{study_name}/result` | 최적화 결과 조회 | < 1.5초        |
| GET    | `/api/v1/backtests/optimize/`                    | 스터디 목록 조회 | < 1초          |

### 데이터 품질 API (1개)

| 메서드 | 엔드포인트                               | 설명             | 응답 시간 목표 |
| ------ | ---------------------------------------- | ---------------- | -------------- |
| GET    | `/api/v1/dashboard/data-quality-summary` | 데이터 품질 요약 | < 2초          |

**총 5개 API 엔드포인트**

---

## 🎯 Custom Hooks 상세 명세

### 1. useOptimization

```typescript
export const useOptimization = (studyName?: string) => {
  const queryClient = useQueryClient();
  const { showSuccess, showError } = useSnackbar();
  const [isOptimizing, setIsOptimizing] = useState(false);

  // 스터디 목록
  const studiesQuery = useQuery({
    queryKey: optimizationQueryKeys.studies(),
    queryFn: async () => (await OptimizationService.getStudies()).data,
    staleTime: 1000 * 60 * 5,
  });

  // 스터디 상세
  const studyDetailQuery = useQuery({
    queryKey: optimizationQueryKeys.study(studyName!),
    queryFn: async () =>
      (await OptimizationService.getStudy({ studyName: studyName! })).data,
    enabled: !!studyName,
  });

  // 진행률 (5초 폴링)
  const progressQuery = useQuery({
    queryKey: optimizationQueryKeys.progress(studyName!),
    queryFn: async () =>
      (await OptimizationService.getProgress({ studyName: studyName! })).data,
    enabled: !!studyName && isOptimizing,
    refetchInterval: 5000,
  });

  // 폴링 중단 로직
  useEffect(() => {
    if (
      progressQuery.data?.status === "completed" ||
      progressQuery.data?.status === "failed"
    ) {
      setIsOptimizing(false);
      queryClient.invalidateQueries({
        queryKey: optimizationQueryKeys.result(studyName!),
      });
    }
  }, [progressQuery.data?.status]);

  // 최적화 결과
  const resultQuery = useQuery({
    queryKey: optimizationQueryKeys.result(studyName!),
    queryFn: async () =>
      (await OptimizationService.getResult({ studyName: studyName! })).data,
    enabled: !!studyName && !isOptimizing,
  });

  // 최적화 시작
  const startMutation = useMutation({
    mutationFn: (request: OptimizationRequest) =>
      OptimizationService.startOptimization({ body: request }),
    onSuccess: () => {
      setIsOptimizing(true);
      queryClient.invalidateQueries({
        queryKey: optimizationQueryKeys.studies(),
      });
      showSuccess("최적화가 시작되었습니다");
    },
    onError: () => showError("최적화 시작 실패"),
  });

  return {
    studies: studiesQuery.data ?? [],
    studyDetail: studyDetailQuery.data,
    progress: progressQuery.data,
    result: resultQuery.data,
    bestParams: resultQuery.data?.best_params,
    startOptimization: startMutation.mutate,
    isOptimizing,
    loading: studiesQuery.isLoading,
    error: studiesQuery.error,
  };
};
```

### 2. useDataQuality

```typescript
export const useDataQuality = () => {
  const qualitySummaryQuery = useQuery({
    queryKey: dataQualityQueryKeys.summary(),
    queryFn: async () => (await DashboardService.getDataQualitySummary()).data,
    staleTime: 1000 * 60 * 1, // 1분
    refetchInterval: 1000 * 60 * 1, // 1분 자동 새로고침
  });

  return {
    qualitySummary: qualitySummaryQuery.data,
    recentAlerts: qualitySummaryQuery.data?.recent_alerts ?? [],
    severityStats: qualitySummaryQuery.data?.severity_stats ?? {},
    anomalyDetails: qualitySummaryQuery.data?.anomaly_details ?? [],
    loading: qualitySummaryQuery.isLoading,
    error: qualitySummaryQuery.error,
  };
};
```

---

## 🧪 테스트 전략

### Unit Tests

**useOptimization.test.ts**:

- [ ] studies 조회 성공
- [ ] startOptimization 성공 → isOptimizing = true
- [ ] progress 폴링 (refetchInterval 검증)
- [ ] 폴링 중단 (status = 'completed')
- [ ] resultQuery 활성화 (isOptimizing = false)

**useDataQuality.test.ts**:

- [ ] qualitySummary 조회 성공
- [ ] 자동 새로고침 (refetchInterval 검증)
- [ ] recentAlerts 추출 성공

### E2E Tests (Playwright)

**optimization.spec.ts**:

```typescript
test("백테스트 최적화 전체 플로우", async ({ page }) => {
  await page.goto("/backtests/optimize");

  // Step 1: 전략 선택
  await page.click('[data-testid="strategy-select"]');
  await page.click('text="BB + Harvard RSI"');

  // Step 2: 파라미터 범위 입력
  await page.fill('[name="bb_window_min"]', "10");
  await page.fill('[name="bb_window_max"]', "30");

  // Step 3: 최적화 설정
  await page.fill('[name="n_trials"]', "50");
  await page.click('button:has-text("최적화 시작")');

  // 진행률 표시 확인
  await expect(
    page.locator('[data-testid="optimization-progress"]')
  ).toBeVisible();

  // 폴링 동작 확인 (최대 30초 대기)
  await page.waitForSelector('[data-testid="best-params-panel"]', {
    timeout: 30000,
  });
  await expect(page.locator('[data-testid="best-sharpe-ratio"]')).toBeVisible();
});
```

---

## 🚨 위험 및 대응

| 위험                             | 영향                   | 가능성 | 대응 전략                                                 |
| -------------------------------- | ---------------------- | ------ | --------------------------------------------------------- |
| 최적화 장시간 실행 (> 10분)      | 사용자 이탈, 폴링 과다 | 높음   | 진행률 표시, 백그라운드 작업 큐, 중단 버튼, 이메일 알림   |
| 폴링으로 인한 API 과부하         | 서버 부하 증가         | 중간   | 5초 간격 제한, 폴링 중단 로직, 최대 폴링 시간 설정 (10분) |
| react-hook-form 검증 복잡도      | 개발 시간 증가         | 낮음   | Yup 스키마 검증, Backend Pydantic 스키마 재사용           |
| 데이터 품질 대시보드 데이터 부족 | 빈 상태, 사용자 혼란   | 중간   | 샘플 데이터 표시, 온보딩 가이드, 데이터 수집 안내         |

---

## 📚 참고 문서

- **유저 스토리**:
  [AI_INTEGRATION_USER_STORIES.md](../AI_INTEGRATION_USER_STORIES.md) (US-9,
  US-10)
- **Master Plan**: [MASTER_PLAN.md](../MASTER_PLAN.md)
- **프로젝트 대시보드**: [PROJECT_DASHBOARD.md](../PROJECT_DASHBOARD.md)
- **Backend 최적화 서비스**:
  [PHASE2_D1_IMPLEMENTATION_REPORT.md](../../../backend/ai_integration/phase2_automation_and_optimization/PHASE2_D1_IMPLEMENTATION_REPORT.md)

---

**작성자**: Frontend Team  
**승인자**: 퀀트 플랫폼 프론트엔드 리드  
**최종 업데이트**: 2025-10-14  
**다음 리뷰**: Phase 2 완료 시 (2025-11-04)
