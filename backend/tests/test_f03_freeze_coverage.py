"""F03: legacy mistake metadata write-freeze coverage (suggestions, folders,
tags, Note<->KP links).

True ASGI handler + PostgreSQL metadata-write probes. The admin dependency is
overridden only to reach the freeze branch; this file makes NO claim about
authentication (see test_pr09_* for the auth boundary).
"""

from __future__ import annotations

import asyncio
import uuid

import httpx
from sqlalchemy import delete, select

import main
from app.database import async_session, engine
from app.models.folder import Folder
from app.models.note import Note, Subject, Tag, User, note_tags
from app.models.taxonomy import KnowledgePoint
from app.routers.auth import get_current_admin
from app.schemas.taxonomy import KnowledgePointCreate, SubjectCreate
from app.services.taxonomy_service import create_knowledge_point, create_subject


async def _seed(session) -> dict:
    token = uuid.uuid4().hex[:8]
    mistake = Note(slug=f"f03-mistake-{token}", title="m", content="", type="mistake")
    normal = Note(slug=f"f03-note-{token}", title="n", content="", type="note")
    folder = Folder(name=f"f03-folder-{token}")
    tag_target = Tag(name=f"f03-tag-{token}")
    session.add_all([mistake, normal, folder, tag_target])
    await session.flush()
    await session.execute(
        note_tags.insert().values(note_id=mistake.id, tag_id=tag_target.id)
    )
    await session.flush()
    subject = await create_subject(session, SubjectCreate(name=f"F03 Subject {token}"))
    kp = await create_knowledge_point(
        session, KnowledgePointCreate(subject_id=subject.id, name=f"F03 KP {token}")
    )
    seed = {
        "mistake_id": mistake.id,
        "normal_id": normal.id,
        "mistake_slug": mistake.slug,
        "normal_slug": normal.slug,
        "folder_id": folder.id,
        "tag_id": tag_target.id,
        "subject_id": subject.id,
        "kp_id": kp.id,
    }
    await session.commit()
    return seed


async def _cleanup(seed: dict, admin_id: uuid.UUID) -> None:
    async with async_session() as session:
        await session.execute(
            delete(note_tags).where(
                note_tags.c.note_id.in_([seed["mistake_id"], seed["normal_id"]])
            )
        )
        await session.execute(
            delete(Note).where(Note.id.in_([seed["mistake_id"], seed["normal_id"]]))
        )
        await session.execute(delete(Tag).where(Tag.id == seed["tag_id"]))
        await session.execute(delete(Folder).where(Folder.id == seed["folder_id"]))
        await session.execute(delete(KnowledgePoint).where(KnowledgePoint.id == seed["kp_id"]))
        await session.execute(delete(Subject).where(Subject.id == seed["subject_id"]))
        await session.execute(delete(User).where(User.id == admin_id))
        await session.commit()


async def _run() -> None:
    admin_id = uuid.uuid4()

    async def admin_override():
        return User(id=admin_id, username="f03-admin", is_admin=True)

    async with async_session() as session:
        session.add(User(id=admin_id, username=f"f03-admin-{admin_id.hex[:8]}", password_hash="test-only", is_admin=True))
        await session.commit()

    async with async_session() as session:
        seed = await _seed(session)
    mistake_id = seed["mistake_id"]
    normal_id = seed["normal_id"]
    mistake_slug = seed["mistake_slug"]
    normal_slug = seed["normal_slug"]
    folder_id = seed["folder_id"]
    tag_id = seed["tag_id"]
    kp_id = seed["kp_id"]

    main.app.dependency_overrides[get_current_admin] = admin_override
    try:
        await main.validate_database_readiness()
        transport = httpx.ASGITransport(app=main.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            # 1. suggestions move_to_folder on a legacy mistake -> 410, no write
            r = await client.post(
                "/api/ai/suggestions/execute",
                json={"type": "suggestion", "action": "move_to_folder", "folder_id": str(folder_id), "targets": [mistake_slug]},
            )
            assert r.status_code == 410, r.text
            assert r.json()["detail"]["code"] == "legacy_mistake_write_frozen"
            async with async_session() as session:
                fresh = await session.get(Note, mistake_id)
                assert fresh.folder_id is None

            # 2. mixed batch (mistake first) -> 410 and the ordinary note is untouched
            r = await client.post(
                "/api/ai/suggestions/execute",
                json={
                    "type": "suggestion",
                    "action": "move_to_folder",
                    "folder_id": str(folder_id),
                    "targets": [mistake_slug, normal_slug],
                },
            )
            assert r.status_code == 410, r.text
            async with async_session() as session:
                assert (await session.get(Note, normal_id)).folder_id is None
                assert (await session.get(Note, mistake_id)).folder_id is None

            # 3. ordinary-only batch succeeds
            r = await client.post(
                "/api/ai/suggestions/execute",
                json={"type": "suggestion", "action": "move_to_folder", "folder_id": str(folder_id), "targets": [normal_slug]},
            )
            assert r.status_code == 200, r.text
            assert r.json()["executed"] == 1
            async with async_session() as session:
                assert (await session.get(Note, normal_id)).folder_id == folder_id

            # 4. add_tag on a legacy mistake -> 410
            r = await client.post(
                "/api/ai/suggestions/execute",
                json={"type": "suggestion", "action": "add_tag", "tag": f"f03-new-{uuid.uuid4().hex[:6]}", "targets": [mistake_slug]},
            )
            assert r.status_code == 410, r.text

            # 5. folders.move-note on a legacy mistake -> 410
            r = await client.post(
                f"/api/folders/move-note/{mistake_slug}",
                json={"folder_id": str(folder_id)},
            )
            assert r.status_code == 410, r.text

            # 6. deleting a tag attached to a legacy mistake -> 410
            r = await client.delete(f"/api/tags/{tag_id}")
            assert r.status_code == 410, r.text

            # 7. Note<->KP link on a legacy mistake -> 410
            r = await client.post(f"/api/admin/notes/{mistake_id}/knowledge-points/{kp_id}")
            assert r.status_code == 410, r.text
            # ordinary note link still succeeds
            r = await client.post(f"/api/admin/notes/{normal_id}/knowledge-points/{kp_id}")
            assert r.status_code == 200, r.text
    finally:
        main.app.dependency_overrides.pop(get_current_admin, None)
        await _cleanup(seed, admin_id)
        await engine.dispose()


def test_legacy_mistake_metadata_writes_are_frozen() -> None:
    asyncio.run(_run())
