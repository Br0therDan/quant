# Database Entity Relationship Diagram (ERD)

**업데이트**: 2025년 10월 15일  
**버전**: Phase 4 완료 (AI/ML 통합)

---

## 📋 목차

1. [개요](#-개요)
2. [전체 ERD](#-전체-erd)
3. [도메인별 상세 ERD](#-도메인별-상세-erd)
4. [주요 테이블 설명](#-주요-테이블-설명)
5. [인덱스 전략](#-인덱스-전략)

---

## 📊 개요

### 데이터베이스 구성

- **MongoDB**: 메타데이터, 사용자 데이터, 설정 (비동기)
- **DuckDB**: 시계열 데이터 고성능 캐시 (동기)
- **ChromaDB**: 벡터 데이터베이스 (GenAI RAG, 선택적)

### 주요 도메인

1. **User Domain**: 사용자, 인증, 권한
2. **Trading Domain**: 전략, 백테스트, 최적화
3. **Market Data Domain**: 주식, 재무, 경제 지표, 뉴스
4. **ML Platform Domain**: Feature, Model, Experiment, Evaluation
5. **GenAI Domain**: Chat Session, Prompt, Strategy Generation

---

## 🗺️ 전체 ERD

```mermaid
erDiagram
    %% User Domain
    User {
        string id PK
        string email UK
        string username UK
        string password_hash
        boolean is_active
        boolean is_verified
        datetime created_at
        datetime updated_at
    }

    %% Trading Domain
    Strategy {
        string id PK
        string name
        string description
        string strategy_type
        object parameters
        string user_id FK
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    StrategyTemplate {
        string id PK
        string name
        string description
        string strategy_type
        object default_parameters
        object parameter_schema
        array tags
        int usage_count
        datetime created_at
        datetime updated_at
    }

    Backtest {
        string id PK
        string name
        string description
        string strategy_id FK
        object config
        string status
        string user_id FK
        datetime created_at
        datetime updated_at
    }

    BacktestExecution {
        string id PK
        string backtest_id FK
        string execution_id
        string status
        datetime started_at
        datetime completed_at
        object error_details
        string user_id FK
    }

    BacktestResult {
        string id PK
        string backtest_id FK
        string execution_id
        object performance
        array trades
        object risk_metrics
        object portfolio_value
        datetime executed_at
        string user_id FK
    }

    OptimizationStudy {
        string id PK
        string name
        string strategy_id FK
        object parameter_space
        int n_trials
        string status
        object best_params
        float best_value
        string user_id FK
        datetime created_at
        datetime updated_at
    }

    Portfolio {
        string id PK
        string name
        array positions
        object performance
        string user_id FK
        datetime created_at
        datetime updated_at
    }

    %% Market Data Domain
    MarketData {
        string id PK
        string symbol
        datetime date
        float open_price
        float high_price
        float low_price
        float close_price
        int volume
        string data_source
        datetime created_at
    }

    Company {
        string id PK
        string symbol UK
        string name
        string sector
        string industry
        object financials
        datetime created_at
        datetime updated_at
    }

    EconomicIndicator {
        string id PK
        string indicator_type
        datetime date
        float value
        string unit
        string source
        datetime created_at
    }

    NewsData {
        string id PK
        string symbol
        string title
        string content
        string url
        float sentiment_score
        array topics
        string source
        datetime published_at
        datetime created_at
    }

    TechnicalIndicator {
        string id PK
        string symbol
        string indicator_type
        datetime date
        object values
        datetime created_at
    }

    %% ML Platform Domain
    Feature {
        string id PK
        string name
        string description
        string feature_type
        object schema
        string version
        object statistics
        string user_id FK
        datetime created_at
        datetime updated_at
    }

    FeatureVersion {
        string id PK
        string feature_id FK
        string version
        object schema
        object statistics
        string status
        datetime created_at
    }

    MLModel {
        string id PK
        string name
        string model_type
        string version
        object parameters
        object metrics
        string status
        string artifact_path
        string user_id FK
        datetime created_at
        datetime updated_at
    }

    Experiment {
        string id PK
        string name
        string description
        object parameters
        array model_ids
        object metrics
        string user_id FK
        datetime created_at
        datetime updated_at
    }

    ModelDeployment {
        string id PK
        string model_id FK
        string environment
        string status
        object config
        datetime deployed_at
        datetime updated_at
    }

    EvaluationScenario {
        string id PK
        string name
        string description
        object config
        array model_ids
        object results
        string user_id FK
        datetime created_at
        datetime updated_at
    }

    %% GenAI Domain
    ChatSession {
        string id PK
        string session_id UK
        string user_id FK
        array conversation_history
        object context
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    PromptTemplate {
        string id PK
        string name
        string description
        string template
        object variables
        array tags
        string user_id FK
        datetime created_at
        datetime updated_at
    }

    GeneratedStrategy {
        string id PK
        string name
        string description
        string code
        object parameters
        string prompt
        string model_used
        string user_id FK
        datetime created_at
    }

    %% User Domain
    Watchlist {
        string id PK
        string name
        string description
        array symbols
        object metadata
        string user_id FK
        datetime created_at
        datetime updated_at
    }

    Dashboard {
        string id PK
        string user_id FK
        object layout
        array widgets
        datetime created_at
        datetime updated_at
    }

    %% Relationships

    %% User Relationships
    User ||--o{ Strategy : creates
    User ||--o{ Backtest : owns
    User ||--o{ BacktestExecution : executes
    User ||--o{ BacktestResult : generates
    User ||--o{ OptimizationStudy : runs
    User ||--o{ Portfolio : manages
    User ||--o{ Watchlist : creates
    User ||--o{ Dashboard : customizes
    User ||--o{ Feature : defines
    User ||--o{ MLModel : trains
    User ||--o{ Experiment : conducts
    User ||--o{ EvaluationScenario : evaluates
    User ||--o{ ChatSession : initiates
    User ||--o{ PromptTemplate : creates
    User ||--o{ GeneratedStrategy : generates

    %% Trading Relationships
    StrategyTemplate ||--o{ Strategy : instantiates
    Strategy ||--o{ Backtest : uses
    Strategy ||--o{ OptimizationStudy : optimizes
    Backtest ||--o{ BacktestExecution : runs
    Backtest ||--o{ BacktestResult : produces
    BacktestExecution ||--|| BacktestResult : creates

    %% Market Data Relationships
    Company ||--o{ MarketData : provides
    MarketData ||--o{ TechnicalIndicator : derives
    Company ||--o{ NewsData : mentions
    MarketData ||--o{ Backtest : feeds

    %% ML Platform Relationships
    Feature ||--o{ FeatureVersion : versions
    MLModel ||--o{ Experiment : includes
    MLModel ||--o{ ModelDeployment : deploys
    MLModel ||--o{ EvaluationScenario : evaluates
    Experiment ||--o{ EvaluationScenario : analyzes

    %% GenAI Relationships
    PromptTemplate ||--o{ GeneratedStrategy : uses
    ChatSession ||--o{ GeneratedStrategy : creates
    GeneratedStrategy ||--o{ Strategy : becomes
```

---

## 🎯 도메인별 상세 ERD

### 1. User Domain

```mermaid
erDiagram
    User {
        string id PK "ObjectId"
        string email UK "이메일 (Unique)"
        string username UK "사용자명 (Unique)"
        string password_hash "비밀번호 해시"
        boolean is_active "활성 여부"
        boolean is_verified "이메일 인증 여부"
        datetime created_at "생성일"
        datetime updated_at "수정일"
    }

    Watchlist {
        string id PK
        string name "관심종목 이름"
        string description "설명"
        array symbols "종목 심볼 리스트"
        object metadata "추가 메타데이터"
        string user_id FK
        datetime created_at
        datetime updated_at
    }

    Dashboard {
        string id PK
        string user_id FK
        object layout "대시보드 레이아웃 설정"
        array widgets "위젯 리스트"
        datetime created_at
        datetime updated_at
    }

    User ||--o{ Watchlist : "1:N"
    User ||--|| Dashboard : "1:1"
```

### 2. Trading Domain

```mermaid
erDiagram
    Strategy {
        string id PK
        string name "전략 이름"
        string description "전략 설명"
        string strategy_type "전략 타입 (SMA, RSI, etc.)"
        object parameters "전략 파라미터"
        string user_id FK
        boolean is_active "활성 여부"
        datetime created_at
        datetime updated_at
    }

    StrategyTemplate {
        string id PK
        string name "템플릿 이름"
        string description "템플릿 설명"
        string strategy_type "전략 타입"
        object default_parameters "기본 파라미터"
        object parameter_schema "파라미터 스키마 (검증용)"
        array tags "태그"
        int usage_count "사용 횟수"
        datetime created_at
        datetime updated_at
    }

    Backtest {
        string id PK
        string name "백테스트 이름"
        string description "백테스트 설명"
        string strategy_id FK
        object config "백테스트 설정 (심볼, 기간 등)"
        string status "상태 (pending, running, completed)"
        string user_id FK
        datetime created_at
        datetime updated_at
    }

    BacktestExecution {
        string id PK
        string backtest_id FK
        string execution_id "실행 ID (UUID)"
        string status "실행 상태"
        datetime started_at "시작 시간"
        datetime completed_at "완료 시간"
        object error_details "에러 상세 (실패 시)"
        string user_id FK
    }

    BacktestResult {
        string id PK
        string backtest_id FK
        string execution_id FK
        object performance "성과 지표 (총 수익률, 샤프, etc.)"
        array trades "거래 내역"
        object risk_metrics "리스크 지표 (MDD, VaR, etc.)"
        object portfolio_value "포트폴리오 가치 시계열"
        datetime executed_at
        string user_id FK
    }

    OptimizationStudy {
        string id PK
        string name "최적화 스터디 이름"
        string strategy_id FK
        object parameter_space "파라미터 탐색 공간"
        int n_trials "시도 횟수"
        string status "상태 (running, completed)"
        object best_params "최적 파라미터"
        float best_value "최적 값 (Sharpe 등)"
        string user_id FK
        datetime created_at
        datetime updated_at
    }

    Portfolio {
        string id PK
        string name "포트폴리오 이름"
        array positions "포지션 리스트"
        object performance "성과"
        string user_id FK
        datetime created_at
        datetime updated_at
    }

    StrategyTemplate ||--o{ Strategy : "템플릿 사용"
    Strategy ||--o{ Backtest : "전략 실행"
    Strategy ||--o{ OptimizationStudy : "최적화"
    Backtest ||--o{ BacktestExecution : "실행 이력"
    BacktestExecution ||--|| BacktestResult : "결과 생성"
```

### 3. Market Data Domain

```mermaid
erDiagram
    MarketData {
        string id PK
        string symbol "종목 심볼"
        datetime date "날짜"
        float open_price "시가"
        float high_price "고가"
        float low_price "저가"
        float close_price "종가"
        int volume "거래량"
        string data_source "데이터 소스 (alpha_vantage)"
        datetime created_at
    }

    Company {
        string id PK
        string symbol UK "종목 심볼 (Unique)"
        string name "회사명"
        string sector "섹터"
        string industry "산업"
        object financials "재무 데이터"
        datetime created_at
        datetime updated_at
    }

    EconomicIndicator {
        string id PK
        string indicator_type "지표 타입 (GDP, CPI, etc.)"
        datetime date "날짜"
        float value "값"
        string unit "단위"
        string source "출처"
        datetime created_at
    }

    NewsData {
        string id PK
        string symbol "관련 종목 심볼"
        string title "뉴스 제목"
        string content "뉴스 내용"
        string url "뉴스 URL"
        float sentiment_score "감성 점수 (-1 ~ 1)"
        array topics "토픽 리스트"
        string source "출처"
        datetime published_at "발행일"
        datetime created_at
    }

    TechnicalIndicator {
        string id PK
        string symbol "종목 심볼"
        string indicator_type "지표 타입 (SMA, RSI, etc.)"
        datetime date "날짜"
        object values "지표 값 (period별)"
        datetime created_at
    }

    Company ||--o{ MarketData : "제공"
    MarketData ||--o{ TechnicalIndicator : "계산"
    Company ||--o{ NewsData : "언급"
```

### 4. ML Platform Domain

```mermaid
erDiagram
    Feature {
        string id PK
        string name "Feature 이름"
        string description "Feature 설명"
        string feature_type "Feature 타입"
        object schema "Feature 스키마"
        string version "버전"
        object statistics "통계 (평균, 분산 등)"
        string user_id FK
        datetime created_at
        datetime updated_at
    }

    FeatureVersion {
        string id PK
        string feature_id FK
        string version "버전 번호 (semantic)"
        object schema "스키마"
        object statistics "통계"
        string status "상태 (draft, production)"
        datetime created_at
    }

    MLModel {
        string id PK
        string name "모델 이름"
        string model_type "모델 타입 (LightGBM, Prophet, etc.)"
        string version "버전"
        object parameters "하이퍼파라미터"
        object metrics "평가 지표 (RMSE, AUC, etc.)"
        string status "상태 (training, production, archived)"
        string artifact_path "모델 파일 경로"
        string user_id FK
        datetime created_at
        datetime updated_at
    }

    Experiment {
        string id PK
        string name "실험 이름"
        string description "실험 설명"
        object parameters "실험 파라미터"
        array model_ids "실험에 포함된 모델 ID 리스트"
        object metrics "실험 결과 지표"
        string user_id FK
        datetime created_at
        datetime updated_at
    }

    ModelDeployment {
        string id PK
        string model_id FK
        string environment "배포 환경 (dev, staging, prod)"
        string status "배포 상태 (deployed, rollback)"
        object config "배포 설정"
        datetime deployed_at "배포 시간"
        datetime updated_at
    }

    EvaluationScenario {
        string id PK
        string name "평가 시나리오 이름"
        string description "시나리오 설명"
        object config "평가 설정"
        array model_ids "평가 대상 모델 ID 리스트"
        object results "평가 결과"
        string user_id FK
        datetime created_at
        datetime updated_at
    }

    Feature ||--o{ FeatureVersion : "버전 관리"
    MLModel ||--o{ Experiment : "실험 포함"
    MLModel ||--o{ ModelDeployment : "배포"
    MLModel ||--o{ EvaluationScenario : "평가"
    Experiment ||--o{ EvaluationScenario : "분석"
```

### 5. GenAI Domain

```mermaid
erDiagram
    ChatSession {
        string id PK
        string session_id UK "세션 UUID (Unique)"
        string user_id FK
        array conversation_history "대화 이력 (role, content)"
        object context "세션 컨텍스트"
        boolean is_active "활성 여부"
        datetime created_at
        datetime updated_at
    }

    PromptTemplate {
        string id PK
        string name "프롬프트 템플릿 이름"
        string description "템플릿 설명"
        string template "프롬프트 템플릿 문자열"
        object variables "변수 스키마"
        array tags "태그"
        string user_id FK
        datetime created_at
        datetime updated_at
    }

    GeneratedStrategy {
        string id PK
        string name "생성된 전략 이름"
        string description "전략 설명"
        string code "생성된 전략 코드"
        object parameters "전략 파라미터"
        string prompt "사용된 프롬프트"
        string model_used "사용된 LLM 모델 (gpt-4o-mini, etc.)"
        string user_id FK
        datetime created_at
    }

    RAGDocument {
        string id PK
        string document_id UK "문서 UUID (ChromaDB ID)"
        string document_type "문서 타입 (backtest, strategy)"
        string user_id FK
        string content "텍스트 내용"
        object metadata "메타데이터"
        array embeddings "벡터 임베딩 (ChromaDB)"
        datetime created_at
    }

    PromptTemplate ||--o{ GeneratedStrategy : "사용"
    ChatSession ||--o{ GeneratedStrategy : "생성"
    GeneratedStrategy ||--o{ Strategy : "변환"
    RAGDocument ||--o{ ChatSession : "컨텍스트 제공"
```

---

## 📝 주요 테이블 설명

### User

**목적**: 사용자 인증 및 권한 관리

**주요 필드**:

- `email`: 로그인 ID (Unique Index)
- `is_verified`: 이메일 인증 여부 (회원가입 시 false)
- `is_active`: 계정 활성 여부 (탈퇴 시 false)

**인덱스**:

- Primary: `id`
- Unique: `email`, `username`

### Strategy

**목적**: 사용자 정의 거래 전략

**주요 필드**:

- `strategy_type`: 전략 타입 (SMA_CROSSOVER, RSI_MEAN_REVERSION, etc.)
- `parameters`: 전략별 파라미터 (JSON)
  ```json
  {
    "short_window": 20,
    "long_window": 50,
    "rsi_period": 14,
    "oversold": 30,
    "overbought": 70
  }
  ```

**인덱스**:

- Primary: `id`
- Composite: `(user_id, strategy_type)`
- Composite: `(user_id, is_active)`

### Backtest

**목적**: 백테스트 설정 및 메타데이터

**주요 필드**:

- `config`: 백테스트 설정
  ```json
  {
    "symbols": ["AAPL", "MSFT"],
    "start_date": "2020-01-01",
    "end_date": "2023-12-31",
    "initial_capital": 100000,
    "commission": 0.001
  }
  ```
- `status`: `pending` | `running` | `completed` | `failed`

**인덱스**:

- Primary: `id`
- Composite: `(user_id, status)`
- Composite: `(strategy_id, created_at)`

### BacktestResult

**목적**: 백테스트 실행 결과

**주요 필드**:

- `performance`: 성과 지표
  ```json
  {
    "total_return": 0.35,
    "sharpe_ratio": 1.8,
    "max_drawdown": -0.15,
    "win_rate": 0.62,
    "total_trades": 150
  }
  ```
- `trades`: 거래 내역 배열
  ```json
  [
    {
      "date": "2020-03-15",
      "symbol": "AAPL",
      "action": "BUY",
      "quantity": 10,
      "price": 250.5,
      "commission": 2.5
    }
  ]
  ```

**인덱스**:

- Primary: `id`
- Composite: `(backtest_id, executed_at)`
- Composite: `(user_id, executed_at)`

### OptimizationStudy

**목적**: Optuna 기반 하이퍼파라미터 최적화

**주요 필드**:

- `parameter_space`: 파라미터 탐색 공간
  ```json
  {
    "short_window": { "type": "int", "low": 5, "high": 50 },
    "long_window": { "type": "int", "low": 20, "high": 200 },
    "rsi_period": { "type": "int", "low": 7, "high": 21 }
  }
  ```
- `best_params`: 최적 파라미터
- `best_value`: 최적 값 (Sharpe Ratio 등)

**인덱스**:

- Primary: `id`
- Composite: `(strategy_id, status)`
- Composite: `(user_id, created_at)`

### MLModel

**목적**: 머신러닝 모델 메타데이터 및 버전 관리

**주요 필드**:

- `model_type`: `LightGBM` | `CatBoost` | `Prophet` | `LSTM`
- `metrics`: 평가 지표
  ```json
  {
    "rmse": 0.05,
    "mae": 0.03,
    "r2": 0.85,
    "auc": 0.92
  }
  ```
- `artifact_path`: 모델 파일 경로 (S3, local, etc.)

**인덱스**:

- Primary: `id`
- Composite: `(model_type, status)`
- Composite: `(user_id, created_at)`

### ChatSession

**목적**: GenAI 대화 세션 관리

**주요 필드**:

- `conversation_history`: 대화 이력
  ````json
  [
    {
      "role": "user",
      "content": "RSI 전략 만들어줘",
      "timestamp": "2025-10-15T10:00:00Z"
    },
    {
      "role": "assistant",
      "content": "RSI 전략 코드:\n```python\n...",
      "timestamp": "2025-10-15T10:00:05Z"
    }
  ]
  ````
- `context`: 세션 컨텍스트 (이전 백테스트 결과 등)

**인덱스**:

- Primary: `id`
- Unique: `session_id`
- Composite: `(user_id, is_active)`

### RAGDocument

**목적**: RAG용 벡터 문서 (ChromaDB 메타데이터)

**주요 필드**:

- `document_type`: `backtest` | `strategy` | `market_insight`
- `content`: 텍스트 내용 (벡터화 대상)
- `embeddings`: ChromaDB에 저장된 벡터 (참조용)
- `metadata`: 문서 메타데이터
  ```json
  {
    "backtest_id": "...",
    "total_return": 0.35,
    "sharpe_ratio": 1.8,
    "strategy_name": "RSI Mean Reversion"
  }
  ```

**인덱스**:

- Primary: `id`
- Unique: `document_id`
- Composite: `(user_id, document_type)`

---

## 🔍 인덱스 전략

### MongoDB 인덱스

#### User Collection

```javascript
// Unique Indexes
db.users.createIndex({ email: 1 }, { unique: true });
db.users.createIndex({ username: 1 }, { unique: true });

// Compound Index
db.users.createIndex({ is_active: 1, created_at: -1 });
```

#### Strategy Collection

```javascript
// Compound Indexes
db.strategies.createIndex({ user_id: 1, strategy_type: 1 });
db.strategies.createIndex({ user_id: 1, is_active: 1 });
db.strategies.createIndex({ strategy_type: 1, created_at: -1 });
```

#### Backtest Collection

```javascript
// Compound Indexes
db.backtests.createIndex({ user_id: 1, status: 1 });
db.backtests.createIndex({ strategy_id: 1, created_at: -1 });
db.backtests.createIndex({ user_id: 1, created_at: -1 });
```

#### BacktestResult Collection

```javascript
// Compound Indexes
db.backtest_results.createIndex({ backtest_id: 1, executed_at: -1 });
db.backtest_results.createIndex({ user_id: 1, executed_at: -1 });
db.backtest_results.createIndex({ execution_id: 1 }, { unique: true });
```

#### ChatSession Collection

```javascript
// Unique Index
db.chat_sessions.createIndex({ session_id: 1 }, { unique: true });

// Compound Indexes
db.chat_sessions.createIndex({ user_id: 1, is_active: 1 });
db.chat_sessions.createIndex({ user_id: 1, updated_at: -1 });
```

### DuckDB 인덱스

#### market_data 테이블

```sql
-- Primary Index
CREATE UNIQUE INDEX idx_market_data_pk ON market_data (symbol, date);

-- Query Optimization
CREATE INDEX idx_market_data_symbol_date ON market_data (symbol, date DESC);
CREATE INDEX idx_market_data_date ON market_data (date);
```

#### technical_indicators 테이블

```sql
-- Compound Index
CREATE INDEX idx_tech_indicators ON technical_indicators (symbol, indicator_type, date DESC);
```

### ChromaDB 컬렉션

#### user_backtests

**메타데이터 필터링**:

```python
collection.query(
    query_texts=["RSI 전략"],
    where={"user_id": "user123"},  # 사용자 필터
    n_results=5
)
```

#### user_strategies

**메타데이터 필터링**:

```python
collection.query(
    query_texts=["모멘텀 전략"],
    where={"strategy_type": "MOMENTUM"},  # 전략 타입 필터
    n_results=3
)
```

---

## 📈 성능 최적화 권장사항

### 1. MongoDB

- **TTL 인덱스**: BacktestExecution (실패한 실행은 30일 후 자동 삭제)

  ```javascript
  db.backtest_executions.createIndex(
    { completed_at: 1 },
    {
      expireAfterSeconds: 2592000,
      partialFilterExpression: { status: "failed" },
    }
  );
  ```

- **부분 인덱스**: 활성 전략만 인덱싱
  ```javascript
  db.strategies.createIndex(
    { user_id: 1, created_at: -1 },
    { partialFilterExpression: { is_active: true } }
  );
  ```

### 2. DuckDB

- **Parquet 저장**: 대용량 시계열 데이터

  ```sql
  COPY market_data TO 'market_data.parquet' (FORMAT PARQUET, COMPRESSION ZSTD);
  ```

- **파티셔닝**: 연도별 파티션
  ```sql
  CREATE TABLE market_data_2023 AS SELECT * FROM market_data WHERE YEAR(date) = 2023;
  ```

### 3. ChromaDB

- **배치 인덱싱**: 대량 문서 인덱싱 시

  ```python
  collection.add(
      documents=batch_documents,  # 100개씩 배치
      metadatas=batch_metadatas,
      ids=batch_ids
  )
  ```

- **임베딩 캐싱**: 동일 문서 재인덱싱 방지

---

## 🔗 관련 문서

- [Backend README](./README.md)
- [API Structure](../docs/backend/API_STRUCTURE.md)
- [GenAI OpenAI Client Design](../docs/backend/GENAI_OPENAI_CLIENT_DESIGN.md)

---

**마지막 업데이트**: 2025년 10월 15일  
**담당**: Backend Team
