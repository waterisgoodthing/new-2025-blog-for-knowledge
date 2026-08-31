"""No-DB contract checks for the LSR-03 actual-table rollback harness.

These checks intentionally inspect source only.  They are the preflight gate
for a future fresh isolated run and must never require ``LSR03_DATABASE_URL``.
"""

from __future__ import annotations

import ast
import os
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[2]
ROLLBACK = ROOT / "backend/tests/lsr03_rollback_rehearsal.py"
MIGRATION = ROOT / "backend/alembic/versions/026_legacy_system_retirement.py"
GUARDED_RUNNER = ROOT / "backend/tests/lsr03_guarded_runner.py"
SEED_HELPER = ROOT / "backend/tests/lsr03_seed_rehearsal.py"
VALIDATION = ROOT / "docs/workflows/legacy-system-retirement/validation.md"


def _function_source(name: str) -> str:
    tree = ast.parse(ROLLBACK.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return ast.get_source_segment(ROLLBACK.read_text(encoding="utf-8"), node) or ""
    raise AssertionError(f"missing helper: {name}")


def _function_node(name: str) -> ast.FunctionDef | ast.AsyncFunctionDef:
    tree = ast.parse(ROLLBACK.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    raise AssertionError(f"missing helper: {name}")


def _called_names(node: ast.AST) -> set[str]:
    return {
        call.func.id
        for call in ast.walk(node)
        if isinstance(call, ast.Call) and isinstance(call.func, ast.Name)
    }


def test_actual_fixture_does_not_read_ledger_as_adapter_runner() -> None:
    source = _function_source("run_inbound_fixtures")
    adapter_block = source[source.index("async with adapter_maker() as adapter:"):source.index("async with admin_maker() as cleanup:")]
    assert "_rollback_attempt(adapter, baseline, label)" in adapter_block
    assert "legacy_note_migrations" not in adapter_block
    assert "SELECT current_database()" not in adapter_block


def test_actual_fixture_binds_every_inbound_edge_to_mistake_draft_item() -> None:
    source = _function_source("run_inbound_fixtures")
    setup = source[source.index("for label in"):source.index("if not all(")]
    assert setup.count('baseline["target_mistake_draft_item_id"]') >= 2
    assert 'baseline["target_question_draft_item_id"]' not in setup
    rollback = _function_source("_rollback_attempt")
    assert '"mditem": row["target_mistake_draft_item_id"]' in rollback


def test_actual_fixture_exposes_identity_zero_mutation_and_cleanup_evidence() -> None:
    source = _function_source("run_inbound_fixtures")
    assert "admin_identity = await _identity" in source
    assert 'adapter_identity = await _identity(adapter, "legacy_note_adapter_runner", parsed.database)' in source
    assert "zero_mutation = await _assert_zero_mutation" in source
    assert "await _assert_cleanup(cleanup, baseline, label)" in source
    assert 'baseline["target_mistake_draft_id"]' in source
    assert '"cleanup_zero": True' in source


def test_baseline_and_after_use_the_same_full_ledger_snapshot_helper() -> None:
    run_source = _function_source("run_inbound_fixtures")
    run_node = _function_node("run_inbound_fixtures")
    baseline_calls = [
        call
        for call in ast.walk(run_node)
        if isinstance(call, ast.Call)
        and isinstance(call.func, ast.Name)
        and call.func.id == "_ledger_snapshot"
    ]
    assert len(baseline_calls) == 1
    assert isinstance(baseline_calls[0].args[0], ast.Name)
    assert baseline_calls[0].args[0].id == "admin"
    assert isinstance(baseline_calls[0].args[1], ast.Name)
    assert baseline_calls[0].args[1].id == "baseline_id"
    assert "SELECT id,source_note_id,mapping_version" not in run_source

    zero_source = _function_source("_assert_zero_mutation")
    assert "after = await _ledger_snapshot(session, baseline[\"id\"])" in zero_source


def test_main_selects_the_unique_active_ledger_for_logical_rollback() -> None:
    source = _function_source("main")
    selector_start = source.index("SELECT id,source_note_id,mapping_version,source_hash,state")
    selector_end = source.index(
        '"""), {"source": ACTIVE_SOURCE})).mappings().one()', selector_start
    )
    selector = source[selector_start:selector_end]
    assert "WHERE source_note_id=:source" in selector
    assert "mapping_version='v1-active'" in selector
    assert "state='migrated_active'" in selector
    assert ".mappings().one()" in source[selector_end:]
    assert "LIMIT" not in selector


def test_both_ledger_selectors_bind_source_mapping_and_state() -> None:
    for function_name, mapping, state in (
        ("run_inbound_fixtures", "v1-paused", "migrated_paused"),
        ("main", "v1-active", "migrated_active"),
    ):
        source = _function_source(function_name)
        assert "source_note_id=:source" in source
        assert f"mapping_version='{mapping}'" in source
        assert f"state='{state}'" in source
        expected_source = "BASELINE_SOURCE" if function_name == "run_inbound_fixtures" else "ACTIVE_SOURCE"
        assert f'"source": {expected_source}' in source
    assert ".scalar_one()" in _function_source("run_inbound_fixtures")


def test_main_uses_structured_adapter_role_url_without_legacy_username_replacement() -> None:
    source = _function_source("main")
    assert '_role_url(os.environ["LSR03_DATABASE_URL"], "legacy_note_adapter_runner")' in source
    assert 'replace("limengyang@"' not in source


def test_structured_adapter_role_url_strips_password_without_target_drift() -> None:
    from tests.lsr03_rollback_rehearsal import _asyncpg_url, _role_url

    raw = "postgresql://fixture_admin:temporary-secret@127.0.0.1:55432/lsr03_fixture"
    parsed = urlsplit(_asyncpg_url(_role_url(raw, "legacy_note_adapter_runner")))
    assert parsed.scheme == "postgresql+asyncpg"
    assert parsed.username == "legacy_note_adapter_runner"
    assert parsed.password is None
    assert parsed.hostname == "127.0.0.1"
    assert parsed.port == 55432
    assert parsed.path == "/lsr03_fixture"
    assert "temporary-secret" not in parsed.geturl()


def test_seed_helper_freezes_r6_ids_and_precedes_actual_rehearsal_recipe() -> None:
    source = SEED_HELPER.read_text(encoding="utf-8")
    rollback = ROLLBACK.read_text(encoding="utf-8")
    workflow = VALIDATION.read_text(encoding="utf-8")
    for value in (
        "11111111-1111-4111-8111-111111111111",
        "22222222-2222-4222-8222-222222222222",
        "33333333-3333-4333-8333-333333333333",
        "44444444-4444-4444-8444-444444444445",
        "55555555-5555-4555-8555-555555555555",
    ):
        assert value in source
    assert 'BASELINE_SOURCE = uuid.UUID("44444444-4444-4444-8444-444444444445")' in rollback
    assert 'ACTIVE_SOURCE = uuid.UUID("88888888-8888-4888-8888-888888888888")' in rollback
    assert "LSR03_SEED_TARGET_NOT_EMPTY" in source
    assert "json.dumps" in source
    seed_command = "tests/lsr03_seed_rehearsal.py"
    rehearsal_command = "tests/lsr03_rollback_rehearsal.py --inbound-fixtures"
    assert seed_command in workflow
    assert rehearsal_command in workflow
    assert workflow.index(seed_command) < workflow.index(rehearsal_command)


def test_seed_helper_binds_every_paused_baseline_identity_and_fails_before_db_import() -> None:
    source = SEED_HELPER.read_text(encoding="utf-8")
    tree = ast.parse(source)
    top_level_imports = [
        node.module or ""
        for node in tree.body
        if isinstance(node, ast.ImportFrom)
    ]
    assert "sqlalchemy" not in top_level_imports
    assert "app.services.legacy_note_migration_adapter" not in top_level_imports
    baseline_start = source.index("async def _create_paused_baseline")
    baseline_source = source[baseline_start:]
    for value in (
        "source_note_id=BASELINE_SOURCE",
        "source_approved_by=SOURCE_ACTOR",
        "question_conversion_approved_by=QUESTION_ACTOR",
        "mistake_conversion_approved_by=MISTAKE_ACTOR",
        "mapping_version=\"v1-paused\"",
    ):
        assert value in baseline_source
    for table in (
        "legacy_migration_approval_authorizations",
        "legacy_migration_rollback_admins",
    ):
        assert table in source
    main_source = source[source.index("async def main"):]
    assert main_source.index("_require_guarded_invocation(raw)") < main_source.index("identity_probe(raw)")
    assert main_source.index("identity_probe(raw)") < main_source.index("_seed_source_data(raw)")


def test_migration_guard_checks_the_same_three_inbound_edges() -> None:
    source = MIGRATION.read_text(encoding="utf-8")
    assert "c.mistake_draft_item_id=m.target_mistake_draft_item_id" in source
    assert "a.mistake_draft_item_id=m.target_mistake_draft_item_id" in source
    assert "d.id=m.target_mistake_draft_id AND d.attempt_id IS NOT NULL" in source
    assert "LEGACY_MIGRATION_UNEXPECTED_INBOUND_REFERENCE_SNAPSHOT_RESTORE_REQUIRED" in source


def test_rollback_audit_snapshot_orders_by_the_026_primary_key() -> None:
    migration = MIGRATION.read_text(encoding="utf-8")
    ddl_start = migration.index("CREATE TABLE public.legacy_migration_rollback_audits")
    ddl_end = migration.index("        );", ddl_start)
    rollback_audit_ddl = migration[ddl_start:ddl_end]
    assert "ledger_id UUID PRIMARY KEY" in rollback_audit_ddl

    helper_node = _function_node("_audit_event_snapshot")
    sql_literals = [
        node.value
        for node in ast.walk(helper_node)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    ]
    audit_queries = [value for value in sql_literals if "legacy_migration_rollback_audits" in value]
    assert len(audit_queries) == 1
    assert "ORDER BY ledger_id" in audit_queries[0]
    assert "ORDER BY id" not in audit_queries[0]


def test_guard_runner_is_fail_closed_before_any_child_command() -> None:
    source = GUARDED_RUNNER.read_text(encoding="utf-8")
    assert 'if parsed.hostname != "127.0.0.1"' in source
    assert "if parsed.port != 55432" in source
    assert 'if not parsed.path.startswith("/lsr03_")' in source
    assert 'env["DATABASE_URL"] = parsed.raw' in source
    assert "identity_probe(env[\"LSR03_DATABASE_URL\"])" in source


def test_rehearsal_guard_and_zero_mutation_contract_are_structural() -> None:
    url_guard = _called_names(_function_node("_validate_rehearsal_url"))
    assert {"parse_isolated_url"}.issubset(url_guard)
    run_node = _function_node("run_inbound_fixtures")
    probe_lines = [node.lineno for node in ast.walk(run_node) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "identity_probe"]
    engine_lines = [node.lineno for node in ast.walk(run_node) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "create_async_engine"]
    assert probe_lines and engine_lines and min(probe_lines) < min(engine_lines)
    zero_calls = _called_names(_function_node("_assert_zero_mutation"))
    assert {"_ledger_snapshot", "_relation_snapshot", "_audit_event_snapshot"}.issubset(zero_calls)
    relation_source = _function_source("_relation_snapshot")
    assert "for name, table, key, value in (" in relation_source
    assert '"capture", "capture_items"' in relation_source
    assert '"attempt", "attempts"' in relation_source
    assert '"mistake_draft", "mistake_drafts"' in relation_source
    assert '"attachment", "attachments"' in relation_source


def test_url_guard_rejects_non_isolated_or_conflicting_identity_without_connecting() -> None:
    original = {key: os.environ.get(key) for key in ("LSR03_DATABASE_URL", "DATABASE_URL")}
    valid = "postgresql://fixture_admin:secret@127.0.0.1:55432/lsr03_static"
    node = _function_node("_validate_rehearsal_url")

    class Parsed:
        username = "fixture_admin"
        database = "lsr03_static"

    def fake_parse(raw: str):
        from urllib.parse import urlsplit

        parsed = urlsplit(raw)
        if parsed.scheme not in {"postgresql", "postgresql+asyncpg"} or parsed.hostname != "127.0.0.1" or parsed.port != 55432 or not parsed.path.startswith("/lsr03_"):
            raise ValueError("not an isolated URL")
        return Parsed()

    namespace = {"os": os, "GuardError": ValueError, "parse_isolated_url": fake_parse}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(ROLLBACK), "exec"), namespace)
    validate = namespace["_validate_rehearsal_url"]
    try:
        os.environ["LSR03_DATABASE_URL"] = valid
        os.environ["DATABASE_URL"] = valid
        assert validate(valid).database == "lsr03_static"
        for invalid in (
            "postgresql://fixture_admin:secret@127.0.0.1:5432/lsr03_static",
            "postgresql://fixture_admin:secret@localhost:55432/lsr03_static",
            "postgresql://fixture_admin:secret@127.0.0.1:55432/blog_v2",
        ):
            try:
                validate(invalid)
            except ValueError:
                pass
            else:
                raise AssertionError(f"invalid URL accepted: {invalid}")
        os.environ["DATABASE_URL"] = "postgresql://other@127.0.0.1:55432/lsr03_static"
        try:
            validate(valid)
        except ValueError:
            pass
        else:
            raise AssertionError("conflicting DATABASE_URL accepted")
    finally:
        for key, value in original.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def test_logical_rollback_emits_single_json_replay_evidence() -> None:
    source = _function_source("main")
    assert "json.dumps" in source
    assert '"rollback_ledger_state"' in source
    assert '"target_question_id"' in source
    assert '"target_mistake_id"' in source
    assert '"pre_rollback_target_counts"' in source
    assert '"rollback_event"' in source
    assert '"rollback_audit"' in source
    assert '"rollback_replay"' in source
    assert "rollback_reference" in source
    assert "rollback_hash" in source
    assert "rollback_actor_id" in source
    assert "rollback_audit_digest" in source
    assert "source_hash" in source
    assert "mapping_version" in source
