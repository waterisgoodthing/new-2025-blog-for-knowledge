"""PR-06 fixed_interval_v2 scheduling semantics — state machine tests.

Cases follow requirements.md R01 acceptance (Case A-D) and design.md D2:
    A: rating=1 lapse -> repetitions=0, state=active, interval shortened
    B: 4->4->5->4 success streak -> state=mastered
    C: mastered item absent from due queue (and submissions rejected)
    D: concurrent/stale submission -> optimistic concurrency still rejects
"""

import unittest
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.database import async_session, engine
from app.models.review_item import ReviewItem, ReviewRecord
from app.schemas.mistake import MistakeDraftCreate
from app.schemas.question import QuestionDraftCreate
from app.schemas.taxonomy import SubjectCreate
from app.services.draft_service import convert_question_draft, create_question_draft
from app.services.mistake_service import convert_mistake_draft, create_mistake_draft
from app.services.review_item_service import (
    ReviewConflict,
    list_due_items,
    submit_review,
)
from app.services.taxonomy_service import create_subject


class ReviewSchedulingV2Test(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # IsolatedAsyncioTestCase creates a new loop per test; do not reuse a
        # pooled asyncpg connection left by an earlier test module's loop.
        await engine.dispose(close=False)
        self.session = async_session()
        self.addAsyncCleanup(engine.dispose)
        self.addAsyncCleanup(self.session.close)
        self.addAsyncCleanup(self.session.rollback)
        await self.session.begin()

    async def _new_item(self, suffix: str) -> ReviewItem:
        subject = await create_subject(
            self.session,
            SubjectCreate(name=f"SchedV2 {suffix} {uuid.uuid4().hex[:8]}"),
        )
        draft = await create_question_draft(
            self.session,
            QuestionDraftCreate(
                subject_id=subject.id,
                question_text=f"Scheduling v2 question {suffix}?",
                question_type="short_answer",
                correct_answer="Correct",
                explanation="Explanation",
            ),
        )
        question = await convert_question_draft(self.session, draft.item.id, version=1)
        mistake_draft = await create_mistake_draft(
            self.session,
            MistakeDraftCreate(question_id=question.id),
        )
        mistake = await convert_mistake_draft(
            self.session, mistake_draft.item.id, version=1
        )
        item = await self.session.get(ReviewItem, mistake.review_item_id)
        await self.session.refresh(item)
        return item

    async def _submit(self, item: ReviewItem, rating: int, when: datetime):
        updated, record = await submit_review(
            self.session,
            item.id,
            rating=rating,
            expected_next_review_at=item.next_review_at,
            now=when,
        )
        await self.session.refresh(updated)
        return updated, record

    async def test_case_a_lapse_resets_repetitions_and_shortens_interval(self):
        item = await self._new_item("case-a")
        now = item.next_review_at + timedelta(minutes=1)

        # Build progress: two successes -> repetitions=2, interval 7d.
        for expected_days in (3, 7):
            item, _ = await self._submit(item, rating=4, when=now)
            now = item.next_review_at + timedelta(minutes=1)
            self.assertEqual(item.interval_days, expected_days)
        self.assertEqual(item.repetitions, 2)

        # Case A: rating=1 -> lapse. repetitions=0, state stays active,
        # interval shortened 7d -> 1d, last_rating recorded.
        item, record = await self._submit(item, rating=1, when=now)
        self.assertEqual(item.repetitions, 0)
        self.assertEqual(item.state, "active")
        self.assertEqual(item.interval_days, 1)
        self.assertEqual(item.last_rating, 1)
        self.assertEqual(record.previous_interval_days, 7)
        self.assertEqual(record.next_interval_days, 1)
        self.assertEqual(record.previous_state, "active")
        self.assertEqual(record.new_state, "active")

    async def test_case_b_success_streak_4454_reaches_mastered(self):
        item = await self._new_item("case-b")
        now = item.next_review_at + timedelta(minutes=1)

        expectations = [
            # (rating, repetitions_after, interval_days, new_state)
            (4, 1, 3, "active"),
            (4, 2, 7, "active"),
            (5, 3, 14, "active"),  # rating=5 climbs one step, never jumps
            (4, 4, 30, "mastered"),
        ]
        for rating, reps, days, new_state in expectations:
            item, record = await self._submit(item, rating=rating, when=now)
            now = item.next_review_at + timedelta(minutes=1)
            self.assertEqual(item.repetitions, reps, f"repetitions after {rating}")
            self.assertEqual(item.interval_days, days, f"interval after {rating}")
            self.assertEqual(item.state, new_state, f"state after {rating}")
            self.assertEqual(item.last_rating, rating)
            self.assertEqual(record.previous_state, "active")
            self.assertEqual(record.new_state, new_state)

        self.assertEqual(item.state, "mastered")
        # next_review_at was fixed at the 4th submit (submit time + 30d); `now`
        # has since advanced past it, so compare against now minus the 1min step
        # (no additional +30d: that would double-count the ladder interval).
        self.assertEqual(item.next_review_at, now - timedelta(minutes=1))

    async def test_case_c_mastered_item_leaves_due_queue_and_rejects_submit(self):
        item = await self._new_item("case-c")
        now = item.next_review_at + timedelta(minutes=1)
        for _ in range(4):
            item, _ = await self._submit(item, rating=4, when=now)
            now = item.next_review_at + timedelta(minutes=1)
        self.assertEqual(item.state, "mastered")

        due_at = item.next_review_at + timedelta(days=1)
        due_ids = {due_item.id for due_item, _mistake in await list_due_items(self.session, now=due_at)}
        self.assertNotIn(item.id, due_ids)

        with self.assertRaises(ReviewConflict):
            await submit_review(
                self.session,
                item.id,
                rating=4,
                expected_next_review_at=item.next_review_at,
                now=due_at,
            )

    async def test_case_d_stale_expected_next_review_at_still_rejected(self):
        item = await self._new_item("case-d")
        stale_expected = item.next_review_at
        now = stale_expected + timedelta(minutes=1)

        # A first submission succeeds and moves the item forward.
        item, _ = await self._submit(item, rating=4, when=now)

        # A racing submission that read the item before the first commit
        # still carries the stale snapshot and must be rejected.
        with self.assertRaises(ReviewConflict):
            await submit_review(
                self.session,
                item.id,
                rating=5,
                expected_next_review_at=stale_expected,
                now=now + timedelta(minutes=1),
            )

        # The item reflects exactly one successful submission.
        self.assertEqual(item.repetitions, 1)
        records = list(
            (
                await self.session.execute(
                    select(ReviewRecord).where(ReviewRecord.review_item_id == item.id)
                )
            ).scalars()
        )
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].rating, 4)

    async def test_rating_three_never_masters_and_ladder_caps_at_thirty_days(self):
        item = await self._new_item("rating3")
        now = item.next_review_at + timedelta(minutes=1)

        expected_intervals = [3, 7, 14, 30, 30]
        for days in expected_intervals:
            item, _ = await self._submit(item, rating=3, when=now)
            now = item.next_review_at + timedelta(minutes=1)
            self.assertEqual(item.interval_days, days)
            self.assertEqual(item.state, "active")

        self.assertEqual(item.repetitions, 5)

    async def test_rating_zero_is_the_hard_lapse_step(self):
        item = await self._new_item("rating0")
        now = item.next_review_at + timedelta(minutes=1)

        item, record = await self._submit(item, rating=0, when=now)
        self.assertEqual(item.repetitions, 0)
        self.assertEqual(item.interval_days, 1)
        self.assertEqual(item.state, "active")
        self.assertEqual(item.last_rating, 0)
        self.assertEqual(record.next_interval_days, 1)

    async def test_schedule_v2_rejects_out_of_range_ratings(self):
        from app.services.review_item_service import schedule_v2

        for bad in (-1, 6, 100):
            with self.assertRaises(ValueError):
                schedule_v2(bad, 0)

    async def test_rating_two_is_the_mild_lapse_step(self):
        item = await self._new_item("rating2")
        now = item.next_review_at + timedelta(minutes=1)

        item, record = await self._submit(item, rating=2, when=now)
        self.assertEqual(item.repetitions, 0)
        self.assertEqual(item.interval_days, 2)
        self.assertEqual(item.state, "active")
        self.assertEqual(item.last_rating, 2)
        self.assertEqual(record.next_interval_days, 2)

    async def test_records_carry_state_transitions_and_ratings(self):
        item = await self._new_item("records")
        now = item.next_review_at + timedelta(minutes=1)

        # rating=1 lapses (streak back to 0), so reaching mastered needs four
        # consecutive successes afterwards: 4,1,4,4,4,4 (streak 1,0,1,2,3,4).
        sequence = [(4, "active"), (1, "active"), (4, "active"), (4, "active"), (4, "active"), (4, "mastered")]
        for rating, _state in sequence:
            item, _ = await self._submit(item, rating=rating, when=now)
            now = item.next_review_at + timedelta(minutes=1)

        records = list(
            (
                await self.session.execute(
                    select(ReviewRecord)
                    .where(ReviewRecord.review_item_id == item.id)
                    .order_by(ReviewRecord.reviewed_at)
                )
            ).scalars()
        )
        self.assertEqual(
            [(record.rating, record.previous_state, record.new_state) for record in records],
            [
                (4, "active", "active"),
                (1, "active", "active"),
                (4, "active", "active"),
                (4, "active", "active"),
                (4, "active", "active"),
                (4, "active", "mastered"),
            ],
        )
        self.assertEqual(item.last_rating, 4)
