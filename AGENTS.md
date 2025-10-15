# Project-Wide Development Guide for AI Agents

> **Note**: For detailed implementation guides, see:
>
> - [Backend AGENTS.md](./backend/AGENTS.md) - FastAPI service patterns
> - [Frontend AGENTS.md](./frontend/AGENTS.md) - Next.js component patterns

## Project Overview

**Fullstack Monorepo** quantitative trading backtesting platform with:

- **Backend**: FastAPI + MongoDB (port 8500) + DuckDB cache
- **Frontend**: Next.js 15 + React 19 (port 3000)
- **Package Manager**: pnpm workspaces (Node.js), uv (Python)
- **Database Architecture**: MongoDB (metadata) + DuckDB (time series cache) +
  Alpha Vantage (external API)

## Critical Cross-Project Rules

### 1. Port Configuration (MANDATORY)

```bash
Backend:  http://localhost:8500  # NOT 8000
Frontend: http://localhost:3000
```

**Never use port 8000** - breaks frontend-backend communication.

### 2. Package Management

```bash
# ❌ WRONG
npm install    # Use pnpm
pip install    # Use uv
yarn add       # Use pnpm
poetry add     # Use uv

# ✅ CORRECT
pnpm install              # Node.js dependencies
pnpm --filter backend     # Specific workspace
uv sync                   # Python dependencies
uv add package-name       # Add Python package
```

### 3. API Client Regeneration Workflow

**MUST regenerate after ANY backend schema change:**

```bash
# From project root
pnpm gen:client

# This does:
# 1. Download http://localhost:8500/openapi.json
# 2. Save to frontend/src/openapi.json
# 3. Generate TypeScript client in frontend/src/client/
```

### 4. Backend Architecture Pattern

**ALL services accessed via ServiceFactory singleton:**

```python
# ✅ CORRECT
from app.services.service_factory import service_factory
service = service_factory.get_market_data_service()

# ❌ WRONG - breaks DI
from app.services.market_data_service import MarketDataService
service = MarketDataService()
```

### 5. Frontend Architecture Pattern

**ALL API calls through custom hooks:**

```typescript
// ✅ CORRECT
import { useBacktest } from "@/hooks/useBacktests";
const { backtestList } = useBacktest();

// ❌ WRONG - violates hook pattern
import { BacktestService } from "@/client";
const data = await BacktestService.getBacktests();
```

## Development Workflow

### Starting Development Servers

```bash
# Both servers simultaneously
pnpm run:dev

# Individual servers
pnpm run:dev:backend   # Port 8500
pnpm run:dev:frontend  # Port 3000

# Or directly
cd backend && uv run fastapi dev app/main.py --port 8500
cd frontend && pnpm dev
```

### Code Quality & Testing

```bash
# Backend
cd backend
uv run ruff format        # Format Python
uv run ruff check --fix   # Lint Python
uv run mypy app/          # Type check
uv run pytest             # Run tests

# Frontend
cd frontend
pnpm format               # Format TypeScript
pnpm lint:fix             # Lint TypeScript
pnpm build                # Type check (via tsc)
```

## Database Architecture

### 3-Layer Caching Strategy

```
Request → DuckDB (L1, 24h TTL) → MongoDB (L2) → Alpha Vantage (L3)
            ↓ Hit                   ↓ Hit            ↓ Fetch
         Return                  Return          Cache & Return
```

- **DuckDB**: High-performance columnar cache (10-100x faster for analytics)
- **MongoDB**: Metadata, user data, configurations
- **Alpha Vantage**: External market data (5 calls/min rate limit)

### Database Connections

```python
# Backend: Get connections via DatabaseManager
db_manager = service_factory.get_database_manager()
duckdb_conn = db_manager.duckdb_conn  # Sync connection
# MongoDB accessed via Beanie ODM (async)
```

## Environment Variables

Required `.env` file in project root:

```bash
# Alpha Vantage API
ALPHA_VANTAGE_API_KEY=your_api_key

# MongoDB
MONGODB_SERVER=localhost:27019

# DuckDB (backend internal path)
DUCKDB_PATH=./app/data/quant.duckdb

# Backend URL (for frontend)
NEXT_PUBLIC_API_BASE_URL=http://localhost:8500
BACKEND_URL=http://localhost:8500
```

## Common Tasks

### Adding a New API Endpoint

1. **Backend**: Create route in `backend/app/api/routes/{domain}/`
2. **Backend**: Add service method in `backend/app/services/{domain}_service/`
3. **Backend**: Define schemas in `backend/app/schemas/{domain}/`
4. **Backend**: Register models in `backend/app/models/__init__.py` (if needed)
5. **Regenerate**: Run `pnpm gen:client` from root
6. **Frontend**: Create/update hook in `frontend/src/hooks/use{Domain}.ts`
7. **Frontend**: Use hook in components

### Adding a New Model

**Backend:**

```python
# 1. Create model in backend/app/models/{domain}/{model}.py
# 2. Register in backend/app/models/__init__.py
collections = [NewModel, ...]

# 3. Create corresponding schema
# backend/app/schemas/{domain}/{model}.py
```

**Frontend:**

```typescript
// Types auto-generated after pnpm gen:client
import type { NewModel } from "@/client";
```

## Alpha Vantage MCP Integration

Access real-time market data in VS Code via MCP:

```bash
# Test MCP server
python3 scripts/test_mcp_setup.py

# Use in GitHub Copilot Chat
@workspace What is the latest stock price for AAPL?
```

Configured in `.vscode/mcp.json`.

## Critical Pitfalls

### Backend

❌ **Don't use port 8000** ❌ **Don't instantiate services directly** ❌ **Don't
use 'summary' in route decorators** (breaks client generation) ❌ **Don't forget
response_model** in endpoints ❌ **Don't use pip/poetry** (use uv)

### Frontend

❌ **Don't call API services directly** (use custom hooks) ❌ **Don't edit
src/client/** (auto-generated) ❌ **Don't use npm/yarn** (use pnpm) ❌ **Don't
forget to invalidate queries** after mutations ❌ **Don't use console.log for
user feedback** (use Snackbar)

## Project Structure

```
quant/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── api/routes/  # REST endpoints
│   │   ├── models/      # Beanie ODM models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # Business logic
│   │   └── strategies/  # Trading strategies
│   └── AGENTS.md        # Detailed backend guide
├── frontend/            # Next.js application
│   ├── src/
│   │   ├── app/        # Next.js App Router
│   │   ├── client/     # Auto-generated API client
│   │   ├── components/ # React components
│   │   ├── contexts/   # React Context providers
│   │   └── hooks/      # Custom React hooks
│   └── AGENTS.md       # Detailed frontend guide
├── packages/           # Shared packages
│   └── quant-pack/    # mysingle-quant package
├── scripts/           # Build/utility scripts
├── docs/              # Documentation
└── AGENTS.md          # This file
```

## Quick Reference

| Task                  | Command                                           |
| --------------------- | ------------------------------------------------- |
| Start both servers    | `pnpm dev`                                        |
| Start backend only    | `pnpm dev:backend`                                |
| Start frontend only   | `pnpm dev:frontend`                               |
| Regenerate API client | `pnpm gen:client`                                 |
| Install dependencies  | `pnpm install && uv sync`                         |
| Format all code       | `pnpm format && cd backend && uv run ruff format` |
| Run tests             | `cd backend && uv run pytest`                     |
| View API docs         | `http://localhost:8500/docs`                      |

## Documentation Index

- **Backend Details**: [backend/AGENTS.md](./backend/AGENTS.md)

  - ServiceFactory pattern
  - Database architecture
  - Caching strategy
  - API development

- **Frontend Details**: [frontend/AGENTS.md](./frontend/AGENTS.md)

  - Custom hooks pattern
  - State management
  - Component architecture
  - Material-UI patterns

- **GenAI Enhancement**:
  [docs/backend/gen_ai_enhancement/](./docs/backend/gen_ai_enhancement/)
  - [Master Plan](./docs/backend/gen_ai_enhancement/MASTER_PLAN.md) -
    Phase/Sprint 전체 계획
  - [Dashboard](./docs/backend/gen_ai_enhancement/DASHBOARD.md) - 프로젝트 진행
    현황
  - [README](./docs/backend/gen_ai_enhancement/README.md) - 작업 지침 및 문서
    규칙

**문서 작성 규칙** (GenAI Enhancement 프로젝트):

- ✅ **Phase 완료 시만 문서 작성** (`PHASE{N}_COMPLETION_REPORT.md`)
- ❌ **Sprint/Task 완료 시 문서 작성 안 함**
- ✅ **DASHBOARD.md만 업데이트** (체크박스, 진행률, 주요 이슈만)
- ❌ **개별 Task 상세 업데이트 금지** (문서 과다 방지)

- **API Documentation**: `http://localhost:8500/docs` (when backend running)

- **Authentication Flow**: [AUTH_FLOW.md](./AUTH_FLOW.md)

- **Backend README**: [backend/README.md](./backend/README.md)

- **Frontend README**: [frontend/README.md](./frontend/README.md)

---

**For AI Agents**: Always check backend/AGENTS.md and frontend/AGENTS.md for
detailed implementation patterns before making code changes.
