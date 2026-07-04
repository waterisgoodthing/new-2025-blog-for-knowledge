import unittest

from pydantic import ValidationError

from app.database import async_session, engine
from app.schemas.taxonomy import (
    ChapterCreate,
    KnowledgePointCreate,
    SubjectCreate,
    SubjectUpdate,
)
from app.services.taxonomy_service import (
    TaxonomyConflict,
    TaxonomyValidationError,
    create_chapter,
    create_knowledge_point,
    create_subject,
    delete_chapter,
    delete_subject,
    update_subject,
)


class SubjectSchemaTest(unittest.TestCase):
    def test_subject_names_are_trimmed_and_blank_names_are_rejected(self):
        created = SubjectCreate(name="  计算机网络  ")
        updated = SubjectUpdate(name="  数据结构  ")

        self.assertEqual(created.name, "计算机网络")
        self.assertEqual(updated.name, "数据结构")

        with self.assertRaises(ValidationError):
            SubjectCreate(name="   ")
        with self.assertRaises(ValidationError):
            SubjectUpdate(name=None)


class TaxonomyServiceTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.session = async_session()
        await self.session.begin()

    async def asyncTearDown(self):
        await self.session.rollback()
        await self.session.close()
        await engine.dispose()

    async def test_subject_update_and_duplicate_conflict(self):
        first = await create_subject(
            self.session,
            SubjectCreate(name="Batch2 Subject A"),
        )
        second = await create_subject(
            self.session,
            SubjectCreate(name="Batch2 Subject B"),
        )

        updated = await update_subject(
            self.session,
            first.id,
            SubjectUpdate(name="Batch2 Subject Updated"),
        )
        self.assertEqual(updated.name, "Batch2 Subject Updated")

        with self.assertRaises(TaxonomyConflict):
            await update_subject(
                self.session,
                second.id,
                SubjectUpdate(name="Batch2 Subject Updated"),
            )

    async def test_parent_records_with_dependencies_cannot_be_deleted(self):
        subject = await create_subject(
            self.session,
            SubjectCreate(name="Batch2 Parent Subject"),
        )
        chapter = await create_chapter(
            self.session,
            ChapterCreate(subject_id=subject.id, name="Batch2 Chapter"),
        )
        await create_knowledge_point(
            self.session,
            KnowledgePointCreate(
                subject_id=subject.id,
                chapter_id=chapter.id,
                name="Batch2 Knowledge Point",
            ),
        )

        with self.assertRaises(TaxonomyConflict):
            await delete_chapter(self.session, chapter.id)
        with self.assertRaises(TaxonomyConflict):
            await delete_subject(self.session, subject.id)

    async def test_knowledge_point_rejects_chapter_from_another_subject(self):
        first = await create_subject(
            self.session,
            SubjectCreate(name="Batch2 Subject One"),
        )
        second = await create_subject(
            self.session,
            SubjectCreate(name="Batch2 Subject Two"),
        )
        chapter = await create_chapter(
            self.session,
            ChapterCreate(subject_id=first.id, name="Batch2 Foreign Chapter"),
        )

        with self.assertRaises(TaxonomyValidationError):
            await create_knowledge_point(
                self.session,
                KnowledgePointCreate(
                    subject_id=second.id,
                    chapter_id=chapter.id,
                    name="Batch2 Invalid Knowledge Point",
                ),
            )
