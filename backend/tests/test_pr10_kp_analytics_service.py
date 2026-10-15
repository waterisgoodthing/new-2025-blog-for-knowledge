"""PR-10 KP analytics service tests: W3-D05 fixture matrix + N+1 evidence.

Run against a migrated scratch database via the Week 3 guard:

    python3 scripts/week3-scratch-guard.py run --db-name astra_week3_pr10 \
        -- backend/.venv/bin/python -m pytest tests/test_pr10_kp_analytics_service.py -q
"""

from __future__ import annotations

import unittest
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import event

from app.database import async_session, engine
from app.models.attempt import Attempt
from app.models.mistake import Mistake
from app.models.question import DraftItem, Question
from app.models.review_item import ReviewItem, ReviewRecord
from app.models.taxonomy import KnowledgePointLink
from app.schemas.question import QuestionDraftCreate
from app.schemas.taxonomy import KnowledgePointCreate, SubjectCreate
from app.services import kp_analytics_service
from app.services.draft_service import convert_question_draft, create_question_draft
from app.services.taxonomy_service import create_knowledge_point, create_subject


class KPAnalyticsServiceTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await engine.dispose(close=False)
        self.session = async_session()
        self.addAsyncCleanup(engine.dispose)
        self.addAsyncCleanup(self.session.close)
        self.addAsyncCleanup(self.session.rollback)
        await self.session.begin()
        self.now = datetime(2026, 6, 1, 12, 0, tzinfo=timezone.utc)

    async def _subject(self) -> object:
        return await create_subject(
            self.session,
            SubjectCreate(name=f"PR10 Subject {uuid.uuid4().hex[:8]}"),
        )

    async def _kp(self, subject, *, status: str = "active"):
        return await create_knowledge_point(
            self.session,
            KnowledgePointCreate(
                subject_id=subject.id,
                name=f"KP {uuid.uuid4().hex[:8]}",
                status=status,
            ),
        )

    async def _question(self, subject, kp_ids, *, status: str = "active"):
        draft = await create_question_draft(
            self.session,
            QuestionDraftCreate(
                subject_id=subject.id,
                question_text=f"PR10 question {uuid.uuid4().hex[:8]}?",
                question_type="short_answer",
                correct_answer="Answer",
                knowledge_point_ids=list(kp_ids),
            ),
        )
        question = await convert_question_draft(self.session, draft.item.id, version=1)
        if status != "active":
            stored = await self.session.get(Question, question.id)
            stored.status = status
            await self.session.flush()
        return question

    async def _attempt(self, question, *, is_correct: bool, context_type: str = "practice"):
        attempt = Attempt(
            question_id=question.id,
            submitted_answer="x",
            is_correct=is_correct,
            context_type=context_type,
        )
        self.session.add(attempt)
        await self.session.flush()
        return attempt

    async def _mistake(self, subject, question, kp_id, *, status: str = "active"):
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
            question_text="PR10 mistake",
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

    async def _review_item(self, mistake, *, state: str, next_review_at: datetime):
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

    async def _record(self, item, *, rating: int, at: datetime):
        record = ReviewRecord(
            review_item_id=item.id,
            rating=rating,
            reviewed_at=at,
            previous_interval_days=0,
            next_interval_days=1,
            previous_next_review_at=at - timedelta(days=1),
            next_review_at=at + timedelta(days=1),
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def _analytics(self):
        return await kp_analytics_service.get_knowledge_point_analytics(
            self.session, now=self.now
        )

    async def _by_id(self, *kp_ids):
        wanted = set(kp_ids)
        items = await self._analytics()
        return {item.knowledge_point_id: item for item in items if item.knowledge_point_id in wanted}

    async def _measured_statement_count(self) -> int:
        statements: list[str] = []

        def _capture(conn, cursor, statement, parameters, context, executemany):
            statements.append(statement)

        event.listen(engine.sync_engine, "before_cursor_execute", _capture)
        try:
            await self._analytics()
        finally:
            event.remove(engine.sync_engine, "before_cursor_execute", _capture)
        return len(statements)

    async def test_practice_attempt_metrics_exclude_review_and_editor_context(self):
        subject = await self._subject()
        kp = await self._kp(subject)
        question = await self._question(subject, [kp.id])
        await self._attempt(question, is_correct=True)
        await self._attempt(question, is_correct=True)
        await self._attempt(question, is_correct=False)
        await self._attempt(question, is_correct=False, context_type="review")
        await self._attempt(question, is_correct=False, context_type="editor_check")

        item = (await self._by_id(kp.id))[kp.id]
        self.assertEqual(item.attempt_count, 3)
        self.assertEqual(item.wrong_count, 1)
        self.assertAlmostEqual(item.accuracy, 2 / 3)
        self.assertAlmostEqual(item.wrong_rate, 1 / 3)

    async def test_zero_denominator_returns_zero_floats_not_none_or_nan(self):
        subject = await self._subject()
        kp = await self._kp(subject)
        await self._question(subject, [kp.id])

        item = (await self._by_id(kp.id))[kp.id]
        self.assertEqual(item.attempt_count, 0)
        self.assertEqual(item.wrong_count, 0)
        self.assertEqual(item.accuracy, 0.0)
        self.assertEqual(item.wrong_rate, 0.0)
        self.assertIsInstance(item.accuracy, float)
        self.assertIsInstance(item.wrong_rate, float)
        self.assertEqual(item.accuracy, item.accuracy)
        self.assertEqual(item.wrong_rate, item.wrong_rate)

    async def test_review_metrics_cover_due_future_and_mastered_items(self):
        subject = await self._subject()
        kp = await self._kp(subject)
        question = await self._question(subject, [kp.id])

        due_mistake = await self._mistake(subject, question, kp.id)
        due_item = await self._review_item(
            due_mistake, state="active", next_review_at=self.now - timedelta(hours=1)
        )
        await self._record(due_item, rating=1, at=self.now - timedelta(hours=2))
        await self._record(due_item, rating=2, at=self.now - timedelta(hours=1))
        await self._record(due_item, rating=4, at=self.now - timedelta(minutes=30))

        mastered_mistake = await self._mistake(subject, question, kp.id)
        mastered_item = await self._review_item(
            mastered_mistake, state="mastered", next_review_at=self.now - timedelta(hours=1)
        )
        await self._record(mastered_item, rating=5, at=self.now - timedelta(hours=3))

        future_mistake = await self._mistake(subject, question, kp.id)
        future_item = await self._review_item(
            future_mistake, state="active", next_review_at=self.now + timedelta(days=1)
        )
        await self._record(future_item, rating=3, at=self.now - timedelta(hours=4))

        item = (await self._by_id(kp.id))[kp.id]
        self.assertEqual(item.review_count, 5)
        self.assertEqual(item.lapse_count, 2)
        self.assertEqual(item.due_count, 1)

    async def test_archived_question_mistake_and_inactive_kp_are_excluded(self):
        subject = await self._subject()
        active_kp = await self._kp(subject)
        archived_question = await self._question(subject, [active_kp.id], status="archived")
        await self._attempt(archived_question, is_correct=False)

        active_question = await self._question(subject, [active_kp.id])
        archived_mistake = await self._mistake(
            subject, active_question, active_kp.id, status="archived"
        )
        await self._review_item(
            archived_mistake, state="active", next_review_at=self.now - timedelta(hours=1)
        )

        inactive_kp = await self._kp(subject, status="archived")
        inactive_question = await self._question(subject, [inactive_kp.id])
        await self._attempt(inactive_question, is_correct=False)

        result = await self._by_id(active_kp.id)
        item = result[active_kp.id]
        self.assertEqual(item.attempt_count, 0)
        self.assertEqual(item.wrong_count, 0)
        self.assertEqual(item.review_count, 0)
        self.assertEqual(item.due_count, 0)
        self.assertEqual(item.lapse_count, 0)

        all_items = await self._analytics()
        self.assertNotIn(inactive_kp.id, {entry.knowledge_point_id for entry in all_items})

    async def test_archived_question_active_mistake_review_path_is_excluded(self):
        subject = await self._subject()
        kp = await self._kp(subject)
        archived_question = await self._question(subject, [kp.id], status="archived")
        mistake = await self._mistake(subject, archived_question, kp.id)
        review_item = await self._review_item(
            mistake, state="active", next_review_at=self.now - timedelta(hours=1)
        )
        await self._record(review_item, rating=1, at=self.now - timedelta(hours=2))

        item = (await self._by_id(kp.id))[kp.id]
        self.assertEqual(item.attempt_count, 0)
        self.assertEqual(item.review_count, 0)
        self.assertEqual(item.due_count, 0)
        self.assertEqual(item.lapse_count, 0)

    async def test_multi_kp_question_counts_fully_for_each_kp_and_ties_sort_by_id(self):
        subject = await self._subject()
        first_kp = await self._kp(subject)
        second_kp = await self._kp(subject)
        question = await self._question(subject, [first_kp.id, second_kp.id])
        await self._attempt(question, is_correct=False)

        result = await self._analytics()
        by_id = {item.knowledge_point_id: item for item in result}
        self.assertEqual(by_id[first_kp.id].attempt_count, 1)
        self.assertEqual(by_id[second_kp.id].attempt_count, 1)
        self.assertEqual(by_id[first_kp.id].wrong_count, 1)
        self.assertEqual(by_id[second_kp.id].wrong_count, 1)

        relevant = [
            item.knowledge_point_id
            for item in result
            if item.knowledge_point_id in {first_kp.id, second_kp.id}
        ]
        self.assertLess(first_kp.id, second_kp.id)
        self.assertEqual(relevant, [first_kp.id, second_kp.id])

    async def test_query_count_does_not_grow_with_knowledge_point_count(self):
        subject = await self._subject()
        first_kp = await self._kp(subject)
        await self._question(subject, [first_kp.id])
        await self.session.flush()
        small_count = await self._measured_statement_count()

        for _ in range(24):
            extra_kp = await self._kp(subject)
            await self._question(subject, [extra_kp.id])
        await self.session.flush()
        large_count = await self._measured_statement_count()

        self.assertEqual(small_count, large_count)
        self.assertLessEqual(large_count, 2)
