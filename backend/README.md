# Data Service

Market data management microservice for the Quant Backtest Platform.

## Features

- Market data fetching from Alpha Vantage API
- MongoDB storage with Beanie ODM
- Data quality analysis
- FastAPI-based REST API
- Async/await support
- Docker containerization

## Installation

### Using uv (recommended)

```bash
# Install dependencies
uv sync

# Install with development dependencies
uv sync --dev
```

### Using pip

```bash
pip install -e .

# With development dependencies
pip install -e ".[dev]"
```

## Configuration

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Update the following environment variables:
- `MONGODB_URL`: MongoDB connection string
- `ALPHA_VANTAGE_API_KEY`: Your Alpha Vantage API key

## Running the Service

### Using uv

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### Using Docker

```bash
# Build the image
docker build -t data-service .

# Run with docker-compose
docker-compose up
```

## API Documentation

Once the service is running, visit:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## API Endpoints

### Market Data
- `GET /api/v1/market-data/symbols` - Get available symbols
- `GET /api/v1/market-data/data/{symbol}` - Get market data for symbol
- `POST /api/v1/market-data/data/bulk` - Request bulk data
- `GET /api/v1/market-data/coverage/{symbol}` - Get data coverage
- `GET /api/v1/market-data/quality/{symbol}` - Analyze data quality

### Health Check
- `GET /api/v1/health/` - Service health check

## Testing

```bash
# Run tests with uv
uv run pytest

# Run with coverage
uv run pytest --cov=app

# Run specific test file
uv run pytest tests/test_market_data_service.py
```

## Development

### Code Formatting

```bash
# Format code with black
uv run black .

# Lint with ruff
uv run ruff check .

# Type checking with mypy
uv run mypy .
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
uv run pre-commit install

# Run all hooks
uv run pre-commit run --all-files
```

## Architecture

The service follows a layered architecture:

```
app/
├── api/           # FastAPI routes and dependencies
├── core/          # Configuration and settings
├── models/        # Beanie document models
├── schemas/       # Pydantic request/response models
├── services/      # Business logic layer
└── main.py        # FastAPI application entry point
```

## Database Schema

### MarketData Collection
- `symbol`: Stock symbol
- `date`: Trading date
- `open_price`, `high_price`, `low_price`, `close_price`: OHLC prices
- `volume`: Trading volume
- `adjusted_close`: Adjusted closing price
- `dividend_amount`: Dividend amount
- `split_coefficient`: Stock split coefficient

### DataRequest Collection
- `symbol`: Requested symbol
- `start_date`, `end_date`: Date range
- `status`: Request status (pending, completed, failed)
- `records_count`: Number of records fetched

### DataQuality Collection
- `symbol`: Symbol analyzed
- `date_range_start`, `date_range_end`: Analysis period
- `total_records`: Number of records
- `missing_days`: Missing trading days
- `duplicate_records`: Duplicate entries
- `price_anomalies`: Price anomalies detected
- `quality_score`: Overall quality score (0-100)

## License

MIT
