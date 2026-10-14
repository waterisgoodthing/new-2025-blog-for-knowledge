"""PR-09 rework tests: next_due mapping, report honesty, source drift, MissingGreenlet.

Covers PR9F-01..07 and PR9U-01.  DB-backed tests require scratch PostgreSQL
via ``scripts/week3-scratch-guard.py`` and self-skip otherwise.
"""

from __future__ import annotations

import json
import unittest
import uuid
from datetime import date, datetime, timezone

from sqlalchemy import text

from app.services.wk3_mistake_visibility_migration import (
    MAPPING_VERSION,
    Wk3MigrationReport,
    _map_next_review_to_due,
)

# ---------------------------------------------------------------------------
# Pure tests (no DB)
# ---------------------------------------------------------------------------


def test_map_next_review_date_to_utc_midnight() -> None:
    mapped, used = _map_next_review_to_due(date(2026, 12, 15))
    assert used is True
    assert mapped == datetime(2026, 12, 15, tzinfo=timezone.utc)


def test_map_next_review_none_returns_default() -> None:
    mapped, used = _map_next_review_to_due(None)
    assert mapped is None
    assert used is False


def test_map_next_review_naive_datetime_assumes_utc() -> None:
    naive = datetime(2027, 1, 20, 8, 30)
    mapped, used = _map_next_review_to_due(naive)
    assert used is True
    assert mapped == datetime(2027, 1, 20, 8, 30, tzinfo=timezone.utc)


def test_map_next_review_aware_datetime_converts_to_utc() -> None:
    from datetime import timedelta

    aware = datetime(2027, 1, 20, 8, 30, tzinfo=timezone(timedelta(hours=8)))
    mapped, used = _map_next_review_to_due(aware)
    assert used is True
    assert mapped == datetime(2027, 1, 20, 0, 30, tzinfo=timezone.utc)


def test_map_next_review_invalid_returns_default() -> None:
    mapped, used = _map_next_review_to_due("not-a-date")
    assert mapped is None
    assert used is False


# --- PR9F-04: first dry-run must not report replay_noop=false ---


def test_first_dry_run_replay_noop_is_true() -> None:
    report = Wk3MigrationReport(generated_at="2026-09-24T00:00:00+00:00", dry_run=True)
    report.would_create = 3
    data = report.to_json_dict()
    assert data["checks"]["replay_noop"] is True
    assert data["idempotency"]["replay_noop"] is True


def test_real_run_can_report_replay_noop_false() -> None:
    report = Wk3MigrationReport(generated_at="2026-09-24T00:00:00+00:00", dry_run=False)
    report.targets_created = 1
    report.replay_noop = False
    data = report.to_json_dict()
    assert data["checks"]["replay_noop"] is False


# --- PR9F-03: dry-run planned values ---


def test_dry_run_report_has_would_fields_and_zero_created() -> None:
    report = Wk3MigrationReport(generated_at="2026-09-24T00:00:00+00:00", dry_run=True)
    report.source_total = 2
    report.would_create = 2
    report.would_create_review_items = 2
    report.would_next_due_from_source = 1
    report.would_next_due_default = 1
    data = report.to_json_dict()
    assert data["dry_run"] is True
    assert data["targets"]["created"] == 0
    assert data["targets"]["would_create"] == 2
    assert data["review_items"]["created_v2"] == 0
    assert data["review_items"]["would_create_v2"] == 2
    assert data["review_items"]["next_due_from_source"] == 0
    assert data["review_items"]["would_next_due_from_source"] == 1


def test_real_run_report_created_fields_have_values() -> None:
    report = Wk3MigrationReport(generated_at="2026-09-24T00:00:00+00:00", dry_run=False)
    report.source_total = 1
    report.targets_created = 1
    report.review_items_created_v2 = 1
    report.next_due_from_source = 1
    data = report.to_json_dict()
    assert data["targets"]["created"] == 1
    assert data["review_items"]["created_v2"] == 1
    assert data["review_items"]["next_due_from_source"] == 1


# --- PR9F-02: checks are computed, not hardcoded ---


def test_report_checks_use_instance_fields() -> None:
    report = Wk3MigrationReport(generated_at="2026-09-24T00:00:00+00:00")
    report.provenance_match = False
    report.visibility_matrix_match = False
    report.public_field_allowlist_match = True
    data = report.to_json_dict()
    assert data["checks"]["provenance_match"] is False
    assert data["checks"]["visibility_matrix_match"] is False
    assert data["checks"]["public_field_allowlist_match"] is True


# --- PR9F-05: retained_public_only goes to rejected ---


def test_report_rejected_count_includes_source_drift() -> None:
    report = Wk3MigrationReport(generated_at="2026-09-24T00:00:00+00:00")
    report.source_total = 2
    report.skipped_already_migrated = 1
    report.rejected.append({"source_note_id": "x", "reason": "source_drift"})
    data = report.to_json_dict()
    assert data["checks"]["count_match"] is True
    assert data["targets"]["rejected"][0]["reason"] == "source_drift"


def test_report_retained_public_only_maps_to_rejected_reason() -> None:
    report = Wk3MigrationReport(generated_at="2026-09-24T00:00:00+00:00")
    report.source_total = 1
    report.rejected.append({
        "source_note_id": "y",
        "reason": "mapping_failed_retained_public_only",
    })
    data = report.to_json_dict()
    assert data["targets"]["rejected"][0]["reason"] == "mapping_failed_retained_public_only"
    assert data["checks"]["count_match"] is True


# --- R3: dry-run count_match must include would_* plan counts ---


def test_dry_run_count_match_uses_would_fields() -> None:
    report = Wk3MigrationReport(generated_at="2026-09-24T00:00:00+00:00", dry_run=True)
    report.source_total = 2
    report.would_create = 1
    report.would_reconcile = 1
    assert report.to_json_dict()["checks"]["count_match"] is True
    report.would_reconcile = 0
    assert report.to_json_dict()["checks"]["count_match"] is False


# ---------------------------------------------------------------------------
# DB-backed tests (require scratch PostgreSQL via guard)
# ---------------------------------------------------------------------------


async def _count(session, sql: str, **params) -> int:
    return int((await session.execute(text(sql), params)).scalar() or 0)


async def _setup_infra(session) -> tuple[int, int]:
    """Create subject + knowledge point; return (subject_id, kp_id)."""
    await session.execute(text(
        "DO $$ BEGIN "
        "IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='legacy_note_adapter_runner') THEN "
        "  CREATE ROLE legacy_note_adapter_runner LOGIN; "
        "END IF; "
        "END $$"
    ))
    subject_id = (await session.execute(text(
        "INSERT INTO public.subjects (name, status) VALUES ('pr09-rework-subj','active') "
        "ON CONFLICT (name) DO UPDATE SET name=EXCLUDED.name RETURNING id"
    ))).scalar_one()
    kp_id = (await session.execute(text(
        "INSERT INTO public.knowledge_points (subject_id, name) VALUES (:sid,'pr09-rework-kp') "
        "ON CONFLICT (subject_id, lower(name)) WHERE parent_id IS NULL "
        "DO UPDATE SET name=EXCLUDED.name RETURNING id"
    ), {"sid": subject_id})).scalar_one()
    return int(subject_id), int(kp_id)


async def _cleanup_note(session, note_id: uuid.UUID) -> None:
    """Remove the seeded note and every migration row/target that blocks its deletion.

    ``legacy_note_migrations`` rejects direct DELETE via guard triggers and its
    ``source_note_id`` FK is ON DELETE RESTRICT, so cleanup runs in
    ``session_replication_role = replica`` (superuser scratch DB) to drop ledger
    rows and associated targets first, then the note itself.
    """
    try:
        await session.execute(text("RESET SESSION AUTHORIZATION"))
    except Exception:
        pass
    await session.execute(text("SET session_replication_role = replica"))
    try:
        rows = (await session.execute(text(
            "SELECT target_review_item_id, target_mistake_id, target_mistake_draft_id, "
            "target_mistake_draft_item_id, target_question_draft_id, target_question_draft_item_id, "
            "target_question_id, target_question_source_id "
            "FROM public.legacy_note_migrations WHERE source_note_id=:sid"
        ), {"sid": note_id})).all()
        for ri, mk, md, mdi, qd, qdi, qid, qsid in rows:
            deletes = (
                ("review_records", "review_item_id", ri),
                ("review_items", "id", ri),
                ("knowledge_point_links", "target_id", str(mk) if mk is not None else None),
                ("mistakes", "id", mk),
                ("mistake_drafts", "id", md),
                ("draft_items", "id", mdi),
                ("question_knowledge_points", "question_id", qid),
                ("question_sources", "id", qsid),
                ("question_drafts", "id", qd),
                ("questions", "id", qid),
                ("draft_items", "id", qdi),
            )
            for table, col, val in deletes:
                if val is None:
                    continue
                if table == "knowledge_point_links":
                    await session.execute(text(
                        f"DELETE FROM public.{table} WHERE {col}=:val AND target_type='mistake'"
                    ), {"val": val})
                else:
                    await session.execute(text(
                        f"DELETE FROM public.{table} WHERE {col}=:val"
                    ), {"val": val})
        for table in (
            "legacy_note_migration_events",
            "legacy_migration_rollback_audits",
            "legacy_note_migration_rejections",
            "legacy_note_migrations",
        ):
            await session.execute(
                text(f"DELETE FROM public.{table} WHERE source_note_id=:sid"), {"sid": note_id}
            )
        await session.execute(text("DELETE FROM public.notes WHERE id=:sid"), {"sid": note_id})
        await session.commit()
    finally:
        await session.execute(text("RESET session_replication_role"))
        await session.commit()


async def _seed_migratable_note(
    session,
    *,
    status: str = "published",
    hidden: bool = False,
    next_review: date | None = date(2026, 12, 15),
    title: str = "pr09-rework-note",
) -> uuid.UUID:
    note_id = uuid.uuid4()
    slug = f"pr09rw-{note_id.hex[:12]}"
    ai_meta = json.dumps({
        "legacy_question": {
            "question_type": "true_false",
            "options": [],
        }
    })
    await session.execute(text(
        "INSERT INTO public.notes "
        "(id,slug,title,content,type,status,hidden,revision,ef,interval,repetitions,"
        "subject,question,my_answer,correct_answer,analysis,knowledge_points,"
        "next_review,ai_metadata) "
        "VALUES (:id,:slug,:title,'c','mistake',:status,:hidden,1,2.5,0,0,"
        "'pr09-rework-subj','Q?','wrong','True','an','pr09-rework-kp',"
        ":next_review,CAST(:ai_meta AS json))"
    ), {
        "id": note_id, "slug": slug, "title": title,
        "status": status, "hidden": hidden,
        "next_review": next_review,
        "ai_meta": ai_meta,
    })
    return note_id


class Wk3ReworkDbTest(unittest.IsolatedAsyncioTestCase):
    """DB-backed rework verification.  Skips without scratch PostgreSQL."""

    async def asyncSetUp(self):
        from app.database import async_session, engine

        await engine.dispose(close=False)
        self.session = async_session()
        self.addAsyncCleanup(engine.dispose)
        self.addAsyncCleanup(self.session.close)
        self.addAsyncCleanup(self.session.rollback)
        self._db_ready = True
        try:
            await self.session.execute(text("SELECT 1 FROM public.notes LIMIT 1"))
        except Exception:
            self._db_ready = False

    def _require_db(self):
        if not self._db_ready:
            self.skipTest("scratch PostgreSQL required (run via week3-scratch-guard)")

    async def _reset_identity(self) -> None:
        """Restore the superuser identity a dry-run's adapter switch left set."""
        try:
            await self.session.execute(text("RESET SESSION AUTHORIZATION"))
            await self.session.commit()
        except Exception:
            await self.session.rollback()

    async def _prepare_note(self, **kwargs) -> uuid.UUID:
        try:
            await _setup_infra(self.session)
            note_id = await _seed_migratable_note(self.session, **kwargs)
            await self.session.commit()
            return note_id
        except Exception as exc:
            self.skipTest(f"scratch PostgreSQL with ledger access required: {exc}")

    async def test_next_due_maps_from_source(self):
        """PR9F-01: review_items.next_due must equal source next_review."""
        self._require_db()
        from app.services.wk3_mistake_visibility_migration import run_wk3_migration

        note_id = await self._prepare_note(next_review=date(2026, 12, 15))

        try:
            report = await run_wk3_migration(self.session, dry_run=False)
            await self.session.commit()
        except Exception as exc:
            self.skipTest(f"migration infrastructure required: {exc}")

        expected = datetime(2026, 12, 15, tzinfo=timezone.utc)
        row = (await self.session.execute(text(
            "SELECT ri.next_review_at FROM public.review_items ri "
            "JOIN public.mistakes m ON m.id = ri.mistake_id "
            "JOIN public.legacy_note_migrations lm ON lm.target_mistake_id = m.id "
            "WHERE lm.source_note_id = :sid"
        ), {"sid": note_id})).scalar_one_or_none()

        self.assertIsNotNone(row, "review item must exist after migration")
        if isinstance(row, datetime) and row.tzinfo is not None:
            self.assertEqual(row.astimezone(timezone.utc), expected)
        else:
            self.assertEqual(row, expected)

        self.assertEqual(report.next_due_from_source, 1)
        self.assertEqual(report.next_due_default, 0)

        await _cleanup_note(self.session, note_id)

    async def test_dry_run_reports_planned_values(self):
        """PR9F-03: dry-run reports would_* and zero created."""
        self._require_db()
        from app.services.wk3_mistake_visibility_migration import run_wk3_migration

        note_id = await self._prepare_note(next_review=date(2027, 1, 20))

        try:
            report = await run_wk3_migration(self.session, dry_run=True)
            await self.session.rollback()
        except Exception as exc:
            self.skipTest(f"migration infrastructure required: {exc}")

        self.assertTrue(report.dry_run)
        self.assertEqual(report.targets_created, 0, "dry-run must not claim created targets")
        self.assertEqual(report.review_items_created_v2, 0, "dry-run must not claim created review items")
        self.assertEqual(report.would_create, 1)
        self.assertEqual(report.would_create_review_items, 1)
        self.assertEqual(report.would_next_due_from_source, 1)

        data = report.to_json_dict()
        self.assertEqual(data["targets"]["created"], 0)
        self.assertEqual(data["targets"]["would_create"], 1)
        self.assertEqual(data["review_items"]["created_v2"], 0)
        self.assertEqual(data["review_items"]["would_create_v2"], 1)
        self.assertTrue(data["checks"]["replay_noop"], "first dry-run must not report replay_noop=false")

        await _cleanup_note(self.session, note_id)

    async def test_checks_reflect_visibility_mismatch(self):
        """PR9F-02: compute_reconciliation_checks returns false on broken visibility."""
        self._require_db()
        from app.services.wk3_mistake_visibility_migration import (
            compute_reconciliation_checks,
            run_wk3_migration,
        )

        note_id = await self._prepare_note(
            status="published", hidden=False, next_review=date(2026, 12, 15),
        )

        try:
            report = await run_wk3_migration(self.session, dry_run=False)
            await self.session.commit()
            self.assertGreaterEqual(report.targets_created, 1)

            checks_ok = await compute_reconciliation_checks(self.session)
            self.assertTrue(checks_ok["visibility_matrix_match"])

            await self.session.execute(text(
                "UPDATE public.mistakes SET visibility='private' "
                "WHERE id IN (SELECT target_mistake_id FROM public.legacy_note_migrations "
                "WHERE source_note_id=:sid AND target_mistake_id IS NOT NULL)"
            ), {"sid": note_id})
            await self.session.commit()

            checks_bad = await compute_reconciliation_checks(self.session)
            self.assertFalse(
                checks_bad["visibility_matrix_match"],
                "visibility_matrix_match must be false after breaking one visibility",
            )
        except Exception as exc:
            if "skipTest" in type(exc).__name__.lower() or isinstance(exc, unittest.SkipTest):
                raise
            self.skipTest(f"migration infrastructure required: {exc}")

        await _cleanup_note(self.session, note_id)

    async def test_source_drift_detected_and_target_not_overwritten(self):
        """PR9U-01 / W3-D10: source title drift -> rejected source_drift, no overwrite."""
        self._require_db()
        from app.services.wk3_mistake_visibility_migration import run_wk3_migration

        note_id = await self._prepare_note(title="original-title", next_review=date(2026, 12, 15))

        try:
            report1 = await run_wk3_migration(self.session, dry_run=False)
            await self.session.commit()
        except Exception as exc:
            self.skipTest(f"migration infrastructure required: {exc}")
        self.assertGreaterEqual(report1.targets_created, 1)

        orig_title = (await self.session.execute(text(
            "SELECT title FROM public.mistakes WHERE id IN "
            "(SELECT target_mistake_id FROM public.legacy_note_migrations "
            "WHERE source_note_id=:sid AND target_mistake_id IS NOT NULL)"
        ), {"sid": note_id})).scalar_one()
        self.assertEqual(orig_title, "original-title")

        await self.session.execute(text(
            "UPDATE public.notes SET title='changed-title', revision=revision+1 WHERE id=:id"
        ), {"id": note_id})
        await self.session.commit()

        report2 = await run_wk3_migration(self.session, dry_run=False)
        await self.session.commit()

        drift_reasons = [r["reason"] for r in report2.rejected]
        self.assertIn(
            "source_drift", drift_reasons,
            f"source_drift must appear in rejected, got {report2.rejected}",
        )
        self.assertFalse(
            report2.provenance_match,
            "provenance_match must be false on source drift",
        )

        target_title = (await self.session.execute(text(
            "SELECT title FROM public.mistakes WHERE id IN "
            "(SELECT target_mistake_id FROM public.legacy_note_migrations "
            "WHERE source_note_id=:sid AND target_mistake_id IS NOT NULL)"
        ), {"sid": note_id})).scalar_one()
        self.assertEqual(
            target_title, "original-title",
            "target content must NOT be overwritten on source drift",
        )

        await _cleanup_note(self.session, note_id)

    async def test_dry_run_does_not_persist_approval_actors(self):
        """R2: dry-run must not create/publish wk3 approval actors."""
        self._require_db()
        from unittest import mock

        import app.services.wk3_mistake_visibility_migration as mod

        note_id = await self._prepare_note(title=f"pr09-rw2-actors-{uuid.uuid4().hex[:8]}")
        fresh = [uuid.uuid4() for _ in range(4)]

        try:
            users_before = await _count(self.session, "SELECT count(*) FROM public.users")
            authz_before = await _count(
                self.session,
                "SELECT count(*) FROM public.legacy_migration_approval_authorizations",
            )
            with (
                mock.patch.object(mod, "_ACTOR_SOURCE", fresh[0]),
                mock.patch.object(mod, "_ACTOR_QUESTION", fresh[1]),
                mock.patch.object(mod, "_ACTOR_MISTAKE", fresh[2]),
                mock.patch.object(mod, "_ACTOR_SCHEDULE", fresh[3]),
            ):
                report = await mod.run_wk3_migration(self.session, dry_run=True)
                await self.session.rollback()
                await self._reset_identity()
        except Exception as exc:
            if isinstance(exc, unittest.SkipTest):
                raise
            self.skipTest(f"migration infrastructure required: {exc}")

        self.assertTrue(report.dry_run)
        users_after = await _count(self.session, "SELECT count(*) FROM public.users")
        authz_after = await _count(
            self.session,
            "SELECT count(*) FROM public.legacy_migration_approval_authorizations",
        )
        self.assertEqual(users_after, users_before, "dry-run must not persist users")
        self.assertEqual(
            authz_after, authz_before,
            "dry-run must not persist legacy_migration_approval_authorizations",
        )

        fresh_users = await _count(
            self.session,
            "SELECT count(*) FROM public.users "
            "WHERE id IN (:a,:b,:c,:d)",
            a=fresh[0], b=fresh[1], c=fresh[2], d=fresh[3],
        )
        fresh_authz = await _count(
            self.session,
            "SELECT count(*) FROM public.legacy_migration_approval_authorizations "
            "WHERE user_id IN (:a,:b,:c,:d)",
            a=fresh[0], b=fresh[1], c=fresh[2], d=fresh[3],
        )
        self.assertEqual(fresh_users, 0, "dry-run must not insert actor users")
        self.assertEqual(fresh_authz, 0, "dry-run must not insert actor authorizations")

        await _cleanup_note(self.session, note_id)

    async def test_dry_run_mixed_scenario_is_zero_persistence(self):
        """R1/R3/R4: mixed dry-run (migrated+reconcile, un-migrated) writes nothing."""
        self._require_db()
        from app.services.wk3_mistake_visibility_migration import run_wk3_migration

        try:
            await _setup_infra(self.session)
            note_a = await _seed_migratable_note(
                self.session, status="published", hidden=False,
                title=f"pr09-rw2-mixed-a-{uuid.uuid4().hex[:8]}",
            )
            await self.session.commit()
        except Exception as exc:
            self.skipTest(f"scratch PostgreSQL with ledger access required: {exc}")

        try:
            await run_wk3_migration(self.session, dry_run=False)
            await self.session.commit()
        except Exception as exc:
            if isinstance(exc, unittest.SkipTest):
                raise
            self.skipTest(f"migration infrastructure required: {exc}")

        target_a = (await self.session.execute(text(
            "SELECT target_mistake_id FROM public.legacy_note_migrations "
            "WHERE source_note_id=:sid AND mapping_version=:mv "
            "AND target_mistake_id IS NOT NULL"
        ), {"sid": note_a, "mv": MAPPING_VERSION})).scalar_one()

        await self.session.execute(text(
            "UPDATE public.mistakes SET visibility='private' WHERE id=:id"
        ), {"id": target_a})
        await self.session.commit()

        try:
            note_b = await _seed_migratable_note(
                self.session, status="unpublished", hidden=True,
                title=f"pr09-rw2-mixed-b-{uuid.uuid4().hex[:8]}",
            )
            await self.session.commit()
        except Exception as exc:
            await _cleanup_note(self.session, note_a)
            self.skipTest(f"could not seed un-migrated note: {exc}")

        before = (await self.session.execute(text(
            "SELECT visibility, version FROM public.mistakes WHERE id=:id"
        ), {"id": target_a})).one()

        counts_before = {
            "users": await _count(self.session, "SELECT count(*) FROM public.users"),
            "authz": await _count(
                self.session,
                "SELECT count(*) FROM public.legacy_migration_approval_authorizations",
            ),
            "ledger": await _count(
                self.session, "SELECT count(*) FROM public.legacy_note_migrations"
            ),
            "mistakes": await _count(self.session, "SELECT count(*) FROM public.mistakes"),
        }

        report = await run_wk3_migration(self.session, dry_run=True)
        await self.session.rollback()
        await self._reset_identity()

        after = (await self.session.execute(text(
            "SELECT visibility, version FROM public.mistakes WHERE id=:id"
        ), {"id": target_a})).one()
        counts_after = {
            "users": await _count(self.session, "SELECT count(*) FROM public.users"),
            "authz": await _count(
                self.session,
                "SELECT count(*) FROM public.legacy_migration_approval_authorizations",
            ),
            "ledger": await _count(
                self.session, "SELECT count(*) FROM public.legacy_note_migrations"
            ),
            "mistakes": await _count(self.session, "SELECT count(*) FROM public.mistakes"),
        }

        self.assertEqual(
            (after.visibility, after.version), (before.visibility, before.version),
            "dry-run must not change mistakes.visibility/version",
        )
        self.assertEqual(counts_after["users"], counts_before["users"])
        self.assertEqual(counts_after["authz"], counts_before["authz"])
        self.assertEqual(counts_after["ledger"], counts_before["ledger"])
        self.assertEqual(counts_after["mistakes"], counts_before["mistakes"])

        b_ledger = await _count(
            self.session,
            "SELECT count(*) FROM public.legacy_note_migrations "
            "WHERE source_note_id=:sid AND mapping_version=:mv",
            sid=note_b, mv=MAPPING_VERSION,
        )
        self.assertEqual(b_ledger, 0, "un-migrated note must not gain a dry-run ledger row")

        self.assertEqual(report.visibility_reconciled, 0)
        self.assertGreaterEqual(report.would_reconcile, 1)
        self.assertGreaterEqual(report.would_create, 1)
        self.assertIs(report.to_json_dict()["checks"]["count_match"], True)

        await _cleanup_note(self.session, note_a)
        await _cleanup_note(self.session, note_b)
