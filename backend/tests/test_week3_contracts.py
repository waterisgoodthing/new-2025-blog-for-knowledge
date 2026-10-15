"""Week 3 contract lock tests (W3-00, agent W3-00-impl-contracts).

Executable assertions that pin the contracts decided in W3-D03 .. W3-D09 so
PR-09 / PR-10 / PR-11 / PR-12 / PR-13 can implement against a fixed target.

These tests assert contract constants, pure mapping/rate functions and the
*current* canonical model/schema shapes. They do not call any not-yet-existing
endpoint and must pass before those PRs land.

Run:  cd backend && PYTHONPATH=. .venv/bin/python -m pytest tests/test_week3_contracts.py -q
"""

from __future__ import annotations

import math

import pytest

from app.models.note import Note
from app.models.question import QuestionKnowledgePoint
from app.models.taxonomy import KnowledgePoint
from app.schemas.mistake import MistakeOut, PublicMistakeOut
from app.schemas.practice import PracticeEmptyMetadata as PracticeEmptyMetadataModel
from week3_contracts_support import (
    DASHBOARD_RECENTLY_MASTERED_ITEM_FIELDS,
    DASHBOARD_RECENTLY_MASTERED_LIMIT,
    DASHBOARD_SECTION_ACTIONS_FIELDS,
    DASHBOARD_SECTION_ACTION_FIELDS,
    DASHBOARD_SUMMARY_DELTA_FIELDS,
    DASHBOARD_TODAY_FIRST_ACTION_FIELDS,
    DASHBOARD_TODAY_FIRST_ACTION_KINDS,
    DASHBOARD_WEAK_TOP3_ITEM_FIELDS,
    DASHBOARD_WEAK_TOP_N,
    KP_ANALYTICS_METRIC_FIELDS,
    KP_ANALYTICS_SORT_KEY,
    KNOWLEDGE_POINT_ID_TYPE,
    LEGACY_MISTAKE_COMPAT_READS,
    LEGACY_MISTAKE_WRITE_FREEZE_TARGETS,
    LEGACY_NOTE_STATUS_PUBLISHED,
    LEGACY_NOTE_STATUS_UNPUBLISHED,
    LEGACY_NOTE_VISIBILITY_MATRIX,
    NOTE_ID_TYPE,
    PRACTICE_FORBIDDEN_ITEM_FIELDS,
    PRACTICE_ITEMS_MAX,
    PRACTICE_ITEMS_MIN,
    PRACTICE_REQUIRED_ITEM_FIELDS,
    PRACTICE_RESPONSE_FIELDS,
    PRACTICE_EMPTY_METADATA_FIELDS,
    PUBLIC_MISTAKE_DTO_ALLOWLIST,
    PUBLIC_MISTAKE_DTO_FORBIDDEN,
    KPAnalyticsItem,
    PracticeItem,
    PracticeResponse,
    DashboardRecentlyMasteredItem,
    DashboardSectionAction,
    DashboardSectionActions,
    DashboardTodayFirstAction,
    DashboardWeakTop3Item,
    assert_practice_item_keys,
    compute_attempt_rates,
    dashboard_first_action_kind,
    kp_weakness_sort_key,
    map_legacy_note_to_mistake_visibility,
    normalize_sql_type_name,
)
from app.schemas.dashboard import (
    DashboardRecentlyMasteredItem as DashboardRecentlyMasteredModel,
    DashboardSectionAction as DashboardSectionActionModel,
    DashboardSectionActions as DashboardSectionActionsModel,
    DashboardSummary as DashboardSummaryModel,
    DashboardTodayFirstAction as DashboardTodayFirstActionModel,
    DashboardWeakKnowledgePoint as DashboardWeakKnowledgePointModel,
)

# ---------------------------------------------------------------------------
# W3-D03 — public DTO allowlist
# ---------------------------------------------------------------------------

W3_D03_EXPECTED_ALLOWLIST = frozenset(
    {
        "id",
        "title",
        "question_text",
        "correct_answer",
        "analysis",
        "reason_category",
        "mistake_reason",
        "difficulty",
        "knowledge_point_ids",
        "created_at",
        "updated_at",
    }
)

W3_D03_PRIVATE_FIELDS = frozenset(
    {
        "my_answer",
        "source_draft_item_id",
        "subject_id",
        "version",
        "review_item_id",
        "status",
        "visibility",
    }
)


def test_public_dto_allowlist_matches_w3_d03_field_set() -> None:
    assert PUBLIC_MISTAKE_DTO_ALLOWLIST == W3_D03_EXPECTED_ALLOWLIST
    assert len(PUBLIC_MISTAKE_DTO_ALLOWLIST) == 11


def test_public_dto_allowlist_spells_difficulty_not_difficult() -> None:
    assert "difficulty" in PUBLIC_MISTAKE_DTO_ALLOWLIST
    assert "difficult" not in PUBLIC_MISTAKE_DTO_ALLOWLIST


def test_public_dto_allowlist_excludes_private_fields() -> None:
    for field in W3_D03_PRIVATE_FIELDS:
        assert field not in PUBLIC_MISTAKE_DTO_ALLOWLIST, f"{field} must not be public"
    assert W3_D03_PRIVATE_FIELDS == PUBLIC_MISTAKE_DTO_FORBIDDEN - {"question_id"}
    assert W3_D03_PRIVATE_FIELDS.isdisjoint(PUBLIC_MISTAKE_DTO_ALLOWLIST)


def test_public_dto_allowlist_excludes_forbidden_names() -> None:
    for field in (
        "my_answer",
        "source_draft_item_id",
        "subject_id",
        "version",
        "review_item_id",
        "status",
        "visibility",
    ):
        assert field not in PUBLIC_MISTAKE_DTO_ALLOWLIST


def test_mistake_out_is_not_the_public_dto_and_keeps_private_fields() -> None:
    mistake_out_fields = frozenset(MistakeOut.model_fields.keys())
    assert mistake_out_fields != PUBLIC_MISTAKE_DTO_ALLOWLIST
    assert W3_D03_PRIVATE_FIELDS <= mistake_out_fields
    assert "my_answer" in mistake_out_fields
    assert PUBLIC_MISTAKE_DTO_ALLOWLIST <= mistake_out_fields
    assert mistake_out_fields - PUBLIC_MISTAKE_DTO_ALLOWLIST >= {
        "my_answer",
        "source_draft_item_id",
        "subject_id",
        "version",
        "review_item_id",
        "status",
        "visibility",
    }


# ---------------------------------------------------------------------------
# W3-D06 — visibility/status mapping matrix
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "status,hidden,expected_status,expected_visibility",
    LEGACY_NOTE_VISIBILITY_MATRIX,
    ids=[
        "published_visible",
        "published_hidden",
        "unpublished_visible",
        "unpublished_hidden",
    ],
)
def test_legacy_note_to_mistake_visibility_matrix(
    status: str,
    hidden: bool,
    expected_status: str,
    expected_visibility: str,
) -> None:
    assert map_legacy_note_to_mistake_visibility(status, hidden) == (
        expected_status,
        expected_visibility,
    )


def test_visibility_matrix_covers_all_four_cells_exactly() -> None:
    assert len(LEGACY_NOTE_VISIBILITY_MATRIX) == 4
    cells = {(s, h) for s, h, _st, _vis in LEGACY_NOTE_VISIBILITY_MATRIX}
    assert cells == {
        (LEGACY_NOTE_STATUS_PUBLISHED, False),
        (LEGACY_NOTE_STATUS_PUBLISHED, True),
        (LEGACY_NOTE_STATUS_UNPUBLISHED, False),
        (LEGACY_NOTE_STATUS_UNPUBLISHED, True),
    }
    public_cells = [
        (s, h) for s, h, _st, vis in LEGACY_NOTE_VISIBILITY_MATRIX if vis == "public"
    ]
    assert public_cells == [(LEGACY_NOTE_STATUS_PUBLISHED, False)]


def test_canonical_status_is_never_unpublished() -> None:
    for _s, _h, canonical_status, _vis in LEGACY_NOTE_VISIBILITY_MATRIX:
        assert canonical_status == "active"


@pytest.mark.parametrize(
    "hidden",
    [False, 0, None],
    ids=["hidden_false", "hidden_zero", "hidden_none"],
)
def test_hidden_falsy_values_are_visible_when_published(hidden: object) -> None:
    assert map_legacy_note_to_mistake_visibility(
        LEGACY_NOTE_STATUS_PUBLISHED, hidden
    ) == ("active", "public")


@pytest.mark.parametrize(
    "hidden",
    [True, 1],
    ids=["hidden_true", "hidden_one"],
)
def test_hidden_truthy_values_are_hidden_when_published(hidden: object) -> None:
    assert map_legacy_note_to_mistake_visibility(
        LEGACY_NOTE_STATUS_PUBLISHED, hidden
    ) == ("active", "private")


@pytest.mark.parametrize(
    "hidden",
    [False, 0, None, True, 1],
    ids=["false", "zero", "none", "true", "one"],
)
def test_unpublished_is_always_private_regardless_of_hidden(hidden: object) -> None:
    assert map_legacy_note_to_mistake_visibility(
        LEGACY_NOTE_STATUS_UNPUBLISHED, hidden
    ) == ("active", "private")


# ---------------------------------------------------------------------------
# W3-D05 — analytics / practice / dashboard shapes
# ---------------------------------------------------------------------------

W3_D05_METRICS = frozenset(
    {
        "attempt_count",
        "wrong_count",
        "review_count",
        "due_count",
        "accuracy",
        "wrong_rate",
        "lapse_count",
    }
)


def test_kp_analytics_metric_fields_match_w3_d05() -> None:
    assert KP_ANALYTICS_METRIC_FIELDS == W3_D05_METRICS


def test_kp_analytics_item_shape_includes_identity_and_metrics() -> None:
    keys = frozenset(KPAnalyticsItem.__annotations__.keys())
    assert keys == W3_D05_METRICS | {"knowledge_point_id"}


def test_kp_analytics_sort_key_is_stable_and_locked() -> None:
    assert KP_ANALYTICS_SORT_KEY == (
        "-wrong_rate",
        "-lapse_count",
        "-due_count",
        "knowledge_point_id",
    )


def test_kp_weakness_sort_key_orders_by_locked_priority_then_id() -> None:
    items = [
        {
            "knowledge_point_id": 2,
            "attempt_count": 5,
            "wrong_count": 1,
            "review_count": 1,
            "due_count": 1,
            "accuracy": 0.8,
            "wrong_rate": 0.2,
            "lapse_count": 0,
        },
        {
            "knowledge_point_id": 1,
            "attempt_count": 5,
            "wrong_count": 4,
            "review_count": 2,
            "due_count": 3,
            "accuracy": 0.2,
            "wrong_rate": 0.8,
            "lapse_count": 2,
        },
        {
            "knowledge_point_id": 3,
            "attempt_count": 5,
            "wrong_count": 4,
            "review_count": 2,
            "due_count": 3,
            "accuracy": 0.2,
            "wrong_rate": 0.8,
            "lapse_count": 2,
        },
        {
            "knowledge_point_id": 4,
            "attempt_count": 5,
            "wrong_count": 4,
            "review_count": 2,
            "due_count": 3,
            "accuracy": 0.2,
            "wrong_rate": 0.8,
            "lapse_count": 5,
        },
    ]
    ordered = sorted(items, key=kp_weakness_sort_key)
    assert [i["knowledge_point_id"] for i in ordered] == [4, 1, 3, 2]


def test_practice_item_required_fields_locked() -> None:
    assert PRACTICE_REQUIRED_ITEM_FIELDS == frozenset(
        {"question_id", "knowledge_point_id", "selection_reason"}
    )
    keys = frozenset(PracticeItem.__annotations__.keys())
    assert keys == PRACTICE_REQUIRED_ITEM_FIELDS


def test_practice_item_forbids_answer_leak_fields() -> None:
    assert PRACTICE_FORBIDDEN_ITEM_FIELDS == frozenset(
        {"answer_data", "correct_answer", "analysis", "explanation"}
    )
    keys = frozenset(PracticeItem.__annotations__.keys())
    assert PRACTICE_FORBIDDEN_ITEM_FIELDS.isdisjoint(keys)


def test_practice_item_validator_rejects_leaks_and_missing_fields() -> None:
    assert_practice_item_keys({"question_id", "knowledge_point_id", "selection_reason"})
    with pytest.raises(AssertionError):
        assert_practice_item_keys({"question_id", "knowledge_point_id", "selection_reason", "correct_answer"})
    with pytest.raises(AssertionError):
        assert_practice_item_keys({"question_id", "knowledge_point_id"})


def test_practice_response_has_items_and_empty_metadata() -> None:
    keys = frozenset(PracticeResponse.__annotations__.keys())
    assert PRACTICE_RESPONSE_FIELDS <= keys
    assert keys == PRACTICE_RESPONSE_FIELDS


def test_practice_item_count_bounds_are_zero_to_ten() -> None:
    assert PRACTICE_ITEMS_MIN == 0
    assert PRACTICE_ITEMS_MAX == 10


def test_practice_empty_metadata_shape_locked() -> None:
    assert frozenset(PracticeEmptyMetadataModel.model_fields) == PRACTICE_EMPTY_METADATA_FIELDS


def test_dashboard_summary_delta_fields_locked() -> None:
    assert DASHBOARD_SUMMARY_DELTA_FIELDS == frozenset(
        {
            "review_today_count",
            "practice_today_count",
            "weak_top3",
            "recently_mastered_4",
            "today_first_action",
        }
    )


def test_dashboard_summary_model_exposes_delta_and_section_action_fields() -> None:
    keys = frozenset(DashboardSummaryModel.model_fields)
    assert DASHBOARD_SUMMARY_DELTA_FIELDS <= keys
    assert "section_actions" in keys


def test_dashboard_weak_top3_item_shape_locked() -> None:
    assert DASHBOARD_WEAK_TOP3_ITEM_FIELDS == frozenset(DashboardWeakTop3Item.__annotations__)
    assert DASHBOARD_WEAK_TOP_N == 3
    assert frozenset(DashboardWeakKnowledgePointModel.model_fields) == DASHBOARD_WEAK_TOP3_ITEM_FIELDS


def test_dashboard_recently_mastered_item_shape_locked() -> None:
    assert DASHBOARD_RECENTLY_MASTERED_ITEM_FIELDS == frozenset(
        DashboardRecentlyMasteredItem.__annotations__
    )
    assert DASHBOARD_RECENTLY_MASTERED_LIMIT == 4
    assert (
        frozenset(DashboardRecentlyMasteredModel.model_fields)
        == DASHBOARD_RECENTLY_MASTERED_ITEM_FIELDS
    )


def test_dashboard_section_action_shape_locked() -> None:
    assert DASHBOARD_SECTION_ACTION_FIELDS == frozenset(DashboardSectionAction.__annotations__)
    assert DASHBOARD_SECTION_ACTIONS_FIELDS == frozenset(DashboardSectionActions.__annotations__)
    assert frozenset(DashboardSectionActionModel.model_fields) == DASHBOARD_SECTION_ACTION_FIELDS
    assert (
        frozenset(DashboardSectionActionsModel.model_fields)
        == DASHBOARD_SECTION_ACTIONS_FIELDS
    )


def test_dashboard_today_first_action_shape_locked() -> None:
    assert DASHBOARD_TODAY_FIRST_ACTION_FIELDS == frozenset(
        DashboardTodayFirstAction.__annotations__
    )
    assert frozenset(DashboardTodayFirstActionModel.model_fields) == (
        DASHBOARD_TODAY_FIRST_ACTION_FIELDS
    )
    assert frozenset(DashboardTodayFirstActionModel.model_fields["kind"].annotation.__args__) == (
        DASHBOARD_TODAY_FIRST_ACTION_KINDS
    )


def test_dashboard_first_action_priority_is_deterministic() -> None:
    assert dashboard_first_action_kind(2, 3) == "review"
    assert dashboard_first_action_kind(0, 3) == "practice"
    assert dashboard_first_action_kind(0, 0) == "none"


def test_zero_denominator_yields_zero_floats_not_none_or_nan() -> None:
    accuracy, wrong_rate = compute_attempt_rates(0, 0)
    assert accuracy == 0.0
    assert wrong_rate == 0.0
    assert isinstance(accuracy, float) and isinstance(wrong_rate, float)
    assert accuracy is not None and wrong_rate is not None
    assert not math.isnan(accuracy) and not math.isnan(wrong_rate)


def test_nonzero_denominator_rates() -> None:
    accuracy, wrong_rate = compute_attempt_rates(4, 1)
    assert accuracy == 0.75
    assert wrong_rate == 0.25


@pytest.mark.parametrize(
    "graded_attempts,wrong_count",
    [
        (-1, 0),
        (-5, 0),
        (-1, -1),
        (0, 1),
        (0, -1),
        (3, 4),
        (3, -1),
        (1, 2),
    ],
    ids=[
        "negative_graded",
        "negative_graded_large",
        "both_negative",
        "wrong_exceeds_zero_graded",
        "wrong_negative_zero_graded",
        "wrong_exceeds_graded",
        "wrong_negative",
        "wrong_exceeds_graded_small",
    ],
)
def test_attempt_rates_reject_out_of_bounds(
    graded_attempts: int, wrong_count: int
) -> None:
    with pytest.raises(ValueError):
        compute_attempt_rates(graded_attempts, wrong_count)


def test_attempt_rates_accept_boundary_values() -> None:
    assert compute_attempt_rates(0, 0) == (0.0, 0.0)
    assert compute_attempt_rates(1, 0) == (1.0, 0.0)
    assert compute_attempt_rates(1, 1) == (0.0, 1.0)
    assert compute_attempt_rates(5, 5) == (0.0, 1.0)


# ---------------------------------------------------------------------------
# W3-D04 — migration 032 key types
# ---------------------------------------------------------------------------


def test_note_id_contract_constant() -> None:
    assert NOTE_ID_TYPE == "UUID"


def test_knowledge_point_id_contract_constant() -> None:
    assert KNOWLEDGE_POINT_ID_TYPE == "INTEGER"


def test_note_model_id_type_matches_contract() -> None:
    assert normalize_sql_type_name(Note.__table__.c.id.type) == NOTE_ID_TYPE


def test_knowledge_point_model_id_type_matches_contract() -> None:
    assert normalize_sql_type_name(KnowledgePoint.__table__.c.id.type) == KNOWLEDGE_POINT_ID_TYPE


def test_question_knowledge_point_key_types_match_contract() -> None:
    cols = QuestionKnowledgePoint.__table__.c
    assert normalize_sql_type_name(cols.knowledge_point_id.type) == KNOWLEDGE_POINT_ID_TYPE
    assert normalize_sql_type_name(cols.question_id.type) == "UUID"


def test_knowledge_point_id_is_not_uuid_sketch() -> None:
    assert normalize_sql_type_name(KnowledgePoint.__table__.c.id.type) != "UUID"
    assert normalize_sql_type_name(
        QuestionKnowledgePoint.__table__.c.knowledge_point_id.type
    ) != "UUID"


# ---------------------------------------------------------------------------
# W3-D09 — legacy mistake write freeze (F-1..F-9) and compat reads (K-1..K-12)
# ---------------------------------------------------------------------------

W3_D09_FREEZE_TARGETS = frozenset(
    {
        "notes.create_mistake_type",
        "notes.update_type_to_mistake",
        "notes.promote",
        "ui.staged_mistake_form",
        "ui.mistake_form",
        "ui.write_note_mistake_edit",
        "review.sm2_submit",
        "notes.field_update_mistake",
        "notes.delete_mistake",
    }
)

W3_D09_COMPAT_READS = frozenset(
    {
        "k1.notes.list",
        "k2.notes.get_by_slug",
        "k3.review.queue",
        "k4.review.stats",
        "k5.review.plan",
        "k6.hooks.use_note_index",
        "k7.ui.public_mistakes_page",
        "k8.ui.note_detail_mistake_render",
        "k9.services.knowledge_suggestion_reads",
        "k10.search.notes_search",
        "k11.ui.list_sidebar_route_metadata",
        "k12.tests.compat_baseline",
    }
)


def test_legacy_mistake_write_freeze_targets_are_exactly_f1_to_f9() -> None:
    assert LEGACY_MISTAKE_WRITE_FREEZE_TARGETS == W3_D09_FREEZE_TARGETS
    assert len(LEGACY_MISTAKE_WRITE_FREEZE_TARGETS) == 9


def test_legacy_mistake_compat_reads_are_exactly_k1_to_k12() -> None:
    assert LEGACY_MISTAKE_COMPAT_READS == W3_D09_COMPAT_READS
    assert len(LEGACY_MISTAKE_COMPAT_READS) == 12


def test_freeze_targets_and_compat_reads_are_disjoint() -> None:
    assert LEGACY_MISTAKE_WRITE_FREEZE_TARGETS.isdisjoint(LEGACY_MISTAKE_COMPAT_READS)


# ---------------------------------------------------------------------------
# PR-09 — PublicMistakeOut is exactly the W3-D03 allowlist
# ---------------------------------------------------------------------------


def test_public_mistake_out_fields_equal_w3_d03_allowlist() -> None:
    fields = frozenset(PublicMistakeOut.model_fields.keys())
    assert fields == PUBLIC_MISTAKE_DTO_ALLOWLIST == W3_D03_EXPECTED_ALLOWLIST
    assert fields.isdisjoint(W3_D03_PRIVATE_FIELDS | PUBLIC_MISTAKE_DTO_FORBIDDEN)


def test_public_mistake_out_has_no_private_fields() -> None:
    fields = frozenset(PublicMistakeOut.model_fields.keys())
    for forbidden in ("my_answer", "source_draft_item_id", "subject_id", "version", "review_item_id", "status", "visibility", "question_id"):
        assert forbidden not in fields, f"{forbidden} must not appear in PublicMistakeOut"
