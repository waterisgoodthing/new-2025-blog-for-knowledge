import unittest

from sqlalchemy import func, select

from app.database import async_session, engine
from app.models.mistake import Mistake, MistakeDraft
from app.models.question import DraftItem
from app.models.review_item import ReviewItem
from app.schemas.question import QuestionCreate
from app.schemas.taxonomy import KnowledgePointCreate, SubjectCreate
from app.services import attempt_service, mistake_service, question_service
from app.services.taxonomy_service import create_knowledge_point, create_subject


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

    async def test_auto_draft_snapshots_question_knowledge_points_into_mistake(self):
        kp_a = await create_knowledge_point(
            self.session,
            KnowledgePointCreate(subject_id=self.subject.id, name="I3 KP A"),
        )
        kp_b = await create_knowledge_point(
            self.session,
            KnowledgePointCreate(subject_id=self.subject.id, name="I3 KP B"),
        )
        question = await question_service.create_question(
            self.session,
            QuestionCreate(
                subject_id=self.subject.id,
                stem_md="I3 KP inheritance question",
                question_type="short_answer",
                answer_data={"kind": "short_answer", "value": "right"},
                knowledge_point_links=[
                    {"knowledge_point_id": kp_a.id},
                    {"knowledge_point_id": kp_b.id},
                ],
            ),
        )
        attempt = await attempt_service.submit_attempt(
            self.session, question.id, submitted_answer="wrong"
        )
        draft = await mistake_service.get_mistake_draft(
            self.session, attempt.mistake_draft_item_id
        )
        self.assertEqual(draft.knowledge_point_ids, sorted([kp_a.id, kp_b.id]))

        converted = await mistake_service.convert_mistake_draft(
            self.session, draft.item.id, draft.item.version
        )
        self.assertEqual(converted.knowledge_point_ids, sorted([kp_a.id, kp_b.id]))

    async def test_kp_chain_from_attempt_to_review_analytics(self):
        from app.services.kp_analytics_service import get_knowledge_point_analytics
        from app.services.reanswer_service import submit_reanswer_attempt
        from app.services.review_item_service import submit_review

        kp_a = await create_knowledge_point(
            self.session,
            KnowledgePointCreate(subject_id=self.subject.id, name="Chain KP A"),
        )
        kp_b = await create_knowledge_point(
            self.session,
            KnowledgePointCreate(subject_id=self.subject.id, name="Chain KP B"),
        )
        question = await question_service.create_question(
            self.session,
            QuestionCreate(
                subject_id=self.subject.id,
                stem_md="Chain multiple choice",
                question_type="multiple_choice",
                options=[
                    {"key": "A", "text": "a"},
                    {"key": "B", "text": "b"},
                    {"key": "C", "text": "c"},
                ],
                answer_data={"kind": "multiple_choice", "value": ["A", "C"]},
                knowledge_point_links=[
                    {"knowledge_point_id": kp_a.id},
                    {"knowledge_point_id": kp_b.id},
                ],
            ),
        )
        # wrong practice attempt -> draft inherits both question KPs
        attempt = await attempt_service.submit_attempt(
            self.session, question.id, submitted_answer="A,B"
        )
        draft = await mistake_service.get_mistake_draft(
            self.session, attempt.mistake_draft_item_id
        )
        self.assertEqual(draft.knowledge_point_ids, sorted([kp_a.id, kp_b.id]))

        mistake = await mistake_service.convert_mistake_draft(
            self.session, draft.item.id, draft.item.version
        )
        self.assertEqual(mistake.knowledge_point_ids, sorted([kp_a.id, kp_b.id]))

        item = await self.session.get(ReviewItem, mistake.review_item_id)
        # review-context re-answer must NOT count as a practice attempt
        await submit_reanswer_attempt(
            self.session, question.id, submitted_answer="A,C"
        )
        updated, record = await submit_review(
            self.session,
            item.id,
            rating=0,
            expected_next_review_at=item.next_review_at,
        )
        self.assertEqual(record.rating, 0)

        analytics = {
            row.knowledge_point_id: row
            for row in await get_knowledge_point_analytics(self.session)
        }
        for kp_id in (kp_a.id, kp_b.id):
            row = analytics[kp_id]
            self.assertEqual(row.attempt_count, 1)  # review context excluded
            self.assertEqual(row.wrong_count, 1)
            self.assertEqual(row.review_count, 1)
            self.assertEqual(row.lapse_count, 1)  # rating 0 counts as a lapse
        # scheduler advanced from the initial due time
        self.assertGreater(updated.next_review_at, item.created_at)
