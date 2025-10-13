# Phase 3: 생성형 AI & ChatOps 구현 계획

> **기간**: 2025-11-05 ~ 2025-11-19 (2주)  
> **우선순위**: 🟡 중간  
> **목표**: 내러티브 리포트 + 대화형 전략 빌더 + ChatOps  
> **Backend API**: 7개 엔드포인트 (100% 완료)

---

## 📋 Phase 3 개요

### 비즈니스 가치

사용자가 **GPT-4 기반 내러티브 리포트**로 백테스트 인사이트를 자연어로 이해하고,
**대화형 전략 빌더**로 코드 작성 없이 전략을 생성하며, **ChatOps**로 시스템
상태를 대화형으로 조회할 수 있습니다.

### 주요 산출물

- ✅ **4개 신규 Custom Hooks**: useNarrativeReport, useStrategyBuilder,
  useChatOps, useChatOpsAdvanced
- ✅ **18개 UI 컴포넌트**: 리포트 5개, 빌더 5개, ChatOps 8개
- ✅ **7개 API 엔드포인트 연동**: 리포트 1개, 빌더 3개, ChatOps 1개, 고급
  ChatOps 4개
- ✅ **3개 신규 페이지**: `/backtests/{id}/report`, `/strategy-builder`,
  `/chatops`

### 성공 지표 (KPI)

**기술 메트릭**:

- API 엔드포인트 연동: **20/32** (Phase 3 완료 시)
- Custom Hooks: **9/13**
- UI 컴포넌트: **38/60**

**성능 메트릭**:

- 내러티브 리포트 생성: **< 10초**
- LLM 응답 (전략 빌더): **< 5초**
- ChatOps 명령 실행: **< 3초**

**비즈니스 메트릭**:

- AI 리포트 생성: **> 20건/월** (Phase 3 종료 시)
- 전략 빌더 사용: **> 25건/월**

---

## 📅 Sprint 계획

### Sprint 4 (Week 4: 2025-11-05 ~ 2025-11-11)

#### Day 18-19 (2025-11-05 ~ 2025-11-06): useNarrativeReport 훅 + 컴포넌트 5개

**목표**: AI 기반 백테스트 리포트 생성 UI 구축

**작업 항목**:

**Day 18 (훅 구현)**:

- [ ] `useNarrativeReport.ts` 파일 생성
- [ ] Query Key 정의
- [ ] `useMutation` 구현:
  - [ ] generateReport (리포트 생성)
  - [ ] regenerateReport (재생성)
- [ ] `useState` 구현:
  - [ ] sections (섹션 데이터)
  - [ ] isGenerating (생성 중 상태)
- [ ] Export 함수 (PDF, JSON)
- [ ] Unit Test 작성

**Day 19 (컴포넌트 5개)**:

- [ ] `ReportViewer.tsx`:
  - [ ] Markdown 렌더링 (react-markdown)
  - [ ] 섹션 네비게이션 (목차)
  - [ ] 다크 모드 지원
- [ ] `SectionRenderer.tsx`:
  - [ ] 섹션별 컴포넌트 (제목, 본문, 차트)
  - [ ] KPI 하이라이트 (Chip)
- [ ] `ExportButton.tsx`:
  - [ ] PDF 내보내기 (jspdf)
  - [ ] JSON 내보내기
  - [ ] 다운로드 진행 상태
- [ ] `ShareDialog.tsx`:
  - [ ] 링크 복사 (클립보드)
  - [ ] 이메일 공유 (mailto)
- [ ] `RegenerationButton.tsx`:
  - [ ] 재생성 버튼 (로딩 스피너)
  - [ ] 확인 다이얼로그

**예상 소요 시간**: 16시간 (2일)  
**담당자**: Frontend 엔지니어  
**참고 문서**:
[AI_INTEGRATION_USER_STORIES.md - US-11](../AI_INTEGRATION_USER_STORIES.md#us-11)

---

#### Day 20-22 (2025-11-07 ~ 2025-11-09): useStrategyBuilder 훅 + 컴포넌트 5개

**목표**: 대화형 전략 빌더 UI 구축

**작업 항목**:

**Day 20 (훅 구현)**:

- [ ] `useStrategyBuilder.ts` 파일 생성
- [ ] Query Key 정의
- [ ] `useMutation` 구현:
  - [ ] parseIntent (의도 파싱)
  - [ ] recommendIndicators (지표 추천)
  - [ ] generateStrategy (전략 생성)
- [ ] `useState` 구현:
  - [ ] conversation (대화 히스토리)
  - [ ] currentIntent (현재 의도)
  - [ ] recommendations (추천 지표)
- [ ] Unit Test 작성

**Day 21-22 (컴포넌트 5개)**:

- [ ] `ConversationInterface.tsx`:
  - [ ] 채팅 UI (메시지 리스트 + 입력창)
  - [ ] 사용자/AI 메시지 구분
  - [ ] 타이핑 애니메이션
- [ ] `IntentParser.tsx`:
  - [ ] 의도 분류 결과 표시 (Chip: BUY_SIGNAL, SELL_SIGNAL 등)
  - [ ] 신뢰도 퍼센트
- [ ] `IndicatorRecommendation.tsx`:
  - [ ] 추천 지표 카드 (RSI, MACD 등)
  - [ ] 설명 툴팁
  - [ ] 선택 체크박스
- [ ] `StrategyPreview.tsx`:
  - [ ] Monaco Editor 통합 (Python 코드)
  - [ ] 읽기 전용 모드
  - [ ] 코드 복사 버튼
- [ ] `ValidationFeedback.tsx`:
  - [ ] 검증 상태 (SUCCESS, WARNING, ERROR)
  - [ ] 피드백 메시지
  - [ ] 수정 제안

**예상 소요 시간**: 20시간 (2.5일)  
**담당자**: Frontend 엔지니어  
**참고 문서**:
[AI_INTEGRATION_USER_STORIES.md - US-12](../AI_INTEGRATION_USER_STORIES.md#us-12)

---

### Sprint 5 (Week 5: 2025-11-12 ~ 2025-11-19)

#### Day 23-24 (2025-11-12 ~ 2025-11-13): useChatOps 훅 + 컴포넌트 4개

**목표**: ChatOps 시스템 점검 UI 구축

**작업 항목**:

**Day 23 (훅 구현)**:

- [ ] `useChatOps.ts` 파일 생성
- [ ] Query Key 정의
- [ ] `useMutation` 구현:
  - [ ] sendCommand (명령 전송)
- [ ] `useState` 구현:
  - [ ] messages (메시지 히스토리)
  - [ ] connectionStatus (연결 상태)
- [ ] Unit Test 작성

**Day 24 (컴포넌트 4개)**:

- [ ] `ChatInterface.tsx`:
  - [ ] 전체 레이아웃 (메시지 리스트 + 입력창)
  - [ ] 연결 상태 표시 (🟢 Connected, 🔴 Disconnected)
- [ ] `MessageList.tsx`:
  - [ ] 메시지 스크롤 (자동 스크롤 to bottom)
  - [ ] 시스템/사용자 메시지 구분
  - [ ] 타임스탬프
- [ ] `CommandInput.tsx`:
  - [ ] 자동완성 (명령어 제안)
  - [ ] Enter 키 전송
  - [ ] 로딩 스피너
- [ ] `StatusCard.tsx`:
  - [ ] 시스템 상태 요약 (DuckDB, MongoDB, Alpha Vantage)
  - [ ] 상태 아이콘 (✅ Healthy, ⚠️ Warning, ❌ Error)
  - [ ] 상세 정보 툴팁

**예상 소요 시간**: 12시간 (1.5일 + 1일)  
**담당자**: Frontend 엔지니어  
**참고 문서**:
[AI_INTEGRATION_USER_STORIES.md - US-13](../AI_INTEGRATION_USER_STORIES.md#us-13)

---

#### Day 25-26 (2025-11-14 ~ 2025-11-15): useChatOpsAdvanced 훅 + 컴포넌트 4개

**목표**: ChatOps 고급 기능 (멀티턴 대화, 전략 비교, 자동 백테스트) UI 구축

**작업 항목**:

**Day 25 (훅 구현)**:

- [ ] `useChatOpsAdvanced.ts` 파일 생성
- [ ] Query Key 정의
- [ ] `useMutation` 구현:
  - [ ] createSession (세션 생성)
  - [ ] sendChatMessage (멀티턴 대화)
  - [ ] compareStrategies (전략 비교)
  - [ ] triggerBacktest (자동 백테스트)
- [ ] `useState` 구현:
  - [ ] sessions (세션 목록)
  - [ ] currentSession (현재 세션)
  - [ ] comparisonResults (비교 결과)
- [ ] Unit Test 작성

**Day 26 (컴포넌트 4개)**:

- [ ] `SessionManager.tsx`:
  - [ ] 세션 목록 (사이드바)
  - [ ] 세션 생성/삭제 버튼
  - [ ] 활성 세션 하이라이트
- [ ] `StrategyComparison.tsx`:
  - [ ] 비교 테이블 (전략별 컬럼)
  - [ ] 메트릭 하이라이트 (최고 성능)
  - [ ] LLM 분석 결과 (Markdown)
- [ ] `AutoBacktestTrigger.tsx`:
  - [ ] 백테스트 설정 입력 (간단한 폼)
  - [ ] 트리거 버튼
  - [ ] 생성된 백테스트 ID 표시 (링크)
- [ ] `ConversationHistory.tsx`:
  - [ ] 대화 히스토리 (접을 수 있는 리스트)
  - [ ] 턴별 구분 (사용자 질문 → AI 응답)
  - [ ] 검색 기능

**예상 소요 시간**: 16시간 (2일)  
**담당자**: Frontend 엔지니어  
**참고 문서**:
[AI_INTEGRATION_USER_STORIES.md - US-14, US-15](../AI_INTEGRATION_USER_STORIES.md#us-14)

---

#### Day 27-28 (2025-11-16 ~ 2025-11-19): Phase 3 통합 테스트 및 리뷰

**목표**: Phase 3 산출물 검증, KPI 평가, Phase 4 착수 준비

**작업 항목**:

**Day 27 (통합 테스트)**:

- [ ] E2E 테스트 (Playwright):
  - [ ] 내러티브 리포트 생성 (< 10초)
  - [ ] 전략 빌더 대화 플로우
  - [ ] ChatOps 명령 실행 (< 3초)
  - [ ] 멀티턴 대화 및 전략 비교
- [ ] 성능 프로파일링:
  - [ ] LLM 응답 시간 (< 5초)
  - [ ] PDF 생성 시간 (< 3초)
- [ ] 에러 처리 검증:
  - [ ] LLM 타임아웃 (10초)
  - [ ] WebSocket 재연결 로직

**Day 28 (리뷰 및 문서화)**:

- [ ] **체크리스트 검증**:
  - [ ] 4개 신규 훅 완성 ✅
  - [ ] 18개 UI 컴포넌트 완성 ✅
  - [ ] 7개 API 엔드포인트 연동 ✅
  - [ ] TypeScript/ESLint 에러 0개 ✅
  - [ ] Unit Test 커버리지 78%+ ✅
- [ ] **KPI 평가**:
  - [ ] 리포트 생성 < 10초 ✅
  - [ ] LLM 응답 < 5초 ✅
  - [ ] ChatOps 명령 < 3초 ✅
- [ ] **Phase 3 리뷰 미팅** (오후 2시, 1시간):
  - [ ] 데모 (리포트, 전략 빌더, ChatOps)
  - [ ] KPI 결과 공유
  - [ ] 피드백 수집
  - [ ] Phase 4 착수 승인
- [ ] **문서 업데이트**:
  - [ ] PROJECT_DASHBOARD.md (진행률 업데이트)
  - [ ] Phase 3 완료 리포트 작성

**예상 소요 시간**: 16시간 (2일 × 2)  
**담당자**: 전체 팀

---

## 🛠️ 기술 스택 (Phase 3)

### 필수 라이브러리

| 라이브러리           | 버전   | 용도                    |
| -------------------- | ------ | ----------------------- |
| react-markdown       | ^9.0.0 | 내러티브 리포트 렌더링  |
| jspdf                | ^2.5.0 | PDF 내보내기            |
| socket.io-client     | ^4.7.0 | 실시간 통신 (ChatOps)   |
| @monaco-editor/react | ^4.6.0 | 코드 에디터 (전략 빌더) |

### 설치 명령어

```bash
cd frontend
pnpm add react-markdown jspdf socket.io-client @monaco-editor/react
```

---

## 📊 Backend API 명세 (Phase 3)

### 내러티브 리포트 API (1개)

| 메서드 | 엔드포인트                                | 설명        | 응답 시간 목표 |
| ------ | ----------------------------------------- | ----------- | -------------- |
| POST   | `/api/v1/narrative/backtests/{id}/report` | 리포트 생성 | < 10초         |

### 전략 빌더 API (3개)

| 메서드 | 엔드포인트                 | 설명      | 응답 시간 목표 |
| ------ | -------------------------- | --------- | -------------- |
| POST   | `/api/v1/strategy-builder` | 의도 파싱 | < 3초          |
| POST   | `/api/v1/strategy-builder` | 지표 추천 | < 5초          |
| POST   | `/api/v1/strategy-builder` | 전략 생성 | < 5초          |

### ChatOps API (1개)

| 메서드 | 엔드포인트        | 설명      | 응답 시간 목표 |
| ------ | ----------------- | --------- | -------------- |
| POST   | `/api/v1/chatops` | 명령 실행 | < 3초          |

### ChatOps 고급 API (4개)

| 메서드 | 엔드포인트                                            | 설명          | 응답 시간 목표 |
| ------ | ----------------------------------------------------- | ------------- | -------------- |
| POST   | `/api/v1/chatops-advanced/sessions`                   | 세션 생성     | < 1초          |
| POST   | `/api/v1/chatops-advanced/sessions/{session_id}/chat` | 멀티턴 대화   | < 5초          |
| POST   | `/api/v1/chatops-advanced/strategies/compare`         | 전략 비교     | < 8초          |
| POST   | `/api/v1/chatops-advanced/backtests/trigger`          | 자동 백테스트 | < 3초          |

**총 7개 API 엔드포인트** (Phase 3 누적: 20개)

---

## 🎯 Custom Hooks 상세 명세

### 1. useNarrativeReport

```typescript
export const useNarrativeReport = (backtestId: string) => {
  const { showSuccess, showError } = useSnackbar();
  const [sections, setSections] = useState<ReportSection[]>([]);

  const generateMutation = useMutation({
    mutationFn: () => NarrativeService.generateReport({ backtestId }),
    onSuccess: (response) => {
      setSections(response.data.sections);
      showSuccess("리포트가 생성되었습니다");
    },
    onError: () => showError("리포트 생성 실패"),
  });

  const regenerateMutation = useMutation({
    mutationFn: () => NarrativeService.regenerateReport({ backtestId }),
    onSuccess: (response) => {
      setSections(response.data.sections);
      showSuccess("리포트가 재생성되었습니다");
    },
  });

  const exportPDF = async () => {
    const doc = new jsPDF();
    // PDF 생성 로직
    doc.save(`backtest-report-${backtestId}.pdf`);
    showSuccess("PDF가 다운로드되었습니다");
  };

  return {
    sections,
    generateReport: generateMutation.mutate,
    regenerateReport: regenerateMutation.mutate,
    exportPDF,
    isGenerating: generateMutation.isPending || regenerateMutation.isPending,
    error: generateMutation.error,
  };
};
```

### 2. useStrategyBuilder

```typescript
export const useStrategyBuilder = () => {
  const [conversation, setConversation] = useState<ConversationTurn[]>([]);
  const [currentIntent, setCurrentIntent] = useState<IntentResponse | null>(
    null
  );
  const [recommendations, setRecommendations] = useState<
    IndicatorRecommendation[]
  >([]);

  const parseIntentMutation = useMutation({
    mutationFn: (input: string) =>
      StrategyBuilderService.parseIntent({ body: { input } }),
    onSuccess: (response) => {
      setCurrentIntent(response.data);
      setConversation((prev) => [
        ...prev,
        { role: "user", content: input },
        { role: "ai", content: response.data.intent_type },
      ]);
    },
  });

  const recommendMutation = useMutation({
    mutationFn: (intent: IntentType) =>
      StrategyBuilderService.recommendIndicators({ body: { intent } }),
    onSuccess: (response) => {
      setRecommendations(response.data.indicators);
    },
  });

  const generateMutation = useMutation({
    mutationFn: (params: StrategyGenerationParams) =>
      StrategyBuilderService.generateStrategy({ body: params }),
    onSuccess: (response) => {
      setConversation((prev) => [
        ...prev,
        { role: "ai", content: response.data.code },
      ]);
    },
  });

  return {
    conversation,
    currentIntent,
    recommendations,
    parseIntent: parseIntentMutation.mutate,
    recommendIndicators: recommendMutation.mutate,
    generateStrategy: generateMutation.mutate,
    isProcessing:
      parseIntentMutation.isPending ||
      recommendMutation.isPending ||
      generateMutation.isPending,
  };
};
```

### 3. useChatOps

```typescript
export const useChatOps = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [connectionStatus, setConnectionStatus] = useState<
    "connected" | "disconnected"
  >("connected");

  const sendCommandMutation = useMutation({
    mutationFn: (command: string) =>
      ChatOpsService.sendCommand({ body: { command } }),
    onSuccess: (response) => {
      setMessages((prev) => [
        ...prev,
        { role: "user", content: command },
        { role: "system", content: response.data.result },
      ]);
    },
  });

  return {
    messages,
    connectionStatus,
    sendCommand: sendCommandMutation.mutate,
    isSending: sendCommandMutation.isPending,
  };
};
```

### 4. useChatOpsAdvanced

```typescript
export const useChatOpsAdvanced = () => {
  const queryClient = useQueryClient();
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSession, setCurrentSession] = useState<string | null>(null);

  const createSessionMutation = useMutation({
    mutationFn: () => ChatOpsAdvancedService.createSession(),
    onSuccess: (response) => {
      setSessions((prev) => [...prev, response.data]);
      setCurrentSession(response.data.session_id);
    },
  });

  const sendChatMutation = useMutation({
    mutationFn: ({
      sessionId,
      message,
    }: {
      sessionId: string;
      message: string;
    }) => ChatOpsAdvancedService.sendChat({ sessionId, body: { message } }),
  });

  const compareStrategiesMutation = useMutation({
    mutationFn: (strategyIds: string[]) =>
      ChatOpsAdvancedService.compareStrategies({
        body: { strategy_ids: strategyIds },
      }),
  });

  const triggerBacktestMutation = useMutation({
    mutationFn: (config: BacktestConfig) =>
      ChatOpsAdvancedService.triggerBacktest({ body: config }),
  });

  return {
    sessions,
    currentSession,
    createSession: createSessionMutation.mutate,
    sendChat: sendChatMutation.mutate,
    compareStrategies: compareStrategiesMutation.mutate,
    triggerBacktest: triggerBacktestMutation.mutate,
    comparisonResults: compareStrategiesMutation.data,
  };
};
```

---

## 🧪 테스트 전략

### Unit Tests

**useNarrativeReport.test.ts**:

- [ ] generateReport 성공 → sections 업데이트
- [ ] regenerateReport 성공 → sections 업데이트
- [ ] exportPDF 호출 → jsPDF 다운로드
- [ ] LLM 타임아웃 에러 처리

### E2E Tests (Playwright)

**narrative-report.spec.ts**:

```typescript
test("내러티브 리포트 생성 및 PDF 내보내기", async ({ page }) => {
  await page.goto("/backtests/123/report");
  await page.click('button:has-text("리포트 생성")');

  // 로딩 표시 확인
  await expect(page.locator('[data-testid="report-loading"]')).toBeVisible();

  // 리포트 생성 (< 10초)
  const startTime = Date.now();
  await page.waitForSelector('[data-testid="report-viewer"]', {
    timeout: 10000,
  });
  const loadTime = Date.now() - startTime;
  expect(loadTime).toBeLessThan(10000);

  // PDF 내보내기
  const [download] = await Promise.all([
    page.waitForEvent("download"),
    page.click('button:has-text("PDF 내보내기")'),
  ]);
  expect(download.suggestedFilename()).toContain("backtest-report-123.pdf");
});
```

---

## 🚨 위험 및 대응

| 위험                          | 영향                            | 가능성 | 대응 전략                                                     |
| ----------------------------- | ------------------------------- | ------ | ------------------------------------------------------------- |
| LLM 응답 지연 (> 10초)        | 사용자 대기 시간 증가, 타임아웃 | 높음   | 로딩 스피너, 진행률 표시, 타임아웃 10초, 에러 처리            |
| PDF 생성 실패 (jspdf 에러)    | 리포트 내보내기 불가            | 중간   | 에러 바운더리, JSON 내보내기 폴백, 브라우저 호환성 테스트     |
| WebSocket 연결 끊김 (ChatOps) | 실시간 채팅 중단                | 중간   | 재연결 로직 (최대 5회), 폴백 API (Long Polling), 연결 상태 UI |
| Monaco Editor 번들 크기       | 초기 로딩 시간 증가             | 낮음   | 코드 스플리팅 (dynamic import), lazy loading                  |

---

## 📚 참고 문서

- **유저 스토리**:
  [AI_INTEGRATION_USER_STORIES.md](../AI_INTEGRATION_USER_STORIES.md) (US-11,
  US-12, US-13, US-14, US-15)
- **Master Plan**: [MASTER_PLAN.md](../MASTER_PLAN.md)
- **프로젝트 대시보드**: [PROJECT_DASHBOARD.md](../PROJECT_DASHBOARD.md)
- **Backend 생성형 AI 서비스**:
  [PHASE3_D1/D2/D3_IMPLEMENTATION_REPORT.md](../../../backend/ai_integration/phase3_generative_interfaces/)

---

**작성자**: Frontend Team  
**승인자**: 퀀트 플랫폼 프론트엔드 리드  
**최종 업데이트**: 2025-10-14  
**다음 리뷰**: Phase 3 완료 시 (2025-11-19)
