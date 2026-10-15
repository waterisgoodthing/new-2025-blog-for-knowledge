"""PR-09 freeze, visibility, and public DTO tests (pure + route static)."""

from __future__ import annotations

import uuid

import pytest
from fastapi.routing import APIRoute
from pydantic import ValidationError

import main
from app.routers.auth import get_current_admin
from app.schemas.mistake import (
    MistakeOut,
    MistakeVisibilityUpdate,
    PublicMistakeListResponse,
    PublicMistakeOut,
)
from app.services.legacy_mistake_freeze import (
    LEGACY_MISTAKE_WRITE_FROZEN_CODE,
    LegacyMistakeWriteFrozen,
    assert_not_legacy_mistake_write,
    freeze_error_detail,
)
from week3_contracts_support import (
    PUBLIC_MISTAKE_DTO_ALLOWLIST,
    PUBLIC_MISTAKE_DTO_FORBIDDEN,
)

# ---------------------------------------------------------------------------
# PublicMistakeOut allowlist
# ---------------------------------------------------------------------------


def test_public_mistake_out_exact_allowlist() -> None:
    assert frozenset(PublicMistakeOut.model_fields.keys()) == PUBLIC_MISTAKE_DTO_ALLOWLIST


def test_public_mistake_out_forbids_private_fields() -> None:
    fields = frozenset(PublicMistakeOut.model_fields.keys())
    assert fields.isdisjoint(PUBLIC_MISTAKE_DTO_FORBIDDEN)


def test_mistake_out_still_has_private_fields() -> None:
    fields = frozenset(MistakeOut.model_fields.keys())
    assert "my_answer" in fields
    assert "visibility" in fields
    assert PUBLIC_MISTAKE_DTO_ALLOWLIST <= fields


def test_mistake_visibility_literal_allows_both() -> None:
    out = MistakeOut.model_validate({
        "id": uuid.uuid4(),
        "source_draft_item_id": uuid.uuid4(),
        "question_id": uuid.uuid4(),
        "subject_id": 1,
        "title": "t",
        "question_text": "q",
        "my_answer": "a",
        "correct_answer": "c",
        "analysis": "an",
        "reason_category": "concept",
        "mistake_reason": None,
        "difficulty": "easy",
        "status": "active",
        "visibility": "public",
        "version": 1,
        "knowledge_point_ids": [],
        "review_item_id": uuid.uuid4(),
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
    })
    assert out.visibility == "public"
    out2 = out.model_copy(update={"visibility": "private"})
    assert out2.visibility == "private"


def test_public_list_response_shape() -> None:
    resp = PublicMistakeListResponse(items=[], total=0, page=1, size=20, empty=True, message="empty")
    assert resp.empty is True
    assert resp.items == []


# ---------------------------------------------------------------------------
# MistakeVisibilityUpdate schema
# ---------------------------------------------------------------------------


def test_visibility_update_requires_version_and_visibility() -> None:
    payload = MistakeVisibilityUpdate(version=1, visibility="public")
    assert payload.visibility == "public"
    with pytest.raises(ValidationError):
        MistakeVisibilityUpdate(version=0, visibility="public")
    with pytest.raises(ValidationError):
        MistakeVisibilityUpdate(version=1, visibility="x")


# ---------------------------------------------------------------------------
# Freeze helper unit tests (F-1..F-9 predicate)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "types",
    [
        ("mistake",),
        ("note", "mistake"),
        ("mistake", "note"),
        (None, "mistake"),
    ],
)
def test_freeze_helper_rejects_mistake_type(types: tuple) -> None:
    with pytest.raises(LegacyMistakeWriteFrozen) as exc_info:
        assert_not_legacy_mistake_write(*types, operation="test")
    assert exc_info.value.code == LEGACY_MISTAKE_WRITE_FROZEN_CODE
    detail = freeze_error_detail("test")
    assert detail["code"] == LEGACY_MISTAKE_WRITE_FROZEN_CODE


@pytest.mark.parametrize(
    "types",
    [
        (),
        ("note",),
        ("blog",),
        ("note", "blog"),
        (None,),
        (None, "note"),
    ],
)
def test_freeze_helper_allows_non_mistake(types: tuple) -> None:
    assert_not_legacy_mistake_write(*types, operation="test")


def test_freeze_error_detail_shape() -> None:
    detail = freeze_error_detail("notes.create")
    assert detail["code"] == "legacy_mistake_write_frozen"
    assert detail["operation"] == "notes.create"
    assert "frozen" in detail["message"].lower()


# ---------------------------------------------------------------------------
# Route-level freeze wiring (F-1..F-9) and admin/public boundaries
# ---------------------------------------------------------------------------


def _route(path: str, method: str) -> APIRoute:
    for route in main.app.routes:
        if isinstance(route, APIRoute) and route.path == path and method in route.methods:
            return route
    raise AssertionError(f"Missing route: {method} {path}")


def _dependencies(route: APIRoute) -> set:
    return {dependency.call for dependency in route.dependant.dependencies}


FREEZE_WRITE_ROUTES = [
    ("/api/notes", "POST"),
    ("/api/notes/{slug}", "PUT"),
    ("/api/notes/{slug}", "DELETE"),
    ("/api/notes/batch-delete", "POST"),
    ("/api/notes/{slug}/promote", "POST"),
    ("/api/review/{slug}", "POST"),
]


@pytest.mark.parametrize(("path", "method"), FREEZE_WRITE_ROUTES)
def test_legacy_mistake_write_routes_require_admin(path: str, method: str) -> None:
    assert get_current_admin in _dependencies(_route(path, method)), f"{method} {path}"


COMPAT_READ_ROUTES = [
    ("/api/notes", "GET"),
    ("/api/notes/{slug}", "GET"),
    ("/api/review/queue", "GET"),
    ("/api/review/stats", "GET"),
    ("/api/review/plan", "GET"),
]


@pytest.mark.parametrize(("path", "method"), COMPAT_READ_ROUTES)
def test_compat_reads_still_registered_without_freeze(path: str, method: str) -> None:
    _route(path, method)


def test_public_mistakes_route_exists_without_admin() -> None:
    route = _route("/api/public/mistakes", "GET")
    assert get_current_admin not in _dependencies(route)


def test_admin_visibility_route_exists_with_admin() -> None:
    route = _route("/api/admin/mistakes/{mistake_id}/visibility", "PATCH")
    assert get_current_admin in _dependencies(route)


def test_admin_mistakes_routes_require_admin() -> None:
    for path, method in [
        ("/api/admin/mistakes", "GET"),
        ("/api/admin/mistakes/{mistake_id}", "GET"),
        ("/api/admin/mistakes/{mistake_id}", "PUT"),
        ("/api/admin/mistakes/{mistake_id}", "DELETE"),
    ]:
        assert get_current_admin in _dependencies(_route(path, method)), f"{method} {path}"
