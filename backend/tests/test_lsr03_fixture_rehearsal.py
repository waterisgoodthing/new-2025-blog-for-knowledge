import asyncio
import ast
import os
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

import pytest

from tests.lsr03_fixture_rehearsal import run
from tests.lsr03_validation_helper import _adapter_database_url, validate


FIXTURE_DIR = Path(__file__).parent


def _function_source(filename: str, function_name: str) -> str:
    source = (FIXTURE_DIR / filename).read_text()
    tree = ast.parse(source, filename=filename)
    function = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef))
        and node.name == function_name
    )
    return ast.get_source_segment(source, function) or ""


def _database_url() -> str:
    return os.environ.get("LSR03_DATABASE_URL", "")


def test_archive_canonicalization_uses_adapter_identity_but_replay_keeps_verifier_identity() -> None:
    helper = (FIXTURE_DIR / "lsr03_validation_helper.py").read_text()
    validate_source = _function_source("lsr03_validation_helper.py", "validate")
    temp_source = _function_source("lsr03_validation_helper.py", "_create_temp_sources")

    assert "legacy_note_adapter_runner" in helper
    assert "127.0.0.1" in helper
    assert "55432" in helper
    assert "/lsr03_" in helper
    assert "adapter_database_url = _adapter_database_url(database_url)" in validate_source
    assert "canonical_rows = await _canonical_source_rows(adapter_connection)" in validate_source
    assert "await _create_temp_sources(connection, canonical_rows)" in validate_source
    assert "canonicalize_legacy_note" not in temp_source


def test_adapter_url_preserves_isolated_target_without_password_or_identity_drift() -> None:
    adapter_url = _adapter_database_url(
        "postgresql+asyncpg://fixture_admin@127.0.0.1:55432/lsr03_fixture"
    )
    parsed = urlsplit(adapter_url)
    assert parsed.username == "legacy_note_adapter_runner"
    assert parsed.password is None
    assert parsed.hostname == "127.0.0.1"
    assert parsed.port == 55432
    assert parsed.path == "/lsr03_fixture"


def test_adapter_url_strips_temporary_password_and_rejects_non_isolated_targets() -> None:
    temporary_secret = "temporary-secret"
    adapter_url = _adapter_database_url(
        f"postgresql+asyncpg://fixture_admin:{temporary_secret}@127.0.0.1:55432/lsr03_fixture"
    )
    parsed = urlsplit(adapter_url)
    assert parsed.username == "legacy_note_adapter_runner"
    assert parsed.password is None
    assert temporary_secret not in adapter_url
    with pytest.raises(ValueError, match="127.0.0.1:55432"):
        _adapter_database_url("postgresql+asyncpg://fixture_admin@localhost:5432/blog_v2")


def test_synthetic_negative_fixture_matrix_isolated_only() -> None:
    database_url = _database_url()
    if not database_url:
        pytest.skip("LSR03_DATABASE_URL is required for isolated fixture tests")
    result = asyncio.run(run(database_url))
    assert all(result["nonce"].values())
    assert all(result["collisions"].values())
    assert all(result["chapters"].values())
    assert result["inbound"]["rollback_result"].startswith("SNAPSHOT_RESTORE_REQUIRED")


def test_external_archive_manifest_replay_isolated_only() -> None:
    database_url = _database_url()
    if not database_url:
        pytest.skip("LSR03_DATABASE_URL is required for isolated archive tests")
    with tempfile.TemporaryDirectory(prefix="lsr03-test-archive-") as directory:
        result = asyncio.run(validate(database_url, directory))
    assert result["counts"] == {
        "archive": result["run_manifest"]["archive_rowcount"],
        "disposition": result["run_manifest"]["archive_rowcount"],
        "live": result["run_manifest"]["archive_rowcount"],
        "manifest": result["run_manifest"]["archive_rowcount"],
        "snapshot": result["run_manifest"]["archive_rowcount"],
    }
    assert result["bidirectional_except_rows"] == 0
    assert result["full_outer_missing_or_extra"] == 0
    assert result["archive_manifest_mismatch"] == 0
    assert all(result["negative"].values())
