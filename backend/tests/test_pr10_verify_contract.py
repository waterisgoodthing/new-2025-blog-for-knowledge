"""PR-10 independent verification: contract, admin-only permission, DTO 3-way.

Cross-checks the backend Pydantic schema, the locked W3-D05 contract constants,
and the frontend typed DTO/endpoint string. HTTP checks use TestClient against
the guard-provided scratch database.

    python3 scripts/week3-scratch-guard.py run --db-name astra_week3_pr10_verify \
        -- backend/.venv/bin/python -m pytest tests/test_pr10_verify_contract.py -q
"""

from __future__ import annotations

import asyncio
import os
import re
import uuid
from pathlib import Path

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

import main
from app.routers.auth import get_current_admin
from app.schemas.kp_analytics import KnowledgePointAnalyticsItem
from week3_contracts_support import KP_ANALYTICS_METRIC_FIELDS

ANALYTICS_PATH = "/api/admin/knowledge-points/analytics"
BACKEND_FIELDS = frozenset(KnowledgePointAnalyticsItem.model_fields.keys())
FRONTEND_TS = (
    Path(__file__).resolve().parents[2] / "src" / "lib" / "api" / "knowledge-points.ts"
)


def _analytics_route() -> APIRoute:
    route = next(
        (
            r
            for r in main.app.routes
            if isinstance(r, APIRoute) and r.path == ANALYTICS_PATH and "GET" in r.methods
        ),
        None,
    )
    assert route is not None, f"missing GET {ANALYTICS_PATH}"
    return route


async def _seed_admin(username: str, password: str) -> None:
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

    from app.utils.auth import hash_password

    engine = create_async_engine(os.environ["DATABASE_URL"])
    try:
        async with AsyncSession(engine) as session:
            await session.execute(
                text(
                    "INSERT INTO public.users (id,username,password_hash,is_admin) "
                    "VALUES (:id,:username,:password,true)"
                ),
                {
                    "id": uuid.uuid4(),
                    "username": username,
                    "password": hash_password(password),
                },
            )
            await session.commit()
    finally:
        await engine.dispose()


@pytest.fixture(scope="module")
def client():
    with TestClient(main.app) as c:
        yield c


def test_c1_anonymous_request_is_rejected(client):
    response = client.get(ANALYTICS_PATH)
    assert response.status_code in (401, 403), response.text


def test_c1_admin_request_returns_200_and_metric_payload(client):
    username = f"pr10-verify-{uuid.uuid4().hex[:8]}"
    password = "pr10-verify-pass-123"
    asyncio.run(_seed_admin(username, password))

    login = client.post(
        "/api/auth/login", json={"username": username, "password": password}
    )
    assert login.status_code == 200, login.text

    response = client.get(ANALYTICS_PATH)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert isinstance(payload, list)
    for item in payload:
        assert set(item) == BACKEND_FIELDS


def test_c2_backend_schema_matches_locked_w3_d05_contract():
    assert BACKEND_FIELDS == KP_ANALYTICS_METRIC_FIELDS | {"knowledge_point_id"}
    assert len(BACKEND_FIELDS) == 8


def test_c2_route_requires_current_admin_and_is_get_only():
    route = _analytics_route()
    assert route.methods == {"GET"}
    dependency_calls = {dep.call for dep in route.dependant.dependencies}
    assert get_current_admin in dependency_calls


def test_c3_frontend_dto_fields_and_endpoint_match_backend():
    text = FRONTEND_TS.read_text(encoding="utf-8")
    interface_body = re.search(r"export interface KpAnalytics \{(.*?)\}", text, re.S)
    assert interface_body is not None, "KpAnalytics interface not found"
    ts_fields = set(re.findall(r"^\s*(\w+)\s*:", interface_body.group(1), re.M))
    assert ts_fields == BACKEND_FIELDS, (ts_fields, BACKEND_FIELDS)

    metric_block = re.search(
        r"KP_ANALYTICS_METRIC_FIELDS\s*=\s*\[(.*?)\]", text, re.S
    )
    assert metric_block is not None
    ts_metrics = set(re.findall(r"'(\w+)'", metric_block.group(1)))
    assert ts_metrics == KP_ANALYTICS_METRIC_FIELDS

    assert ANALYTICS_PATH in text, "frontend client endpoint drifted from router path"


def test_c3_analytics_route_precedes_param_route():
    paths = [r.path for r in main.app.routes if isinstance(r, APIRoute)]
    assert paths.index(ANALYTICS_PATH) < paths.index(
        "/api/admin/knowledge-points/{knowledge_point_id}"
    )
