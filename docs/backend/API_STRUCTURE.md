# Backend API Structure

**업데이트 날짜**: 2025년 10월 15일  
**현재 버전**: Phase 2.1b 완료

---

## 📂 API 디렉토리 구조

```
backend/app/api/
├── __init__.py                    # Main API router 통합
└── routes/
    ├── __init__.py                # Sub-routers export
    ├── market_data/               # 마켓 데이터 도메인
    │   ├── __init__.py            # Market data router 통합
    │   ├── stock.py               # 주식 데이터
    │   ├── crypto.py              # 암호화폐 데이터
    │   ├── fundamental.py         # 기본 재무 데이터
    │   ├── economic_indicator.py  # 경제 지표
    │   ├── intelligence.py        # 시장 인텔리전스
    │   ├── management.py          # 데이터 관리
    │   ├── technical_indicators.py # 기술적 지표
    │   └── regime.py              # 시장 국면 분석
    ├── trading/                   # 트레이딩 도메인
    │   ├── __init__.py
    │   ├── backtests.py           # 백테스트
    │   ├── strategies.py          # 전략
    │   └── signals.py             # 신호
    ├── ml_platform/               # ML 플랫폼 도메인
    │   ├── __init__.py
    │   └── ml/                    # ML 엔드포인트
    ├── gen_ai/                    # Gen AI 도메인
    │   ├── __init__.py
    │   └── strategy/              # AI 전략 생성
    ├── user/                      # 사용자 도메인
    │   ├── __init__.py
    │   ├── watchlists.py          # 관심 종목
    │   └── dashboard.py           # 대시보드
    └── system/                    # 시스템 도메인
        ├── __init__.py
        └── health.py              # 헬스체크
```

---

## 🏷️ API Tags & Prefixes

### Main API Router (`/api`)

| Tag           | Prefix           | Description               | Router Source          |
|---------------|------------------|---------------------------|------------------------|
| Market Data   | `/market-data`   | 마켓 데이터 API           | `market_data_router`   |
| Backtest      | `/backtests`     | 백테스트 실행 및 관리     | `backtests_router`     |
| Strategy      | `/strategies`    | 전략 템플릿 및 설정       | `strategies_router`    |
| Signals       | `/signals`       | 트레이딩 신호             | `signals_router`       |
| ML            | `/ml`            | 머신러닝 모델 및 학습     | `ml_router`            |
| Gen AI        | `/gen-ai`        | AI 기반 전략 생성         | `gen_ai_router`        |
| Watchlist     | `/watchlists`    | 사용자 관심 종목 관리     | `watchlists_router`    |
| Dashboard     | `/dashboard`     | 사용자 대시보드           | `dashboard_router`     |
| System        | `/system`        | 시스템 상태 및 헬스체크   | `system_router`        |

### Market Data Sub-Routes (`/api/market-data`)

| Sub-Prefix              | Description              | Endpoints                          |
|-------------------------|--------------------------|------------------------------------|
| `/stock`                | 주식 데이터              | daily, weekly, monthly, quote      |
| `/crypto`               | 암호화폐 데이터          | prices, exchange rates             |
| `/fundamental`          | 기본 재무 데이터         | company overview, financials       |
| `/economic_indicators`  | 경제 지표                | GDP, inflation, unemployment       |
| `/intelligence`         | 시장 인텔리전스          | news, sentiment, topics            |
| `/management`           | 데이터 관리              | coverage, quality, refresh         |
| `/tech_indicators`      | 기술적 지표              | SMA, EMA, RSI, MACD, etc.          |
| `/regime`               | 시장 국면 분석           | regime detection, transitions      |

### Trading Sub-Routes

| Router              | Prefix         | Description                  |
|---------------------|----------------|------------------------------|
| `backtests_router`  | `/backtests`   | 백테스트 CRUD, 실행, 결과    |
| `strategies_router` | `/strategies`  | 전략 템플릿, 파라미터 최적화 |
| `signals_router`    | `/signals`     | 실시간 신호, 알림            |

---

## 🔧 Router 통합 흐름

```
main.py (FastAPI app)
    ↓
app/api/__init__.py (api_router)
    ↓
app/api/routes/__init__.py (domain routers)
    ↓
app/api/routes/{domain}/__init__.py (sub-routers)
    ↓
app/api/routes/{domain}/{endpoint}.py (endpoint implementations)
```

### Example: Stock Data Request Flow

```
GET /api/market-data/stock/daily/{symbol}
    ↓
api_router (prefix="/api")
    ↓
market_data_router (prefix="/market-data", tag="Market Data")
    ↓
stock_router (prefix="/stock")
    ↓
get_daily_prices() endpoint
    ↓
StockService.get_daily_prices()
    ↓
Fetcher → Storage → Coverage (modular architecture)
```

---

## 📋 도메인별 책임 분리

### Market Data Domain
- **목적**: 외부 마켓 데이터 제공
- **데이터 소스**: Alpha Vantage API
- **캐싱**: MongoDB + DuckDB
- **주요 서비스**: StockService, CryptoService, IntelligenceService

### Trading Domain
- **목적**: 백테스트 및 전략 실행
- **엔진**: Backtest Orchestrator
- **상태 관리**: MongoDB (결과 저장)
- **주요 서비스**: BacktestService, StrategyService, SignalService

### ML Platform Domain
- **목적**: 머신러닝 모델 학습 및 예측
- **프레임워크**: scikit-learn, Prophet
- **모델 관리**: ModelRegistry
- **주요 서비스**: MLTrainer, ModelLifecycleService

### Gen AI Domain
- **목적**: AI 기반 전략 자동 생성
- **모델**: OpenAI GPT-4
- **검증**: 백테스트 자동 실행
- **주요 서비스**: StrategyGeneratorService

### User Domain
- **목적**: 사용자별 설정 및 대시보드
- **인증**: JWT (mysingle-quant)
- **저장소**: MongoDB
- **주요 서비스**: WatchlistService, DashboardService

### System Domain
- **목적**: 시스템 모니터링 및 상태 확인
- **엔드포인트**: `/health`, `/metrics`
- **모니터링**: Data Quality Sentinel

---

## 🔐 인증 및 권한

### Authentication
- **방식**: JWT Bearer Token
- **제공자**: `mysingle-quant.auth`
- **의존성**: `get_current_active_verified_user`

### Router-level Dependencies
```python
# Market data router에 인증 적용
router = APIRouter(dependencies=[Depends(get_current_active_verified_user)])
```

### Endpoint-level Dependencies
```python
@router.get("/stock/daily/{symbol}")
async def get_daily_prices(
    symbol: str,
    current_user: User = Depends(get_current_active_verified_user)
):
    ...
```

---

## 📖 API 문서 접근

- **Swagger UI**: `http://localhost:8500/docs`
- **ReDoc**: `http://localhost:8500/redoc`
- **OpenAPI JSON**: `http://localhost:8500/openapi.json`

---

## 🔄 Phase 2.1 Modularization Progress

### Completed
- ✅ **Phase 2.1a**: `technical_indicator.py` (1464 → 5 files)
- ✅ **Phase 2.1b**: `stock.py` (1241 → 6 files)

### In Progress
- 🔄 **Phase 2.1c**: `intelligence.py` (1163 lines) - NEXT

### Benefits
- **Single Responsibility**: 각 파일이 하나의 명확한 책임
- **Testability**: 모듈별 독립 테스트 가능
- **Maintainability**: 코드 수정 범위 최소화
- **Scalability**: 새 기능 추가 용이

---

## 📝 변경 이력

### 2025-10-15
- **Phase 2.1b 완료**: stock.py 모듈화 (6 files)
- **API 구조 정리**: 도메인별 디렉토리 분리
- **Tag 네이밍 표준화**: Market Data, Trading, ML, Gen AI, User, System

### Previous
- **Phase 2.1a 완료**: technical_indicator.py 모듈화 (5 files)
- **Initial structure**: Monolithic API routes

---

## 🎯 Next Steps (Phase 2.1c)

1. `intelligence.py` 분할 (1163 lines):
   - `news_analyzer.py`: 뉴스 분석
   - `sentiment.py`: 감성 분석
   - `topic_extractor.py`: 주제 추출
   - `aggregator.py`: 데이터 통합

2. 문서 업데이트:
   - API endpoint 상세 문서
   - 도메인별 아키텍처 다이어그램
   - 성능 벤치마크
