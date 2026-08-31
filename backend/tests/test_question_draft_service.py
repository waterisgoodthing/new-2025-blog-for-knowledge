import unittest

from pydantic import ValidationError

from app.database import async_session, engine
from app.schemas.taxonomy import KnowledgePointCreate, SubjectCreate
from app.schemas.question import QuestionDraftCreate, QuestionDraftUpdate, QuestionUpdate
from app.services.draft_service import (
    DraftConflict,
    DraftValidationError,
    convert_question_draft,
    create_question_draft,
    reject_question_draft,
    update_question_draft,
)
from app.services.taxonomy_service import create_knowledge_point, create_subject
from app.services.question_service import (
    QuestionConflict,
    QuestionValidationError,
    archive_question,
    update_question,
)


class QuestionDraftSchemaTest(unittest.TestCase):
    def test_choice_questions_require_clean_non_empty_options(self):
        payload = QuestionDraftCreate(
            subject_id=1,
            question_text="  以下哪一项正确？  ",
            question_type="single_choice",
            options=[" 选项 A ", "选项 B"],
        )

        self.assertEqual(payload.question_text, "以下哪一项正确？")
        self.assertEqual(payload.options, ["选项 A", "选项 B"])

        with self.assertRaises(ValidationError):
            QuestionDraftCreate(
                subject_id=1,
                question_text="以下哪一项正确？",
                question_type="single_choice",
                options=[],
            )


class QuestionDraftServiceTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.session = async_session()
        self.addAsyncCleanup(engine.dispose)
        self.addAsyncCleanup(self.session.close)
        self.addAsyncCleanup(self.session.rollback)
        await self.session.begin()

    async def test_manual_draft_preserves_taxonomy_links(self):
        subject = await create_subject(
            self.session,
            SubjectCreate(name="Batch3 Draft Subject"),
        )
        point = await create_knowledge_point(
            self.session,
            KnowledgePointCreate(
                subject_id=subject.id,
                name="Batch3 Draft Knowledge",
            ),
        )

        draft = await create_question_draft(
            self.session,
            QuestionDraftCreate(
                subject_id=subject.id,
                question_text="Batch3 question?",
                question_type="short_answer",
                knowledge_point_ids=[point.id],
            ),
        )

        self.assertEqual(draft.item.status, "pending")
        self.assertEqual(draft.item.source_type, "manual")
        self.assertEqual(draft.knowledge_point_ids, [point.id])

    async def test_stale_draft_version_cannot_overwrite_newer_edit(self):
        subject = await create_subject(
            self.session,
            SubjectCreate(name="Batch3 Version Subject"),
        )
        draft = await create_question_draft(
            self.session,
            QuestionDraftCreate(
                subject_id=subject.id,
                question_text="Original question",
                question_type="short_answer",
            ),
        )

        updated = await update_question_draft(
            self.session,
            draft.item.id,
            QuestionDraftUpdate(version=1, question_text="Updated question"),
        )
        self.assertEqual(updated.question_text, "Updated question")
        self.assertEqual(updated.item.version, 2)

        with self.assertRaises(DraftConflict):
            await update_question_draft(
                self.session,
                draft.item.id,
                QuestionDraftUpdate(version=1, question_text="Stale edit"),
            )

    async def test_conversion_is_idempotent_and_preserves_manual_source(self):
        subject = await create_subject(
            self.session,
            SubjectCreate(name="Batch3 Convert Subject"),
        )
        draft = await create_question_draft(
            self.session,
            QuestionDraftCreate(
                subject_id=subject.id,
                question_text="Convert this question",
                question_type="short_answer",
            ),
        )

        first = await convert_question_draft(
            self.session,
            draft.item.id,
            version=1,
        )
        second = await convert_question_draft(
            self.session,
            draft.item.id,
            version=1,
        )

        self.assertEqual(first.id, second.id)
        self.assertEqual(first.sources[0].source_type, "manual")
        self.assertEqual(first.sources[0].source_ref, str(draft.item.id))

    async def test_rejected_draft_cannot_be_converted(self):
        subject = await create_subject(
            self.session,
            SubjectCreate(name="Batch3 Reject Subject"),
        )
        draft = await create_question_draft(
            self.session,
            QuestionDraftCreate(
                subject_id=subject.id,
                question_text="Reject this question",
                question_type="short_answer",
            ),
        )

        rejected = await reject_question_draft(
            self.session,
            draft.item.id,
            version=1,
        )
        self.assertEqual(rejected.item.status, "rejected")

        with self.assertRaises(DraftConflict):
            await convert_question_draft(
                self.session,
                draft.item.id,
                version=2,
            )

    async def test_question_update_uses_version_and_delete_archives(self):
        subject = await create_subject(
            self.session,
            SubjectCreate(name="Batch3 Question Subject"),
        )
        draft = await create_question_draft(
            self.session,
            QuestionDraftCreate(
                subject_id=subject.id,
                question_text="Formal question",
                question_type="short_answer",
            ),
        )
        question = await convert_question_draft(
            self.session,
            draft.item.id,
            version=1,
        )

        updated = await update_question(
            self.session,
            question.id,
            QuestionUpdate(version=1, explanation="Checked explanation"),
        )
        self.assertEqual(updated.explanation, "Checked explanation")
        self.assertEqual(updated.version, 2)

        with self.assertRaises(QuestionConflict):
            await update_question(
                self.session,
                question.id,
                QuestionUpdate(version=1, explanation="Stale explanation"),
            )

        archived = await archive_question(
            self.session,
            question.id,
            version=2,
        )
        self.assertEqual(archived.status, "archived")

    async def test_merged_question_type_validation_is_a_domain_error(self):
        subject = await create_subject(
            self.session,
            SubjectCreate(name="Batch3 Contract Subject"),
        )
        draft = await create_question_draft(
            self.session,
            QuestionDraftCreate(
                subject_id=subject.id,
                question_text="Contract question",
                question_type="short_answer",
            ),
        )

        with self.assertRaises(DraftValidationError):
            await update_question_draft(
                self.session,
                draft.item.id,
                QuestionDraftUpdate(version=1, question_type="single_choice"),
            )

        question = await convert_question_draft(
            self.session,
            draft.item.id,
            version=1,
        )
        with self.assertRaises(QuestionValidationError):
            await update_question(
                self.session,
                question.id,
                QuestionUpdate(version=1, question_type="single_choice"),
            )
