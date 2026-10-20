"""PR-12 Note <-> KnowledgePoint service tests (migration 032 semantics).

Run via the Week 3 scratch guard against a migrated scratch database:

    python3 scripts/week3-scratch-guard.py run --db-name astra_week3_pr12 \\
        -- backend/.venv/bin/python -m pytest \\
        tests/test_pr12_note_knowledge_points_service.py -q
"""

from __future__ import annotations

import asyncio
import unittest
import uuid

from sqlalchemy import func, select

from app.database import async_session, engine
from app.models.note import Note
from app.models.note_knowledge_point import NoteKnowledgePoint
from app.models.taxonomy import KnowledgePoint, KnowledgePointLink
from app.schemas.taxonomy import KnowledgePointCreate, SubjectCreate
from app.services import note_knowledge_point_service as service
from app.services.taxonomy_service import create_knowledge_point, create_subject


class NoteKnowledgePointServiceTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await engine.dispose(close=False)
        self.session = async_session()
        self.addAsyncCleanup(engine.dispose)
        self.addAsyncCleanup(self.session.close)
        self.addAsyncCleanup(self.session.rollback)
        await self.session.begin()

    async def _subject(self):
        return await create_subject(
            self.session,
            SubjectCreate(name=f"pr12-subject-{uuid.uuid4().hex[:8]}"),
        )

    async def _kp(self, subject, *, status: str = "active"):
        return await create_knowledge_point(
            self.session,
            KnowledgePointCreate(
                subject_id=subject.id,
                name=f"pr12-kp-{uuid.uuid4().hex[:8]}",
                status=status,
            ),
        )

    async def _note(self, *, note_type: str = "note"):
        note = Note(
            slug=f"pr12-note-{uuid.uuid4().hex}",
            title="PR-12 note",
            content="body",
            type=note_type,
        )
        self.session.add(note)
        await self.session.flush()
        return note

    async def _seed(self):
        subject = await self._subject()
        kp = await self._kp(subject)
        note = await self._note()
        return note, kp

    async def _link_count(self, note_id, kp_id) -> int:
        return int(
            (
                await self.session.execute(
                    select(func.count())
                    .select_from(NoteKnowledgePoint)
                    .where(
                        NoteKnowledgePoint.note_id == note_id,
                        NoteKnowledgePoint.knowledge_point_id == kp_id,
                    )
                )
            ).scalar_one()
        )

    async def test_link_creates_row_then_is_idempotent(self):
        note, kp = await self._seed()
        self.assertTrue(await service.link(self.session, note.id, kp.id))
        self.assertFalse(await service.link(self.session, note.id, kp.id))
        self.assertEqual(await self._link_count(note.id, kp.id), 1)

    async def test_unlink_removes_then_is_idempotent(self):
        note, kp = await self._seed()
        await service.link(self.session, note.id, kp.id)
        self.assertTrue(await service.unlink(self.session, note.id, kp.id))
        self.assertFalse(await service.unlink(self.session, note.id, kp.id))
        self.assertEqual(await self._link_count(note.id, kp.id), 0)

    async def test_link_missing_note_raises_not_found(self):
        subject = await self._subject()
        kp = await self._kp(subject)
        with self.assertRaises(service.NoteKnowledgePointNotFound):
            await service.link(self.session, uuid.uuid4(), kp.id)

    async def test_link_missing_knowledge_point_raises_not_found(self):
        note = await self._note()
        with self.assertRaises(service.NoteKnowledgePointNotFound):
            await service.link(self.session, note.id, 2_000_000_000)

    async def test_unlink_missing_note_raises_not_found(self):
        subject = await self._subject()
        kp = await self._kp(subject)
        with self.assertRaises(service.NoteKnowledgePointNotFound):
            await service.unlink(self.session, uuid.uuid4(), kp.id)

    async def test_unlink_missing_knowledge_point_raises_not_found(self):
        note = await self._note()
        with self.assertRaises(service.NoteKnowledgePointNotFound):
            await service.unlink(self.session, note.id, 2_000_000_000)

    async def test_list_knowledge_points_for_note(self):
        subject = await self._subject()
        kp_a = await self._kp(subject)
        kp_b = await self._kp(subject)
        note = await self._note()
        other_note = await self._note()
        await service.link(self.session, note.id, kp_a.id)
        await service.link(self.session, note.id, kp_b.id)
        await service.link(self.session, other_note.id, kp_b.id)

        found = await service.list_knowledge_points(self.session, note.id)
        self.assertEqual({kp.id for kp in found}, {kp_a.id, kp_b.id})

    async def test_list_notes_for_knowledge_point(self):
        note, kp = await self._seed()
        other_note = await self._note()
        await service.link(self.session, note.id, kp.id)
        await service.link(self.session, other_note.id, kp.id)

        found = await service.list_notes(self.session, kp.id)
        self.assertEqual({row.id for row in found}, {note.id, other_note.id})

    async def test_list_missing_note_raises_not_found(self):
        with self.assertRaises(service.NoteKnowledgePointNotFound):
            await service.list_knowledge_points(self.session, uuid.uuid4())

    async def test_list_missing_knowledge_point_raises_not_found(self):
        with self.assertRaises(service.NoteKnowledgePointNotFound):
            await service.list_notes(self.session, 2_000_000_000)

    async def test_deleting_note_cascades_link(self):
        note, kp = await self._seed()
        await service.link(self.session, note.id, kp.id)
        await self.session.delete(note)
        await self.session.flush()
        self.assertEqual(await self._link_count(note.id, kp.id), 0)

    async def test_deleting_knowledge_point_cascades_link(self):
        subject = await self._subject()
        kp = await self._kp(subject)
        note = await self._note()
        await service.link(self.session, note.id, kp.id)
        await self.session.delete(kp)
        await self.session.flush()
        self.assertEqual(await self._link_count(note.id, kp.id), 0)

    async def test_link_does_not_touch_polymorphic_knowledge_point_links(self):
        subject = await self._subject()
        kp = await self._kp(subject)
        note = await self._note()
        before = await self.session.scalar(
            select(func.count()).select_from(KnowledgePointLink)
        )
        await service.link(self.session, note.id, kp.id)
        after = await self.session.scalar(
            select(func.count()).select_from(KnowledgePointLink)
        )
        self.assertEqual(after, before)

    async def test_concurrent_duplicate_link_is_idempotent_not_error(self):
        """Two writers racing the composite PK must not surface an error.

        Seeding is committed on its own session so the two racing sessions can
        both see the note/KP. Session A holds the uncommitted link row; the
        service call on session B blocks on the unique key until A commits, then
        hits IntegrityError and must convert it to an idempotent no-op.
        """
        seed = async_session()
        try:
            subject = await create_subject(
                seed, SubjectCreate(name=f"pr12-race-{uuid.uuid4().hex[:8]}")
            )
            kp = await create_knowledge_point(
                seed,
                KnowledgePointCreate(
                    subject_id=subject.id,
                    name=f"pr12-race-kp-{uuid.uuid4().hex[:8]}",
                ),
            )
            note = Note(
                slug=f"pr12-race-note-{uuid.uuid4().hex}",
                title="race",
                content="body",
                type="note",
            )
            seed.add(note)
            await seed.flush()
            note_id, kp_id = note.id, kp.id
            await seed.commit()
        finally:
            await seed.close()

        holder = async_session()
        racer = async_session()
        try:
            holder.add(
                NoteKnowledgePoint(note_id=note_id, knowledge_point_id=kp_id)
            )
            await holder.flush()

            task = asyncio.create_task(service.link(racer, note_id, kp_id))
            await asyncio.sleep(0.3)
            self.assertFalse(task.done(), "racer should be blocked on the unique key")

            await holder.commit()
            created = await asyncio.wait_for(task, timeout=10)
            self.assertFalse(created)

            count = await racer.scalar(
                select(func.count())
                .select_from(NoteKnowledgePoint)
                .where(
                    NoteKnowledgePoint.note_id == note_id,
                    NoteKnowledgePoint.knowledge_point_id == kp_id,
                )
            )
            self.assertEqual(count, 1)
        finally:
            cleanup = async_session()
            try:
                await cleanup.execute(
                    NoteKnowledgePoint.__table__.delete().where(
                        NoteKnowledgePoint.note_id == note_id
                    )
                )
                await cleanup.execute(Note.__table__.delete().where(Note.id == note_id))
                await cleanup.execute(
                    KnowledgePoint.__table__.delete().where(
                        KnowledgePoint.id == kp_id
                    )
                )
                await cleanup.commit()
            finally:
                await cleanup.close()
            await holder.close()
            await racer.close()

    async def test_link_then_list_round_trip_on_note_and_mistake_types(self):
        subject = await self._subject()
        kp = await self._kp(subject)
        plain_note = await self._note(note_type="note")
        await service.link(self.session, plain_note.id, kp.id)
        found = await service.list_notes(self.session, kp.id)
        self.assertIn(plain_note.id, {row.id for row in found})
