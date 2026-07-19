import asyncio
import logging
import hashlib
import uuid
from types import SimpleNamespace
from uuid import UUID

from fastapi import FastAPI
from fastapi import Request
from fastapi.testclient import TestClient
import pytest

import main
from app.database import get_db
from app.middleware.request_observability import request_observability
from app.models.note import User
from app.routers import auth
from app.routers import diagnostics as diagnostics_router
from app.routers.auth import get_current_admin


def test_production_startup_rejects_active_auth_bypass_before_database_readiness(monkeypatch) -> None:
    async def should_not_reach_database_readiness():
        raise AssertionError("production bypass must fail before database readiness")

    async def start_lifespan() -> None:
        async with main.lifespan(main.app):
            pass

    monkeypatch.setattr(
        main,
        "get_settings",
        lambda: SimpleNamespace(
            ENV="production",
            JWT_SECRET_KEY="secure-test-key",
            ALLOWED_ORIGINS="https://example.test",
            AUTH_BYPASS="true",
            AUTH_BYPASS_ALLOW="true",
        ),
    )
    monkeypatch.setattr(main, "validate_database_readiness", should_not_reach_database_readiness)

    with pytest.raises(RuntimeError, match="AUTH_BYPASS"):
        asyncio.run(start_lifespan())


def test_production_startup_rejects_enabled_public_registration_before_database_readiness(monkeypatch) -> None:
    async def should_not_reach_database_readiness():
        raise AssertionError("production registration must fail before database readiness")

    async def start_lifespan() -> None:
        async with main.lifespan(main.app):
            pass

    monkeypatch.setattr(
        main,
        "get_settings",
        lambda: SimpleNamespace(
            ENV="production",
            JWT_SECRET_KEY="secure-test-key",
            ALLOWED_ORIGINS="https://example.test",
            AUTH_BYPASS="false",
            AUTH_BYPASS_ALLOW="false",
            ENABLE_REGISTRATION=True,
        ),
    )
    monkeypatch.setattr(main, "validate_database_readiness", should_not_reach_database_readiness)

    with pytest.raises(RuntimeError, match="ENABLE_REGISTRATION"):
        asyncio.run(start_lifespan())


@pytest.mark.parametrize(
    ("settings", "error_pattern"),
    [
        (
            SimpleNamespace(
                ENV="production",
                JWT_SECRET_KEY="your-secret-key-change-this",
                ALLOWED_ORIGINS="https://example.test",
                AUTH_BYPASS="false",
                AUTH_BYPASS_ALLOW="false",
            ),
            "JWT_SECRET_KEY",
        ),
        (
            SimpleNamespace(
                ENV="production",
                JWT_SECRET_KEY="secure-test-key",
                ALLOWED_ORIGINS="*",
                AUTH_BYPASS="false",
                AUTH_BYPASS_ALLOW="false",
            ),
            "CORS",
        ),
    ],
)
def test_production_startup_raises_runtime_error_for_insecure_settings(
    monkeypatch,
    settings,
    error_pattern,
) -> None:
    async def start_lifespan() -> None:
        async with main.lifespan(main.app):
            pass

    monkeypatch.setattr(main, "get_settings", lambda: settings)

    with pytest.raises(RuntimeError, match=error_pattern):
        asyncio.run(start_lifespan())


def test_nonproduction_startup_keeps_the_existing_auth_bypass_configuration_semantics(monkeypatch) -> None:
    readiness_calls = 0

    async def readiness() -> None:
        nonlocal readiness_calls
        readiness_calls += 1

    async def start_lifespan() -> None:
        async with main.lifespan(main.app):
            pass

    monkeypatch.setattr(
        main,
        "get_settings",
        lambda: SimpleNamespace(
            ENV="development",
            AUTH_BYPASS="true",
            AUTH_BYPASS_ALLOW="true",
            KEEP_ALIVE_ENABLED=False,
        ),
    )
    monkeypatch.setattr(main, "validate_database_readiness", readiness)

    asyncio.run(start_lifespan())

    assert readiness_calls == 1


def test_public_health_is_lightweight() -> None:
    with TestClient(main.app) as client:
        response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_responses_include_a_server_generated_request_id() -> None:
    with TestClient(main.app) as client:
        response = client.get(
            "/api/health",
            headers={"X-Request-ID": "client-controlled"},
        )

    request_id = response.headers["X-Request-ID"]
    UUID(request_id)
    assert request_id != "client-controlled"


def test_diagnostics_requires_an_administrator() -> None:
    with TestClient(main.app) as client:
        response = client.get("/api/admin/diagnostics")

    assert response.status_code == 401


def test_administrator_can_read_safe_diagnostics() -> None:
    async def override_admin():
        return object()

    main.app.dependency_overrides[get_current_admin] = override_admin
    try:
        with TestClient(main.app) as client:
            response = client.get("/api/admin/diagnostics")
    finally:
        main.app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["overall"] == "ok"
    assert payload["checks"] == {
        "service": {"status": "ok"},
        "database": {"status": "ok"},
        "storage": {"status": "ok"},
        "auth": {"status": "ok"},
    }
    assert "generated_at" in payload
    assert "path" not in response.text.lower()


def test_diagnostics_degrade_without_leaking_internal_details(monkeypatch) -> None:
    class BrokenDatabase:
        async def execute(self, _statement):
            raise RuntimeError("database-password=private")

    async def override_admin():
        return object()

    async def override_database():
        yield BrokenDatabase()

    monkeypatch.setattr(
        diagnostics_router,
        "get_settings",
        lambda: SimpleNamespace(
            UPLOAD_ROOT="/definitely/not/a/real/private/storage/path",
            AUTH_BYPASS="true",
            AUTH_BYPASS_ALLOW="true",
        ),
    )
    main.app.dependency_overrides[get_current_admin] = override_admin
    main.app.dependency_overrides[get_db] = override_database
    try:
        with TestClient(main.app) as client:
            response = client.get("/api/admin/diagnostics")
    finally:
        main.app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["overall"] == "degraded"
    assert response.json()["checks"] == {
        "service": {"status": "ok"},
        "database": {"status": "error"},
        "storage": {"status": "error"},
        "auth": {"status": "warning"},
    }
    assert "private" not in response.text.lower()
    assert "path" not in response.text.lower()


def test_unhandled_error_returns_and_logs_only_safe_context(caplog) -> None:
    app = FastAPI()
    app.middleware("http")(request_observability)

    @app.get("/boom")
    async def boom():
        raise RuntimeError("private-body token=super-secret")

    with caplog.at_level(logging.ERROR, logger="app.observability"):
        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.get("/boom?private=query-secret")

    request_id = response.headers["X-Request-ID"]
    UUID(request_id)
    assert response.status_code == 500
    assert response.json() == {
        "detail": "Internal server error",
        "request_id": request_id,
    }
    record = next(record for record in caplog.records if record.name == "app.observability")
    assert record.safe_route == "/boom"
    assert record.request_id == request_id
    assert record.actor == "anonymous"
    assert record.error_class == "RuntimeError"
    assert record.safe_summary == "Unhandled application error"
    assert "super-secret" not in caplog.text
    assert "query-secret" not in caplog.text


def test_admin_auth_sets_only_an_anonymized_actor(monkeypatch) -> None:
    user_id = uuid.uuid4()
    user = User(id=user_id, username="private-admin", is_admin=True)

    async def resolve_user(_session_token, _db):
        return user, "password"

    monkeypatch.setattr(auth, "_resolve_session_user", resolve_user)
    request = Request({"type": "http", "method": "GET", "path": "/", "headers": []})

    resolved = asyncio.run(
        get_current_admin(request, session_token="private-token", db=object())
    )

    assert resolved is user
    assert request.state.actor == hashlib.sha256(str(user_id).encode()).hexdigest()[:12]
    assert request.state.actor != str(user_id)
    assert request.state.actor != user.username
