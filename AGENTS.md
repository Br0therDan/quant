# ## 아키텍쳐 개요

이 프로젝트는 **풀스택 모노레포** 구조의 퀸트 백테스트 플랫폼입니다:

- **Backend**: FastAPI + Beanie ODM + MongoDB (포트 8000)
- **Frontend**: Next.js 15 + React 19 + Material-UI (포트 3000)
- **Database**: MongoDB (메타데이터) + DuckDB (고성능 시계열 캐시)
- **Architecture**: ServiceFactory 패턴 + 하이브리드 데이터베이스Copilot
  Instructions - 퀀트 백테스트 플랫폼

## 아키텍처 개요

이 프로젝트는 **풀스택 모노레포** 구조의 퀀트 백테스트 플랫폼입니다:

- **Backend**: FastAPI + Beanie ODM + MongoDB (포트 8000)
- **Frontend**: Next.js 15 + React 19 + Material-UI (포트 3000)
- **Database**: MongoDB (메타데이터) + DuckDB (시계열 캐시)

## 핵심 개발 패턴

### 1. 서비스 팩토리 패턴

모든 서비스는 `ServiceFactory` 싱글톤을 통해 의존성 주입됩니다:

```python
# backend/app/services/service_factory.py 사용
from app.services.service_factory import service_factory

# DuckDB 연동된 서비스 인스턴스 가져오기
market_service = service_factory.get_market_data_service()  # DuckDB 캐시 포함
backtest_service = service_factory.get_backtest_service()   # DuckDB 결과 저장
database_manager = service_factory.get_database_manager()   # DuckDB 직접 접근
```

### 2. Beanie ODM 모델 패턴

MongoDB 문서는 `backend/app/models/`에 정의되며 `__init__.py`의 `collections`
리스트에 등록:

```python
# models/__init__.py에서 자동 등록
collections = [MarketData, Company, Strategy, Backtest, ...]
```

### 3. API 라우터 구조

모든 API는 `backend/app/api/routes/`에서 정의되고 `__init__.py`에서 통합:

```python
# api/__init__.py에서 라우터 자동 포함
api_router.include_router(market_data_router)
```

## 필수 개발 워크플로우

### API 클라이언트 생성

OpenAPI 스키마 변경 시 TypeScript 클라이언트 재생성:

```bash
pnpm gen:client  # 또는 ./scripts/generate-client.sh
```

### 개발 서버 실행

```bash
# 백엔드만:
pnpm run:dev:backend
# 프론트엔드만:
pnpm run:dev:frontend
# Docker 전체 스택:
pnpm run:docker
```

### Docker Desktop 실행

```bash
# Docker Desktop에서 전체 스택 실행
pnpm run:docker
# 프론트엔드만:
pnpm run:dev:frontend
# 백엔드만:
pnpm run:dev:backend
```

### 패키지 관리

- **Python**: UV 워크스페이스 (`uv sync`, `uv add`)
- **Node.js**: pnpm 워크스페이스 (`pnpm install`, `pnpm --filter`)

## 프로젝트별 컨벤션

### Alpha Vantage API 통합

- Rate limiting: 5 calls/min (자동 처리)
- 캐싱: DuckDB에 24시간 TTL
- 클라이언트: `services/data_service/alpha_vantage_client.py`

### 전략 시스템

- 기본 클래스: `services/strategy_service/base_strategy.py`
- 구현체: `backend/app/strategies/` (SMA, RSI, Momentum 등)
- 템플릿: MongoDB에 시드됨 (`seed_strategy_templates()`)

### DuckDB 통합 데이터 흐름

1. **수집 계층**: Alpha Vantage API → DuckDB 캐시 (고속)
2. **메타데이터**: 전략, 설정 → MongoDB
3. **분석 처리**: DuckDB 컬럼나 엔진 (10-100배 빠름)
4. **결과 저장**: 백테스트 결과 → DuckDB + MongoDB 이중 저장
5. **투명한 캐싱**: API 사용자는 캐시 로직을 신경 쓸 필요 없음

## 환경 변수

필수 환경 변수 (`.env` 참조):

```
ALPHA_VANTAGE_API_KEY=your_key
MONGODB_URL=mongodb://localhost:27017/quant
DUCKDB_PATH=./backend/app/data/quant.duckdb  # 백엔드 애플리케이션 내부
```

## 테스트 패턴

- **Backend**: `pytest backend/tests/` (FastAPI TestClient)
- **Frontend**: Material-UI + React 19 패턴
- **통합**: Docker Compose로 전체 스택 테스트

## 코드 품질

- **Python**: `ruff format`, `ruff check`, `mypy`
- **TypeScript**: `biome check`, `biome format`
- 모든 public 함수는 docstring 필수, 타입힌트 필수

## 특별한 파일들

- `backend/app/main.py`: FastAPI 앱 + DuckDB 사전 초기화 + ServiceFactory 통합
  관리
- `backend/app/services/service_factory.py`: 서비스 의존성 주입 및 DuckDB 연동
  중앙 제어
- `backend/app/services/database_manager.py`: DuckDB 스키마 및 데이터 관리 전담
- `backend/app/data/`: DuckDB 데이터 파일 저장소 (자동 생성)
- `scripts/generate-client.sh`: OpenAPI → TypeScript 클라이언트 생성 (로그 출력
  차단)
- `shared/`: 크로스 서비스 공통 코드 (CLI, config, utils)

## DuckDB 통합 개발 패턴

### 자동 초기화

```python
# main.py - 애플리케이션 시작 시 DuckDB 사전 초기화
@asynccontextmanager
async def lifespan(app: FastAPI):
    # DuckDB 및 모든 서비스 사전 초기화
    database_manager = service_factory.get_database_manager()
    service_factory.get_market_data_service()  # DuckDB 캐시 연동
    service_factory.get_backtest_service()     # DuckDB 결과 저장
```

### 투명한 캐싱 사용

```python
# MarketDataService - 자동 DuckDB 캐시 처리
async def get_market_data(symbol, start_date, end_date, force_refresh=False):
    # 1. DuckDB 캐시 먼저 확인 (밀리초 단위)
    # 2. 캐시 미스 시 MongoDB 확인
    # 3. 최종적으로 Alpha Vantage API 호출
    # 4. 결과를 DuckDB + MongoDB에 자동 저장
```

### 고성능 분석 API

```python
# 새로운 DuckDB 기반 분석 엔드포인트
GET /api/v1/market-data/analytics/cache-performance
GET /api/v1/backtests/analytics/performance-stats
GET /api/v1/backtests/analytics/trades
```
