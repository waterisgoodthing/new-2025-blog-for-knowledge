"""B04 definition-comparing catalog gate (EV03 remediation).

``alembic check`` only compares ORM metadata and cannot see changes inside
SQL-owned objects: it missed an ``integer -> bigint`` column change, a dropped
CHECK constraint and a disabled guard trigger (EV03). This checker reads the
live ``pg_catalog`` and compares normalized *definitions* (type/length,
nullable, server default; PK/UNIQUE/FK/CHECK definitions with actions and
validation state; index expressions/order/uniqueness/partial predicate;
function signature/body/security/search_path; trigger binding/events/enabled)
against the versioned manifest in ``schema_manifest.json``.

It is an independent command, not a pytest helper::

    python -m app.models.schema_catalog_gate            # check (exit 1 on drift)
    python -m app.models.schema_catalog_gate --write    # regenerate manifest

Only the governed scope from ``schema_manifest.py`` is compared. Objects outside
the manifest but inside the governed namespace are reported as unexpected and
never auto-removed.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from app.models.schema_manifest import (
    ALL_SCHEMAS,
    MANIFEST_PATH,
    MANIFEST_VERSION,
    governed_columns,
    is_governed_table,
    load_manifest,
)

_SCHEMA_FILTER = ", ".join(f"'{schema}'" for schema in ALL_SCHEMAS)


async def _rows(conn: AsyncConnection, sql: str) -> list[Any]:
    return list((await conn.execute(text(sql))).all())


def _text(value: Any) -> Any:
    """Normalize asyncpg's internal "char" columns (bytes) to str."""
    if isinstance(value, (bytes, bytearray)):
        return value.decode()
    return value


async def _collect_columns(conn: AsyncConnection) -> dict[str, dict]:
    result: dict[str, dict] = {}
    rows = await _rows(
        conn,
        f"""
        SELECT n.nspname, c.relname, a.attname,
               format_type(a.atttypid, a.atttypmod) AS formatted_type,
               a.attnotnull,
               pg_get_expr(ad.adbin, ad.adrelid) AS default_expr
        FROM pg_attribute a
        JOIN pg_class c ON c.oid = a.attrelid
        JOIN pg_namespace n ON n.oid = c.relnamespace
        LEFT JOIN pg_attrdef ad ON ad.adrelid = a.attrelid AND ad.adnum = a.attnum
        WHERE a.attnum > 0 AND NOT a.attisdropped
          AND c.relkind IN ('r', 'p')
          AND n.nspname IN ({_SCHEMA_FILTER})
        ORDER BY n.nspname, c.relname, a.attnum
        """,
    )
    for schema, table, column, formatted_type, notnull, default_expr in rows:
        if not governed_columns(schema, table, column):
            continue
        result[f"{schema}.{table}.{column}"] = {
            "type": formatted_type,
            "notnull": bool(notnull),
            "default": default_expr,
        }
    return result


async def _collect_constraints(conn: AsyncConnection) -> dict[str, dict]:
    result: dict[str, dict] = {}
    rows = await _rows(
        conn,
        f"""
        SELECT n.nspname, cl.relname, con.conname, con.contype,
               pg_get_constraintdef(con.oid, true) AS definition,
               con.convalidated
        FROM pg_constraint con
        JOIN pg_class cl ON cl.oid = con.conrelid
        JOIN pg_namespace n ON n.oid = cl.relnamespace
        WHERE n.nspname IN ({_SCHEMA_FILTER})
          AND con.contype IN ('c', 'f', 'p', 'u')
        ORDER BY n.nspname, cl.relname, con.conname
        """,
    )
    for schema, table, name, contype, definition, validated in rows:
        if not is_governed_table(schema, table):
            continue
        result[f"{schema}.{name}"] = {
            "table": f"{schema}.{table}",
            "kind": _text(contype),
            "definition": " ".join(str(definition).split()),
            "validated": bool(validated),
        }
    return result


async def _collect_indexes(conn: AsyncConnection) -> dict[str, dict]:
    result: dict[str, dict] = {}
    rows = await _rows(
        conn,
        f"""
        SELECT n.nspname, ct.relname, ci.relname,
               pg_get_indexdef(ci.oid) AS definition,
               i.indisunique, i.indisvalid,
               pg_get_expr(i.indpred, i.indrelid) AS predicate
        FROM pg_index i
        JOIN pg_class ci ON ci.oid = i.indexrelid
        JOIN pg_class ct ON ct.oid = i.indrelid
        JOIN pg_namespace n ON n.oid = ci.relnamespace
        WHERE n.nspname IN ({_SCHEMA_FILTER})
          AND ct.relkind IN ('r', 'p')
        ORDER BY n.nspname, ct.relname, ci.relname
        """,
    )
    for schema, table, name, definition, unique, valid, predicate in rows:
        if not is_governed_table(schema, table):
            continue
        result[f"{schema}.{name}"] = {
            "table": f"{schema}.{table}",
            "definition": " ".join(str(definition).split()),
            "unique": bool(unique),
            "valid": bool(valid),
            "predicate": " ".join(str(predicate).split()) if predicate else None,
        }
    return result


async def _collect_functions(conn: AsyncConnection) -> dict[str, dict]:
    result: dict[str, dict] = {}
    rows = await _rows(
        conn,
        f"""
        SELECT n.nspname, p.proname,
               pg_get_function_identity_arguments(p.oid) AS identity_args,
               pg_get_function_result(p.oid) AS result,
               l.lanname,
               p.prosecdef,
               p.proconfig,
               pg_get_functiondef(p.oid) AS definition
        FROM pg_proc p
        JOIN pg_namespace n ON n.oid = p.pronamespace
        JOIN pg_language l ON l.oid = p.prolang
        WHERE n.nspname = 'legacy_migration'
        ORDER BY n.nspname, p.proname, identity_args
        """,
    )
    for schema, name, identity_args, result_type, language, secdef, config, definition in rows:
        key = f"{schema}.{name}({identity_args})"
        result[key] = {
            "result": result_type,
            "language": language,
            "security_definer": bool(secdef),
            "config": list(config) if config else [],
            "definition": str(definition),
        }
    return result


async def _collect_triggers(conn: AsyncConnection) -> dict[str, dict]:
    result: dict[str, dict] = {}
    rows = await _rows(
        conn,
        f"""
        SELECT n.nspname, c.relname, t.tgname,
               pg_get_triggerdef(t.oid, true) AS definition,
               t.tgenabled,
               pn.nspname, p.proname
        FROM pg_trigger t
        JOIN pg_class c ON c.oid = t.tgrelid
        JOIN pg_namespace n ON n.oid = c.relnamespace
        JOIN pg_proc p ON p.oid = t.tgfoid
        JOIN pg_namespace pn ON pn.oid = p.pronamespace
        WHERE NOT t.tgisinternal
          AND n.nspname IN ({_SCHEMA_FILTER})
        ORDER BY n.nspname, c.relname, t.tgname
        """,
    )
    for schema, table, name, definition, enabled, fn_schema, fn_name in rows:
        if not is_governed_table(schema, table):
            continue
        result[f"{schema}.{name}"] = {
            "table": f"{schema}.{table}",
            "function": f"{fn_schema}.{fn_name}",
            "enabled": _text(enabled),
            "definition": " ".join(str(definition).split()),
        }
    return result


async def collect_catalog(conn: AsyncConnection) -> dict:
    """Return the normalized governed catalog (without the revision stamp)."""
    return {
        "manifest_version": MANIFEST_VERSION,
        "columns": await _collect_columns(conn),
        "constraints": await _collect_constraints(conn),
        "indexes": await _collect_indexes(conn),
        "functions": await _collect_functions(conn),
        "triggers": await _collect_triggers(conn),
    }


async def current_revision(conn: AsyncConnection) -> str | None:
    return await conn.scalar(text("SELECT version_num FROM alembic_version"))


def diff_manifest(expected: dict, actual: dict) -> list[str]:
    """Return human-readable drift entries between two normalized catalogs."""
    errors: list[str] = []
    if expected.get("revision") != actual.get("revision"):
        errors.append(
            f"revision: manifest={expected.get('revision')!r} db={actual.get('revision')!r}"
        )
    for section in ("columns", "constraints", "indexes", "functions", "triggers"):
        expected_section = expected.get(section, {})
        actual_section = actual.get(section, {})
        for key in sorted(set(expected_section) | set(actual_section)):
            if key not in actual_section:
                errors.append(f"{section}: missing {key}")
                continue
            if key not in expected_section:
                errors.append(f"{section}: unexpected {key}")
                continue
            if expected_section[key] != actual_section[key]:
                errors.append(
                    f"{section}: changed {key}\n"
                    f"    expected={json.dumps(expected_section[key], sort_keys=True)}\n"
                    f"    actual  ={json.dumps(actual_section[key], sort_keys=True)}"
                )
    return errors


async def catalog_gate_errors(conn: AsyncConnection, expected: dict | None = None) -> list[str]:
    if expected is None:
        expected = load_manifest()
    actual = await collect_catalog(conn)
    actual["revision"] = await current_revision(conn)
    return diff_manifest(expected, actual)


async def _write_manifest(conn: AsyncConnection) -> None:
    manifest = await collect_catalog(conn)
    manifest["revision"] = await current_revision(conn)
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {MANIFEST_PATH} (revision={manifest['revision']})")


async def _amain(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="B04 governed catalog gate")
    parser.add_argument("--write", action="store_true", help="regenerate the manifest")
    args = parser.parse_args(argv)

    from app.database import engine

    try:
        async with engine.connect() as conn:
            if args.write:
                await _write_manifest(conn)
                return 0
            errors = await catalog_gate_errors(conn)
    finally:
        await engine.dispose()

    if errors:
        print("CATALOG GATE FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("catalog gate passed: governed definitions match the manifest")
    return 0


def main(argv: list[str] | None = None) -> int:
    return asyncio.run(_amain(list(sys.argv[1:] if argv is None else argv)))


if __name__ == "__main__":
    raise SystemExit(main())
