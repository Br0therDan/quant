# Phase 3 착수: 생성형 AI & ChatOps

## 개요

**Phase**: Phase 3 - 생성형 AI & ChatOps  
**기간**: 2025-10-14 ~ 2025-11-03 (3주)  
**목표**: 내러티브 리포트 생성, 대화형 전략 빌더, ChatOps 인터페이스 구현  
**상태**: 🚀 진행중

## Phase 2 회고

### 주요 성과 ✅

- **useOptimization**: 317 lines, 5초 폴링 로직, 4개 컴포넌트 (1,473 lines)
- **useDataQuality**: 184 lines, 1분 자동 새로고침, 4개 컴포넌트 (1,265 lines)
- **총 코드량**: 3,239 lines (누적 7,929 lines)
- **API 연동**: 13/32 엔드포인트 (41%)
- **TypeScript 에러**: 0개 유지 ✅
- **성능**: 최적화 폴링 5초, 데이터 품질 모니터링 1분 간격

### 교훈

- ✅ **폴링 로직**: useEffect cleanup 패턴 효과적
- ✅ **복잡한 폼**: react-hook-form 생산성 향상
- ✅ **차트 라이브러리**: recharts 안정적
- ⚠️ **MUI 업그레이드**: @mui/lab 별도 설치 필요 (Timeline)

## Phase 3 목표

### 핵심 산출물

| 산출물                                    | 예상 공수 | 우선순위 | 상태    |
| ----------------------------------------- | --------- | -------- | ------- |
| useNarrativeReport 훅                     | 2일       | P0       | 🚀 시작 |
| ReportViewer 컴포넌트 세트 (5개)          | 2일       | P0       | 🚀 시작 |
| useStrategyBuilder 훅                     | 2.5일     | P0       | 🚀 시작 |
| ConversationInterface 컴포넌트 세트 (5개) | 1.5일     | P0       | 🚀 시작 |
| useChatOps 훅                             | 1.5일     | P1       | ⏸️ 대기 |
| ChatInterface 컴포넌트 세트 (4개)         | 1일       | P1       | ⏸️ 대기 |
| useChatOpsAdvanced 훅                     | 2일       | P1       | ⏸️ 대기 |
| Advanced ChatOps 컴포넌트 세트 (4개)      | 1일       | P1       | ⏸️ 대기 |

### 기술 스택 추가

```bash
# 필수 라이브러리 설치
cd frontend
pnpm add react-markdown jspdf socket.io-client @monaco-editor/react
pnpm add -D @types/react-markdown
```

**라이브러리 상세:**

- **react-markdown**: 내러티브 리포트 Markdown 렌더링
- **jspdf**: PDF 내보내기
- **socket.io-client**: 실시간 ChatOps 통신
- **@monaco-editor/react**: 코드 에디터 (전략 빌더)

## Week 1: 내러티브 리포트 (Day 1-5)

### useNarrativeReport 훅 인터페이스

```typescript
interface NarrativeReport {
  id: string;
  title: string;
  sections: ReportSection[];
  generated_at: string;
  metadata: Record<string, any>;
}

interface ReportSection {
  type: "summary" | "analysis" | "recommendation" | "chart" | "table";
  title: string;
  content: string;
  data?: any;
}

// 훅 함수
const {
  // 상태
  report, // 현재 리포트
  sections, // 섹션 목록
  isGenerating, // 생성 중 여부
  isExporting, // PDF 내보내기 중

  // 액션
  generateReport, // 새 리포트 생성
  regenerateReport, // 리포트 재생성
  exportPDF, // PDF 내보내기
  shareReport, // 공유 (이메일/Slack)
} = useNarrativeReport(backtestId);
```

### 컴포넌트 구조

```
components/narrative-report/
├── ReportViewer.tsx              (메인 뷰어, 350 lines)
├── SectionRenderer.tsx           (섹션 렌더링, 250 lines)
├── ExportButton.tsx              (PDF 내보내기, 150 lines)
├── ShareDialog.tsx               (공유 다이얼로그, 200 lines)
├── RegenerationButton.tsx        (재생성 버튼, 100 lines)
└── index.ts                      (export 통합)
```

### API 엔드포인트 (Backend)

- `POST /api/ai/narrative/generate` - 리포트 생성
- `POST /api/ai/narrative/{id}/regenerate` - 재생성
- `GET /api/ai/narrative/{id}` - 리포트 조회
- `POST /api/ai/narrative/{id}/share` - 공유

### 체크리스트

- [ ] `pnpm add react-markdown jspdf`
- [ ] `frontend/src/hooks/useNarrativeReport.ts` 생성
- [ ] ReportViewer 컴포넌트 (Markdown 렌더링, 차트 임베딩)
- [ ] SectionRenderer 컴포넌트 (타입별 섹션 렌더링)
- [ ] ExportButton 컴포넌트 (jsPDF 통합, 다운로드)
- [ ] ShareDialog 컴포넌트 (이메일/Slack 폼)
- [ ] RegenerationButton 컴포넌트 (로딩 스피너, 에러 처리)
- [ ] API 연동 테스트 (mock data)
- [ ] TypeScript 에러 0개 확인
- [ ] Biome 포맷팅 적용

## Week 2: 대화형 전략 빌더 (Day 6-10)

### useStrategyBuilder 훅 인터페이스

```typescript
interface Conversation {
  id: string;
  messages: Message[];
  strategy?: GeneratedStrategy;
}

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

interface GeneratedStrategy {
  name: string;
  code: string;
  parameters: Record<string, any>;
  indicators: string[];
  validation: ValidationResult;
}

// 훅 함수
const {
  // 상태
  conversation, // 대화 내역
  isGenerating, // 전략 생성 중
  recommendations, // 지표 추천

  // 액션
  sendMessage, // 메시지 전송
  parseIntent, // 의도 파싱
  generateStrategy, // 전략 코드 생성
  validateStrategy, // 전략 검증
} = useStrategyBuilder();
```

### 컴포넌트 구조

```
components/strategy-builder/
├── ConversationInterface.tsx      (메인 인터페이스, 400 lines)
├── IntentParser.tsx               (의도 파싱 UI, 200 lines)
├── IndicatorRecommendation.tsx    (지표 추천 카드, 250 lines)
├── StrategyPreview.tsx            (Monaco Editor, 300 lines)
├── ValidationFeedback.tsx         (검증 결과, 150 lines)
└── index.ts                       (export 통합)
```

### API 엔드포인트 (Backend)

- `POST /api/ai/strategy-builder/message` - 메시지 전송
- `POST /api/ai/strategy-builder/parse-intent` - 의도 파싱
- `POST /api/ai/strategy-builder/recommend` - 지표 추천
- `POST /api/ai/strategy-builder/generate` - 전략 생성
- `POST /api/ai/strategy-builder/validate` - 전략 검증

### 체크리스트

- [ ] `pnpm add @monaco-editor/react`
- [ ] `frontend/src/hooks/useStrategyBuilder.ts` 생성
- [ ] ConversationInterface 컴포넌트 (채팅 UI, 메시지 리스트)
- [ ] IntentParser 컴포넌트 (의도 분류, 엔티티 추출)
- [ ] IndicatorRecommendation 컴포넌트 (지표 카드, 설명)
- [ ] StrategyPreview 컴포넌트 (Monaco Editor, 하이라이팅)
- [ ] ValidationFeedback 컴포넌트 (에러/경고/성공 메시지)
- [ ] API 연동 테스트
- [ ] TypeScript 에러 0개 확인
- [ ] Biome 포맷팅 적용

## Week 3: ChatOps (Day 11-15)

### useChatOps 훅 인터페이스

```typescript
interface ChatSession {
  id: string;
  messages: ChatMessage[];
  status: "active" | "idle" | "processing";
}

interface ChatMessage {
  id: string;
  type: "command" | "response" | "status";
  content: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

// 훅 함수
const {
  // 상태
  sessions, // 채팅 세션 목록
  currentSession, // 현재 세션
  isConnected, // WebSocket 연결 상태

  // 액션
  sendCommand, // 명령어 전송 (/backtest, /optimize, etc.)
  createSession, // 새 세션 생성
  switchSession, // 세션 전환
} = useChatOps();
```

### 컴포넌트 구조

```
components/chatops/
├── ChatInterface.tsx         (메인 인터페이스, 350 lines)
├── MessageList.tsx           (메시지 리스트, 250 lines)
├── CommandInput.tsx          (명령어 입력, 200 lines)
├── StatusCard.tsx            (작업 상태, 150 lines)
├── SessionManager.tsx        (세션 관리, 200 lines)
├── StrategyComparison.tsx    (전략 비교, 250 lines)
├── AutoBacktestTrigger.tsx   (자동 백테스트, 180 lines)
├── ConversationHistory.tsx   (대화 히스토리, 220 lines)
└── index.ts                  (export 통합)
```

### API 엔드포인트 (Backend)

- `WS /api/ai/chatops` - WebSocket 연결
- `POST /api/ai/chatops/command` - 명령어 실행 (폴백)
- `GET /api/ai/chatops/sessions` - 세션 목록
- `POST /api/ai/chatops/sessions` - 세션 생성

### 체크리스트

- [ ] `pnpm add socket.io-client`
- [ ] `frontend/src/hooks/useChatOps.ts` 생성
- [ ] `frontend/src/hooks/useChatOpsAdvanced.ts` 생성
- [ ] ChatInterface 컴포넌트 (WebSocket 연결, 재연결 로직)
- [ ] MessageList 컴포넌트 (가상화 스크롤, 타임스탬프)
- [ ] CommandInput 컴포넌트 (자동완성, 명령어 검증)
- [ ] StatusCard 컴포넌트 (실시간 상태 업데이트)
- [ ] SessionManager, StrategyComparison, AutoBacktestTrigger,
      ConversationHistory (Advanced)
- [ ] WebSocket 재연결 로직 (최대 5회)
- [ ] 에러 바운더리 적용
- [ ] API 연동 테스트
- [ ] TypeScript 에러 0개 확인
- [ ] Biome 포맷팅 적용

## 성능 목표

| 메트릭             | 목표   | 측정 방법                      |
| ------------------ | ------ | ------------------------------ |
| 리포트 생성        | < 10초 | Backend LLM 응답 시간          |
| 전략 빌더 LLM 응답 | < 5초  | API 응답 시간                  |
| WebSocket 재연결   | < 3초  | socket.io 이벤트 로그          |
| PDF 내보내기       | < 2초  | jsPDF 생성 시간                |
| Monaco Editor 로딩 | < 1초  | Dynamic import, code splitting |

## 위험 관리

| 위험                    | 대응 전략                                       |
| ----------------------- | ----------------------------------------------- |
| LLM 응답 지연 (> 10초)  | 로딩 스피너 + 진행률 표시, 타임아웃 설정        |
| WebSocket 연결 불안정   | 재연결 로직 (최대 5회), 폴백 API (Long Polling) |
| Monaco Editor 번들 크기 | Dynamic import, code splitting                  |
| PDF 생성 메모리 누수    | 생성 후 cleanup, 최대 페이지 제한 (50페이지)    |
| 복잡한 대화 상태 관리   | Zustand 스토어, useReducer 패턴                 |

## 일일 진행 계획

### Day 1-2 (10/14-10/15): useNarrativeReport + ReportViewer

- [ ] 라이브러리 설치 (react-markdown, jspdf)
- [ ] useNarrativeReport 훅 (200 lines)
- [ ] ReportViewer 컴포넌트 (350 lines)
- [ ] SectionRenderer 컴포넌트 (250 lines)

### Day 3-4 (10/16-10/17): 리포트 액션 + 내보내기

- [ ] ExportButton 컴포넌트 (jsPDF, 150 lines)
- [ ] ShareDialog 컴포넌트 (200 lines)
- [ ] RegenerationButton 컴포넌트 (100 lines)
- [ ] API 연동 테스트

### Day 5-6 (10/18-10/19): useStrategyBuilder + ConversationInterface

- [ ] @monaco-editor/react 설치
- [ ] useStrategyBuilder 훅 (250 lines)
- [ ] ConversationInterface 컴포넌트 (400 lines)

### Day 7-8 (10/20-10/21): 전략 빌더 컴포넌트

- [ ] IntentParser 컴포넌트 (200 lines)
- [ ] IndicatorRecommendation 컴포넌트 (250 lines)
- [ ] StrategyPreview 컴포넌트 (Monaco, 300 lines)

### Day 9-10 (10/22-10/23): 전략 검증 + 마무리

- [ ] ValidationFeedback 컴포넌트 (150 lines)
- [ ] 전략 빌더 E2E 테스트
- [ ] 문서 업데이트

### Day 11-12 (10/24-10/25): useChatOps + ChatInterface

- [ ] socket.io-client 설치
- [ ] useChatOps 훅 (200 lines)
- [ ] ChatInterface 컴포넌트 (350 lines)
- [ ] MessageList 컴포넌트 (250 lines)

### Day 13-14 (10/26-10/27): ChatOps 고급 기능

- [ ] useChatOpsAdvanced 훅 (250 lines)
- [ ] SessionManager, StrategyComparison, AutoBacktestTrigger (630 lines)
- [ ] WebSocket 재연결 로직

### Day 15 (10/28): Phase 3 마무리

- [ ] E2E 테스트 (리포트, 전략 빌더, ChatOps)
- [ ] 성능 검증 (< 10초, < 5초, < 3초)
- [ ] Phase 3 완료 보고서 작성

## 성공 기준

### 기능 완성도

- ✅ useNarrativeReport, useStrategyBuilder, useChatOps, useChatOpsAdvanced 훅
  완성
- ✅ 18개 컴포넌트 완성 (Report 5개 + Builder 5개 + ChatOps 8개)
- ✅ API 연동 20/32 (63%)

### 코드 품질

- ✅ TypeScript 에러 0개
- ✅ ESLint 경고 0개
- ✅ 테스트 커버리지 78%+

### 성능

- ✅ 리포트 생성 < 10초
- ✅ 전략 빌더 LLM 응답 < 5초
- ✅ WebSocket 재연결 < 3초

### 비즈니스

- ✅ AI 리포트 생성 > 20건/월
- ✅ 전략 빌더 사용 > 25건/월

---

**다음 단계**: useNarrativeReport 훅 작성 시작  
**예상 완료**: 2025-11-03  
**담당**: Frontend Team Phase 3
