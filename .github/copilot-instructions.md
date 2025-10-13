# GitHub Copilot Instructions - 퀀트 백테스트 플랫폼

## 아키텍처 개요

**풀스택 모노레포** 구조의 퀀트 백테스트 플랫폼:

- **Backend**: FastAPI + Beanie ODM + MongoDB (포트 8500) + DuckDB (고성능 캐시)
- **Frontend**: Next.js 15 + React 19 + Material-UI (포트 3000)
- **Shared Package**: `mysingle-quant` - Alpha Vantage API 클라이언트
- **Database Architecture**: 3-Layer Caching (DuckDB → MongoDB → Alpha Vantage)

## 🚨 필수 개발 규칙

### 1. Backend: ServiceFactory 패턴 (절대 규칙)

모든 서비스는 **반드시** `ServiceFactory` 싱글톤으로 접근:

```python
# ✅ CORRECT
from app.services.service_factory import service_factory
market_service = service_factory.get_market_data_service()

# ❌ WRONG - 의존성 주입 깨짐
from app.services.market_data_service import MarketDataService
service = MarketDataService()  # 절대 금지!
```

### 2. Frontend: Custom Hooks 패턴 (절대 규칙)

모든 API 호출은 **반드시** 커스텀 훅으로 접근:

```typescript
// ✅ CORRECT
import { useBacktest } from "@/hooks/useBacktest";
const { backtestList, createBacktest } = useBacktest();

// ❌ WRONG - 컴포넌트에서 직접 호출 금지
import { BacktestService } from "@/client";
const data = await BacktestService.getBacktests();
```

### 3. 포트 설정 (중요!)

- Backend: **8500** (8000 아님!)
- Frontend: **3000**
- API Base URL: `http://localhost:8500`

### 4. 패키지 관리자

- Python: **uv** only (`uv sync`, `uv add`) - pip/poetry 금지
- Node.js: **pnpm** only (`pnpm install`) - npm/yarn 금지

## 핵심 워크플로우

### API 변경 후 클라이언트 재생성 (필수!)

```bash
# OpenAPI 스키마 변경 후 반드시 실행
pnpm gen:client

# 작동 원리:
# 1. backend/app/main.py에서 OpenAPI JSON 추출 (로그 억제)
# 2. frontend/src/openapi.json 저장
# 3. @hey-api/openapi-ts로 TypeScript 클라이언트 생성
# 4. frontend/src/client/ 디렉토리에 자동 생성
```

### 개발 서버 시작

```bash
# 풀스택 동시 실행
pnpm dev

# 개별 실행
pnpm dev:backend   # 포트 8500
pnpm dev:frontend  # 포트 3000
```

### 새 API 엔드포인트 추가

1. **Backend**: `backend/app/api/routes/{domain}/{endpoint}.py` 생성
2. **Backend**: `response_model` 필수, `summary` 필드 금지 (클라이언트 생성 오류
   )
3. **Backend**: 서비스는 `service_factory`로 주입
4. **Regenerate**: `pnpm gen:client` 실행
5. **Frontend**: `frontend/src/hooks/use{Domain}.ts`에 훅 추가
6. **Frontend**: TanStack Query v5 패턴 사용 (`useQuery`, `useMutation`)

## Backend 핵심 패턴

### Beanie ODM 모델 자동 등록

```python
# backend/app/models/{domain}/{model}.py 생성
# backend/app/models/__init__.py에 등록
collections = [MarketData, Company, Strategy, Backtest, ...]

# main.py에서 자동 등록
app = create_fastapi_app(
    document_models=models.collections,  # 자동 등록
)
```

### DuckDB 3-Layer Caching

```
Request → DuckDB (L1, 24h TTL) → MongoDB (L2) → Alpha Vantage (L3)
            ↓ Hit                ↓ Hit            ↓ Fetch
         Return              Return           Cache & Return
```

- **DuckDB**: 시계열 데이터 고속 캐시 (10-100배 성능)
- **MongoDB**: 메타데이터, 설정
- **Alpha Vantage**: 외부 API (5 calls/min, 자동 제한)

### 서비스 초기화 순서 (중요!)

```python
# backend/app/main.py의 lifespan에서
database_manager = service_factory.get_database_manager()  # 1. DuckDB 연결
service_factory.get_market_data_service()  # 2. DuckDB 주입
service_factory.get_backtest_service()     # 3. 의존성 연결
```

## Frontend 핵심 패턴

### TanStack Query v5 상태 관리

```typescript
// frontend/src/hooks/useBacktest.ts 패턴
export const backtestQueryKeys = {
  all: ["backtest"] as const,
  lists: () => [...backtestQueryKeys.all, "list"] as const,
  detail: (id: string) => [...backtestQueryKeys.all, "detail", id] as const,
};

// Query (읽기)
const backtestListQuery = useQuery({
  queryKey: backtestQueryKeys.lists(),
  queryFn: async () => (await BacktestService.getBacktests()).data,
  staleTime: 1000 * 60 * 5, // 5분
});

// Mutation (쓰기)
const createBacktestMutation = useMutation({
  mutationFn: (data: BacktestCreate) =>
    BacktestService.createBacktest({ body: data }),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: backtestQueryKeys.lists() });
    showSuccess("백테스트가 생성되었습니다");
  },
});
```

### Material-UI 스낵바 패턴

```typescript
import { useSnackbar } from "@/contexts/SnackbarContext";
const { showSuccess, showError } = useSnackbar();

// 성공/에러 알림
showSuccess("작업 완료!");
showError("오류 발생!");
```

## 프로젝트별 컨벤션

### API 엔드포인트 규칙

```python
# ✅ CORRECT
@router.get("/{symbol}", response_model=DataResponse)
async def get_data(symbol: str):
    service = service_factory.get_market_data_service()
    return await service.get_data(symbol)

# ❌ WRONG
@router.get("/{symbol}", summary="Get data")  # summary 금지!
```

### 코드 품질 도구

```bash
# Backend
cd backend && uv run ruff format    # 포맷
cd backend && uv run ruff check     # 린트
cd backend && uv run pytest         # 테스트

# Frontend
pnpm lint:fix                       # Biome 포맷+린트
pnpm build                          # TypeScript 체크
```

### 전략 시스템 아키텍처

```python
# 기본 클래스: backend/app/services/strategy_service/base_strategy.py
# 구현체: backend/app/strategies/{strategy_name}.py
# 시드: backend/app/utils/seed.py의 seed_strategy_templates()
```

## 중요 파일 위치

- **ServiceFactory**: `backend/app/services/service_factory.py`
- **API Routes**: `backend/app/api/routes/__init__.py` (자동 통합)
- **Models**: `backend/app/models/__init__.py` (collections 리스트)
- **Client Config**: `frontend/src/runtimeConfig.ts` (API base URL)
- **Hooks**: `frontend/src/hooks/use{Domain}.ts` (TanStack Query)
- **Client Gen**: `scripts/generate-client.sh` (로그 억제)

## 환경 변수

```bash
# .env 파일
ALPHA_VANTAGE_API_KEY=your_api_key
MONGODB_SERVER=localhost:27019
DUCKDB_PATH=./app/data/quant.duckdb
NEXT_PUBLIC_API_BASE_URL=http://localhost:8500
```

## 디버깅 팁

- **DuckDB 캐시**: 자동 처리, 개발자 개입 불필요
- **Alpha Vantage Rate Limit**: 5 calls/min, DuckDB 캐시로 우회
- **서비스 의존성**: 반드시 `service_factory` 사용
- **Query 무효화**: Mutation 성공 시 `invalidateQueries` 필수

## 주요 개선 프로젝트 문서

### Strategy & Backtest 리팩토링 (진행 중)

- **아키텍처 검토**: `docs/backend/strategy_backtest/ARCHITECTURE_REVIEW.md`
  - 현재 시스템 12가지 문제점 분석
  - 개선 방안 및 4단계 로드맵
- **Phase 1 가이드**: `docs/backend/strategy_backtest/REFACTORING_PHASE1.md`
  - 의존성 주입 개선 (즉시 실행)
  - 거래 로직 통합 (중복 제거)
  - 파라미터 타입 안전성 (Pydantic)
- **새 아키텍처**: `docs/backend/strategy_backtest/NEW_ARCHITECTURE.md`
  - 레이어드 아키텍처 설계
  - 핵심 컴포넌트 (Orchestrator, Executor, etc.)
  - 확장 포인트 및 성능 최적화
- **마이그레이션 계획**: `docs/backend/strategy_backtest/MIGRATION_PLAN.md`
  - 무중단 배포 전략
  - 데이터 마이그레이션 스크립트
  - 롤백 절차

상세 가이드: `AGENTS.md`, `backend/AGENTS.md`, `frontend/AGENTS.md`
