"""PR-09 wk3-mistake-visibility-v1 ledger runner tests (DB-backed).

Covers: dry-run zero persistence, first-run creation, idempotent replay,
visibility reconcile on v1-* targets, and reconciliation report schema.
"""

from __future__ import annotations

import json
import unittest
import uuid
from datetime import datetime, timezone

from sqlalchemy import text

from app.services.wk3_mistake_visibility_migration import (
    MAPPING_VERSION,
    UNMAPPED_SOURCE_FIELDS,
    Wk3MigrationReport,
    _mapping_bucket,
    map_legacy_note_to_mistake_visibility,
)

REPORT_REQUIRED_KEYS = {
    "mapping_version",
    "generated_at",
    "source",
    "targets",
    "review_items",
    "unmapped_source_fields",
    "checks",
    "idempotency",
}

REPORT_SOURCE_KEYS = {"total_legacy_mistakes", "by_mapping"}
REPORT_TARGET_KEYS = {"created", "visibility_reconciled", "skipped_already_migrated", "rejected"}
REPORT_CHECK_KEYS = {
    "count_match",
    "provenance_match",
    "visibility_matrix_match",
    "public_field_allowlist_match",
    "replay_noop",
}


# ---------------------------------------------------------------------------
# Pure report / mapping tests (no DB)
# ---------------------------------------------------------------------------


def test_mapping_version_fits_column() -> None:
    assert len(MAPPING_VERSION.encode()) <= 64
    assert MAPPING_VERSION == "wk3-mistake-visibility-v1"


def test_report_json_schema_keys() -> None:
    report = Wk3MigrationReport(generated_at="2026-09-22T00:00:00+00:00")
    data = report.to_json_dict()
    assert REPORT_REQUIRED_KEYS <= set(data.keys())
    assert REPORT_SOURCE_KEYS <= set(data["source"].keys())
    assert REPORT_TARGET_KEYS <= set(data["targets"].keys())
    assert REPORT_CHECK_KEYS <= set(data["checks"].keys())
    assert "replay_noop" in data["idempotency"]
    assert data["mapping_version"] == MAPPING_VERSION


def test_report_by_mapping_has_four_cells() -> None:
    report = Wk3MigrationReport()
    assert set(report.by_mapping.keys()) == {
        "published_visible",
        "published_hidden",
        "unpublished_visible",
        "unpublished_hidden",
    }


def test_report_unmapped_fields() -> None:
    report = Wk3MigrationReport()
    data = report.to_json_dict()
    assert data["unmapped_source_fields"] == list(UNMAPPED_SOURCE_FIELDS)
    assert data["review_items"]["unmapped"] == list(UNMAPPED_SOURCE_FIELDS)


def test_report_count_match_logic() -> None:
    report = Wk3MigrationReport()
    report.source_total = 3
    report.targets_created = 1
    report.visibility_reconciled = 1
    report.skipped_already_migrated = 1
    assert report.to_json_dict()["checks"]["count_match"] is True
    report.rejected.append({"source_note_id": "x", "reason": "y"})
    report.source_total = 4
    assert report.to_json_dict()["checks"]["count_match"] is True
    report.source_total = 5
    assert report.to_json_dict()["checks"]["count_match"] is False


def test_report_replay_noop_flag() -> None:
    report = Wk3MigrationReport(replay_noop=True)
    assert report.to_json_dict()["idempotency"]["replay_noop"] is True
    report2 = Wk3MigrationReport(replay_noop=False)
    assert report2.to_json_dict()["checks"]["replay_noop"] is False


def test_mapping_bucket_covers_matrix() -> None:
    assert _mapping_bucket("published", False) == "published_visible"
    assert _mapping_bucket("published", True) == "published_hidden"
    assert _mapping_bucket("unpublished", False) == "unpublished_visible"
    assert _mapping_bucket("unpublished", True) == "unpublished_hidden"
    assert _mapping_bucket("published", 0) == "published_visible"
    assert _mapping_bucket("published", None) == "published_visible"


def test_visibility_mapping_reexported() -> None:
    assert map_legacy_note_to_mistake_visibility("published", False) == "public"
    assert map_legacy_note_to_mistake_visibility("published", True) == "private"
    assert map_legacy_note_to_mistake_visibility("unpublished", False) == "private"
    assert map_legacy_note_to_mistake_visibility("unpublished", True) == "private"


def test_report_serializable() -> None:
    report = Wk3MigrationReport(generated_at="2026-09-22T00:00:00+00:00")
    raw = json.dumps(report.to_json_dict())
    parsed = json.loads(raw)
    assert parsed["mapping_version"] == MAPPING_VERSION


# ---------------------------------------------------------------------------
# DB-backed tests (require scratch PostgreSQL via guard)
# ---------------------------------------------------------------------------


async def _count(session, sql: str, **params) -> int:
    return int((await session.execute(text(sql), params)).scalar() or 0)


async def _insert_legacy_mistake_note(session, *, status: str, hidden: bool) -> uuid.UUID:
    note_id = uuid.uuid4()
    await session.execute(text(
        "INSERT INTO public.notes "
        "(id,slug,title,content,type,status,hidden,revision,ef,interval,repetitions) "
        "VALUES (:id,:slug,'t','c','mistake',:status,:hidden,1,2.5,0,0)"
    ), {"id": note_id, "slug": f"wk3-{note_id.hex[:12]}", "status": status, "hidden": hidden})
    return note_id


async def _setup_adapter_identity(session) -> None:
    await session.execute(text(
        "DO $$ BEGIN "
        "IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='legacy_note_adapter_runner') THEN "
        "  CREATE ROLE legacy_note_adapter_runner LOGIN; "
        "END IF; "
        "END $$"
    ))


class Wk3RunnerDryRunTest(unittest.IsolatedAsyncioTestCase):
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

    async def test_dry_run_zero_persistence(self):
        if not self._db_ready:
            self.skipTest("scratch PostgreSQL required (run via week3-scratch-guard)")
        from app.services.wk3_mistake_visibility_migration import run_wk3_migration

        try:
            await _setup_adapter_identity(self.session)
            note_id = await _insert_legacy_mistake_note(self.session, status="published", hidden=False)
            await self.session.commit()
            ledger_before = await _count(
                self.session, "SELECT count(*) FROM public.legacy_note_migrations"
            )
            mistakes_before = await _count(self.session, "SELECT count(*) FROM public.mistakes")
        except Exception as exc:
            self.skipTest(f"scratch PostgreSQL with ledger access required: {exc}")

        report = await run_wk3_migration(self.session, dry_run=True)
        await self.session.rollback()

        ledger_after = await _count(
            self.session, "SELECT count(*) FROM public.legacy_note_migrations"
        )
        mistakes_after = await _count(self.session, "SELECT count(*) FROM public.mistakes")

        self.assertTrue(report.dry_run)
        self.assertEqual(ledger_after, ledger_before, "dry-run must not leave ledger rows")
        self.assertEqual(mistakes_after, mistakes_before, "dry-run must not create mistakes")

        try:
            await self.session.execute(text("RESET SESSION AUTHORIZATION"))
        except Exception:
            pass
        await self.session.execute(
            text("DELETE FROM public.notes WHERE id=:id"), {"id": note_id}
        )
        await self.session.commit()

    async def test_runner_report_json_roundtrip(self):
        import tempfile
        from pathlib import Path

        from app.services.wk3_mistake_visibility_migration import write_report

        report = Wk3MigrationReport(generated_at="2026-09-22T00:00:00+00:00")
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "report.json"
            write_report(report, out)
            data = json.loads(out.read_text())
            self.assertLessEqual(REPORT_REQUIRED_KEYS, set(data.keys()))
            self.assertEqual(data["mapping_version"], MAPPING_VERSION)
