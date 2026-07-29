import unittest
import uuid
from datetime import datetime, timedelta, timezone

from pydantic import ValidationError
from sqlalchemy import func, select

from app.database import async_session, engine
from app.models.mistake import Mistake
from app.models.review_item import ReviewItem, ReviewRecord
from app.schemas.mistake import MistakeDraftCreate
from app.schemas.question import QuestionDraftCreate
from app.schemas.taxonomy import SubjectCreate
from app.services.draft_service import convert_question_draft, create_question_draft
from app.services.mistake_service import (
    MistakeConflict,
    archive_mistake,
    convert_mistake_draft,
    create_mistake_draft,
)
from app.services.review_item_service import ReviewConflict, list_due_items, submit_review
from app.services.taxonomy_service import create_subject


class MistakeDraftSchemaTest(unittest.TestCase):
    def test_draft_requires_exactly_one_question_source(self):
        question_id = uuid.uuid4()
        payload = MistakeDraftCreate(
            question_id=question_id,
            my_answer="  我的答案  ",
        )
        self.assertEqual(payload.my_answer, "我的答案")

        with self.assertRaises(ValidationError):
            MistakeDraftCreate()

        with self.assertRaises(ValidationError):
            MistakeDraftCreate(
                question_id=question_id,
                question_draft_id=uuid.uuid4(),
            )


class MistakeReviewServiceTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # IsolatedAsyncioTestCase creates a new loop per test; do not reuse a
        # pooled asyncpg connection left by an earlier test module's loop.
        await engine.dispose(close=False)
        self.session = async_session()
        self.addAsyncCleanup(engine.dispose)
        self.addAsyncCleanup(self.session.close)
        self.addAsyncCleanup(self.session.rollback)
        await self.session.begin()

    async def _question(self, suffix: str):
        subject = await create_subject(
            self.session,
            SubjectCreate(name=f"Batch4 Subject {suffix}"),
        )
        draft = await create_question_draft(
            self.session,
            QuestionDraftCreate(
                subject_id=subject.id,
                question_text=f"Batch4 question {suffix}?",
                question_type="short_answer",
                correct_answer="Correct",
                explanation="Explanation",
            ),
        )
        return await convert_question_draft(self.session, draft.item.id, version=1)

    def _review_item_ids(self, due_items):
        return {item.id for item, _mistake in due_items}

    async def test_conversion_is_idempotent_and_creates_one_review_item(self):
        question = await self._question("conversion")
        draft = await create_mistake_draft(
            self.session,
            MistakeDraftCreate(
                question_id=question.id,
                my_answer="Wrong",
                mistake_reason="Missed a condition",
            ),
        )

        before = await self.session.scalar(select(func.count()).select_from(ReviewItem))
        first = await convert_mistake_draft(self.session, draft.item.id, version=1)
        second = await convert_mistake_draft(self.session, draft.item.id, version=1)
        after = await self.session.scalar(select(func.count()).select_from(ReviewItem))

        self.assertEqual(first.id, second.id)
        self.assertEqual(first.review_item_id, second.review_item_id)
        self.assertEqual(after, before + 1)
        self.assertEqual(first.visibility, "private")

    async def test_converted_draft_with_missing_target_is_a_conflict(self):
        question = await self._question("invalid-target")
        draft = await create_mistake_draft(
            self.session,
            MistakeDraftCreate(question_id=question.id),
        )
        first = await convert_mistake_draft(self.session, draft.item.id, version=1)
        item = await self.session.get(type(draft.item), draft.item.id)
        item.target_id = str(uuid.uuid4())
        await self.session.flush()

        with self.assertRaises(MistakeConflict):
            await convert_mistake_draft(self.session, draft.item.id, version=item.version)

        self.assertIsNotNone(first.id)

    async def test_question_draft_source_resolves_to_formal_question_id(self):
        subject = await create_subject(
            self.session,
            SubjectCreate(name="Batch4 Question Draft Source"),
        )
        question_draft = await create_question_draft(
            self.session,
            QuestionDraftCreate(
                subject_id=subject.id,
                question_text="Draft source question",
                question_type="short_answer",
            ),
        )
        mistake_draft = await create_mistake_draft(
            self.session,
            MistakeDraftCreate(question_draft_id=question_draft.id),
        )
        question = await convert_question_draft(
            self.session,
            question_draft.item.id,
            version=1,
        )
        mistake = await convert_mistake_draft(
            self.session,
            mistake_draft.item.id,
            version=1,
        )

        self.assertEqual(mistake.question_id, question.id)

    async def test_unconfirmed_draft_does_not_enter_review_queue(self):
        question = await self._question("pending")
        due_at = datetime.now(timezone.utc) + timedelta(minutes=1)
        queue_before = await list_due_items(
            self.session,
            now=due_at,
        )
        await create_mistake_draft(
            self.session,
            MistakeDraftCreate(question_id=question.id),
        )

        mistake_count = await self.session.scalar(
            select(func.count())
            .select_from(Mistake)
            .where(Mistake.question_id == question.id)
        )
        queue = await list_due_items(
            self.session,
            now=due_at,
        )

        self.assertEqual(mistake_count, 0)
        self.assertEqual(
            self._review_item_ids(queue),
            self._review_item_ids(queue_before),
        )

    async def test_review_uses_fixed_interval_and_rejects_stale_submission(self):
        question = await self._question("review")
        draft = await create_mistake_draft(
            self.session,
            MistakeDraftCreate(question_id=question.id),
        )
        mistake = await convert_mistake_draft(self.session, draft.item.id, version=1)
        item = await self.session.get(ReviewItem, mistake.review_item_id)
        expected = item.next_review_at
        mappings = {0: 1, 1: 1, 2: 1, 3: 3, 4: 7, 5: 14}
        previous_interval = 0
        for rating, days in mappings.items():
            now = expected + timedelta(minutes=1)
            updated, record = await submit_review(
                self.session,
                item.id,
                rating=rating,
                expected_next_review_at=expected,
                now=now,
            )
            self.assertEqual(updated.interval_days, days)
            self.assertEqual(updated.next_review_at, now + timedelta(days=days))
            self.assertEqual(record.previous_interval_days, previous_interval)
            self.assertEqual(record.next_interval_days, days)
            previous_interval = days
            expected = updated.next_review_at

        self.assertEqual(
            await self.session.scalar(
                select(func.count())
                .select_from(ReviewRecord)
                .where(ReviewRecord.review_item_id == item.id)
            ),
            6,
        )

        with self.assertRaises(ReviewConflict):
            await submit_review(
                self.session,
                item.id,
                rating=4,
                expected_next_review_at=item.created_at,
                now=now,
            )

    async def test_archiving_mistake_pauses_review_item(self):
        question = await self._question("archive")
        draft = await create_mistake_draft(
            self.session,
            MistakeDraftCreate(question_id=question.id),
        )
        mistake = await convert_mistake_draft(self.session, draft.item.id, version=1)

        archived = await archive_mistake(self.session, mistake.id, version=1)
        review_item = await self.session.get(ReviewItem, mistake.review_item_id)

        self.assertEqual(archived.status, "archived")
        self.assertEqual(review_item.state, "paused")

        repeated = await archive_mistake(self.session, mistake.id, version=1)
        self.assertEqual(repeated.id, archived.id)
