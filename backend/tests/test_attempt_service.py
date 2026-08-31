import unittest

from sqlalchemy import func, select

from app.database import async_session, engine
from app.models.mistake import Mistake, MistakeDraft
from app.models.question import DraftItem
from app.schemas.question import QuestionCreate
from app.schemas.taxonomy import SubjectCreate
from app.services import attempt_service, question_service
from app.services.taxonomy_service import create_subject


class AttemptServiceTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.session = async_session()
        self.addAsyncCleanup(engine.dispose)
        self.addAsyncCleanup(self.session.close)
        self.addAsyncCleanup(self.session.rollback)
        await self.session.begin()
        self.subject = await create_subject(self.session, SubjectCreate(name="I3 Attempt Subject"))
        self.question = await question_service.create_question(
            self.session,
            QuestionCreate(
                subject_id=self.subject.id,
                stem_md="I3 test question",
                question_type="short_answer",
                answer_data={"kind": "short_answer", "value": "correct"},
            ),
        )

    async def _count(self, model):
        return await self.session.scalar(select(func.count()).select_from(model))

    async def test_incorrect_attempt_creates_one_pending_mistake_draft(self):
        drafts_before = await self._count(MistakeDraft)
        items_before = await self._count(DraftItem)
        mistakes_before = await self._count(Mistake)
        attempt = await attempt_service.submit_attempt(
            self.session, self.question.id, submitted_answer="wrong"
        )
        self.assertFalse(attempt.is_correct)
        self.assertIsNotNone(attempt.mistake_draft_item_id)
        self.assertEqual(await self._count(MistakeDraft), drafts_before + 1)
        self.assertEqual(await self._count(DraftItem), items_before + 1)
        self.assertEqual(await self._count(Mistake), mistakes_before)

        repeated = await attempt_service.create_mistake_draft_for_attempt(self.session, attempt.id)
        self.assertEqual(repeated.item.id, attempt.mistake_draft_item_id)
        self.assertEqual(await self._count(MistakeDraft), drafts_before + 1)

    async def test_correct_attempt_never_creates_mistake_draft(self):
        drafts_before = await self._count(MistakeDraft)
        attempt = await attempt_service.submit_attempt(
            self.session, self.question.id, submitted_answer="correct"
        )
        self.assertTrue(attempt.is_correct)
        self.assertIsNone(attempt.mistake_draft_item_id)
        self.assertEqual(await self._count(MistakeDraft), drafts_before)
