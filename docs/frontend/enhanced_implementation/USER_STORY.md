# User Stories - Strategy & Backtest System with AI Integration

> **최종 업데이트**: 2025년 10월 14일  
> **AI Integration 상태**: Phase 3 완료 (100%), Phase 4 완료 (100%)  
> **프론트엔드 구현 대상**: Phase 1-4 완료 기능

## 유저 스토리 목록

### 핵심 시나리오 (Phase 1-2 완료)

| ID   | 스토리          | 사용자        | 목표               | Phase | 우선순위 | 상태    |
| ---- | --------------- | ------------- | ------------------ | ----- | -------- | ------- |
| US-1 | 백테스트 실행   | 퀀트 트레이더 | 전략 성과 검증     | 1-2   | 높음     | ✅ 완료 |
| US-2 | 성과 분석       | 투자자        | 리스크/수익률 확인 | 1-2   | 높음     | ✅ 완료 |
| US-3 | 전략 수정       | 개발자        | 파라미터 최적화    | 1-2   | 중간     | ✅ 완료 |
| US-4 | 거래 내역 조회  | 애널리스트    | 의사결정 분석      | 1-2   | 중간     | ✅ 완료 |
| US-5 | 실시간 모니터링 | 운영자        | 시스템 상태 확인   | 1-2   | 낮음     | ✅ 완료 |

### AI Integration 시나리오 (Phase 1-4 완료)

| ID    | 스토리                 | 사용자        | 목표                        | Phase | 우선순위 | 상태    |
| ----- | ---------------------- | ------------- | --------------------------- | ----- | -------- | ------- |
| US-6  | ML 기반 신호 활용      | 퀀트 트레이더 | AI 신호로 수익률 개선       | 1     | 높음     | ✅ 완료 |
| US-7  | 시장 국면 분석         | 애널리스트    | 국면별 전략 적응            | 1     | 높음     | ✅ 완료 |
| US-8  | 포트폴리오 확률 예측   | 투자자        | 미래 수익률 분포 확인       | 1     | 높음     | ✅ 완료 |
| US-9  | 백테스트 자동 최적화   | 개발자        | 최적 파라미터 자동 탐색     | 2     | 높음     | ✅ 완료 |
| US-10 | 데이터 품질 모니터링   | 운영자        | 이상 데이터 조기 감지       | 2     | 높음     | ✅ 완료 |
| US-11 | 내러티브 리포트 생성   | 임원          | AI 기반 인사이트 요약       | 3     | 중간     | ✅ 완료 |
| US-12 | 대화형 전략 빌더       | 초보 트레이더 | 자연어로 전략 생성          | 3     | 중간     | ✅ 완료 |
| US-13 | ChatOps 시스템 점검    | 운영자        | 대화형 시스템 상태 조회     | 3     | 중간     | ✅ 완료 |
| US-14 | 멀티턴 대화 전략 상담  | 퀀트 트레이더 | 전략 비교 및 추천 받기      | 3     | 중간     | ✅ 완료 |
| US-15 | 자동 백테스트 트리거   | 개발자        | 대화 중 즉시 백테스트 실행  | 3     | 중간     | ✅ 완료 |
| US-16 | 피처 스토어 탐색       | 데이터 과학자 | ML 피처 버전 관리 및 조회   | 4     | 높음     | ✅ 완료 |
| US-17 | 모델 라이프사이클 관리 | ML 엔지니어   | 모델 실험 추적 및 배포      | 4     | 높음     | ✅ 완료 |
| US-18 | 모델 성능 평가         | ML 엔지니어   | 벤치마크 스위트로 모델 검증 | 4     | 중간     | ✅ 완료 |
| US-19 | 프롬프트 템플릿 관리   | AI 엔지니어   | LLM 프롬프트 버전 관리      | 4     | 중간     | ✅ 완료 |

---

## US-1: 백테스트 실행

### 스토리 개요

**As a** 퀀트 트레이더  
**I want to** 전략에 대한 백테스트를 실행  
**So that** 과거 데이터로 전략 성과를 검증할 수 있다

**수락 기준**:

- ✅ 전략 선택 및 설정 입력
- ✅ 백테스트 실행 시작
- ✅ 진행 상태 확인 가능
- ✅ 완료 후 결과 조회

**비즈니스 가치**: 전략 검증을 통한 투자 리스크 감소

### 시퀀스 다이어그램

```mermaid
sequenceDiagram
    actor User as 사용자
    participant FE as Frontend
    participant API as Backend API
    participant BS as BacktestService
    participant ORCH as Orchestrator
    participant MDS as MarketDataService
    participant DUCK as DuckDB
    participant AV as Alpha Vantage

    User->>FE: 전략 선택 + 설정 입력
    FE->>API: POST /backtests

    API->>BS: create_backtest(config)
    BS->>BS: Backtest 문서 생성
    BS-->>API: backtest_id
    API-->>FE: { id, status: "pending" }
    FE-->>User: 백테스트 시작됨

    par 비동기 실행
        BS->>ORCH: execute_backtest(backtest_id)

        rect rgb(200, 220, 255)
            note right of ORCH: 1. 데이터 수집 (병렬)
            ORCH->>MDS: get_historical_data(symbols)
            MDS->>DUCK: check cache
            alt 캐시 히트
                DUCK-->>MDS: 데이터 반환 (0.5ms)
            else 캐시 미스
                MDS->>AV: API 호출
                AV-->>MDS: 데이터
                MDS->>DUCK: 캐시 저장
            end
            MDS-->>ORCH: market_data
        end

        rect rgb(220, 255, 220)
            note right of ORCH: 2. 신호 생성
            ORCH->>ORCH: generate_signals()
        end

        rect rgb(255, 240, 220)
            note right of ORCH: 3. 시뮬레이션
            ORCH->>ORCH: simulate_trades()
        end

        rect rgb(255, 220, 255)
            note right of ORCH: 4. 성과 분석
            ORCH->>ORCH: calculate_metrics()
        end

        ORCH->>DUCK: save_results()
        ORCH-->>BS: BacktestResult
        BS->>BS: 상태 업데이트 (completed)
    end

    User->>FE: 결과 조회 요청
    FE->>API: GET /backtests/{id}
    API->>BS: get_backtest(id)
    BS-->>API: backtest + result
    API-->>FE: { status: "completed", metrics: {...} }
    FE-->>User: 성과 지표 표시
```

### 플로우차트

```mermaid
flowchart TD
    Start([사용자: 백테스트 시작]) --> Input[전략 선택 + 파라미터 입력]
    Input --> Validate{입력 검증}

    Validate -->|유효하지 않음| Error1[에러 메시지 표시]
    Error1 --> Input

    Validate -->|유효함| Create[백테스트 생성<br/>POST /backtests]
    Create --> Queue[비동기 실행 큐에 추가]
    Queue --> Pending[상태: pending]

    Pending --> Poll{폴링<br/>GET /backtests/id}
    Poll -->|실행 중| Wait[3초 대기]
    Wait --> Poll

    Poll -->|완료| Result[결과 조회]
    Poll -->|실패| Error2[에러 로그 표시]

    Result --> Display[성과 지표 대시보드<br/>- 총 수익률<br/>- 샤프 비율<br/>- 최대 낙폭]
    Display --> Chart[차트 렌더링<br/>- 포트폴리오 가치 추이<br/>- 거래 내역]

    Chart --> End([완료])
    Error2 --> End

    style Start fill:#e1f5e1
    style End fill:#ffe1e1
    style Display fill:#e1e5ff
    style Chart fill:#fff5e1
```

---

## US-2: 성과 분석 및 비교

### 스토리 개요

**As a** 투자자  
**I want to** 여러 백테스트 결과를 비교 분석  
**So that** 최적의 전략을 선택할 수 있다

**수락 기준**:

- ✅ 포트폴리오 가치 시계열 조회
- ✅ 거래 내역 상세 조회
- ✅ 성과 지표 비교
- ✅ 차트 시각화

**비즈니스 가치**: 데이터 기반 의사결정

### 시퀀스 다이어그램

```mermaid
sequenceDiagram
    actor User as 투자자
    participant FE as Frontend
    participant API as Backend API
    participant DM as DatabaseManager
    participant DUCK as DuckDB

    User->>FE: 백테스트 결과 페이지 접속

    par 병렬 데이터 로드
        FE->>API: GET /backtests/{id}
        API-->>FE: backtest + metrics

        FE->>API: GET /backtests/{id}/portfolio-history
        API->>DM: get_portfolio_history(id)
        DM->>DUCK: SELECT * FROM portfolio_history
        DUCK-->>DM: 1000+ rows (1ms)
        DM-->>API: DataFrame
        API-->>FE: { data: [...], count: 1234 }

        FE->>API: GET /backtests/{id}/trades-history
        API->>DM: get_trades_history(id)
        DM->>DUCK: SELECT * FROM trades
        DUCK-->>DM: 50+ rows (<1ms)
        DM-->>API: DataFrame
        API-->>FE: { data: [...], count: 56 }
    end

    FE->>FE: 차트 렌더링
    FE-->>User: 대시보드 표시

    User->>FE: 다른 백테스트 선택
    Note over User,FE: 위 프로세스 반복
```

### 플로우차트

```mermaid
flowchart TD
    Start([투자자: 결과 분석]) --> List[백테스트 목록 조회<br/>GET /backtests]

    List --> Select[백테스트 선택]
    Select --> Load{데이터 로드}

    Load -->|API 호출 1| Metrics[성과 지표<br/>GET /backtests/id]
    Load -->|API 호출 2| Portfolio[포트폴리오 히스토리<br/>GET /backtests/id/portfolio-history]
    Load -->|API 호출 3| Trades[거래 내역<br/>GET /backtests/id/trades-history]

    Metrics --> Render
    Portfolio --> Render
    Trades --> Render[대시보드 렌더링]

    Render --> Display1[KPI 카드<br/>- 총 수익률: +15.3%<br/>- 샤프 비율: 1.8<br/>- 최대 낙폭: -8.2%]
    Display1 --> Display2[포트폴리오 차트<br/>- 시계열 라인 차트<br/>- 기준선 비교]
    Display2 --> Display3[거래 테이블<br/>- 매수/매도 내역<br/>- 손익 계산]

    Display3 --> Compare{다른 전략 비교?}
    Compare -->|예| Select
    Compare -->|아니오| Export[데이터 내보내기<br/>CSV / Excel]

    Export --> End([완료])

    style Start fill:#e1f5e1
    style End fill:#ffe1e1
    style Display1 fill:#e1e5ff
    style Display2 fill:#fff5e1
    style Display3 fill:#ffe5f0
```

---

## US-3: 전략 파라미터 최적화

### 스토리 개요

**As a** 전략 개발자  
**I want to** 전략 파라미터를 조정하여 재실행  
**So that** 최적의 설정값을 찾을 수 있다

**수락 기준**:

- ✅ 기존 전략 복제
- ✅ 파라미터 수정
- ✅ 빠른 재실행
- ✅ 이전 결과와 비교

**비즈니스 가치**: 전략 성과 개선

### 시퀀스 다이어그램

```mermaid
sequenceDiagram
    actor Dev as 개발자
    participant FE as Frontend
    participant API as Backend API
    participant SS as StrategyService
    participant BS as BacktestService
    participant CACHE as DuckDB Cache

    Dev->>FE: 기존 백테스트 선택
    FE->>API: GET /backtests/{id}
    API-->>FE: { strategy_id, config }

    Dev->>FE: "파라미터 수정" 버튼
    FE-->>Dev: 파라미터 편집 폼

    Dev->>FE: 파라미터 변경<br/>(예: SMA 20 → 30)
    FE->>FE: 로컬 검증

    Dev->>FE: "재실행" 버튼
    FE->>API: POST /backtests<br/>{ strategy_id, new_params }

    API->>BS: create_backtest()
    BS->>BS: 새 백테스트 생성

    rect rgb(200, 255, 200)
        note right of BS: 캐시 활용으로 빠른 실행
        BS->>CACHE: 동일 심볼+기간 확인
        CACHE-->>BS: 캐시 히트 (데이터 수집 생략)
        BS->>BS: 신호 재생성<br/>(변경된 파라미터)
        BS->>BS: 시뮬레이션 재실행
    end

    BS-->>API: new_backtest_id
    API-->>FE: { id, status: "completed" }

    FE->>API: GET /backtests/{new_id}
    API-->>FE: new_result

    FE->>FE: 이전/신규 결과 비교
    FE-->>Dev: 성과 비교 차트
```

### 플로우차트

```mermaid
flowchart TD
    Start([개발자: 파라미터 최적화]) --> Select[백테스트 선택]

    Select --> Clone[설정 복제]
    Clone --> Edit[파라미터 수정<br/>- SMA 기간: 20 → 30<br/>- RSI 임계값: 70 → 75]

    Edit --> Validate{검증}
    Validate -->|범위 초과| Error[에러 메시지]
    Error --> Edit

    Validate -->|유효| Submit[재실행 요청<br/>POST /backtests]

    Submit --> Cache{DuckDB 캐시}
    Cache -->|히트| Fast[고속 실행<br/>데이터 수집 생략<br/>3-5초]
    Cache -->|미스| Slow[전체 실행<br/>데이터 수집 포함<br/>10-30초]

    Fast --> Complete
    Slow --> Complete[실행 완료]

    Complete --> Compare[결과 비교<br/>- 이전 vs 신규<br/>- 수익률 차이<br/>- 리스크 변화]

    Compare --> Decision{개선됨?}
    Decision -->|예| Save[최적 파라미터 저장]
    Decision -->|아니오| Retry{재시도?}

    Retry -->|예| Edit
    Retry -->|아니오| End1([종료])
    Save --> End2([완료])

    style Start fill:#e1f5e1
    style End1 fill:#ffe1e1
    style End2 fill:#e1ffe1
    style Fast fill:#fff5e1
    style Compare fill:#e1e5ff
```

---

## US-4: 거래 내역 상세 분석

### 스토리 개요

**As a** 애널리스트  
**I want to** 개별 거래 내역을 상세 조회  
**So that** 전략 의사결정 과정을 분석할 수 있다

**수락 기준**:

- ✅ 거래 타임라인 조회
- ✅ 매수/매도 근거 확인
- ✅ 손익 계산
- ✅ 필터링 및 정렬

**비즈니스 가치**: 전략 개선 인사이트

### 시퀀스 다이어그램

```mermaid
sequenceDiagram
    actor Analyst as 애널리스트
    participant FE as Frontend
    participant API as Backend API
    participant DM as DatabaseManager
    participant DUCK as DuckDB

    Analyst->>FE: 거래 내역 페이지 접속
    FE->>API: GET /backtests/{id}/trades-history

    API->>DM: get_trades_history(id)
    DM->>DUCK: SELECT * FROM trades<br/>ORDER BY timestamp
    DUCK-->>DM: trades (50-500 rows)
    DM-->>API: DataFrame
    API-->>FE: { data: [...], count: 234 }

    FE->>FE: 테이블 렌더링
    FE-->>Analyst: 거래 목록 표시

    Analyst->>FE: 필터 적용<br/>(예: 심볼=AAPL, 매수만)
    FE->>FE: 클라이언트 필터링
    FE-->>Analyst: 필터된 결과

    Analyst->>FE: 거래 클릭
    FE-->>Analyst: 상세 모달<br/>- 시그널 정보<br/>- 가격/수량<br/>- 손익<br/>- 차트
```

### 플로우차트

```mermaid
flowchart TD
    Start([애널리스트: 거래 분석]) --> Load[거래 내역 로드<br/>GET /trades-history]

    Load --> Display[거래 테이블 표시<br/>- 타임스탬프<br/>- 심볼<br/>- 매수/매도<br/>- 가격/수량]

    Display --> Filter{필터 적용?}
    Filter -->|예| FilterOpt[필터 옵션<br/>- 심볼 선택<br/>- 날짜 범위<br/>- 거래 유형]
    FilterOpt --> Filtered[필터된 결과]
    Filter -->|아니오| Select

    Filtered --> Select[거래 선택]
    Select --> Detail[상세 정보 조회<br/>- 시그널 근거<br/>- 포트폴리오 영향<br/>- 수익/손실]

    Detail --> Chart[차트 오버레이<br/>- 가격 차트<br/>- 거래 마커<br/>- 지표 표시]

    Chart --> Export{데이터 내보내기?}
    Export -->|예| CSV[CSV 다운로드]
    Export -->|아니오| More{다른 거래?}

    CSV --> More
    More -->|예| Select
    More -->|아니오| End([완료])

    style Start fill:#e1f5e1
    style End fill:#ffe1e1
    style Detail fill:#e1e5ff
    style Chart fill:#fff5e1
```

---

## 공통 기술 요소

### 프론트엔드 훅 사용 패턴

```typescript
// 백테스트 목록 조회
const { backtestList } = useBacktest();

// 백테스트 생성
const { createBacktest } = useBacktest();
await createBacktest(config);

// 백테스트 상세
const { backtest } = useBacktest(backtestId);

// 포트폴리오 히스토리
const { portfolioHistory } = useBacktest(backtestId);

// 거래 내역
const { tradesHistory } = useBacktest(backtestId);
```

### API 응답 형식

```json
{
  "status": "success",
  "data": {
    "id": "backtest_123",
    "status": "completed",
    "metrics": {
      "total_return": 0.153,
      "sharpe_ratio": 1.8,
      "max_drawdown": -0.082
    }
  },
  "source": "duckdb"
}
```

### 에러 처리

```json
{
  "status": "error",
  "error": {
    "code": "INVALID_PARAMETERS",
    "message": "SMA period must be between 1 and 200",
    "details": {
      "field": "sma_period",
      "value": 250
    }
  }
}
```
