"""B04/EV03: the catalog gate must compare definitions, not just names.

Reproduces the three false-negative counterexamples from the execution
verification (integer->bigint, dropped CHECK, disabled guard trigger) plus the
additional shape/definition cases, and proves each is reported. Every probe runs
in its own transaction and is rolled back, and the final re-check on the clean
catalog passes.
"""

from __future__ import annotations

import asyncio

from sqlalchemy import text

from app.database import engine
from app.models.schema_catalog_gate import catalog_gate_errors


async def _gate_errors() -> list[str]:
    async with engine.connect() as conn:
        trans = await conn.begin()
        try:
            return await catalog_gate_errors(conn)
        finally:
            await trans.rollback()


async def _probe(sql: str, expected_token: str) -> None:
    async with engine.connect() as conn:
        trans = await conn.begin()
        try:
            for statement in sql.strip().split(";\n"):
                statement = statement.strip()
                if statement:
                    await conn.execute(text(statement))
            errors = await catalog_gate_errors(conn)
            assert any(expected_token in error for error in errors), (
                f"gate missed {expected_token!r}: {errors}"
            )
        finally:
            await trans.rollback()


async def _exercise() -> None:
    try:
        # baseline: clean catalog matches the manifest
        assert await _gate_errors() == []

        # EV03 #1: integer -> bigint on a SQL-owned draft column
        await _probe(
            "ALTER TABLE public.draft_items ALTER COLUMN conversion_sequence TYPE bigint",
            "public.draft_items.conversion_sequence",
        )
        # EV03 #2: dropped webauthn purpose CHECK
        await _probe(
            "ALTER TABLE public.webauthn_challenges DROP CONSTRAINT ck_webauthn_challenges_purpose",
            "constraints: missing public.ck_webauthn_challenges_purpose",
        )
        # EV03 #3: disabled guard trigger
        await _probe(
            "ALTER TABLE public.legacy_note_migrations DISABLE TRIGGER trg_lnm_guard",
            "public.trg_lnm_guard",
        )
        # column default / nullable shape change
        await _probe(
            "ALTER TABLE public.draft_items ALTER COLUMN source_hash SET DEFAULT 'x'",
            "public.draft_items.source_hash",
        )
        # same-name index definition change
        await _probe(
            """
DROP INDEX public.idx_legacy_note_migrations_state;
CREATE INDEX idx_legacy_note_migrations_state ON public.legacy_note_migrations (state, id)
""",
            "public.idx_legacy_note_migrations_state",
        )
        # function body change
        await _probe(
            """
CREATE OR REPLACE FUNCTION legacy_migration.legacy_uuid_or_null(p_value text)
RETURNS uuid LANGUAGE sql AS $$ SELECT NULL::uuid $$;
""",
            "legacy_migration.legacy_uuid_or_null",
        )
        # FK action change (drop + recreate with CASCADE instead of RESTRICT)
        await _probe(
            """
ALTER TABLE public.legacy_note_migrations DROP CONSTRAINT fk_lnm_source_approval_event;
ALTER TABLE public.legacy_note_migrations ADD CONSTRAINT fk_lnm_source_approval_event FOREIGN KEY (source_approval_event_id) REFERENCES public.legacy_note_migration_events (id) ON DELETE CASCADE
""",
            "public.fk_lnm_source_approval_event",
        )
        # unexpected governed object must be reported, never auto-removed
        await _probe(
            """
CREATE TRIGGER b04_probe_trigger AFTER INSERT ON public.legacy_note_migrations FOR EACH ROW EXECUTE FUNCTION legacy_migration.guard_legacy_note_migration()
""",
            "triggers: unexpected public.b04_probe_trigger",
        )

        # clean catalog is unchanged after all rollbacks
        assert await _gate_errors() == []
    finally:
        await engine.dispose()


def test_catalog_gate_detects_definition_drift() -> None:
    asyncio.run(_exercise())
