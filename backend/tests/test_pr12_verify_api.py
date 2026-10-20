"""PR-12 independent API/contract verifier (PR-12-verify).

Run ONLY through the Week 3 scratch guard against a migrated (032) scratch DB:

    python3 scripts/week3-scratch-guard.py run --db-name astra_week3_pr12_verify \\
        -- backend/.venv/bin/python -m pytest tests/test_pr12_verify_api.py -q

Verifies:
  * router/admin gate (anonymous 401/403)
  * link/unlink idempotency + duplicates
  * 404 for missing note/KP on link, unlink and both list directions
  * list direction correctness (note->KP and KP->note)
  * concurrent duplicate link does not surface a 500 (deterministic race)
  * direct IntegrityError branch is converted to an idempotent no-op
"""

from __future__ import annotations

import asyncio
import os
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import main
from app.models.note import Note, Subject
from app.models.note_knowledge_point import NoteKnowledgePoint
from app.models.taxonomy import KnowledgePoint
from app.services import note_knowledge_point_service as service
from app.utils.auth import hash_password


def _sync_url() -> str:
    return os.environ["DATABASE_URL"]


NOTE_KP = "/api/admin/notes/{note_id}/knowledge-points/{kp_id}"
NOTE_KP_LIST = "/api/admin/notes/{note_id}/knowledge-points"
KP_NOTES = "/api/admin/notes/knowledge-points/{kp_id}/notes"


async def _seed() -> dict:
    engine = create_async_engine(_sync_url())
    suffix = uuid.uuid4().hex[:8]
    try:
        async with AsyncSession(engine) as s:
            from sqlalchemy import text

            await s.execute(
                text(
                    "INSERT INTO public.users (id,username,password_hash,is_admin) "
                    "VALUES (:i,:u,:p,true)"
                ),
                {"i": uuid.uuid4(), "u": f"pr12v-admin-{suffix}", "p": hash_password("pr12v-pass-123")},
            )
            sid = (await s.execute(text("INSERT INTO public.subjects(name) VALUES(:n) RETURNING id"), {"n": f"pr12v-subj-{suffix}"})).scalar_one()
            kp = (await s.execute(text("INSERT INTO public.knowledge_points(subject_id,name) VALUES(:s,:n) RETURNING id"), {"s": sid, "n": f"pr12v-kp-{suffix}"})).scalar_one()
            note = (await s.execute(text(
                "INSERT INTO public.notes(id,slug,title,content,type,ef,interval,repetitions) "
                "VALUES(gen_random_uuid(),:slug,'t','c','note',2.5,0,0) RETURNING id"),
                {"slug": f"pr12v-note-{suffix}"})).scalar_one()
            await s.commit()
    finally:
        await engine.dispose()
    return {"username": f"pr12v-admin-{suffix}", "password": "pr12v-pass-123",
            "note_id": str(note), "kp_id": int(kp)}


@pytest.fixture(scope="module")
def client():
    with TestClient(main.app) as c:
        yield c


@pytest.fixture(scope="module")
def seeded():
    return asyncio.run(_seed())


def paths(s):
    return {"link": NOTE_KP.format(note_id=s["note_id"], kp_id=s["kp_id"]),
            "note_list": NOTE_KP_LIST.format(note_id=s["note_id"]),
            "kp_list": KP_NOTES.format(kp_id=s["kp_id"])}


def test_anonymous_all_routes_rejected(client, seeded):
    p = paths(seeded)
    for method, url in [("post", p["link"]), ("delete", p["link"]),
                        ("get", p["note_list"]), ("get", p["kp_list"])]:
        resp = getattr(client, method)(url)
        assert resp.status_code in (401, 403), (method, url, resp.status_code)


def test_admin_link_idempotent_unlink_idempotent_and_lists(client, seeded):
    p = paths(seeded)
    assert client.post("/api/auth/login", json={"username": seeded["username"], "password": seeded["password"]}).status_code == 200

    first = client.post(p["link"])
    assert first.status_code == 200, first.text
    assert first.json() == {"note_id": seeded["note_id"], "knowledge_point_id": seeded["kp_id"], "linked": True}

    dup = client.post(p["link"])
    assert dup.status_code == 200, dup.text
    assert dup.json()["linked"] is True

    note_view = client.get(p["note_list"])
    assert note_view.status_code == 200
    assert [row["id"] for row in note_view.json()] == [seeded["kp_id"]]

    kp_view = client.get(p["kp_list"])
    assert kp_view.status_code == 200
    assert seeded["note_id"] in {row["id"] for row in kp_view.json()}
    assert {"id", "slug", "title", "type", "status", "hidden"} <= set(kp_view.json()[0])

    assert client.delete(p["link"]).status_code == 204
    assert client.delete(p["link"]).status_code == 204
    assert client.get(p["note_list"]).json() == []
    assert seeded["note_id"] not in {row["id"] for row in client.get(p["kp_list"]).json()}


def test_missing_note_and_kp_are_404(client, seeded):
    p = paths(seeded)
    assert client.post(NOTE_KP.format(note_id=uuid.uuid4(), kp_id=seeded["kp_id"])).status_code == 404
    assert client.post(NOTE_KP.format(note_id=seeded["note_id"], kp_id=2_000_000_000)).status_code == 404
    assert client.delete(NOTE_KP.format(note_id=uuid.uuid4(), kp_id=seeded["kp_id"])).status_code == 404
    assert client.delete(NOTE_KP.format(note_id=seeded["note_id"], kp_id=2_000_000_000)).status_code == 404
    assert client.get(NOTE_KP_LIST.format(note_id=uuid.uuid4())).status_code == 404
    assert client.get(KP_NOTES.format(kp_id=2_000_000_000)).status_code == 404
    _ = p


def _maker(url: str):
    eng = create_async_engine(url)
    return eng, async_sessionmaker(eng, class_=AsyncSession, expire_on_commit=False)


async def _race_setup(suffix: str):
    engine = create_async_engine(_sync_url())
    try:
        async with AsyncSession(engine) as s:
            subject = Subject(name=f"pr12v-race-subj-{suffix}", status="active", sort_order=0)
            s.add(subject)
            await s.flush()
            kp = KnowledgePoint(subject_id=subject.id, name=f"pr12v-race-kp-{suffix}", status="active", sort_order=0)
            note = Note(slug=f"pr12v-race-note-{suffix}", title="race", content="b", type="note")
            s.add_all([kp, note])
            await s.flush()
            ids = (uuid.UUID(str(note.id)), int(kp.id))
            await s.commit()
            return ids
    finally:
        await engine.dispose()


def test_concurrent_duplicate_link_no_500():
    async def run():
        suffix = uuid.uuid4().hex[:8]
        note_id, kp_id = await _race_setup(suffix)
        eng, maker = _maker(_sync_url())
        holder = maker()
        racer = maker()
        try:
            holder.add(NoteKnowledgePoint(note_id=note_id, knowledge_point_id=kp_id))
            await holder.flush()
            task = asyncio.create_task(service.link(racer, note_id, kp_id))
            await asyncio.sleep(0.3)
            assert not task.done(), "racer must be blocked on the unique key"
            await holder.commit()
            created = await asyncio.wait_for(task, timeout=10)
            assert created is False
            count = await racer.scalar(select(func.count()).select_from(NoteKnowledgePoint).where(
                NoteKnowledgePoint.note_id == note_id, NoteKnowledgePoint.knowledge_point_id == kp_id))
            assert count == 1
        finally:
            cleanup = maker()
            try:
                from sqlalchemy import text
                await cleanup.execute(NoteKnowledgePoint.__table__.delete().where(NoteKnowledgePoint.note_id == note_id))
                await cleanup.execute(Note.__table__.delete().where(Note.id == note_id))
                await cleanup.execute(KnowledgePoint.__table__.delete().where(KnowledgePoint.id == kp_id))
                await cleanup.execute(text("DELETE FROM public.subjects WHERE name LIKE 'pr12v-race-subj-%'"))
                await cleanup.commit()
            finally:
                await cleanup.close()
            await holder.close()
            await racer.close()
            await eng.dispose()

    asyncio.run(run())


def test_integrity_error_branch_is_idempotent(monkeypatch):
    """Deterministic direct IntegrityError path (no timing reliance)."""
    async def run():
        suffix = uuid.uuid4().hex[:8]
        note_id, kp_id = await _race_setup(suffix)
        eng, maker = _maker(_sync_url())
        winner = maker()
        try:
            winner.add(NoteKnowledgePoint(note_id=note_id, knowledge_point_id=kp_id))
            await winner.commit()
        finally:
            await winner.close()

        loser = maker()
        real_get = loser.get
        state = {"n": 0}

        async def fake_get(entity, ident, *a, **k):
            if entity is NoteKnowledgePoint:
                state["n"] += 1
                if state["n"] == 1:
                    return None  # force insert -> IntegrityError branch
            return await real_get(entity, ident, *a, **k)

        monkeypatch.setattr(loser, "get", fake_get)
        created = await service.link(loser, note_id, kp_id)
        assert created is False
        cleanup = maker()
        try:
            await cleanup.execute(NoteKnowledgePoint.__table__.delete().where(NoteKnowledgePoint.note_id == note_id))
            await cleanup.execute(Note.__table__.delete().where(Note.id == note_id))
            await cleanup.execute(KnowledgePoint.__table__.delete().where(KnowledgePoint.id == kp_id))
            await cleanup.commit()
        finally:
            await cleanup.close()
            await loser.close()
            await eng.dispose()

    asyncio.run(run())
