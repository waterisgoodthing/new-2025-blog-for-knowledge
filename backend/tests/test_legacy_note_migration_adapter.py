import asyncio
import hashlib
import uuid
from datetime import date, datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from app.services.legacy_note_migration_adapter import (
    _as_datetime,
    _assert_runner,
    _validate_schedule,
    build_legacy_migration_idempotency_key,
    build_legacy_migration_notes,
    build_question_source_provenance,
    should_retain_public_only,
    validate_legacy_mapping_payload,
)


def test_canonical_dates_are_normalized_to_utc_datetimes() -> None:
    assert _as_datetime("2026-01-10T09:02:03.123456Z") == datetime(
        2026, 1, 10, 9, 2, 3, 123456, tzinfo=timezone.utc
    )
    with pytest.raises(ValueError, match="DATE_AMBIGUOUS"):
        _as_datetime("2026-02-01")
    with pytest.raises(ValueError, match="DATE_AMBIGUOUS"):
        _as_datetime(date(2026, 2, 1))


def test_schedule_requires_explicit_utc_mapping_and_complete_approval() -> None:
    actor = uuid.UUID("66666666-6666-4666-8666-666666666666")
    approved_at = datetime(2026, 8, 25, 12, 0, tzinfo=timezone.utc)
    mapped_next = datetime(2026, 8, 26, 0, 0, tzinfo=timezone.utc)

    assert _validate_schedule(
        mapped_next_review_at=mapped_next,
        schedule_approved_by=actor,
        schedule_approved_at=approved_at,
        schedule_approval_sequence=1,
    ) == mapped_next

    with pytest.raises(ValueError, match="DATE_AMBIGUOUS"):
        _validate_schedule(
            mapped_next_review_at=None,
            schedule_approved_by=actor,
            schedule_approved_at=approved_at,
            schedule_approval_sequence=1,
        )
    with pytest.raises(ValueError, match="DATE_AMBIGUOUS"):
        _validate_schedule(
            mapped_next_review_at=datetime(2026, 8, 26, 0, 0),
            schedule_approved_by=actor,
            schedule_approved_at=approved_at,
            schedule_approval_sequence=1,
        )
    with pytest.raises(ValueError, match="DATE_AMBIGUOUS"):
        _validate_schedule(
            mapped_next_review_at=datetime(2026, 8, 26, 0, 0, tzinfo=timezone(timedelta(hours=2))),
            schedule_approved_by=actor,
            schedule_approved_at=approved_at,
            schedule_approval_sequence=1,
        )
    with pytest.raises(ValueError, match="APPROVAL_REQUIRED"):
        _validate_schedule(
            mapped_next_review_at=mapped_next,
            schedule_approved_by=None,
            schedule_approved_at=None,
            schedule_approval_sequence=None,
        )
    with pytest.raises(ValueError, match="APPROVAL_REQUIRED"):
        _validate_schedule(
            mapped_next_review_at=mapped_next,
            schedule_approved_by=actor,
            schedule_approved_at=None,
            schedule_approval_sequence=1,
        )


def test_adapter_rejects_non_runner_session() -> None:
    class WrongRoleSession:
        async def execute(self, _statement):
            return SimpleNamespace(one=lambda: SimpleNamespace(current_user="app_role", session_user="app_role"))

    with pytest.raises(PermissionError, match="legacy_note_adapter_runner"):
        asyncio.run(_assert_runner(WrongRoleSession()))


def test_adapter_does_not_guess_an_unmapped_subject() -> None:
    with pytest.raises(ValueError, match="SUBJECT_UNMAPPED"):
        validate_legacy_mapping_payload(
            {
                "question": "What?",
                "question_type": "short_answer",
                "answers": {"correct_answer": "x"},
                "options": [],
            }
        )


def test_adapter_normalizes_legacy_string_options_to_keyed_options() -> None:
    normalized = validate_legacy_mapping_payload({
        "subject_id": 1, "question": "Pick", "question_type": "single_choice",
        "answers": {"correct_answer": "A"}, "options": ["one", "two"],
        "interval": 0, "repetitions": 0, "knowledge_points": ["Algebra"],
    })
    assert normalized["options"] == [{"key": "A", "text": "one"}, {"key": "B", "text": "two"}]


def test_adapter_allows_empty_options_for_short_answer() -> None:
    normalized = validate_legacy_mapping_payload({
        "subject_id": 1, "question": "Explain", "question_type": "short_answer",
        "answers": {"correct_answer": "because"}, "options": [],
        "interval": 0, "repetitions": 0, "knowledge_points": ["Algebra"],
    })
    assert normalized["options"] == []


def test_adapter_allows_empty_options_for_true_false_and_keeps_boolean_answer_data() -> None:
    normalized = validate_legacy_mapping_payload({
        "subject_id": 1, "question": "Is two even?", "question_type": "true_false",
        "answers": {"correct_answer": "True"}, "options": [],
        "interval": 0, "repetitions": 0, "knowledge_points": ["Algebra"],
    })
    assert normalized["options"] == []
    assert normalized["answer_data"] == {"kind": "true_false", "value": True}


def test_adapter_rejects_empty_options_for_choice_types() -> None:
    with pytest.raises(ValueError, match="QUESTION_INVALID"):
        validate_legacy_mapping_payload({
            "subject_id": 1, "question": "Pick", "question_type": "single_choice",
            "answers": {"correct_answer": "A"}, "options": [],
            "interval": 0, "repetitions": 0, "knowledge_points": ["Algebra"],
        })


def test_adapter_enforces_complete_answer_option_invariants() -> None:
    def payload(question_type: str, options: list[dict] | list[str], answer: str) -> dict:
        return {
            "subject_id": 1, "question": "Pick", "question_type": question_type,
            "answers": {"correct_answer": answer}, "options": options,
            "interval": 0, "repetitions": 0, "knowledge_points": ["Algebra"],
        }

    with pytest.raises(ValueError, match="QUESTION_INVALID"):
        validate_legacy_mapping_payload(payload("short_answer", [{"key": "A", "text": "one"}], "one"))
    with pytest.raises(ValueError, match="QUESTION_INVALID"):
        validate_legacy_mapping_payload(payload("single_choice", [{"key": "A", "text": "one"}], "A"))
    with pytest.raises(ValueError, match="QUESTION_INVALID"):
        validate_legacy_mapping_payload(payload("single_choice", [
            {"key": "A", "text": "one"}, {"key": "A", "text": "duplicate"},
        ], "A"))
    with pytest.raises(ValueError, match="ANSWER_INVALID"):
        validate_legacy_mapping_payload(payload("single_choice", [
            {"key": "A", "text": "one"}, {"key": "B", "text": "two"},
        ], "A,B"))
    with pytest.raises(ValueError, match="ANSWER_INVALID"):
        validate_legacy_mapping_payload(payload("multiple_choice", [
            {"key": "A", "text": "one"}, {"key": "B", "text": "two"},
        ], "A,A"))
    with pytest.raises(ValueError, match="ANSWER_INVALID"):
        validate_legacy_mapping_payload(payload("multiple_choice", [
            {"key": "A", "text": "one"}, {"key": "B", "text": "two"},
        ], "C"))


def test_adapter_rejects_option_dict_extra_keys() -> None:
    with pytest.raises(ValueError, match="QUESTION_INVALID"):
        validate_legacy_mapping_payload({
            "subject_id": 1, "question": "Pick", "question_type": "single_choice",
            "answers": {"correct_answer": "A"}, "options": [{"key": "A", "text": "one", "x": 1}],
            "interval": 0, "repetitions": 0, "knowledge_points": ["Algebra"],
        })


def test_idempotency_key_binds_source_revision_and_hash_within_column_limit() -> None:
    source_id = "11111111-1111-4111-8111-111111111111"
    first = build_legacy_migration_idempotency_key(source_id, "v1-paused", 7, "a" * 64)
    assert len(first) <= 128
    expected = "legacy:" + hashlib.sha256(
        f"legacy-note-migration|{source_id}|7|{'a' * 64}|v1-paused".encode()
    ).hexdigest()
    assert first == expected
    assert first == build_legacy_migration_idempotency_key(source_id, "v1-paused", 7, "a" * 64)
    assert first != build_legacy_migration_idempotency_key(source_id, "v1-paused", 8, "a" * 64)
    assert first != build_legacy_migration_idempotency_key(source_id, "v1-paused", 7, "b" * 64)


def test_question_source_provenance_mirrors_canonical_question_contract() -> None:
    source_id = uuid.UUID("11111111-1111-4111-8111-111111111111")
    payload = {
        "id": str(source_id), "slug": "legacy-q", "source_url": "/notes/legacy-q",
        "title": "Legacy question", "content": "context", "question": "Pick one",
        "question_type": "single_choice", "options": ["one", "two"],
        "answers": {"correct_answer": "A"}, "analysis": "because",
        "subject_id": 4, "difficulty": "medium", "revision": 9,
    }
    normalized = validate_legacy_mapping_payload({
        **payload, "interval": 0, "repetitions": 0, "knowledge_points": ["Algebra"],
    })
    provenance = build_question_source_provenance(
        source_note_id=source_id,
        mapping_version="v1-paused",
        source_hash="a" * 64,
        payload=payload,
        normalized=normalized,
    )
    assert provenance["source_note_id"] == str(source_id)
    assert provenance["source_slug"] == "legacy-q"
    assert provenance["source_revision"] == 9
    assert set(provenance["mirror_contract"]) == {
        "subject_id", "title", "question_text", "stem_md", "question_type", "options",
        "difficulty", "correct_answer", "answer_data", "analysis_md", "explanation",
    }
    assert provenance["mirror_contract"]["answer_data"] == {"kind": "single_choice", "value": ["A"]}


def test_migration_notes_keep_explicit_lossiness_from_canonical_payload() -> None:
    notes = build_legacy_migration_notes({
        "content": "context",
        "knowledge_points": ["Algebra"],
        "legacy_review_json": {"ef": 2.5, "interval": 3},
    })
    assert {note["code"] for note in notes} == {
        "CONTENT_PROVENANCE_ONLY",
        "LEGACY_REVIEW_PROVENANCE_ONLY",
        "MISTAKE_PROJECTION_ID_SET_ONLY",
    }


def test_public_retention_requires_a_validated_unmappable_payload() -> None:
    base = {"status": "published", "hidden": False}
    mappable = {
        **base, "subject_id": 1, "question": "Why?", "question_type": "short_answer",
        "answers": {"correct_answer": "because"}, "options": [], "interval": 0,
        "repetitions": 0, "knowledge_points": ["Algebra"],
    }
    unmappable = {**base, **mappable, "question": ""}
    hidden_unmappable = {**unmappable, "hidden": True}
    assert should_retain_public_only(mappable) is False
    assert should_retain_public_only(unmappable) is True
    assert should_retain_public_only(hidden_unmappable) is False
