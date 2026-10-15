"""PR-13 practice HTTP contract: admin-only read endpoint, answer-free DTO.

Run via the Week 3 scratch guard against a migrated scratch database:

    python3 scripts/week3-scratch-guard.py run --db-name astra_week3_pr13 \
        -- backend/.venv/bin/python -m pytest tests/test_pr13_practice_http.py -q
"""

from __future__ import annotations

import asyncio
import os
import uuid

import pytest
from fastapi.testclient import TestClient

import main
from app.utils.auth import hash_password

PRACTICE_PATH = "/api/admin/practice/today"
ITEM_FIELDS = {"question_id", "knowledge_point_id", "selection_reason"}
FORBIDDEN_ITEM_FIELDS = {"answer_data", "correct_answer", "analysis", "explanation"}
RESPONSE_FIELDS = {"items", "empty_metadata"}


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


def test_practice_endpoint_is_anonymous_unauthorized(client) -> None:
    response = client.get(PRACTICE_PATH)
    assert response.status_code in (401, 403)


def test_practice_endpoint_returns_admin_answer_free_payload(client) -> None:
    username = f"pr13-admin-{uuid.uuid4().hex[:8]}"
    password = "pr13-admin-pass-123"
    asyncio.run(_seed_admin(username, password))

    login = client.post(
        "/api/auth/login", json={"username": username, "password": password}
    )
    assert login.status_code == 200, login.text

    response = client.get(PRACTICE_PATH)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert set(payload) == RESPONSE_FIELDS
    assert isinstance(payload["items"], list)
    assert len(payload["items"]) <= 10
    for item in payload["items"]:
        assert set(item) == ITEM_FIELDS
        assert FORBIDDEN_ITEM_FIELDS.isdisjoint(item)
    metadata = payload["empty_metadata"]
    assert metadata["returned_count"] == len(payload["items"])
    assert metadata["window_hours"] == 7 * 24
