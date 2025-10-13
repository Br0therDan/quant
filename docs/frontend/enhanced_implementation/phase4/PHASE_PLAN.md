# Phase 4: MLOps 플랫폼 구현 계획

> **기간**: 2025-11-20 ~ 2025-12-02 (2주)  
> **우선순위**: 🟢 장기  
> **목표**: 피처 스토어 + 모델 라이프사이클 + 평가 하니스 + 프롬프트 거버넌스  
> **Backend API**: 12개 엔드포인트 (100% 완료)

---

## 📋 Phase 4 개요

### 비즈니스 가치

사용자가 **피처 스토어**로 ML 피처 버전을 관리하고, **모델 라이프사이클** 도구로
실험 추적 및 배포를 자동화하며, **평가 하니스**로 모델 성능을 벤치마크하고,
**프롬프트 거버넌스**로 LLM 프롬프트를 버전 관리할 수 있습니다.

### 주요 산출물

- ✅ **4개 신규 Custom Hooks**: useFeatureStore, useModelLifecycle,
  useEvaluationHarness, usePromptGovernance
- ✅ **16개 UI 컴포넌트**: 각 기능별 4개씩
- ✅ **12개 API 엔드포인트 연동**: 피처 스토어 2개, 모델 라이프사이클 4개, 평가
  3개, 프롬프트 4개
- ✅ **4개 신규 페이지**: `/features`, `/ml/lifecycle`, `/ml/evaluation`,
  `/prompts`

### 성공 지표 (KPI)

**기술 메트릭**:

- API 엔드포인트 연동: **32/32** (Phase 4 완료 시, 100% 달성) 🎉
- Custom Hooks: **13/13** (100% 달성) 🎉
- UI 컴포넌트: **60/60** (100% 달성) 🎉

**성능 메트릭**:

- 피처 조회: **< 1초**
- 모델 실험 조회: **< 2초**
- 평가 실행: **< 5초**
- 프롬프트 저장: **< 1초**

**비즈니스 메트릭**:

- 피처 스토어 활용: **> 10건/월**
- 모델 실험 추적: **> 15건/월**

---

## 📅 Sprint 계획

### Sprint 6 (Week 6: 2025-11-20 ~ 2025-11-26)

#### Day 27-28 (2025-11-20 ~ 2025-11-21): useFeatureStore 훅 + 컴포넌트 4개

**목표**: 피처 스토어 탐색 UI 구축

**작업 항목**:

**Day 27 (훅 구현)**:

- [ ] `useFeatureStore.ts` 파일 생성
- [ ] Query Key 정의:
  ```typescript
  export const featureStoreQueryKeys = {
    all: ["feature-store"] as const,
    features: () => [...featureStoreQueryKeys.all, "features"] as const,
    feature: (name: string) =>
      [...featureStoreQueryKeys.all, "feature", name] as const,
    versions: (name: string) =>
      [...featureStoreQueryKeys.all, "versions", name] as const,
    datasets: () => [...featureStoreQueryKeys.all, "datasets"] as const,
  };
  ```
- [ ] `useQuery` 구현:
  - [ ] features (피처 목록)
  - [ ] featureDetail (피처 상세)
  - [ ] versions (버전 히스토리)
  - [ ] datasets (데이터셋 목록)
- [ ] Unit Test 작성

**Day 28 (컴포넌트 4개)**:

- [ ] `FeatureList.tsx`:
  - [ ] 피처 카드 그리드 (이름, 타입, 최신 버전)
  - [ ] 필터 (타입별, 날짜별)
  - [ ] 검색 기능
- [ ] `FeatureDetail.tsx`:
  - [ ] 피처 메타데이터 (이름, 설명, 타입)
  - [ ] 통계 (최소, 최대, 평균, 표준편차)
  - [ ] 샘플 데이터 테이블
- [ ] `VersionHistory.tsx`:
  - [ ] Timeline 컴포넌트 (버전별)
  - [ ] 변경 사항 (Diff)
  - [ ] 롤백 버튼
- [ ] `DatasetExplorer.tsx`:
  - [ ] 데이터셋 목록
  - [ ] 피처 포함 여부 (체크박스)
  - [ ] 다운로드 버튼

**예상 소요 시간**: 16시간 (2일)  
**담당자**: Frontend 엔지니어  
**참고 문서**:
[AI_INTEGRATION_USER_STORIES.md - US-16](../AI_INTEGRATION_USER_STORIES.md#us-16)

---

#### Day 29-31 (2025-11-22 ~ 2025-11-24): useModelLifecycle 훅 + 컴포넌트 4개

**목표**: 모델 라이프사이클 관리 UI 구축

**작업 항목**:

**Day 29 (훅 구현)**:

- [ ] `useModelLifecycle.ts` 파일 생성
- [ ] Query Key 정의
- [ ] `useQuery` 구현:
  - [ ] experiments (실험 목록)
  - [ ] experimentDetail (실험 상세)
  - [ ] models (모델 레지스트리)
  - [ ] deployments (배포 목록)
  - [ ] metrics (메트릭 조회)
- [ ] `useMutation` 구현:
  - [ ] createExperiment (실험 생성)
  - [ ] registerModel (모델 등록)
  - [ ] deployModel (모델 배포)
- [ ] Unit Test 작성

**Day 30-31 (컴포넌트 4개)**:

- [ ] `ExperimentList.tsx`:
  - [ ] 실험 테이블 (이름, 상태, 메트릭)
  - [ ] 정렬/필터 (상태별, 날짜별)
  - [ ] 실험 생성 버튼
- [ ] `ModelRegistry.tsx`:
  - [ ] 모델 카드 그리드 (이름, 버전, 정확도)
  - [ ] 배포 상태 (Chip: Production, Staging, Archived)
  - [ ] 배포 버튼
- [ ] `DeploymentPipeline.tsx`:
  - [ ] 배포 워크플로우 (Stepper)
  - [ ] 단계: 검증 → 스테이징 → 프로덕션
  - [ ] 진행 상태 표시
- [ ] `MetricsTracker.tsx`:
  - [ ] Recharts LineChart (메트릭 시계열)
  - [ ] 실험별 비교 (멀티 라인)
  - [ ] 범례 (Legend)

**예상 소요 시간**: 20시간 (2.5일)  
**담당자**: Frontend 엔지니어  
**참고 문서**:
[AI_INTEGRATION_USER_STORIES.md - US-17](../AI_INTEGRATION_USER_STORIES.md#us-17)

---

### Sprint 7 (Week 7: 2025-11-27 ~ 2025-12-02)

#### Day 32-33 (2025-11-27 ~ 2025-11-28): useEvaluationHarness 훅 + 컴포넌트 4개

**목표**: 모델 평가 하니스 UI 구축

**작업 항목**:

**Day 32 (훅 구현)**:

- [ ] `useEvaluationHarness.ts` 파일 생성
- [ ] Query Key 정의
- [ ] `useQuery` 구현:
  - [ ] benchmarks (벤치마크 스위트 목록)
  - [ ] evaluationResults (평가 결과)
  - [ ] comparisons (모델 비교)
  - [ ] explainability (설명 가능성 리포트)
- [ ] `useMutation` 구현:
  - [ ] runEvaluation (평가 실행)
- [ ] Unit Test 작성

**Day 33 (컴포넌트 4개)**:

- [ ] `BenchmarkSuite.tsx`:
  - [ ] 벤치마크 목록 (이름, 설명, 테스트 수)
  - [ ] 선택 체크박스
  - [ ] 실행 버튼
- [ ] `EvaluationResults.tsx`:
  - [ ] 결과 테이블 (메트릭별 컬럼)
  - [ ] 통과/실패 상태 (✅ Pass, ❌ Fail)
  - [ ] 상세 보기 버튼
- [ ] `ModelComparison.tsx`:
  - [ ] Recharts BarChart (모델별 메트릭 비교)
  - [ ] 최고 성능 하이라이트
  - [ ] 차이 퍼센트 표시
- [ ] `ExplainabilityReport.tsx`:
  - [ ] SHAP 값 시각화 (D3.js)
  - [ ] Feature Importance 막대 차트
  - [ ] 설명 텍스트 (Markdown)

**예상 소요 시간**: 12시간 (1.5일 + 1일)  
**담당자**: Frontend 엔지니어  
**참고 문서**:
[AI_INTEGRATION_USER_STORIES.md - US-18](../AI_INTEGRATION_USER_STORIES.md#us-18)

---

#### Day 34 (2025-11-29): usePromptGovernance 훅 + 컴포넌트 4개

**목표**: 프롬프트 템플릿 관리 UI 구축

**작업 항목**:

**Day 34 (훅 + 컴포넌트)**:

- [ ] `usePromptGovernance.ts` 파일 생성
- [ ] Query Key 정의
- [ ] `useQuery` 구현:
  - [ ] templates (템플릿 목록)
  - [ ] templateDetail (템플릿 상세)
  - [ ] versions (버전 히스토리)
  - [ ] usage (사용 통계)
- [ ] `useMutation` 구현:
  - [ ] createTemplate (템플릿 생성)
  - [ ] updateTemplate (템플릿 업데이트)
  - [ ] publishTemplate (템플릿 배포)
- [ ] Unit Test 작성
- [ ] `TemplateList.tsx`: 템플릿 카드 그리드 (이름, 버전, 상태)
- [ ] `TemplateEditor.tsx`: Monaco Editor 통합 (Jinja2 하이라이팅)
- [ ] `VersionControl.tsx`: Git-style 버전 히스토리
- [ ] `UsageAnalytics.tsx`: Recharts 사용 통계 (호출 수, 성공률)

**예상 소요 시간**: 8시간 (1일)  
**담당자**: Frontend 엔지니어  
**참고 문서**:
[AI_INTEGRATION_USER_STORIES.md - US-19](../AI_INTEGRATION_USER_STORIES.md#us-19)

---

#### Day 35-36 (2025-11-30 ~ 2025-12-02): Phase 4 통합 테스트 및 프로그램 완료 리뷰

**목표**: Phase 4 산출물 검증, 전체 프로그램 KPI 평가, 배포 준비

**작업 항목**:

**Day 35 (통합 테스트)**:

- [ ] E2E 테스트 (Playwright):
  - [ ] 피처 스토어 조회 (< 1초)
  - [ ] 모델 실험 생성 및 배포
  - [ ] 평가 실행 (< 5초)
  - [ ] 프롬프트 템플릿 편집 및 배포
- [ ] 성능 프로파일링:
  - [ ] 모든 페이지 FCP < 1.5초
  - [ ] API 응답 시간 검증
- [ ] 회귀 테스트:
  - [ ] Phase 1-3 기능 재검증

**Day 36 (프로그램 완료 리뷰)**:

- [ ] **전체 체크리스트 검증**:
  - [ ] 32/32 API 엔드포인트 연동 ✅ 🎉
  - [ ] 13/13 Custom Hooks 완성 ✅ 🎉
  - [ ] 60+ UI 컴포넌트 완성 ✅ 🎉
  - [ ] TypeScript/ESLint 에러 0개 ✅
  - [ ] Unit Test 커버리지 80%+ ✅
  - [ ] E2E 테스트 커버리지 80%+ ✅
- [ ] **최종 KPI 평가**:
  - [ ] 기술 KPI 100% 달성 ✅
  - [ ] 성능 KPI 100% 달성 ✅
  - [ ] 비즈니스 KPI 100% 달성 ✅
- [ ] **프로그램 완료 리뷰 미팅** (오후 2시, 2시간):
  - [ ] 전체 데모 (Phase 1-4)
  - [ ] KPI 결과 공유 (슬라이드)
  - [ ] 피드백 수집
  - [ ] 배포 승인
- [ ] **문서 업데이트**:
  - [ ] PROJECT_DASHBOARD.md (100% 완료)
  - [ ] 프로그램 완료 리포트 작성
  - [ ] 사용자 가이드 작성
  - [ ] API 문서 업데이트

**예상 소요 시간**: 16시간 (2일)  
**담당자**: 전체 팀

---

## 🛠️ 기술 스택 (Phase 4)

### 필수 라이브러리

| 라이브러리           | 버전    | 용도                            |
| -------------------- | ------- | ------------------------------- |
| recharts             | ^2.10.0 | 메트릭 트래커, 사용 통계 차트   |
| d3                   | ^7.9.0  | SHAP 값 시각화, 네트워크 그래프 |
| @monaco-editor/react | ^4.6.0  | 프롬프트 템플릿 에디터          |
| date-fns             | ^3.0.0  | 버전 히스토리 날짜 포맷팅       |

**모든 라이브러리 Phase 1-3에서 이미 설치됨** ✅

---

## 📊 Backend API 명세 (Phase 4)

### 피처 스토어 API (2개)

| 메서드 | 엔드포인트                | 설명           | 응답 시간 목표 |
| ------ | ------------------------- | -------------- | -------------- |
| GET    | `/api/v1/features`        | 피처 목록 조회 | < 1초          |
| GET    | `/api/v1/features/{name}` | 피처 상세 조회 | < 1초          |

### 모델 라이프사이클 API (4개)

| 메서드 | 엔드포인트                      | 설명                 | 응답 시간 목표 |
| ------ | ------------------------------- | -------------------- | -------------- |
| GET    | `/api/v1/ml/experiments`        | 실험 목록 조회       | < 2초          |
| POST   | `/api/v1/ml/experiments`        | 실험 생성            | < 1초          |
| GET    | `/api/v1/ml/models`             | 모델 레지스트리 조회 | < 1.5초        |
| POST   | `/api/v1/ml/models/{id}/deploy` | 모델 배포            | < 3초          |

### 평가 하니스 API (3개)

| 메서드 | 엔드포인트                        | 설명           | 응답 시간 목표 |
| ------ | --------------------------------- | -------------- | -------------- |
| GET    | `/api/v1/evaluation/benchmarks`   | 벤치마크 목록  | < 1초          |
| POST   | `/api/v1/evaluation/run`          | 평가 실행      | < 5초          |
| GET    | `/api/v1/evaluation/results/{id}` | 평가 결과 조회 | < 1.5초        |

### 프롬프트 거버넌스 API (4개)

| 메서드 | 엔드포인트                                       | 설명            | 응답 시간 목표 |
| ------ | ------------------------------------------------ | --------------- | -------------- |
| GET    | `/api/v1/prompt-governance/templates`            | 템플릿 목록     | < 1초          |
| POST   | `/api/v1/prompt-governance/templates`            | 템플릿 생성     | < 1초          |
| PUT    | `/api/v1/prompt-governance/templates/{id}`       | 템플릿 업데이트 | < 1초          |
| GET    | `/api/v1/prompt-governance/templates/{id}/usage` | 사용 통계       | < 1.5초        |

**총 12개 API 엔드포인트** (Phase 4 누적: 32개, 100% 완료) 🎉

---

## 🎯 Custom Hooks 상세 명세

### 1. useFeatureStore

```typescript
export const useFeatureStore = (featureName?: string) => {
  const queryClient = useQueryClient();

  const featuresQuery = useQuery({
    queryKey: featureStoreQueryKeys.features(),
    queryFn: async () => (await FeatureStoreService.getFeatures()).data,
    staleTime: 1000 * 60 * 5,
  });

  const featureDetailQuery = useQuery({
    queryKey: featureStoreQueryKeys.feature(featureName!),
    queryFn: async () =>
      (await FeatureStoreService.getFeature({ name: featureName! })).data,
    enabled: !!featureName,
  });

  const versionsQuery = useQuery({
    queryKey: featureStoreQueryKeys.versions(featureName!),
    queryFn: async () =>
      (await FeatureStoreService.getVersions({ name: featureName! })).data,
    enabled: !!featureName,
  });

  const datasetsQuery = useQuery({
    queryKey: featureStoreQueryKeys.datasets(),
    queryFn: async () => (await FeatureStoreService.getDatasets()).data,
  });

  return {
    features: featuresQuery.data ?? [],
    featureDetail: featureDetailQuery.data,
    versions: versionsQuery.data ?? [],
    datasets: datasetsQuery.data ?? [],
    loading: featuresQuery.isLoading,
    error: featuresQuery.error,
  };
};
```

### 2. useModelLifecycle

```typescript
export const useModelLifecycle = () => {
  const queryClient = useQueryClient();
  const { showSuccess, showError } = useSnackbar();

  const experimentsQuery = useQuery({
    queryKey: modelLifecycleQueryKeys.experiments(),
    queryFn: async () => (await MLLifecycleService.getExperiments()).data,
    staleTime: 1000 * 60 * 5,
  });

  const modelsQuery = useQuery({
    queryKey: modelLifecycleQueryKeys.models(),
    queryFn: async () => (await MLLifecycleService.getModels()).data,
  });

  const createExperimentMutation = useMutation({
    mutationFn: (config: ExperimentConfig) =>
      MLLifecycleService.createExperiment({ body: config }),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: modelLifecycleQueryKeys.experiments(),
      });
      showSuccess("실험이 생성되었습니다");
    },
  });

  const deployModelMutation = useMutation({
    mutationFn: ({ id, environment }: { id: string; environment: string }) =>
      MLLifecycleService.deployModel({ id, body: { environment } }),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: modelLifecycleQueryKeys.models(),
      });
      showSuccess("모델이 배포되었습니다");
    },
  });

  return {
    experiments: experimentsQuery.data ?? [],
    models: modelsQuery.data ?? [],
    createExperiment: createExperimentMutation.mutate,
    deployModel: deployModelMutation.mutate,
    loading: experimentsQuery.isLoading,
  };
};
```

### 3. useEvaluationHarness

```typescript
export const useEvaluationHarness = () => {
  const { showSuccess, showError } = useSnackbar();

  const benchmarksQuery = useQuery({
    queryKey: evaluationQueryKeys.benchmarks(),
    queryFn: async () => (await EvaluationService.getBenchmarks()).data,
  });

  const runEvaluationMutation = useMutation({
    mutationFn: (config: EvaluationConfig) =>
      EvaluationService.runEvaluation({ body: config }),
    onSuccess: (response) => {
      showSuccess(`평가 완료: ${response.data.id}`);
    },
    onError: () => showError("평가 실행 실패"),
  });

  const resultsQuery = useQuery({
    queryKey: evaluationQueryKeys.results(),
    queryFn: async () => (await EvaluationService.getResults()).data,
  });

  return {
    benchmarks: benchmarksQuery.data ?? [],
    results: resultsQuery.data ?? [],
    runEvaluation: runEvaluationMutation.mutate,
    isEvaluating: runEvaluationMutation.isPending,
  };
};
```

### 4. usePromptGovernance

```typescript
export const usePromptGovernance = (templateId?: string) => {
  const queryClient = useQueryClient();
  const { showSuccess, showError } = useSnackbar();

  const templatesQuery = useQuery({
    queryKey: promptGovernanceQueryKeys.templates(),
    queryFn: async () => (await PromptGovernanceService.getTemplates()).data,
  });

  const templateDetailQuery = useQuery({
    queryKey: promptGovernanceQueryKeys.template(templateId!),
    queryFn: async () =>
      (await PromptGovernanceService.getTemplate({ id: templateId! })).data,
    enabled: !!templateId,
  });

  const createTemplateMutation = useMutation({
    mutationFn: (template: PromptTemplate) =>
      PromptGovernanceService.createTemplate({ body: template }),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: promptGovernanceQueryKeys.templates(),
      });
      showSuccess("템플릿이 생성되었습니다");
    },
  });

  const updateTemplateMutation = useMutation({
    mutationFn: ({ id, template }: { id: string; template: PromptTemplate }) =>
      PromptGovernanceService.updateTemplate({ id, body: template }),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: promptGovernanceQueryKeys.templates(),
      });
      showSuccess("템플릿이 업데이트되었습니다");
    },
  });

  return {
    templates: templatesQuery.data ?? [],
    templateDetail: templateDetailQuery.data,
    createTemplate: createTemplateMutation.mutate,
    updateTemplate: updateTemplateMutation.mutate,
    loading: templatesQuery.isLoading,
  };
};
```

---

## 🧪 테스트 전략

### Unit Tests

**useFeatureStore.test.ts**:

- [ ] features 조회 성공
- [ ] featureDetail 조회 성공 (featureName 제공 시)
- [ ] versions 조회 성공
- [ ] datasets 조회 성공

**useModelLifecycle.test.ts**:

- [ ] experiments 조회 성공
- [ ] createExperiment 성공 → invalidateQueries
- [ ] deployModel 성공 → showSuccess 호출

### E2E Tests (Playwright)

**mlops-platform.spec.ts**:

```typescript
test("MLOps 플랫폼 전체 플로우", async ({ page }) => {
  // 피처 스토어
  await page.goto("/features");
  await expect(
    page.locator('[data-testid="feature-card"]').first()
  ).toBeVisible();

  // 모델 라이프사이클
  await page.goto("/ml/lifecycle");
  await page.click('button:has-text("실험 생성")');
  await page.fill('[name="experiment_name"]', "Test Experiment");
  await page.click('button:has-text("생성")');
  await expect(page.locator('text="실험이 생성되었습니다"')).toBeVisible();

  // 평가 하니스
  await page.goto("/ml/evaluation");
  await page.click('[data-testid="benchmark-suite"]');
  await page.click('button:has-text("평가 실행")');
  await page.waitForSelector('[data-testid="evaluation-results"]', {
    timeout: 5000,
  });

  // 프롬프트 거버넌스
  await page.goto("/prompts");
  await page.click('button:has-text("템플릿 생성")');
  await page.fill('[name="template_name"]', "Test Template");
  await page.click('button:has-text("저장")');
  await expect(page.locator('text="템플릿이 생성되었습니다"')).toBeVisible();
});
```

---

## 🚨 위험 및 대응

| 위험                    | 영향                 | 가능성 | 대응 전략                                             |
| ----------------------- | -------------------- | ------ | ----------------------------------------------------- |
| Monaco Editor 성능 저하 | 프롬프트 편집 지연   | 낮음   | 코드 스플리팅, lazy loading, 가상화                   |
| D3.js 시각화 복잡도     | 개발 시간 증가       | 중간   | 기존 예제 활용, 라이브러리 래퍼 (visx) 고려           |
| Backend API 데이터 부족 | 빈 상태, 사용자 혼란 | 높음   | 샘플 데이터 제공, 온보딩 가이드, 데이터 시딩 스크립트 |
| 피처 스토어 복잡한 UI   | 사용자 학습 곡선     | 중간   | 튜토리얼 추가, 툴팁, 도움말 센터                      |

---

## 🎉 프로그램 완료 기준

### Phase 4 완료 기준

- [ ] 4개 신규 훅 완성 ✅
- [ ] 16개 UI 컴포넌트 완성 ✅
- [ ] 12개 API 엔드포인트 연동 ✅
- [ ] TypeScript/ESLint 에러 0개 ✅
- [ ] Unit Test 커버리지 80%+ ✅

### 전체 프로그램 완료 기준

- [ ] **32/32 API 엔드포인트 연동** ✅ 🎉
- [ ] **13/13 Custom Hooks** ✅ 🎉
- [ ] **60+ UI 컴포넌트** ✅ 🎉
- [ ] **E2E 테스트 커버리지 80%+** ✅
- [ ] **성능 KPI 달성** (ML < 1초, 예측 < 3초, 최적화 폴링 5초, 리포트 < 10초)
      ✅
- [ ] **비즈니스 KPI 달성** (백테스트 > 50건/월, 최적화 > 20건/월, 리포트 >
      30건/월, 전략 빌더 > 40건/월) ✅
- [ ] **문서화 100%** (Storybook, 사용자 가이드, API 문서) ✅
- [ ] **배포 준비 완료** (Production 배포, 모니터링 설정) ✅

---

## 📚 참고 문서

- **유저 스토리**:
  [AI_INTEGRATION_USER_STORIES.md](../AI_INTEGRATION_USER_STORIES.md) (US-16,
  US-17, US-18, US-19)
- **Master Plan**: [MASTER_PLAN.md](../MASTER_PLAN.md)
- **프로젝트 대시보드**: [PROJECT_DASHBOARD.md](../PROJECT_DASHBOARD.md)
- **Backend MLOps 서비스**:
  [PHASE4_D1_IMPLEMENTATION_REPORT.md](../../../backend/ai_integration/PHASE4_D1_IMPLEMENTATION_REPORT.md)

---

**작성자**: Frontend Team  
**승인자**: 퀀트 플랫폼 프론트엔드 리드  
**최종 업데이트**: 2025-10-14  
**다음 리뷰**: Phase 4 완료 시 (2025-12-02)  
**프로그램 완료 예정일**: 2025-12-15 🎉
