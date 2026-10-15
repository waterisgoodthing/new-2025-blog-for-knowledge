#!/usr/bin/env python3
"""Run the approved single-owner mapping against an isolated PostgreSQL clone."""

import argparse
import csv
import hashlib
import io
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ISOLATED_DATABASE_PREFIX = "i10_owner_backfill_"
EXPECTED_ENTITY_COUNT = 121
EXPECTED_DATABASE_REVISION = "025"
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


def evaluate_audit(metrics: dict) -> bool:
    return (
        metrics.get("source_count") == EXPECTED_ENTITY_COUNT
        and metrics.get("manifest_count") == EXPECTED_ENTITY_COUNT
        and metrics.get("sidecar_count") == EXPECTED_ENTITY_COUNT
        and metrics.get("database_revision") == EXPECTED_DATABASE_REVISION
        and metrics.get("canonical_owner_count") == 1
        and all(
            metrics.get(key) == 0
            for key in (
                "missing_count",
                "extra_count",
                "hash_drift_count",
                "owner_conflict_count",
                "owner_fk_orphan_count",
                "relationship_orphan_count",
            )
        )
    )


def validate_manifest(payload: dict) -> dict[str, int]:
    rows = payload.get("rows", [])
    source_keys = [
        (row.get("source_table"), row.get("source_id")) for row in rows
    ]
    duplicate_count = len(source_keys) - len(set(source_keys))
    owners = {row.get("target_owner_id") for row in rows}
    expected_owner = payload.get("canonical_owner_id")

    if len(rows) != payload.get("source_count"):
        raise ValueError("Manifest source_count does not match row count")
    if duplicate_count:
        raise ValueError("Manifest contains duplicate source keys")
    if owners != {expected_owner} or expected_owner is None:
        raise ValueError("Manifest does not use one canonical owner")

    return {
        "row_count": len(rows),
        "owner_count": len(owners),
        "duplicate_count": duplicate_count,
    }


def validate_target_database(database: str) -> str:
    if database == "blog_db":
        raise ValueError("Refusing daily database blog_db")
    if not database.startswith(ISOLATED_DATABASE_PREFIX):
        raise ValueError(
            f"Target database must start with {ISOLATED_DATABASE_PREFIX}"
        )
    return database


class IsolatedDatabase:
    def __init__(
        self,
        database: str,
        *,
        host: str = "localhost",
        port: str = "5432",
        user: str = "blog_user",
    ):
        self.database = validate_target_database(database)
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


def _source_rows(database: IsolatedDatabase) -> dict[str, list[tuple[str, str]]]:
    rows = {}
    for table in SOURCE_TABLES:
        output = database.query(
            f"SELECT id::text, row_to_json(t)::text FROM "
            f"(SELECT * FROM public.{table} ORDER BY id) AS t"
        )
        rows[table] = [tuple(line.split("\t", 1)) for line in output]
    return rows


def _source_hashes(
    source_rows: dict[str, list[tuple[str, str]]],
) -> dict[tuple[str, str], str]:
    hashes = {}
    for table, rows in source_rows.items():
        for source_id, raw_json in rows:
            canonical = _canonical_json(raw_json, table=table)
            hashes[(table, source_id)] = hashlib.sha256(
                canonical.encode("utf-8")
            ).hexdigest()
    return hashes


def _create_sidecar(database: IsolatedDatabase) -> None:
    database.execute(
        """
        BEGIN;
        CREATE SCHEMA i10_dry_run;
        CREATE TABLE i10_dry_run.owner_backfill (
            source_table text NOT NULL,
            source_id text NOT NULL,
            owner_id uuid NOT NULL REFERENCES public.users(id),
            source_row_hash text NOT NULL,
            disposition text NOT NULL,
            approval_reference text NOT NULL,
            rollback_source text NOT NULL,
            PRIMARY KEY (source_table, source_id)
        );
        COMMIT;
        """
    )


def _copy_manifest(database: IsolatedDatabase, manifest: dict) -> None:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    for row in manifest["rows"]:
        writer.writerow(
            (
                row["source_table"],
                row["source_id"],
                row["target_owner_id"],
                row["source_row_hash"],
                row["disposition"],
                row["approval_reference"],
                row["rollback_source"],
            )
        )
    database.execute(
        """
        COPY i10_dry_run.owner_backfill (
            source_table,
            source_id,
            owner_id,
            source_row_hash,
            disposition,
            approval_reference,
            rollback_source
        ) FROM STDIN WITH (FORMAT csv)
        """,
        input_text=buffer.getvalue(),
    )


def _sidecar_keys(database: IsolatedDatabase) -> set[tuple[str, str]]:
    lines = database.query(
        "SELECT source_table, source_id "
        "FROM i10_dry_run.owner_backfill ORDER BY source_table, source_id"
    )
    return {tuple(line.split("\t", 1)) for line in lines}


def run_backfill(
    *,
    database_name: str,
    manifest_path: Path,
    host: str = "localhost",
    port: str = "5432",
    user: str = "blog_user",
) -> dict:
    database = IsolatedDatabase(
        database_name, host=host, port=port, user=user
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_validation = validate_manifest(manifest)

    identity = database.query(
        "SELECT current_database(), current_user, "
        "current_setting('transaction_read_only')"
    )
    expected_identity = f"{database_name}\t{user}\ton"
    if identity != [expected_identity]:
        raise RuntimeError(
            f"Unexpected isolated database identity: {identity!r}"
        )

    revision_rows = database.query("SELECT version_num FROM alembic_version")
    if revision_rows != [EXPECTED_DATABASE_REVISION]:
        raise RuntimeError(
            f"Expected revision {EXPECTED_DATABASE_REVISION}, "
            f"found {revision_rows!r}"
        )

    source_rows = _source_rows(database)
    source_hashes = _source_hashes(source_rows)
    manifest_hashes = {
        (row["source_table"], row["source_id"]): row["source_row_hash"]
        for row in manifest["rows"]
    }
    manifest_keys = set(manifest_hashes)
    source_keys = set(source_hashes)

    _create_sidecar(database)
    _copy_manifest(database, manifest)
    sidecar_keys = _sidecar_keys(database)

    relationship_orphans = {
        name: int(database.query(sql)[0])
        for name, sql in RELATIONSHIP_QUERIES.items()
    }
    table_counts = {
        table: len(rows) for table, rows in source_rows.items()
    }
    metrics = {
        "source_count": len(source_keys),
        "manifest_count": manifest_validation["row_count"],
        "sidecar_count": int(
            database.query(
                "SELECT count(*) FROM i10_dry_run.owner_backfill"
            )[0]
        ),
        "missing_count": len(source_keys - manifest_keys),
        "extra_count": len(manifest_keys - source_keys),
        "hash_drift_count": sum(
            source_hashes.get(key) != manifest_hashes.get(key)
            for key in source_keys | manifest_keys
        ),
        "owner_conflict_count": int(
            database.query(
                "SELECT count(*) FROM i10_dry_run.owner_backfill "
                f"WHERE owner_id::text <> "
                f"'{manifest['canonical_owner_id']}'"
            )[0]
        ),
        "owner_fk_orphan_count": int(
            database.query(
                "SELECT count(*) FROM i10_dry_run.owner_backfill b "
                "LEFT JOIN public.users u ON u.id=b.owner_id "
                "WHERE u.id IS NULL"
            )[0]
        ),
        "relationship_orphan_count": sum(relationship_orphans.values()),
        "database_revision": revision_rows[0],
        "canonical_owner_count": int(
            database.query(
                "SELECT count(*) FROM public.users "
                f"WHERE id::text='{manifest['canonical_owner_id']}'"
            )[0]
        ),
    }
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target_database": database_name,
        "target_role": user,
        "manifest_path": str(manifest_path),
        "manifest_sha256": hashlib.sha256(
            manifest_path.read_bytes()
        ).hexdigest(),
        "canonical_owner_id": manifest["canonical_owner_id"],
        "table_counts": table_counts,
        "disposition_counts": manifest["disposition_counts"],
        "relationship_orphans": relationship_orphans,
        "sidecar_key_match": sidecar_keys == manifest_keys == source_keys,
        "metrics": metrics,
    }
    report["passed"] = (
        report["sidecar_key_match"]
        and table_counts == manifest["table_counts"]
        and evaluate_audit(metrics)
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", required=True)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", default="5432")
    parser.add_argument("--user", default="blog_user")
    args = parser.parse_args()

    report = run_backfill(
        database_name=args.database,
        manifest_path=args.manifest,
        host=args.host,
        port=args.port,
        user=args.user,
    )
    args.report.write_text(
        json.dumps(report, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "target_database": report["target_database"],
                "metrics": report["metrics"],
                "passed": report["passed"],
            },
            ensure_ascii=True,
            sort_keys=True,
        )
    )
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
