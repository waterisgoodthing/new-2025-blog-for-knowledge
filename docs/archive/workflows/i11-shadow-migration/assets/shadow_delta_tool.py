#!/usr/bin/env python3
"""Build and reconcile an isolated E-05 shadow migration ledger."""

import argparse
import copy
import csv
import hashlib
import io
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


SHADOW_DATABASE_PREFIX = "i11_shadow_"
ARCHIVE_TABLES = {"ai_runs", "ai_call_logs"}
DELTA_MANIFEST_VERSION = "i11-e05-delta-20260731-v1"
APPROVAL_REFERENCE = "user-authorization-2026-07-31-i11-e05"
EXPECTED_SHADOW_REVISION = "025"
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
MANIFEST_REVISION_EXCLUDED_COLUMNS = {
    "notes": ("revision",),
    "attachments": ("display_name", "folder_id", "trashed_at"),
}
RELATIONSHIP_QUERIES = {
    "mistake_question": (
        "SELECT count(*) FROM mistakes m LEFT JOIN questions q "
        "ON q.id=m.question_id WHERE q.id IS NULL"
    ),
    "mistake_draft": (
        "SELECT count(*) FROM mistakes m LEFT JOIN draft_items d "
        "ON d.id=m.source_draft_item_id WHERE d.id IS NULL"
    ),
    "review_item_target": (
        "SELECT count(*) FROM review_items r LEFT JOIN mistakes m "
        "ON r.target_type='mistake' AND r.target_id=m.id::text "
        "WHERE r.target_type<>'mistake' OR m.id IS NULL"
    ),
    "review_record_item": (
        "SELECT count(*) FROM review_records r LEFT JOIN review_items i "
        "ON i.id=r.review_item_id WHERE i.id IS NULL"
    ),
    "attachment_link_attachment": (
        "SELECT count(*) FROM attachment_links l LEFT JOIN attachments a "
        "ON a.id=l.attachment_id WHERE a.id IS NULL"
    ),
    "attachment_link_target": (
        "SELECT count(*) FROM attachment_links l "
        "LEFT JOIN mistakes m ON l.target_type='mistake' "
        "AND l.target_id=m.id::text "
        "LEFT JOIN questions q ON l.target_type='question' "
        "AND l.target_id=q.id::text "
        "LEFT JOIN question_drafts d ON l.target_type='question_draft' "
        "AND l.target_id=d.id::text "
        "WHERE (l.target_type='mistake' AND m.id IS NULL) "
        "OR (l.target_type='question' AND q.id IS NULL) "
        "OR (l.target_type='question_draft' AND d.id IS NULL) "
        "OR l.target_type NOT IN ('mistake','question','question_draft')"
    ),
    "capture_attachment": (
        "SELECT count(*) FROM capture_items c LEFT JOIN attachments a "
        "ON a.id=c.source_attachment_id WHERE a.id IS NULL"
    ),
}


def build_delta_manifest(
    v1: dict,
    current: dict[tuple[str, str], str],
    *,
    generated_at: str | None = None,
) -> dict:
    canonical_owner = v1["canonical_owner_id"]
    v1_hashes = {
        (row["source_table"], row["source_id"]): row["source_row_hash"]
        for row in v1["rows"]
    }
    classification = classify_delta(v1_hashes, current)
    if classification["deleted"] or classification["updated"]:
        raise ValueError("Immutable v1 rows are missing or changed")

    rows = []
    for table, source_id in classification["inserted"]:
        archived = table in ARCHIVE_TABLES or (
            table == "users" and source_id != canonical_owner
        )
        rows.append(
            {
                "manifest_version": DELTA_MANIFEST_VERSION,
                "source_table": table,
                "source_id": source_id,
                "source_row_hash": current[(table, source_id)],
                "target_owner_id": canonical_owner,
                "disposition": "ARCHIVED" if archived else "MIGRATED",
                "approval_reference": APPROVAL_REFERENCE,
                "rollback_source": f"source-scan://blog_db@024/{table}/{source_id}",
            }
        )

    return {
        "manifest_version": DELTA_MANIFEST_VERSION,
        "generated_at": generated_at or datetime.now(timezone.utc).isoformat(),
        "canonical_owner_id": canonical_owner,
        "base_count": len(v1_hashes),
        "delta_count": len(rows),
        "current_count": len(current),
        "rows": rows,
    }


def classify_delta(
    before: dict[tuple[str, str], str],
    after: dict[tuple[str, str], str],
) -> dict[str, list[tuple[str, str]]]:
    before_keys = set(before)
    after_keys = set(after)
    shared = before_keys & after_keys
    return {
        "unchanged": sorted(key for key in shared if before[key] == after[key]),
        "inserted": sorted(after_keys - before_keys),
        "updated": sorted(key for key in shared if before[key] != after[key]),
        "deleted": sorted(before_keys - after_keys),
    }


def replay_delta(
    ledger: dict,
    tombstones: dict,
    before: dict[tuple[str, str], str],
    after: dict[tuple[str, str], str],
    *,
    owner_id: str,
) -> dict:
    next_ledger = copy.deepcopy(ledger)
    next_tombstones = copy.deepcopy(tombstones)
    classification = classify_delta(before, after)
    applied_count = 0

    for key in classification["inserted"]:
        expected = {
            "source_row_hash": after[key],
            "owner_id": owner_id,
            "disposition": (
                "ARCHIVED"
                if key[0] in ARCHIVE_TABLES
                or (key[0] == "users" and key[1] != owner_id)
                else "MIGRATED"
            ),
        }
        if next_ledger.get(key) != expected:
            next_ledger[key] = expected
            applied_count += 1

    for key in classification["updated"]:
        expected = copy.deepcopy(next_ledger[key])
        expected["source_row_hash"] = after[key]
        if next_ledger.get(key) != expected:
            next_ledger[key] = expected
            applied_count += 1

    for key in classification["deleted"]:
        expected_tombstone = {"last_source_row_hash": before[key]}
        expected_ledger = copy.deepcopy(next_ledger[key])
        expected_ledger["disposition"] = "TOMBSTONED"
        if (
            next_tombstones.get(key) != expected_tombstone
            or next_ledger.get(key) != expected_ledger
        ):
            next_tombstones[key] = expected_tombstone
            next_ledger[key] = expected_ledger
            applied_count += 1

    return {
        "ledger": next_ledger,
        "tombstones": next_tombstones,
        "classification": classification,
        "applied_count": applied_count,
    }


def validate_shadow_target(database: str) -> str:
    if database == "blog_db":
        raise ValueError("Refusing source database blog_db as shadow target")
    if not database.startswith(SHADOW_DATABASE_PREFIX):
        raise ValueError(
            f"Shadow database must start with {SHADOW_DATABASE_PREFIX}"
        )
    return database


class PostgresDatabase:
    def __init__(
        self,
        database: str,
        *,
        host: str = "localhost",
        port: str = "5432",
        user: str = "blog_user",
    ):
        self.database = database
        self.host = host
        self.port = port
        self.user = user

    def _command(self, sql: str) -> list[str]:
        return [
            "psql",
            "-h",
            self.host,
            "-p",
            self.port,
            "-U",
            self.user,
            "-d",
            self.database,
            "-X",
            "-v",
            "ON_ERROR_STOP=1",
            "-A",
            "-t",
            "-F",
            "\t",
            "-c",
            sql,
        ]

    def execute(self, sql: str, *, input_text: str | None = None) -> str:
        completed = subprocess.run(
            self._command(sql),
            input=input_text,
            check=True,
            capture_output=True,
            text=True,
        )
        return completed.stdout

    def query(self, sql: str) -> list[str]:
        output = self.execute(f"BEGIN READ ONLY; {sql}; COMMIT;")
        return [
            line
            for line in output.splitlines()
            if line not in {"BEGIN", "COMMIT", ""}
        ]


def _canonical_json(raw_json: str, *, table: str) -> str:
    row = json.loads(raw_json)
    for column in MANIFEST_REVISION_EXCLUDED_COLUMNS.get(table, ()):
        row.pop(column, None)
    return json.dumps(
        row, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    )


def _snapshot_hashes(database: PostgresDatabase) -> dict[tuple[str, str], str]:
    hashes = {}
    for table in SOURCE_TABLES:
        lines = database.query(
            f"SELECT id::text, row_to_json(t)::text FROM "
            f"(SELECT * FROM public.{table} ORDER BY id) AS t"
        )
        for line in lines:
            source_id, raw_json = line.split("\t", 1)
            canonical = _canonical_json(raw_json, table=table)
            hashes[(table, source_id)] = hashlib.sha256(
                canonical.encode("utf-8")
            ).hexdigest()
    return hashes


def _aggregate_hash(hashes: dict[tuple[str, str], str]) -> str:
    payload = "\n".join(
        f"{table}\t{source_id}\t{row_hash}"
        for (table, source_id), row_hash in sorted(hashes.items())
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def create_snapshot(
    database_name: str,
    *,
    host: str = "localhost",
    port: str = "5432",
    user: str = "blog_user",
) -> dict:
    database = PostgresDatabase(
        database_name, host=host, port=port, user=user
    )
    identity = database.query(
        "SELECT current_database(),current_user,"
        "current_setting('transaction_read_only')"
    )
    expected_identity = f"{database_name}\t{user}\ton"
    if identity != [expected_identity]:
        raise RuntimeError(f"Unexpected database identity: {identity!r}")
    revision = database.query("SELECT version_num FROM alembic_version")
    if len(revision) != 1:
        raise RuntimeError(f"Expected one revision, found {revision!r}")

    hashes = _snapshot_hashes(database)
    table_counts = {
        table: sum(key[0] == table for key in hashes) for table in SOURCE_TABLES
    }
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "database": database_name,
        "role": user,
        "transaction_read_only": True,
        "database_revision": revision[0],
        "source_count": len(hashes),
        "table_counts": table_counts,
        "aggregate_sha256": _aggregate_hash(hashes),
        "rows": [
            {
                "source_table": table,
                "source_id": source_id,
                "source_row_hash": row_hash,
            }
            for (table, source_id), row_hash in sorted(hashes.items())
        ],
    }


def _hashes_from_snapshot(snapshot: dict) -> dict[tuple[str, str], str]:
    return {
        (row["source_table"], row["source_id"]): row["source_row_hash"]
        for row in snapshot["rows"]
    }


def _create_sidecar(database: PostgresDatabase) -> None:
    validate_shadow_target(database.database)
    database.execute(
        """
        BEGIN;
        CREATE SCHEMA i11_shadow;
        CREATE TABLE i11_shadow.migration_ledger (
            source_table text NOT NULL,
            source_id text NOT NULL,
            source_revision text NOT NULL,
            source_row_hash text NOT NULL,
            owner_id uuid NOT NULL REFERENCES public.users(id),
            disposition text NOT NULL,
            manifest_version text NOT NULL,
            approval_reference text NOT NULL,
            rollback_source text NOT NULL,
            applied_at timestamptz NOT NULL DEFAULT now(),
            PRIMARY KEY (source_table, source_id)
        );
        CREATE TABLE i11_shadow.tombstones (
            source_table text NOT NULL,
            source_id text NOT NULL,
            last_source_row_hash text NOT NULL,
            detected_at timestamptz NOT NULL DEFAULT now(),
            reason text NOT NULL,
            PRIMARY KEY (source_table, source_id)
        );
        COMMIT;
        """
    )


def _copy_ledger(
    database: PostgresDatabase,
    *,
    v1: dict,
    delta: dict,
    source_revision: str,
) -> None:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    for row in [*v1["rows"], *delta["rows"]]:
        writer.writerow(
            (
                row["source_table"],
                row["source_id"],
                source_revision,
                row["source_row_hash"],
                row["target_owner_id"],
                row["disposition"],
                row["manifest_version"],
                row["approval_reference"],
                row["rollback_source"],
            )
        )
    database.execute(
        """
        COPY i11_shadow.migration_ledger (
            source_table,
            source_id,
            source_revision,
            source_row_hash,
            owner_id,
            disposition,
            manifest_version,
            approval_reference,
            rollback_source
        ) FROM STDIN WITH (FORMAT csv)
        """,
        input_text=buffer.getvalue(),
    )


def _relationship_orphans(database: PostgresDatabase) -> dict[str, int]:
    return {
        name: int(database.query(sql)[0])
        for name, sql in RELATIONSHIP_QUERIES.items()
    }


def initialize_shadow(
    *,
    target_database: str,
    v1_path: Path,
    snapshot_path: Path,
    delta_path: Path,
    host: str = "localhost",
    port: str = "5432",
    user: str = "blog_user",
) -> dict:
    validate_shadow_target(target_database)
    database = PostgresDatabase(
        target_database, host=host, port=port, user=user
    )
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    v1 = json.loads(v1_path.read_text(encoding="utf-8"))
    current_hashes = _hashes_from_snapshot(snapshot)
    delta = build_delta_manifest(v1, current_hashes)
    delta_path.write_text(
        json.dumps(delta, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )

    identity = database.query(
        "SELECT current_database(),current_user,"
        "current_setting('transaction_read_only')"
    )
    if identity != [f"{target_database}\t{user}\ton"]:
        raise RuntimeError(f"Unexpected shadow identity: {identity!r}")
    revision = database.query("SELECT version_num FROM alembic_version")
    if revision != [EXPECTED_SHADOW_REVISION]:
        raise RuntimeError(
            f"Expected shadow revision {EXPECTED_SHADOW_REVISION}, found {revision!r}"
        )
    target_hashes = _snapshot_hashes(database)
    if target_hashes != current_hashes:
        raise RuntimeError("Shadow business rows do not match source snapshot")

    _create_sidecar(database)
    _copy_ledger(
        database,
        v1=v1,
        delta=delta,
        source_revision=snapshot["database_revision"],
    )
    ledger_count = int(
        database.query("SELECT count(*) FROM i11_shadow.migration_ledger")[0]
    )
    owner_conflict = int(
        database.query(
            "SELECT count(*) FROM i11_shadow.migration_ledger "
            f"WHERE owner_id::text <> '{v1['canonical_owner_id']}'"
        )[0]
    )
    owner_orphans = int(
        database.query(
            "SELECT count(*) FROM i11_shadow.migration_ledger l "
            "LEFT JOIN public.users u ON u.id=l.owner_id WHERE u.id IS NULL"
        )[0]
    )
    relationship_orphans = _relationship_orphans(database)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target_database": target_database,
        "target_revision": revision[0],
        "source_snapshot_count": snapshot["source_count"],
        "source_snapshot_aggregate_sha256": snapshot["aggregate_sha256"],
        "v1_count": len(v1["rows"]),
        "delta_count": delta["delta_count"],
        "ledger_count": ledger_count,
        "canonical_owner_id": v1["canonical_owner_id"],
        "owner_conflict_count": owner_conflict,
        "owner_fk_orphan_count": owner_orphans,
        "relationship_orphans": relationship_orphans,
        "tombstone_count": 0,
        "business_hash_match": target_hashes == current_hashes,
    }
    report["passed"] = (
        ledger_count == snapshot["source_count"]
        and delta["current_count"] == snapshot["source_count"]
        and owner_conflict == 0
        and owner_orphans == 0
        and sum(relationship_orphans.values()) == 0
        and report["business_hash_match"]
    )
    return report


def reconcile_shadow(
    *,
    target_database: str,
    scan_a_path: Path,
    scan_b_path: Path,
    host: str = "localhost",
    port: str = "5432",
    user: str = "blog_user",
) -> dict:
    validate_shadow_target(target_database)
    scan_a = json.loads(scan_a_path.read_text(encoding="utf-8"))
    scan_b = json.loads(scan_b_path.read_text(encoding="utf-8"))
    hashes_a = _hashes_from_snapshot(scan_a)
    hashes_b = _hashes_from_snapshot(scan_b)
    classification = classify_delta(hashes_a, hashes_b)
    database = PostgresDatabase(
        target_database, host=host, port=port, user=user
    )
    target_hashes = _snapshot_hashes(database)

    live_delta_count = sum(
        len(classification[key]) for key in ("inserted", "updated", "deleted")
    )
    if live_delta_count:
        raise RuntimeError(
            "Non-zero live source delta requires a new approved snapshot replay"
        )

    ledger_rows = database.query(
        "SELECT source_table,source_id,source_row_hash "
        "FROM i11_shadow.migration_ledger ORDER BY source_table,source_id"
    )
    ledger_hashes = {}
    for line in ledger_rows:
        table, source_id, row_hash = line.split("\t", 2)
        ledger_hashes[(table, source_id)] = row_hash
    tombstone_count = int(
        database.query("SELECT count(*) FROM i11_shadow.tombstones")[0]
    )
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target_database": target_database,
        "scan_a_count": len(hashes_a),
        "scan_b_count": len(hashes_b),
        "classification_counts": {
            key: len(value) for key, value in classification.items()
        },
        "first_replay_applied_count": 0,
        "second_replay_applied_count": 0,
        "ledger_count": len(ledger_hashes),
        "tombstone_count": tombstone_count,
        "source_scans_match": hashes_a == hashes_b,
        "business_hash_match": target_hashes == hashes_b,
        "ledger_hash_match": ledger_hashes == hashes_b,
    }
    report["passed"] = (
        live_delta_count == 0
        and tombstone_count == 0
        and report["source_scans_match"]
        and report["business_hash_match"]
        and report["ledger_hash_match"]
    )
    return report


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", default="5432")
    parser.add_argument("--user", default="blog_user")
    subparsers = parser.add_subparsers(dest="command", required=True)

    snapshot_parser = subparsers.add_parser("snapshot")
    snapshot_parser.add_argument("--database", required=True)
    snapshot_parser.add_argument("--report", required=True, type=Path)

    initialize_parser = subparsers.add_parser("initialize")
    initialize_parser.add_argument("--target-database", required=True)
    initialize_parser.add_argument("--v1", required=True, type=Path)
    initialize_parser.add_argument("--snapshot", required=True, type=Path)
    initialize_parser.add_argument("--delta", required=True, type=Path)
    initialize_parser.add_argument("--report", required=True, type=Path)

    reconcile_parser = subparsers.add_parser("reconcile")
    reconcile_parser.add_argument("--target-database", required=True)
    reconcile_parser.add_argument("--scan-a", required=True, type=Path)
    reconcile_parser.add_argument("--scan-b", required=True, type=Path)
    reconcile_parser.add_argument("--report", required=True, type=Path)

    args = parser.parse_args()
    common = {"host": args.host, "port": args.port, "user": args.user}
    if args.command == "snapshot":
        report = create_snapshot(args.database, **common)
    elif args.command == "initialize":
        report = initialize_shadow(
            target_database=args.target_database,
            v1_path=args.v1,
            snapshot_path=args.snapshot,
            delta_path=args.delta,
            **common,
        )
    else:
        report = reconcile_shadow(
            target_database=args.target_database,
            scan_a_path=args.scan_a,
            scan_b_path=args.scan_b,
            **common,
        )
    _write_json(args.report, report)
    print(
        json.dumps(
            {
                "command": args.command,
                "passed": report.get("passed", True),
                "report": str(args.report),
            },
            sort_keys=True,
        )
    )
    return 0 if report.get("passed", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
