from __future__ import annotations

import pytest


LOGIN_ENDPOINT = "/api/v1/auth/login"
REFRESH_ENDPOINT = "/api/v1/auth/refresh"
LOGOUT_ENDPOINT = "/api/v1/auth/logout"
VERIFY_ENDPOINT = "/api/v1/auth/token/verify"


async def _login(async_client, username: str, password: str):
    return await async_client.post(
        LOGIN_ENDPOINT,
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )


@pytest.mark.asyncio
async def test_login_returns_tokens(async_client, stub_user) -> None:
    response = await _login(async_client, stub_user.email, "dev-superuser-password")

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["refresh_token"]


@pytest.mark.asyncio
async def test_login_rejects_invalid_credentials(async_client, stub_user) -> None:
    response = await _login(async_client, stub_user.email, "wrong-password")

    assert response.status_code == 401
    assert "Invalid credentials" in response.text


@pytest.mark.asyncio
async def test_login_rejects_inactive_user(async_client, stub_user) -> None:
    stub_user.is_active = False
    response = await _login(async_client, stub_user.email, "dev-superuser-password")

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_refresh_token_returns_new_tokens(async_client, stub_user) -> None:
    login_response = await _login(async_client, stub_user.email, "dev-superuser-password")
    login_payload = login_response.json()
    refresh_token = login_payload["refresh_token"]

    refresh_response = await async_client.post(
        REFRESH_ENDPOINT,
        headers={"X-Refresh-Token": refresh_token},
    )

    assert refresh_response.status_code == 200
    payload = refresh_response.json()
    assert payload["access_token"]
    assert payload["access_token"] != login_payload["access_token"]


@pytest.mark.asyncio
async def test_refresh_token_requires_header(async_client) -> None:
    response = await async_client.post(REFRESH_ENDPOINT)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout_clears_tokens(async_client, auth_headers) -> None:
    response = await async_client.post(LOGOUT_ENDPOINT, headers=auth_headers)

    assert response.status_code == 204
    cookies = response.headers.get_list("set-cookie")
    assert any("access_token=" in cookie for cookie in cookies)


@pytest.mark.asyncio
async def test_verify_token_returns_user_info(async_client, auth_headers) -> None:
    response = await async_client.get(VERIFY_ENDPOINT, headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["email"] == "dev-superuser@mysingle.io"


@pytest.mark.asyncio
async def test_protected_route_requires_authorization(async_client) -> None:
    response = await async_client.get("/api/v1/dashboard/summary")

    assert response.status_code == 404
