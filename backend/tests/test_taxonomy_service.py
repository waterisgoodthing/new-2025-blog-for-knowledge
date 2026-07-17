import unittest

from pydantic import ValidationError

from app.database import async_session, engine
from app.schemas.taxonomy import (
    KnowledgePointCreate,
    KnowledgePointUpdate,
    SubjectCreate,
    SubjectUpdate,
)
from app.services.taxonomy_service import (
    TaxonomyConflict,
    TaxonomyValidationError,
    archive_knowledge_point,
    create_knowledge_point,
    create_subject,
    get_subject_knowledge_tree,
    update_knowledge_point,
    update_subject,
)


class TaxonomySchemaTest(unittest.TestCase):
    def test_subject_names_are_trimmed_and_blank_names_are_rejected(self):
        created = SubjectCreate(name="  计算机网络  ")
        updated = SubjectUpdate(name="  数据结构  ")

        self.assertEqual(created.name, "计算机网络")
        self.assertEqual(updated.name, "数据结构")

        with self.assertRaises(ValidationError):
            SubjectCreate(name="   ")
        with self.assertRaises(ValidationError):
            SubjectUpdate(name=None)

    def test_status_values_are_limited(self):
        self.assertEqual(SubjectCreate(name="数学").status, "active")
        self.assertEqual(KnowledgePointCreate(subject_id=1, name="函数").status, "active")

        with self.assertRaises(ValidationError):
            SubjectCreate(name="数学", status="disabled")
        with self.assertRaises(ValidationError):
            KnowledgePointCreate(subject_id=1, name="函数", status="disabled")


class TaxonomyServiceTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.session = async_session()
        self.addAsyncCleanup(engine.dispose)
        self.addAsyncCleanup(self.session.close)
        self.addAsyncCleanup(self.session.rollback)
        await self.session.begin()

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

    async def test_knowledge_point_parent_must_belong_to_same_subject(self):
        first = await create_subject(
            self.session,
            SubjectCreate(name="Batch2 Subject One"),
        )
        second = await create_subject(
            self.session,
            SubjectCreate(name="Batch2 Subject Two"),
        )
        parent = await create_knowledge_point(
            self.session,
            KnowledgePointCreate(subject_id=first.id, name="Batch2 Parent"),
        )

        with self.assertRaises(TaxonomyValidationError):
            await create_knowledge_point(
                self.session,
                KnowledgePointCreate(
                    subject_id=second.id,
                    parent_id=parent.id,
                    name="Batch2 Invalid Child",
                ),
            )

    async def test_knowledge_point_cannot_move_under_descendant(self):
        subject = await create_subject(
            self.session,
            SubjectCreate(name="Batch2 Cycle Subject"),
        )
        parent = await create_knowledge_point(
            self.session,
            KnowledgePointCreate(subject_id=subject.id, name="Batch2 Cycle Parent"),
        )
        child = await create_knowledge_point(
            self.session,
            KnowledgePointCreate(
                subject_id=subject.id,
                parent_id=parent.id,
                name="Batch2 Cycle Child",
            ),
        )

        with self.assertRaises(TaxonomyValidationError):
            await update_knowledge_point(
                self.session,
                parent.id,
                KnowledgePointUpdate(parent_id=child.id),
            )

    async def test_archiving_knowledge_point_archives_subtree(self):
        subject = await create_subject(
            self.session,
            SubjectCreate(name="Batch2 Archive Subject"),
        )
        parent = await create_knowledge_point(
            self.session,
            KnowledgePointCreate(subject_id=subject.id, name="Batch2 Archive Parent"),
        )
        child = await create_knowledge_point(
            self.session,
            KnowledgePointCreate(
                subject_id=subject.id,
                parent_id=parent.id,
                name="Batch2 Archive Child",
            ),
        )

        await archive_knowledge_point(self.session, parent.id)
        tree = await get_subject_knowledge_tree(self.session, subject.id)

        self.assertEqual(tree.nodes[0].status, "archived")
        self.assertEqual(tree.nodes[0].children[0].status, "archived")
        self.assertEqual(tree.nodes[0].children[0].id, child.id)

    async def test_subject_knowledge_tree_is_nested(self):
        subject = await create_subject(
            self.session,
            SubjectCreate(name="Batch2 Tree Subject"),
        )
        parent = await create_knowledge_point(
            self.session,
            KnowledgePointCreate(subject_id=subject.id, name="高等数学"),
        )
        child = await create_knowledge_point(
            self.session,
            KnowledgePointCreate(subject_id=subject.id, parent_id=parent.id, name="函数"),
        )
        grandchild = await create_knowledge_point(
            self.session,
            KnowledgePointCreate(
                subject_id=subject.id,
                parent_id=child.id,
                name="三角函数",
            ),
        )

        tree = await get_subject_knowledge_tree(self.session, subject.id)

        self.assertEqual(tree.subject.id, subject.id)
        self.assertEqual(tree.nodes[0].id, parent.id)
        self.assertEqual(tree.nodes[0].children[0].id, child.id)
        self.assertEqual(tree.nodes[0].children[0].children[0].id, grandchild.id)
