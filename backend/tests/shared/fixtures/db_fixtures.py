"""Database related fixtures."""

from __future__ import annotations

import inspect
from collections.abc import AsyncIterator, Iterator
from unittest.mock import AsyncMock

import duckdb
import pytest


@pytest.fixture
async def mongodb_client() -> AsyncIterator[AsyncMock]:
    """Async mock that mimics the MongoDB client used in services."""

    client = AsyncMock(name="MockMotorClient")
    client.drop_database = AsyncMock(name="drop_database")
    client.close = AsyncMock(name="close")
    try:
        yield client
    finally:
        close_result = client.close()
        if inspect.isawaitable(close_result):
            await close_result


@pytest.fixture
async def clean_db(mongodb_client: AsyncMock) -> AsyncIterator[None]:
    """Ensure the mocked MongoDB database is cleaned after each test."""

    try:
        yield None
    finally:
        drop_result = mongodb_client.drop_database()
        if inspect.isawaitable(drop_result):
            await drop_result


@pytest.fixture
def duckdb_conn(tmp_path) -> Iterator[duckdb.DuckDBPyConnection]:
    """Provide an in-memory DuckDB connection for analytical tests."""

    connection = duckdb.connect(database=":memory:")
    try:
        yield connection
    finally:
        connection.close()
