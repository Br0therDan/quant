"""Watchlist API route tests."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.config import settings
from app.api.routes import watchlists as watchlists_routes

API_PREFIX = settings.API_PREFIX


@pytest.fixture
def watchlist_service_mock():
    """Create a mock watchlist service with async helpers."""

    service = SimpleNamespace(
        get_watchlist=AsyncMock(),
        create_watchlist=AsyncMock(),
        update_watchlist=AsyncMock(),
        list_watchlists=AsyncMock(),
        delete_watchlist=AsyncMock(),
        get_watchlist_coverage=AsyncMock(),
        setup_default_watchlist=AsyncMock(),
    )
    return service


@pytest.fixture
def client():
    """Synchronous test client that skips heavy application startup."""

    test_app = FastAPI()
    test_app.include_router(
        watchlists_routes.router, prefix=f"{API_PREFIX}/watchlists"
    )
    user = SimpleNamespace(id="user-1")
    test_app.dependency_overrides[
        watchlists_routes.get_current_active_verified_user
    ] = lambda: user

    with TestClient(test_app) as client:
        yield client


def test_create_watchlist_creates_new(client, watchlist_service_mock):
    """POST /watchlists/ should create a new watchlist when it does not exist."""

    watchlist_service_mock.get_watchlist.return_value = None
    watchlist_service_mock.create_watchlist.return_value = SimpleNamespace(
        name="default", symbols=["AAPL"], description=""
    )

    with patch(
        "app.api.routes.watchlists.service_factory.get_watchlist_service",
        return_value=watchlist_service_mock,
    ):
        response = client.post(
            f"{API_PREFIX}/watchlists/",
            json={"symbols": ["AAPL"], "description": "My list"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "default"
    watchlist_service_mock.create_watchlist.assert_awaited_once()


def test_create_watchlist_updates_existing(client, watchlist_service_mock):
    """POST /watchlists/ should update an existing watchlist when found."""

    watchlist_service_mock.get_watchlist.return_value = SimpleNamespace(
        name="default", symbols=["AAPL"], description=""
    )
    watchlist_service_mock.update_watchlist.return_value = SimpleNamespace(
        name="default", symbols=["MSFT"], description="Updated"
    )

    with patch(
        "app.api.routes.watchlists.service_factory.get_watchlist_service",
        return_value=watchlist_service_mock,
    ):
        response = client.post(
            f"{API_PREFIX}/watchlists/",
            json={"symbols": ["MSFT"], "description": "Updated"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["symbols"] == ["MSFT"]
    watchlist_service_mock.update_watchlist.assert_awaited_once()


def test_list_watchlists_returns_summary(client, watchlist_service_mock):
    """GET /watchlists/ should return the user's watchlist summaries."""

    watchlist_service_mock.list_watchlists.return_value = [
        SimpleNamespace(name="default", symbols=["AAPL"], description=""),
        SimpleNamespace(name="growth", symbols=["MSFT"], description="Growth"),
    ]

    with patch(
        "app.api.routes.watchlists.service_factory.get_watchlist_service",
        return_value=watchlist_service_mock,
    ):
        response = client.get(f"{API_PREFIX}/watchlists/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_count"] == 2
    assert {item["name"] for item in payload["watchlists"]} == {"default", "growth"}


def test_get_watchlist_not_found(client, watchlist_service_mock):
    """GET /watchlists/{name} should return 404 for unknown watchlists."""

    watchlist_service_mock.get_watchlist.return_value = None

    with patch(
        "app.api.routes.watchlists.service_factory.get_watchlist_service",
        return_value=watchlist_service_mock,
    ):
        response = client.get(f"{API_PREFIX}/watchlists/missing")

    assert response.status_code == 404


def test_delete_watchlist_returns_message(client, watchlist_service_mock):
    """DELETE /watchlists/{name} should return a confirmation payload."""

    watchlist_service_mock.delete_watchlist.return_value = True

    with patch(
        "app.api.routes.watchlists.service_factory.get_watchlist_service",
        return_value=watchlist_service_mock,
    ):
        response = client.delete(f"{API_PREFIX}/watchlists/default")

    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "default"


def test_get_watchlist_coverage_handles_missing(client, watchlist_service_mock):
    """GET /watchlists/{name}/coverage should map service errors to HTTP codes."""

    watchlist_service_mock.get_watchlist_coverage.return_value = {"error": "Watchlist not found"}

    with patch(
        "app.api.routes.watchlists.service_factory.get_watchlist_service",
        return_value=watchlist_service_mock,
    ):
        response = client.get(f"{API_PREFIX}/watchlists/default/coverage")

    assert response.status_code == 404


def test_setup_default_watchlist(client, watchlist_service_mock):
    """POST /watchlists/setup-default should return information about the default watchlist."""

    watchlist_service_mock.setup_default_watchlist.return_value = SimpleNamespace(
        name="default", symbols=["AAPL", "MSFT"]
    )

    with patch(
        "app.api.routes.watchlists.service_factory.get_watchlist_service",
        return_value=watchlist_service_mock,
    ):
        response = client.post(f"{API_PREFIX}/watchlists/setup-default")

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 2
