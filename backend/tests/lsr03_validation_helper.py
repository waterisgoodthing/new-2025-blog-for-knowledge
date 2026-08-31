"""Independent LSR-03 archive/replay validation for synthetic isolated data.

The positive run has five separate sources of truth: a source snapshot,
external archive rows, a separate expected-hash manifest, a second live-source
read, and an all-disposition replay scope.  This module is invoked through the
fail-closed guarded runner and never selects a database or credentials.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlsplit, urlunsplit

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine


MAPPING_VERSION = "lsr03-fixture-v2"
ARCHIVE_NAME = "archive.ndjson"
ARCHIVE_MANIFEST_NAME = "archive-expected-hashes.ndjson"
RUN_MANIFEST_NAME = "run-manifest.json"
SYNTHETIC_SOURCE_IDS = (
    "22222222-2222-4222-8222-222222222223",
    "33333333-3333-4333-8333-333333333334",
    "44444444-4444-4444-8444-444444444445",
    "90000000-0000-4000-8000-000000000019",
)


def _adapter_database_url(database_url: str) -> str:
    """Build the isolated adapter identity URL without carrying credentials."""
    parsed = urlsplit(database_url)
    scheme = "postgresql+asyncpg" if parsed.scheme == "postgresql" else parsed.scheme
    if scheme != "postgresql+asyncpg":
        raise ValueError("LSR03 adapter URL must use the asyncpg PostgreSQL scheme")
    if parsed.hostname != "127.0.0.1" or parsed.port != 55432:
        raise ValueError("LSR03 adapter URL must remain on 127.0.0.1:55432")
    if (
        not parsed.path.startswith("/lsr03_")
        or "/" in parsed.path[1:]
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("LSR03 adapter URL must remain an isolated lsr03_* database")
    # Rebuild the netloc from the fixed adapter identity so any temporary
    # password on the guarded input is deliberately omitted.
    return urlunsplit(
        (scheme, f"legacy_note_adapter_runner@{parsed.hostname}:{parsed.port}", parsed.path, "", "")
    )


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _write_ndjson(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.write_text(
        "".join(_canonical_json(row) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )


def _read_ndjson(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


async def _canonical_source_rows(connection: AsyncConnection) -> list[dict[str, Any]]:
    """Ask the owner-only canonicalizer for rows through the adapter identity."""
    rows: list[dict[str, Any]] = []
    for source_id in SYNTHETIC_SOURCE_IDS:
        row = (await connection.execute(text("""
          SELECT legacy_migration.canonicalize_legacy_note(:source_note_id) AS canonical_payload,
                 encode(public.digest(convert_to(
                   legacy_migration.canonicalize_legacy_note(:source_note_id)::text, 'UTF8'
                 ), 'sha256'), 'hex') AS source_hash
        """), {"source_note_id": source_id})).mappings().one()
        rows.append({"source_note_id": uuid.UUID(source_id), **row})
    return rows


async def _create_temp_sources(
    connection: AsyncConnection, canonical_rows: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Create verifier-owned temp relations from adapter-produced rows."""
    for ddl in (
        """CREATE TEMP TABLE lsr03_run_manifest(
             run_id uuid PRIMARY KEY, mapping_version text NOT NULL,
             evaluation_time_utc timestamptz NOT NULL,
             source_snapshot_version text NOT NULL, archive_rowcount bigint NOT NULL,
             archive_hash char(64) NOT NULL CHECK (archive_hash ~ '^[0-9a-f]{64}$')
           ) ON COMMIT DROP""",
        """CREATE TEMP TABLE lsr03_source_snapshot(
             source_note_id uuid NOT NULL, mapping_version text NOT NULL,
             canonical_payload jsonb NOT NULL, source_hash char(64) NOT NULL,
             PRIMARY KEY (source_note_id, mapping_version)
           ) ON COMMIT DROP""",
        """CREATE TEMP TABLE lsr03_archive_rows(
             source_note_id uuid NOT NULL, mapping_version text NOT NULL,
             canonical_payload jsonb NOT NULL, source_hash char(64) NOT NULL,
             PRIMARY KEY (source_note_id, mapping_version)
           ) ON COMMIT DROP""",
        """CREATE TEMP TABLE lsr03_archive_manifest(
             source_note_id uuid NOT NULL, mapping_version text NOT NULL,
             expected_source_hash char(64) NOT NULL,
             PRIMARY KEY (source_note_id, mapping_version)
           ) ON COMMIT DROP""",
        """CREATE TEMP TABLE lsr03_live_source(
             source_note_id uuid NOT NULL, mapping_version text NOT NULL,
             source_hash char(64) NOT NULL,
             PRIMARY KEY (source_note_id, mapping_version)
           ) ON COMMIT DROP""",
        """CREATE TEMP TABLE lsr03_disposition(
             source_note_id uuid NOT NULL, mapping_version text NOT NULL,
             disposition text NOT NULL, source_hash char(64) NOT NULL,
             PRIMARY KEY (source_note_id, mapping_version)
           ) ON COMMIT DROP""",
    ):
        await connection.execute(text(ddl))

    for row in canonical_rows:
        params = {
            "source_note_id": row["source_note_id"],
            "mapping_version": MAPPING_VERSION,
            "canonical_payload": _canonical_json(row["canonical_payload"]),
            "source_hash": row["source_hash"],
        }
        await connection.execute(text("""
          INSERT INTO lsr03_source_snapshot
            (source_note_id,mapping_version,canonical_payload,source_hash)
          VALUES (:source_note_id,:mapping_version,CAST(:canonical_payload AS jsonb),:source_hash)
        """), params)
        await connection.execute(text("""
          INSERT INTO lsr03_live_source(source_note_id,mapping_version,source_hash)
          VALUES (:source_note_id,:mapping_version,:source_hash)
        """), params)
        await connection.execute(text("""
          INSERT INTO lsr03_disposition(source_note_id,mapping_version,disposition,source_hash)
          VALUES (:source_note_id,:mapping_version,'migrated_paused',:source_hash)
        """), params)
    return [
        {
            "source_note_id": str(row["source_note_id"]),
            "mapping_version": MAPPING_VERSION,
            "canonical_payload": row["canonical_payload"],
            "source_hash": str(row["source_hash"]),
        }
        for row in canonical_rows
    ]


async def _load_external_archive(connection: AsyncConnection, archive_dir: Path) -> None:
    archive_rows = _read_ndjson(archive_dir / ARCHIVE_NAME)
    manifest_rows = _read_ndjson(archive_dir / ARCHIVE_MANIFEST_NAME)
    if not archive_rows or not manifest_rows:
        raise AssertionError("archive and expected-hash manifest must both be non-empty")
    for row in archive_rows:
        await connection.execute(text("""
          INSERT INTO lsr03_archive_rows
            (source_note_id,mapping_version,canonical_payload,source_hash)
          VALUES (:source_note_id,:mapping_version,CAST(:canonical_payload AS jsonb),:source_hash)
        """), {**row, "canonical_payload": _canonical_json(row["canonical_payload"])})
    for row in manifest_rows:
        await connection.execute(text("""
          INSERT INTO lsr03_archive_manifest
            (source_note_id,mapping_version,expected_source_hash)
          VALUES (:source_note_id,:mapping_version,:expected_source_hash)
        """), row)


async def _relation_counts(connection: AsyncConnection) -> dict[str, int]:
    result = await connection.execute(text("""
      SELECT 'snapshot' AS scope,count(*)::int AS n FROM lsr03_source_snapshot
      UNION ALL SELECT 'archive',count(*)::int FROM lsr03_archive_rows
      UNION ALL SELECT 'manifest',count(*)::int FROM lsr03_archive_manifest
      UNION ALL SELECT 'live',count(*)::int FROM lsr03_live_source
      UNION ALL SELECT 'disposition',count(*)::int FROM lsr03_disposition
      ORDER BY scope
    """))
    return {row.scope: row.n for row in result}


async def _replay_mismatch(connection: AsyncConnection, archive_relation: str = "lsr03_archive_rows") -> tuple[int, int]:
    """Return (bidirectional EXCEPT rows, FULL OUTER missing/extra rows)."""
    # The relation name is a fixed internal constant, never user input.
    except_rows = await connection.scalar(text(f"""
      SELECT count(*) FROM (
        (SELECT source_note_id,mapping_version,source_hash FROM lsr03_source_snapshot
         EXCEPT SELECT source_note_id,mapping_version,source_hash FROM {archive_relation})
        UNION ALL
        (SELECT source_note_id,mapping_version,source_hash FROM {archive_relation}
         EXCEPT SELECT source_note_id,mapping_version,source_hash FROM lsr03_source_snapshot)
        UNION ALL
        (SELECT source_note_id,mapping_version,source_hash FROM lsr03_live_source
         EXCEPT SELECT source_note_id,mapping_version,source_hash FROM lsr03_disposition)
        UNION ALL
        (SELECT source_note_id,mapping_version,source_hash FROM lsr03_disposition
         EXCEPT SELECT source_note_id,mapping_version,source_hash FROM lsr03_live_source)
      ) differences
    """))
    full_outer = await connection.scalar(text(f"""
      SELECT count(*) FROM lsr03_source_snapshot s
      FULL OUTER JOIN {archive_relation} a
        ON a.source_note_id=s.source_note_id AND a.mapping_version=s.mapping_version
      WHERE s.source_note_id IS NULL OR a.source_note_id IS NULL
         OR s.source_hash IS DISTINCT FROM a.source_hash
         OR s.canonical_payload IS DISTINCT FROM a.canonical_payload
    """))
    return int(except_rows or 0), int(full_outer or 0)


async def _archive_manifest_mismatch(connection: AsyncConnection) -> int:
    """Compare every archive row with the independent expected-hash file."""
    result = await connection.scalar(text("""
      SELECT count(*) FROM lsr03_archive_rows a
      FULL OUTER JOIN lsr03_archive_manifest m
        ON m.source_note_id=a.source_note_id AND m.mapping_version=a.mapping_version
      WHERE a.source_note_id IS NULL OR m.source_note_id IS NULL
         OR a.source_hash IS DISTINCT FROM m.expected_source_hash
    """))
    return int(result or 0)


async def _negative_replay_fixtures(connection: AsyncConnection) -> dict[str, bool]:
    """Exercise tamper, missing, and extra rows in isolated temp relations."""
    await connection.execute(text(
        "CREATE TEMP TABLE lsr03_replay_probe ON COMMIT DROP AS TABLE lsr03_archive_rows"
    ))
    await connection.execute(text("""
      UPDATE lsr03_replay_probe SET source_hash=repeat('0',64)
       WHERE (source_note_id,mapping_version)=(
         SELECT source_note_id,mapping_version FROM lsr03_replay_probe LIMIT 1)
    """))
    tampered = await connection.scalar(text("""
      SELECT count(*) FROM lsr03_replay_probe p
      FULL OUTER JOIN lsr03_source_snapshot s USING (source_note_id,mapping_version)
      WHERE p.source_note_id IS NULL OR s.source_note_id IS NULL OR p.source_hash IS DISTINCT FROM s.source_hash
    """))
    await connection.execute(text("TRUNCATE lsr03_replay_probe"))
    await connection.execute(text("""
      INSERT INTO lsr03_replay_probe SELECT * FROM lsr03_archive_rows
       WHERE (source_note_id,mapping_version) <> (
         SELECT source_note_id,mapping_version FROM lsr03_archive_rows LIMIT 1)
    """))
    missing = await connection.scalar(text("""
      SELECT count(*) FROM lsr03_source_snapshot s
      FULL OUTER JOIN lsr03_replay_probe p USING (source_note_id,mapping_version)
      WHERE s.source_note_id IS NULL OR p.source_note_id IS NULL
    """))
    await connection.execute(text("""
      INSERT INTO lsr03_replay_probe(source_note_id,mapping_version,canonical_payload,source_hash)
      VALUES ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa','lsr03-fixture-extra','{}',repeat('a',64))
    """))
    extra = await connection.scalar(text("""
      SELECT count(*) FROM lsr03_source_snapshot s
      FULL OUTER JOIN lsr03_replay_probe p USING (source_note_id,mapping_version)
      WHERE s.source_note_id IS NULL OR p.source_note_id IS NULL
    """))
    return {
        "tamper_detected": bool(tampered),
        "missing_detected": bool(missing),
        "extra_detected": bool(extra),
    }


async def validate(database_url: str, artifact_dir: str | None = None) -> dict[str, Any]:
    """Run the positive archive/replay check and its isolated negatives."""
    created_temp = artifact_dir is None
    directory = Path(artifact_dir) if artifact_dir else Path(tempfile.mkdtemp(prefix="lsr03-archive-"))
    directory.mkdir(parents=True, exist_ok=True)
    run_id = str(uuid.uuid4())
    evaluation_dt = datetime.now(timezone.utc).replace(microsecond=datetime.now(timezone.utc).microsecond)
    evaluation_time = evaluation_dt.isoformat(timespec="microseconds").replace("+00:00", "Z")
    # The guarded runner accepts the psql spelling as well as asyncpg.  Keep
    # the verifier connection usable with the exact URL handed to the runner.
    adapter_database_url = _adapter_database_url(database_url)
    engine = create_async_engine(
        database_url.replace("postgresql://", "postgresql+asyncpg://", 1),
        poolclass=None,
    )
    adapter_engine = create_async_engine(adapter_database_url, poolclass=None)
    try:
        async with adapter_engine.connect() as adapter_connection:
            canonical_rows = await _canonical_source_rows(adapter_connection)
        async with engine.begin() as connection:
            archive_rows = await _create_temp_sources(connection, canonical_rows)
            _write_ndjson(directory / ARCHIVE_NAME, archive_rows)
            expected_lines = [
                {
                    "source_note_id": row["source_note_id"],
                    "mapping_version": row["mapping_version"],
                    "expected_source_hash": row["source_hash"],
                }
                for row in archive_rows
            ]
            _write_ndjson(directory / ARCHIVE_MANIFEST_NAME, expected_lines)
            run_manifest = {
                "run_id": run_id,
                "mapping_version": MAPPING_VERSION,
                "evaluation_time_utc": evaluation_time,
                "source_snapshot_version": "synthetic-notes-v1",
                "archive_rowcount": len(archive_rows),
                "archive_hash": _sha256((directory / ARCHIVE_NAME).read_text(encoding="utf-8")),
            }
            (directory / RUN_MANIFEST_NAME).write_text(
                _canonical_json(run_manifest) + "\n", encoding="utf-8", newline="\n"
            )
            await connection.execute(text("""
              INSERT INTO lsr03_run_manifest
                (run_id,mapping_version,evaluation_time_utc,source_snapshot_version,archive_rowcount,archive_hash)
              VALUES (:run_id,:mapping_version,:evaluation_time_utc,:source_snapshot_version,:archive_rowcount,:archive_hash)
            """), {**run_manifest, "evaluation_time_utc": evaluation_dt})
            await _load_external_archive(connection, directory)
            counts = await _relation_counts(connection)
            expected_count = int(run_manifest["archive_rowcount"])
            if set(counts) != {"snapshot", "archive", "manifest", "live", "disposition"}:
                raise AssertionError(f"incomplete five-way manifest: {counts}")
            if any(value != expected_count for value in counts.values()):
                raise AssertionError(f"five-way count mismatch: expected={expected_count}, actual={counts}")
            except_rows, full_outer = await _replay_mismatch(connection)
            archive_manifest_mismatch = await _archive_manifest_mismatch(connection)
            if except_rows or full_outer or archive_manifest_mismatch:
                raise AssertionError(
                    "positive replay mismatch: "
                    f"except={except_rows}, full_outer={full_outer}, "
                    f"archive_manifest={archive_manifest_mismatch}"
                )
            negative = await _negative_replay_fixtures(connection)
            if not all(negative.values()):
                raise AssertionError(f"negative replay fixture was not detected: {negative}")
            result = {
                "run_manifest": run_manifest,
                "counts": counts,
                "bidirectional_except_rows": except_rows,
                "full_outer_missing_or_extra": full_outer,
                "archive_manifest_mismatch": archive_manifest_mismatch,
                "negative": negative,
                "artifact_dir": str(directory),
                "temporary_artifact_dir": created_temp,
            }
            print(json.dumps(result, ensure_ascii=False, sort_keys=True))
            return result
    finally:
        await adapter_engine.dispose()
        await engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database-url", default=os.environ.get("LSR03_DATABASE_URL"))
    parser.add_argument("--artifact-dir")
    args = parser.parse_args()
    if not args.database_url:
        parser.error("--database-url or LSR03_DATABASE_URL is required")
    asyncio.run(validate(args.database_url, args.artifact_dir))


if __name__ == "__main__":
    main()
