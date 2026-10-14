"""PR-11 dashboard summary HTTP contract: admin-only, stable delta shape.

Run via the Week 3 scratch guard against a migrated scratch database:

    python3 scripts/week3-scratch-guard.py run --db-name astra_week3_pr11 \
        -- backend/.venv/bin/python -m pytest tests/test_pr11_dashboard_http.py -q
"""

from __future__ import annotations

import asyncio
import os
import uuid

import pytest
from fastapi.testclient import TestClient

import main
from app.utils.auth import hash_password

SUMMARY_PATH = "/api/admin/dashboard/summary"

DELTA_FIELDS = {
    "review_today_count",
    "practice_today_count",
    "weak_top3",
    "recently_mastered_4",
    "today_first_action",
}
SECTION_ACTIONS_FIELDS = {"review", "practice"}
SECTION_ACTION_FIELDS = {"section", "count", "available", "target_route", "reason"}
FIRST_ACTION_FIELDS = {"kind", "count", "target_route", "reason"}
WEAK_ITEM_FIELDS = {
    "knowledge_point_id",
    "name",
    "attempt_count",
    "wrong_rate",
    "lapse_count",
    "due_count",
}
MASTERED_ITEM_FIELDS = {"review_item_id", "mistake_id", "question_text", "mastered_at"}


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


def test_summary_endpoint_is_anonymous_unauthorized(client) -> None:
    response = client.get(SUMMARY_PATH)
    assert response.status_code in (401, 403)


def test_summary_endpoint_returns_complete_delta_shape(client) -> None:
    username = f"pr11-admin-{uuid.uuid4().hex[:8]}"
    password = "pr11-admin-pass-123"
    asyncio.run(_seed_admin(username, password))

    login = client.post(
        "/api/auth/login", json={"username": username, "password": password}
    )
    assert login.status_code == 200, login.text

    response = client.get(SUMMARY_PATH)
    assert response.status_code == 200, response.text
    payload = response.json()

    assert DELTA_FIELDS <= set(payload)
    assert isinstance(payload["review_today_count"], int)
    assert isinstance(payload["practice_today_count"], int)
    assert isinstance(payload["weak_top3"], list)
    assert isinstance(payload["recently_mastered_4"], list)

    actions = payload["section_actions"]
    assert set(actions) == SECTION_ACTIONS_FIELDS
    for action in actions.values():
        assert set(action) == SECTION_ACTION_FIELDS

    first_action = payload["today_first_action"]
    assert set(first_action) == FIRST_ACTION_FIELDS
    assert first_action["kind"] in {"review", "practice", "none"}

    for item in payload["weak_top3"]:
        assert set(item) == WEAK_ITEM_FIELDS
    for item in payload["recently_mastered_4"]:
        assert set(item) == MASTERED_ITEM_FIELDS
