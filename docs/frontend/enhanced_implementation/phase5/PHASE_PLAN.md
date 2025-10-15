# Phase 5: 페이지 통합 및 사용자 시나리오 구현

**작성일**: 2025-10-15  
**전제 조건**: Phase 1-4 완료 (51개 컴포넌트, 13개 훅, 17,737 lines, TypeScript
0 에러)  
**목표**: User Stories 기반 페이지 구현, 엔드투엔드 사용자 플로우 완성

---

## 🎯 Phase 5 개요

### 현재 상태 진단

**✅ 완료된 작업**:

- Phase 1-4: **51개 도메인별 컴포넌트** 완성 (MLOps, GenAI, 최적화, 데이터 품질)
- **13개 커스텀 훅** 완성 (API 통합, 상태 관리)
- **17,737 lines** 프로덕션 코드
- **TypeScript 에러 0개** (타입 안전성 100%)

**❌ 미완료 작업**:

- **MLOps 페이지 누락** (Feature Store, Model Lifecycle, Evaluation)
- **GenAI 페이지 누락** (ChatOps, Strategy Builder, Narrative Report)
- **최적화 페이지 누락** (Optimization 워크플로우)
- **데이터 품질 페이지 누락** (Data Quality 대시보드)
- **User Stories 구현 누락** (US-6 ~ US-19, 14개 AI Integration 시나리오)

**문제점**:

> 컴포넌트와 훅은 완성되었지만, **이를 활용하는 페이지가 없어** 사용자가 기능에
> 접근할 수 없음. 기존 페이지(백테스트, 전략, 마켓 데이터)만 존재하며, AI
> Integration 기능이 고립되어 있음.

---

## 📋 Phase 5 목표

### 1. User Stories 기반 페이지 구현

**US-6 ~ US-19** (14개 AI Integration 시나리오) 구현:

- ✅ 기술적 구성 요소 완료 (컴포넌트, 훅)
- ❌ 사용자 접근 경로 누락 (페이지)
- 🎯 **목표**: User Stories → 실제 사용 가능한 페이지 구현

### 2. 도메인별 페이지 구조 완성

**4개 주요 도메인**:

1. **MLOps Platform** (6개 페이지)
2. **GenAI Services** (5개 페이지)
3. **Optimization** (2개 페이지)
4. **Data Quality** (2개 페이지)

### 3. 네비게이션 및 UX 개선

- Sidebar 메뉴 확장 (MLOps, GenAI, Tools 섹션)
- Breadcrumb 통합
- 페이지 간 자연스러운 이동 경로

---

## 🗂️ Phase 5 페이지 구조

### 1. MLOps Platform Domain (6 pages)

#### 1.1 Feature Store 메인 페이지

```
/mlops/feature-store
├── 목적: Feature Engineering 중앙 관리
├── 컴포넌트: FeatureList, DatasetExplorer
├── User Story: US-16 (피처 스토어 탐색)
└── 주요 기능:
    ├── Feature 목록 조회 (필터링, 정렬)
    ├── Dataset 탐색
    ├── Feature 생성 버튼 → 상세 페이지 이동
    └── 통계 대시보드 (Feature 수, 버전 수, 최근 업데이트)
```

**파일**: `frontend/src/app/(main)/mlops/feature-store/page.tsx`

**레이아웃**:

```tsx
<PageContainer title="Feature Store" breadcrumbs={[...]}>
  <Grid container spacing={3}>
    {/* KPI Cards */}
    <Grid size={12}>
      <StatisticsCards />
    </Grid>

    {/* Main Content */}
    <Grid size={8}>
      <FeatureList onFeatureClick={...} onCreateClick={...} />
    </Grid>

    {/* Side Panel */}
    <Grid size={4}>
      <DatasetExplorer />
    </Grid>
  </Grid>
</PageContainer>
```

---

#### 1.2 Feature 상세 페이지

```
/mlops/feature-store/[id]
├── 목적: Feature 상세 정보 및 관리
├── 컴포넌트: FeatureDetail, VersionHistory
├── User Story: US-16 (버전 관리, 통계)
└── 주요 기능:
    ├── Feature 메타데이터 (이름, 설명, 타입, 상태)
    ├── 버전 히스토리 (타임라인)
    ├── 통계 정보 (분포, 결측치, 이상치)
    ├── 계보 추적 (Lineage)
    └── CRUD 작업 (수정, 삭제, 버전 생성)
```

**파일**: `frontend/src/app/(main)/mlops/feature-store/[id]/page.tsx`

**레이아웃**:

```tsx
<PageContainer title={feature.name} breadcrumbs={[...]}>
  <Grid container spacing={3}>
    {/* Feature Detail */}
    <Grid size={8}>
      <FeatureDetail featureId={id} />
    </Grid>

    {/* Version History */}
    <Grid size={4}>
      <VersionHistory featureId={id} />
    </Grid>
  </Grid>
</PageContainer>
```

---

#### 1.3 Model Lifecycle 메인 페이지

```
/mlops/model-lifecycle
├── 목적: ML 모델 실험 추적 및 배포 관리
├── 컴포넌트: ExperimentList, ModelRegistry
├── User Story: US-17 (모델 라이프사이클 관리)
└── 주요 기능:
    ├── Experiment 목록 (진행 상태별 필터)
    ├── Model Registry (배포 상태별 필터)
    ├── 실험 생성 버튼 → 생성 폼
    ├── 모델 배포 파이프라인 접근
    └── KPI: 총 실험 수, 배포된 모델 수, 평균 성능
```

**파일**: `frontend/src/app/(main)/mlops/model-lifecycle/page.tsx`

**레이아웃**:

```tsx
<PageContainer title="Model Lifecycle" breadcrumbs={[...]}>
  <Grid container spacing={3}>
    {/* Statistics */}
    <Grid size={12}>
      <StatisticsCards />
    </Grid>

    {/* Experiments */}
    <Grid size={6}>
      <ExperimentList onExperimentClick={...} />
    </Grid>

    {/* Model Registry */}
    <Grid size={6}>
      <ModelRegistry onModelClick={...} />
    </Grid>
  </Grid>
</PageContainer>
```

---

#### 1.4 Model 상세 페이지

```
/mlops/model-lifecycle/models/[id]
├── 목적: 모델 상세 정보 및 배포 관리
├── 컴포넌트: DeploymentPipeline, MetricsTracker
├── User Story: US-17 (Drift 감지, 배포)
└── 주요 기능:
    ├── 모델 메타데이터 (버전, 알고리즘, 하이퍼파라미터)
    ├── 메트릭 추적 (정확도, 손실, 커스텀 메트릭)
    ├── 배포 파이프라인 (Staging → Production)
    ├── Drift 감지 대시보드
    └── 모델 비교 (버전 간)
```

**파일**: `frontend/src/app/(main)/mlops/model-lifecycle/models/[id]/page.tsx`

---

#### 1.5 Evaluation Harness 메인 페이지

```
/mlops/evaluation
├── 목적: 모델 평가 및 벤치마크
├── 컴포넌트: BenchmarkSuite, ABTestingPanel, FairnessAuditor
├── User Story: US-18 (모델 성능 평가)
└── 주요 기능:
    ├── 벤치마크 스위트 실행
    ├── A/B 테스트 관리
    ├── 공정성 감사 (Fairness Metrics)
    ├── 평가 결과 시각화
    └── 시나리오별 성능 비교
```

**파일**: `frontend/src/app/(main)/mlops/evaluation/page.tsx`

**레이아웃**:

```tsx
<PageContainer title="Model Evaluation" breadcrumbs={[...]}>
  <Tabs value={tab} onChange={setTab}>
    <Tab label="Benchmarks" />
    <Tab label="A/B Testing" />
    <Tab label="Fairness Audit" />
  </Tabs>

  {tab === 0 && <BenchmarkSuite />}
  {tab === 1 && <ABTestingPanel />}
  {tab === 2 && <FairnessAuditor />}
</PageContainer>
```

---

#### 1.6 Prompt Governance 페이지

```
/mlops/prompt-governance
├── 목적: LLM 프롬프트 템플릿 관리
├── 컴포넌트: PromptTemplateEditor, VersionControl, UsageAnalytics
├── User Story: US-19 (프롬프트 버전 관리)
└── 주요 기능:
    ├── 템플릿 목록 (서비스별 분류)
    ├── 템플릿 편집기 (Monaco Editor)
    ├── 버전 관리 (Git-style)
    ├── 사용량 분석 (성공률, 응답 시간)
    └── 템플릿 테스트 실행
```

**파일**: `frontend/src/app/(main)/mlops/prompt-governance/page.tsx`

---

### 2. GenAI Services Domain (5 pages)

#### 2.1 ChatOps 메인 페이지

```
/gen-ai/chatops
├── 목적: 대화형 시스템 관리 및 전략 상담
├── 컴포넌트: ChatInterface
├── User Story: US-13, US-14, US-15 (ChatOps 시스템)
└── 주요 기능:
    ├── 멀티턴 대화 인터페이스
    ├── 시스템 상태 조회 (자연어 명령)
    ├── 전략 비교 및 추천
    ├── 자동 백테스트 트리거
    └── 세션 히스토리 관리
```

**파일**: `frontend/src/app/(main)/gen-ai/chatops/page.tsx`

**레이아웃**:

```tsx
<PageContainer title="ChatOps" breadcrumbs={[...]}>
  <Grid container spacing={2}>
    {/* Chat Interface (Full Width) */}
    <Grid size={12}>
      <ChatInterface
        enableBacktestTrigger={true}
        enableStrategyComparison={true}
        enableSystemStatus={true}
      />
    </Grid>

    {/* Session History (Optional Sidebar) */}
    <Grid size={3}>
      <SessionHistory />
    </Grid>
  </Grid>
</PageContainer>
```

---

#### 2.2 Strategy Builder 페이지

```
/gen-ai/strategy-builder
├── 목적: 자연어로 트레이딩 전략 생성
├── 컴포넌트: ConversationInterface, StrategyPreview, ValidationFeedback
├── User Story: US-12 (대화형 전략 빌더)
└── 주요 기능:
    ├── 자연어 입력 (예: "RSI 전략 만들어줘")
    ├── Intent 파싱 및 파라미터 추출
    ├── 지표 추천 (TechnicalIndicator 제안)
    ├── 전략 미리보기 (코드 생성)
    ├── 파라미터 검증 및 피드백
    └── 전략 저장 → Strategy 페이지 이동
```

**파일**: `frontend/src/app/(main)/gen-ai/strategy-builder/page.tsx`

**레이아웃**:

```tsx
<PageContainer title="Strategy Builder" breadcrumbs={[...]}>
  <Grid container spacing={3}>
    {/* Conversation Interface */}
    <Grid size={7}>
      <ConversationInterface onStrategyGenerated={...} />
    </Grid>

    {/* Strategy Preview */}
    <Grid size={5}>
      <StrategyPreview strategy={generatedStrategy} />
      <ValidationFeedback validations={validations} />
    </Grid>
  </Grid>
</PageContainer>
```

---

#### 2.3 Narrative Report 뷰어 페이지

```
/gen-ai/narrative-reports
├── 목적: AI 생성 백테스트 리포트 조회
├── 컴포넌트: ReportViewer, ExportButton, ShareDialog
├── User Story: US-11 (내러티브 리포트 생성)
└── 주요 기능:
    ├── 리포트 목록 (백테스트별)
    ├── 리포트 뷰어 (Markdown 렌더링)
    ├── 섹션별 네비게이션
    ├── 리포트 재생성 버튼
    ├── Export (PDF, Word)
    └── 공유 기능 (링크, 이메일)
```

**파일**: `frontend/src/app/(main)/gen-ai/narrative-reports/page.tsx`

**레이아웃**:

```tsx
<PageContainer title="Narrative Reports" breadcrumbs={[...]}>
  <Grid container spacing={3}>
    {/* Report List */}
    <Grid size={3}>
      <ReportList onReportSelect={...} />
    </Grid>

    {/* Report Viewer */}
    <Grid size={9}>
      <ReportViewer reportId={selectedId} />
      <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
        <ExportButton format="pdf" />
        <ShareDialog reportId={selectedId} />
        <RegenerationButton backtestId={backtestId} />
      </Box>
    </Grid>
  </Grid>
</PageContainer>
```

---

#### 2.4 Narrative Report 상세 페이지

```
/gen-ai/narrative-reports/[id]
├── 목적: 단일 리포트 상세 뷰
├── 컴포넌트: ReportViewer, SectionRenderer
├── User Story: US-11 (리포트 탐색)
└── 주요 기능:
    ├── 리포트 전체 내용
    ├── 섹션별 앵커 링크
    ├── 차트 및 테이블 임베드
    └── 백테스트 결과 링크
```

**파일**: `frontend/src/app/(main)/gen-ai/narrative-reports/[id]/page.tsx`

---

#### 2.5 ML Models 페이지 (Phase 1 완료, 위치 이동)

```
/gen-ai/ml-models (또는 /mlops/ml-models)
├── 목적: ML 모델 학습 및 관리
├── 컴포넌트: MLModelList, MLModelDetail, MLModelComparison, MLTrainingDialog
├── User Story: US-6, US-7, US-8 (ML 기반 신호 활용)
└── 주요 기능:
    ├── 모델 목록 (필터링, 정렬)
    ├── 모델 학습 (TrainingDialog)
    ├── 모델 비교 (성능 차트)
    └── 모델 배포 상태
```

**파일**: `frontend/src/app/(main)/mlops/ml-models/page.tsx` (기존 위치에서
이동)

---

### 3. Optimization Domain (2 pages)

#### 3.1 백테스트 최적화 메인 페이지

```
/optimization/backtest
├── 목적: Optuna 기반 파라미터 자동 최적화
├── 컴포넌트: OptimizationWizard, OptimizationProgress
├── User Story: US-9 (백테스트 자동 최적화)
└── 주요 기능:
    ├── 최적화 대상 전략 선택
    ├── 파라미터 범위 설정 (Wizard)
    ├── 목적 함수 선택 (샤프 비율, 총 수익률 등)
    ├── 최적화 실행 및 진행 상황 모니터링
    └── 최적 파라미터 적용 → 백테스트 생성
```

**파일**: `frontend/src/app/(main)/optimization/backtest/page.tsx`

**레이아웃**:

```tsx
<PageContainer title="Backtest Optimization" breadcrumbs={[...]}>
  <Stepper activeStep={step}>
    <Step label="Select Strategy" />
    <Step label="Configure Parameters" />
    <Step label="Run Optimization" />
    <Step label="Apply Results" />
  </Stepper>

  {step === 0 && <StrategySelector />}
  {step === 1 && <OptimizationWizard />}
  {step === 2 && <OptimizationProgress name={optimizationName} />}
  {step === 3 && <BestParamsPanel />}
</PageContainer>
```

---

#### 3.2 최적화 결과 상세 페이지

```
/optimization/backtest/[name]
├── 목적: 최적화 결과 분석
├── 컴포넌트: TrialHistoryChart, BestParamsPanel
├── User Story: US-9 (최적 파라미터 확인)
└── 주요 기능:
    ├── Trial 히스토리 차트 (성능 추이)
    ├── 최적 파라미터 요약
    ├── 파라미터 중요도 차트
    ├── Pareto Front 시각화
    └── 최적 결과로 백테스트 실행 버튼
```

**파일**: `frontend/src/app/(main)/optimization/backtest/[name]/page.tsx`

---

### 4. Data Quality Domain (2 pages)

#### 4.1 데이터 품질 대시보드

```
/data-quality
├── 목적: 이상 데이터 감지 및 모니터링
├── 컴포넌트: DataQualityDashboard, AlertTimeline, SeverityPieChart, AnomalyDetailTable
├── User Story: US-10 (데이터 품질 모니터링)
└── 주요 기능:
    ├── 실시간 이상 감지 현황 (KPI 카드)
    ├── 심각도별 분포 (Pie Chart)
    ├── 알림 타임라인 (최근 24시간)
    ├── 이상치 상세 테이블 (필터링, 정렬)
    └── 수동 검증 및 무시 기능
```

**파일**: `frontend/src/app/(main)/data-quality/page.tsx`

**레이아웃**:

```tsx
<PageContainer title="Data Quality Sentinel" breadcrumbs={[...]}>
  <DataQualityDashboard />
</PageContainer>
```

---

#### 4.2 데이터 품질 알림 상세 페이지

```
/data-quality/alerts/[id]
├── 목적: 개별 이상치 상세 분석
├── 컴포넌트: AnomalyDetailTable (확장 뷰)
└── 주요 기능:
    ├── 이상치 메타데이터 (타임스탬프, 심볼, 필드)
    ├── 컨텍스트 데이터 (전후 데이터 포인트)
    ├── 시각화 (차트 오버레이)
    ├── 액션 (무시, 수정, 재검증)
    └── 관련 백테스트 영향 분석
```

**파일**: `frontend/src/app/(main)/data-quality/alerts/[id]/page.tsx`

---

## 🗺️ 네비게이션 구조 개선

### Sidebar 메뉴 확장

**기존 메뉴**:

```tsx
- Dashboard
- Strategies
  - My Strategies
  - Templates
  - Create
- Backtests
  - Run
  - History
- Market Data
  - Stocks
  - Forex
  - Crypto
```

**Phase 5 추가 메뉴**:

```tsx
- MLOps Platform ⭐ NEW
  - Feature Store
  - Model Lifecycle
  - Model Evaluation
  - ML Models
  - Prompt Governance

- GenAI Services ⭐ NEW
  - ChatOps
  - Strategy Builder
  - Narrative Reports

- Tools ⭐ NEW
  - Optimization
  - Data Quality
```

**파일 수정**: `frontend/src/components/layout/sidebar/Sidebar.tsx`

---

## 📅 Phase 5 일정 (3주)

### Week 1: MLOps 페이지 (5일)

**Day 1-2: Feature Store**

- ✅ 메인 페이지 (`/mlops/feature-store`)
- ✅ 상세 페이지 (`/mlops/feature-store/[id]`)
- ✅ FeatureList + DatasetExplorer 통합
- ✅ VersionHistory 탭 추가

**Day 3-4: Model Lifecycle**

- ✅ 메인 페이지 (`/mlops/model-lifecycle`)
- ✅ 모델 상세 페이지 (`/mlops/model-lifecycle/models/[id]`)
- ✅ ExperimentList + ModelRegistry 레이아웃
- ✅ DeploymentPipeline 통합

**Day 5: Evaluation & Prompt Governance**

- ✅ Evaluation 페이지 (`/mlops/evaluation`)
- ✅ Prompt Governance 페이지 (`/mlops/prompt-governance`)
- ✅ Tabs 레이아웃 (Benchmark, A/B Test, Fairness)

**산출물**:

- 6개 페이지 파일
- Sidebar 메뉴 확장 (MLOps 섹션)
- Breadcrumb 통합

---

### Week 2: GenAI 페이지 (5일)

**Day 1-2: ChatOps**

- ✅ ChatOps 메인 페이지 (`/gen-ai/chatops`)
- ✅ ChatInterface 전체 화면 레이아웃
- ✅ Session History 사이드바
- ✅ 시스템 상태 조회 통합

**Day 3: Strategy Builder**

- ✅ Strategy Builder 페이지 (`/gen-ai/strategy-builder`)
- ✅ ConversationInterface + StrategyPreview 레이아웃
- ✅ 전략 저장 → Strategies 페이지 리다이렉트

**Day 4-5: Narrative Reports**

- ✅ 리포트 목록 페이지 (`/gen-ai/narrative-reports`)
- ✅ 리포트 상세 페이지 (`/gen-ai/narrative-reports/[id]`)
- ✅ ReportViewer + Export 버튼 통합
- ✅ 백테스트 연동 (결과 → 리포트 링크)

**산출물**:

- 5개 페이지 파일
- Sidebar 메뉴 확장 (GenAI 섹션)
- 백테스트 상세 페이지에 "Generate Report" 버튼 추가

---

### Week 3: Optimization & Data Quality + 통합 (5일)

**Day 1-2: Optimization**

- ✅ 최적화 메인 페이지 (`/optimization/backtest`)
- ✅ OptimizationWizard Stepper 레이아웃
- ✅ 최적화 결과 상세 페이지 (`/optimization/backtest/[name]`)
- ✅ TrialHistoryChart + BestParamsPanel

**Day 3: Data Quality**

- ✅ 데이터 품질 대시보드 (`/data-quality`)
- ✅ 알림 상세 페이지 (`/data-quality/alerts/[id]`)
- ✅ DataQualityDashboard 전체 화면

**Day 4: 네비게이션 통합**

- ✅ Sidebar 메뉴 최종 정리 (3개 섹션 추가)
- ✅ Breadcrumb 모든 페이지 적용
- ✅ 페이지 간 링크 정리 (크로스 도메인 네비게이션)

**Day 5: 통합 테스트 및 버그 수정**

- ✅ 모든 페이지 접근성 테스트
- ✅ 타입 에러 검증 (`tsc --noEmit`)
- ✅ 빌드 테스트 (`pnpm build`)
- ✅ 문서 업데이트 (Phase 5 완료 보고서)

**산출물**:

- 4개 페이지 파일
- Sidebar 메뉴 확장 (Tools 섹션)
- Phase 5 완료 보고서 (`PHASE5_COMPLETION_REPORT.md`)

---

## 🎯 User Stories 매핑

### Phase 5에서 완성되는 User Stories

| User Story | 페이지                      | 컴포넌트                                          | 완성도 |
| ---------- | --------------------------- | ------------------------------------------------- | ------ |
| US-6       | `/mlops/ml-models`          | MLModelList, MLModelDetail                        | 100%   |
| US-7       | `/strategies/[id]`          | RegimeIndicator (기존 페이지에 추가)              | 80%    |
| US-8       | `/strategies/[id]`          | ForecastChart (기존 페이지에 추가)                | 80%    |
| US-9       | `/optimization/backtest`    | OptimizationWizard, OptimizationProgress          | 100%   |
| US-10      | `/data-quality`             | DataQualityDashboard                              | 100%   |
| US-11      | `/gen-ai/narrative-reports` | ReportViewer, ExportButton                        | 100%   |
| US-12      | `/gen-ai/strategy-builder`  | ConversationInterface, StrategyPreview            | 100%   |
| US-13      | `/gen-ai/chatops`           | ChatInterface (시스템 상태)                       | 100%   |
| US-14      | `/gen-ai/chatops`           | ChatInterface (전략 비교)                         | 100%   |
| US-15      | `/gen-ai/chatops`           | ChatInterface (자동 백테스트)                     | 100%   |
| US-16      | `/mlops/feature-store`      | FeatureList, FeatureDetail, VersionHistory        | 100%   |
| US-17      | `/mlops/model-lifecycle`    | ExperimentList, ModelRegistry, DeploymentPipeline | 100%   |
| US-18      | `/mlops/evaluation`         | BenchmarkSuite, ABTestingPanel, FairnessAuditor   | 100%   |
| US-19      | `/mlops/prompt-governance`  | PromptTemplateEditor, VersionControl              | 100%   |

**총 14개 User Stories 완성** (AI Integration 전체 시나리오)

---

## 📊 성공 기준

### 1. 기술적 기준

- ✅ **페이지 수**: 15개 추가 (MLOps 6 + GenAI 5 + Optimization 2 + Data
  Quality 2)
- ✅ **TypeScript 에러**: 0개 유지
- ✅ **빌드 성공**: `pnpm build` 에러 없이 완료
- ✅ **네비게이션**: Sidebar 3개 섹션 추가, Breadcrumb 전체 적용

### 2. 사용자 경험 기준

- ✅ **접근성**: 모든 AI Integration 기능 3클릭 이내 접근
- ✅ **플로우**: User Stories 시나리오 엔드투엔드 구현
- ✅ **일관성**: Material-UI Grid v7, PageContainer 패턴 통일

### 3. 문서화 기준

- ✅ **Phase 5 완료 보고서**: 페이지별 스크린샷, 코드 통계
- ✅ **사용자 가이드**: 각 도메인별 사용법 문서
- ✅ **API 통합 검증**: 백엔드 API 32개 엔드포인트 연동 확인

---

## 🚀 다음 단계 (Phase 6 Preview)

Phase 5 완료 후:

1. **E2E 테스트** (Playwright, 주요 플로우)
2. **성능 최적화** (Lighthouse, Web Vitals)
3. **Storybook 문서화** (컴포넌트 카탈로그)
4. **Production 배포** (CI/CD, 모니터링)

---

## 📝 참고 문서

- [User Stories](../USER_STORY.md) - AI Integration 시나리오 상세
- [AI Integration User Stories](../AI_INTEGRATION_USER_STORIES.md) - Phase별
  우선순위
- [Backend README](../../../../backend/README.md) - API 엔드포인트 명세
- [Project Dashboard](../PROJECT_DASHBOARD.md) - Phase 1-4 완료 현황

---

**작성자**: GitHub Copilot  
**리뷰어**: Frontend Lead  
**승인 필요**: Phase 5 시작 전 검토 및 승인
