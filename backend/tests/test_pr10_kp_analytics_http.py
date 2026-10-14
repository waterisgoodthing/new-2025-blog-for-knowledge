"""PR-10 KP analytics HTTP test: admin-only read endpoint returns W3-D05 payload.

Run via the Week 3 scratch guard against a migrated scratch database:

    python3 scripts/week3-scratch-guard.py run --db-name astra_week3_pr10 \
        -- backend/.venv/bin/python -m pytest tests/test_pr10_kp_analytics_http.py -q
"""

from __future__ import annotations

import asyncio
import os
import uuid

import pytest
from fastapi.testclient import TestClient

import main
from app.utils.auth import hash_password

ANALYTICS_PATH = "/api/admin/knowledge-points/analytics"
METRIC_FIELDS = {
    "knowledge_point_id",
    "attempt_count",
    "wrong_count",
    "review_count",
    "due_count",
    "accuracy",
    "wrong_rate",
    "lapse_count",
}


async def _seed_admin(username: str, password: str) -> None:
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

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


def test_analytics_endpoint_is_anonymous_unauthorized(client) -> None:
    response = client.get(ANALYTICS_PATH)
    assert response.status_code in (401, 403)


def test_analytics_endpoint_returns_admin_payload(client) -> None:
    username = f"pr10-admin-{uuid.uuid4().hex[:8]}"
    password = "pr10-admin-pass-123"
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
        assert set(item) == METRIC_FIELDS
