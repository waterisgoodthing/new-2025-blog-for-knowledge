"""PR-05 Review Schema v2 contract tests (test-first).

Run via a Week-2 scratch-DB wrapper only (astra or opencode session instance):
    python3 /tmp/astra-week2-20260909/run-scratch.py .venv/bin/python -m pytest tests/test_review_schema_v2.py -q
"""

from __future__ import annotations

import os
import re
import subprocess
import unittest
import uuid
from datetime import datetime, timezone
from pathlib import Path

from pydantic import ValidationError
from sqlalchemy import inspect, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import IntegrityError

from app.database import async_session, engine
from app.models.review_item import ReviewItem, ReviewRecord
from app.schemas.question import QuestionDraftCreate
from app.schemas.review_item import ReviewItemOut, ReviewRecordOut, ReviewSubmit
from app.schemas.taxonomy import SubjectCreate
from app.services.draft_service import convert_question_draft, create_question_draft
from app.services.mistake_service import MistakeDraftCreate, convert_mistake_draft, create_mistake_draft
from app.services.taxonomy_service import create_subject


_BACKEND_DIR = Path(__file__).resolve().parent.parent
_PROJECT_ROOT = _BACKEND_DIR.parent
_MIGRATION_028_PATH = _BACKEND_DIR / "alembic" / "versions" / "028_review_items_v2.py"
_MIGRATION_029_PATH = _BACKEND_DIR / "alembic" / "versions" / "029_review_record_states.py"
_FRONTEND_DTO_PATH = _PROJECT_ROOT / "src" / "lib" / "api" / "review-items.ts"

_ALLOWED_STATES = {"active", "mastered", "paused"}
_FORBIDDEN_STATES = {"learning", "relearning", "young", "mature", "graduated"}


def _is_scratch_database() -> bool:
    url = os.environ.get("DATABASE_URL", "")
    return "astra_week2_" in url or "opencode_week2_" in url


def _run_alembic(args: list[str]) -> None:
    # The scratch wrapper exports DATABASE_URL/PYTHONPATH into this process;
    # alembic must target the same database the tests are running against.
    cmd = [".venv/bin/alembic"] + args
    result = subprocess.run(
        cmd,
        cwd=_BACKEND_DIR,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"alembic {' '.join(args)} failed (exit {result.returncode}):\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )


class ReviewSchemaV2ModelTest(unittest.TestCase):
    """Static contract on SQLAlchemy models."""

    def _check_constraint(self, name: str):
        for arg in ReviewItem.__table_args__:
            if hasattr(arg, "name") and arg.name == name:
                return arg
        self.fail(f"Missing ReviewItem check constraint {name}")

    def _record_check_constraint(self, name: str):
        for arg in ReviewRecord.__table_args__:
            if hasattr(arg, "name") and arg.name == name:
                return arg
        self.fail(f"Missing ReviewRecord check constraint {name}")

    def test_review_item_state_includes_mastered(self):
        constraint = self._check_constraint("ck_review_items_state")
        sql = str(constraint.sqltext).lower()
        self.assertIn("mastered", sql)
        for state in _ALLOWED_STATES:
            self.assertIn(state, sql)

    def test_review_item_algorithm_allows_v1_and_v2(self):
        constraint = self._check_constraint("ck_review_items_algorithm")
        sql = str(constraint.sqltext).lower()
        self.assertIn("fixed_interval_v1", sql)
        self.assertIn("fixed_interval_v2", sql)

    def test_review_item_last_rating_is_smallint_nullable_no_default(self):
        col = ReviewItem.__table__.c.last_rating
        self.assertTrue(col.nullable)
        self.assertEqual(str(col.type).lower(), "smallint")
        self.assertIsNone(col.default)
        self.assertIsNone(col.server_default)

    def test_review_item_algorithm_defaults_to_v2(self):
        col = ReviewItem.__table__.c.algorithm
        self.assertEqual(col.default.arg, "fixed_interval_v2")
        self.assertIsNotNone(col.server_default)
        self.assertIn("fixed_interval_v2", str(col.server_default.arg).lower())

    def test_review_item_state_excludes_forbidden_states(self):
        constraint = self._check_constraint("ck_review_items_state")
        sql = str(constraint.sqltext).lower()
        for forbidden in _FORBIDDEN_STATES:
            self.assertNotIn(forbidden, sql)

    def test_review_record_state_columns_are_not_null_with_active_default(self):
        prev = ReviewRecord.__table__.c.previous_state
        new = ReviewRecord.__table__.c.new_state
        self.assertFalse(prev.nullable)
        self.assertFalse(new.nullable)
        self.assertIn(str(prev.type).lower(), {"varchar(20)", "character varying(20)"})
        self.assertIn(str(new.type).lower(), {"varchar(20)", "character varying(20)"})
        self.assertIsNotNone(prev.server_default)
        self.assertIsNotNone(new.server_default)
        self.assertIn("active", str(prev.server_default.arg).lower())
        self.assertIn("active", str(new.server_default.arg).lower())

    def test_review_record_state_check_matches_item_state_set(self):
        constraint = self._record_check_constraint("ck_review_records_state")
        sql = str(constraint.sqltext).lower()
        for state in _ALLOWED_STATES:
            self.assertIn(state, sql)
        for forbidden in _FORBIDDEN_STATES:
            self.assertNotIn(forbidden, sql)


class ReviewSchemaV2PydanticTest(unittest.TestCase):
    """Static contract on Pydantic request/response schemas."""

    def _valid_item_kwargs(self, **overrides):
        return {
            "id": uuid.uuid4(),
            "target_type": "mistake",
            "target_id": str(uuid.uuid4()),
            "state": "mastered",
            "algorithm": "fixed_interval_v2",
            "interval_days": 3,
            "repetitions": 4,
            "next_review_at": datetime.now(timezone.utc),
            "last_reviewed_at": None,
            "last_rating": None,
            "question_text": "Question",
            "mistake_reason": "Reason",
            **overrides,
        }

    def _valid_record_kwargs(self, **overrides):
        now = datetime.now(timezone.utc)
        return {
            "id": uuid.uuid4(),
            "review_item_id": uuid.uuid4(),
            "rating": 4,
            "reviewed_at": now,
            "previous_interval_days": 1,
            "next_interval_days": 7,
            "previous_next_review_at": now,
            "next_review_at": now,
            "previous_state": "active",
            "new_state": "mastered",
            "created_at": now,
            **overrides,
        }

    def test_review_item_out_accepts_mastered_and_null_last_rating(self):
        item = ReviewItemOut(**self._valid_item_kwargs())
        self.assertEqual(item.state, "mastered")
        self.assertIsNone(item.last_rating)

    def test_review_item_out_accepts_last_rating_zero(self):
        item = ReviewItemOut(**self._valid_item_kwargs(last_rating=0))
        self.assertEqual(item.last_rating, 0)

    def test_review_item_out_rejects_unknown_state(self):
        with self.assertRaises(ValidationError):
            ReviewItemOut(**self._valid_item_kwargs(state="graduated"))

    def test_review_item_out_rejects_unknown_algorithm(self):
        with self.assertRaises(ValidationError):
            ReviewItemOut(**self._valid_item_kwargs(algorithm="sm2"))

    def test_review_record_out_requires_previous_state(self):
        with self.assertRaises(ValidationError):
            ReviewRecordOut(**self._valid_record_kwargs(previous_state=None))

    def test_review_record_out_requires_new_state(self):
        with self.assertRaises(ValidationError):
            ReviewRecordOut(**self._valid_record_kwargs(new_state=None))

    def test_review_record_out_rejects_unknown_state(self):
        with self.assertRaises(ValidationError):
            ReviewRecordOut(**self._valid_record_kwargs(new_state="mature"))

    def test_review_submit_accepts_six_ratings(self):
        now = datetime.now(timezone.utc)
        for rating in range(6):
            with self.subTest(rating=rating):
                ReviewSubmit(rating=rating, expected_next_review_at=now)

    def test_review_submit_rejects_rating_six(self):
        now = datetime.now(timezone.utc)
        with self.assertRaises(ValidationError):
            ReviewSubmit(rating=6, expected_next_review_at=now)


class ReviewSchemaV2FrontendTest(unittest.TestCase):
    """Static contract on src/lib/api/review-items.ts."""

    def setUp(self):
        self.source = _FRONTEND_DTO_PATH.read_text(encoding="utf-8")

    def test_review_item_state_union_includes_mastered(self):
        self.assertIn("state: 'active' | 'mastered' | 'paused'", self.source)

    def test_review_item_algorithm_union_includes_v2(self):
        self.assertIn("algorithm: 'fixed_interval_v1' | 'fixed_interval_v2'", self.source)

    def test_review_item_last_rating_optional(self):
        self.assertIn("last_rating: number | null", self.source)

    def test_review_record_state_unions_present(self):
        self.assertIn("previous_state: 'active' | 'mastered' | 'paused'", self.source)
        self.assertIn("new_state: 'active' | 'mastered' | 'paused'", self.source)

    def test_old_state_union_removed(self):
        self.assertNotIn("state: 'active' | 'paused'", self.source)

    def test_old_algorithm_union_removed(self):
        for line in self.source.splitlines():
            stripped = line.strip()
            if stripped.startswith("algorithm:"):
                self.assertNotEqual(stripped, "algorithm: 'fixed_interval_v1'")

    def test_no_forbidden_states_in_dto(self):
        for forbidden in _FORBIDDEN_STATES:
            self.assertNotIn(f"'{forbidden}'", self.source)


class ReviewSchemaV2MigrationStaticTest(unittest.TestCase):
    """Static contract on migration files."""

    def test_028_file_exists(self):
        self.assertTrue(_MIGRATION_028_PATH.exists())

    def test_029_file_exists(self):
        self.assertTrue(_MIGRATION_029_PATH.exists())

    def test_028_revision_chain(self):
        source = _MIGRATION_028_PATH.read_text(encoding="utf-8")
        self.assertIn('revision: str = "028"', source)
        self.assertIn('down_revision: str | None = "027"', source)

    def test_029_revision_chain(self):
        source = _MIGRATION_029_PATH.read_text(encoding="utf-8")
        self.assertIn('revision: str = "029"', source)
        self.assertIn('down_revision: str | None = "028"', source)

    def test_028_updates_existing_rows_to_v2(self):
        source = _MIGRATION_028_PATH.read_text(encoding="utf-8")
        self.assertIn("fixed_interval_v2", source)
        # Expect an UPDATE that migrates existing rows, not just a default change.
        self.assertRegex(source, r"UPDATE\s+review_items", re.IGNORECASE)

    def test_028_adds_last_rating(self):
        source = _MIGRATION_028_PATH.read_text(encoding="utf-8")
        self.assertIn("last_rating", source)

    def test_029_adds_state_columns(self):
        source = _MIGRATION_029_PATH.read_text(encoding="utf-8")
        self.assertIn("previous_state", source)
        self.assertIn("new_state", source)

    def test_migrations_have_state_checks(self):
        for path in (_MIGRATION_028_PATH, _MIGRATION_029_PATH):
            source = path.read_text(encoding="utf-8").lower()
            for state in _ALLOWED_STATES:
                self.assertIn(state, source)

    def test_migrations_exclude_forbidden_states(self):
        for path in (_MIGRATION_028_PATH, _MIGRATION_029_PATH):
            source = path.read_text(encoding="utf-8").lower()
            for forbidden in _FORBIDDEN_STATES:
                self.assertNotIn(forbidden, source)


@unittest.skipUnless(_is_scratch_database(), "scratch DB only")
class ReviewSchemaV2MigrationDynamicTest(unittest.IsolatedAsyncioTestCase):
    """Dynamic migration replay using the scratch database."""

    async def asyncSetUp(self):
        # IsolatedAsyncioTestCase creates a new loop per test; discard any
        # pooled connection left by an earlier test module on another loop.
        await engine.dispose(close=False)
        self.session = async_session()
        self.addAsyncCleanup(engine.dispose)
        self.addAsyncCleanup(self.session.close)
        self.addAsyncCleanup(self.session.rollback)
        await self.session.begin()

    async def _alembic(self, args: list[str]) -> None:
        await self.session.rollback()
        try:
            _run_alembic(args)
        finally:
            await self.session.begin()

    async def _create_review_item(self, state: str, algorithm: str, last_rating: int | None):
        subject = await create_subject(
            self.session,
            SubjectCreate(name=f"PR05 {uuid.uuid4().hex[:8]}"),
        )
        qdraft = await create_question_draft(
            self.session,
            QuestionDraftCreate(
                subject_id=subject.id,
                question_text="PR05 test question?",
                question_type="short_answer",
                correct_answer="Correct",
                explanation="Explanation",
            ),
        )
        question = await convert_question_draft(self.session, qdraft.item.id, version=1)
        mdraft = await create_mistake_draft(
            self.session,
            MistakeDraftCreate(
                question_id=question.id,
                my_answer="Wrong",
                mistake_reason="Missed",
            ),
        )
        mistake = await convert_mistake_draft(self.session, mdraft.item.id, version=1)
        item = await self.session.get(ReviewItem, mistake.review_item_id)
        item.state = state
        item.algorithm = algorithm
        if last_rating is not None:
            item.last_rating = last_rating
        await self.session.commit()
        await self.session.begin()
        return item.id

    async def _cleanup_review_item(self, item_id: uuid.UUID) -> None:
        await self.session.rollback()
        async with engine.connect() as conn:
            await conn.execute(
                text("DELETE FROM review_records WHERE review_item_id = :id"),
                {"id": item_id},
            )
            await conn.execute(
                text("DELETE FROM review_items WHERE id = :id"),
                {"id": item_id},
            )
            await conn.commit()
        await self.session.begin()

    async def _inspect_review_items_columns(self):
        async with engine.connect() as conn:
            return await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_columns("review_items"))

    async def _inspect_review_records_columns(self):
        async with engine.connect() as conn:
            return await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_columns("review_records"))

    async def _inspect_review_item_constraints(self):
        async with engine.connect() as conn:
            return await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_check_constraints("review_items"))

    async def _get_review_item_row(self, item_id: uuid.UUID):
        async with engine.connect() as conn:
            result = await conn.execute(
                text("SELECT state, algorithm FROM review_items WHERE id = :id"),
                {"id": item_id},
            )
            return result.mappings().one_or_none()

    async def _get_review_item_last_rating(self, item_id: uuid.UUID):
        async with engine.connect() as conn:
            result = await conn.execute(
                text("SELECT last_rating FROM review_items WHERE id = :id"),
                {"id": item_id},
            )
            row = result.mappings().one_or_none()
            return row["last_rating"] if row else None

    async def _get_review_records_count(self):
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT COUNT(*) FROM review_records"))
            return result.scalar_one()

    async def test_migration_replay_and_state_normalization(self):
        # Start from a known head, create data, then exercise downgrades/upgrades.
        await self._alembic(["upgrade", "head"])
        item_id = await self._create_review_item(
            state="mastered", algorithm="fixed_interval_v2", last_rating=4
        )

        # 029 -> 028: record state columns must disappear.
        await self._alembic(["downgrade", "028"])
        record_cols = await self._inspect_review_records_columns()
        record_col_names = {c["name"] for c in record_cols}
        self.assertNotIn("previous_state", record_col_names)
        self.assertNotIn("new_state", record_col_names)
        item_row = await self._get_review_item_row(item_id)
        self.assertEqual(item_row["state"], "mastered")
        self.assertEqual(item_row["algorithm"], "fixed_interval_v2")
        self.assertEqual(await self._get_review_item_last_rating(item_id), 4)

        # 028 -> 027: mastered collapses to active, algorithm back to v1, last_rating dropped.
        await self._alembic(["downgrade", "027"])
        cols = await self._inspect_review_items_columns()
        col_names = {c["name"] for c in cols}
        self.assertNotIn("last_rating", col_names)
        item_row = await self._get_review_item_row(item_id)
        self.assertEqual(item_row["state"], "active")
        self.assertEqual(item_row["algorithm"], "fixed_interval_v1")

        # Verify v1 CHECK constraints restored.
        constraints = await self._inspect_review_item_constraints()
        check_names = {c["name"] for c in constraints}
        self.assertIn("ck_review_items_state", check_names)
        self.assertIn("ck_review_items_algorithm", check_names)
        state_sql = next(c["sqltext"] for c in constraints if c["name"] == "ck_review_items_state")
        self.assertIn("active", state_sql.lower())
        self.assertIn("paused", state_sql.lower())
        self.assertNotIn("mastered", state_sql.lower())
        algo_sql = next(c["sqltext"] for c in constraints if c["name"] == "ck_review_items_algorithm")
        self.assertIn("fixed_interval_v1", algo_sql.lower())
        self.assertNotIn("fixed_interval_v2", algo_sql.lower())

        # 027 -> 028: all rows updated to v2, last_rating re-added.
        await self._alembic(["upgrade", "028"])
        cols = await self._inspect_review_items_columns()
        col_names = {c["name"] for c in cols}
        self.assertIn("last_rating", col_names)
        item_row = await self._get_review_item_row(item_id)
        self.assertEqual(item_row["state"], "active")
        self.assertEqual(item_row["algorithm"], "fixed_interval_v2")
        self.assertIsNone(await self._get_review_item_last_rating(item_id))

        # Verify v2 CHECK constraints.
        constraints = await self._inspect_review_item_constraints()
        state_sql = next(c["sqltext"] for c in constraints if c["name"] == "ck_review_items_state")
        self.assertIn("mastered", state_sql.lower())
        algo_sql = next(c["sqltext"] for c in constraints if c["name"] == "ck_review_items_algorithm")
        self.assertIn("fixed_interval_v1", algo_sql.lower())
        self.assertIn("fixed_interval_v2", algo_sql.lower())

        # 028 -> 029: record state columns added and backfilled.
        await self._alembic(["upgrade", "029"])
        record_cols = await self._inspect_review_records_columns()
        record_col_names = {c["name"] for c in record_cols}
        self.assertIn("previous_state", record_col_names)
        self.assertIn("new_state", record_col_names)
        prev_col = next(c for c in record_cols if c["name"] == "previous_state")
        new_col = next(c for c in record_cols if c["name"] == "new_state")
        self.assertFalse(prev_col["nullable"])
        self.assertFalse(new_col["nullable"])
        self.assertIsNotNone(prev_col["default"])
        self.assertIsNotNone(new_col["default"])
        self.assertIn("active", str(prev_col["default"]).lower())
        self.assertIn("active", str(new_col["default"]).lower())

        # Leave the database back at head for any subsequent test modules.
        await self._alembic(["downgrade", "027"])
        await self._alembic(["upgrade", "head"])
        await self._cleanup_review_item(item_id)

    async def test_new_rows_default_to_v2_algorithm_after_028(self):
        await self._alembic(["upgrade", "head"])
        subject = await create_subject(
            self.session,
            SubjectCreate(name=f"PR05 default {uuid.uuid4().hex[:8]}"),
        )
        qdraft = await create_question_draft(
            self.session,
            QuestionDraftCreate(
                subject_id=subject.id,
                question_text="PR05 default question?",
                question_type="short_answer",
                correct_answer="Correct",
                explanation="Explanation",
            ),
        )
        question = await convert_question_draft(self.session, qdraft.item.id, version=1)
        mdraft = await create_mistake_draft(
            self.session,
            MistakeDraftCreate(
                question_id=question.id,
                my_answer="Wrong",
                mistake_reason="Missed",
            ),
        )
        mistake = await convert_mistake_draft(self.session, mdraft.item.id, version=1)
        item_id = mistake.review_item_id
        await self.session.commit()
        await self.session.begin()
        item_row = await self._get_review_item_row(item_id)
        self.assertEqual(item_row["algorithm"], "fixed_interval_v2")
        await self._cleanup_review_item(item_id)

    async def test_forbidden_states_rejected_at_database_level(self):
        await self._alembic(["upgrade", "head"])
        item_id = await self._create_review_item(
            state="active", algorithm="fixed_interval_v2", last_rating=None
        )
        async with engine.connect() as conn:
            with self.assertRaises(IntegrityError):
                await conn.execute(
                    text("UPDATE review_items SET state = 'graduated' WHERE id = :id"),
                    {"id": item_id},
                )
                await conn.commit()
        await self._cleanup_review_item(item_id)
