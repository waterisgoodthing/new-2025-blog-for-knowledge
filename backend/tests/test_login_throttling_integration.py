"""Integration tests for login throttling through the real FastAPI endpoint.

Uses the real ``POST /api/auth/login`` route and the real throttle service, but
overrides the ``get_db`` dependency with an in-process fake so the tests stay
fast and database-independent (the same pattern as
``test_auth_error_handling.py``). The endpoint also logs WARN lines for
throttled attempts; pytest captures them.

One test measures the genuine default 2s delay; the remaining cases override
``LOGIN_THROTTLE_DELAYS`` with sub-second values to keep runtime bounded while
still exercising the endpoint's timing path.
"""

from __future__ import annotations

import time
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

import main
from app.database import get_db
from app.models.note import User
from app.routers import auth as auth_router
from app.services import login_throttle as lt
from app.utils.auth import hash_password

_REAL_2S_TOLERANCE_LOW = 1.5
_REAL_2S_TOLERANCE_HIGH = 2.5


class _ScalarResult:
    def __init__(self, value):
        self.value = value

    def scalar_one_or_none(self):
        return self.value


class _FakeDb:
    """Minimal AsyncSession stand-in: returns a configured user or None."""

    def __init__(self, user=None):
        self.user = user

    async def execute(self, _statement):
        return _ScalarResult(self.user)

    def add(self, _obj):
        return None

    async def flush(self):
        return None


def _settings(
    *,
    enabled: bool = True,
    delays: str = "2,5,15",
    threshold: int = 3,
    ip_ttl: int = 3600,
    max_failures: int = 10,
) -> SimpleNamespace:
    return SimpleNamespace(
        LOGIN_THROTTLE_ENABLED=enabled,
        LOGIN_THROTTLE_WARN_THRESHOLD=threshold,
        LOGIN_THROTTLE_DELAYS=delays,
        LOGIN_THROTTLE_IP_TTL_SECONDS=ip_ttl,
        LOGIN_THROTTLE_ACCOUNT_MAX_FAILURES=max_failures,
    )


def _login(client: TestClient, username: str, password: str = "definitely-wrong"):
    return client.post(
        "/api/auth/login", json={"username": username, "password": password}
    )


@pytest.fixture(autouse=True)
def _isolate(monkeypatch):
    lt.reset_state()
    yield
    lt.reset_state()
    main.app.dependency_overrides.pop(get_db, None)


def _install(monkeypatch, *, user=None, **settings_overrides):
    fake_db = _FakeDb(user=user)

    async def override_get_db():
        yield fake_db

    main.app.dependency_overrides[get_db] = override_get_db
    settings = _settings(**settings_overrides)
    monkeypatch.setattr(auth_router, "get_settings", lambda: settings)
    return settings


def test_fourth_failure_has_real_two_second_delay(monkeypatch):
    _install(monkeypatch, delays="2,5,15")
    client = TestClient(main.app, client=("203.0.113.10", 41001))

    for attempt in range(1, 4):
        assert _login(client, "slow-real-user").status_code == 401, attempt

    started = time.perf_counter()
    response = _login(client, "slow-real-user")
    elapsed = time.perf_counter() - started

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}
    assert _REAL_2S_TOLERANCE_LOW <= elapsed <= _REAL_2S_TOLERANCE_HIGH, elapsed
    print(f"[timing] real default 4th-attempt elapsed={elapsed:.3f}s")


def test_short_config_fourth_attempt_waits_first_delay(monkeypatch):
    _install(monkeypatch, delays="0.25,0.5,0.75")
    client = TestClient(main.app, client=("203.0.113.11", 41002))

    for _ in range(3):
        assert _login(client, "short-config-user").status_code == 401

    started = time.perf_counter()
    response = _login(client, "short-config-user")
    elapsed = time.perf_counter() - started

    assert response.status_code == 401
    assert elapsed >= 0.2, elapsed
    print(f"[timing] short-config 4th-attempt elapsed={elapsed:.3f}s")


def test_account_dimension_applies_from_a_new_ip(monkeypatch):
    _install(monkeypatch, delays="0.25,0.5,0.75")

    first_ip = TestClient(main.app, client=("198.51.100.1", 42001))
    for _ in range(3):
        assert _login(first_ip, "account-across-ip").status_code == 401

    second_ip = TestClient(main.app, client=("198.51.100.2", 42002))
    started = time.perf_counter()
    response = _login(second_ip, "account-across-ip")
    elapsed = time.perf_counter() - started

    assert response.status_code == 401
    assert elapsed >= 0.2, elapsed
    print(f"[timing] account-dimension new-IP elapsed={elapsed:.3f}s")


def test_ip_dimension_applies_to_a_new_account(monkeypatch):
    _install(monkeypatch, delays="0.25,0.5,0.75")
    client = TestClient(main.app, client=("198.51.100.9", 43001))

    # Three failures across three distinct accounts leave the shared IP at the
    # threshold, while the fourth account has zero failures of its own.
    for index in range(3):
        assert _login(client, f"shared-ip-victim-{index}").status_code == 401

    started = time.perf_counter()
    response = _login(client, "shared-ip-fresh-account")
    elapsed = time.perf_counter() - started

    assert response.status_code == 401
    assert elapsed >= 0.2, elapsed
    print(f"[timing] ip-dimension new-account elapsed={elapsed:.3f}s")


def test_disabled_throttle_adds_no_delay(monkeypatch):
    _install(monkeypatch, enabled=False, delays="0.25,0.5,0.75")
    client = TestClient(main.app, client=("203.0.113.12", 41003))

    for _ in range(10):
        assert _login(client, "disabled-user").status_code == 401

    started = time.perf_counter()
    response = _login(client, "disabled-user")
    elapsed = time.perf_counter() - started

    assert response.status_code == 401
    assert elapsed < 0.2, elapsed
    print(f"[timing] disabled-throttle elapsed={elapsed:.3f}s")


def test_successful_login_resets_account_delay(monkeypatch):
    user = User(
        username="reset-user",
        password_hash=hash_password("correct-horse"),
        is_admin=False,
    )
    # Use a 2s first delay so a broken reset (2s throttle + bcrypt) is clearly
    # distinguishable from an unthrottled bcrypt verify (<1s).
    _install(monkeypatch, user=user, delays="2,3,4")

    same_ip = TestClient(main.app, client=("192.0.2.50", 44001))
    for _ in range(3):
        assert _login(same_ip, "reset-user", password="wrong").status_code == 401

    # A successful login from a fresh IP clears the account counter (the request
    # itself is delayed by the pending account failures).
    verified = _login(
        TestClient(main.app, client=("192.0.2.51", 44002)),
        "reset-user",
        password="correct-horse",
    )
    assert verified.status_code == 200

    started = time.perf_counter()
    after_success = _login(
        TestClient(main.app, client=("192.0.2.52", 44003)),
        "reset-user",
        password="wrong",
    )
    elapsed = time.perf_counter() - started

    # A broken reset would add the 2s account delay; a reset account leaves only
    # the unavoidable bcrypt cost, which stays well under 1s even at cost=12.
    assert after_success.status_code == 401
    assert elapsed < 1.0, elapsed
    print(f"[timing] post-success account reset elapsed={elapsed:.3f}s")
