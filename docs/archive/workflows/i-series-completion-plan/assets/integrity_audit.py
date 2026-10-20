#!/usr/bin/env python3
"""C6/C7 read-only integrity audit for an Alembic revision-024 database."""

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import manifest_tool


EXPECTED_AGGREGATE = "b40b109a0a1a7eca9b633a11503f8327c8c051fa0b4f05fb0efa04a79089adb6"
EXPECTED_OWNER = "4c503215-b158-4162-b472-79df8289ed0a"
EXPECTED_REVISION = "024"
EXPECTED_SOURCE_COUNT = 121


@dataclass(frozen=True)
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    user: str = "blog_user"
    database: str = "blog_db"


class ReadOnlyDatabase:
    def __init__(self, config: DatabaseConfig):
        self.config = config

    def query(self, sql: str) -> list[str]:
        command = [
            "psql",
            "-h",
            self.config.host,
            "-p",
            str(self.config.port),
            "-U",
            self.config.user,
            "-d",
            self.config.database,
            "-X",
            "-v",
            "ON_ERROR_STOP=1",
            "-A",
            "-t",
            "-F",
            "\t",
            "-c",
            f"BEGIN READ ONLY; {sql} COMMIT;",
        ]
        completed = subprocess.run(command, check=True, capture_output=True, text=True)
        return [line for line in completed.stdout.splitlines() if line not in {"BEGIN", "COMMIT", ""}]


def _single_value(database: ReadOnlyDatabase, sql: str) -> str:
    rows = database.query(sql)
    if len(rows) != 1:
        raise RuntimeError(f"Expected one query result, found {len(rows)}")
    return rows[0]


def _source_revision(database: ReadOnlyDatabase) -> str:
    return _single_value(database, "SELECT version_num FROM alembic_version;")


def _canonical_owner(database: ReadOnlyDatabase) -> str:
    return _single_value(
        database,
        "SELECT id::text FROM users WHERE is_admin IS TRUE ORDER BY id LIMIT 1;",
    )


def _read_source_rows(database: ReadOnlyDatabase, projection) -> dict[str, list[tuple[str, str]]]:
    branches = [
        f"SELECT '{table}'::text AS source_table, id::text AS source_id, "
        f"{manifest_tool._row_json_expression(table, projection)}::text AS row_data "
        f"FROM public.{table} AS t"
        for table in manifest_tool.SOURCE_TABLES
    ]
    lines = database.query(
        "SELECT source_table, source_id, row_data FROM ("
        + " UNION ALL ".join(branches)
        + ") AS source_rows ORDER BY source_table, source_id;"
    )
    source_rows = {table: [] for table in manifest_tool.SOURCE_TABLES}
    for line in lines:
        table, source_id, raw_json = line.split("\t", 2)
        source_rows[table].append((source_id, raw_json))
    return source_rows


def verify_manifest(database: ReadOnlyDatabase, manifest: dict) -> dict:
    database_revision = _source_revision(database)
    manifest_revision = manifest["source_revision"]
    projection = manifest_tool.resolve_revision_projection(manifest_revision, database_revision)
    source_rows = _read_source_rows(database, projection)
    report = manifest_tool.verify_manifest_rows(manifest, source_rows)
    current_manifest = manifest_tool.build_manifest(
        source_rows,
        canonical_owner=manifest["canonical_owner_id"],
        source_revision=manifest_revision,
        generated_at=manifest["generated_at"],
    )
    report["source_aggregate_sha256"] = current_manifest["source_aggregate_sha256"]
    report["source_aggregate_matches"] = (
        report["source_aggregate_sha256"] == manifest["source_aggregate_sha256"] == EXPECTED_AGGREGATE
    )
    report["manifest_source_revision"] = manifest_revision
    report["database_revision_actual"] = database_revision
    report["projection_applied"] = bool(projection)
    report["passed"] = bool(
        report["passed"]
        and report["source_count"] == EXPECTED_SOURCE_COUNT
        and report["manifest_count"] == EXPECTED_SOURCE_COUNT
        and report["source_aggregate_matches"]
    )
    return report


def check_fk_integrity(database: ReadOnlyDatabase) -> dict[str, int]:
    # Reuse the exact C1 relationship contract against the selected database.
    original_psql = manifest_tool._psql
    manifest_tool._psql = database.query
    try:
        return manifest_tool._relationship_orphans()
    finally:
        manifest_tool._psql = original_psql


def check_backfill_correctness(database: ReadOnlyDatabase) -> dict[str, int]:
    return {
        "notes_revision_null": int(
            _single_value(database, "SELECT count(*) FROM notes WHERE revision IS NULL;")
        ),
        "notes_revision_min": int(
            _single_value(database, "SELECT coalesce(min(revision), 0) FROM notes;")
        ),
        "attachments_display_name_null": int(
            _single_value(
                database,
                "SELECT count(*) FROM attachments WHERE nullif(btrim(display_name), '') IS NULL;",
            )
        ),
        "attachments_display_name_mismatch": int(
            _single_value(
                database,
                "SELECT count(*) FROM attachments WHERE display_name IS DISTINCT FROM original_name;",
            )
        ),
        "attachments_folder_id_null": int(
            _single_value(database, "SELECT count(*) FROM attachments WHERE folder_id IS NULL;")
        ),
    }


def get_source_facts(database: ReadOnlyDatabase) -> dict:
    table_counts = {
        table: int(_single_value(database, f"SELECT count(*) FROM public.{table};"))
        for table in manifest_tool.SOURCE_TABLES
    }
    return {
        "table_counts": table_counts,
        "extensions": database.query("SELECT extname FROM pg_extension ORDER BY extname;"),
        "canonical_owner": _canonical_owner(database),
        "admin_count": int(
            _single_value(database, "SELECT count(*) FROM users WHERE is_admin IS TRUE;")
        ),
        "total_users": int(_single_value(database, "SELECT count(*) FROM users;")),
    }


def evaluate_audit(facts: dict) -> dict:
    report = dict(facts)
    report["fk_orphan_count"] = sum(report["fk_integrity"].values())
    manifest = report["manifest_verification"]
    backfill = report["backfill_verification"]
    source = report["source_facts"]
    report["passed"] = bool(
        report["source_revision"] == EXPECTED_REVISION
        and manifest["passed"]
        and manifest["source_count"] == EXPECTED_SOURCE_COUNT
        and manifest["manifest_count"] == EXPECTED_SOURCE_COUNT
        and manifest["source_aggregate_matches"]
        and report["fk_orphan_count"] == 0
        and backfill["notes_revision_null"] == 0
        and backfill["notes_revision_min"] >= 1
        and backfill["attachments_display_name_null"] == 0
        and backfill["attachments_display_name_mismatch"] == 0
        and sum(source["table_counts"].values()) == EXPECTED_SOURCE_COUNT
        and {"pg_trgm", "plpgsql"}.issubset(source["extensions"])
        and source["canonical_owner"] == EXPECTED_OWNER
        and source["admin_count"] == 4
        and source["total_users"] == 8
    )
    report["manifest_passed"] = manifest["passed"]
    report["conclusion"] = "PASS" if report["passed"] else "FAIL"
    return report


def run_audit(config: DatabaseConfig, manifest_path: Path, output_path: Path) -> bool:
    database = ReadOnlyDatabase(config)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    reused_path = Path(__file__).with_name("c1-post-upgrade-verification.json")
    reused = json.loads(reused_path.read_text(encoding="utf-8"))
    if not reused.get("passed") or not reused.get("source_aggregate_matches"):
        raise RuntimeError("C1 post-upgrade verification is not PASS")

    facts = {
        "audit_date": datetime.now(timezone.utc).isoformat(),
        "database": config.database,
        "read_only_transaction": True,
        "source_revision": _source_revision(database),
        "manifest_verification_reused": reused_path.name,
        "manifest_verification": verify_manifest(database, manifest),
        "fk_integrity": check_fk_integrity(database),
        "backfill_verification": check_backfill_correctness(database),
        "source_facts": get_source_facts(database),
    }
    result = evaluate_audit(facts)
    output_path.write_text(json.dumps(result, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return result["passed"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=5432)
    parser.add_argument("--user", default="blog_user")
    parser.add_argument("--database", default="blog_db")
    args = parser.parse_args()
    config = DatabaseConfig(args.host, args.port, args.user, args.database)
    return 0 if run_audit(config, args.manifest, args.output) else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (RuntimeError, subprocess.CalledProcessError, ValueError, json.JSONDecodeError) as error:
        print(f"BLOCKED: {error}", file=sys.stderr)
        sys.exit(1)
