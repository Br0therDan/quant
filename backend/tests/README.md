# Backend Test Suite Structure

This directory hosts the reorganised backend test suite used in the coverage
expansion initiative documented in `docs/backend/test_implementation`. The
structure follows the micro-service oriented layout introduced in **Phase 0** of
the master plan.

```
tests/
├── README.md
├── __init__.py
├── conftest.py
├── domains/
│   ├── trading/
│   │   ├── api/
│   │   ├── services/
│   │   ├── strategies/
│   │   └── test_trading_e2e.py
│   ├── market_data/
│   │   ├── api/
│   │   ├── services/
│   │   └── test_market_data_e2e.py
│   ├── ml_platform/
│   │   ├── api/
│   │   ├── services/
│   │   └── test_ml_e2e.py
│   ├── gen_ai/
│   │   ├── api/
│   │   ├── services/
│   │   └── test_gen_ai_e2e.py
│   └── user/
│       ├── api/
│       ├── services/
│       └── test_user_e2e.py
└── shared/
    ├── fixtures/
    │   ├── api_fixtures.py
    │   ├── db_fixtures.py
    │   └── mock_fixtures.py
    └── test_service_factory.py (planned)
```

## Phase 0 Automation

The migration of the legacy flat tests into the new domain-aware layout is
performed by `scripts/migrate-tests-phase0.sh`. The script is idempotent and can
be rerun safely.

```
uv run bash scripts/migrate-tests-phase0.sh
```

It will:

1. Create the domain and shared directories when missing.
2. Move the legacy files listed in the master plan mapping table.
3. Leave existing files untouched when they are already in place.

## Fixtures

Shared fixtures now live under `tests/shared/fixtures/` and the root `tests/conftest.py`
registers them via `pytest_plugins` so that they are automatically available in every
test module.

- `api_fixtures.py` – FastAPI test client & authentication helpers.
- `db_fixtures.py` – MongoDB (async mock) and DuckDB in-memory connections.
- `mock_fixtures.py` – External API mocks (Alpha Vantage & OpenAI).

Additional project specific fixtures should be added here to keep the domain
test suites lightweight and consistent.

## Legacy Cleanup Checklist

- [x] Create domain-oriented directories.
- [x] Move ML, trading and market-data tests to their new homes.
- [x] Consolidate duplicate test modules in the old structure.
- [x] Provide automation for future runs.
- [x] Centralise shared fixtures.

Future phases (1-4) will populate the remaining empty directories with detailed
domain tests following the scenarios defined in the master plan.
