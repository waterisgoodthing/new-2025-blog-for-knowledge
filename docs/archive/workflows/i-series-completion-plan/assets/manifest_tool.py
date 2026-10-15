#!/usr/bin/env python3
import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ARCHIVE_TABLES = {"ai_runs", "ai_call_logs"}
APPROVAL_REFERENCE = "user-authorization-2026-07-28"
MANIFEST_VERSION = "i-series-c1-20260728-v1"
CANONICAL_OWNER = "4c503215-b158-4162-b472-79df8289ed0a"
SOURCE_TABLES = (
    "notes",
    "questions",
    "mistakes",
    "review_items",
    "review_records",
    "attachments",
    "attachment_links",
    "capture_items",
    "draft_items",
    "ai_runs",
    "ai_call_logs",
    "users",
)
SUPPORTED_REVISION_PROJECTIONS = {
    ("020", "020"): {},
    ("020", "024"): {
        "notes": ("revision",),
        "attachments": ("display_name", "folder_id", "trashed_at"),
    },
}


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _canonical_json(raw_json: str) -> str:
    return json.dumps(json.loads(raw_json), ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def resolve_revision_projection(manifest_revision: str, database_revision: str):
    pair = (manifest_revision, database_revision)
    if pair not in SUPPORTED_REVISION_PROJECTIONS:
        raise RuntimeError(
            "Unsupported manifest/database revision pair: "
            f"manifest={manifest_revision}, database={database_revision}"
        )
    return SUPPORTED_REVISION_PROJECTIONS[pair]


def project_row_to_manifest_revision(
    table: str,
    raw_json: str,
    *,
    manifest_revision: str,
    database_revision: str,
) -> str:
    projection = resolve_revision_projection(manifest_revision, database_revision)
    row = json.loads(raw_json)
    for column in projection.get(table, ()):
        row.pop(column, None)
    return json.dumps(row, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def _aggregate_hash(rows) -> str:
    payload = "\n".join(
        f'{row["source_table"]}\t{row["source_id"]}\t{row["source_row_hash"]}'
        for row in sorted(rows, key=lambda item: (item["source_table"], item["source_id"]))
    )
    return _sha256(payload)


def build_manifest(source_rows, *, canonical_owner: str, source_revision: str, generated_at: str):
    rows = []
    for table in sorted(source_rows):
        for source_id, raw_json in sorted(source_rows[table]):
            canonical_row = _canonical_json(raw_json)
            archived = table in ARCHIVE_TABLES or (table == "users" and source_id != canonical_owner)
            disposition = "ARCHIVED" if archived else "MIGRATED"
            rows.append(
                {
                    "manifest_version": MANIFEST_VERSION,
                    "source_revision": source_revision,
                    "source_table": table,
                    "source_id": source_id,
                    "source_row_hash": _sha256(canonical_row),
                    "source_owner_evidence": (
                        "canonical_admin_uuid_min"
                        if table == "users" and source_id == canonical_owner
                        else "authorized_single_owner_mapping"
                    ),
                    "target_owner_id": canonical_owner,
                    "target_type": f"archive/{table}" if archived else table,
                    "target_id": source_id,
                    "disposition": disposition,
                    "rule_id": (
                        "D6_OWNER_CONTROLLED_READ_ONLY_ARCHIVE"
                        if table in ARCHIVE_TABLES
                        else "D3_NON_CANONICAL_IDENTITY_ARCHIVE"
                        if table == "users" and archived
                        else "D1_D2_CANONICAL_OWNER_MIGRATION"
                    ),
                    "conflict_code": None,
                    "approved_at": "2026-07-28",
                    "approval_reference": APPROVAL_REFERENCE,
                    "rollback_source": f"source-snapshot://blog_db@{source_revision}/{table}/{source_id}",
                }
            )
    table_counts = {table: len(table_rows) for table, table_rows in source_rows.items()}
    disposition_counts = Counter(row["disposition"] for row in rows)
    manifest = {
        "manifest_version": MANIFEST_VERSION,
        "generated_at": generated_at,
        "source_database": "blog_db:5432",
        "source_revision": source_revision,
        "canonical_owner_id": canonical_owner,
        "source_count": len(rows),
        "table_counts": dict(sorted(table_counts.items())),
        "disposition_counts": dict(sorted(disposition_counts.items())),
        "source_aggregate_sha256": _aggregate_hash(rows),
        "rows": rows,
    }
    payload = json.dumps(manifest, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    manifest["manifest_payload_sha256"] = _sha256(payload)
    return manifest


def verify_manifest_rows(manifest, source_rows):
    manifest_keys = [(row["source_table"], row["source_id"]) for row in manifest["rows"]]
    manifest_counts = Counter(manifest_keys)
    source_by_key = {
        (table, source_id): _sha256(_canonical_json(raw_json))
        for table, table_rows in source_rows.items()
        for source_id, raw_json in table_rows
    }
    manifest_by_key = {
        (row["source_table"], row["source_id"]): row for row in manifest["rows"]
    }
    source_keys = set(source_by_key)
    unique_manifest_keys = set(manifest_by_key)
    result = {
        "source_count": len(source_keys),
        "manifest_count": len(manifest_keys),
        "missing_manifest": len(source_keys - unique_manifest_keys),
        "extra_manifest": len(unique_manifest_keys - source_keys),
        "duplicate_manifest": sum(count - 1 for count in manifest_counts.values() if count > 1),
        "hash_drift": sum(
            manifest_by_key[key]["source_row_hash"] != source_by_key[key]
            for key in source_keys & unique_manifest_keys
        ),
        "owner_conflict": sum(
            row["target_owner_id"] != manifest["canonical_owner_id"] for row in manifest["rows"]
        ),
        "invalid_disposition": sum(
            row["disposition"] not in {"MIGRATED", "MERGED", "ARCHIVED", "QUARANTINED", "REJECTED_WITH_REASON"}
            for row in manifest["rows"]
        ),
        "disposition_rule_conflict": sum(
            row["disposition"]
            != (
                "ARCHIVED"
                if row["source_table"] in ARCHIVE_TABLES
                or (row["source_table"] == "users" and row["source_id"] != manifest["canonical_owner_id"])
                else "MIGRATED"
            )
            for row in manifest["rows"]
        ),
    }
    result["passed"] = all(
        result[key] == 0
        for key in (
            "missing_manifest",
            "extra_manifest",
            "duplicate_manifest",
            "hash_drift",
            "owner_conflict",
            "invalid_disposition",
            "disposition_rule_conflict",
        )
    )
    return result


def _psql(sql: str) -> list[str]:
    command = [
        "psql",
        "-h",
        "localhost",
        "-p",
        "5432",
        "-U",
        "blog_user",
        "-d",
        "blog_db",
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


def _source_revision() -> str:
    rows = _psql("SELECT version_num FROM alembic_version;")
    if len(rows) != 1:
        raise RuntimeError(f"Expected one Alembic revision, found {len(rows)}")
    return rows[0]


def _canonical_owner() -> str:
    rows = _psql("SELECT id::text FROM users WHERE is_admin IS TRUE ORDER BY id LIMIT 1;")
    if rows != [CANONICAL_OWNER]:
        raise RuntimeError(f"Canonical owner drift: expected {CANONICAL_OWNER}, found {rows}")
    return rows[0]


def _read_source_per_table():
    source_rows = {}
    for table in SOURCE_TABLES:
        lines = _psql(
            f"SELECT id::text, row_to_json(t)::text FROM "
            f"(SELECT * FROM public.{table} ORDER BY id) AS t;"
        )
        source_rows[table] = [tuple(line.split("\t", 1)) for line in lines]
    return source_rows


def _row_json_expression(table: str, projection) -> str:
    excluded_columns = projection.get(table, ())
    if not excluded_columns:
        return "to_jsonb(t)"
    sql_columns = ", ".join(f"'{column}'" for column in excluded_columns)
    return f"(to_jsonb(t) - ARRAY[{sql_columns}]::text[])"


def _read_source_union(projection):
    branches = [
        f"SELECT '{table}'::text AS source_table, id::text AS source_id, "
        f"{_row_json_expression(table, projection)}::text AS row_data "
        f"FROM public.{table} AS t"
        for table in SOURCE_TABLES
    ]
    lines = _psql(
        "SELECT source_table, source_id, row_data FROM ("
        + " UNION ALL ".join(branches)
        + ") AS source_rows ORDER BY source_table, source_id;"
    )
    source_rows = {table: [] for table in SOURCE_TABLES}
    for line in lines:
        table, source_id, raw_json = line.split("\t", 2)
        source_rows[table].append((source_id, raw_json))
    return source_rows


def _relationship_orphans() -> dict[str, int]:
    queries = {
        "mistake_question": "SELECT count(*) FROM mistakes m LEFT JOIN questions q ON q.id=m.question_id WHERE q.id IS NULL;",
        "mistake_draft": "SELECT count(*) FROM mistakes m LEFT JOIN draft_items d ON d.id=m.source_draft_item_id WHERE d.id IS NULL;",
        "review_item_target": "SELECT count(*) FROM review_items r LEFT JOIN mistakes m ON r.target_type='mistake' AND r.target_id=m.id::text WHERE r.target_type<>'mistake' OR m.id IS NULL;",
        "review_record_item": "SELECT count(*) FROM review_records r LEFT JOIN review_items i ON i.id=r.review_item_id WHERE i.id IS NULL;",
        "attachment_link_attachment": "SELECT count(*) FROM attachment_links l LEFT JOIN attachments a ON a.id=l.attachment_id WHERE a.id IS NULL;",
        "attachment_link_target": "SELECT count(*) FROM attachment_links l LEFT JOIN mistakes m ON l.target_type='mistake' AND l.target_id=m.id::text LEFT JOIN questions q ON l.target_type='question' AND l.target_id=q.id::text LEFT JOIN question_drafts d ON l.target_type='question_draft' AND l.target_id=d.id::text WHERE (l.target_type='mistake' AND m.id IS NULL) OR (l.target_type='question' AND q.id IS NULL) OR (l.target_type='question_draft' AND d.id IS NULL) OR l.target_type NOT IN ('mistake','question','question_draft');",
        "capture_attachment": "SELECT count(*) FROM capture_items c LEFT JOIN attachments a ON a.id=c.source_attachment_id WHERE a.id IS NULL;",
    }
    return {name: int(_psql(sql)[0]) for name, sql in queries.items()}


def _write_json(path: str, payload) -> None:
    Path(path).write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def generate(output: str) -> None:
    revision = _source_revision()
    if revision != "020":
        raise RuntimeError(f"C1 requires source revision 020, found {revision}")
    manifest = build_manifest(
        _read_source_per_table(),
        canonical_owner=_canonical_owner(),
        source_revision=revision,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
    _write_json(output, manifest)
    print(json.dumps({key: manifest[key] for key in ("source_count", "table_counts", "disposition_counts", "source_aggregate_sha256", "manifest_payload_sha256")}, sort_keys=True))


def verify(manifest_path: str, report_path: str) -> bool:
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    database_revision = _source_revision()
    manifest_revision = manifest["source_revision"]
    projection = resolve_revision_projection(manifest_revision, database_revision)
    source_rows = _read_source_union(projection)
    report = verify_manifest_rows(manifest, source_rows)
    report["manifest_source_revision"] = manifest_revision
    report["database_revision_actual"] = database_revision
    report["projection_revision"] = manifest_revision
    report["projection_applied"] = bool(projection)
    report["source_revision_actual"] = database_revision
    report["source_revision_expected"] = manifest_revision
    report["canonical_owner_actual"] = _canonical_owner()
    report["source_aggregate_sha256"] = _aggregate_hash(
        build_manifest(
            source_rows,
            canonical_owner=manifest["canonical_owner_id"],
            source_revision=manifest["source_revision"],
            generated_at=manifest["generated_at"],
        )["rows"]
    )
    report["source_aggregate_matches"] = report["source_aggregate_sha256"] == manifest["source_aggregate_sha256"]
    report["relationship_orphans"] = _relationship_orphans()
    report["orphan_count"] = sum(report["relationship_orphans"].values())
    report["passed"] = bool(
        report["passed"]
        and report["canonical_owner_actual"] == manifest["canonical_owner_id"]
        and report["source_aggregate_matches"]
        and report["orphan_count"] == 0
        and report["source_count"] == 121
    )
    report["dry_run_ready"] = "PASS" if report["passed"] else "BLOCKED"
    _write_json(report_path, report)
    print(json.dumps(report, sort_keys=True))
    return report["passed"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate and independently verify the I-series C1 owner manifest")
    subparsers = parser.add_subparsers(dest="command", required=True)
    generate_parser = subparsers.add_parser("generate")
    generate_parser.add_argument("--output", required=True)
    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("--manifest", required=True)
    verify_parser.add_argument("--report", required=True)
    args = parser.parse_args()
    if args.command == "generate":
        generate(args.output)
        return 0
    return 0 if verify(args.manifest, args.report) else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (RuntimeError, subprocess.CalledProcessError, ValueError, json.JSONDecodeError) as error:
        print(f"BLOCKED: {error}", file=sys.stderr)
        sys.exit(1)
