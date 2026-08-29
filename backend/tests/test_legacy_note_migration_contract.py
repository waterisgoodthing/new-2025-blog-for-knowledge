import os
import json
import unittest

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


MIRROR_NEGATIVE_FIXTURES = (
    ("empty_choice_options", "single_choice", [], "A", {"kind": "single_choice", "value": ["A"]}),
    ("one_choice_option", "single_choice", [{"key": "A", "text": "one"}], "A", {"kind": "single_choice", "value": ["A"]}),
    ("duplicate_option_keys", "single_choice", [{"key": "A", "text": "one"}, {"key": "A", "text": "again"}], "A", {"kind": "single_choice", "value": ["A"]}),
    ("unknown_single_answer_key", "single_choice", [{"key": "A", "text": "one"}, {"key": "B", "text": "two"}], "C", {"kind": "single_choice", "value": ["C"]}),
    ("duplicate_multiple_answer", "multiple_choice", [{"key": "A", "text": "one"}, {"key": "B", "text": "two"}], "A,A", {"kind": "multiple_choice", "value": ["A", "A"]}),
    ("nonempty_short_answer_options", "short_answer", [{"key": "A", "text": "one"}], "one", {"kind": "short_answer", "value": "one"}),
    ("true_false_non_boolean_answer_data", "true_false", [], "True", {"kind": "true_false", "value": "True"}),
)

RETAINED_NEGATIVE_SLOT_COLUMNS = (
    "question_conversion_approved_by", "question_conversion_approved_at",
    "question_conversion_sequence", "question_approval_event_id",
    "mistake_conversion_approved_by", "mistake_conversion_approved_at",
    "mistake_conversion_sequence", "mistake_approval_event_id",
    "schedule_approved_by", "schedule_approved_at", "schedule_approval_sequence",
    "schedule_approval_event_id", "rollback_actor_id", "rollback_event_id",
    "rollback_reference", "target_bundle_hash", "mapped_next_review_at",
    "mapped_last_reviewed_at",
)
RETAINED_NEGATIVE_BUNDLE_FIXTURES = ("empty_arrays", "target_scalar")


class LegacyNoteMigrationContractTest(unittest.IsolatedAsyncioTestCase):
    async def test_isolated_retained_negative_fixtures_fail_without_mutation(self):
        """Executable isolated fixture; intentionally not run in this no-DB pass."""
        database_url = os.environ.get("LSR03_DATABASE_URL")
        if not database_url:
            self.skipTest("LSR03_DATABASE_URL is required for isolated database tests")

        engine = create_async_engine(database_url, poolclass=None)
        try:
            async with engine.connect() as connection:
                baseline = (await connection.execute(text("""
                    SELECT m.id,m.source_note_id,m.mapping_version,m.source_hash,m.approved_by,
                           row_to_json(m)::text AS ledger_json,
                           (SELECT count(*) FROM public.legacy_note_migration_events e WHERE e.ledger_id=m.id) AS event_count
                    FROM public.legacy_note_migrations m
                    WHERE m.state='pending_mapping' AND m.source_status='published' AND m.source_hidden=FALSE
                      AND m.source_approval_event_id IS NOT NULL
                    LIMIT 1
                """))).mappings().one_or_none()
                if baseline is None:
                    self.skipTest("an approved public pending isolated baseline is required")
                for column in RETAINED_NEGATIVE_BUNDLE_FIXTURES + RETAINED_NEGATIVE_SLOT_COLUMNS:
                    savepoint = await connection.begin_nested()
                    try:
                        if column not in RETAINED_NEGATIVE_BUNDLE_FIXTURES:
                            value = "f" * 64 if column in {"rollback_reference", "target_bundle_hash"} else (
                                1 if column.endswith("sequence") else "11111111-1111-4111-8111-111111111111"
                            )
                            if column.endswith("_at") or column.endswith("_reviewed_at"):
                                value = "2026-08-25T00:00:00+00:00"
                            await connection.execute(text(
                                f"UPDATE public.legacy_note_migrations SET {column}=:value WHERE id=:ledger"
                            ), {"value": value, "ledger": baseline["id"]})
                        if column == "empty_arrays":
                            bundle_sql = "ROW(NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,CAST(:qkps AS integer[]),CAST(:projections AS integer[]))::legacy_migration.legacy_note_migration_target_bundle"
                        elif column == "target_scalar":
                            bundle_sql = "ROW(NULL,NULL,:question,NULL,NULL,NULL,NULL,NULL,NULL::integer[],NULL::integer[])::legacy_migration.legacy_note_migration_target_bundle"
                        else:
                            bundle_sql = "ROW(NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL::integer[],NULL::integer[])::legacy_migration.legacy_note_migration_target_bundle"
                        failed = False
                        try:
                            await connection.execute(text(f"""
                                SELECT legacy_migration.transition_legacy_note_migration(
                                  :ledger,'pending_mapping','retained_public_only',:actor,'fixture',:source,:mapping,:hash,
                                  {bundle_sql},:rollback_reference,:rollback_hash,:mapped_next,:mapped_last,'{{}}')
                            """), {
                                "ledger": baseline["id"], "actor": baseline["approved_by"],
                                "source": baseline["source_note_id"], "mapping": baseline["mapping_version"],
                                "hash": baseline["source_hash"], "rollback_reference": "f" * 64 if column == "rollback_reference" else None,
                                "rollback_hash": "f" * 64 if column == "target_bundle_hash" else None,
                                "mapped_next": "2026-08-25T00:00:00+00:00" if column == "mapped_next_review_at" else None,
                                "mapped_last": "2026-08-25T00:00:00+00:00" if column == "mapped_last_reviewed_at" else None,
                                "qkps": "{}" if column == "empty_arrays" else None,
                                "projections": "{}" if column == "empty_arrays" else None,
                                "question": "11111111-1111-4111-8111-111111111111" if column == "target_scalar" else None,
                            })
                        except Exception:
                            failed = True
                        self.assertTrue(failed, column)
                    finally:
                        await savepoint.rollback()
                    after = (await connection.execute(text("""
                        SELECT row_to_json(m)::text AS ledger_json,
                               (SELECT count(*) FROM public.legacy_note_migration_events e WHERE e.ledger_id=m.id) AS event_count
                        FROM public.legacy_note_migrations m WHERE m.id=:ledger
                    """), {"ledger": baseline["id"]})).mappings().one()
                    self.assertEqual(after["ledger_json"], baseline["ledger_json"], column)
                    self.assertEqual(after["event_count"], baseline["event_count"], column)
        finally:
            await engine.dispose()

    async def test_isolated_mirror_negative_fixtures_reject_and_rollback(self):
        """Executable isolated fixture; intentionally not run in this no-DB pass."""
        database_url = os.environ.get("LSR03_DATABASE_URL")
        if not database_url:
            self.skipTest("LSR03_DATABASE_URL is required for isolated database tests")

        engine = create_async_engine(database_url, poolclass=None)
        try:
            async with engine.connect() as connection:
                baseline = (await connection.execute(text("""
                    SELECT m.target_question_id,m.target_question_source_id,m.source_note_id,
                           m.mapping_version,m.source_hash,qs.source_note
                    FROM public.legacy_note_migrations m
                    JOIN public.question_sources qs ON qs.id=m.target_question_source_id
                    WHERE m.state IN ('migrated_active','migrated_paused')
                    LIMIT 1
                """))).mappings().one_or_none()
                if baseline is None:
                    self.skipTest("a migrated isolated baseline is required")
                source_note = baseline["source_note"]
                if isinstance(source_note, str):
                    source_note = json.loads(source_note)
                for name, question_type, options, correct_answer, answer_data in MIRROR_NEGATIVE_FIXTURES:
                    savepoint = await connection.begin_nested()
                    try:
                        metadata = json.loads(json.dumps(source_note))
                        mirror = metadata["mirror_contract"]
                        mirror.update({
                            "question_type": question_type, "options": options,
                            "correct_answer": correct_answer, "answer_data": answer_data,
                        })
                        await connection.execute(text("""
                            UPDATE public.questions
                               SET question_type=:question_type, options=CAST(:options AS json),
                                   correct_answer=:correct_answer, answer_data=CAST(:answer_data AS json)
                             WHERE id=:question_id
                        """), {
                            "question_type": question_type, "options": json.dumps(options),
                            "correct_answer": correct_answer, "answer_data": json.dumps(answer_data),
                            "question_id": baseline["target_question_id"],
                        })
                        await connection.execute(text("""
                            UPDATE public.question_sources SET source_note=:source_note WHERE id=:source_id
                        """), {
                            "source_note": json.dumps(metadata, separators=(",", ":")),
                            "source_id": baseline["target_question_source_id"],
                        })
                        result = await connection.scalar(text("""
                            SELECT legacy_migration.legacy_question_mirror_matches(
                              :question_id,:source_id,:source_note_id,:mapping_version,:source_hash)
                        """), dict(baseline))
                        self.assertFalse(result, name)
                    finally:
                        await savepoint.rollback()
                restored = await connection.scalar(text(
                    "SELECT source_note FROM public.question_sources WHERE id=:source_id"
                ), {"source_id": baseline["target_question_source_id"]})
                self.assertEqual(restored, source_note if isinstance(restored, dict) else json.dumps(source_note, separators=(",", ":")))
        finally:
            await engine.dispose()

    async def test_isolated_database_exposes_frozen_contract_surface(self):
        database_url = os.environ.get("LSR03_DATABASE_URL")
        if not database_url:
            self.skipTest("LSR03_DATABASE_URL is required for isolated database tests")

        engine = create_async_engine(database_url, poolclass=None)
        try:
            async with engine.connect() as connection:
                revision = await connection.scalar(text("SELECT version_num FROM alembic_version"))
                ledger = await connection.scalar(
                    text("SELECT to_regclass('public.legacy_note_migrations')::text")
                )
                migration_schema = await connection.scalar(
                    text("SELECT to_regnamespace('legacy_migration')::text")
                )
            self.assertEqual(revision, "026")
            self.assertEqual(ledger, "legacy_note_migrations")
            self.assertEqual(migration_schema, "legacy_migration")
        finally:
            await engine.dispose()

    async def test_ledger_keeps_immutable_payload_and_sixteen_key_marker(self):
        database_url = os.environ.get("LSR03_DATABASE_URL")
        if not database_url:
            self.skipTest("LSR03_DATABASE_URL is required for isolated database tests")

        engine = create_async_engine(database_url, poolclass=None)
        try:
            async with engine.connect() as connection:
                ledger_columns = set((await connection.execute(text("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_schema='public' AND table_name='legacy_note_migrations'
                """))).scalars())
                marker_columns = set((await connection.execute(text("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_schema='legacy_migration'
                      AND table_name='legacy_migration_guard_nonces'
                """))).scalars())
            self.assertIn("canonical_payload", ledger_columns)
            self.assertGreaterEqual(
                len(marker_columns),
                16,
                "the frozen marker must carry all identity/binding keys",
            )
        finally:
            await engine.dispose()


if __name__ == "__main__":
    unittest.main()
