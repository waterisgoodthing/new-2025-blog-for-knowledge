import unittest

from pydantic import ValidationError
from sqlalchemy import UniqueConstraint

from app.database import async_session, engine
from app.models.taxonomy import KnowledgePoint
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

    def test_knowledge_point_metadata_matches_sa_a_index_contract(self):
        indexes = {index.name: index for index in KnowledgePoint.__table__.indexes}

        self.assertTrue(
            {
                "idx_knowledge_points_parent",
                "idx_knowledge_points_subject_parent_sort",
                "idx_knowledge_points_subject_sort",
                "uq_knowledge_points_root_name",
                "uq_knowledge_points_child_name",
            }.issubset(indexes),
        )
        self.assertTrue(indexes["uq_knowledge_points_root_name"].unique)
        self.assertTrue(indexes["uq_knowledge_points_child_name"].unique)
        self.assertIn(
            "parent_id IS NULL",
            str(indexes["uq_knowledge_points_root_name"].dialect_options["postgresql"]["where"]),
        )
        self.assertIn(
            "parent_id IS NOT NULL",
            str(indexes["uq_knowledge_points_child_name"].dialect_options["postgresql"]["where"]),
        )
        self.assertFalse(
            any(
                constraint.name == "uq_knowledge_points_sibling_name"
                for constraint in KnowledgePoint.__table__.constraints
                if isinstance(constraint, UniqueConstraint)
            )
        )


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

    async def test_knowledge_point_root_name_conflict_is_case_insensitive(self):
        subject = await create_subject(
            self.session,
            SubjectCreate(name="Batch2 Case-Insensitive Root Subject"),
        )
        await create_knowledge_point(
            self.session,
            KnowledgePointCreate(subject_id=subject.id, name="Batch2 Algebra"),
        )

        with self.assertRaises(TaxonomyConflict):
            await create_knowledge_point(
                self.session,
                KnowledgePointCreate(subject_id=subject.id, name="batch2 algebra"),
            )

    async def test_knowledge_point_child_rename_conflict_is_case_insensitive(self):
        subject = await create_subject(
            self.session,
            SubjectCreate(name="Batch2 Case-Insensitive Child Subject"),
        )
        parent = await create_knowledge_point(
            self.session,
            KnowledgePointCreate(subject_id=subject.id, name="Batch2 Parent"),
        )
        await create_knowledge_point(
            self.session,
            KnowledgePointCreate(
                subject_id=subject.id,
                parent_id=parent.id,
                name="Batch2 Geometry",
            ),
        )
        target = await create_knowledge_point(
            self.session,
            KnowledgePointCreate(
                subject_id=subject.id,
                parent_id=parent.id,
                name="Batch2 Algebra",
            ),
        )

        with self.assertRaises(TaxonomyConflict):
            await update_knowledge_point(
                self.session,
                target.id,
                KnowledgePointUpdate(name="batch2 geometry"),
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
