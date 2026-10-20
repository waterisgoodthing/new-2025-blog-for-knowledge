"""F04 schema-ownership dual gate.

1. ORM-managed: alembic ``compare_metadata`` reports no unexplained diff.
2. SQL-managed: the migration-026 manifest objects exist in the live catalog
   with the expected shape, and a deliberate removal is detected (not silently
   ignored by the autogenerate allowlist).
"""

from __future__ import annotations

import asyncio
from types import SimpleNamespace

from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from app.database import engine
from app.models.registry import SCHEMA_LIFECYCLE_METADATA
from app.models.sql_owned import (
    SQL_OWNED_COLUMNS,
    SQL_OWNED_INDEXES,
    SQL_OWNED_TABLES,
    SQL_OWNED_TRIGGERS,
    include_object,
    is_sql_owned_orm_object,
)

WEB_AUTHN_INDEX_PREDICATES = {
    "idx_webauthn_challenges_purpose_session": "session_id IS NOT NULL",
    "idx_webauthn_challenges_purpose_user": "user_id IS NOT NULL",
    "idx_webauthn_challenges_expires": "consumed_at IS NULL",
    "idx_webauthn_challenges_challenge_hash": None,
}


# ---------------------------------------------------------------------------
# Pure allowlist behavior
# ---------------------------------------------------------------------------


def test_sql_owned_tables_and_indexes_are_excluded() -> None:
    assert is_sql_owned_orm_object(SimpleNamespace(), "legacy_note_migrations", "table", True, None)
    assert is_sql_owned_orm_object(SimpleNamespace(), "idx_legacy_note_migrations_state", "index", True, None)


def test_sql_owned_draft_columns_are_excluded() -> None:
    column = SimpleNamespace(table=SimpleNamespace(name="draft_items"))
    assert is_sql_owned_orm_object(column, "source_hash", "column", True, None)
    assert is_sql_owned_orm_object(column, "target_mistake_id", "column", True, None)


def test_unrelated_objects_are_not_excluded() -> None:
    assert not is_sql_owned_orm_object(SimpleNamespace(), "webauthn_challenges", "table", True, None)
    assert not is_sql_owned_orm_object(
        SimpleNamespace(table=SimpleNamespace(name="draft_items")), "my_answer", "column", True, None
    )
    assert include_object(
        SimpleNamespace(table=SimpleNamespace(name="webauthn_challenges")),
        "idx_webauthn_challenges_challenge_hash",
        "index",
        True,
        None,
    )


# ---------------------------------------------------------------------------
# Catalog manifest gate
# ---------------------------------------------------------------------------


async def _missing_manifest_objects(conn: AsyncConnection) -> list[str]:
    missing: list[str] = []

    for table in sorted(SQL_OWNED_TABLES):
        found = await conn.scalar(
            text(
                "SELECT 1 FROM information_schema.tables "
                "WHERE table_schema='public' AND table_name=:t"
            ),
            {"t": table},
        )
        if found != 1:
            missing.append(f"table {table}")

    for table, columns in SQL_OWNED_COLUMNS.items():
        rows = await conn.execute(
            text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_schema='public' AND table_name=:t"
            ),
            {"t": table},
        )
        present = {row[0] for row in rows}
        for column in sorted(columns):
            if column not in present:
                missing.append(f"column {table}.{column}")

    for index in sorted(SQL_OWNED_INDEXES):
        found = await conn.scalar(
            text("SELECT 1 FROM pg_indexes WHERE schemaname='public' AND indexname=:n"),
            {"n": index},
        )
        if found != 1:
            missing.append(f"index {index}")

    for trigger in sorted(SQL_OWNED_TRIGGERS):
        found = await conn.scalar(
            text("SELECT 1 FROM pg_trigger WHERE tgname=:n AND NOT tgisinternal"),
            {"n": trigger},
        )
        if found != 1:
            missing.append(f"trigger {trigger}")

    for index, predicate in WEB_AUTHN_INDEX_PREDICATES.items():
        row = await conn.scalar(
            text("SELECT indexdef FROM pg_indexes WHERE schemaname='public' AND indexname=:n"),
            {"n": index},
        )
        if row is None:
            missing.append(f"index {index}")
        elif predicate is not None and predicate not in row:
            missing.append(f"index {index} predicate")

    return missing


async def _orm_diff(conn: AsyncConnection):
    def compare(sync_conn):
        context = MigrationContext.configure(sync_conn, opts={"include_object": include_object})
        return compare_metadata(context, SCHEMA_LIFECYCLE_METADATA)

    return await conn.run_sync(compare)


async def _exercise_dual_gate() -> None:
    try:
        async with engine.connect() as conn:
            await _dual_gate_body(conn)
    finally:
        await engine.dispose()


async def _dual_gate_body(conn: AsyncConnection) -> None:
    trans = await conn.begin()
    try:
        # 1. clean catalog satisfies the SQL-owned manifest
        assert await _missing_manifest_objects(conn) == []
        # 2. no unexplained ORM drift
        assert await _orm_diff(conn) == []

        # 3. negative: dropping a SQL-owned index is detected
        await conn.execute(text("DROP INDEX public.idx_legacy_note_migrations_state"))
        assert "index idx_legacy_note_migrations_state" in await _missing_manifest_objects(conn)

        # 4. negative: dropping an ORM-managed index is detected by autogenerate
        #    (the index is still in metadata, so it is reported as an add_index)
        await conn.execute(text("DROP INDEX public.idx_webauthn_challenges_challenge_hash"))
        diff = await _orm_diff(conn)
        assert any(
            entry[0] == "add_index" and entry[1].name == "idx_webauthn_challenges_challenge_hash"
            for entry in diff
        ), diff
    finally:
        await trans.rollback()


def test_schema_ownership_dual_gate() -> None:
    asyncio.run(_exercise_dual_gate())
