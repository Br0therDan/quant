# Phase 2 계획: 최적화 & 모니터링

**작성일**: 2025-10-14  
**작성자**: AI Agent  
**작업 범위**: Phase 2 - 백테스트 자동 최적화 & 데이터 품질 대시보드

---

## 📋 Phase 2 Overview

Phase 2에서는 백테스트 자동 최적화 시스템과 데이터 품질 모니터링 대시보드를
구축합니다.

### 목표

| 항목                 | 세부 목표                                |
| -------------------- | ---------------------------------------- |
| **Custom Hooks**     | useOptimization, useDataQuality (2개)    |
| **UI Components**    | 8개 (Optimization 4개 + DataQuality 4개) |
| **예상 코드 라인수** | 2,500+ lines                             |
| **예상 소요**        | 4-5일                                    |

---

## 🎯 Epic 1: 백테스트 자동 최적화 (useOptimization)

### Backend API 확인

OpenAPI 스펙 확인 필요:

- `POST /api/v1/optimization/start` - 최적화 시작
- `GET /api/v1/optimization/studies` - 스터디 목록 조회
- `GET /api/v1/optimization/studies/{study_id}` - 스터디 상세 조회
- `GET /api/v1/optimization/studies/{study_id}/trials` - 트라이얼 히스토리 조회
- `GET /api/v1/optimization/studies/{study_id}/best-params` - 최적 파라미터 조회

### useOptimization 훅 설계

```typescript
// frontend/src/hooks/useOptimization.ts

export const optimizationQueryKeys = {
  all: ["optimization"] as const,
  studies: () => [...optimizationQueryKeys.all, "studies"] as const,
  study: (id: string) => [...optimizationQueryKeys.studies(), id] as const,
  trials: (id: string) =>
    [...optimizationQueryKeys.study(id), "trials"] as const,
  bestParams: (id: string) =>
    [...optimizationQueryKeys.study(id), "bestParams"] as const,
  progress: (id: string) =>
    [...optimizationQueryKeys.study(id), "progress"] as const,
} as const;

export function useOptimization() {
  const queryClient = useQueryClient();
  const { showSuccess, showError } = useSnackbar();

  // 스터디 목록 조회
  const studiesQuery = useQuery({
    queryKey: optimizationQueryKeys.studies(),
    queryFn: async () => {
      const response = await OptimizationService.getStudies({
        query: { skip: 0, limit: 100 },
      });
      return response.data;
    },
    staleTime: 1000 * 60 * 5,
    gcTime: 30 * 60 * 1000,
  });

  // 최적화 시작 Mutation
  const startOptimizationMutation = useMutation({
    mutationFn: async (config: OptimizationConfig) => {
      const response = await OptimizationService.startOptimization({
        body: config,
      });
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({
        queryKey: optimizationQueryKeys.studies(),
      });
      showSuccess(`최적화 "${data.study_id}"가 시작되었습니다`);
    },
    onError: (error) => {
      showError(`최적화 시작 실패: ${error.message}`);
    },
  });

  return useMemo(
    () => ({
      studies: studiesQuery.data,
      isLoading: studiesQuery.isLoading,
      error: studiesQuery.error,
      startOptimization: startOptimizationMutation.mutate,
      startOptimizationAsync: startOptimizationMutation.mutateAsync,
      isOptimizing: startOptimizationMutation.isPending,
      refetch: studiesQuery.refetch,
    }),
    [studiesQuery, startOptimizationMutation]
  );
}

// 개별 스터디 상세 조회
export function useOptimizationStudy(
  studyId: string,
  options?: { pollInterval?: number }
) {
  const studyQuery = useQuery({
    queryKey: optimizationQueryKeys.study(studyId),
    queryFn: async () => {
      const response = await OptimizationService.getStudy({
        path: { study_id: studyId },
      });
      return response.data;
    },
    enabled: !!studyId,
    staleTime: 1000 * 5, // 5초 (진행 중 상태 추적)
    gcTime: 30 * 60 * 1000,
    refetchInterval: options?.pollInterval || 5000, // 5초마다 폴링
  });

  // 트라이얼 히스토리 조회
  const trialsQuery = useQuery({
    queryKey: optimizationQueryKeys.trials(studyId),
    queryFn: async () => {
      const response = await OptimizationService.getTrials({
        path: { study_id: studyId },
      });
      return response.data;
    },
    enabled: !!studyId && !!studyQuery.data,
    staleTime: 1000 * 30,
    gcTime: 30 * 60 * 1000,
  });

  // 최적 파라미터 조회
  const bestParamsQuery = useQuery({
    queryKey: optimizationQueryKeys.bestParams(studyId),
    queryFn: async () => {
      const response = await OptimizationService.getBestParams({
        path: { study_id: studyId },
      });
      return response.data;
    },
    enabled: !!studyId && studyQuery.data?.status === "completed",
    staleTime: 1000 * 60 * 5,
    gcTime: 30 * 60 * 1000,
  });

  // 진행률 계산
  const progress = useMemo(() => {
    if (!studyQuery.data) return 0;
    const { n_trials, n_trials_completed } = studyQuery.data;
    return (n_trials_completed / n_trials) * 100;
  }, [studyQuery.data]);

  return useMemo(
    () => ({
      study: studyQuery.data,
      trials: trialsQuery.data,
      bestParams: bestParamsQuery.data,
      progress,
      isLoading: studyQuery.isLoading,
      error: studyQuery.error,
      refetch: {
        study: studyQuery.refetch,
        trials: trialsQuery.refetch,
        bestParams: bestParamsQuery.refetch,
      },
    }),
    [studyQuery, trialsQuery, bestParamsQuery, progress]
  );
}
```

### UI Components (4개)

#### 1. OptimizationWizard.tsx (350 lines)

- **목적**: 최적화 설정 마법사
- **기능**:
  - 스텝 1: 전략 선택
  - 스텝 2: 파라미터 범위 설정 (min/max)
  - 스텝 3: 최적화 옵션 (n_trials, timeout)
  - 스텝 4: 확인 및 시작
- **사용 라이브러리**: react-hook-form, Material-UI Stepper

#### 2. OptimizationProgress.tsx (300 lines)

- **목적**: 실시간 최적화 진행 상황
- **기능**:
  - 진행률 표시 (Progress Bar)
  - 현재 트라이얼 정보
  - 예상 완료 시간
  - 중단 버튼
- **폴링**: 5초 간격 자동 갱신

#### 3. TrialHistoryChart.tsx (330 lines)

- **목적**: 트라이얼 히스토리 시각화
- **기능**:
  - X축: Trial Number
  - Y축: Objective Value (Sharpe Ratio)
  - Scatter Plot + Line Chart
  - 최적 트라이얼 하이라이트
- **사용 라이브러리**: Recharts

#### 4. BestParamsPanel.tsx (270 lines)

- **목적**: 최적 파라미터 패널
- **기능**:
  - 최적 파라미터 목록 (Table)
  - Objective Value 표시
  - 백테스트 재실행 버튼
  - 전략 저장 버튼
- **사용 라이브러리**: Material-UI Table, Chip

### 예상 코드 라인수

| 항목                     | Lines     |
| ------------------------ | --------- |
| useOptimization.ts       | 400       |
| OptimizationWizard.tsx   | 350       |
| OptimizationProgress.tsx | 300       |
| TrialHistoryChart.tsx    | 330       |
| BestParamsPanel.tsx      | 270       |
| **합계**                 | **1,650** |

---

## 🎯 Epic 2: 데이터 품질 대시보드 (useDataQuality)

### Backend API 확인

OpenAPI 스펙 확인 필요:

- `GET /api/v1/data-quality/summary` - 품질 요약
- `GET /api/v1/data-quality/alerts` - 알림 목록
- `GET /api/v1/data-quality/alerts/{alert_id}` - 알림 상세
- `GET /api/v1/data-quality/anomalies` - 이상 탐지 결과
- `GET /api/v1/data-quality/metrics/{symbol}` - 심볼별 메트릭

### useDataQuality 훅 설계

```typescript
// frontend/src/hooks/useDataQuality.ts

export const dataQualityQueryKeys = {
  all: ["dataQuality"] as const,
  summary: () => [...dataQualityQueryKeys.all, "summary"] as const,
  alerts: () => [...dataQualityQueryKeys.all, "alerts"] as const,
  alert: (id: string) => [...dataQualityQueryKeys.alerts(), id] as const,
  anomalies: () => [...dataQualityQueryKeys.all, "anomalies"] as const,
  metrics: (symbol: string) =>
    [...dataQualityQueryKeys.all, "metrics", symbol] as const,
} as const;

export function useDataQuality() {
  const queryClient = useQueryClient();

  // 품질 요약 조회
  const summaryQuery = useQuery({
    queryKey: dataQualityQueryKeys.summary(),
    queryFn: async () => {
      const response = await DataQualityService.getSummary();
      return response.data;
    },
    staleTime: 1000 * 60 * 5,
    gcTime: 30 * 60 * 1000,
  });

  // 알림 목록 조회
  const alertsQuery = useQuery({
    queryKey: dataQualityQueryKeys.alerts(),
    queryFn: async () => {
      const response = await DataQualityService.getAlerts({
        query: { skip: 0, limit: 100 },
      });
      return response.data;
    },
    staleTime: 1000 * 30, // 30초 (알림은 빠르게 갱신)
    gcTime: 10 * 60 * 1000,
  });

  // 이상 탐지 결과 조회
  const anomaliesQuery = useQuery({
    queryKey: dataQualityQueryKeys.anomalies(),
    queryFn: async () => {
      const response = await DataQualityService.getAnomalies({
        query: { skip: 0, limit: 50 },
      });
      return response.data;
    },
    staleTime: 1000 * 60 * 5,
    gcTime: 30 * 60 * 1000,
  });

  // 심각도별 통계 계산
  const severityStats = useMemo(() => {
    if (!alertsQuery.data?.alerts) return null;

    const stats = { critical: 0, high: 0, medium: 0, low: 0 };
    for (const alert of alertsQuery.data.alerts) {
      stats[alert.severity]++;
    }
    return stats;
  }, [alertsQuery.data]);

  return useMemo(
    () => ({
      qualitySummary: summaryQuery.data,
      recentAlerts: alertsQuery.data,
      anomalyDetails: anomaliesQuery.data,
      severityStats,
      isLoading: {
        summary: summaryQuery.isLoading,
        alerts: alertsQuery.isLoading,
        anomalies: anomaliesQuery.isLoading,
      },
      error: summaryQuery.error || alertsQuery.error || anomaliesQuery.error,
      refetch: {
        summary: summaryQuery.refetch,
        alerts: alertsQuery.refetch,
        anomalies: anomaliesQuery.refetch,
      },
    }),
    [summaryQuery, alertsQuery, anomaliesQuery, severityStats]
  );
}

// 개별 심볼 메트릭 조회
export function useDataQualityMetrics(symbol: string) {
  return useQuery({
    queryKey: dataQualityQueryKeys.metrics(symbol),
    queryFn: async () => {
      const response = await DataQualityService.getMetrics({
        path: { symbol },
      });
      return response.data;
    },
    enabled: !!symbol,
    staleTime: 1000 * 60 * 5,
    gcTime: 30 * 60 * 1000,
  });
}
```

### UI Components (4개)

#### 1. DataQualityDashboard.tsx (360 lines)

- **목적**: 데이터 품질 대시보드 메인 화면
- **기능**:
  - 품질 점수 표시 (0-100)
  - 심각도별 알림 개수 (Card Grid)
  - 최근 이상 탐지 목록
  - 심볼별 품질 메트릭 테이블
- **사용 라이브러리**: Material-UI Grid, Card, Chip

#### 2. AlertTimeline.tsx (320 lines)

- **목적**: 알림 타임라인
- **기능**:
  - 시간순 알림 표시 (Timeline)
  - 심각도별 색상 구분
  - 알림 상세 정보 (Collapse)
  - 필터링 (심각도, 날짜)
- **사용 라이브러리**: Material-UI Timeline, date-fns

#### 3. SeverityPieChart.tsx (260 lines)

- **목적**: 심각도 분포 파이 차트
- **기능**:
  - 심각도별 알림 개수 (Pie Chart)
  - 퍼센티지 표시
  - 클릭 시 필터링
- **사용 라이브러리**: Recharts PieChart

#### 4. AnomalyDetailTable.tsx (310 lines)

- **목적**: 이상 탐지 상세 테이블
- **기능**:
  - 이상 탐지 결과 목록 (Table)
  - 정렬 (심각도, 날짜, 심볼)
  - 페이지네이션
  - CSV 다운로드
- **사용 라이브러리**: Material-UI Table, TablePagination

### 예상 코드 라인수

| 항목                     | Lines     |
| ------------------------ | --------- |
| useDataQuality.ts        | 350       |
| DataQualityDashboard.tsx | 360       |
| AlertTimeline.tsx        | 320       |
| SeverityPieChart.tsx     | 260       |
| AnomalyDetailTable.tsx   | 310       |
| **합계**                 | **1,600** |

---

## 📅 Phase 2 타임라인

### Week 1 (Day 1-3): 최적화 시스템

| Day | 작업                                      | 산출물    | 예상 소요 |
| --- | ----------------------------------------- | --------- | --------- |
| 1   | Backend API 확인 + useOptimization 훅     | 400 lines | 6시간     |
| 2   | OptimizationWizard + OptimizationProgress | 650 lines | 8시간     |
| 3   | TrialHistoryChart + BestParamsPanel       | 600 lines | 8시간     |

### Week 2 (Day 4-5): 데이터 품질 대시보드

| Day | 작업                                  | 산출물    | 예상 소요 |
| --- | ------------------------------------- | --------- | --------- |
| 4   | Backend API 확인 + useDataQuality 훅  | 350 lines | 5시간     |
| 4   | DataQualityDashboard + AlertTimeline  | 680 lines | 8시간     |
| 5   | SeverityPieChart + AnomalyDetailTable | 570 lines | 7시간     |

### 총 예상 소요: 42시간 (5일)

---

## 🎯 Phase 2 완료 기준

| 항목                | 완료 기준                                        |
| ------------------- | ------------------------------------------------ |
| **Custom Hooks**    | useOptimization, useDataQuality 완성 (750 lines) |
| **UI Components**   | 8개 컴포넌트 완성 (2,500+ lines)                 |
| **TypeScript 에러** | 0개                                              |
| **Backend 연동**    | 10+ API 엔드포인트 검증                          |
| **성능 KPI**        | 최적화 진행률 폴링 < 100ms, 대시보드 로딩 < 1초  |
| **문서화**          | PHASE2_COMPLETION_REPORT.md 작성                 |

---

## 🚀 Phase 2 시작 준비

### 1. Backend API 확인 (즉시)

```bash
# OpenAPI 스펙 확인
open http://localhost:8500/docs

# 필요한 엔드포인트 확인
- /api/v1/optimization/*
- /api/v1/data-quality/*
```

### 2. 라이브러리 설치 (필요 시)

```bash
cd frontend

# 이미 설치됨 (Phase 1에서)
# recharts, react-hook-form, date-fns, lodash
```

### 3. OpenAPI 클라이언트 재생성 (필요 시)

```bash
pnpm gen:client
```

### 4. Phase 2 작업 시작

```bash
# useOptimization 훅 생성
touch frontend/src/hooks/useOptimization.ts

# useDataQuality 훅 생성
touch frontend/src/hooks/useDataQuality.ts

# 컴포넌트 디렉토리 생성
mkdir -p frontend/src/components/optimization
mkdir -p frontend/src/components/data-quality
```

---

## 📊 Phase 2 진행률 추적

| Epic                     | 진행률 | 상태    |
| ------------------------ | ------ | ------- |
| **최적화 시스템**        | 0%     | ⏸️ 대기 |
| **데이터 품질 대시보드** | 0%     | ⏸️ 대기 |

---

## 🎉 Phase 2 진입 준비 완료

**Phase 1 완료 상태**:

- ✅ ML 모델 관리 (1,590 lines)
- ✅ 시장 국면 감지 (1,600 lines)
- ✅ 포트폴리오 예측 (1,350 lines)
- ✅ 기존 훅 통합 (150 lines)
- ✅ **총 4,690 lines 코드 작성**

**Phase 2 목표**:

- 🎯 최적화 시스템 (1,650 lines)
- 🎯 데이터 품질 대시보드 (1,600 lines)
- 🎯 **총 3,250 lines 추가 예상**

**다음 단계**: Backend API 확인 후 useOptimization 훅 개발 시작

---

**작성 완료일**: 2025-10-14  
**Phase 2 시작 예정일**: 2025-10-15  
**Phase 2 완료 예정일**: 2025-10-19
