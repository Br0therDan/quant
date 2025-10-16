from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List

import pytest
from unittest.mock import AsyncMock


class _FakeCursor:
    def __init__(self, count: int) -> None:
        self._count = count

    def fetchone(self) -> tuple[int]:
        return (self._count,)


class _FakeConnection:
    def __init__(self, count: int) -> None:
        self._count = count

    def execute(self, _query: str, _params: List[str]) -> _FakeCursor:
        return _FakeCursor(self._count)


@pytest.fixture
def fake_registry(monkeypatch: pytest.MonkeyPatch) -> type:
    class FakeModelRegistry:
        list_return: List[Dict[str, Any]] = [
            {
                "version": "v1",
                "model_type": "signal",
                "created_at": "2024-01-01",
                "metrics": {"accuracy": 0.9},
                "feature_count": 10,
                "num_iterations": 100,
                "feature_names": ["rsi"],
            }
        ]
        info_return: Dict[str, Any] = list_return[0]
        deleted_versions: List[str] = []

        def __init__(self, base_dir: str | Path) -> None:
            self.base_dir = base_dir

        def list_models(self, model_type: str = "signal") -> List[Dict[str, Any]]:
            return self.list_return

        def get_latest_version(self, model_type: str = "signal") -> str | None:
            return self.list_return[-1]["version"] if self.list_return else None

        def get_model_info(self, version: str) -> Dict[str, Any]:
            if version != self.info_return["version"]:
                raise ValueError("model not found")
            return self.info_return

        def delete_model(self, version: str) -> bool:
            self.deleted_versions.append(version)
            return True

    monkeypatch.setattr(
        "app.api.routes.ml_platform.train.ModelRegistry", FakeModelRegistry
    )
    return FakeModelRegistry


@pytest.fixture
def background_task_stub(monkeypatch: pytest.MonkeyPatch) -> AsyncMock:
    task = AsyncMock()
    monkeypatch.setattr(
        "app.api.routes.ml_platform.train._train_model_background", task
    )
    return task


def _patch_database(monkeypatch: pytest.MonkeyPatch, count: int) -> None:
    conn = _FakeConnection(count)
    monkeypatch.setattr(
        "app.api.routes.ml_platform.train.service_factory.get_database_manager",
        lambda: SimpleNamespace(duckdb_conn=conn),
    )


@pytest.mark.asyncio
async def test_train_model_starts_background_task(
    async_client, auth_headers, background_task_stub, monkeypatch
) -> None:
    _patch_database(monkeypatch, count=1)

    response = await async_client.post(
        "/api/v1/ml/train/train",
        headers=auth_headers,
        json={"symbols": ["AAPL"], "lookback_days": 120},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "started"
    background_task_stub.assert_called_once()


@pytest.mark.asyncio
async def test_train_model_returns_not_found_when_symbol_missing(
    async_client, auth_headers, background_task_stub, monkeypatch
) -> None:
    _patch_database(monkeypatch, count=0)

    response = await async_client.post(
        "/api/v1/ml/train/train",
        headers=auth_headers,
        json={"symbols": ["AAPL"]},
    )

    assert response.status_code == 404
    background_task_stub.assert_not_called()


@pytest.mark.asyncio
async def test_list_models_uses_registry(async_client, auth_headers, fake_registry) -> None:
    response = await async_client.get(
        "/api/v1/ml/train/models",
        headers=auth_headers,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == len(fake_registry.list_return)


@pytest.mark.asyncio
async def test_get_model_info_returns_metadata(async_client, auth_headers, fake_registry) -> None:
    response = await async_client.get(
        "/api/v1/ml/train/models/v1",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["version"] == "v1"


@pytest.mark.asyncio
async def test_delete_model_marks_version(async_client, auth_headers, fake_registry) -> None:
    response = await async_client.delete(
        "/api/v1/ml/train/models/v1",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert "deleted" in response.json()["message"].lower()
    assert "v1" in fake_registry.deleted_versions
