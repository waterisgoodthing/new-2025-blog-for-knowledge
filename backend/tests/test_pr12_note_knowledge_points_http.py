"""PR-12 Note <-> KnowledgePoint HTTP tests: admin gate + status semantics.

Run via the Week 3 scratch guard against a migrated scratch database:

    python3 scripts/week3-scratch-guard.py run --db-name astra_week3_pr12 \\
        -- backend/.venv/bin/python -m pytest \\
        tests/test_pr12_note_knowledge_points_http.py -q
"""

from __future__ import annotations

import asyncio
import os
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

import main
from app.utils.auth import hash_password

NOTE_KP_PATH = "/api/admin/notes/{note_id}/knowledge-points/{kp_id}"
NOTE_KP_LIST_PATH = "/api/admin/notes/{note_id}/knowledge-points"
KP_NOTES_PATH = "/api/admin/notes/knowledge-points/{kp_id}/notes"


async def _seed() -> dict:
    engine = create_async_engine(os.environ["DATABASE_URL"])
    suffix = uuid.uuid4().hex[:8]
    try:
        async with AsyncSession(engine) as session:
            await session.execute(
                text(
                    "INSERT INTO public.users (id,username,password_hash,is_admin) "
                    "VALUES (:id,:username,:password,true)"
                ),
                {
                    "id": uuid.uuid4(),
                    "username": f"pr12-admin-{suffix}",
                    "password": hash_password("pr12-admin-pass-123"),
                },
            )
            subject_id = (
                await session.execute(
                    text("INSERT INTO public.subjects (name) VALUES (:name) RETURNING id"),
                    {"name": f"pr12-subject-{suffix}"},
                )
            ).scalar_one()
            kp_id = (
                await session.execute(
                    text(
                        "INSERT INTO public.knowledge_points (subject_id, name) "
                        "VALUES (:subject_id, :name) RETURNING id"
                    ),
                    {"subject_id": subject_id, "name": f"pr12-kp-{suffix}"},
                )
            ).scalar_one()
            note_id = (
                await session.execute(
                    text(
                        "INSERT INTO public.notes "
                        "(id,slug,title,content,type,ef,interval,repetitions) "
                        "VALUES (gen_random_uuid(),:slug,'t','c','note',2.5,0,0) "
                        "RETURNING id"
                    ),
                    {"slug": f"pr12-note-{suffix}"},
                )
            ).scalar_one()
            await session.commit()
    finally:
        await engine.dispose()
    return {
        "username": f"pr12-admin-{suffix}",
        "password": "pr12-admin-pass-123",
        "note_id": str(note_id),
        "kp_id": int(kp_id),
    }


@pytest.fixture(scope="module")
def client():
    with TestClient(main.app) as c:
        yield c


@pytest.fixture(scope="module")
def seeded():
    return asyncio.run(_seed())


def _paths(seeded) -> dict:
    return {
        "link": NOTE_KP_PATH.format(note_id=seeded["note_id"], kp_id=seeded["kp_id"]),
        "note_list": NOTE_KP_LIST_PATH.format(note_id=seeded["note_id"]),
        "kp_list": KP_NOTES_PATH.format(kp_id=seeded["kp_id"]),
    }


# ---------------------------------------------------------------------------
# Anonymous access
# ---------------------------------------------------------------------------


def test_anonymous_link_is_rejected(client, seeded) -> None:
    resp = client.post(_paths(seeded)["link"])
    assert resp.status_code in (401, 403)


def test_anonymous_unlink_is_rejected(client, seeded) -> None:
    resp = client.delete(_paths(seeded)["link"])
    assert resp.status_code in (401, 403)


def test_anonymous_note_list_is_rejected(client, seeded) -> None:
    resp = client.get(_paths(seeded)["note_list"])
    assert resp.status_code in (401, 403)


def test_anonymous_kp_list_is_rejected(client, seeded) -> None:
    resp = client.get(_paths(seeded)["kp_list"])
    assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# Admin behaviour
# ---------------------------------------------------------------------------


def _login(client, seeded) -> None:
    login = client.post(
        "/api/auth/login",
        json={"username": seeded["username"], "password": seeded["password"]},
    )
    assert login.status_code == 200, login.text


def test_admin_link_is_idempotent_then_lists_and_unlinks(client, seeded) -> None:
    _login(client, seeded)
    paths = _paths(seeded)

    first = client.post(paths["link"])
    assert first.status_code == 200, first.text
    assert first.json() == {
        "note_id": seeded["note_id"],
        "knowledge_point_id": seeded["kp_id"],
        "linked": True,
    }

    duplicate = client.post(paths["link"])
    assert duplicate.status_code == 200, duplicate.text
    assert duplicate.json()["linked"] is True

    note_list = client.get(paths["note_list"])
    assert note_list.status_code == 200, note_list.text
    assert [item["id"] for item in note_list.json()] == [seeded["kp_id"]]

    kp_list = client.get(paths["kp_list"])
    assert kp_list.status_code == 200, kp_list.text
    assert seeded["note_id"] in {item["id"] for item in kp_list.json()}

    removed = client.delete(paths["link"])
    assert removed.status_code == 204, removed.text

    removed_again = client.delete(paths["link"])
    assert removed_again.status_code == 204, removed_again.text


def test_admin_link_missing_note_is_404(client, seeded) -> None:
    _login(client, seeded)
    resp = client.post(
        NOTE_KP_PATH.format(note_id=uuid.uuid4(), kp_id=seeded["kp_id"])
    )
    assert resp.status_code == 404


def test_admin_link_missing_knowledge_point_is_404(client, seeded) -> None:
    _login(client, seeded)
    resp = client.post(
        NOTE_KP_PATH.format(note_id=seeded["note_id"], kp_id=2_000_000_000)
    )
    assert resp.status_code == 404


def test_admin_unlink_missing_note_is_404(client, seeded) -> None:
    _login(client, seeded)
    resp = client.delete(
        NOTE_KP_PATH.format(note_id=uuid.uuid4(), kp_id=seeded["kp_id"])
    )
    assert resp.status_code == 404
