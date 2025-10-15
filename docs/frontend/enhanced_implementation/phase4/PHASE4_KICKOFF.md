# Phase 4: MLOps Platform - Kickoff Plan

**시작일**: 2025-10-15  
**목표 완료일**: 2025-12-02  
**현재 상태**: 🚀 진행 중

---

## 개요

Phase 4는 **MLOps 플랫폼** 구축을 목표로 하며, 머신러닝 모델의 전체
라이프사이클을 관리하는 4개의 핵심 시스템을 개발합니다:

1. **Feature Store**: 피처 관리, 버전 관리, 데이터셋 탐색
2. **Model Lifecycle**: 실험 추적, 모델 레지스트리, 배포 파이프라인
3. **Evaluation Harness**: 벤치마크, 평가, 모델 비교, 설명 가능성
4. **Prompt Governance**: 프롬프트 템플릿, 버전 관리, 사용량 분석

---

## Phase 3 완료 요약

**총 코드**: 10,538 lines (Phase 1-3 합계)

- **Phase 1**: 4,690 lines (ML Model + Regime Detection + Portfolio Forecast)
- **Phase 2**: 3,239 lines (Optimization + Data Quality)
- **Phase 3**: 2,609 lines (Narrative Report + Strategy Builder + ChatOps)

**Phase 3 산출물**:

- ✅ useNarrativeReport (180 lines) + 5 components (1,196 lines)
- ✅ useStrategyBuilder (181 lines) + 6 components (571 lines)
- ✅ useChatOps (226 lines) + ChatInterface (244 lines)
- ✅ TypeScript 에러 0개
- ✅ Biome 포맷팅 적용

**미완료 항목 (선택 사항)**:

- ⏸️ useChatOpsAdvanced (고급 기능)
- ⏸️ MessageList, CommandInput, StatusCard, SessionManager 컴포넌트
- ⏸️ E2E 테스트 (전체 Phase 통합 테스트는 Phase 6에서 진행)

---

## Phase 4 목표

### 핵심 목표

1. **4개 Custom Hooks 완성**: useFeatureStore, useModelLifecycle,
   useEvaluationHarness, usePromptGovernance
2. **16개 UI 컴포넌트 개발**: 각 시스템당 4개 컴포넌트
3. **12개 API 엔드포인트 연동**: Backend OpenAPI 스키마 활용
4. **TypeScript 타입 안전성**: 0 에러 유지
5. **성능 최적화**: TanStack Query 캐싱, 폴링, 낙관적 업데이트

### 예상 산출물

- **총 코드**: ~3,500 lines
  - Hooks: ~800 lines (각 200 lines)
  - Components: ~2,700 lines (각 ~170 lines)
- **문서**: 각 시스템별 완료 리포트 (4개)

---

## 상세 일정

### Day 1-2: Feature Store System (2025-10-15 ~ 2025-10-17)

**목표**: 피처 엔지니어링 데이터 관리 및 버전 관리 시스템

**Deliverables**:

- `useFeatureStore.ts` (200 lines)
  - `useFeatures()`: 피처 목록 조회 (페이지네이션, 필터링)
  - `useFeatureDetail(featureId)`: 피처 상세 정보 (통계, 타입, 설명)
  - `useFeatureVersions(featureId)`: 피처 버전 히스토리
  - `useDatasets()`: 데이터셋 목록
  - `createFeature()`: 새 피처 생성
  - `updateFeature()`: 피처 업데이트
  - `deleteFeature()`: 피처 삭제

**Components** (~680 lines):

1. **FeatureList.tsx** (180 lines)

   - MUI DataGrid로 피처 목록 표시
   - 필터: 타입, 태그, 생성일
   - 검색 기능 (TextField)
   - 정렬 (이름, 생성일, 사용 빈도)

2. **FeatureDetail.tsx** (170 lines)

   - 피처 메타데이터 (이름, 타입, 설명, 생성자)
   - 통계 정보 (Card): 평균, 중앙값, 표준편차, 결측치 비율
   - 분포 차트 (recharts Histogram)
   - 편집/삭제 버튼

3. **VersionHistory.tsx** (160 lines)

   - Timeline으로 버전 히스토리 표시
   - 버전 비교 (Diff 뷰)
   - 롤백 기능
   - 변경 사항 설명

4. **DatasetExplorer.tsx** (170 lines)
   - 데이터셋 카드 Grid
   - 샘플 데이터 미리보기 (Table)
   - 다운로드 버튼
   - 피처 간 상관관계 히트맵 (recharts)

**Backend API** (예상):

- `GET /api/features`: 피처 목록
- `GET /api/features/{feature_id}`: 피처 상세
- `GET /api/features/{feature_id}/versions`: 버전 히스토리
- `GET /api/datasets`: 데이터셋 목록
- `POST /api/features`: 피처 생성
- `PUT /api/features/{feature_id}`: 피처 업데이트
- `DELETE /api/features/{feature_id}`: 피처 삭제

---

### Day 3-4: Model Lifecycle System (2025-10-18 ~ 2025-10-20) ✅ **COMPLETE**

**목표**: 실험 추적, 모델 레지스트리, 배포 파이프라인 관리

**Status**: ✅ **완료 (2,347 lines)**

**Deliverables**:

- ✅ `useModelLifecycle.ts` (520 lines) - **COMPLETE**
  - useExperiments(): 실험 목록 (필터: 상태, 날짜)
  - useExperimentDetail(experimentId): 실험 상세 (메트릭, 로그, 아티팩트)
  - useModels(): 등록된 모델 목록
  - useModelDetail(modelId): 모델 상세 (버전, 성능, 메트릭)
  - useDeploymentDetail(deploymentId): 배포 상세 (헬스 메트릭, 5초 폴링)
  - createExperiment(): 실험 생성
  - registerModel(): 모델 등록
  - deployModel(): 모델 배포

**Components** (1,827 lines total) - **ALL COMPLETE**:

1. ✅ **ExperimentList.tsx** (375 lines) - **COMPLETE**

   - 실험 목록 Table (이름, 상태, 메트릭, 생성일)
   - 필터: 상태 (running/completed/failed/cancelled), 날짜 범위
   - 정렬: 이름, 생성일, 실행 시간
   - 실험 비교 (체크박스 + 비교 버튼, ≥2 선택 필요)
   - 상태별 색상 코딩 (Chip)

2. ✅ **ModelRegistry.tsx** (480 lines) - **COMPLETE**

   - 모델 카드 Grid (3열: xs=12, sm=6, md=4)
   - 카드 내용: 이름, 버전, 상태 chip, 정확도, 태그, 생성 정보
   - 배포 액션 버튼 (RocketLaunchIcon)
   - 아카이브 버튼 (ArchiveIcon)
   - 모델 상세 Dialog (fullWidth, maxWidth="md")
   - 메트릭 Grid (4 카드: Accuracy, F1, AUC, Loss)

3. ✅ **DeploymentPipeline.tsx** (478 lines) - **COMPLETE**

   - Stepper로 배포 단계 표시 (준비 → 검증 → 배포 → 모니터링)
   - 단계별 아이콘 (CheckCircle, Error)
   - LinearProgress (진행 중인 배포)
   - 배포 로그 Accordion (최대 높이 300px, 스크롤)
   - 롤백 버튼 (활성 배포만, 확인 Dialog)
   - 헬스 메트릭 카드 (요청 수, 에러율, 평균 지연시간)
   - 환경별 색상 코딩 (production=error, staging=warning, dev=default)

4. ✅ **MetricsTracker.tsx** (479 lines) - **COMPLETE**
   - 실시간 메트릭 차트 (recharts LineChart, 50 epochs)
   - 메트릭 카드 (정확도, 손실, F1, AUC) with trend indicators
   - 메트릭 선택 드롭다운 (4 옵션)
   - 차트 뷰 토글 (단일/비교)
   - 추가 정보: 총 에포크, 최적 에포크, 최종 값
   - TODO: 실시간 폴링 (hook에 refetchInterval 지원 필요)

**Exports**:

- ✅ `index.ts` (15 lines) - All 4 components exported

**Quality Assurance**:

- ✅ TypeScript Errors: 0 (모든 파일)
- ✅ Biome Formatting: Applied to all 5 files
- ✅ Lint Issues Resolved:
  - Removed unused import (ModelRegistry.tsx)
  - Removed unused parameter (DeploymentPipeline.tsx)
  - Removed invalid hook parameter (MetricsTracker.tsx)

**Backend API** (TODO - Mock data currently used):

- `GET /api/mlops/experiments`: 실험 목록
- `GET /api/mlops/experiments/{experiment_id}`: 실험 상세 (logs, artifacts)
- `GET /api/mlops/models`: 모델 목록
- `GET /api/mlops/models/{model_id}`: 모델 상세
- `GET /api/mlops/deployments`: 배포 목록
- `GET /api/mlops/deployments/{deployment_id}`: 배포 상세 (health metrics)
- `POST /api/mlops/experiments`: 실험 생성
- `POST /api/mlops/models`: 모델 등록
- `POST /api/mlops/models/{model_id}/deploy`: 모델 배포
- `POST /api/mlops/models/{model_id}/archive`: 모델 아카이브
- `POST /api/mlops/deployments/{deployment_id}/rollback`: 배포 롤백

**Documentation**:

- ✅ PHASE4_DAY3_4_COMPLETE.md (detailed completion report)

---

### Day 5-6: Evaluation Harness System (2025-10-21 ~ 2025-10-23) ✅ **COMPLETE**

**목표**: 모델 평가, 벤치마킹, A/B 테스팅, 공정성 감사

**Status**: ✅ **완료 (2,451 lines)**

**Deliverables**:

- ✅ `useEvaluationHarness.ts` (816 lines) - **COMPLETE**
  - Main Hook:
    - useBenchmarksList(): 벤치마크 목록 (staleTime: 5분)
    - useABTestsList(): A/B 테스트 목록 (staleTime: 2분)
    - useFairnessList(): 공정성 리포트 목록 (staleTime: 5분)
    - createBenchmark(), runBenchmark(), createEvaluation()
    - createABTest(), requestFairnessAudit()
  - Detail Hooks (6 sub-hooks):
    - useBenchmarkDetail(benchmarkId): 벤치마크 상세 + test cases
    - useBenchmarkRun(runId): 벤치마크 실행 상태 (3초 auto-refresh)
    - useEvaluationJob(jobId): 평가 작업 진행 (5초 auto-refresh)
    - useABTestDetail(testId): A/B 테스트 상세 (5초 auto-refresh)
    - useFairnessReport(reportId): 공정성 리포트 (5초 auto-refresh)
    - useEvaluationList(): 모든 평가 작업 목록

**Components** (1,620 lines total) - **ALL COMPLETE**:

1. ✅ **BenchmarkSuite.tsx** (488 lines) - **COMPLETE**

   - 벤치마크 목록 Table (이름, 테스트 수, 상태, 마지막 실행, 결과)
   - 상태 Chip: draft (grey), active (green), archived (orange)
   - 벤치마크 실행 Dialog:
     - Model selection (required)
     - Progress tracking (LinearProgress 0-100%)
     - Real-time status alert (useBenchmarkRun, 3초 polling)
   - 벤치마크 생성 Dialog:
     - Test case builder (동적 add/remove)
     - Expected metrics JSON input

2. ✅ **EvaluationResults.tsx** (442 lines) - **COMPLETE**

   - 5 Metric Cards (Grid size={{ xs: 12, sm: 6, md: 2.4 }}):
     - Accuracy, Precision, Recall, F1 Score, AUC-ROC
   - 3 Tabs:
     - Tab 1: Confusion Matrix (ScatterChart heatmap, red-green gradient)
     - Tab 2: ROC Curve (LineChart + diagonal reference line)
     - Tab 3: Precision-Recall Curve (LineChart)
   - Auto-refresh (useEvaluationJob, 5초 polling)

3. ✅ **ABTestingPanel.tsx** (642 lines) - **COMPLETE**

   - 4-Stage Stepper: Setup → Run → Analyze → Decide
   - Model Comparison Cards (A vs B, traffic split %)
   - Results Comparison Table:
     - Side-by-side metrics (accuracy, precision, recall, f1, auc)
     - Difference Chip (green: A better, red: B better)
   - Statistical Significance Alert:
     - p-value, effect size, confidence level
   - Winner Declaration Card (Gavel icon, color-coded)
   - Create Dialog:
     - Traffic split slider (0-100%, Model A %)
     - Sample size, confidence level (90%/95%/99%)

4. ✅ **FairnessAuditor.tsx** (539 lines) - **COMPLETE**
   - Bias Detection Alert (severity: low/medium/high/critical)
   - Fairness Metrics RadarChart (4 metrics):
     - Demographic Parity, Equal Opportunity, Equalized Odds, Disparate Impact
   - Group Metrics Comparison Table:
     - Accuracy, Precision, Recall, FPR, FNR per group
   - Recommendations Section (Alert array)
   - Request Dialog:
     - Multi-select protected attributes (gender, age, race, ethnicity)
     - Fairness threshold (0.7/0.8/0.9/0.95)

**Additional Files**:

- ✅ `index.ts` (15 lines) - exports all 4 components

**Backend API** (실제 연동 필요, 현재 mock):

- `GET /api/mlops/benchmarks`: 벤치마크 목록
- `GET /api/mlops/benchmarks/{benchmark_id}`: 벤치마크 상세
- `POST /api/mlops/benchmarks`: 벤치마크 생성
- `POST /api/mlops/benchmarks/{benchmark_id}/run`: 벤치마크 실행
- `GET /api/mlops/benchmarks/runs/{run_id}`: 실행 상태
- `GET /api/mlops/evaluations`: 평가 목록
- `POST /api/mlops/evaluations`: 평가 생성
- `GET /api/mlops/evaluations/{job_id}`: 평가 작업 상태
- `GET /api/mlops/ab-tests`: A/B 테스트 목록
- `POST /api/mlops/ab-tests`: A/B 테스트 생성
- `GET /api/mlops/ab-tests/{test_id}`: A/B 테스트 상세
- `GET /api/mlops/fairness`: 공정성 리포트 목록
- `POST /api/mlops/fairness`: 공정성 감사 요청
- `GET /api/mlops/fairness/{report_id}`: 공정성 리포트 상세

**Documentation**:

- ✅ PHASE4_DAY5_6_COMPLETE.md (comprehensive completion report with 2,451 lines
  breakdown)

**Quality Metrics**:

- ✅ TypeScript Errors: 0
- ✅ Lint Warnings: 0
- ✅ Biome Formatting: Applied
- ✅ Auto-Refresh Logic: Implemented (3-5s polling based on status)
- ✅ Type Safety: All interfaces defined, FairnessReport restructured
  - 피처 중요도 (recharts Waterfall)
  - LIME 설명 (텍스트 + 하이라이트)
  - 예측 상세 (입력 데이터, 예측 값, 신뢰도)

**Backend API** (예상):

- `GET /api/benchmarks`: 벤치마크 목록
- `GET /api/benchmarks/{benchmark_id}`: 벤치마크 상세
- `GET /api/evaluations/{model_id}`: 평가 결과
- `POST /api/evaluations/compare`: 모델 비교
- `GET /api/explainability/{model_id}/{prediction_id}`: 설명 가능성
- `POST /api/benchmarks/{benchmark_id}/run`: 벤치마크 실행

---

### Day 7-8: Prompt Governance System (2025-10-24 ~ 2025-10-26)

**목표**: LLM 프롬프트 템플릿 관리, 버전 관리, 사용량 분석

**Deliverables**:

- `usePromptGovernance.ts` (200 lines)
  - `usePromptTemplates()`: 프롬프트 템플릿 목록
  - `usePromptTemplateDetail(templateId)`: 템플릿 상세
  - `usePromptVersions(templateId)`: 버전 히스토리
  - `usePromptUsage(templateId)`: 사용량 통계
  - `createTemplate()`: 템플릿 생성
  - `updateTemplate()`: 템플릿 업데이트
  - `deleteTemplate()`: 템플릿 삭제
  - `testPrompt()`: 프롬프트 테스트

**Components** (~680 lines):

1. **TemplateList.tsx** (170 lines)

   - 템플릿 카드 Grid (이름, 설명, 버전, 사용 횟수)
   - 필터: 태그, 생성일
   - 검색 (이름, 설명)
   - 정렬 (사용 빈도, 최근 업데이트)

2. **TemplateEditor.tsx** (190 lines)

   - Monaco Editor로 프롬프트 편집 (Markdown 하이라이트)
   - 변수 자동 완성 ({{variable}})
   - 테스트 패널 (샘플 입력 → 출력 미리보기)
   - 저장/버전 생성 버튼

3. **VersionControl.tsx** (160 lines)

   - 버전 Timeline
   - 버전 비교 (Diff 뷰)
   - 롤백 기능
   - 변경 사항 설명

4. **UsageAnalytics.tsx** (160 lines)
   - 사용량 차트 (recharts LineChart, 시계열)
   - 성공률 (Pie Chart)
   - 응답 시간 분포 (AreaChart)
   - Top 템플릿 (Table)

**Backend API** (예상):

- `GET /api/prompts/templates`: 템플릿 목록
- `GET /api/prompts/templates/{template_id}`: 템플릿 상세
- `GET /api/prompts/templates/{template_id}/versions`: 버전 히스토리
- `GET /api/prompts/templates/{template_id}/usage`: 사용량 통계
- `POST /api/prompts/templates`: 템플릿 생성
- `PUT /api/prompts/templates/{template_id}`: 템플릿 업데이트
- `DELETE /api/prompts/templates/{template_id}`: 템플릿 삭제
- `POST /api/prompts/test`: 프롬프트 테스트

---

## 기술 스택

### 기존 라이브러리 (Phase 3에서 설치 완료)

- ✅ **@tanstack/react-query** v5: 서버 상태 관리
- ✅ **@mui/material** v6: UI 컴포넌트
- ✅ **recharts** v2.10.0: 차트
- ✅ **d3** v7.9.0: 고급 시각화
- ✅ **@monaco-editor/react** v4.7.0: 코드 에디터
- ✅ **date-fns** v3.0.0: 날짜 포맷팅
- ✅ **lodash** v4.17.21: 유틸리티

### 추가 필요 라이브러리 (확인 필요)

```bash
# Phase 4에서 추가로 필요할 수 있는 라이브러리 (확인 후 설치)
pnpm add react-diff-viewer  # 버전 비교 Diff 뷰
pnpm add react-window       # 가상화 (대량 데이터 렌더링)
```

---

## 개발 프로세스

### 각 시스템 개발 단계 (2일 사이클)

1. **Day 1 오전**: Hook 설계 및 구현

   - TanStack Query 패턴 적용
   - TypeScript 타입 정의
   - API 클라이언트 통합 (pnpm gen:client 선행)

2. **Day 1 오후**: Component 1-2 구현

   - UI 레이아웃 (MUI Grid)
   - 데이터 바인딩 (Hook 연결)
   - 에러 핸들링

3. **Day 2 오전**: Component 3-4 구현

   - 차트/시각화 (recharts)
   - 인터랙션 (버튼, 폼)
   - 로딩/빈 상태

4. **Day 2 오후**: 통합 테스트 및 문서화
   - TypeScript 에러 체크 (pnpm build)
   - Biome 포맷팅 (pnpm format)
   - 완료 리포트 작성

### 코드 품질 기준

- **TypeScript**: 0 에러, strict 모드
- **ESLint**: 0 경고 (Biome)
- **Import**: Absolute path (@/hooks, @/components)
- **Naming**: camelCase (변수), PascalCase (컴포넌트), kebab-case (파일)
- **주석**: JSDoc for hooks, inline comments for complex logic

---

## 위험 관리

### 주요 위험

1. **Backend API 미완성** (높음)
   - 대응: Mock 데이터 우선 개발, API 스펙 사전 확인
2. **차트 성능 이슈** (중간)

   - 대응: 데이터 페이지네이션, react-window 가상화

3. **Monaco Editor 통합 복잡도** (중간)

   - 대응: Phase 3 StrategyPreview 코드 재사용

4. **Diff 뷰 복잡도** (낮음)
   - 대응: react-diff-viewer 라이브러리 활용

---

## 성공 기준

### Phase 4 완료 조건

- ✅ 4개 Custom Hooks 완성 (useFeatureStore, useModelLifecycle,
  useEvaluationHarness, usePromptGovernance)
- ✅ 16개 UI 컴포넌트 완성
- ✅ TypeScript 에러 0개
- ✅ Biome 포맷팅 적용
- ✅ 각 시스템별 완료 리포트 (4개)

### 전체 프로젝트 기준 (Phase 1-4)

- **API 연동**: 32/32 (100%)
- **Custom Hooks**: 12/13 (92%, useChatOpsAdvanced 제외)
- **UI 컴포넌트**: 55/60 (92%, 선택 컴포넌트 제외)
- **총 코드**: ~14,000 lines

---

## 다음 단계

**즉시 시작**: Day 1-2 Feature Store System

1. Backend API 스펙 확인 (OpenAPI 스키마)
2. `useFeatureStore.ts` 훅 구현
3. `FeatureList.tsx`, `FeatureDetail.tsx` 컴포넌트 구현
4. `VersionHistory.tsx`, `DatasetExplorer.tsx` 컴포넌트 구현
5. 통합 테스트 및 PHASE4_DAY1_2_COMPLETE.md 작성

---

**작성일**: 2025-10-15  
**작성자**: GitHub Copilot  
**상태**: ✅ 승인됨 - Phase 4 Day 1-2 착수 가능
