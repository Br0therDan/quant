# Backend Development Guide for AI Agents

## Project Overview

This is a **FastAPI-based quantitative trading backtesting platform** with
advanced architecture patterns including ServiceFactory (DI), 3-layer caching
(DuckDB/MongoDB/Alpha Vantage), and domain-driven service design.

## Critical Architecture Rules

### 1. ServiceFactory Pattern (Mandatory)

**ALL services MUST be accessed through the singleton ServiceFactory**

```python
# ✅ CORRECT
from app.services.service_factory import service_factory
market_service = service_factory.get_market_data_service()

# ❌ WRONG - Never instantiate directly
from app.services.market_data_service import MarketDataService
service = MarketDataService()  # This will break dependency injection
```

### 2. Port Configuration

- Backend runs on **port 8500** (NOT 8000)
- Frontend expects backend at `http://localhost:8500`
- Update both frontend config and backend startup if changing

### 3. Database Architecture

#### MongoDB (Async)

- User data, configurations, metadata
- Accessed via Beanie ODM
- Models in `app/models/` auto-registered in `__init__.py`

#### DuckDB (Sync)

- Time series data, analytics cache
- 10-100x faster than MongoDB for analytics
- Integrated through DatabaseManager in ServiceFactory

#### Alpha Vantage API

- External market data source
- Rate limited: 5 calls/min (auto-managed)
- Integrated via `mysingle-quant` package

## Service Layer Structure

### MarketDataService (Domain-Driven)

Access domain-specific services through properties:

```python
market_service = service_factory.get_market_data_service()

# Domain services
market_service.stock          # Stock price data
market_service.fundamental    # Financial statements
market_service.economic      # Economic indicators
market_service.intelligence  # News & sentiment
```

### Other Core Services

```python
backtest_service = service_factory.get_backtest_service()
strategy_service = service_factory.get_strategy_service()
watchlist_service = service_factory.get_watchlist_service()
database_manager = service_factory.get_database_manager()
```

## API Development Guidelines

### 1. Endpoint Pattern

```python
@router.get(
    "/{symbol}",
    response_model=DataResponse,  # REQUIRED
    # NO 'summary' field - breaks client generation
)
async def get_data(symbol: str):
    service = service_factory.get_market_data_service()
    return await service.get_data(symbol)
```

### 2. Model Registration

All Beanie models must be registered in `app/models/__init__.py`:

```python
collections = [
    MarketData,
    Company,
    Strategy,
    Backtest,
    # ... add new models here
]
```

### 3. Schema Organization

- Request schemas: `app/schemas/{domain}/`
- Response schemas: Same location
- Use Pydantic BaseModel
- Include examples for OpenAPI docs

## Caching Strategy

### 3-Layer Cache Flow

```
Request
  ↓
DuckDB Cache (L1) → 24h TTL, columnar storage
  ↓ (miss)
MongoDB Cache (L2) → Configurable TTL
  ↓ (miss)
Alpha Vantage API (L3) → External source
  ↓
Cache & Return
```

### Implementation

```python
# Service handles caching automatically
data = await market_service.stock.get_daily_prices("AAPL")
# Checks: DuckDB → MongoDB → Alpha Vantage → Cache in DuckDB
```

## Common Tasks

### Adding a New Endpoint

1. **Create route** in `app/api/routes/{domain}/`
2. **Add service method** in `app/services/{domain}_service/`
3. **Define schemas** in `app/schemas/{domain}/`
4. **Update models** if needed (register in `__init__.py`)
5. **Regenerate client**: `pnpm gen:client` from project root

### Adding a New Service

1. Create service class in `app/services/`
2. Add getter method in `ServiceFactory`
3. Initialize in `ServiceFactory.__init__`
4. Inject dependencies via constructor

### Debugging DuckDB Queries

```python
# Access DuckDB connection directly
db_manager = service_factory.get_database_manager()
conn = db_manager.duckdb_conn

# Run raw SQL for debugging
result = conn.execute("SELECT * FROM stock_prices LIMIT 5").fetchall()
```

## Data Quality & Validation

### DataQualityMixin

All data models should inherit from `DataQualityMixin`:

```python
from app.utils.data_quality import DataQualityMixin

class MarketData(DataQualityMixin, Document):
    # Automatic validation for:
    # - Negative prices
    # - Infinite values
    # - Missing fields
    # - Type consistency
```

## Testing

### Running Tests

```bash
# All tests
uv run pytest

# Specific module
uv run pytest tests/test_market_data_service.py

# With coverage
uv run pytest --cov=app
```

### Test Patterns

```python
import pytest
from app.services.service_factory import service_factory

@pytest.fixture
def market_service():
    return service_factory.get_market_data_service()

async def test_get_stock_data(market_service):
    data = await market_service.stock.get_daily_prices("AAPL")
    assert data is not None
```

## Rate Limiting

Alpha Vantage API has strict limits:

- **5 calls/minute** (free tier)
- **500 calls/day** (free tier)

Rate limiting is handled automatically by `AlphaVantageClient`. If rate limit is
hit, cached data is returned.

## Error Handling

### Custom Exceptions

```python
from app.utils.exceptions import (
    DataNotFoundError,
    APIRateLimitError,
    ValidationError
)

# In service methods
if not data:
    raise DataNotFoundError(f"No data found for {symbol}")
```

### FastAPI Exception Handlers

Defined in `app/main.py`:

- `DataNotFoundError` → 404
- `APIRateLimitError` → 429
- `ValidationError` → 422

## Environment Variables

Required in `.env`:

```bash
ALPHA_VANTAGE_API_KEY=your_key_here
MONGODB_SERVER=localhost:27019
DUCKDB_PATH=./app/data/quant.duckdb
BACKEND_URL=http://localhost:8500
```

## Code Quality Standards

### Type Hints (Required)

```python
async def get_data(symbol: str, date: Optional[datetime] = None) -> DataResponse:
    """Get market data for symbol."""
    pass
```

### Docstrings (Required for Public Functions)

```python
def calculate_returns(prices: List[float]) -> List[float]:
    """
    Calculate percentage returns from price series.

    Args:
        prices: List of sequential prices

    Returns:
        List of percentage returns

    Raises:
        ValueError: If prices list is empty
    """
    pass
```

### Linting & Formatting

```bash
# Format
uv run ruff format

# Lint
uv run ruff check --fix

# Type check
uv run mypy app/
```

## Common Pitfalls

❌ **Don't instantiate services directly**

```python
service = MarketDataService()  # Wrong
```

❌ **Don't use 'summary' in route decorators**

```python
@router.get("/", summary="Get data")  # Breaks client generation
```

❌ **Don't forget response_model**

```python
@router.get("/")  # Missing response_model
async def get_data(): pass
```

❌ **Don't access DuckDB without ServiceFactory**

```python
import duckdb
conn = duckdb.connect()  # Wrong - use database_manager
```

✅ **Do use ServiceFactory for everything**

```python
service = service_factory.get_market_data_service()
```

✅ **Do register new models**

```python
# In app/models/__init__.py
collections = [..., YourNewModel]
```

✅ **Do regenerate client after schema changes**

```bash
pnpm gen:client
```

## Quick Reference

| Task             | Command                                      |
| ---------------- | -------------------------------------------- |
| Start dev server | `uv run fastapi dev app/main.py --port 8500` |
| Run tests        | `uv run pytest`                              |
| Format code      | `uv run ruff format`                         |
| Lint code        | `uv run ruff check --fix`                    |
| Type check       | `uv run mypy app/`                           |
| Generate client  | `pnpm gen:client`                            |
| View API docs    | `http://localhost:8500/docs`                 |

## Architecture Diagrams

### Service Flow

```
FastAPI Router → ServiceFactory → Service Layer → Database Manager → MongoDB/DuckDB
                                                                   → Alpha Vantage API
```

### Cache Flow

```
Request → DuckDB (L1) → MongoDB (L2) → Alpha Vantage (L3)
             ↓              ↓                ↓
          Return        Return           Fetch & Cache
```

## Additional Notes

- **DuckDB is SYNC**: Use it in sync contexts or with `asyncio.to_thread()`
- **MongoDB is ASYNC**: All Beanie operations are async
- **Alpha Vantage**: Real external API, not mocked (use cache wisely)
- **Auto-registration**: Models, routes auto-discovered (follow conventions)
