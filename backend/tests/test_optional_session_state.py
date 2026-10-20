from collections.abc import Iterable
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi.testclient import TestClient

import main
from app.database import get_db
from app.models.note import User
from app.models.session import AdminSession
from app.utils.auth import hash_session_token


class _ScalarResult:
    def __init__(self, value):
        self.value = value

    def scalar_one_or_none(self):
        return self.value


class _ResolverDb:
    def __init__(self, responses: Iterable[object]):
        self._responses = iter(responses)

    async def execute(self, _statement):
        response = next(self._responses)
        if isinstance(response, BaseException):
            raise response
        return _ScalarResult(response)


def _request_with_db(path: str, db: _ResolverDb, *, cookie: str | None = None):
    async def override_get_db():
        yield db

    main.app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(main.app, raise_server_exceptions=False) as client:
            if cookie:
                client.cookies.set("admin_session", cookie)
            return client.get(path)
    finally:
        main.app.dependency_overrides.pop(get_db, None)


def _admin_user() -> User:
    return User(
        id=UUID("00000000-0000-0000-0000-000000000001"),
        username="isolated-admin",
        password_hash="disabled",
        is_admin=True,
    )


def _session(token: str, *, expires_at: datetime) -> AdminSession:
    return AdminSession(
        user_id=UUID("00000000-0000-0000-0000-000000000001"),
        token_hash=hash_session_token(token),
        auth_level="password",
        expires_at=expires_at,
        revoked=False,
    )


def test_optional_session_state_returns_anonymous_200_without_cookie():
    response = _request_with_db("/api/auth/session-state", _ResolverDb([]))

    assert response.status_code == 200
    assert response.json() == {"authenticated": False, "is_admin": False}


def test_optional_session_state_returns_minimal_admin_state_for_valid_cookie():
    token = "isolated-valid-session"
    response = _request_with_db(
        "/api/auth/session-state",
        _ResolverDb([_session(token, expires_at=datetime.now(timezone.utc) + timedelta(days=1)), _admin_user()]),
        cookie=token,
    )

    assert response.status_code == 200
    assert response.json() == {"authenticated": True, "is_admin": True}


def test_optional_session_state_downgrades_expired_cookie_to_anonymous():
    token = "isolated-expired-session"
    response = _request_with_db(
        "/api/auth/session-state",
        _ResolverDb([_session(token, expires_at=datetime.now(timezone.utc) - timedelta(seconds=1))]),
        cookie=token,
    )

    assert response.status_code == 200
    assert response.json() == {"authenticated": False, "is_admin": False}


def test_optional_session_state_keeps_infrastructure_failure_visible():
    response = _request_with_db(
        "/api/auth/session-state",
        _ResolverDb([RuntimeError("isolated database failure")]),
        cookie="isolated-failing-session",
    )

    assert response.status_code == 500


def test_strict_me_remains_401_for_anonymous_request():
    response = _request_with_db("/api/auth/me", _ResolverDb([]))

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
