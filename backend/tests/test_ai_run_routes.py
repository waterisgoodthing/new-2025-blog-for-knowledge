import unittest

import main
from fastapi.testclient import TestClient

from app.routers.auth import get_current_admin
from app.schemas.ai_run import AiRunListResponse


class AiRunRouteContractTest(unittest.TestCase):
    def test_admin_run_contracts_are_registered(self):
        contracts = {
            (route.path, method)
            for route in main.app.routes
            for method in getattr(route, "methods", set())
        }
        expected = {
            ("/api/admin/ai/runs", "GET"),
            ("/api/admin/ai/runs/{run_id}", "GET"),
            ("/api/admin/ai/runs/{run_id}/retry", "POST"),
            ("/api/admin/ai/runs/{run_id}/decision", "POST"),
        }
        self.assertTrue(expected.issubset(contracts))

    def test_every_run_route_depends_on_admin(self):
        protected = [
            route
            for route in main.app.routes
            if route.path.startswith("/api/admin/ai/runs")
        ]
        self.assertTrue(protected)
        for route in protected:
            calls = {dependency.call for dependency in route.dependant.dependencies}
            self.assertIn(get_current_admin, calls, route.path)

    def test_anonymous_run_requests_are_rejected(self):
        client = TestClient(main.app)
        response = client.get("/api/admin/ai/runs")
        self.assertEqual(response.status_code, 401)

    def test_run_list_uses_paginated_response_contract(self):
        route = next(
            route
            for route in main.app.routes
            if route.path == "/api/admin/ai/runs"
            and "GET" in getattr(route, "methods", set())
        )
        self.assertIs(route.response_model, AiRunListResponse)
