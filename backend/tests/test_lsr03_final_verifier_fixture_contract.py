"""No-DB contract checks for the task-local synthetic source fixtures."""

import ast
from pathlib import Path

from tests.lsr03_final_verifier_harness import (
    SYNTHETIC_CORRECT_ANSWER as HARNESS_CORRECT,
    SYNTHETIC_MY_ANSWER as HARNESS_MY,
    SYNTHETIC_OPTIONS as HARNESS_OPTIONS,
    MISTAKE_ACTOR as HARNESS_MISTAKE_ACTOR,
    QUESTION_ACTOR as HARNESS_QUESTION_ACTOR,
    SCHEDULE_ACTOR as HARNESS_SCHEDULE_ACTOR,
    SOURCE_ACTOR as HARNESS_SOURCE_ACTOR,
)
from tests.lsr03_rehearsal import (
    MISTAKE,
    QUESTION,
    SCHEDULE_ACTOR as REHEARSAL_SCHEDULE_ACTOR,
    SOURCE,
)
from tests.lsr03_rollback_rehearsal import ROLLBACK_ACTOR as REHEARSAL_ROLLBACK_ACTOR
from tests.lsr03_seed_rehearsal import (
    MISTAKE_ACTOR as SEED_MISTAKE_ACTOR,
    QUESTION_ACTOR as SEED_QUESTION_ACTOR,
    ROLLBACK_ACTOR as SEED_ROLLBACK_ACTOR,
    SCHEDULE_ACTOR as SEED_SCHEDULE_ACTOR,
    SOURCE_ACTOR as SEED_SOURCE_ACTOR,
    SYNTHETIC_CORRECT_ANSWER as SEED_CORRECT,
    SYNTHETIC_MY_ANSWER as SEED_MY,
    SYNTHETIC_OPTIONS as SEED_OPTIONS,
)


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


def test_single_choice_fixture_answers_are_option_keys() -> None:
    for options, my_answer, correct_answer in (
        (SEED_OPTIONS, SEED_MY, SEED_CORRECT),
        (HARNESS_OPTIONS, HARNESS_MY, HARNESS_CORRECT),
    ):
        keys = {item["key"] for item in options}
        assert len(keys) == len(options) >= 2
        assert correct_answer in keys
        assert my_answer in keys


def test_approval_actor_matrix_is_shared_across_fixtures() -> None:
    """All fixture entry points must use the seed authorization identities."""
    authorized = {
        "SOURCE": str(SEED_SOURCE_ACTOR),
        "QUESTION": str(SEED_QUESTION_ACTOR),
        "MISTAKE": str(SEED_MISTAKE_ACTOR),
        "SCHEDULE": str(SEED_SCHEDULE_ACTOR),
        "ROLLBACK": str(SEED_ROLLBACK_ACTOR),
    }
    fixture_matrix = {
        "rehearsal": {
            "SOURCE": str(SOURCE),
            "QUESTION": str(QUESTION),
            "MISTAKE": str(MISTAKE),
            "SCHEDULE": str(REHEARSAL_SCHEDULE_ACTOR),
        },
        "verifier": {
            "SOURCE": HARNESS_SOURCE_ACTOR,
            "QUESTION": HARNESS_QUESTION_ACTOR,
            "MISTAKE": HARNESS_MISTAKE_ACTOR,
            "SCHEDULE": HARNESS_SCHEDULE_ACTOR,
        },
        "rollback": {"ROLLBACK": str(REHEARSAL_ROLLBACK_ACTOR)},
    }

    assert len(set(authorized.values())) == 5, "approval actors must remain independent"
    rehearsal = fixture_matrix["rehearsal"]
    assert rehearsal["SCHEDULE"] == authorized["SCHEDULE"], (
        f"rehearsal SCHEDULE={rehearsal['SCHEDULE']} "
        f"but authorized={authorized['SCHEDULE']}"
    )
    for fixture_name, actors in fixture_matrix.items():
        assert actors == {role: authorized[role] for role in actors}, (
            f"{fixture_name} approval actor matrix drift: {actors} != {authorized}"
        )


def test_seed_really_creates_and_authorizes_schedule_actor() -> None:
    source = _function_source("lsr03_seed_rehearsal.py", "_seed_source_data")
    assert "INSERT INTO public.users" in source
    assert '(SCHEDULE_ACTOR, "lsr03_schedule")' in source
    assert "INSERT INTO public.legacy_migration_approval_authorizations" in source
    assert '(SCHEDULE_ACTOR, "schedule")' in source


def test_rehearsal_really_approves_schedule_for_active_and_idempotent_paths() -> None:
    source = _function_source("lsr03_rehearsal.py", "main")
    assert source.count("schedule_approved_by=SCHEDULE_ACTOR") == 2
    assert source.count("mapped_next_review_at=MAPPED_NEXT_REVIEW_AT") == 2
    assert "MAPPED_NEXT_REVIEW_AT = datetime(2026, 8, 26, 0, 0, tzinfo=timezone.utc)" in (
        FIXTURE_DIR / "lsr03_rehearsal.py"
    ).read_text()
    assert "if active:" in source
    assert 'mapping_version="v1-active"' in source


def test_verifier_extended_seed_writes_and_reads_schedule_authorization() -> None:
    source = _function_source("lsr03_final_verifier_harness.py", "seed_extended")
    assert "INSERT INTO public.users" in source
    assert "INSERT INTO public.legacy_migration_approval_authorizations" in source
    assert "ON CONFLICT (user_id,approval_kind) DO UPDATE SET enabled=true" in source
    assert '"id": SCHEDULE_ACTOR' in source
    assert "SELECT enabled" in source
    assert "user_id=:id AND approval_kind='schedule' AND enabled" in source
    assert '"schedule_authorized": True' not in source


def test_extended_seed_makes_retained_source_public_but_unmappable() -> None:
    source = _function_source("lsr03_final_verifier_harness.py", "seed_extended")
    assert '"retained": ""' in source
    assert ":question" in source
    assert "metadata" in source
    assert "hidden" in source
    rehearsal = _function_source("lsr03_rehearsal.py", "main")
    assert "retained_public_only" in rehearsal
    assert "target_qkp_ids" in rehearsal
    assert "target_projection_ids" in rehearsal


def test_post_positive_verifier_is_single_json_fail_closed_and_scoped() -> None:
    source = (FIXTURE_DIR / "lsr03_final_verifier_harness.py").read_text()
    assert "async def verify_positive" in source
    verifier = _function_source("lsr03_final_verifier_harness.py", "verify_positive")
    assert "jsonb_build_object" in verifier
    assert "migrated_active" in verifier
    assert "migrated_paused" in verifier
    assert "retained_public_only" in verifier
    assert "v1-chapter-019" in source
    for relation in (
        "public.question_drafts", "public.draft_items", "public.question_sources",
        "public.question_knowledge_points", "public.mistake_drafts", "public.mistakes",
        "public.review_items", "public.review_records", "public.legacy_note_migrations",
    ):
        assert relation in verifier
    assert "_positive_expected_values_sql()" in verifier
    assert "CURRENT_USER" in verifier.upper()
    assert "pass" in verifier
    assert "canonicalize_legacy_note" not in verifier


def test_harness_exposes_post_positive_command() -> None:
    source = (FIXTURE_DIR / "lsr03_final_verifier_harness.py").read_text()
    assert "--verify-positive" in source
    assert "await verify_positive(args.database_url)" in source


def test_harness_pre026_sentinel_commands_are_exact_and_fail_closed() -> None:
    source = (FIXTURE_DIR / "lsr03_final_verifier_harness.py").read_text()
    assert "PRE026_RESTORE_SENTINEL" in source
    assert "--seed-pre026-restore-sentinel" in source
    assert "--verify-pre026-restore-sentinel" in source
    assert "count(*)" in source
    assert "sha256" in source
    seed = _function_source("lsr03_seed_rehearsal.py", "_seed_source_data")
    assert "PRE026_RESTORE_SENTINEL" in seed
    assert "id <> :sentinel" in seed
    assert "LSR03_SEED_TARGET_NOT_EMPTY" in seed


def test_pre026_sentinel_snapshot_casts_all_json_literal_bindings() -> None:
    source = _function_source("lsr03_final_verifier_harness.py", "_pre026_sentinel_snapshot")
    assert "CAST(:id AS uuid)" in source
    assert "CAST(:slug AS text)" in source


def test_pre026_sentinel_hash_formats_naive_utc_timestamps_without_session_timezone() -> None:
    source = _function_source("lsr03_final_verifier_harness.py", "_pre026_sentinel_snapshot")
    assert "to_char(n.created_at,'YYYY-MM-DD\"T\"HH24:MI:SS.US\"Z\"')" in source
    assert "to_char(n.updated_at,'YYYY-MM-DD\"T\"HH24:MI:SS.US\"Z\"')" in source
    assert "n.created_at AT TIME ZONE 'UTC'" not in source
    assert "n.updated_at AT TIME ZONE 'UTC'" not in source


def test_pre026_verifier_checks_namespace_absence_not_a_schema_as_relation() -> None:
    source = _function_source("lsr03_final_verifier_harness.py", "verify_pre026_restore_sentinel")
    assert "pg_namespace" in source or "to_regnamespace" in source
    assert "to_regclass('legacy_migration')" not in source


def test_retained_arrays_are_strictly_null_not_truthiness_checked() -> None:
    source = _function_source("lsr03_rehearsal.py", "main")
    assert "result.target_qkp_ids is not None" in source
    assert "result.target_projection_ids is not None" in source
    assert "or result.target_qkp_ids or result.target_projection_ids" not in source


def test_positive_parity_binds_options_provenance_and_mirror_fields() -> None:
    source = _function_source("lsr03_final_verifier_harness.py", "verify_positive")
    for marker in (
        "q_options", "canonical_payload->'options'", "live_payload->'options'", "source_note_id", "source_revision",
        "source_title", "source_url", "source_hash", "source_revision",
        "q_analysis", "q_explanation", "q_difficulty", "mi_analysis", "mi_difficulty",
        "qs_note::jsonb->>'source_note_id'", "qs_note::jsonb->>'source_revision'",
    ):
        assert marker in source


def test_positive_expected_pairs_are_exactly_four_and_unique() -> None:
    from tests.lsr03_final_verifier_harness import ROLLBACK_BASELINE_SOURCE, POSITIVE_SOURCE_PAIRS

    assert len(POSITIVE_SOURCE_PAIRS) == 4
    assert len({(source, mapping) for source, mapping, _state in POSITIVE_SOURCE_PAIRS}) == 4
    assert all(source != ROLLBACK_BASELINE_SOURCE for source, _mapping, _state in POSITIVE_SOURCE_PAIRS)
    assert {state for _source, _mapping, state in POSITIVE_SOURCE_PAIRS} == {
        "migrated_active", "migrated_paused", "retained_public_only"
    }


def test_positive_expected_state_values_are_typed_as_the_026_enum() -> None:
    source = _function_source("lsr03_final_verifier_harness.py", "_positive_expected_values_sql")
    assert "::public.legacy_note_migration_state" in source
    source = _function_source("lsr03_final_verifier_harness.py", "verify_positive")
    assert "_positive_expected_values_sql()" in source


def test_positive_verifier_exactly_scopes_four_positive_plus_rollback_baseline_pairs() -> None:
    source = (FIXTURE_DIR / "lsr03_final_verifier_harness.py").read_text()
    verifier = _function_source("lsr03_final_verifier_harness.py", "verify_positive")
    assert "allowed_pairs" in verifier
    assert "actual_pairs" in verifier
    assert "allowed_pair_mismatch_count" in verifier
    assert "actual_ledger_row_count" in verifier
    assert "EXCEPT" in verifier
    assert "l.source_note_id IN (SELECT source_note_id FROM expected)" not in verifier
    assert "ROLLBACK_BASELINE_SOURCE" in source
