"""PR-12 static contract tests: migration 032 shape, model, router wiring.

No database is required. Run with:

    cd backend && PYTHONPATH=. .venv/bin/python -m pytest \\
        tests/test_pr12_note_knowledge_points_contract.py -q
"""

from __future__ import annotations

import re
from pathlib import Path

from fastapi.routing import APIRoute

import main
from app.models.note_knowledge_point import NoteKnowledgePoint
from app.models.registry import MODEL_REGISTRY
from app.routers.auth import get_current_admin
from week3_contracts_support import (
    KNOWLEDGE_POINT_ID_TYPE,
    NOTE_ID_TYPE,
    normalize_sql_type_name,
)

MIGRATION_PATH = (
    Path(__file__).parents[1]
    / "alembic"
    / "versions"
    / "032_note_knowledge_points.py"
)

NOTE_KP_PATH = "/api/admin/notes/{note_id}/knowledge-points/{knowledge_point_id}"
KP_NOTES_PATH = "/api/admin/notes/knowledge-points/{knowledge_point_id}/notes"
NOTE_KP_LIST_PATH = "/api/admin/notes/{note_id}/knowledge-points"


def _migration_source() -> str:
    return MIGRATION_PATH.read_text(encoding="utf-8")


def _route(path: str, method: str) -> APIRoute:
    for route in main.app.routes:
        if (
            isinstance(route, APIRoute)
            and route.path == path
            and method in (route.methods or set())
        ):
            return route
    raise AssertionError(f"Missing route: {method} {path}")


# ---------------------------------------------------------------------------
# Migration 032 static shape
# ---------------------------------------------------------------------------


def test_migration_revision_and_down_revision() -> None:
    source = _migration_source()
    assert re.search(r'revision:\s*str\s*=\s*"032"', source)
    assert re.search(r'down_revision:\s*str\s*\|\s*None\s*=\s*"031"', source)


def test_migration_is_net_new_and_does_not_touch_polymorph_table() -> None:
    source = _migration_source()
    bodies = source.split("def upgrade", 1)[1]
    assert "note_knowledge_points" in bodies
    assert "knowledge_point_links" not in bodies
    assert 'drop_table("knowledge_point_links"' not in source


def test_migration_declares_uuid_and_integer_columns() -> None:
    source = _migration_source()
    assert "note_id" in source and "postgresql.UUID" in source
    assert "knowledge_point_id" in source and "sa.Integer()" in source


def test_migration_uses_composite_primary_key_and_cascade_fks() -> None:
    source = _migration_source()
    assert 'sa.PrimaryKeyConstraint("note_id", "knowledge_point_id")' in source
    assert source.count('ondelete="CASCADE"') == 2
    assert '"notes.id"' in source
    assert '"knowledge_points.id"' in source


def test_migration_names_the_kp_lookup_index() -> None:
    source = _migration_source()
    assert "idx_note_knowledge_points_kp" in source
    assert '["knowledge_point_id", "note_id"]' in source


def test_migration_upgrade_and_downgrade_are_symmetric() -> None:
    source = _migration_source()
    assert "create_table" in source
    assert "drop_table" in source
    assert "create_index" in source
    assert "drop_index" in source


# ---------------------------------------------------------------------------
# Model shape vs W3-D04 contract
# ---------------------------------------------------------------------------


def test_model_table_name() -> None:
    assert NoteKnowledgePoint.__tablename__ == "note_knowledge_points"


def test_model_key_types_match_w3_d04() -> None:
    columns = NoteKnowledgePoint.__table__.c
    assert normalize_sql_type_name(columns.note_id.type) == NOTE_ID_TYPE
    assert (
        normalize_sql_type_name(columns.knowledge_point_id.type)
        == KNOWLEDGE_POINT_ID_TYPE
    )


def test_model_composite_primary_key() -> None:
    primary_key = NoteKnowledgePoint.__table__.primary_key
    assert list(primary_key.columns.keys()) == ["note_id", "knowledge_point_id"]


def test_model_foreign_keys_cascade() -> None:
    cascades = {}
    for fk in NoteKnowledgePoint.__table__.foreign_keys:
        cascades[fk.column.table.name] = fk.ondelete
    assert cascades == {"notes": "CASCADE", "knowledge_points": "CASCADE"}


def test_model_has_kp_lookup_index() -> None:
    index_names = {index.name for index in NoteKnowledgePoint.__table__.indexes}
    assert "idx_note_knowledge_points_kp" in index_names


def test_model_does_not_enforce_subject_consistency() -> None:
    assert "subject" not in {column.name for column in NoteKnowledgePoint.__table__.c}


def test_model_is_registered_for_alembic_metadata() -> None:
    assert NoteKnowledgePoint in MODEL_REGISTRY


# ---------------------------------------------------------------------------
# Router wiring: admin-only, explicit user intent
# ---------------------------------------------------------------------------


def _route_dependency_calls(route: APIRoute) -> set[object]:
    return {
        dependency.call
        for dependency in route.dependant.dependencies
        if dependency.call is not None
    }


def test_link_route_is_post_and_admin_only() -> None:
    route = _route(NOTE_KP_PATH, "POST")
    assert get_current_admin in _route_dependency_calls(route)


def test_unlink_route_is_delete_and_admin_only() -> None:
    route = _route(NOTE_KP_PATH, "DELETE")
    assert get_current_admin in _route_dependency_calls(route)


def test_note_to_kp_list_route_is_admin_only() -> None:
    route = _route(NOTE_KP_LIST_PATH, "GET")
    assert get_current_admin in _route_dependency_calls(route)


def test_kp_to_note_list_route_is_admin_only() -> None:
    route = _route(KP_NOTES_PATH, "GET")
    assert get_current_admin in _route_dependency_calls(route)


def test_router_prefix_is_admin_scoped() -> None:
    for path in (NOTE_KP_PATH, NOTE_KP_LIST_PATH, KP_NOTES_PATH):
        assert path.startswith("/api/admin/notes")


def test_pinned_revision_matches_current_head() -> None:
    assert main.EXPECTED_ALEMBIC_REVISION == "034"


def test_uuid_path_parameter_type() -> None:
    schema = main.app.openapi()
    operation = schema["paths"][NOTE_KP_PATH]["post"]
    note_param = next(
        param for param in operation["parameters"] if param["name"] == "note_id"
    )
    assert note_param["schema"]["format"] == "uuid"
