"""PR-09 HTTP matrix: public DTO leak checks, anonymous 401/403,
legacy mistake write-freeze F-1..F-9 negatives, compat reads, optimistic lock,
and admin write-path success (PR9F-06).

Run via the Week 3 scratch guard against a migrated scratch DB:

    python3 scripts/week3-scratch-guard.py run \\
        --db-name astra_week3_pr09_verify_api \\
        --url postgresql+asyncpg://postgres@127.0.0.1:49621/astra_week3_pr09_verify_api \\
        -- backend/.venv/bin/python -m pytest tests/test_pr09_verify_http.py -q
"""

from __future__ import annotations

import asyncio
import os
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

import main

LEAK_MARKER = "PR09LEAK_http_my_answer_4d1e"

FORBIDDEN_PUBLIC_FIELDS = {
    "my_answer",
    "source_draft_item_id",
    "subject_id",
    "version",
    "review_item_id",
    "status",
    "visibility",
    "question_id",
}


async def _with_session(fn):
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

    engine = create_async_engine(os.environ["DATABASE_URL"])
    try:
        async with AsyncSession(engine) as s:
            return await fn(s)
    finally:
        await engine.dispose()


@pytest.fixture(scope="module")
def client():
    with TestClient(main.app) as c:
        yield c


@pytest.fixture(scope="module")
def admin_client(client):
    asyncio.run(_login_admin(client))
    return client


async def _seed_note(slug: str, *, note_type: str = "mistake", **fields) -> str:
    async def _fn(s):
        note_id = uuid.uuid4()
        await s.execute(text(
            "INSERT INTO public.notes (id,slug,title,content,type,status,hidden,ef,interval,repetitions,"
            "question,my_answer,correct_answer,analysis,revision) "
            "VALUES (:id,:slug,:title,:content,:type,'published',false,2.5,0,0,"
            ":question,:my_answer,:correct_answer,:analysis,1)"
        ), {
            "id": note_id,
            "slug": slug,
            "title": fields.get("title", "http-fixture"),
            "content": fields.get("content", "content"),
            "type": note_type,
            "question": fields.get("question", "Q?"),
            "my_answer": fields.get("my_answer", "secret-my-answer"),
            "correct_answer": fields.get("correct_answer", "A"),
            "analysis": fields.get("analysis", "an"),
        })
        await s.commit()
        return str(note_id)
    return await _with_session(_fn)


async def _seed_public_mistake(*, visibility: str = "public", status: str = "active", my_answer: str = LEAK_MARKER) -> str:
    async def _fn(s):
        mistake_id = uuid.uuid4()
        subject_id = (await s.execute(
            text("INSERT INTO public.subjects (name) VALUES (:n) RETURNING id"),
            {"n": f"pr09-http-sub-{uuid.uuid4().hex[:8]}"},
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
                "VALUES (gen_random_uuid(),:s,'','Public question text','short_answer','[]','{}','a',"
                "'active','private',1) RETURNING id"
            ),
            {"s": subject_id},
        )).scalar_one()
        await s.execute(
            text(
                "INSERT INTO public.mistakes (id,source_draft_item_id,question_id,subject_id,title,question_text,"
                "my_answer,correct_answer,analysis,reason_category,mistake_reason,difficulty,status,visibility,version) "
                "VALUES (:id,:d,:q,:s,'Public Title','Public question text',"
                ":my_answer, 'CA-VALUE', 'AN-VALUE', 'concept', 'reason', 'easy', :status, :visibility, 1)"
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
        await s.execute(text(
            "INSERT INTO public.users (id,username,password_hash,is_admin) "
            "VALUES (:id,'pr09-http-admin',:pw,true) "
            "ON CONFLICT (username) DO UPDATE "
            "SET password_hash = EXCLUDED.password_hash, is_admin = true"
        ), {"id": user_id, "pw": hash_password("pr09-http-pass-123")})
        await s.commit()
    await _with_session(_fn)
    resp = client.post("/api/auth/login", json={"username": "pr09-http-admin", "password": "pr09-http-pass-123"})
    assert resp.status_code == 200, resp.text


# ---------------------------------------------------------------------------
# Public read: Empty envelope + field allowlist
# ---------------------------------------------------------------------------


def test_public_empty_envelope_explicit(client):
    """Honest empty envelope, isolated from rows committed by earlier modules.

    ``/api/public/mistakes`` has no tenant/filter scope, so ``empty=True`` is
    only observable when zero active public rows exist. Serve this one request
    from a transaction-scoped session that hides every active public mistake
    (uncommitted), then roll it back. The assertion is unchanged and the
    endpoint genuinely computes the empty envelope.
    """
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

    from app.database import get_db

    async def _isolated_empty_db():
        engine = create_async_engine(os.environ["DATABASE_URL"])
        conn = await engine.connect()
        trans = await conn.begin()
        session = AsyncSession(bind=conn, expire_on_commit=False)
        try:
            await session.execute(text(
                "UPDATE public.mistakes SET visibility='private' "
                "WHERE status='active' AND visibility='public'"
            ))
            await session.flush()
            yield session
        finally:
            await session.close()
            await trans.rollback()
            await conn.close()
            await engine.dispose()

    main.app.dependency_overrides[get_db] = _isolated_empty_db
    try:
        resp = client.get("/api/public/mistakes")
    finally:
        main.app.dependency_overrides.pop(get_db, None)

    assert resp.status_code == 200
    data = resp.json()
    assert data["empty"] is True
    assert isinstance(data["message"], str) and data["message"]
    assert data["items"] == []
    assert set(data.keys()) == {"items", "total", "page", "size", "empty", "message"}


def test_public_populated_allowlist_and_no_private_fields(client):
    mistake_id = asyncio.run(_seed_public_mistake(visibility="public", status="active", my_answer=LEAK_MARKER))
    asyncio.run(_seed_public_mistake(visibility="private", status="active", my_answer="PRIVATE_ROW_MUST_HIDE"))
    asyncio.run(_seed_public_mistake(visibility="public", status="archived", my_answer="ARCHIVED_MUST_HIDE"))

    resp = client.get("/api/public/mistakes")
    assert resp.status_code == 200
    data = resp.json()
    assert data["empty"] is False
    assert len(data["items"]) >= 1
    item = next(i for i in data["items"] if i["id"] == mistake_id)
    allowlist = {
        "id", "title", "question_text", "correct_answer", "analysis",
        "reason_category", "mistake_reason", "difficulty", "knowledge_point_ids",
        "created_at", "updated_at",
    }
    assert set(item.keys()) == allowlist
    for name in FORBIDDEN_PUBLIC_FIELDS:
        assert name not in item
    raw = resp.text
    assert LEAK_MARKER not in raw
    assert "PRIVATE_ROW_MUST_HIDE" not in raw
    assert "ARCHIVED_MUST_HIDE" not in raw
    assert "my_answer" not in raw
    assert "CA-VALUE" in raw


# ---------------------------------------------------------------------------
# Anonymous admin -> 401/403
# ---------------------------------------------------------------------------


def test_anonymous_admin_list_401_403(client):
    assert client.get("/api/admin/mistakes").status_code in (401, 403)


def test_anonymous_admin_update_401_403(client):
    resp = client.put(
        f"/api/admin/mistakes/{uuid.uuid4()}",
        json={"version": 1, "my_answer": "x"},
    )
    assert resp.status_code in (401, 403)


def test_anonymous_visibility_patch_401_403(client):
    resp = client.patch(
        f"/api/admin/mistakes/{uuid.uuid4()}/visibility",
        json={"version": 1, "visibility": "public"},
    )
    assert resp.status_code in (401, 403)


def test_anonymous_legacy_note_create_401_403(client):
    resp = client.post("/api/notes", json={"slug": "x", "title": "t", "content": "c", "type": "note"})
    assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# F-1..F-9 freeze negatives (410 + code legacy_mistake_write_frozen)
# ---------------------------------------------------------------------------


def _assert_frozen(resp, operation: str) -> None:
    assert resp.status_code == 410, (operation, resp.status_code, resp.text)
    detail = resp.json()["detail"]
    assert detail["code"] == "legacy_mistake_write_frozen"
    assert detail["operation"] == operation


def test_F1_create_type_mistake_frozen(admin_client):
    resp = admin_client.post("/api/notes", json={
        "slug": f"pr09-f1-{uuid.uuid4().hex[:8]}",
        "title": "t", "content": "c", "type": "mistake",
    })
    _assert_frozen(resp, "notes.create")


def test_F2_update_type_into_mistake_frozen(admin_client):
    slug = f"pr09-f2-{uuid.uuid4().hex[:8]}"
    asyncio.run(_seed_note(slug, note_type="note"))
    resp = admin_client.put(f"/api/notes/{slug}", json={"type": "mistake"})
    _assert_frozen(resp, "notes.update")


def test_F3_promote_to_mistake_frozen(admin_client):
    slug = f"pr09-f3-{uuid.uuid4().hex[:8]}"
    asyncio.run(_seed_note(slug, note_type="note"))
    resp = admin_client.post(f"/api/notes/{slug}/promote", params={"new_type": "mistake"})
    _assert_frozen(resp, "notes.promote")


def test_F4_legacy_writer_ui_create_path_frozen(admin_client):
    resp = admin_client.post("/api/notes", json={
        "slug": f"pr09-f4-{uuid.uuid4().hex[:8]}",
        "title": "t", "content": "c", "type": "mistake",
    })
    _assert_frozen(resp, "notes.create")


def test_F5_legacy_writer_ui_edit_save_frozen(admin_client):
    slug = f"pr09-f5-{uuid.uuid4().hex[:8]}"
    asyncio.run(_seed_note(slug, note_type="mistake", my_answer="legacy-edit-target"))
    resp = admin_client.put(f"/api/notes/{slug}", json={"content": "edited-by-legacy-writer"})
    _assert_frozen(resp, "notes.update")


def test_F6_write_note_mistake_content_save_frozen(admin_client):
    slug = f"pr09-f6-{uuid.uuid4().hex[:8]}"
    asyncio.run(_seed_note(slug, note_type="mistake", content="original"))
    resp = admin_client.put(f"/api/notes/{slug}", json={"content": "write-note-save"})
    _assert_frozen(resp, "notes.update")


def test_F7_sm2_submit_frozen(admin_client):
    slug = f"pr09-f7-{uuid.uuid4().hex[:8]}"
    asyncio.run(_seed_note(slug, note_type="mistake"))
    resp = admin_client.post(f"/api/review/{slug}", json={"quality": 5})
    _assert_frozen(resp, "review.sm2_submit")


def test_F8_field_update_frozen(admin_client):
    slug = f"pr09-f8-{uuid.uuid4().hex[:8]}"
    asyncio.run(_seed_note(slug, note_type="mistake"))
    resp = admin_client.put(f"/api/notes/{slug}", json={"title": "renamed", "my_answer": "changed"})
    _assert_frozen(resp, "notes.update")


def test_F9_delete_frozen(admin_client):
    slug = f"pr09-f9-{uuid.uuid4().hex[:8]}"
    asyncio.run(_seed_note(slug, note_type="mistake"))
    resp = admin_client.delete(f"/api/notes/{slug}")
    _assert_frozen(resp, "notes.delete")


def test_F9_batch_delete_frozen(admin_client):
    slug = f"pr09-f9b-{uuid.uuid4().hex[:8]}"
    asyncio.run(_seed_note(slug, note_type="mistake"))
    resp = admin_client.post("/api/notes/batch-delete", json=[slug])
    _assert_frozen(resp, "notes.batch_delete")


def test_note_type_create_still_allowed(admin_client):
    resp = admin_client.post("/api/notes", json={
        "slug": f"pr09-ok-{uuid.uuid4().hex[:8]}",
        "title": "t", "content": "c", "type": "note",
    })
    assert resp.status_code == 201, resp.text


# ---------------------------------------------------------------------------
# Compat reads K sampling still 200
# ---------------------------------------------------------------------------


def test_compat_read_list_notes(admin_client):
    resp = admin_client.get("/api/notes")
    assert resp.status_code == 200


def test_notes_list_types_filter_is_a_server_side_whitelist(admin_client):
    # A12: the manage list must exclude legacy rows server-side.
    note_slug = f"a12-note-{uuid.uuid4().hex[:8]}"
    blog_slug = f"a12-blog-{uuid.uuid4().hex[:8]}"
    mistake_slug = f"a12-mistake-{uuid.uuid4().hex[:8]}"
    asyncio.run(_seed_note(note_slug, note_type="note"))
    asyncio.run(_seed_note(blog_slug, note_type="blog"))
    asyncio.run(_seed_note(mistake_slug, note_type="mistake"))

    resp = admin_client.get("/api/notes?types=note,blog&size=100")
    assert resp.status_code == 200, resp.text
    listed = resp.json()["items"]
    assert all(item["type"] in {"note", "blog"} for item in listed)
    slugs = {item["slug"] for item in listed}
    assert note_slug in slugs and blog_slug in slugs
    assert mistake_slug not in slugs

    only_mistake = admin_client.get("/api/notes?types=mistake&size=100")
    assert only_mistake.status_code == 200
    assert all(item["type"] == "mistake" for item in only_mistake.json()["items"])


def test_compat_read_search(admin_client):
    resp = admin_client.post("/api/admin/search", json={"query": "verify", "limit": 5})
    assert resp.status_code == 200


def test_compat_read_review_queue(admin_client):
    resp = admin_client.get("/api/review/queue")
    assert resp.status_code == 200


def test_compat_read_get_single_mistake_note(admin_client):
    slug = f"pr09-kget-{uuid.uuid4().hex[:8]}"
    asyncio.run(_seed_note(slug, note_type="mistake"))
    resp = admin_client.get(f"/api/notes/{slug}")
    assert resp.status_code == 200
    assert resp.json()["type"] == "mistake"


# ---------------------------------------------------------------------------
# Admin write-path success (PR9F-06) + optimistic lock
# ---------------------------------------------------------------------------


def test_visibility_wrong_version_409(admin_client):
    mistake_id = asyncio.run(_seed_public_mistake(visibility="private", status="active"))
    resp = admin_client.patch(
        f"/api/admin/mistakes/{mistake_id}/visibility",
        json={"version": 99, "visibility": "public"},
    )
    assert resp.status_code == 409, (resp.status_code, resp.text)


def test_visibility_correct_version_toggles(admin_client):
    mistake_id = asyncio.run(_seed_public_mistake(visibility="private", status="active"))
    resp = admin_client.patch(
        f"/api/admin/mistakes/{mistake_id}/visibility",
        json={"version": 1, "visibility": "public"},
    )
    assert resp.status_code == 200, (resp.status_code, resp.text)
    body = resp.json()
    assert body["visibility"] == "public"
    assert body["version"] == 2
    resp2 = admin_client.patch(
        f"/api/admin/mistakes/{mistake_id}/visibility",
        json={"version": 2, "visibility": "private"},
    )
    assert resp2.status_code == 200
    assert resp2.json()["visibility"] == "private"
    assert resp2.json()["version"] == 3


def test_put_mistake_success_200(admin_client):
    mistake_id = asyncio.run(_seed_public_mistake(visibility="private", status="active"))
    resp = admin_client.put(
        f"/api/admin/mistakes/{mistake_id}",
        json={"version": 1, "my_answer": "updated-answer", "mistake_reason": "revised"},
    )
    assert resp.status_code == 200, (resp.status_code, resp.text)
    body = resp.json()
    assert body["my_answer"] == "updated-answer"
    assert body["mistake_reason"] == "revised"
    assert body["version"] == 2


def test_put_mistake_wrong_version_409(admin_client):
    mistake_id = asyncio.run(_seed_public_mistake(visibility="private", status="active"))
    resp = admin_client.put(
        f"/api/admin/mistakes/{mistake_id}",
        json={"version": 99, "my_answer": "x"},
    )
    assert resp.status_code == 409, (resp.status_code, resp.text)


def test_delete_mistake_success_200(admin_client):
    mistake_id = asyncio.run(_seed_public_mistake(visibility="private", status="active"))
    resp = admin_client.request(
        "DELETE", f"/api/admin/mistakes/{mistake_id}",
        json={"version": 1},
    )
    assert resp.status_code == 200, (resp.status_code, resp.text)
    body = resp.json()
    assert body["status"] == "archived"
    assert body["version"] == 2


def test_delete_mistake_wrong_version_409(admin_client):
    mistake_id = asyncio.run(_seed_public_mistake(visibility="private", status="active"))
    resp = admin_client.request(
        "DELETE", f"/api/admin/mistakes/{mistake_id}",
        json={"version": 99},
    )
    assert resp.status_code == 409, (resp.status_code, resp.text)
