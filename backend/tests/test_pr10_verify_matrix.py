"""PR-10 independent verification: W3-D05 metric semantic fixture matrix.

Independent of the implementer's test file (test_pr10_kp_analytics_service.py):
re-seeds its own fixtures and asserts the contract directly against the service.

Run via the Week 3 scratch guard:

    python3 scripts/week3-scratch-guard.py run --db-name astra_week3_pr10_verify \
        -- backend/.venv/bin/python -m pytest tests/test_pr10_verify_matrix.py -q
"""

from __future__ import annotations

import unittest
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import event, func, select

from app.database import async_session, engine
from app.models.attempt import Attempt
from app.models.mistake import Mistake
from app.models.question import DraftItem, Question, QuestionKnowledgePoint
from app.models.review_item import ReviewItem, ReviewRecord
from app.models.taxonomy import KnowledgePoint, KnowledgePointLink
from app.schemas.question import QuestionDraftCreate
from app.schemas.taxonomy import KnowledgePointCreate, SubjectCreate
from app.services import kp_analytics_service
from app.services.draft_service import convert_question_draft, create_question_draft
from app.services.taxonomy_service import create_knowledge_point, create_subject

NOW = datetime(2026, 7, 1, 12, 0, tzinfo=timezone.utc)


class VerifyMatrixTest(unittest.IsolatedAsyncioTestCase):
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
            SubjectCreate(name=f"verify-{uuid.uuid4().hex[:8]}"),
        )

    async def _kp(self, subject, *, status: str = "active"):
        return await create_knowledge_point(
            self.session,
            KnowledgePointCreate(
                subject_id=subject.id,
                name=f"kp-{uuid.uuid4().hex[:8]}",
                status=status,
            ),
        )

    async def _question(self, subject, kp_ids, *, status: str = "active"):
        draft = await create_question_draft(
            self.session,
            QuestionDraftCreate(
                subject_id=subject.id,
                question_text=f"q-{uuid.uuid4().hex[:8]}?",
                question_type="short_answer",
                correct_answer="a",
                knowledge_point_ids=list(kp_ids),
            ),
        )
        question = await convert_question_draft(self.session, draft.item.id, version=1)
        if status != "active":
            stored = await self.session.get(Question, question.id)
            stored.status = status
            await self.session.flush()
        return question

    async def _attempt(self, question, *, correct, context="practice"):
        row = Attempt(
            question_id=question.id,
            submitted_answer="x",
            is_correct=correct,
            context_type=context,
        )
        self.session.add(row)
        await self.session.flush()
        return row

    async def _mistake(self, subject, question, kp_id, *, status="active"):
        item = DraftItem(
            draft_type="mistake",
            source_type="question",
            source_id=str(question.id),
            status="pending",
        )
        self.session.add(item)
        await self.session.flush()
        mistake = Mistake(
            source_draft_item_id=item.id,
            question_id=question.id,
            subject_id=subject.id,
            question_text="verify mistake",
            reason_category="concept",
            status=status,
        )
        self.session.add(mistake)
        await self.session.flush()
        self.session.add(
            KnowledgePointLink(
                knowledge_point_id=kp_id,
                target_type="mistake",
                target_id=str(mistake.id),
            )
        )
        await self.session.flush()
        return mistake

    async def _review_item(self, mistake, *, state="active", next_review_at):
        item = ReviewItem(
            target_type="mistake",
            target_id=str(mistake.id),
            mistake_id=mistake.id,
            state=state,
            interval_days=0,
            repetitions=0,
            next_review_at=next_review_at,
        )
        self.session.add(item)
        await self.session.flush()
        return item

    async def _record(self, item, *, rating, at):
        rec = ReviewRecord(
            review_item_id=item.id,
            rating=rating,
            reviewed_at=at,
            previous_interval_days=0,
            next_interval_days=1,
            previous_next_review_at=at - timedelta(days=1),
            next_review_at=at + timedelta(days=1),
        )
        self.session.add(rec)
        await self.session.flush()
        return rec

    async def _analytics(self):
        return await kp_analytics_service.get_knowledge_point_analytics(
            self.session, now=NOW
        )

    async def _item(self, kp_id):
        rows = await self._analytics()
        found = [r for r in rows if r.knowledge_point_id == kp_id]
        self.assertEqual(len(found), 1, f"expected exactly one row for kp {kp_id}")
        return found[0]

    async def _statement_count(self):
        seen: list[str] = []

        def _cap(conn, cursor, statement, parameters, context, executemany):
            seen.append(statement)

        event.listen(engine.sync_engine, "before_cursor_execute", _cap)
        try:
            await self._analytics()
        finally:
            event.remove(engine.sync_engine, "before_cursor_execute", _cap)
        return seen

    async def test_a1_metrics_for_correct_and_wrong_practice_attempts(self):
        subject = await self._subject()
        kp = await self._kp(subject)
        question = await self._question(subject, [kp.id])
        for correct in (True, True, True, False, False):
            await self._attempt(question, correct=correct)

        item = await self._item(kp.id)
        self.assertEqual(item.attempt_count, 5)
        self.assertEqual(item.wrong_count, 2)
        self.assertAlmostEqual(item.accuracy, 3 / 5)
        self.assertAlmostEqual(item.wrong_rate, 2 / 5)
        self.assertIsInstance(item.accuracy, float)
        self.assertIsInstance(item.wrong_rate, float)

    async def test_a2_review_and_editor_context_attempts_do_not_inflate_practice(self):
        subject = await self._subject()
        kp = await self._kp(subject)
        question = await self._question(subject, [kp.id])
        await self._attempt(question, correct=True)
        await self._attempt(question, correct=False)
        await self._attempt(question, correct=False, context="review")
        await self._attempt(question, correct=False, context="editor_check")

        item = await self._item(kp.id)
        self.assertEqual(item.attempt_count, 2)
        self.assertEqual(item.wrong_count, 1)
        self.assertAlmostEqual(item.wrong_rate, 1 / 2)

    async def test_a3_zero_graded_is_zero_float_not_none_or_nan(self):
        subject = await self._subject()
        kp_no_attempts = await self._kp(subject)
        await self._question(subject, [kp_no_attempts.id])

        kp_only_review = await self._kp(subject)
        review_only_question = await self._question(subject, [kp_only_review.id])
        await self._attempt(review_only_question, correct=False, context="review")

        for kp_id in (kp_no_attempts.id, kp_only_review.id):
            item = await self._item(kp_id)
            self.assertEqual(item.attempt_count, 0)
            self.assertEqual(item.wrong_count, 0)
            self.assertEqual(item.accuracy, 0.0)
            self.assertEqual(item.wrong_rate, 0.0)
            self.assertIsInstance(item.accuracy, float)
            self.assertIsInstance(item.wrong_rate, float)
            self.assertFalse(item.accuracy != item.accuracy)
            self.assertFalse(item.wrong_rate != item.wrong_rate)

    async def test_a4_due_count_state_and_time_boundary_and_no_double_count(self):
        subject = await self._subject()
        kp = await self._kp(subject)
        question = await self._question(subject, [kp.id])

        due_mistake = await self._mistake(subject, question, kp.id)
        due_item = await self._review_item(
            due_mistake, state="active", next_review_at=NOW - timedelta(minutes=1)
        )
        await self._record(due_item, rating=4, at=NOW - timedelta(hours=3))
        await self._record(due_item, rating=4, at=NOW - timedelta(hours=2))
        await self._record(due_item, rating=4, at=NOW - timedelta(hours=1))

        boundary_mistake = await self._mistake(subject, question, kp.id)
        await self._review_item(
            boundary_mistake, state="active", next_review_at=NOW
        )

        future_mistake = await self._mistake(subject, question, kp.id)
        await self._review_item(
            future_mistake, state="active", next_review_at=NOW + timedelta(seconds=1)
        )

        mastered_mistake = await self._mistake(subject, question, kp.id)
        await self._review_item(
            mastered_mistake, state="mastered", next_review_at=NOW - timedelta(days=1)
        )

        item = await self._item(kp.id)
        self.assertEqual(item.due_count, 2)
        self.assertEqual(item.review_count, 3)

    async def test_a5_lapse_count_is_lifetime_and_boundary_at_rating_2(self):
        subject = await self._subject()
        kp = await self._kp(subject)
        question = await self._question(subject, [kp.id])
        mistake = await self._mistake(subject, question, kp.id)
        item_row = await self._review_item(
            mistake, state="active", next_review_at=NOW + timedelta(days=10)
        )

        ratings = [0, 1, 2, 3, 4, 5, 2, 3]
        for idx, rating in enumerate(ratings):
            await self._record(item_row, rating=rating, at=NOW - timedelta(hours=idx + 1))

        row = await self._item(kp.id)
        self.assertEqual(row.review_count, len(ratings))
        self.assertEqual(row.lapse_count, 4)
        self.assertEqual(row.due_count, 0)

    async def test_a6_multi_kp_question_counts_full_observation_per_kp(self):
        subject = await self._subject()
        kp_a = await self._kp(subject)
        kp_b = await self._kp(subject)
        question = await self._question(subject, [kp_a.id, kp_b.id])
        await self._attempt(question, correct=False)
        await self._attempt(question, correct=True)
        await self._attempt(question, correct=False)

        item_a = await self._item(kp_a.id)
        item_b = await self._item(kp_b.id)
        for item in (item_a, item_b):
            self.assertEqual(item.attempt_count, 3)
            self.assertEqual(item.wrong_count, 2)
            self.assertAlmostEqual(item.wrong_rate, 2 / 3)

    async def test_a7_archived_question_mistake_and_inactive_kp_excluded(self):
        subject = await self._subject()
        active_kp = await self._kp(subject)

        archived_question = await self._question(
            subject, [active_kp.id], status="archived"
        )
        await self._attempt(archived_question, correct=False)

        active_question = await self._question(subject, [active_kp.id])
        archived_mistake = await self._mistake(
            subject, active_question, active_kp.id, status="archived"
        )
        await self._review_item(
            archived_mistake, state="active", next_review_at=NOW - timedelta(days=1)
        )

        inactive_kp = await self._kp(subject, status="archived")
        inactive_question = await self._question(subject, [inactive_kp.id])
        await self._attempt(inactive_question, correct=False)

        active_item = await self._item(active_kp.id)
        self.assertEqual(active_item.attempt_count, 0)
        self.assertEqual(active_item.wrong_count, 0)
        self.assertEqual(active_item.review_count, 0)
        self.assertEqual(active_item.due_count, 0)
        self.assertEqual(active_item.lapse_count, 0)

        all_ids = {row.knowledge_point_id for row in await self._analytics()}
        self.assertNotIn(inactive_kp.id, all_ids)

    async def test_a8_tie_break_is_ascending_kp_id_and_deterministic(self):
        subject = await self._subject()
        kps = [await self._kp(subject) for _ in range(4)]
        shared_question = await self._question(subject, [kp.id for kp in kps])
        await self._attempt(shared_question, correct=True)
        await self._attempt(shared_question, correct=False)

        rows = [
            row
            for row in await self._analytics()
            if row.knowledge_point_id in {kp.id for kp in kps}
        ]
        ids = [row.knowledge_point_id for row in rows]
        expected = sorted(kp.id for kp in kps)
        self.assertEqual(ids, expected)

        second_pass = [
            row.knowledge_point_id
            for row in await self._analytics()
            if row.knowledge_point_id in {kp.id for kp in kps}
        ]
        self.assertEqual(second_pass, ids)

    async def test_b_statement_count_constant_for_n_and_2n_active_kps(self):
        subject = await self._subject()

        async def build(count):
            for _ in range(count):
                kp = await self._kp(subject)
                await self._question(subject, [kp.id])
            await self.session.flush()

        counts = {}
        for n in (1, 3, 6, 12):
            before = await self.session.scalar(
                select(func.count()).select_from(KnowledgePoint)
            )
            await build(n)
            await self.session.flush()
            after = await self.session.scalar(
                select(func.count()).select_from(KnowledgePoint)
            )
            self.assertEqual(after - before, n)
            counts[n] = len(await self._statement_count())

        self.assertEqual(counts[1], counts[3])
        self.assertEqual(counts[3], counts[6])
        self.assertEqual(counts[6], counts[12])
        self.assertLessEqual(max(counts.values()), 2)

        print(
            "PR-10 verify N+1 statement counts (active KPs -> analytics statements): "
            f"{counts}"
        )
        self.verify_counts = counts
