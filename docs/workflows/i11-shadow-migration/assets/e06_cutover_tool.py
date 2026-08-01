#!/usr/bin/env python3
"""Fail-closed helpers for the bounded E-06 local authority cutover."""

from pathlib import Path


def validate_database_pair(source_database: str, target_database: str) -> tuple[str, str]:
    if source_database == target_database:
        raise ValueError("Source and cutover target databases must differ")
    if source_database != "blog_db":
        raise ValueError("Unexpected E-06 source database")
    if target_database != "blog_v2":
        raise ValueError("Unexpected E-06 cutover target database")
    return source_database, target_database


def rewrite_env_authority(
    env_text: str,
    *,
    expected_current_database: str = "blog_db",
    target_database: str,
    target_upload_root: str,
) -> str:
    lines = env_text.splitlines()
    database_indexes = [
        index for index, line in enumerate(lines) if line.startswith("DATABASE_URL=")
    ]
    if len(database_indexes) != 1:
        raise ValueError("Expected exactly one DATABASE_URL entry")

    index = database_indexes[0]
    prefix, raw_url = lines[index].split("=", 1)
    base, separator, database = raw_url.rpartition("/")
    if not separator or database != expected_current_database:
        raise ValueError("DATABASE_URL does not point to expected source")
    lines[index] = f"{prefix}={base}/{target_database}"

    upload_line = f"UPLOAD_ROOT={Path(target_upload_root)}"
    upload_indexes = [
        index for index, line in enumerate(lines) if line.startswith("UPLOAD_ROOT=")
    ]
    if len(upload_indexes) > 1:
        raise ValueError("Expected at most one UPLOAD_ROOT entry")
    if upload_indexes:
        lines[upload_indexes[0]] = upload_line
    else:
        lines.append(upload_line)
    return "\n".join(lines) + "\n"


def compare_snapshots(
    source: dict,
    target: dict,
    *,
    expected_source_revision: str,
    expected_target_revision: str,
) -> dict:
    source_rows = {
        (row["source_table"], row["source_id"]): row["source_row_hash"]
        for row in source["rows"]
    }
    target_rows = {
        (row["source_table"], row["source_id"]): row["source_row_hash"]
        for row in target["rows"]
    }
    source_keys = set(source_rows)
    target_keys = set(target_rows)
    shared = source_keys & target_keys
    inserted = target_keys - source_keys
    deleted = source_keys - target_keys
    updated = {key for key in shared if source_rows[key] != target_rows[key]}
    delta_count = len(inserted) + len(deleted) + len(updated)
    revisions_match = (
        source["database_revision"] == expected_source_revision
        and target["database_revision"] == expected_target_revision
    )
    return {
        "source_revision": source["database_revision"],
        "target_revision": target["database_revision"],
        "source_count": len(source_rows),
        "target_count": len(target_rows),
        "inserted_count": len(inserted),
        "updated_count": len(updated),
        "deleted_count": len(deleted),
        "delta_count": delta_count,
        "aggregate_match": (
            source["aggregate_sha256"] == target["aggregate_sha256"]
        ),
        "passed": (
            revisions_match
            and delta_count == 0
            and source["aggregate_sha256"] == target["aggregate_sha256"]
        ),
    }
