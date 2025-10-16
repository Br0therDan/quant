from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any, Dict

import pytest
from unittest.mock import AsyncMock

from app.models.trading.backtest import (
    BacktestConfig,
    PerformanceMetrics,
    Position,
    Trade,
)
from app.schemas.enums import BacktestStatus, TradeType


def _config_payload(**overrides: Any) -> Dict[str, Any]:
    base: Dict[str, Any] = {
        "name": "Momentum Backtest",
        "description": "Config for momentum backtest",
        "start_date": datetime(2024, 1, 1, tzinfo=timezone.utc).isoformat(),
        "end_date": datetime(2024, 6, 1, tzinfo=timezone.utc).isoformat(),
        "symbols": ["AAPL", "MSFT"],
        "initial_cash": 100_000.0,
        "max_position_size": 0.2,
        "commission_rate": 0.001,
        "slippage_rate": 0.0005,
        "rebalance_frequency": "monthly",
        "tags": ["momentum"],
    }
    base.update(overrides)
    return base


def _backtest_payload(**overrides: Any) -> SimpleNamespace:
    base: Dict[str, Any] = {
        "id": "bt-1",
        "name": "Momentum Backtest",
        "description": "Test backtest",
        "config": BacktestConfig(
            **{
                **_config_payload(),
                "start_date": datetime(2024, 1, 1, tzinfo=timezone.utc),
                "end_date": datetime(2024, 6, 1, tzinfo=timezone.utc),
            }
        ),
        "status": BacktestStatus.PENDING,
        "start_time": datetime.now(timezone.utc),
        "end_time": None,
        "duration_seconds": None,
        "performance": PerformanceMetrics(
            total_return=12.5,
            annualized_return=20.0,
            volatility=5.0,
            sharpe_ratio=1.4,
            max_drawdown=3.0,
            total_trades=10,
            winning_trades=6,
            losing_trades=4,
            win_rate=0.6,
        ),
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "user_id": "507f1f77bcf86cd799439011",
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def _execution_payload(**overrides: Any) -> SimpleNamespace:
    base: Dict[str, Any] = {
        "id": "exec-1",
        "backtest_id": "bt-1",
        "execution_id": "run-1",
        "start_time": datetime.now(timezone.utc),
        "end_time": datetime.now(timezone.utc),
        "status": BacktestStatus.COMPLETED,
        "portfolio_values": [100000.0, 101200.0],
        "trades": [
            Trade(
                trade_id="trade-1",
                symbol="AAPL",
                trade_type=TradeType.BUY,
                quantity=10,
                price=150.0,
                timestamp=datetime.now(timezone.utc),
            )
        ],
        "positions": {
            "AAPL": Position(
                symbol="AAPL",
                quantity=10,
                avg_price=150.0,
                current_price=155.0,
                unrealized_pnl=50.0,
                realized_pnl=0.0,
                first_buy_date=datetime.now(timezone.utc),
            )
        },
        "error_message": None,
        "created_at": datetime.now(timezone.utc),
    }
    base.update(overrides)
    return SimpleNamespace(**base)


@pytest.fixture
def backtest_service_stub(monkeypatch: pytest.MonkeyPatch) -> SimpleNamespace:
    service = SimpleNamespace(
        create_backtest=AsyncMock(),
        get_backtests=AsyncMock(),
        get_backtest=AsyncMock(),
        update_backtest=AsyncMock(),
        delete_backtest=AsyncMock(),
        get_backtest_executions=AsyncMock(),
        get_backtest_results=AsyncMock(),
    )
    monkeypatch.setattr(
        "app.api.routes.trading.backtests.backtests.service_factory.get_backtest_service",
        lambda: service,
    )
    return service


@pytest.fixture
def orchestrator_stub(monkeypatch: pytest.MonkeyPatch) -> SimpleNamespace:
    orchestrator = SimpleNamespace(execute_backtest=AsyncMock())
    monkeypatch.setattr(
        "app.api.routes.trading.backtests.backtests.service_factory.get_backtest_orchestrator",
        lambda: orchestrator,
    )
    return orchestrator


@pytest.mark.asyncio
async def test_create_backtest_returns_payload(async_client, auth_headers, backtest_service_stub) -> None:
    backtest_service_stub.create_backtest.return_value = _backtest_payload()

    response = await async_client.post(
        "/api/v1/backtests/",
        headers=auth_headers,
        json={
            "name": "Momentum Backtest",
            "description": "Test backtest",
            "config": _config_payload(),
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Momentum Backtest"
    backtest_service_stub.create_backtest.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_backtests_returns_collection(async_client, auth_headers, backtest_service_stub) -> None:
    backtest_service_stub.get_backtests.return_value = [_backtest_payload(id="bt-2")]

    response = await async_client.get("/api/v1/backtests/", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["total"] == 1


@pytest.mark.asyncio
async def test_get_backtest_handles_not_found(async_client, auth_headers, backtest_service_stub) -> None:
    backtest_service_stub.get_backtest.return_value = None

    response = await async_client.get("/api/v1/backtests/bt-missing", headers=auth_headers)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_backtest_enforces_ownership(async_client, auth_headers, backtest_service_stub) -> None:
    backtest_service_stub.get_backtest.return_value = _backtest_payload(user_id="someone-else")

    response = await async_client.get("/api/v1/backtests/bt-1", headers=auth_headers)

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_backtest_returns_updated_model(async_client, auth_headers, backtest_service_stub) -> None:
    existing = _backtest_payload()
    updated = _backtest_payload(name="Updated Backtest")
    backtest_service_stub.get_backtest.return_value = existing
    backtest_service_stub.update_backtest.return_value = updated

    response = await async_client.put(
        "/api/v1/backtests/bt-1",
        headers=auth_headers,
        json={
            "name": "Updated Backtest",
            "config": _config_payload(name="Updated Config"),
        },
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Backtest"


@pytest.mark.asyncio
async def test_delete_backtest_returns_confirmation(async_client, auth_headers, backtest_service_stub) -> None:
    backtest_service_stub.get_backtest.return_value = _backtest_payload()
    backtest_service_stub.delete_backtest.return_value = True

    response = await async_client.delete("/api/v1/backtests/bt-1", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["message"]


@pytest.mark.asyncio
async def test_execute_backtest_uses_orchestrator(async_client, auth_headers, backtest_service_stub, orchestrator_stub) -> None:
    backtest_service_stub.get_backtest.return_value = _backtest_payload()
    orchestrator_stub.execute_backtest.return_value = True
    backtest_service_stub.get_backtest_executions.return_value = [_execution_payload()]

    response = await async_client.post(
        "/api/v1/backtests/bt-1/execute",
        headers=auth_headers,
        json={
            "signals": [
                {
                    "symbol": "AAPL",
                    "action": "BUY",
                    "quantity": 10,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ]
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == BacktestStatus.COMPLETED.value
    orchestrator_stub.execute_backtest.assert_awaited_once_with(backtest_id="bt-1")


@pytest.mark.asyncio
async def test_get_backtest_executions_returns_history(async_client, auth_headers, backtest_service_stub) -> None:
    backtest_service_stub.get_backtest.return_value = _backtest_payload()
    backtest_service_stub.get_backtest_executions.return_value = [_execution_payload()]

    response = await async_client.get(
        "/api/v1/backtests/bt-1/executions",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1


@pytest.mark.asyncio
async def test_performance_analytics_returns_summary(async_client, auth_headers, backtest_service_stub) -> None:
    backtest_service_stub.get_backtest_results.return_value = [
        SimpleNamespace(
            backtest_id="bt-1",
            performance=SimpleNamespace(total_return=10.0, sharpe_ratio=1.2),
        ),
        SimpleNamespace(
            backtest_id="bt-2",
            performance=SimpleNamespace(total_return=20.0, sharpe_ratio=1.8),
        ),
    ]

    response = await async_client.get(
        "/api/v1/backtests/analytics/performance-stats",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["analytics"]["total_backtests"] == 2
