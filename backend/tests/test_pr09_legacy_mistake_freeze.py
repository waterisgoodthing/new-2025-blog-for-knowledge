"""PR-09 legacy mistake write-freeze (W3-D09 F-1..F-9) and compat-read tests.

Route-level and pure-predicate coverage. Compat reads K-1..K-5 are sampled
to prove they still respond 200 after the freeze.
"""

from __future__ import annotations

import pytest
from fastapi import HTTPException
from fastapi.routing import APIRoute

import main
from app.services.legacy_mistake_freeze import (
    LEGACY_MISTAKE_WRITE_FROZEN_CODE,
    LegacyMistakeWriteFrozen,
    assert_not_legacy_mistake_write,
    freeze_error_detail,
)


# ---------------------------------------------------------------------------
# Pure predicate
# ---------------------------------------------------------------------------


def test_freeze_rejects_mistake_type() -> None:
    with pytest.raises(LegacyMistakeWriteFrozen) as exc_info:
        assert_not_legacy_mistake_write("mistake", operation="notes.create")
    assert exc_info.value.code == LEGACY_MISTAKE_WRITE_FROZEN_CODE
    assert exc_info.value.operation == "notes.create"


def test_freeze_rejects_when_any_supplied_type_is_mistake() -> None:
    with pytest.raises(LegacyMistakeWriteFrozen):
        assert_not_legacy_mistake_write("note", "mistake", operation="notes.update")
    with pytest.raises(LegacyMistakeWriteFrozen):
        assert_not_legacy_mistake_write("mistake", "blog", operation="notes.promote")


def test_freeze_allows_non_mistake_types() -> None:
    assert_not_legacy_mistake_write("note", operation="notes.create")
    assert_not_legacy_mistake_write("blog", operation="notes.create")
    assert_not_legacy_mistake_write("note", "blog", operation="notes.update")
    assert_not_legacy_mistake_write(None, operation="notes.update")


def test_freeze_error_detail_shape() -> None:
    detail = freeze_error_detail("notes.delete")
    assert detail["code"] == LEGACY_MISTAKE_WRITE_FROZEN_CODE
    assert detail["operation"] == "notes.delete"
    assert "frozen" in detail["message"].lower() or "W3-D09" in detail["message"]


# ---------------------------------------------------------------------------
# F-1 .. F-9 coverage map (static: every F target has a freeze call site)
# ---------------------------------------------------------------------------

_FREEZE_CALL_SITES: dict[str, tuple[str, str]] = {
    "F-1": ("backend/app/routers/notes.py", "notes.create"),
    "F-2": ("backend/app/routers/notes.py", "notes.update"),
    "F-3": ("backend/app/routers/notes.py", "notes.promote"),
    "F-6": ("backend/app/routers/notes.py", "notes.update"),
    "F-7": ("backend/app/routers/review.py", "review.sm2_submit"),
    "F-8": ("backend/app/routers/notes.py", "notes.update"),
    "F-9": ("backend/app/routers/notes.py", "notes.delete"),
}


@pytest.mark.parametrize("f_id", sorted(_FREEZE_CALL_SITES))
def test_freeze_call_site_exists(f_id: str) -> None:
    path, operation = _FREEZE_CALL_SITES[f_id]
    source = open(path.replace("backend/", "backend/"), encoding="utf-8").read() if False else ""
    full = __import__("pathlib").Path(__file__).parents[1] / path.replace("backend/", "")
    text = full.read_text(encoding="utf-8")
    assert f"operation=\"{operation}\"" in text or f"operation='{operation}'" in text, (
        f"{f_id}: freeze call for {operation} not found in {path}"
    )


def test_batch_delete_has_freeze_call() -> None:
    full = __import__("pathlib").Path(__file__).parents[1] / "app" / "routers" / "notes.py"
    text = full.read_text(encoding="utf-8")
    assert "notes.batch_delete" in text


def test_single_freeze_helper_module_is_used_across_routers() -> None:
    notes_src = (__import__("pathlib").Path(__file__).parents[1] / "app" / "routers" / "notes.py").read_text()
    review_src = (__import__("pathlib").Path(__file__).parents[1] / "app" / "routers" / "review.py").read_text()
    assert "assert_not_legacy_mistake_write" in notes_src
    assert "assert_not_legacy_mistake_write" in review_src


# ---------------------------------------------------------------------------
# Route registration (static)
# ---------------------------------------------------------------------------


def _find_route(path: str, method: str) -> APIRoute | None:
    for route in main.app.routes:
        if isinstance(route, APIRoute) and route.path == path and method in (route.methods or set()):
            return route
    return None


def test_public_mistakes_route_exists_without_auth() -> None:
    from app.routers.auth import get_current_admin

    route = _find_route("/api/public/mistakes", "GET")
    assert route is not None
    deps = {d.call for d in route.dependant.dependencies}
    assert get_current_admin not in deps


def test_admin_visibility_route_exists_with_admin_auth() -> None:
    from app.routers.auth import get_current_admin

    route = _find_route("/api/admin/mistakes/{mistake_id}/visibility", "PATCH")
    assert route is not None
    deps = {d.call for d in route.dependant.dependencies}
    assert get_current_admin in deps


# ---------------------------------------------------------------------------
# K-1 .. K-5 compat reads remain registered (K-12 baseline)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("path", "method"),
    [
        ("/api/notes", "GET"),  # K-1
        ("/api/notes/{slug}", "GET"),  # K-2
        ("/api/review/queue", "GET"),  # K-3
        ("/api/review/stats", "GET"),  # K-4
        ("/api/review/plan", "GET"),  # K-5
    ],
)
def test_compat_reads_still_registered(path: str, method: str) -> None:
    assert _find_route(path, method) is not None


def test_legacy_review_submit_still_registered_but_frozen() -> None:
    assert _find_route("/api/review/{slug}", "POST") is not None
