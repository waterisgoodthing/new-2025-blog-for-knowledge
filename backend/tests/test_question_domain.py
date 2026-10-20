import unittest

from pydantic import ValidationError
from sqlalchemy import select

from app.database import async_session, engine
from app.models.question import QuestionKnowledgePoint
from app.models.taxonomy import KnowledgePointLink
from app.schemas.taxonomy import KnowledgePointCreate, SubjectCreate
from app.schemas.question import (
    QuestionCreate,
    QuestionPatch,
    QuestionSourceCreate,
    QuestionUpdate,
)
from app.services.question_service import (
    QuestionValidationError,
    create_question,
    get_question,
    update_canonical_question,
    update_question,
)
from app.services.taxonomy_service import create_knowledge_point, create_subject


class QuestionDomainSchemaTest(unittest.TestCase):
    def test_direct_question_create_supports_structured_answer_and_default_difficulty(self):
        payload = QuestionCreate(
            subject_id=1,
            stem_md="已知函数 f(x)。",
            question_type="single_choice",
            options=[
                {"key": "A", "text": "有界"},
                {"key": "B", "text": "无界"},
            ],
            answer_data={"kind": "single_choice", "value": ["A"]},
        )

        self.assertEqual(payload.difficulty, "unspecified")
        self.assertEqual(payload.answer_data["value"], ["A"])

    def test_direct_question_create_rejects_answer_option_not_in_options(self):
        with self.assertRaises(ValidationError):
            QuestionCreate(
                subject_id=1,
                stem_md="选择正确选项。",
                question_type="single_choice",
                options=[{"key": "A", "text": "选项 A"}, {"key": "B", "text": "选项 B"}],
                answer_data={"kind": "single_choice", "value": ["C"]},
            )

    def test_url_source_requires_url(self):
        with self.assertRaises(ValidationError):
            QuestionSourceCreate(source_type="url", source_title="External")

    def test_source_ref_is_capped_at_orm_length(self):
        QuestionSourceCreate(
            source_type="manual", source_title="ok", source_ref="x" * 64
        )
        with self.assertRaises(ValidationError):
            QuestionSourceCreate(
                source_type="manual", source_title="ok", source_ref="x" * 65
            )


class QuestionDomainServiceTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.session = async_session()
        self.addAsyncCleanup(engine.dispose)
        self.addAsyncCleanup(self.session.close)
        self.addAsyncCleanup(self.session.rollback)
        await self.session.begin()

    async def test_direct_question_create_preserves_subject_and_sources(self):
        subject = await create_subject(
            self.session,
            SubjectCreate(name="Batch3 Direct Subject"),
        )
        point = await create_knowledge_point(
            self.session,
            KnowledgePointCreate(subject_id=subject.id, name="Direct Point"),
        )
        question = await create_question(
            self.session,
            QuestionCreate(
                subject_id=subject.id,
                stem_md="Direct question",
                question_type="short_answer",
                answer_data={"kind": "short_answer", "value": "答案"},
                knowledge_point_links=[{"knowledge_point_id": point.id, "role": "primary"}],
                sources=[{"source_type": "manual", "source_title": "手工录入"}],
            ),
        )

        self.assertEqual(question.stem_md, "Direct question")
        self.assertEqual(question.knowledge_point_ids, [point.id])
        self.assertEqual(question.sources[0].source_type, "manual")

    async def test_direct_question_rejects_cross_subject_knowledge_point(self):
        first = await create_subject(self.session, SubjectCreate(name="Batch3 First Subject"))
        second = await create_subject(self.session, SubjectCreate(name="Batch3 Second Subject"))
        point = await create_knowledge_point(
            self.session,
            KnowledgePointCreate(subject_id=second.id, name="Foreign Point"),
        )

        with self.assertRaises(QuestionValidationError):
            await create_question(
                self.session,
                QuestionCreate(
                    subject_id=first.id,
                    stem_md="Cross subject question",
                    question_type="short_answer",
                    answer_data={"kind": "short_answer", "value": "答案"},
                    knowledge_point_links=[{"knowledge_point_id": point.id}],
                ),
            )

    async def test_put_update_keeps_knowledge_point_representations_in_sync(self):
        subject = await create_subject(self.session, SubjectCreate(name="A04 Sync Subject"))
        first = await create_knowledge_point(
            self.session,
            KnowledgePointCreate(subject_id=subject.id, name="A04 Point A"),
        )
        second = await create_knowledge_point(
            self.session,
            KnowledgePointCreate(subject_id=subject.id, name="A04 Point B"),
        )
        created = await create_question(
            self.session,
            QuestionCreate(
                subject_id=subject.id,
                stem_md="A04 question",
                question_type="short_answer",
                answer_data={"kind": "short_answer", "value": "答案"},
                knowledge_point_links=[{"knowledge_point_id": first.id}],
            ),
        )

        await update_question(
            self.session,
            created.question.id,
            QuestionUpdate(
                version=created.question.version,
                knowledge_point_ids=[second.id],
            ),
        )

        reloaded = await get_question(self.session, created.question.id)
        self.assertEqual(reloaded.knowledge_point_ids, [second.id])

        dedicated = set(
            (
                await self.session.execute(
                    select(QuestionKnowledgePoint.knowledge_point_id).where(
                        QuestionKnowledgePoint.question_id == created.question.id
                    )
                )
            )
            .scalars()
            .all()
        )
        projection = set(
            (
                await self.session.execute(
                    select(KnowledgePointLink.knowledge_point_id).where(
                        KnowledgePointLink.target_type == "question",
                        KnowledgePointLink.target_id == str(created.question.id),
                    )
                )
            )
            .scalars()
            .all()
        )
        self.assertEqual(dedicated, {second.id})
        self.assertEqual(projection, {second.id})

    async def _kp_representations(self, question_id):
        dedicated = set(
            (
                await self.session.execute(
                    select(QuestionKnowledgePoint.knowledge_point_id).where(
                        QuestionKnowledgePoint.question_id == question_id
                    )
                )
            )
            .scalars()
            .all()
        )
        projection = set(
            (
                await self.session.execute(
                    select(KnowledgePointLink.knowledge_point_id).where(
                        KnowledgePointLink.target_type == "question",
                        KnowledgePointLink.target_id == str(question_id),
                    )
                )
            )
            .scalars()
            .all()
        )
        return dedicated, projection

    async def _seeded_question(self, name, first, second):
        subject = await create_subject(self.session, SubjectCreate(name=name))
        first_point = await create_knowledge_point(
            self.session, KnowledgePointCreate(subject_id=subject.id, name=first)
        )
        second_point = await create_knowledge_point(
            self.session, KnowledgePointCreate(subject_id=subject.id, name=second)
        )
        created = await create_question(
            self.session,
            QuestionCreate(
                subject_id=subject.id,
                stem_md="A04 question",
                question_type="short_answer",
                answer_data={"kind": "short_answer", "value": "答案"},
                knowledge_point_links=[{"knowledge_point_id": first_point.id}],
            ),
        )
        return first_point, second_point, created

    async def test_patch_update_keeps_knowledge_point_representations_in_sync(self):
        first, second, created = await self._seeded_question(
            "A04 Patch Subject", "A04P A", "A04P B"
        )
        await update_canonical_question(
            self.session,
            created.question.id,
            QuestionPatch(
                version=created.question.version,
                knowledge_point_links=[{"knowledge_point_id": second.id}],
            ),
        )
        reloaded = await get_question(self.session, created.question.id)
        dedicated, projection = await self._kp_representations(created.question.id)
        self.assertEqual(reloaded.knowledge_point_ids, [second.id])
        self.assertEqual(dedicated, {second.id})
        self.assertEqual(projection, {second.id})

    async def test_put_without_knowledge_points_preserves_existing_links(self):
        first, _second, created = await self._seeded_question(
            "A04 Preserve Subject", "A04R A", "A04R B"
        )
        await update_question(
            self.session,
            created.question.id,
            QuestionUpdate(version=created.question.version, title="renamed"),
        )
        reloaded = await get_question(self.session, created.question.id)
        dedicated, projection = await self._kp_representations(created.question.id)
        self.assertEqual(reloaded.knowledge_point_ids, [first.id])
        self.assertEqual(dedicated, {first.id})
        self.assertEqual(projection, {first.id})

    async def test_put_empty_knowledge_points_clears_both(self):
        _first, _second, created = await self._seeded_question(
            "A04 Clear Subject", "A04C A", "A04C B"
        )
        await update_question(
            self.session,
            created.question.id,
            QuestionUpdate(version=created.question.version, knowledge_point_ids=[]),
        )
        reloaded = await get_question(self.session, created.question.id)
        dedicated, projection = await self._kp_representations(created.question.id)
        self.assertEqual(reloaded.knowledge_point_ids, [])
        self.assertEqual(dedicated, set())
        self.assertEqual(projection, set())
