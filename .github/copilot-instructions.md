# GitHub Copilot Instructions - 퀀트 백테스트 플랫폼

## 아키텍처 개요

이 프로젝트는 **풀스택 모노레포** 구조의 퀀트 백테스트 플랫폼입니다:

- **Backend**: FastAPI + Beanie ODM + MongoDB (포트 8500) + DuckDB (고성능 캐시)
- **Frontend**: Next.js 15 + React 19 + Material-UI (포트 3000)
- **Shared Package**: `mysingle-quant` - 크로스 서비스 공통 코드 (Alpha Vantage
  클라이언트 포함)
- **Database Architecture**: MongoDB (메타데이터) + DuckDB (시계열 데이터 캐시)

## 핵심 개발 패턴

### 1. 서비스 팩토리 패턴 (Singleton + Dependency Injection)

모든 서비스는 `ServiceFactory` 싱글톤을 통해 의존성 주입됩니다:

```python
# backend/app/services/service_factory.py 사용
from app.services.service_factory import service_factory

# DuckDB 연동된 서비스 인스턴스 가져오기
market_service = service_factory.get_market_data_service()  # DuckDB 캐시 포함
backtest_service = service_factory.get_backtest_service()   # DuckDB 결과 저장
database_manager = service_factory.get_database_manager()   # DuckDB 직접 접근

# 새로운 도메인별 아키텍처
fundamental_service = service_factory.get_fundamental_service()
intelligence_service = service_factory.get_intelligence_service()
```

### 2. 도메인별 아키텍처

MarketDataService는 도메인별로 분리된 서비스들을 제공합니다:

```python
# backend/app/services/market_data_service/__init__.py
class MarketDataService:
    @property
    def stock(self) -> StockService:          # 주식 데이터
    @property
    def fundamental(self) -> FundamentalService:  # 재무 데이터
    @property
    def economic(self) -> EconomicIndicatorService:  # 경제 지표
    @property
    def intelligence(self) -> IntelligenceService:   # 뉴스/감정 분석
```

### 3. Beanie ODM 모델 자동 등록 패턴

MongoDB 문서는 `backend/app/models/` 하위 모듈에 정의되며 `__init__.py`의
`collections` 리스트에 자동 등록:

```python
# models/__init__.py에서 자동 등록
collections = [MarketData, Company, Strategy, Backtest, ...]
```

### 4. Alpha Vantage API 통합 패턴

`mysingle-quant` 패키지의 `AlphaVantageClient`를 사용하여 실제 외부 API 연동:

```python
from mysingle_quant import AlphaVantageClient

# Rate limiting: 5 calls/min (자동 처리)
# 캐싱: DuckDB에 24시간 TTL
# 실제 API 예시: OVERVIEW, INCOME_STATEMENT, REAL_GDP, NEWS_SENTIMENT
```

## 필수 개발 워크플로우

### 백엔드 포트 변경 (중요!)

**백엔드는 포트 8500에서 실행됩니다** (8000 아님):

```bash
# 백엔드 개발 서버 (포트 8500)
pnpm run:dev:backend
# 또는 직접
cd backend && uv run fastapi dev app/main.py --host 0.0.0.0 --port 8500
```

### API 클라이언트 생성 워크플로우

OpenAPI 스키마 변경 시 TypeScript 클라이언트 재생성이 **필수**:

```bash
pnpm gen:client  # 또는 ./scripts/generate-client.sh
# → frontend/src/client/ 디렉토리에 자동 생성
```

### Alpha Vantage MCP 서버 사용

VS Code에서 GitHub Copilot과 함께 실시간 Alpha Vantage 데이터에 접근:

```bash
# MCP 서버 테스트
python3 scripts/test_mcp_setup.py

# GitHub Copilot Chat에서 사용:
# @workspace /mcp-alphavantage AAPL의 최근 주가 정보를 가져와주세요
```

### 패키지 관리 규칙

- **Python**: UV 워크스페이스 (`uv sync`, `uv add`) - pip/poetry 사용 금지
- **Node.js**: pnpm 워크스페이스 (`pnpm install`, `pnpm --filter`) - npm/yarn
  사용 금지

## 프로젝트별 컨벤션

### DuckDB 하이브리드 데이터 흐름

1. **수집**: Alpha Vantage API → DuckDB 캐시 (고속 컬럼나 저장)
2. **메타데이터**: 설정, 사용자 데이터 → MongoDB
3. **분석**: DuckDB 컬럼나 엔진 (10-100배 성능 향상)
4. **결과**: 백테스트 결과 → DuckDB + MongoDB 이중 저장

### 전략 시스템 패턴

```python
# 기본 클래스: services/strategy_service/base_strategy.py
# 구현체: backend/app/strategies/ (SMA, RSI, Momentum 등)
# 템플릿: MongoDB에 시드됨 (seed_strategy_templates())
```

### API 라우터 자동 통합

```python
# backend/app/api/routes/__init__.py에서 자동 포함
api_router.include_router(market_data_router)
api_router.include_router(backtests_router)
api_router.include_router(strategies_router)
```

## 환경 변수 및 설정

```bash
# 필수 환경변수 (.env)
ALPHA_VANTAGE_API_KEY=M9TJCCBXW5PJZ3HF
MONGODB_SERVER=localhost:27019
DUCKDB_PATH=./app/data/quant.duckdb  # 백엔드 내부 경로
BACKEND_URL=http://localhost:8500   # 포트 8500!
```

## 엔드포인트 코드 패턴 주의사항

-

```python
@router.get(
    "/item",
    response_model=ItemResponse
)
async def get_item():
```

- `summary` 필드는 제거해주세요. summary는 자동으로 생성되며, 이는 hey-api
  클라이언트생성시 파싱되어 메서드명으로 사용됩니다.

## 코드 품질 및 테스트

- **Python**: `ruff format`, `ruff check`, `mypy` (pyproject.toml 설정)
- **TypeScript**: `biome check`, `biome format` (biome.json 설정)
- **테스트**: `pytest backend/tests/` (FastAPI TestClient)
- **타입 안전성**: 모든 public 함수는 docstring + 타입힌트 필수

## 특별한 파일들

- `backend/app/main.py`: FastAPI 앱 + ServiceFactory 사전 초기화 + DuckDB 연결
- `backend/app/services/service_factory.py`: 중앙 의존성 주입 관리자
- `packages/quant-pack/`: mysingle-quant 공유 패키지 (Alpha Vantage 클라이언트)
- `scripts/generate-client.sh`: OpenAPI → TypeScript 자동 생성 (로그 차단됨)
- `.vscode/mcp.json`: Alpha Vantage MCP 서버 설정 (uvx av-mcp)

## 디버깅 및 개발 팁

### 서비스 팩토리 초기화 순서

```python
# main.py에서 startup 시 사전 초기화
database_manager = service_factory.get_database_manager()
market_service = service_factory.get_market_data_service()  # DuckDB 의존성 주입
backtest_service = service_factory.get_backtest_service()   # 모든 의존성 연결
```

### DuckDB 캐시 패턴

모든 시계열 데이터는 DuckDB에 자동 캐시되며, 서비스 레이어에서 투명하게
처리됩니다. 개발자는 캐시 로직을 신경 쓸 필요가 없습니다.

### Alpha Vantage Rate Limiting

API 호출이 자동으로 5 calls/min으로 제한되며, DuckDB 캐시를 통해 성능이
최적화됩니다.
