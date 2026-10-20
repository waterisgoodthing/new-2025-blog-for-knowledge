"""PR-13 daily-practice service tests (W3-D05 fixture matrix + filters).

Run against a migrated scratch database via the Week 3 guard:

    python3 scripts/week3-scratch-guard.py run --db-name astra_week3_pr13 \
        -- backend/.venv/bin/python -m pytest tests/test_pr13_practice_service.py -q
"""

from __future__ import annotations

import unittest
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select

from app.database import async_session, engine
from app.models.attempt import Attempt
from app.models.mistake import Mistake
from app.models.question import DraftItem, Question
from app.models.review_item import ReviewItem
from app.schemas.question import QuestionDraftCreate
from app.schemas.taxonomy import KnowledgePointCreate, SubjectCreate
from app.services import practice_service
from app.services.draft_service import convert_question_draft, create_question_draft
from app.services.taxonomy_service import create_knowledge_point, create_subject


class PracticeServiceTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await engine.dispose(close=False)
        self.session = async_session()
        self.addAsyncCleanup(engine.dispose)
        self.addAsyncCleanup(self.session.close)
        self.addAsyncCleanup(self.session.rollback)
        await self.session.begin()
        self.now = datetime(2026, 6, 1, 12, 0, tzinfo=timezone.utc)

    async def _subject(self):
        return await create_subject(
            self.session,
            SubjectCreate(name=f"PR13 Subject {uuid.uuid4().hex[:8]}"),
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

    async def _question(self, subject, kp_ids=(), *, status: str = "active"):
        draft = await create_question_draft(
            self.session,
            QuestionDraftCreate(
                subject_id=subject.id,
                question_text=f"PR13 question {uuid.uuid4().hex[:8]}?",
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

    async def _attempt(
        self,
        question,
        *,
        is_correct: bool,
        submitted_at: datetime,
        context_type: str = "practice",
    ):
        attempt = Attempt(
            question_id=question.id,
            submitted_answer="x",
            is_correct=is_correct,
            context_type=context_type,
            submitted_at=submitted_at,
        )
        self.session.add(attempt)
        await self.session.flush()
        return attempt

    async def _mistake(self, subject, question):
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
            question_text="PR13 mistake",
            reason_category="concept",
            status="active",
        )
        self.session.add(mistake)
        await self.session.flush()
        return mistake

    async def _review_item(self, mistake, *, state: str):
        review_item = ReviewItem(
            target_type="mistake",
            target_id=str(mistake.id),
            mistake_id=mistake.id,
            state=state,
            interval_days=0,
            repetitions=0,
            next_review_at=self.now,
        )
        self.session.add(review_item)
        await self.session.flush()
        return review_item

    async def _practice(self):
        return await practice_service.get_daily_practice(self.session, now=self.now)

    async def _attempt_count(self) -> int:
        return int(
            (
                await self.session.execute(select(func.count()).select_from(Attempt))
            ).scalar_one()
        )

    async def test_target_count_matrix_zero_to_many(self):
        self.assertEqual(practice_service.practice_target_count(0), 0)
        self.assertEqual(practice_service.practice_target_count(1), 1)
        self.assertEqual(practice_service.practice_target_count(2), 2)
        self.assertEqual(practice_service.practice_target_count(3), 3)
        self.assertEqual(practice_service.practice_target_count(11), 3)

    async def test_zero_candidates_returns_honest_empty(self):
        result = await self._practice()
        self.assertEqual(result.items, [])
        self.assertEqual(result.empty_metadata.reason, practice_service.EMPTY_REASON_NO_CANDIDATES)
        self.assertEqual(result.empty_metadata.raw_candidate_count, 0)
        self.assertEqual(result.empty_metadata.eligible_candidate_count, 0)
        self.assertEqual(result.empty_metadata.returned_count, 0)
        self.assertEqual(result.empty_metadata.window_hours, 7 * 24)

    async def test_single_candidate_returns_one(self):
        subject = await self._subject()
        kp = await self._kp(subject)
        question = await self._question(subject, [kp.id])
        result = await self._practice()
        self.assertEqual(len(result.items), 1)
        self.assertEqual(result.items[0].question_id, str(question.id))
        self.assertEqual(result.items[0].knowledge_point_id, kp.id)
        self.assertEqual(result.empty_metadata.target_count, 1)
        self.assertEqual(result.empty_metadata.reason, practice_service.EMPTY_REASON_RETURNED)

    async def test_two_candidates_return_two(self):
        subject = await self._subject()
        kp = await self._kp(subject)
        await self._question(subject, [kp.id])
        await self._question(subject, [kp.id])
        result = await self._practice()
        self.assertEqual(len(result.items), 2)
        self.assertEqual(result.empty_metadata.target_count, 2)

    async def test_three_candidates_return_three(self):
        subject = await self._subject()
        kp = await self._kp(subject)
        for _ in range(3):
            await self._question(subject, [kp.id])
        result = await self._practice()
        self.assertEqual(len(result.items), 3)
        self.assertEqual(result.empty_metadata.target_count, 3)

    async def test_more_than_ten_candidates_returns_target_three_deterministically(self):
        subject = await self._subject()
        kp = await self._kp(subject)
        for _ in range(12):
            await self._question(subject, [kp.id])
        first = await self._practice()
        second = await self._practice()
        self.assertEqual(len(first.items), 3)
        self.assertEqual(
            [item.question_id for item in first.items],
            [item.question_id for item in second.items],
        )
        self.assertEqual(first.empty_metadata.eligible_candidate_count, 12)
        self.assertEqual(first.empty_metadata.target_count, 3)
        self.assertEqual(
            [item.question_id for item in first.items],
            sorted(item.question_id for item in first.items),
        )

    async def test_weak_knowledge_point_priority_consumes_pr10_order(self):
        subject = await self._subject()
        weak_kp = await self._kp(subject)
        calm_kp = await self._kp(subject)
        weak_question = await self._question(subject, [weak_kp.id])
        calm_question = await self._question(subject, [calm_kp.id])
        await self._attempt(
            weak_question,
            is_correct=False,
            submitted_at=self.now - timedelta(days=8),
        )

        result = await self._practice()
        self.assertEqual(
            [item.knowledge_point_id for item in result.items],
            [weak_kp.id, calm_kp.id],
        )
        self.assertEqual(
            result.items[0].selection_reason,
            practice_service.SELECTION_REASON_WRONG_RATE,
        )
        self.assertEqual(
            result.items[1].selection_reason,
            practice_service.SELECTION_REASON_STABLE_FALLBACK,
        )
        self.assertNotEqual(result.items[0].question_id, str(calm_question.id))
        self.assertEqual(result.items[1].question_id, str(calm_question.id))

    async def test_stable_tie_falls_back_to_kp_then_question_id(self):
        subject = await self._subject()
        first_kp = await self._kp(subject)
        second_kp = await self._kp(subject)
        first_question = await self._question(subject, [first_kp.id])
        second_question = await self._question(subject, [second_kp.id])

        result = await self._practice()
        ordered = [
            (item.knowledge_point_id, item.question_id) for item in result.items
        ]
        self.assertEqual(
            ordered,
            [
                (first_kp.id, str(first_question.id)),
                (second_kp.id, str(second_question.id)),
            ],
        )
        self.assertLess(first_kp.id, second_kp.id)

    async def test_archived_question_excluded(self):
        subject = await self._subject()
        kp = await self._kp(subject)
        await self._question(subject, [kp.id], status="archived")
        result = await self._practice()
        self.assertEqual(result.items, [])
        self.assertEqual(result.empty_metadata.reason, practice_service.EMPTY_REASON_NO_CANDIDATES)

    async def test_recent_practice_attempt_excluded_but_review_context_is_not(self):
        subject = await self._subject()
        kp = await self._kp(subject)
        recent_question = await self._question(subject, [kp.id])
        review_context_question = await self._question(subject, [kp.id])
        await self._attempt(
            recent_question,
            is_correct=True,
            submitted_at=self.now - timedelta(hours=1),
        )
        await self._attempt(
            review_context_question,
            is_correct=True,
            submitted_at=self.now - timedelta(hours=1),
            context_type="review",
        )

        result = await self._practice()
        returned = {item.question_id for item in result.items}
        self.assertNotIn(str(recent_question.id), returned)
        self.assertIn(str(review_context_question.id), returned)
        self.assertEqual(result.empty_metadata.recent_attempt_excluded_count, 1)

    async def test_old_practice_attempt_outside_window_does_not_exclude(self):
        subject = await self._subject()
        kp = await self._kp(subject)
        question = await self._question(subject, [kp.id])
        await self._attempt(
            question,
            is_correct=True,
            submitted_at=self.now - timedelta(hours=7 * 24 + 1),
        )
        result = await self._practice()
        self.assertEqual([item.question_id for item in result.items], [str(question.id)])

    async def test_mastered_linked_mistake_excluded(self):
        subject = await self._subject()
        kp = await self._kp(subject)
        mastered_question = await self._question(subject, [kp.id])
        active_question = await self._question(subject, [kp.id])
        mastered_mistake = await self._mistake(subject, mastered_question)
        await self._review_item(mastered_mistake, state="mastered")
        active_mistake = await self._mistake(subject, active_question)
        await self._review_item(active_mistake, state="active")

        result = await self._practice()
        returned = {item.question_id for item in result.items}
        self.assertNotIn(str(mastered_question.id), returned)
        self.assertIn(str(active_question.id), returned)
        self.assertEqual(result.empty_metadata.mastered_excluded_count, 1)

    async def test_question_without_knowledge_point_is_not_a_candidate(self):
        subject = await self._subject()
        await self._question(subject, [])
        result = await self._practice()
        self.assertEqual(result.items, [])
        self.assertEqual(result.empty_metadata.reason, practice_service.EMPTY_REASON_NO_CANDIDATES)
        self.assertEqual(result.empty_metadata.raw_candidate_count, 0)

    async def test_all_candidates_excluded_reason(self):
        subject = await self._subject()
        kp = await self._kp(subject)
        question = await self._question(subject, [kp.id])
        await self._attempt(
            question,
            is_correct=False,
            submitted_at=self.now - timedelta(hours=1),
        )
        result = await self._practice()
        self.assertEqual(result.items, [])
        self.assertEqual(result.empty_metadata.reason, practice_service.EMPTY_REASON_ALL_EXCLUDED)
        self.assertEqual(result.empty_metadata.raw_candidate_count, 1)
        self.assertEqual(result.empty_metadata.eligible_candidate_count, 0)

    async def test_selection_is_read_only_and_creates_no_attempt(self):
        subject = await self._subject()
        kp = await self._kp(subject)
        await self._question(subject, [kp.id])
        before = await self._attempt_count()
        await self._practice()
        await self._practice()
        after = await self._attempt_count()
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
