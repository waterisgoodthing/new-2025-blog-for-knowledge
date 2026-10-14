"""PR-11 dashboard summary service tests (canonical-only, deterministic).

Covers the Week 3 Dashboard delta contract:

- ``review_today_count`` equals canonical due active ReviewItems;
- ``practice_today_count`` consumes the PR-13 practice service (no copy);
- ``weak_top3`` consumes the PR-10 ordering authority;
- ``recently_mastered_4`` latest-record/current-state boundary rules;
- ``today_first_action`` deterministic review-first / practice-first / none;
- per-section action shape and partial-service degradation;
- no legacy Note query feeds any of the three answers.

Run against a migrated scratch database via the Week 3 guard:

    python3 scripts/week3-scratch-guard.py run --db-name astra_week3_pr11 \
        -- backend/.venv/bin/python -m pytest tests/test_pr11_dashboard_service.py -q
"""

from __future__ import annotations

import unittest
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from sqlalchemy import func, select, text
from sqlalchemy.exc import SQLAlchemyError

from app.database import async_session, engine
from app.models.attempt import Attempt
from app.models.mistake import Mistake
from app.models.question import DraftItem, Question
from app.models.review_item import ReviewItem, ReviewRecord
from app.schemas.question import QuestionDraftCreate
from app.schemas.taxonomy import KnowledgePointCreate, SubjectCreate
from app.services import dashboard_service, kp_analytics_service
from app.services.draft_service import convert_question_draft, create_question_draft
from app.services.taxonomy_service import create_knowledge_point, create_subject


# Earlier modules commit canonical rows into the shared pytest scratch DB, and
# the dashboard summary queries are global (no tenant/filter scope). Deactivating
# those rows inside the per-test transaction — always rolled back by the cleanup
# below — gives every test a deterministic active canonical state without a
# destructive TRUNCATE (which cascades into protected legacy append-only tables)
# and without weakening the empty / partial-failure assertions.
_CANONICAL_ISOLATION = (
    "DELETE FROM public.review_records",
    "UPDATE public.review_items SET state = 'paused' WHERE state <> 'paused'",
    "UPDATE public.mistakes SET status = 'archived' WHERE status <> 'archived'",
    "UPDATE public.questions SET status = 'archived' WHERE status <> 'archived'",
    "UPDATE public.knowledge_points SET status = 'archived' WHERE status <> 'archived'",
)


class DashboardPr11ServiceTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await engine.dispose(close=False)
        self.session = async_session()
        self.addAsyncCleanup(engine.dispose)
        self.addAsyncCleanup(self.session.close)
        self.addAsyncCleanup(self.session.rollback)
        await self.session.begin()
        for statement in _CANONICAL_ISOLATION:
            await self.session.execute(text(statement))
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.now = datetime(2026, 6, 1, 12, 0, tzinfo=timezone.utc)

    async def _subject(self):
        return await create_subject(
            self.session,
            SubjectCreate(name=f"PR11 Subject {uuid.uuid4().hex[:8]}"),
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
                question_text=f"PR11 question {uuid.uuid4().hex[:8]}?",
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
            question_text="PR11 mistake",
            reason_category="concept",
            status="active",
        )
        self.session.add(mistake)
        await self.session.flush()
        return mistake

    async def _review_item(
        self,
        mistake,
        *,
        state: str,
        item_id: uuid.UUID | None = None,
        next_review_at: datetime | None = None,
    ):
        review_item = ReviewItem(
            id=item_id or uuid.uuid4(),
            target_type="mistake",
            target_id=str(mistake.id),
            mistake_id=mistake.id,
            state=state,
            interval_days=0,
            repetitions=0,
            next_review_at=next_review_at or self.now,
        )
        self.session.add(review_item)
        await self.session.flush()
        return review_item

    async def _record(
        self,
        review_item,
        *,
        reviewed_at: datetime,
        previous_state: str = "active",
        new_state: str,
        rating: int = 4,
    ):
        record = ReviewRecord(
            review_item_id=review_item.id,
            rating=rating,
            reviewed_at=reviewed_at,
            previous_interval_days=0,
            next_interval_days=3,
            previous_next_review_at=self.now - timedelta(days=1),
            next_review_at=reviewed_at + timedelta(days=3),
            previous_state=previous_state,
            new_state=new_state,
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def _summary(self):
        return await dashboard_service.get_dashboard_summary(
            self.session,
            upload_root=Path(self.tmp.name),
            now=self.now,
        )

    async def _due_review_count(self) -> int:
        return int(
            (
                await self.session.execute(
                    select(func.count())
                    .select_from(ReviewItem)
                    .where(
                        ReviewItem.state == "active",
                        ReviewItem.next_review_at <= self.now,
                    )
                )
            ).scalar_one()
        )

    async def test_review_first_when_due_review_items_exist(self):
        subject = await self._subject()
        kp = await self._kp(subject)
        question = await self._question(subject, [kp.id])
        mistake = await self._mistake(subject, question)
        await self._review_item(mistake, state="active", next_review_at=self.now - timedelta(hours=1))

        summary = await self._summary()

        self.assertEqual(summary.review_today_count, 1)
        self.assertEqual(summary.review_today_count, await self._due_review_count())
        self.assertEqual(summary.counts.due_reviews, summary.review_today_count)
        self.assertTrue(summary.section_actions.review.available)
        self.assertEqual(
            summary.section_actions.review.reason,
            dashboard_service.REVIEW_REASON_DUE,
        )
        self.assertEqual(summary.today_first_action.kind, "review")
        self.assertEqual(summary.today_first_action.count, 1)
        self.assertEqual(
            summary.today_first_action.reason,
            dashboard_service.FIRST_ACTION_REASON_REVIEW_FIRST,
        )
        self.assertEqual(
            summary.today_first_action.target_route,
            dashboard_service.REVIEW_TARGET_ROUTE,
        )

    async def test_practice_first_when_no_due_review_but_candidates_exist(self):
        subject = await self._subject()
        kp = await self._kp(subject)
        await self._question(subject, [kp.id])

        summary = await self._summary()

        self.assertEqual(summary.review_today_count, 0)
        self.assertGreaterEqual(summary.practice_today_count, 1)
        self.assertEqual(summary.today_first_action.kind, "practice")
        self.assertEqual(
            summary.today_first_action.reason,
            dashboard_service.FIRST_ACTION_REASON_PRACTICE_FIRST,
        )
        self.assertEqual(
            summary.section_actions.review.reason,
            dashboard_service.REVIEW_REASON_NONE_DUE,
        )
        self.assertEqual(
            summary.section_actions.practice.reason,
            dashboard_service.PRACTICE_REASON_AVAILABLE,
        )

    async def test_all_empty_answers_are_honest(self):
        summary = await self._summary()

        self.assertEqual(summary.review_today_count, 0)
        self.assertEqual(summary.practice_today_count, 0)
        self.assertEqual(summary.weak_top3, [])
        self.assertEqual(summary.recently_mastered_4, [])
        self.assertEqual(summary.today_first_action.kind, "none")
        self.assertEqual(summary.today_first_action.count, 0)
        self.assertIsNone(summary.today_first_action.target_route)
        self.assertEqual(
            summary.today_first_action.reason,
            dashboard_service.FIRST_ACTION_REASON_NOTHING,
        )
        self.assertEqual(
            summary.section_actions.review.reason,
            dashboard_service.REVIEW_REASON_NONE_DUE,
        )
        self.assertEqual(
            summary.section_actions.practice.reason,
            dashboard_service.PRACTICE_REASON_NONE_ELIGIBLE,
        )
        self.assertEqual(summary.sections.learning, "empty")
        self.assertEqual(summary.sections.activity, "empty")

    async def test_partial_service_failure_degrades_without_raising(self):
        subject = await self._subject()
        kp = await self._kp(subject)
        question = await self._question(subject, [kp.id])
        mistake = await self._mistake(subject, question)
        await self._review_item(mistake, state="active", next_review_at=self.now - timedelta(hours=1))

        async def _boom(*_args, **_kwargs):
            raise SQLAlchemyError("practice offline")

        with patch.object(dashboard_service.practice_service, "get_daily_practice", _boom), patch.object(
            dashboard_service, "load_weak_top3", _boom
        ):
            summary = await self._summary()

        self.assertEqual(summary.review_today_count, 1)
        self.assertEqual(summary.practice_today_count, 0)
        self.assertFalse(summary.section_actions.practice.available)
        self.assertEqual(
            summary.section_actions.practice.reason,
            dashboard_service.PRACTICE_REASON_UNAVAILABLE,
        )
        self.assertEqual(summary.weak_top3, [])
        self.assertEqual(summary.today_first_action.kind, "review")

    async def test_weak_top3_consumes_pr10_ordering_authority(self):
        subject = await self._subject()
        weak_kp = await self._kp(subject)
        calm_kp = await self._kp(subject)
        weak_question = await self._question(subject, [weak_kp.id])
        calm_question = await self._question(subject, [calm_kp.id])
        await self._attempt(
            weak_question,
            is_correct=False,
            submitted_at=self.now - timedelta(days=2),
        )
        await self._attempt(
            calm_question,
            is_correct=True,
            submitted_at=self.now - timedelta(days=2),
        )

        summary = await self._summary()
        authority = await kp_analytics_service.get_knowledge_point_analytics(
            self.session, now=self.now
        )

        self.assertEqual(
            [item.knowledge_point_id for item in summary.weak_top3],
            [item.knowledge_point_id for item in authority[:3]],
        )
        self.assertEqual(summary.weak_top3[0].knowledge_point_id, weak_kp.id)
        self.assertEqual(summary.weak_top3[0].name, weak_kp.name)
        self.assertEqual(summary.weak_top3[0].wrong_rate, 1.0)

    async def test_recently_mastered_excludes_non_mastery_latest_and_non_mastered_current(self):
        subject = await self._subject()
        question = await self._question(subject)

        reverted = await self._review_item(
            await self._mistake(subject, question), state="mastered"
        )
        await self._record(reverted, reviewed_at=self.now - timedelta(days=2), new_state="mastered")
        await self._record(reverted, reviewed_at=self.now - timedelta(days=1), new_state="active")

        question_two = await self._question(subject)
        stale = await self._review_item(
            await self._mistake(subject, question_two), state="active"
        )
        await self._record(stale, reviewed_at=self.now - timedelta(hours=1), new_state="mastered")

        summary = await self._summary()

        returned = {item.review_item_id for item in summary.recently_mastered_4}
        self.assertNotIn(reverted.id, returned)
        self.assertNotIn(stale.id, returned)
        self.assertEqual(summary.recently_mastered_4, [])

    async def test_recently_mastered_orders_by_reviewed_at_then_item_id_and_limits_four(self):
        subject = await self._subject()
        entries = []
        for offset_hours in range(1, 6):
            question = await self._question(subject)
            mistake = await self._mistake(subject, question)
            item = await self._review_item(mistake, state="mastered")
            reviewed_at = self.now - timedelta(hours=offset_hours)
            await self._record(item, reviewed_at=reviewed_at, new_state="mastered")
            entries.append((item.id, reviewed_at))

        summary = await self._summary()

        self.assertEqual(len(summary.recently_mastered_4), 4)
        expected = [item_id for item_id, _ in sorted(entries, key=lambda pair: pair[1], reverse=True)][:4]
        self.assertEqual(
            [item.review_item_id for item in summary.recently_mastered_4],
            expected,
        )
        self.assertEqual(
            [item.mastered_at for item in summary.recently_mastered_4],
            sorted(
                (item.mastered_at for item in summary.recently_mastered_4),
                reverse=True,
            ),
        )

    async def test_recently_mastered_tie_breaks_by_item_id_ascending(self):
        subject = await self._subject()
        low_id = uuid.UUID(int=50)
        high_id = uuid.UUID(int=100)
        reviewed_at = self.now - timedelta(hours=1)
        for item_id in (high_id, low_id):
            question = await self._question(subject)
            mistake = await self._mistake(subject, question)
            item = await self._review_item(mistake, state="mastered", item_id=item_id)
            await self._record(item, reviewed_at=reviewed_at, new_state="mastered")

        summary = await self._summary()

        self.assertEqual(
            [item.review_item_id for item in summary.recently_mastered_4],
            [low_id, high_id],
        )

    async def test_dashboard_service_does_not_query_legacy_notes(self):
        source = Path(dashboard_service.__file__).read_text(encoding="utf-8")
        self.assertNotIn("models.note", source)
        self.assertNotIn("Note.", source)


if __name__ == "__main__":
    unittest.main()
