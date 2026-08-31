import uuid

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

import main
from app.models.note import User
from app.routers import auth as auth_router
from app.routers.auth import get_current_admin, get_passkey_admin


PUBLIC_WRITE_ALLOWLIST = {
    ("POST", "/api/auth/login"),
    ("POST", "/api/auth/login-passkey"),
    ("POST", "/api/auth/logout"),
    ("POST", "/api/auth/passkey/operator/reg-options"),
    ("POST", "/api/auth/passkey/operator/register"),
    ("POST", "/api/auth/passkey/operator/validate-key"),
    ("POST", "/api/auth/register"),
    ("POST", "/api/guest-messages"),
}


def _write_routes():
    for route in main.app.routes:
        if not isinstance(route, APIRoute):
            continue
        for method in (route.methods or set()) & {"POST", "PUT", "PATCH", "DELETE"}:
            yield method, route


def test_every_non_public_write_route_requires_admin_or_passkey_admin():
    missing = []

    for method, route in _write_routes():
        if (method, route.path) in PUBLIC_WRITE_ALLOWLIST:
            continue
        dependencies = {dependency.call for dependency in route.dependant.dependencies}
        if get_current_admin not in dependencies and get_passkey_admin not in dependencies:
            missing.append(f"{method} {route.path}")

    assert missing == [], "Management write routes missing admin protection:\n" + "\n".join(sorted(missing))


NOTE_MUTATIONS = [
    ("POST", "/api/notes", {"slug": "permission-test", "title": "Permission test", "content": "x"}),
    ("PUT", "/api/notes/permission-test", {"title": "Updated"}),
    ("DELETE", "/api/notes/permission-test", None),
]


def _request(client: TestClient, method: str, path: str, payload: dict | None):
    return client.request(method, path, json=payload)


@pytest.mark.parametrize(("method", "path", "payload"), NOTE_MUTATIONS)
def test_note_create_update_delete_reject_anonymous_and_invalid_sessions(monkeypatch, method, path, payload):
    async def missing_session(*_args, **_kwargs):
        return None, None

    monkeypatch.setattr(auth_router, "_resolve_session_user", missing_session)

    client = TestClient(main.app)
    try:
        anonymous = _request(client, method, path, payload)
        client.cookies.set("admin_session", "invalid-p0-auth-session", path="/api")
        invalid = _request(client, method, path, payload)
    finally:
        client.close()

    assert anonymous.status_code == 401
    assert invalid.status_code == 401


@pytest.mark.parametrize(("method", "path", "payload"), NOTE_MUTATIONS)
def test_note_create_update_delete_reject_non_admin_sessions(monkeypatch, method, path, payload):
    async def non_admin_session(*_args, **_kwargs):
        return User(id=uuid.uuid4(), username="p0-auth-reader", is_admin=False), "password"

    monkeypatch.setattr(auth_router, "_resolve_session_user", non_admin_session)

    client = TestClient(main.app)
    try:
        client.cookies.set("admin_session", "p0-auth-reader-session", path="/api")
        response = _request(client, method, path, payload)
    finally:
        client.close()

    assert response.status_code == 403
