from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from fastapi import HTTPException, Response

from mysingle_quant.auth.authenticate import Authentication, generate_jwt
from mysingle_quant.core.config import settings as core_settings


def _stub_user(**overrides):
    base = {
        "id": "507f1f77bcf86cd799439011",
        "email": "dev-superuser@mysingle.io",
        "is_active": True,
        "is_verified": True,
        "is_superuser": True,
    }
    base.update(overrides)
    return SimpleNamespace(**base)


@pytest.fixture(autouse=True)
def hybrid_transport(monkeypatch: pytest.MonkeyPatch) -> None:
    """Force the authentication layer to operate in hybrid transport mode."""

    monkeypatch.setattr(core_settings, "TOKEN_TRANSPORT_TYPE", "hybrid")


def _token_payload(user_id: str, email: str) -> dict[str, object]:
    return {
        "sub": user_id,
        "email": email,
        "is_active": True,
        "is_superuser": True,
        "is_verified": True,
        "aud": core_settings.DEFAULT_AUDIENCE,
        "iat": int(datetime.now(timezone.utc).timestamp()),
    }


def test_login_returns_tokens_and_sets_cookies(monkeypatch: pytest.MonkeyPatch) -> None:
    auth = Authentication()
    auth.transport_type = "hybrid"
    user = _stub_user()

    response = Response()
    tokens = auth.login(user, response)

    assert tokens is not None
    assert tokens["token_type"] == "bearer"
    cookies = response.headers.getlist("set-cookie")
    assert any(cookie.startswith("access_token") for cookie in cookies)
    assert any(cookie.startswith("refresh_token") for cookie in cookies)


@pytest.mark.parametrize(
    "field",
    ["is_active", "is_verified"],
)
def test_login_rejects_inactive_or_unverified_users(field: str) -> None:
    auth = Authentication()
    auth.transport_type = "hybrid"
    user = _stub_user(**{field: False})

    with pytest.raises(HTTPException):
        auth.login(user, Response())


def test_refresh_token_returns_new_tokens(monkeypatch: pytest.MonkeyPatch) -> None:
    auth = Authentication()
    auth.transport_type = "hybrid"
    user = _stub_user()
    refresh = generate_jwt(_token_payload(user.id, user.email))

    response = Response()
    tokens = auth.refresh_token(refresh, response, transport_type="header")

    assert tokens is not None
    assert tokens["token_type"] == "bearer"
    assert tokens["access_token"] != refresh


def test_refresh_token_raises_on_invalid_payload() -> None:
    auth = Authentication()

    with pytest.raises(HTTPException):
        auth.refresh_token("not-a-token", Response(), transport_type="header")


def test_validate_token_decodes_payload() -> None:
    auth = Authentication()
    token = generate_jwt(_token_payload("507f1f77bcf86cd799439011", "user@test.dev"))

    payload = auth.validate_token(token)

    assert payload["email"] == "user@test.dev"


def test_logout_deletes_cookies() -> None:
    auth = Authentication()
    response = Response()
    response.set_cookie("access_token", "value")
    response.set_cookie("refresh_token", "value")

    auth.logout(response)

    cookies = response.headers.getlist("set-cookie")
    assert any("access_token=" in cookie and "Max-Age=0" in cookie for cookie in cookies)
    assert any("refresh_token=" in cookie and "Max-Age=0" in cookie for cookie in cookies)
