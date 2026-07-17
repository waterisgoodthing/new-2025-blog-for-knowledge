from fastapi.routing import APIRoute

import main
from app.routers.auth import get_current_admin


def _dependencies(route: APIRoute):
    return {dependency.call for dependency in route.dependant.dependencies}


def _route(path: str, method: str) -> APIRoute:
    for route in main.app.routes:
        if isinstance(route, APIRoute) and route.path == path and method in route.methods:
            return route
    raise AssertionError(f"Missing route: {method} {path}")


def test_public_note_reads_exist_without_admin_dependency():
    assert get_current_admin not in _dependencies(_route("/api/notes", "GET"))
    assert get_current_admin not in _dependencies(_route("/api/notes/{slug}", "GET"))


def test_private_review_attachment_capture_and_ai_routes_keep_admin_boundary():
    protected_routes = [
        ("/api/review/queue", "GET"),
        ("/api/review/stats", "GET"),
        ("/api/review/plan", "GET"),
        ("/api/review/{slug}", "POST"),
        ("/api/admin/attachments", "GET"),
        ("/api/admin/attachments", "POST"),
        ("/api/admin/captures", "GET"),
        ("/api/admin/captures", "POST"),
        ("/api/ai/analyze", "POST"),
        ("/api/ai/analyze-text", "POST"),
    ]

    for path, method in protected_routes:
        assert get_current_admin in _dependencies(_route(path, method)), f"{method} {path}"


def test_private_note_mutations_keep_admin_boundary():
    for path, method in [
        ("/api/notes", "POST"),
        ("/api/notes/{slug}", "PUT"),
        ("/api/notes/{slug}", "DELETE"),
        ("/api/notes/upload-image", "POST"),
    ]:
        assert get_current_admin in _dependencies(_route(path, method)), f"{method} {path}"
