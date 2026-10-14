"""PR-09-verify-api: HTTP contract / permission / freeze negatives (scope A).

Independent verifier matrix (not migration/ledger). Run via Week 3 scratch guard:

    python3 scripts/week3-scratch-guard.py run \\
        --db-name astra_week3_pr09_ui_api \\
        --url postgresql+asyncpg://postgres@127.0.0.1:49621/astra_week3_pr09_ui_api \\
        -- backend/.venv/bin/python -m pytest tests/test_pr09_verify_api_contract.py -q
"""

from __future__ import annotations

import asyncio
import contextlib
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

import main
import os

LEAK_MARKER = "PR09APILEAK_my_answer_7a3c"

PUBLIC_ALLOWLIST = {
    "id",
    "title",
    "question_text",
    "correct_answer",
    "analysis",
    "reason_category",
    "mistake_reason",
    "difficulty",
    "knowledge_point_ids",
    "created_at",
    "updated_at",
}

FORBIDDEN_FIELDS = (
    "my_answer",
    "source_draft_item_id",
    "subject_id",
    "version",
    "review_item_id",
    "status",
    "visibility",
)

FROZEN_CODE = "legacy_mistake_write_frozen"


@pytest.fixture(scope="module")
def client():
    with TestClient(main.app) as c:
        yield c


async def _with_session(fn):
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

    engine = create_async_engine(os.environ["DATABASE_URL"])
    try:
        async with AsyncSession(engine) as s:
            return await fn(s)
    finally:
        await engine.dispose()


async def _seed_note(slug: str, *, note_type: str = "mistake", **fields) -> str:
    async def _fn(s):
        note_id = uuid.uuid4()
        await s.execute(
            text(
                "INSERT INTO public.notes (id,slug,title,content,type,status,hidden,"
                "ef,interval,repetitions,question,my_answer,correct_answer,analysis,revision) "
                "VALUES (:id,:slug,:title,:content,:type,'published',false,2.5,0,0,"
                ":question,:my_answer,:correct_answer,:analysis,1)"
            ),
            {
                "id": note_id,
                "slug": slug,
                "title": fields.get("title", "verify-fixture"),
                "content": fields.get("content", "content"),
                "type": note_type,
                "question": fields.get("question", "Q?"),
                "my_answer": fields.get("my_answer", "secret-my-answer"),
                "correct_answer": fields.get("correct_answer", "A"),
                "analysis": fields.get("analysis", "an"),
            },
        )
        await s.commit()
        return str(note_id)

    return await _with_session(_fn)


async def _seed_mistake(
    *,
    visibility: str = "public",
    status: str = "active",
    my_answer: str = LEAK_MARKER,
) -> str:
    async def _fn(s):
        mistake_id = uuid.uuid4()
        subject_id = (await s.execute(
            text("INSERT INTO public.subjects (name) VALUES (:n) RETURNING id"),
            {"n": f"pr09api-sub-{uuid.uuid4().hex[:8]}"},
        )).scalar_one()
        draft_item_id = (await s.execute(
            text(
                "INSERT INTO public.draft_items (id,draft_type,source_type,source_id,status,"
                "version,target_type,target_id,source_hash,approved_by,approved_at,"
                "conversion_sequence,target_mistake_id) "
                "VALUES (gen_random_uuid(),'mistake','question',:src,'converted',1,'mistake',"
                ":tgt,repeat('a',64),gen_random_uuid(),now(),1,:mid) RETURNING id"
            ),
            {"src": f"q-{uuid.uuid4().hex[:8]}", "tgt": str(mistake_id), "mid": str(mistake_id)},
        )).scalar_one()
        question_id = (await s.execute(
            text(
                "INSERT INTO public.questions (id,subject_id,stem_md,question_text,question_type,"
                "options,answer_data,correct_answer,status,visibility,version) "
                "VALUES (gen_random_uuid(),:s,'',:qt,'short_answer','[]','{}','a',"
                "'active','private',1) RETURNING id"
            ),
            {"s": subject_id, "qt": "Verify question text"},
        )).scalar_one()
        await s.execute(
            text(
                "INSERT INTO public.mistakes (id,source_draft_item_id,question_id,subject_id,"
                "title,question_text,my_answer,correct_answer,analysis,reason_category,"
                "mistake_reason,difficulty,status,visibility,version) "
                "VALUES (:id,:d,:q,:s,'Verify Title','Verify question text',:my_answer,"
                "'CA-VERIFY','AN-VERIFY','concept','verify-reason','easy',:status,:visibility,1)"
            ),
            {
                "id": mistake_id,
                "d": draft_item_id,
                "q": question_id,
                "s": subject_id,
                "my_answer": my_answer,
                "status": status,
                "visibility": visibility,
            },
        )
        await s.execute(
            text(
                "INSERT INTO public.review_items (id,target_type,target_id,mistake_id,state,"
                "algorithm,interval_days,repetitions) "
                "VALUES (gen_random_uuid(),'mistake',:t,:m,'active','fixed_interval_v2',0,0)"
            ),
            {"t": str(mistake_id), "m": mistake_id},
        )
        await s.commit()
        return str(mistake_id)

    return await _with_session(_fn)


async def _login_admin(client: TestClient) -> None:
    from app.utils.auth import hash_password

    async def _fn(s):
        user_id = uuid.uuid4()
        await s.execute(
            text(
                "INSERT INTO public.users (id,username,password_hash,is_admin) "
                "VALUES (:id,'pr09-verify-api-admin',:pw,true) "
                "ON CONFLICT (username) DO UPDATE "
                "SET password_hash = EXCLUDED.password_hash, is_admin = true"
            ),
            {"id": user_id, "pw": hash_password("pr09-verify-api-pass-123")},
        )
        await s.commit()

    await _with_session(_fn)
    resp = client.post(
        "/api/auth/login",
        json={"username": "pr09-verify-api-admin", "password": "pr09-verify-api-pass-123"},
    )
    assert resp.status_code == 200, resp.text


_logged_in = False


def _ensure_admin(client: TestClient) -> None:
    global _logged_in
    if _logged_in:
        return
    asyncio.run(_login_admin(client))
    _logged_in = True


def _assert_frozen(resp, operation: str) -> None:
    assert resp.status_code == 410, (operation, resp.status_code, resp.text)
    detail = resp.json()["detail"]
    assert detail["code"] == FROZEN_CODE
    assert detail["operation"] == operation


# ---------------------------------------------------------------------------
# 1. Public read: explicit Empty + active/public filter + field-level allowlist
# ---------------------------------------------------------------------------


@contextlib.contextmanager
def _isolated_public_view(*, keep_id: str | None = None):
    """Serve ``/api/public/mistakes`` from a transaction-scoped session.

    ``/api/public/mistakes`` has no tenant/filter scope, so its ``total`` counts
    every active+public row committed by earlier tests or earlier runs of this
    suite. This override hides those rows (by flipping them to ``private``
    inside a transaction) so the envelope reflects only the rows under test,
    then rolls the hide back. When ``keep_id`` is given that row stays visible,
    so the populated assertions remain exact without weakening them.
    """
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

    from app.database import get_db

    async def _view():
        engine = create_async_engine(os.environ["DATABASE_URL"])
        conn = await engine.connect()
        trans = await conn.begin()
        session = AsyncSession(bind=conn, expire_on_commit=False)
        try:
            if keep_id is None:
                await session.execute(
                    text(
                        "UPDATE public.mistakes SET visibility='private' "
                        "WHERE status='active' AND visibility='public'"
                    )
                )
            else:
                await session.execute(
                    text(
                        "UPDATE public.mistakes SET visibility='private' "
                        "WHERE status='active' AND visibility='public' "
                        "AND id != CAST(:keep AS uuid)"
                    ),
                    {"keep": str(keep_id)},
                )
            await session.flush()
            yield session
        finally:
            await session.close()
            await trans.rollback()
            await conn.close()
            await engine.dispose()

    main.app.dependency_overrides[get_db] = _view
    try:
        yield
    finally:
        main.app.dependency_overrides.pop(get_db, None)


def test_public_zero_rows_explicit_empty(client):
    with _isolated_public_view():
        resp = client.get("/api/public/mistakes")
    assert resp.status_code == 200
    data = resp.json()
    assert data["empty"] is True
    assert isinstance(data["message"], str) and data["message"]
    assert data["items"] == []
    assert data["total"] == 0


def test_public_populated_only_active_public_and_field_level(client):
    pub_id = asyncio.run(
        _seed_mistake(visibility="public", status="active", my_answer=LEAK_MARKER)
    )
    asyncio.run(
        _seed_mistake(visibility="private", status="active", my_answer="HIDE_PRIVATE_ROW")
    )
    asyncio.run(
        _seed_mistake(visibility="public", status="archived", my_answer="HIDE_ARCHIVED_ROW")
    )

    with _isolated_public_view(keep_id=pub_id):
        resp = client.get("/api/public/mistakes")
    assert resp.status_code == 200
    data = resp.json()
    assert data["empty"] is False
    assert data["total"] == 1
    assert len(data["items"]) == 1
    item = data["items"][0]
    assert item["id"] == pub_id
    assert set(item.keys()) == PUBLIC_ALLOWLIST
    for name in FORBIDDEN_FIELDS:
        assert name not in item
    raw = resp.text
    for marker in (LEAK_MARKER, "HIDE_PRIVATE_ROW", "HIDE_ARCHIVED_ROW"):
        assert marker not in raw
    for name in FORBIDDEN_FIELDS:
        assert f'"{name}"' not in raw


# ---------------------------------------------------------------------------
# 2. Anonymous admin mutations -> 401/403
# ---------------------------------------------------------------------------


def test_anonymous_visibility_patch_denied(client):
    resp = client.patch(
        f"/api/admin/mistakes/{uuid.uuid4()}/visibility",
        json={"version": 1, "visibility": "public"},
    )
    assert resp.status_code in (401, 403)


def test_anonymous_admin_list_denied(client):
    assert client.get("/api/admin/mistakes").status_code in (401, 403)


def test_anonymous_admin_update_denied(client):
    resp = client.put(
        f"/api/admin/mistakes/{uuid.uuid4()}",
        json={"version": 1, "my_answer": "x"},
    )
    assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# 3. F-1..F-9 freeze negatives (410 + code legacy_mistake_write_frozen)
# ---------------------------------------------------------------------------


def test_F1_create_type_mistake_frozen(client):
    _ensure_admin(client)
    resp = client.post(
        "/api/notes",
        json={
            "slug": f"pr09api-f1-{uuid.uuid4().hex[:8]}",
            "title": "t",
            "content": "c",
            "type": "mistake",
        },
    )
    _assert_frozen(resp, "notes.create")


def test_F2_update_type_into_mistake_frozen(client):
    _ensure_admin(client)
    slug = f"pr09api-f2in-{uuid.uuid4().hex[:8]}"
    asyncio.run(_seed_note(slug, note_type="note"))
    resp = client.put(f"/api/notes/{slug}", json={"type": "mistake"})
    _assert_frozen(resp, "notes.update")


def test_F2_update_type_out_of_mistake_frozen(client):
    _ensure_admin(client)
    slug = f"pr09api-f2out-{uuid.uuid4().hex[:8]}"
    asyncio.run(_seed_note(slug, note_type="mistake"))
    resp = client.put(f"/api/notes/{slug}", json={"type": "note"})
    _assert_frozen(resp, "notes.update")


def test_F3_promote_to_mistake_frozen(client):
    _ensure_admin(client)
    slug = f"pr09api-f3-{uuid.uuid4().hex[:8]}"
    asyncio.run(_seed_note(slug, note_type="note"))
    resp = client.post(f"/api/notes/{slug}/promote", params={"new_type": "mistake"})
    _assert_frozen(resp, "notes.promote")


def test_F3_promote_from_mistake_frozen(client):
    _ensure_admin(client)
    slug = f"pr09api-f3out-{uuid.uuid4().hex[:8]}"
    asyncio.run(_seed_note(slug, note_type="mistake"))
    resp = client.post(f"/api/notes/{slug}/promote", params={"new_type": "note"})
    _assert_frozen(resp, "notes.promote")


def test_F4_staged_mistake_form_create_api_frozen(client):
    _ensure_admin(client)
    resp = client.post(
        "/api/notes",
        json={
            "slug": f"pr09api-f4-{uuid.uuid4().hex[:8]}",
            "title": "staged",
            "content": "c",
            "type": "mistake",
        },
    )
    _assert_frozen(resp, "notes.create")


def test_F5_mistake_form_edit_save_api_frozen(client):
    _ensure_admin(client)
    slug = f"pr09api-f5-{uuid.uuid4().hex[:8]}"
    asyncio.run(_seed_note(slug, note_type="mistake", my_answer="legacy-edit-target"))
    resp = client.put(f"/api/notes/{slug}", json={"content": "edited-by-legacy-writer"})
    _assert_frozen(resp, "notes.update")


def test_F6_write_note_content_write_frozen(client):
    _ensure_admin(client)
    slug = f"pr09api-f6-{uuid.uuid4().hex[:8]}"
    asyncio.run(_seed_note(slug, note_type="mistake", content="original"))
    resp = client.put(f"/api/notes/{slug}", json={"content": "write-note-save"})
    _assert_frozen(resp, "notes.update")


def test_F7_review_sm2_submit_frozen(client):
    _ensure_admin(client)
    slug = f"pr09api-f7-{uuid.uuid4().hex[:8]}"
    asyncio.run(_seed_note(slug, note_type="mistake"))
    resp = client.post(f"/api/review/{slug}", json={"quality": 5})
    _assert_frozen(resp, "review.sm2_submit")


def test_F8_field_update_frozen(client):
    _ensure_admin(client)
    slug = f"pr09api-f8-{uuid.uuid4().hex[:8]}"
    asyncio.run(_seed_note(slug, note_type="mistake"))
    resp = client.put(f"/api/notes/{slug}", json={"title": "renamed", "my_answer": "changed"})
    _assert_frozen(resp, "notes.update")


def test_F9_delete_frozen(client):
    _ensure_admin(client)
    slug = f"pr09api-f9-{uuid.uuid4().hex[:8]}"
    asyncio.run(_seed_note(slug, note_type="mistake"))
    resp = client.delete(f"/api/notes/{slug}")
    _assert_frozen(resp, "notes.delete")


def test_F9_batch_delete_frozen(client):
    _ensure_admin(client)
    slug = f"pr09api-f9b-{uuid.uuid4().hex[:8]}"
    asyncio.run(_seed_note(slug, note_type="mistake"))
    resp = client.post("/api/notes/batch-delete", json=[slug])
    _assert_frozen(resp, "notes.batch_delete")


def test_note_type_create_still_allowed(client):
    _ensure_admin(client)
    resp = client.post(
        "/api/notes",
        json={
            "slug": f"pr09api-ok-{uuid.uuid4().hex[:8]}",
            "title": "t",
            "content": "c",
            "type": "note",
        },
    )
    assert resp.status_code == 201, resp.text


# ---------------------------------------------------------------------------
# 4. Compat reads K sampling still 200
# ---------------------------------------------------------------------------


def test_compat_read_list_notes(client):
    resp = client.get("/api/notes")
    assert resp.status_code == 200


def test_compat_read_search(client):
    _ensure_admin(client)
    resp = client.post("/api/admin/search", json={"query": "verify", "limit": 5})
    assert resp.status_code == 200


def test_compat_read_review_queue(client):
    _ensure_admin(client)
    resp = client.get("/api/review/queue")
    assert resp.status_code == 200


def test_compat_read_single_mistake_note(client):
    slug = f"pr09api-kget-{uuid.uuid4().hex[:8]}"
    asyncio.run(_seed_note(slug, note_type="mistake"))
    resp = client.get(f"/api/notes/{slug}")
    assert resp.status_code == 200
    assert resp.json()["type"] == "mistake"


# ---------------------------------------------------------------------------
# 5. Admin visibility optimistic lock
# ---------------------------------------------------------------------------


def test_visibility_wrong_version_409(client):
    mistake_id = asyncio.run(_seed_mistake(visibility="private", status="active"))
    _ensure_admin(client)
    resp = client.patch(
        f"/api/admin/mistakes/{mistake_id}/visibility",
        json={"version": 99, "visibility": "public"},
    )
    assert resp.status_code == 409, (resp.status_code, resp.text)


def test_visibility_correct_version_toggles(client):
    mistake_id = asyncio.run(_seed_mistake(visibility="private", status="active"))
    _ensure_admin(client)
    resp = client.patch(
        f"/api/admin/mistakes/{mistake_id}/visibility",
        json={"version": 1, "visibility": "public"},
    )
    assert resp.status_code == 200, (resp.status_code, resp.text)
    body = resp.json()
    assert body["visibility"] == "public"
    assert body["version"] == 2
    resp2 = client.patch(
        f"/api/admin/mistakes/{mistake_id}/visibility",
        json={"version": 2, "visibility": "private"},
    )
    assert resp2.status_code == 200
    assert resp2.json()["visibility"] == "private"
