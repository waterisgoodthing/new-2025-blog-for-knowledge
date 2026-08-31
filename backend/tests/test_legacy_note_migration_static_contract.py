import re
from pathlib import Path


MIGRATION = Path(__file__).parents[1] / "alembic" / "versions" / "026_legacy_system_retirement.py"
ADAPTER = Path(__file__).parents[1] / "app" / "services" / "legacy_note_migration_adapter.py"


def test_026_mirror_helpers_use_provenance_and_compare_question_contract() -> None:
    source = MIGRATION.read_text()
    assert "v_source_raw::jsonb" in source
    assert "v_meta->>'source_note_id'" in source
    assert "v_source_note->'mirror_contract'" in source
    for field in ("subject_id", "question_text", "stem_md", "question_type", "options", "difficulty", "correct_answer", "analysis_md", "explanation"):
        assert f"v_question.{field}" in source
    assert "jsonb_build_object('kind','true_false','value',true)" in source


def test_026_mirror_binds_active_private_v1_and_rethrows_unknown_errors() -> None:
    source = MIGRATION.read_text()
    mirror = source.split("CREATE FUNCTION legacy_migration.legacy_question_mirror_matches", 1)[1]
    mirror = mirror.split("CREATE TABLE", 1)[0]
    assert "v_question.status IS DISTINCT FROM 'active'" in mirror
    assert "v_question.visibility IS DISTINCT FROM 'private'" in mirror
    assert "v_question.version IS DISTINCT FROM 1" in mirror
    assert "v_source.question_id IS DISTINCT FROM p_question_id" in mirror
    assert "legacy_migration.legacy_question_source_matches" in mirror
    assert "WHEN others THEN RETURN FALSE" not in mirror


def test_026_mirror_sql_validates_answer_options_independently() -> None:
    source = MIGRATION.read_text()
    mirror = source.split("CREATE FUNCTION legacy_migration.legacy_question_mirror_matches", 1)[1]
    mirror = mirror.split("CREATE TABLE", 1)[0]
    assert "v_options := to_jsonb(v_question.options)" in mirror
    assert "jsonb_array_length(v_options)<2" in mirror
    assert "jsonb_object_length(e.value)<>2" in mirror
    assert "CASE WHEN jsonb_typeof(e.value)='object'" in mirror
    assert "count(DISTINCT e.value->>'key')" in mirror
    assert "v_question.question_type::text IN ('short_answer','true_false')" in mirror
    assert "v_question.correct_answer" in mirror
    assert "v_answer_parts" in mirror
    assert "v_meta->'answer_data' IS NOT DISTINCT FROM v_expected" in mirror


def test_026_pending_recomputes_and_binds_the_frozen_idempotency_key() -> None:
    source = MIGRATION.read_text()
    pending = source.split("CREATE FUNCTION legacy_migration.create_legacy_note_migration_pending", 1)[1]
    pending = pending.split("CREATE FUNCTION legacy_migration.record_legacy_note_migration_approval", 1)[0]
    assert "legacy-note-migration|" in pending
    assert "convert_to" in pending and "'UTF8'" in pending
    assert "p_idempotency_key IS DISTINCT FROM" in pending
    assert "LEGACY_MIGRATION_IDEMPOTENCY_CONFLICT" in pending


def test_026_sql_options_and_answer_helpers_match_python_invariants() -> None:
    source = MIGRATION.read_text()
    options = source.split("CREATE FUNCTION legacy_migration.legacy_question_options_normalize", 1)[1]
    options = options.split("CREATE FUNCTION legacy_migration.legacy_question_answer_data_expected", 1)[0]
    answer = source.split("CREATE FUNCTION legacy_migration.legacy_question_answer_data_expected", 1)[1]
    answer = answer.split("CREATE FUNCTION legacy_migration.legacy_question_source_matches", 1)[0]
    assert "btrim(v#>>'{}')<>''" in options
    assert "btrim(v->>'key')<>''" in options
    assert "btrim(v->>'text')<>''" in options
    assert "position(',' IN p_correct_answer)>0" in answer
    assert "HAVING count(*)>1" in answer


def test_026_retained_transition_rejects_any_target_schedule_or_rollback_state() -> None:
    source = MIGRATION.read_text()
    transition = source.split("CREATE FUNCTION legacy_migration.transition_legacy_note_migration", 1)[1]
    transition = transition.split("CREATE FUNCTION legacy_migration.load_legacy_migration_rollback_audit", 1)[0]
    assert "p_target_bundle.target_question_id IS NOT NULL" in transition
    assert "p_target_bundle.target_mistake_draft_id IS NOT NULL" in transition
    assert "p_target_bundle.target_qkp_ids IS NOT NULL" in transition
    assert "p_target_bundle.target_projection_ids IS NOT NULL" in transition
    assert "p_mapped_next_review_at IS NOT NULL" in transition
    assert "p_rollback_reference IS NOT NULL" in transition
    assert "m.target_bundle_hash IS NOT NULL" in transition
    assert "m.source_approved_at IS NULL" in transition
    assert "m.source_approval_sequence IS NULL" in transition
    assert "m.approved_by IS DISTINCT FROM m.source_approved_by" in transition
    assert "m.approved_at IS DISTINCT FROM m.source_approved_at" in transition
    for slot in (
        "m.question_conversion_approved_by", "m.question_conversion_approved_at",
        "m.question_conversion_sequence", "m.question_approval_event_id",
        "m.mistake_conversion_approved_by", "m.mistake_conversion_approved_at",
        "m.mistake_conversion_sequence", "m.mistake_approval_event_id",
        "m.schedule_approved_by", "m.schedule_approved_at", "m.schedule_approval_sequence",
        "m.schedule_approval_event_id", "m.rollback_actor_id", "m.rollback_event_id",
    ):
        assert f"{slot} IS NOT NULL" in transition


def test_adapter_retained_bundle_uses_sql_null_arrays() -> None:
    source = ADAPTER.read_text()
    retained = source.split("if should_retain_public_only", 1)[1]
    retained = retained.split("bundle_args", 1)[0]
    assert "NULL::integer[]" in retained
    assert "ARRAY[]::integer[]" not in retained


def test_adapter_result_preserves_null_target_arrays_for_retained_rows() -> None:
    source = ADAPTER.read_text()
    assert "target_qkp_ids: tuple[int, ...] | None" in source
    assert "target_projection_ids: tuple[int, ...] | None" in source
    assert 'target_qkp_ids=None if row["target_qkp_ids"] is None else tuple(row["target_qkp_ids"])' in source
    assert 'target_projection_ids=None if row["target_projection_ids"] is None else tuple(row["target_projection_ids"])' in source


def test_adapter_active_schedule_uses_one_explicit_utc_instant() -> None:
    source = ADAPTER.read_text()
    assert "datetime.now" not in source
    assert "mapped_next_review_at = _validate_schedule(" in source
    assert "next_review_at=mapped_next_review_at" in source
    assert '"next_review": mapped_next_review_at' in source


def test_026_retained_ledger_shape_check_blocks_direct_writes() -> None:
    source = MIGRATION.read_text()
    assert "ck_legacy_note_migrations_retained_shape" in source
    assert "ALTER TABLE public.legacy_note_migrations\n          ADD CONSTRAINT" in source
    assert "state <> 'retained_public_only'" in source
    assert "target_qkp_ids IS NULL AND target_projection_ids IS NULL" in source
    assert "approved_by IS NOT DISTINCT FROM source_approved_by" in source
    assert "transition_event_id" in source


def test_026_rollback_deletes_mistake_projection_links_before_mistake_rows() -> None:
    source = MIGRATION.read_text()
    rollback = source.split("IF p_to='rolled_back'", 1)[1]
    projection_delete = "DELETE FROM public.knowledge_point_links\n             WHERE target_type='mistake' AND target_id=m.target_mistake_id::text;"
    assert projection_delete in rollback
    assert rollback.index(projection_delete) < rollback.index("DELETE FROM public.mistakes WHERE id=m.target_mistake_id;")


def test_026_owner_acl_allows_only_owner_projection_delete() -> None:
    source = MIGRATION.read_text()
    statements = [
        statement
        for statement in re.findall(r"\b(?:GRANT|REVOKE)\b.*?;", source, re.IGNORECASE | re.DOTALL)
        if "public.knowledge_point_links" in statement
    ]
    revoke = next(
        (
            statement
            for statement in statements
            if re.match(r"\s*REVOKE\s+(?:DELETE|ALL)", statement, re.IGNORECASE)
        ),
        None,
    )
    assert revoke is not None
    denied_roles = {
        "PUBLIC", "app_role", "legacy_note_adapter", "legacy_note_adapter_runner",
        "legacy_migration_maintenance_runner", "legacy_note_verifier",
    }
    revoked_roles = {
        role.strip().lower()
        for role in re.split(r"\s*,\s*", re.search(r"\bFROM\b(.*?);", revoke, re.IGNORECASE | re.DOTALL).group(1))
    }
    assert {role.lower() for role in denied_roles} <= revoked_roles
    for statement in statements:
        grant_match = re.match(
            r"\s*GRANT\s+(.*?)\s+ON\s+.*?\bpublic\.knowledge_point_links\b.*?\bTO\b(.*?);",
            statement,
            re.IGNORECASE | re.DOTALL,
        )
        if not grant_match or not re.search(r"\b(?:DELETE|ALL)\b", grant_match.group(1), re.IGNORECASE):
            continue
        grantees = {role.strip().lower() for role in re.split(r"\s*,\s*", grant_match.group(2))}
        assert grantees == {"legacy_migration_owner"}


def test_026_nonce_cleanup_function_is_maintenance_only_and_consumed_scoped() -> None:
    source = MIGRATION.read_text()
    assert "CREATE FUNCTION legacy_migration.cleanup_legacy_migration_guard_nonces(" in source
    cleanup = source.split("CREATE FUNCTION legacy_migration.cleanup_legacy_migration_guard_nonces(", 1)[1]
    cleanup = cleanup.split("CREATE FUNCTION legacy_migration.set_legacy_transition_marker(", 1)[0]
    assert "p_cutoff TIMESTAMPTZ, p_limit INTEGER" in cleanup
    assert "RETURNS INTEGER" in cleanup
    assert "SECURITY DEFINER" in cleanup
    assert "SET search_path=pg_catalog,legacy_migration" in cleanup
    assert "current_user IS DISTINCT FROM 'legacy_migration_owner'" in cleanup
    assert "session_user IS DISTINCT FROM 'legacy_migration_maintenance_runner'" in cleanup
    assert "consumed_at IS NOT NULL AND consumed_at < p_cutoff" in cleanup
    assert "FOR UPDATE SKIP LOCKED" in cleanup
    assert "LIMIT p_limit" in cleanup
    assert "DELETE FROM legacy_migration.legacy_migration_guard_nonces" in cleanup
    assert "REVOKE ALL ON legacy_migration.legacy_migration_guard_nonces" in source
    assert "REVOKE TRUNCATE ON legacy_migration.legacy_migration_guard_nonces" in source
    next_function = "CREATE FUNCTION legacy_migration.set_legacy_transition_marker("
    flush_call = source.index("\n    _flush_deferred()\n", source.index(next_function))
    acl = source[flush_call:]
    assert "REVOKE ALL ON FUNCTION legacy_migration.cleanup_legacy_migration_guard_nonces(TIMESTAMPTZ,INTEGER)" in acl
    assert "TO legacy_migration_maintenance_runner" in acl
    assert "ALTER FUNCTION legacy_migration.cleanup_legacy_migration_guard_nonces(TIMESTAMPTZ,INTEGER)" in acl
    for role in ("PUBLIC", "app_role", "legacy_note_adapter", "legacy_note_adapter_runner", "legacy_note_verifier"):
        assert role in acl


def test_026_nonce_cleanup_acl_runs_after_deferred_function_flush() -> None:
    source = MIGRATION.read_text()
    create_marker = "CREATE FUNCTION legacy_migration.cleanup_legacy_migration_guard_nonces("
    next_function = "CREATE FUNCTION legacy_migration.set_legacy_transition_marker("
    create_start = source.index(create_marker)
    create_end = source.index(next_function, create_start)
    create_section = source[create_start:create_end]
    flush_call = source.index("\n    _flush_deferred()\n", create_end)
    late_section = source[flush_call:]
    signature = "legacy_migration.cleanup_legacy_migration_guard_nonces(TIMESTAMPTZ,INTEGER)"

    assert "REVOKE ALL ON FUNCTION " + signature not in create_section
    assert "GRANT EXECUTE ON FUNCTION " + signature not in create_section
    assert "ALTER FUNCTION " + signature not in create_section
    assert "ALTER FUNCTION " + signature in late_section
    assert "REVOKE ALL ON FUNCTION " + signature in late_section
    assert "GRANT EXECUTE ON FUNCTION " + signature in late_section


def test_026_nonce_cleanup_exact_signature_acl_rejects_any_nonmaintenance_grant() -> None:
    source = MIGRATION.read_text()
    signature = "legacy_migration.cleanup_legacy_migration_guard_nonces(TIMESTAMPTZ,INTEGER)"

    def acl_is_closed(sql: str) -> bool:
        statements = [
            statement
            for statement in re.findall(r"\b(?:GRANT|REVOKE)\b.*?;", sql, re.IGNORECASE | re.DOTALL)
            if signature in statement
        ]
        saw_maintenance_grant = False
        for statement in statements:
            grant_match = re.match(
                r"\s*GRANT\s+(.*?)\s+ON\s+FUNCTION\s+" + re.escape(signature) + r"\s+TO\s+(.*?);",
                statement,
                re.IGNORECASE | re.DOTALL,
            )
            if grant_match and re.search(r"\b(?:EXECUTE|ALL)\b", grant_match.group(1), re.IGNORECASE):
                grantees = {role.strip().lower() for role in re.split(r"\s*,\s*", grant_match.group(2))}
                if grantees != {"legacy_migration_maintenance_runner"}:
                    return False
                saw_maintenance_grant = True
                continue
            revoke_match = re.match(
                r"\s*REVOKE\s+(.*?)\s+ON\s+FUNCTION\s+" + re.escape(signature) + r"\s+FROM\s+(.*?);",
                statement,
                re.IGNORECASE | re.DOTALL,
            )
            if revoke_match and re.search(r"\b(?:EXECUTE|ALL)\b", revoke_match.group(1), re.IGNORECASE):
                revoked = {role.strip().lower() for role in re.split(r"\s*,\s*", revoke_match.group(2))}
                if "legacy_migration_maintenance_runner" in revoked:
                    return False
        return saw_maintenance_grant

    assert acl_is_closed(source)
    for role in ("PUBLIC", "app_role", "legacy_note_adapter", "legacy_note_adapter_runner", "legacy_note_verifier"):
        tampered = source + f"\nGRANT EXECUTE ON FUNCTION {signature} TO {role};\n"
        assert not acl_is_closed(tampered)
