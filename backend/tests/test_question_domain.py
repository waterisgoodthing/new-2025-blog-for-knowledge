import unittest

from pydantic import ValidationError

from app.database import async_session, engine
from app.schemas.taxonomy import KnowledgePointCreate, SubjectCreate
from app.schemas.question import QuestionCreate, QuestionSourceCreate
from app.services.question_service import QuestionValidationError, create_question
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
