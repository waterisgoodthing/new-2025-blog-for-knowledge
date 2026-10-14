"""Week 3 contract constants and pure helpers (W3-D03/D04/D05/D06/D09).

Pure definitions only: no product code under ``app/``, no DB, no network.
Imported by ``test_week3_contracts.py`` to lock Week 3 contracts before
PR-09 .. PR-11 implement them.

Reference: docs/workflows/personal-learning-system-convergence/week3/README.md
"""

from __future__ import annotations

from typing import Any, Iterable, TypedDict

# ---------------------------------------------------------------------------
# W3-D03 — public Mistake DTO allowlist
# ---------------------------------------------------------------------------

PUBLIC_MISTAKE_DTO_ALLOWLIST: frozenset[str] = frozenset(
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

PUBLIC_MISTAKE_DTO_FORBIDDEN: frozenset[str] = frozenset(
    {
        "my_answer",
        "source_draft_item_id",
        "subject_id",
        "version",
        "review_item_id",
        "status",
        "visibility",
        "question_id",
    }
)

# ---------------------------------------------------------------------------
# W3-D06 — legacy Note(status, hidden) -> canonical Mistake(status, visibility)
# ---------------------------------------------------------------------------

LEGACY_NOTE_STATUS_PUBLISHED = "published"
LEGACY_NOTE_STATUS_UNPUBLISHED = "unpublished"

CANONICAL_MISTAKE_STATUS = "active"
CANONICAL_VISIBILITY_PUBLIC = "public"
CANONICAL_VISIBILITY_PRIVATE = "private"


def map_legacy_note_to_mistake_visibility(status: str, hidden: object) -> tuple[str, str]:
    """Map a legacy Note publication state to canonical (status, visibility).

    W3-D06 matrix:
      published   x hidden falsy (False/0/None) -> ("active", "public")
      published   x hidden truthy (True/1/...)  -> ("active", "private")
      unpublished x hidden falsy                -> ("active", "private")
      unpublished x hidden truthy               -> ("active", "private")

    ``hidden`` is interpreted by truth value (``bool(hidden)``): only a truthy
    ``hidden`` marks the row hidden; ``False``/``0``/``None`` are all visible.
    Canonical ``status`` is the learning lifecycle (active/archived); legacy
    ``status`` is the publication state. The two must not be conflated.
    """
    is_public = status == LEGACY_NOTE_STATUS_PUBLISHED and not bool(hidden)
    visibility = CANONICAL_VISIBILITY_PUBLIC if is_public else CANONICAL_VISIBILITY_PRIVATE
    return (CANONICAL_MISTAKE_STATUS, visibility)


LEGACY_NOTE_VISIBILITY_MATRIX: tuple[tuple[str, bool, str, str], ...] = (
    (LEGACY_NOTE_STATUS_PUBLISHED, False, CANONICAL_MISTAKE_STATUS, CANONICAL_VISIBILITY_PUBLIC),
    (LEGACY_NOTE_STATUS_PUBLISHED, True, CANONICAL_MISTAKE_STATUS, CANONICAL_VISIBILITY_PRIVATE),
    (LEGACY_NOTE_STATUS_UNPUBLISHED, False, CANONICAL_MISTAKE_STATUS, CANONICAL_VISIBILITY_PRIVATE),
    (LEGACY_NOTE_STATUS_UNPUBLISHED, True, CANONICAL_MISTAKE_STATUS, CANONICAL_VISIBILITY_PRIVATE),
)

# ---------------------------------------------------------------------------
# W3-D05 — KP analytics / practice / dashboard response shapes
# ---------------------------------------------------------------------------


class KPAnalyticsItem(TypedDict):
    """One knowledge-point row of the admin KP analytics endpoint (PR-10)."""

    knowledge_point_id: int
    attempt_count: int
    wrong_count: int
    review_count: int
    due_count: int
    accuracy: float
    wrong_rate: float
    lapse_count: int


KP_ANALYTICS_METRIC_FIELDS: frozenset[str] = frozenset(
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

KP_ANALYTICS_SORT_KEY: tuple[str, ...] = (
    "-wrong_rate",
    "-lapse_count",
    "-due_count",
    "knowledge_point_id",
)


def kp_weakness_sort_key(item: KPAnalyticsItem) -> tuple[float, int, int, int]:
    """Weakness ranking key: wrong_rate DESC, lapse_count DESC, due_count DESC, id ASC."""
    return (-item["wrong_rate"], -item["lapse_count"], -item["due_count"], item["knowledge_point_id"])


class PracticeItem(TypedDict):
    """One daily-practice item (PR-13). Never carries answer/explanation data."""

    question_id: str
    knowledge_point_id: int
    selection_reason: str


class PracticeResponse(TypedDict):
    """Daily practice payload: 0..10 items plus honest Empty metadata."""

    items: list[PracticeItem]
    empty_metadata: dict[str, Any]


PRACTICE_REQUIRED_ITEM_FIELDS: frozenset[str] = frozenset(
    {"question_id", "knowledge_point_id", "selection_reason"}
)

PRACTICE_FORBIDDEN_ITEM_FIELDS: frozenset[str] = frozenset(
    {"answer_data", "correct_answer", "analysis", "explanation"}
)

PRACTICE_RESPONSE_FIELDS: frozenset[str] = frozenset({"items", "empty_metadata"})

PRACTICE_EMPTY_METADATA_FIELDS: frozenset[str] = frozenset(
    {
        "reason",
        "raw_candidate_count",
        "recent_attempt_excluded_count",
        "mastered_excluded_count",
        "eligible_candidate_count",
        "target_count",
        "returned_count",
        "window_hours",
    }
)

PRACTICE_ITEMS_MIN = 0
PRACTICE_ITEMS_MAX = 10

DASHBOARD_SUMMARY_DELTA_FIELDS: frozenset[str] = frozenset(
    {
        "review_today_count",
        "practice_today_count",
        "weak_top3",
        "recently_mastered_4",
        "today_first_action",
    }
)


class DashboardWeakTop3Item(TypedDict):
    """One entry of the weak Top-3 (PR-10 ordering authority, PR-11 render)."""

    knowledge_point_id: int
    name: str
    attempt_count: int
    wrong_rate: float
    lapse_count: int
    due_count: int


class DashboardRecentlyMasteredItem(TypedDict):
    """One recently mastered ReviewItem (latest record set new_state=mastered)."""

    review_item_id: str
    mistake_id: str
    question_text: str
    mastered_at: str


class DashboardSectionAction(TypedDict):
    """Per-section action shape (W3R-05), one per review/practice section."""

    section: str
    count: int
    available: bool
    target_route: str
    reason: str


class DashboardSectionActions(TypedDict):
    review: DashboardSectionAction
    practice: DashboardSectionAction


class DashboardTodayFirstAction(TypedDict):
    """Deterministic today-first fallback; never AI-generated (G4)."""

    kind: str
    count: int
    target_route: str | None
    reason: str


DASHBOARD_WEAK_TOP3_ITEM_FIELDS: frozenset[str] = frozenset(
    {"knowledge_point_id", "name", "attempt_count", "wrong_rate", "lapse_count", "due_count"}
)

DASHBOARD_RECENTLY_MASTERED_ITEM_FIELDS: frozenset[str] = frozenset(
    {"review_item_id", "mistake_id", "question_text", "mastered_at"}
)

DASHBOARD_SECTION_ACTION_FIELDS: frozenset[str] = frozenset(
    {"section", "count", "available", "target_route", "reason"}
)

DASHBOARD_SECTION_ACTIONS_FIELDS: frozenset[str] = frozenset({"review", "practice"})

DASHBOARD_TODAY_FIRST_ACTION_FIELDS: frozenset[str] = frozenset(
    {"kind", "count", "target_route", "reason"}
)

DASHBOARD_TODAY_FIRST_ACTION_KINDS: frozenset[str] = frozenset({"review", "practice", "none"})

DASHBOARD_WEAK_TOP_N: int = 3
DASHBOARD_RECENTLY_MASTERED_LIMIT: int = 4


def dashboard_first_action_kind(review_count: int, practice_count: int) -> str:
    """Deterministic fallback priority: due review first, then practice, else none."""
    if review_count > 0:
        return "review"
    if practice_count > 0:
        return "practice"
    return "none"



def compute_attempt_rates(graded_attempts: int, wrong_count: int) -> tuple[float, float]:
    """Return (accuracy, wrong_rate) over graded practice attempts.

    W3-D05 zero-denominator semantics: graded_attempts == 0 yields 0.0 / 0.0,
    never None and never NaN.

    Bounds contract: ``graded_attempts`` must be >= 0 and ``wrong_count`` must
    satisfy ``0 <= wrong_count <= graded_attempts``; violations raise
    ``ValueError`` rather than producing an out-of-range rate.
    """
    if graded_attempts < 0:
        raise ValueError(
            f"graded_attempts must be >= 0, got {graded_attempts!r}"
        )
    if not (0 <= wrong_count <= graded_attempts):
        raise ValueError(
            f"wrong_count must satisfy 0 <= wrong_count <= graded_attempts, "
            f"got wrong_count={wrong_count!r}, graded_attempts={graded_attempts!r}"
        )
    if graded_attempts == 0:
        return 0.0, 0.0
    wrong_rate = wrong_count / graded_attempts
    accuracy = (graded_attempts - wrong_count) / graded_attempts
    return accuracy, wrong_rate


# ---------------------------------------------------------------------------
# W3-D04 — migration 032 key types (note_knowledge_points)
# ---------------------------------------------------------------------------

NOTE_ID_TYPE = "UUID"
KNOWLEDGE_POINT_ID_TYPE = "INTEGER"


def normalize_sql_type_name(sql_type: object) -> str:
    """Normalize a SQLAlchemy type instance to the contract vocabulary."""
    name = type(sql_type).__name__.upper()
    if "UUID" in name:
        return "UUID"
    if name in {"INT", "INTEGER", "SMALLINT", "BIGINT"} or name.endswith("INTEGER"):
        return "INTEGER"
    return name


# ---------------------------------------------------------------------------
# W3-D09 — legacy mistake write-freeze targets (F-1..F-9) and compat reads (K-1..K-12)
# ---------------------------------------------------------------------------

LEGACY_MISTAKE_WRITE_FREEZE_TARGETS: frozenset[str] = frozenset(
    {
        "notes.create_mistake_type",  # F-1
        "notes.update_type_to_mistake",  # F-2
        "notes.promote",  # F-3
        "ui.staged_mistake_form",  # F-4
        "ui.mistake_form",  # F-5
        "ui.write_note_mistake_edit",  # F-6
        "review.sm2_submit",  # F-7
        "notes.field_update_mistake",  # F-8
        "notes.delete_mistake",  # F-9
    }
)

LEGACY_MISTAKE_COMPAT_READS: frozenset[str] = frozenset(
    {
        "k1.notes.list",  # K-1
        "k2.notes.get_by_slug",  # K-2
        "k3.review.queue",  # K-3
        "k4.review.stats",  # K-4
        "k5.review.plan",  # K-5
        "k6.hooks.use_note_index",  # K-6
        "k7.ui.public_mistakes_page",  # K-7
        "k8.ui.note_detail_mistake_render",  # K-8
        "k9.services.knowledge_suggestion_reads",  # K-9
        "k10.search.notes_search",  # K-10
        "k11.ui.list_sidebar_route_metadata",  # K-11
        "k12.tests.compat_baseline",  # K-12
    }
)


def assert_practice_item_keys(keys: Iterable[str]) -> None:
    """Validate a practice item key set: required present, forbidden absent."""
    key_set = frozenset(keys)
    missing = PRACTICE_REQUIRED_ITEM_FIELDS - key_set
    leaked = PRACTICE_FORBIDDEN_ITEM_FIELDS & key_set
    assert not missing, f"practice item missing required fields: {sorted(missing)}"
    assert not leaked, f"practice item leaks forbidden fields: {sorted(leaked)}"
