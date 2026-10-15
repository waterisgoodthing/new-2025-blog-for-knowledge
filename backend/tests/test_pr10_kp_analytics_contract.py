"""PR-10 KP analytics contract tests: schema, sort key, routing, admin gate."""

from __future__ import annotations

from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

import main
from app.routers.auth import get_current_admin
from app.schemas.kp_analytics import KnowledgePointAnalyticsItem
from app.services import kp_analytics_service
from week3_contracts_support import (
    KP_ANALYTICS_METRIC_FIELDS,
    KP_ANALYTICS_SORT_KEY,
    compute_attempt_rates,
    kp_weakness_sort_key,
)

ANALYTICS_PATH = "/api/admin/knowledge-points/analytics"


def _analytics_route() -> APIRoute:
    route = next(
        (
            route
            for route in main.app.routes
            if isinstance(route, APIRoute)
            and route.path == ANALYTICS_PATH
            and "GET" in route.methods
        ),
        None,
    )
    assert route is not None, f"missing GET {ANALYTICS_PATH}"
    return route


def test_analytics_route_is_registered() -> None:
    _analytics_route()


def test_analytics_route_requires_current_admin() -> None:
    dependency_calls = {dependency.call for dependency in _analytics_route().dependant.dependencies}
    assert get_current_admin in dependency_calls


def test_anonymous_analytics_request_is_rejected() -> None:
    client = TestClient(main.app)
    response = client.get(ANALYTICS_PATH)
    assert response.status_code in (401, 403)


def test_analytics_route_precedes_path_parameter_route() -> None:
    paths = [route.path for route in main.app.routes if isinstance(route, APIRoute)]
    analytics_index = paths.index(ANALYTICS_PATH)
    parametrized_index = paths.index("/api/admin/knowledge-points/{knowledge_point_id}")
    assert analytics_index < parametrized_index


def test_schema_fields_match_w3_d05_metric_set() -> None:
    fields = frozenset(KnowledgePointAnalyticsItem.model_fields.keys())
    assert fields == KP_ANALYTICS_METRIC_FIELDS | {"knowledge_point_id"}


def test_service_sort_key_matches_locked_contract() -> None:
    assert kp_analytics_service.KP_ANALYTICS_SORT_KEY == KP_ANALYTICS_SORT_KEY


def test_service_sort_matches_contract_sort_helper() -> None:
    items = [
        {"knowledge_point_id": 2, "wrong_rate": 0.2, "lapse_count": 0, "due_count": 1},
        {"knowledge_point_id": 1, "wrong_rate": 0.8, "lapse_count": 2, "due_count": 3},
        {"knowledge_point_id": 3, "wrong_rate": 0.8, "lapse_count": 2, "due_count": 3},
        {"knowledge_point_id": 4, "wrong_rate": 0.8, "lapse_count": 5, "due_count": 3},
    ]
    model_items = [
        KnowledgePointAnalyticsItem(
            knowledge_point_id=item["knowledge_point_id"],
            attempt_count=5,
            wrong_count=4,
            review_count=1,
            due_count=item["due_count"],
            accuracy=0.2,
            wrong_rate=item["wrong_rate"],
            lapse_count=item["lapse_count"],
        )
        for item in items
    ]
    service_order = [
        item.knowledge_point_id
        for item in sorted(model_items, key=kp_analytics_service.kp_analytics_sort_key)
    ]
    contract_order = [item["knowledge_point_id"] for item in sorted(items, key=kp_weakness_sort_key)]
    assert service_order == contract_order == [4, 1, 3, 2]


def test_service_rates_match_contract_semantics() -> None:
    for graded, wrong in [(0, 0), (1, 0), (1, 1), (4, 1), (5, 5)]:
        assert kp_analytics_service.compute_attempt_rates(graded, wrong) == compute_attempt_rates(
            graded, wrong
        )


def test_service_rates_return_zero_floats_for_empty_denominator() -> None:
    accuracy, wrong_rate = kp_analytics_service.compute_attempt_rates(0, 0)
    assert accuracy == 0.0 and isinstance(accuracy, float)
    assert wrong_rate == 0.0 and isinstance(wrong_rate, float)
