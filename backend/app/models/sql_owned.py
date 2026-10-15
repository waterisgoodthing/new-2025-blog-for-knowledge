"""F04 SQL-owned schema manifest (migration 026 / 033).

Migration 026 installs the governed legacy Note-migration contract directly in
SQL: six ``public`` tables, six ``draft_items`` columns, two indexes on
``legacy_note_migrations``, and the guard functions/triggers in the
``legacy_migration`` schema. These objects are intentionally NOT represented as
SQLAlchemy models (they are append-only, protected, and must never be dropped
by an autogenerate candidate).

``is_sql_owned_orm_object`` is the precise allowlist consumed by
``alembic/env.py``. It matches exact schema/table/column/index names only —
never a whole table class, ``*``, or "any reflected object" — so real drift on
any other table is still detected.

The same manifest is verified against the live PostgreSQL catalog by
``tests/test_f04_schema_ownership.py`` (type/nullable/unique/predicate checks),
so the exclusion is not a silent "ignore the alarm" switch.
"""

from __future__ import annotations

from typing import Any

from app.models.registry import EXCLUDED_SCHEMA_TABLES

LEGACY_MIGRATION_SCHEMA = "legacy_migration"

SQL_OWNED_TABLES: frozenset[str] = frozenset(
    {
        "legacy_note_migrations",
        "legacy_note_migration_events",
        "legacy_migration_approval_authorizations",
        "legacy_migration_rollback_admins",
        "legacy_migration_rollback_audits",
        "legacy_note_migration_rejections",
    }
)

SQL_OWNED_COLUMNS: dict[str, frozenset[str]] = {
    "draft_items": frozenset(
        {
            "source_hash",
            "approved_by",
            "approved_at",
            "conversion_sequence",
            "target_question_id",
            "target_mistake_id",
        }
    ),
}

SQL_OWNED_INDEXES: frozenset[str] = frozenset(
    {
        "idx_legacy_note_migrations_state",
        "idx_legacy_note_migrations_source_hash",
    }
)

SQL_OWNED_TRIGGERS: frozenset[str] = frozenset(
    {
        "trg_lnm_guard",
        "trg_lnm_event_guard",
        "trg_lnm_event_no_truncate",
        "trg_lnm_rollback_guard",
        "trg_lnm_rollback_no_truncate",
        "trg_lnm_rejection_guard",
        "trg_lnm_rejection_no_truncate",
    }
)


def _table_name(object_: Any) -> str | None:
    table = getattr(object_, "table", None)
    return getattr(table, "name", None)


def _schema_name(object_: Any) -> str | None:
    table = getattr(object_, "table", None)
    if table is not None:
        return getattr(table, "schema", None)
    return getattr(object_, "schema", None)


def _is_public_schema(schema: str | None) -> bool:
    # Reflected public objects may carry schema ``None`` (default search_path)
    # or ``"public"``; both are the SQL-owned namespace.
    return schema in (None, "public")


def is_sql_owned_orm_object(
    object_: Any,
    name: str | None,
    type_: str,
    reflected: bool,
    compare_to: Any,
) -> bool:
    """Return True when ``object_`` is an explicitly SQL-owned object.

    Strict matching: only *reflected* database objects (never model-side
    declarations), only the exact schema/type/parent-table/name, and only when
    there is no metadata counterpart to compare (``compare_to is None``). Any
    wider match would hide real drift.
    """
    if not reflected or compare_to is not None:
        return False

    schema = _schema_name(object_)

    if type_ == "table":
        return name in SQL_OWNED_TABLES and _is_public_schema(schema)

    if type_ == "index":
        if name in SQL_OWNED_INDEXES and _is_public_schema(schema):
            return True
        child_schema = getattr(getattr(object_, "table", None), "schema", None)
        return _table_name(object_) in SQL_OWNED_TABLES and _is_public_schema(child_schema)

    if type_ == "column":
        if not _is_public_schema(schema):
            return False
        table = _table_name(object_)
        partial = SQL_OWNED_COLUMNS.get(table or "")
        return bool(partial and name in partial)

    # Constraints/indexes attached to a wholly SQL-owned table are implied by
    # that table's exclusion; keep them out of the candidate too.
    if type_ in {
        "index",
        "unique_constraint",
        "foreign_key_constraint",
        "check_constraint",
        "primary_key_constraint",
    }:
        return _table_name(object_) in SQL_OWNED_TABLES and _is_public_schema(schema)

    return False


def include_object(object_: Any, name: str | None, type_: str, reflected: bool, compare_to: Any) -> bool:
    """Alembic autogenerate filter.

    Excludes the Phase-C guest tables (own governance) and the F04 SQL-owned
    manifest objects. Everything else is compared normally.
    """
    if type_ == "table" and name in EXCLUDED_SCHEMA_TABLES:
        return False

    if type_ == "index":
        table = getattr(object_, "table", None)
        if table is not None and table.name in EXCLUDED_SCHEMA_TABLES:
            return False

    if is_sql_owned_orm_object(object_, name, type_, reflected, compare_to):
        return False

    return True
