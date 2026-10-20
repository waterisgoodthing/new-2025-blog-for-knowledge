"""PR-09 permission negative tests and PublicMistakeOut leak checks (G3)."""

from __future__ import annotations

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

import main
from app.routers.auth import get_current_admin
from app.schemas.mistake import PublicMistakeListResponse, PublicMistakeOut

PRIVATE_FIELD_NAMES = frozenset(
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


def _route(path: str, method: str) -> APIRoute:
    for route in main.app.routes:
        if isinstance(route, APIRoute) and route.path == path and method in (route.methods or set()):
            return route
    raise AssertionError(f"Missing route: {method} {path}")


# ---------------------------------------------------------------------------
# Anonymous admin endpoints -> 401/403
# ---------------------------------------------------------------------------


def test_admin_mistakes_list_requires_auth() -> None:
    with TestClient(main.app) as client:
        resp = client.get("/api/admin/mistakes")
    assert resp.status_code in (401, 403)


def test_admin_mistakes_update_requires_auth() -> None:
    import uuid

    with TestClient(main.app) as client:
        resp = client.put(
            f"/api/admin/mistakes/{uuid.uuid4()}",
            json={"version": 1, "visibility": "public"},
        )
    assert resp.status_code in (401, 403)


def test_admin_mistakes_visibility_requires_auth() -> None:
    import uuid

    with TestClient(main.app) as client:
        resp = client.patch(
            f"/api/admin/mistakes/{uuid.uuid4()}/visibility",
            json={"version": 1, "visibility": "public"},
        )
    assert resp.status_code in (401, 403)


def test_public_mistakes_accessible_without_auth() -> None:
    with TestClient(main.app) as client:
        resp = client.get("/api/public/mistakes")
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Public DTO leak checks
# ---------------------------------------------------------------------------


def test_public_mistake_out_serialization_has_no_private_fields() -> None:
    import uuid
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    item = PublicMistakeOut(
        id=uuid.uuid4(),
        title="t",
        question_text="q",
        correct_answer="c",
        analysis="a",
        reason_category="concept",
        mistake_reason="r",
        difficulty="easy",
        knowledge_point_ids=[],
        created_at=now,
        updated_at=now,
    )
    dumped = item.model_dump()
    assert PRIVATE_FIELD_NAMES.isdisjoint(dumped.keys())
    dumped_json = item.model_dump_json()
    for name in PRIVATE_FIELD_NAMES:
        assert f'"{name}"' not in dumped_json


def test_public_list_response_shape() -> None:
    resp = PublicMistakeListResponse(items=[], total=0, page=1, size=20, empty=True, message="No published mistakes yet.")
    data = resp.model_dump()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["empty"] is True
    assert data["message"] is not None
    assert set(data.keys()) == {"items", "total", "page", "size", "empty", "message"}


def test_public_list_empty_flag_when_populated() -> None:
    import uuid
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    item = PublicMistakeOut(
        id=uuid.uuid4(),
        title="t",
        question_text="q",
        correct_answer=None,
        analysis=None,
        reason_category="unknown",
        mistake_reason=None,
        difficulty=None,
        knowledge_point_ids=[1],
        created_at=now,
        updated_at=now,
    )
    resp = PublicMistakeListResponse(items=[item], total=1, page=1, size=20)
    assert resp.empty is False
    assert resp.message is None
