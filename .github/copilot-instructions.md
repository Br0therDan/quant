# GitHub Copilot Instructions - 퀀트 백테스트 플랫폼

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
market_service = service_factory.get_market_data_service()
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

### 데이터 흐름

1. **수집**: Alpha Vantage → DuckDB (캐시)
2. **저장**: 메타데이터 → MongoDB
3. **처리**: pandas/vectorbt 백테스트
4. **결과**: MongoDB (BacktestResult)

## 환경 변수

필수 환경 변수 (`.env` 참조):

```
ALPHA_VANTAGE_API_KEY=your_key
MONGODB_URL=mongodb://localhost:27017/quant
DUCKDB_PATH=./data/quant.db
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

- `backend/app/main.py`: FastAPI 앱 + `mysingle_quant` 헬퍼 사용
- `scripts/generate-client.sh`: OpenAPI → TypeScript 클라이언트 생성 (로그 출력
  차단)
- `shared/`: 크로스 서비스 공통 코드 (CLI, config, utils)
