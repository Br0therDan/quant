# AI Integration User Stories & Frontend Implementation Plan

> **최종 업데이트**: 2025년 10월 14일  
> **Backend 상태**: Phase 1-4 완료 (100%)  
> **Frontend 상태**: 구현 대기  
> **우선순위**: Phase별 순차 구현

## 📋 신규 유저 스토리 (AI Integration)

### US-6: ML 기반 신호 활용 (Phase 1) 🎯 높음

**As a** 퀀트 트레이더  
**I want to** ML 모델이 생성한 매수/매도 신호를 전략에 활용  
**So that** 휴리스틱 대비 향상된 수익률을 달성할 수 있다

**수락 기준**:

- ✅ ML 모델 목록 조회 (`GET /api/v1/ml/models`)
- ✅ 모델 상세 정보 확인 (정확도, F1 Score)
- ✅ 특정 모델로 전략 생성
- ✅ 백테스트 실행 시 ML 신호 적용
- ✅ 성과 비교 (ML vs Heuristic)

**API 엔드포인트**:

```typescript
GET / api / v1 / ml / models; // 모델 목록
GET / api / v1 / ml / models / { version }; // 모델 상세
GET / api / v1 / ml / models / compare / { metric }; // 모델 비교
POST / api / v1 / ml / train; // 모델 학습 (Background)
DELETE / api / v1 / ml / models / { version }; // 모델 삭제
```

**프론트엔드 훅**:

```typescript
// ✨ 신규 훅: useMLModel
const {
  models,              // 모델 목록
  modelDetail,         // 선택된 모델 상세
  compareModels,       // 모델 비교 데이터
  trainModel,          // 모델 학습 트리거
  deleteModel,         // 모델 삭제
  isTraining,          // 학습 진행 상태
} = useMLModel(modelVersion?);
```

**UI 컴포넌트**:

1. **MLModelList**: 모델 카드 그리드 (버전, 정확도, 생성일)
2. **MLModelDetail**: 성능 메트릭 차트 (정확도, Precision, Recall, F1)
3. **MLModelComparison**: 여러 모델 비교 테이블
4. **MLTrainingDialog**: 학습 파라미터 입력 폼

---

### US-7: 시장 국면 분석 (Phase 1) 🎯 높음

**As a** 애널리스트  
**I want to** 현재 시장 국면(강세/약세/횡보/고변동성)을 확인  
**So that** 국면에 맞는 전략을 선택할 수 있다

**수락 기준**:

- ✅ 현재 국면 조회 (HMM 기반)
- ✅ 국면 히스토리 차트 (시계열)
- ✅ 심볼별 국면 비교
- ✅ 전략별 국면 적응 파라미터 추천

**API 엔드포인트**:

```typescript
GET / api / v1 / market - data / regime; // 현재 국면
GET / api / v1 / market - data / regime / history / { symbol }; // 국면 히스토리
```

**프론트엔드 훅**:

```typescript
// ✨ 신규 훅: useRegimeDetection
const {
  currentRegime, // 현재 국면 (BULL/BEAR/SIDEWAYS/HIGH_VOLATILITY)
  regimeHistory, // 국면 히스토리 시계열
  regimeConfidence, // 분류 신뢰도
  loading,
  error,
} = useRegimeDetection(symbol);
```

**UI 컴포넌트**:

1. **RegimeIndicator**: 현재 국면 배지 (색상 코딩)
2. **RegimeHistoryChart**: 시계열 영역 차트 (국면 변화)
3. **RegimeComparison**: 여러 심볼 국면 비교
4. **RegimeStrategyRecommendation**: 국면별 추천 전략

---

### US-8: 포트폴리오 확률 예측 (Phase 1) 🎯 높음

**As a** 투자자  
**I want to** 미래 포트폴리오 가치의 확률 분포를 확인  
**So that** 리스크를 정량적으로 평가할 수 있다

**수락 기준**:

- ✅ N일 후 포트폴리오 가치 예측 (5%, 50%, 95% 퍼센타일)
- ✅ 예측 차트 (신뢰구간 포함)
- ✅ 시나리오 분석 (낙관/중립/비관)
- ✅ VaR, CVaR 계산

**API 엔드포인트**:

```typescript
GET / api / v1 / dashboard / portfolio / forecast; // 포트폴리오 예측
```

**프론트엔드 훅**:

```typescript
// ✨ 신규 훅: usePortfolioForecast
const {
  forecast, // 예측 데이터 (퍼센타일 밴드)
  scenarios, // 시나리오 분석 결과
  riskMetrics, // VaR, CVaR
  forecastDays, // 예측 기간
  setForecastDays, // 예측 기간 변경
  loading,
} = usePortfolioForecast(backtestId, days);
```

**UI 컴포넌트**:

1. **ForecastChart**: 퍼센타일 밴드 차트 (p5, p50, p95)
2. **ScenarioAnalysis**: 시나리오별 예상 수익률
3. **RiskMetricsPanel**: VaR, CVaR, Sharpe Ratio
4. **ForecastControls**: 예측 기간 슬라이더

---

### US-9: 백테스트 자동 최적화 (Phase 2) 🎯 높음

**As a** 개발자  
**I want to** Optuna로 전략 파라미터를 자동 최적화  
**So that** 수작업 없이 최적 설정을 찾을 수 있다

**수락 기준**:

- ✅ 최적화 스터디 생성
- ✅ 진행 상황 실시간 조회
- ✅ 최적 파라미터 조회
- ✅ 트라이얼 히스토리 차트

**API 엔드포인트**:

```typescript
POST / api / v1 / backtests / optimize; // 최적화 시작
GET / api / v1 / backtests / optimize / { study_name }; // 진행 상황
GET / api / v1 / backtests / optimize / { study_name } / result; // 결과 조회
GET / api / v1 / backtests / optimize; // 스터디 목록
```

**프론트엔드 훅**:

```typescript
// ✨ 신규 훅: useOptimization
const {
  studies,             // 최적화 스터디 목록
  studyDetail,         // 스터디 상세 (트라이얼 히스토리)
  startOptimization,   // 최적화 시작
  progress,            // 진행 상황 (%)
  bestParams,          // 최적 파라미터
  isOptimizing,        // 최적화 진행 중
} = useOptimization(studyName?);
```

**UI 컴포넌트**:

1. **OptimizationWizard**: 최적화 파라미터 입력 폼
2. **OptimizationProgress**: 진행률 바 + 실시간 업데이트
3. **TrialHistoryChart**: 트라이얼별 성과 차트
4. **BestParamsPanel**: 최적 파라미터 표시 + 적용 버튼

---

### US-10: 데이터 품질 모니터링 (Phase 2) 🎯 높음

**As a** 운영자  
**I want to** 이상 데이터를 실시간으로 감지  
**So that** ML 모델과 백테스트 신뢰성을 보장할 수 있다

**수락 기준**:

- ✅ 최근 24시간 데이터 품질 알림
- ✅ 심각도별 이벤트 집계 (HIGH/MEDIUM/LOW)
- ✅ 이상 데이터 상세 조회
- ✅ 웹훅 알림 설정

**API 엔드포인트**:

```typescript
GET / api / v1 / dashboard / data - quality - summary; // 품질 요약
```

**프론트엔드 훅**:

```typescript
// ✨ 신규 훅: useDataQuality
const {
  qualitySummary, // 품질 요약 (경보 수, 심각도 분포)
  recentAlerts, // 최근 24시간 알림
  severityStats, // 심각도별 통계
  anomalyDetails, // 이상 데이터 상세
  refreshInterval, // 새로고침 간격
} = useDataQuality();
```

**UI 컴포넌트**:

1. **DataQualityDashboard**: 전체 품질 현황
2. **AlertTimeline**: 시간별 알림 타임라인
3. **SeverityPieChart**: 심각도 분포 파이 차트
4. **AnomalyDetailTable**: 이상 데이터 상세 테이블

---

### US-11: 내러티브 리포트 생성 (Phase 3) 🟡 중간

**As a** 임원  
**I want to** AI가 생성한 자연어 리포트를 확인  
**So that** 비전문가도 백테스트 결과를 이해할 수 있다

**수락 기준**:

- ✅ GPT-4 기반 리포트 생성
- ✅ Executive Summary, Performance Analysis, Strategy Insights
- ✅ Risk Assessment, Market Context, Recommendations
- ✅ PDF/Markdown 내보내기

**API 엔드포인트**:

```typescript
POST / api / v1 / narrative / backtests / { id } / report; // 리포트 생성
```

**프론트엔드 훅**:

```typescript
// ✨ 신규 훅: useNarrativeReport
const {
  report, // 생성된 리포트 (6개 섹션)
  generateReport, // 리포트 생성 트리거
  isGenerating, // 생성 진행 중
  exportPDF, // PDF 내보내기
  exportMarkdown, // Markdown 내보내기
} = useNarrativeReport(backtestId);
```

**UI 컴포넌트**:

1. **ReportGenerator**: 리포트 생성 버튼 + 옵션
2. **ExecutiveSummaryCard**: 요약 카드
3. **PerformanceAnalysisSection**: 성과 분석 섹션
4. **RecommendationsList**: AI 추천 사항 리스트
5. **ReportExportMenu**: 내보내기 메뉴

---

### US-12: 대화형 전략 빌더 (Phase 3) 🟡 중간

**As a** 초보 트레이더  
**I want to** 자연어로 전략을 설명하면 자동으로 전략을 생성  
**So that** 복잡한 파라미터 설정 없이 전략을 만들 수 있다

**수락 기준**:

- ✅ 자연어 쿼리 입력 (10-1000자)
- ✅ LLM 의도 파싱 (IntentType 분류)
- ✅ 지표 추천 (임베딩 유사도)
- ✅ 파라미터 검증
- ✅ Human-in-the-Loop 승인

**API 엔드포인트**:

```typescript
POST / api / v1 / strategy - builder; // 전략 생성
POST / api / v1 / strategy - builder / approve; // 승인 처리
POST / api / v1 / strategy - builder / search - indicators; // 지표 검색
```

**프론트엔드 훅**:

```typescript
// ✨ 신규 훅: useStrategyBuilder
const {
  buildStrategy, // 전략 생성 함수
  strategyResponse, // 생성된 전략 응답
  parsedIntent, // 파싱된 의도
  generatedStrategy, // 생성된 전략 설정
  approvalRequired, // 승인 필요 여부
  approveStrategy, // 승인 처리
  isBuilding, // 생성 진행 중
} = useStrategyBuilder();
```

**UI 컴포넌트**:

1. **StrategyBuilderChat**: 자연어 입력 폼
2. **IntentParsingResult**: 의도 파싱 결과 표시
3. **IndicatorRecommendations**: 추천 지표 카드
4. **StrategyApprovalDialog**: 승인 다이얼로그
5. **GeneratedStrategyPreview**: 생성된 전략 미리보기

---

### US-13: ChatOps 시스템 점검 (Phase 3) 🟡 중간

**As a** 운영자  
**I want to** 대화형 인터페이스로 시스템 상태를 조회  
**So that** CLI 없이 빠르게 문제를 진단할 수 있다

**수락 기준**:

- ✅ 자연어 쿼리 (예: "DuckDB 캐시 상태는?")
- ✅ Function calling 기반 LLM
- ✅ 시스템 상태, 캐시 통계, Alpha Vantage 헬스체크
- ✅ RBAC 권한 검사

**API 엔드포인트**:

```typescript
POST / api / v1 / chatops; // ChatOps 쿼리
```

**프론트엔드 훅**:

```typescript
// ✨ 신규 훅: useChatOps
const {
  sendQuery, // 쿼리 전송
  chatHistory, // 대화 히스토리
  isProcessing, // 처리 중
  clearHistory, // 히스토리 초기화
} = useChatOps();
```

**UI 컴포넌트**:

1. **ChatOpsInterface**: 채팅 인터페이스
2. **ChatMessageBubble**: 메시지 버블 (사용자/AI)
3. **SystemStatusCard**: 시스템 상태 카드
4. **ChatOpsShortcuts**: 빠른 명령어 버튼

---

### US-14: 멀티턴 대화 전략 상담 (Phase 3 D3) 🟡 중간

**As a** 퀀트 트레이더  
**I want to** AI와 여러 턴에 걸쳐 전략을 상담  
**So that** 맥락을 유지하며 전략을 개선할 수 있다

**수락 기준**:

- ✅ 대화 세션 생성
- ✅ 멀티턴 대화 (OpenAI gpt-4o)
- ✅ 전략 비교 분석 (LLM 기반 순위)
- ✅ 대화 중 백테스트 트리거

**API 엔드포인트**:

```typescript
POST / api / v1 / chatops - advanced / session / create; // 세션 생성
POST / api / v1 / chatops - advanced / session / { id } / chat; // 채팅
POST / api / v1 / chatops - advanced / strategies / compare; // 전략 비교
POST / api / v1 / chatops - advanced / backtest / trigger; // 백테스트 트리거
```

**프론트엔드 훅**:

```typescript
// ✨ 신규 훅: useChatOpsAdvanced
const {
  sessionId, // 현재 세션 ID
  createSession, // 세션 생성
  sendMessage, // 메시지 전송
  conversation, // 대화 히스토리
  compareStrategies, // 전략 비교
  triggerBacktest, // 백테스트 트리거
  isChatting, // 채팅 진행 중
} = useChatOpsAdvanced();
```

**UI 컴포넌트**:

1. **AdvancedChatInterface**: 고급 채팅 인터페이스
2. **SessionManager**: 세션 관리 패널
3. **StrategyComparisonPanel**: 전략 비교 결과
4. **BacktestTriggerButton**: 백테스트 트리거 버튼

---

### US-15: 자동 백테스트 트리거 (Phase 3 D3) 🟡 중간

**As a** 개발자  
**I want to** 대화 중 AI가 제안한 전략을 즉시 백테스트  
**So that** 빠른 피드백 루프를 만들 수 있다

**수락 기준**:

- ✅ 대화 중 백테스트 트리거
- ✅ UUID 기반 백테스트 추적
- ✅ 실행 상태 실시간 업데이트
- ✅ 완료 후 결과 자동 표시

**API 엔드포인트**:

```typescript
POST / api / v1 / chatops - advanced / backtest / trigger; // 백테스트 트리거
```

**프론트엔드 훅**:

```typescript
// ✨ 업데이트: useChatOpsAdvanced (triggerBacktest 포함)
// 위 US-14 참조
```

**UI 컴포넌트**:

1. **BacktestTriggerCard**: 백테스트 트리거 카드 (대화 내)
2. **BacktestProgressIndicator**: 진행률 표시
3. **BacktestResultPreview**: 결과 미리보기 (대화 내 임베드)

---

### US-16: 피처 스토어 탐색 (Phase 4 D1) 🎯 높음

**As a** 데이터 과학자  
**I want to** ML 피처의 버전을 관리하고 조회  
**So that** 일관된 피처로 모델을 학습할 수 있다

**수락 기준**:

- ✅ 피처 버전 목록 조회
- ✅ 피처 메타데이터 확인
- ✅ 심볼별 피처 데이터 조회
- ✅ 피처 의존성 그래프

**API 엔드포인트**:

```typescript
GET / api / v1 / features / { version } / { symbol }; // 피처 데이터
GET / api / v1 / features / metadata; // 피처 메타데이터
```

**프론트엔드 훅**:

```typescript
// ✨ 신규 훅: useFeatureStore
const {
  features,            // 피처 목록
  featureMetadata,     // 피처 메타데이터
  getFeatureData,      // 피처 데이터 조회
  featureVersions,     // 버전 목록
  loading,
} = useFeatureStore(version?, symbol?);
```

**UI 컴포넌트**:

1. **FeatureStoreExplorer**: 피처 탐색 인터페이스
2. **FeatureMetadataPanel**: 메타데이터 패널
3. **FeatureVersionSelector**: 버전 선택 드롭다운
4. **FeatureDependencyGraph**: 의존성 그래프

---

### US-17: 모델 라이프사이클 관리 (Phase 4 D2) 🎯 높음

**As a** ML 엔지니어  
**I want to** 모델 실험을 추적하고 배포 관리  
**So that** 모델 거버넌스를 강화할 수 있다

**수락 기준**:

- ✅ 실험 목록 조회
- ✅ 모델 버전 관리
- ✅ 드리프트 이벤트 감지
- ✅ 배포 체크리스트

**API 엔드포인트**:

```typescript
GET / api / v1 / ml / experiments; // 실험 목록
GET / api / v1 / ml / runs; // 실행 목록
GET / api / v1 / ml / models; // 모델 버전
GET / api / v1 / ml / drift - events; // 드리프트 이벤트
```

**프론트엔드 훅**:

```typescript
// ✨ 신규 훅: useModelLifecycle
const {
  experiments, // 실험 목록
  runs, // 실행 목록
  modelVersions, // 모델 버전 목록
  driftEvents, // 드리프트 이벤트
  deployModel, // 모델 배포
  archiveModel, // 모델 아카이브
} = useModelLifecycle();
```

**UI 컴포넌트**:

1. **ExperimentsDashboard**: 실험 대시보드
2. **ModelVersionTable**: 모델 버전 테이블
3. **DriftEventTimeline**: 드리프트 타임라인
4. **DeploymentChecklist**: 배포 체크리스트

---

### US-18: 모델 성능 평가 (Phase 4 D3) 🟡 중간

**As a** ML 엔지니어  
**I want to** 벤치마크 스위트로 모델을 검증  
**So that** 프로덕션 배포 전 품질을 보장할 수 있다

**수락 기준**:

- ✅ 평가 시나리오 목록
- ✅ 평가 실행 트리거
- ✅ 결과 비교 (여러 모델)
- ✅ SHAP values, Feature importance

**API 엔드포인트**:

```typescript
GET / api / v1 / evaluation / scenarios; // 시나리오 목록
POST / api / v1 / evaluation / runs; // 평가 실행
GET / api / v1 / evaluation / runs; // 실행 목록
```

**프론트엔드 훅**:

```typescript
// ✨ 신규 훅: useEvaluationHarness
const {
  scenarios,           // 시나리오 목록
  evaluationRuns,      // 평가 실행 목록
  runEvaluation,       // 평가 실행 트리거
  evaluationResults,   // 평가 결과
  shap Values,         // SHAP 설명
  loading,
} = useEvaluationHarness();
```

**UI 컴포넌트**:

1. **EvaluationScenarios**: 시나리오 선택 인터페이스
2. **EvaluationResults**: 결과 비교 테이블
3. **SHAPChart**: SHAP values 차트
4. **FeatureImportanceChart**: 피처 중요도 차트

---

### US-19: 프롬프트 템플릿 관리 (Phase 4 D4) 🟡 중간

**As a** AI 엔지니어  
**I want to** LLM 프롬프트를 버전 관리  
**So that** 프롬프트 품질을 추적하고 개선할 수 있다

**수락 기준**:

- ✅ 프롬프트 템플릿 목록
- ✅ 버전 히스토리
- ✅ A/B 테스트 결과
- ✅ 승인 워크플로우

**API 엔드포인트**:

```typescript
GET / api / v1 / prompt - governance / templates; // 템플릿 목록
POST / api / v1 / prompt - governance / templates; // 템플릿 생성
GET / api / v1 / prompt - governance / templates / { id }; // 템플릿 상세
PUT / api / v1 / prompt - governance / templates / { id }; // 템플릿 업데이트
```

**프론트엔드 훅**:

```typescript
// ✨ 신규 훅: usePromptGovernance
const {
  templates,           // 템플릿 목록
  templateDetail,      // 템플릿 상세
  createTemplate,      // 템플릿 생성
  updateTemplate,      // 템플릿 업데이트
  abTestResults,       // A/B 테스트 결과
  approveTemplate,     // 템플릿 승인
} = usePromptGovernance(templateId?);
```

**UI 컴포넌트**:

1. **PromptTemplateList**: 템플릿 목록
2. **PromptEditor**: 프롬프트 에디터 (Monaco)
3. **VersionHistory**: 버전 히스토리
4. **ABTestResults**: A/B 테스트 결과 차트

---

## 🛠️ 프론트엔드 작업 계획

### Phase 1: 기존 훅 업데이트 및 신규 훅 구축 (우선순위 높음)

#### 1.1 기존 훅 업데이트 (2-3일)

**목표**: 기존 백테스트/전략 훅을 AI Integration에 맞게 확장

```typescript
// ✏️ 업데이트: useBacktest
// 현재: 기본 CRUD만 지원
// 추가: ML 신호, 국면 정보, 최적화 연동

const useBacktest = (backtestId?: string) => {
  // 기존 기능
  const { backtestList, createBacktest, backtest } = useBacktestBase();

  // ✨ 신규 추가
  const { mlSignals } = useMLModel(); // ML 신호 연동
  const { regime } = useRegimeDetection(); // 국면 정보 연동
  const { forecast } = usePortfolioForecast(); // 예측 연동

  return {
    // 기존
    backtestList,
    createBacktest,
    backtest,
    portfolioHistory,
    tradesHistory,

    // 신규
    mlSignals, // ML 신호 데이터
    currentRegime, // 현재 국면
    forecastData, // 예측 데이터
  };
};
```

**작업 항목**:

- [ ] `useBacktest` 확장: ML 신호, 국면, 예측 통합
- [ ] `useStrategy` 확장: 전략 빌더 연동
- [ ] `useMarketData` 확장: 데이터 품질 정보 추가

#### 1.2 Phase 1 신규 훅 구축 (5-7일) 🎯

**US-6: `useMLModel`** (2일)

```typescript
frontend / src / hooks / useMLModel.ts; // 350+ lines
frontend / src / client / services.gen.ts; // 자동 생성 (MLService)
```

**주요 기능**:

- 모델 목록 조회 (`useQuery`)
- 모델 상세 정보 (`useQuery` with caching)
- 모델 비교 (`useQuery` with multiple keys)
- 모델 학습 트리거 (`useMutation` background task)
- 모델 삭제 (`useMutation` with invalidation)

**의존성**:

- TanStack Query v5
- OpenAPI 클라이언트 (`GET /api/v1/ml/models`)
- React Context (선택적 global state)

---

**US-7: `useRegimeDetection`** (1.5일)

```typescript
frontend / src / hooks / useRegimeDetection.ts; // 200+ lines
```

**주요 기능**:

- 현재 국면 조회 (폴링 또는 WebSocket)
- 국면 히스토리 시계열 (`useQuery`)
- 심볼별 국면 비교 (parallel queries)

**의존성**:

- Recharts (시계열 차트)
- Date-fns (날짜 처리)

---

**US-8: `usePortfolioForecast`** (2.5일)

```typescript
frontend / src / hooks / usePortfolioForecast.ts; // 280+ lines
```

**주요 기능**:

- 예측 데이터 조회 (퍼센타일 밴드)
- 시나리오 분석 (낙관/중립/비관)
- VaR, CVaR 계산 (클라이언트 사이드)
- 예측 기간 변경 (reactive)

**의존성**:

- D3.js 또는 Recharts (신뢰구간 차트)
- Lodash (통계 계산)

---

### Phase 2: 최적화 및 데이터 품질 훅 (우선순위 높음)

#### 2.1 Phase 2 신규 훅 구축 (4-5일) 🎯

**US-9: `useOptimization`** (2.5일)

```typescript
frontend / src / hooks / useOptimization.ts; // 320+ lines
```

**주요 기능**:

- 최적화 스터디 생성 (`useMutation`)
- 진행 상황 폴링 (`useQuery` with refetchInterval)
- 트라이얼 히스토리 조회
- 최적 파라미터 적용

**의존성**:

- React Query polling
- Progress bar 컴포넌트

---

**US-10: `useDataQuality`** (1.5일)

```typescript
frontend / src / hooks / useDataQuality.ts; // 220+ lines
```

**주요 기능**:

- 품질 요약 조회 (자동 새로고침)
- 최근 알림 목록
- 심각도별 통계

**의존성**:

- Auto-refresh (SWR 패턴)
- Notification 시스템 연동

---

### Phase 3: 생성형 AI 훅 (우선순위 중간)

#### 3.1 Phase 3 신규 훅 구축 (6-8일) 🟡

**US-11: `useNarrativeReport`** (2일)

```typescript
frontend / src / hooks / useNarrativeReport.ts; // 250+ lines
```

**주요 기능**:

- 리포트 생성 트리거 (Background Task)
- 리포트 섹션별 렌더링
- PDF/Markdown 내보내기

**의존성**:

- React-Markdown (Markdown 렌더링)
- jsPDF (PDF 생성)

---

**US-12: `useStrategyBuilder`** (2.5일)

```typescript
frontend / src / hooks / useStrategyBuilder.ts; // 350+ lines
```

**주요 기능**:

- 전략 생성 (`useMutation`)
- 의도 파싱 결과 처리
- 지표 검색 (디바운싱)
- 승인 워크플로우

**의존성**:

- Debounce (lodash)
- Form validation (React Hook Form)

---

**US-13: `useChatOps`** (1.5일)

```typescript
frontend / src / hooks / useChatOps.ts; // 200+ lines
```

**주요 기능**:

- 쿼리 전송
- 대화 히스토리 관리
- 시스템 상태 파싱

---

**US-14/15: `useChatOpsAdvanced`** (2일)

```typescript
frontend / src / hooks / useChatOpsAdvanced.ts; // 320+ lines
```

**주요 기능**:

- 세션 관리
- 멀티턴 대화
- 전략 비교
- 백테스트 트리거

**의존성**:

- WebSocket (선택적, 실시간 채팅)
- Session storage (세션 영속화)

---

### Phase 4: MLOps 훅 (우선순위 높음 + 중간)

#### 4.1 Phase 4 신규 훅 구축 (7-9일)

**US-16: `useFeatureStore`** (2일) 🎯

```typescript
frontend / src / hooks / useFeatureStore.ts; // 280+ lines
```

---

**US-17: `useModelLifecycle`** (2.5일) 🎯

```typescript
frontend / src / hooks / useModelLifecycle.ts; // 350+ lines
```

---

**US-18: `useEvaluationHarness`** (1.5일) 🟡

```typescript
frontend / src / hooks / useEvaluationHarness.ts; // 240+ lines
```

---

**US-19: `usePromptGovernance`** (1일) 🟡

```typescript
frontend / src / hooks / usePromptGovernance.ts; // 200+ lines
```

---

## 📅 전체 작업 타임라인

### Sprint 1: Phase 1 핵심 훅 (2주)

- Week 1: `useMLModel`, `useRegimeDetection` 완성
- Week 2: `usePortfolioForecast`, 기존 훅 통합

### Sprint 2: Phase 2 최적화 (1주)

- Week 3: `useOptimization`, `useDataQuality` 완성

### Sprint 3: Phase 3 생성형 AI (2주)

- Week 4: `useNarrativeReport`, `useStrategyBuilder`
- Week 5: `useChatOps`, `useChatOpsAdvanced`

### Sprint 4: Phase 4 MLOps (2주)

- Week 6: `useFeatureStore`, `useModelLifecycle`
- Week 7: `useEvaluationHarness`, `usePromptGovernance`

**총 예상 기간**: 7주 (1인 기준)

---

## 🎯 우선순위 매트릭스

### 높음 (즉시 착수) 🔴

1. `useMLModel` - ML 신호 활용 (US-6)
2. `useRegimeDetection` - 시장 국면 (US-7)
3. `usePortfolioForecast` - 확률 예측 (US-8)
4. `useOptimization` - 자동 최적화 (US-9)
5. `useDataQuality` - 데이터 품질 (US-10)
6. `useFeatureStore` - 피처 스토어 (US-16)
7. `useModelLifecycle` - 모델 관리 (US-17)

### 중간 (순차 진행) 🟡

8. `useNarrativeReport` - 내러티브 리포트 (US-11)
9. `useStrategyBuilder` - 전략 빌더 (US-12)
10. `useChatOps` - ChatOps 기본 (US-13)
11. `useChatOpsAdvanced` - ChatOps 고급 (US-14/15)
12. `useEvaluationHarness` - 평가 하니스 (US-18)
13. `usePromptGovernance` - 프롬프트 관리 (US-19)

---

## 🛠️ 기술 스택 및 의존성

### 필수 라이브러리

```json
{
  "@tanstack/react-query": "^5.0.0",
  "@hey-api/openapi-ts": "^0.x",
  "recharts": "^2.x",
  "d3": "^7.x",
  "react-markdown": "^9.x",
  "jspdf": "^2.x",
  "lodash": "^4.x",
  "date-fns": "^3.x"
}
```

### 선택적 라이브러리

```json
{
  "socket.io-client": "^4.x", // WebSocket
  "monaco-editor": "^0.x", // 코드 에디터
  "react-hook-form": "^7.x", // 폼 관리
  "zustand": "^4.x" // 전역 상태 (선택)
}
```

---

## 📝 다음 단계

1. **OpenAPI 클라이언트 재생성** ✅ (이미 완료)

   ```bash
   pnpm gen:client
   ```

2. **Sprint 1 착수**: `useMLModel` 구현 시작

   ```bash
   cd frontend/src/hooks
   touch useMLModel.ts
   ```

3. **컴포넌트 스토리북 준비**

   ```bash
   pnpm add -D @storybook/react
   ```

4. **E2E 테스트 설정**
   ```bash
   pnpm add -D @playwright/test
   ```

---

## 🔗 참고 문서

- [ARCHITECTURE.md](../../backend/strategy_backtest/ARCHITECTURE.md)
- [PROJECT_DASHBOARD.md](../../backend/ai_integration/PROJECT_DASHBOARD.md)
- [Backend AGENTS.md](../../../backend/AGENTS.md)
- [Frontend AGENTS.md](../../../frontend/AGENTS.md)
