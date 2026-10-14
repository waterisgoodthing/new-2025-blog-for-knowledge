"""B04 governed-catalog scope and versioned schema manifest.

The F04 gate must compare *definitions*, not merely object names. This module
defines the exact set of objects the catalog checker owns and loads the
version-controlled manifest that the checker compares against.

The manifest is NOT learned from the database under test. It is generated from
a clean, freshly migrated scratch instance (``python -m
app.models.schema_catalog_gate --write``) and committed; a new migration that
changes governed definitions must ship an explicit manifest diff.

Governed scope (W4 B04):

- every SQL-owned ``public`` table from migration 026 (``SQL_OWNED_TABLES``);
- the migration-026 ``legacy_migration`` schema tables and functions;
- the SQL-owned ``draft_items`` columns (type/nullable/default);
- the migration-033 ``webauthn_challenges`` table columns/constraints/indexes;
- migration-026 guard triggers and their enabled state.

ORM-managed tables outside this scope remain the ORM autogenerate gate's job.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from app.models.sql_owned import (
    SQL_OWNED_COLUMNS,
    SQL_OWNED_INDEXES,
    SQL_OWNED_TABLES,
    SQL_OWNED_TRIGGERS,
)

GOVERNED_SCHEMAS: frozenset[str] = frozenset({"legacy_migration"})
GOVERNED_EXTRA_TABLES: frozenset[str] = frozenset({"webauthn_challenges"})
GOVERNED_PARTIAL_COLUMNS: dict[str, frozenset[str]] = dict(SQL_OWNED_COLUMNS)
ALL_SCHEMAS: tuple[str, ...] = ("public", "legacy_migration")

MANIFEST_PATH = Path(__file__).with_name("schema_manifest.json")

MANIFEST_VERSION = 1

__all__ = [
    "ALL_SCHEMAS",
    "GOVERNED_EXTRA_TABLES",
    "GOVERNED_PARTIAL_COLUMNS",
    "GOVERNED_SCHEMAS",
    "MANIFEST_PATH",
    "MANIFEST_VERSION",
    "SQL_OWNED_INDEXES",
    "SQL_OWNED_TABLES",
    "SQL_OWNED_TRIGGERS",
    "is_governed_table",
    "load_manifest",
]


def is_governed_table(schema: str, table: str) -> bool:
    """Return True when a table belongs to the governed catalog scope."""
    if schema in GOVERNED_SCHEMAS:
        return True
    if table in SQL_OWNED_TABLES or table in GOVERNED_EXTRA_TABLES:
        return True
    return False


def governed_columns(schema: str, table: str, column: str) -> bool:
    """Return True when a column is explicitly part of the governed scope."""
    if schema in GOVERNED_SCHEMAS:
        return True
    if table in SQL_OWNED_TABLES or table in GOVERNED_EXTRA_TABLES:
        return True
    partial = GOVERNED_PARTIAL_COLUMNS.get(table)
    return bool(partial and column in partial and schema == "public")


@lru_cache(maxsize=1)
def load_manifest() -> dict:
    with MANIFEST_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)
