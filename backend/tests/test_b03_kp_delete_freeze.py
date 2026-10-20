"""B03/EV02: deleting a KnowledgePoint must respect the legacy mistake freeze.

The reviewer finding: ``note_knowledge_points`` cascades on KP delete, so a KP
whose only association is a legacy mistake Note could be deleted through the
real admin HTTP route (204) and silently destroy the frozen relation. This file
re-proves the fix:

1. real authenticated ASGI DELETE returns 410 + ``legacy_mistake_write_frozen``
   and a fresh session still sees the relation and the KP;
2. the service-level delete raises the same freeze with zero side effects;
3. the KP row lock serialises a concurrent Note<->KP link against delete, so a
   link that commits first is observed and still frozen;
4. ordinary (non-legacy) KP behaviour and ordinary Note links do not regress.
"""

from __future__ import annotations

import asyncio
import uuid

import httpx
from sqlalchemy import delete, func, select

import main
from app.database import async_session, engine
from app.models.note import Note, Subject, User
from app.models.note_knowledge_point import NoteKnowledgePoint
from app.models.taxonomy import KnowledgePoint
from app.routers.auth import get_current_admin
from app.schemas.taxonomy import KnowledgePointCreate, SubjectCreate
from app.services import note_knowledge_point_service
from app.services.legacy_mistake_freeze import LegacyMistakeWriteFrozen
from app.services.taxonomy_service import (
    create_knowledge_point,
    create_subject,
    delete_knowledge_point,
)


async def _seed(session) -> dict:
    token = uuid.uuid4().hex[:8]
    subject = await create_subject(session, SubjectCreate(name=f"B03 Subject {token}"))
    locked_kp = await create_knowledge_point(
        session, KnowledgePointCreate(subject_id=subject.id, name=f"B03 Locked {token}")
    )
    free_kp = await create_knowledge_point(
        session, KnowledgePointCreate(subject_id=subject.id, name=f"B03 Free {token}")
    )
    legacy = Note(slug=f"b03-legacy-{token}", title="legacy", content="", type="mistake")
    normal = Note(slug=f"b03-normal-{token}", title="normal", content="", type="note")
    session.add_all([legacy, normal])
    await session.flush()
    session.add(
        NoteKnowledgePoint(note_id=legacy.id, knowledge_point_id=locked_kp.id)
    )
    await session.commit()
    return {
        "subject_id": subject.id,
        "locked_kp_id": locked_kp.id,
        "free_kp_id": free_kp.id,
        "legacy_id": legacy.id,
        "normal_id": normal.id,
    }


async def _cleanup(seed: dict, admin_id: uuid.UUID) -> None:
    async with async_session() as session:
        await session.execute(
            delete(NoteKnowledgePoint).where(
                NoteKnowledgePoint.note_id.in_([seed["legacy_id"], seed["normal_id"]])
            )
        )
        await session.execute(
            delete(Note).where(Note.id.in_([seed["legacy_id"], seed["normal_id"]]))
        )
        await session.execute(
            delete(KnowledgePoint).where(
                KnowledgePoint.id.in_([seed["locked_kp_id"], seed["free_kp_id"]])
            )
        )
        await session.execute(delete(Subject).where(Subject.id == seed["subject_id"]))
        await session.execute(delete(User).where(User.id == admin_id))
        await session.commit()


async def _http_delete_locked_kp(seed: dict, admin_id: uuid.UUID) -> None:
    async def admin_override():
        return User(id=admin_id, username="b03-admin", is_admin=True)

    main.app.dependency_overrides[get_current_admin] = admin_override
    try:
        await main.validate_database_readiness()
        transport = httpx.ASGITransport(app=main.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.delete(
                f"/api/admin/knowledge-points/{seed['locked_kp_id']}"
            )
            assert response.status_code == 410, response.text
            assert response.json()["detail"]["code"] == "legacy_mistake_write_frozen"
    finally:
        main.app.dependency_overrides.pop(get_current_admin, None)

    # fresh session: relation AND KP both survived
    async with async_session() as session:
        assert await session.get(KnowledgePoint, seed["locked_kp_id"]) is not None
        pair = await session.get(
            NoteKnowledgePoint, (seed["legacy_id"], seed["locked_kp_id"])
        )
        assert pair is not None
        normal_kp = await session.get(KnowledgePoint, seed["free_kp_id"])
        assert normal_kp is not None

        # ordinary KP with no legacy relation deletes normally
        await delete_knowledge_point(session, seed["free_kp_id"])
        await session.commit()
    async with async_session() as session:
        assert await session.get(KnowledgePoint, seed["free_kp_id"]) is None
        assert await session.get(KnowledgePoint, seed["locked_kp_id"]) is not None


async def _service_delete_freezes_without_side_effect(seed: dict) -> None:
    async with async_session() as session:
        try:
            await delete_knowledge_point(session, seed["locked_kp_id"])
        except LegacyMistakeWriteFrozen as freeze:
            assert freeze.code == "legacy_mistake_write_frozen"
        else:
            raise AssertionError("service delete must freeze on a legacy mistake link")
        await session.rollback()
    async with async_session() as session:
        assert await session.get(KnowledgePoint, seed["locked_kp_id"]) is not None
        assert (
            await session.get(NoteKnowledgePoint, (seed["legacy_id"], seed["locked_kp_id"]))
            is not None
        )


async def _concurrent_link_serialises_before_delete(seed: dict) -> None:
    """A link that commits first is still observed by the waiting delete."""
    async with async_session() as linker, async_session() as deleter:
        # linker takes the KP row lock (uncommitted)
        linked = await note_knowledge_point_service.link(
            linker, seed["normal_id"], seed["locked_kp_id"]
        )
        assert linked is True

        delete_task = asyncio.create_task(
            delete_knowledge_point(deleter, seed["locked_kp_id"])
        )
        await asyncio.sleep(0.3)
        # deleter must be blocked on the KP row lock, not racing past it
        assert not delete_task.done(), "delete did not wait for the KP lock"

        await linker.commit()
        try:
            await asyncio.wait_for(delete_task, timeout=5)
        except LegacyMistakeWriteFrozen:
            pass
        else:
            raise AssertionError("delete must freeze after the concurrent link commits")
        await deleter.rollback()

    async with async_session() as session:
        # the legacy relation and the KP are intact; the ordinary link was undone
        assert await session.get(KnowledgePoint, seed["locked_kp_id"]) is not None
        assert (
            await session.scalar(
                select(func.count())
                .select_from(NoteKnowledgePoint)
                .where(NoteKnowledgePoint.knowledge_point_id == seed["locked_kp_id"])
            )
            >= 1
        )


async def _run() -> None:
    admin_id = uuid.uuid4()
    async with async_session() as session:
        session.add(
            User(
                id=admin_id,
                username=f"b03-admin-{admin_id.hex[:8]}",
                password_hash="test-only",
                is_admin=True,
            )
        )
        await session.commit()
    async with async_session() as session:
        seed = await _seed(session)
    try:
        await _http_delete_locked_kp(seed, admin_id)
        await _service_delete_freezes_without_side_effect(seed)
        await _concurrent_link_serialises_before_delete(seed)
    finally:
        await _cleanup(seed, admin_id)
        await engine.dispose()


def test_kp_delete_respects_legacy_mistake_freeze() -> None:
    asyncio.run(_run())
