import unittest

import main
from fastapi.testclient import TestClient
from app.routers.auth import get_current_admin


class MistakeRouteContractTest(unittest.TestCase):
    def test_private_contracts_are_registered_without_public_mistake_api(self):
        contracts = {
            (route.path, method)
            for route in main.app.routes
            for method in getattr(route, "methods", set())
        }

        expected = {
            ("/api/admin/mistake-drafts", "GET"),
            ("/api/admin/mistake-drafts", "POST"),
            ("/api/admin/mistake-drafts/{draft_item_id}", "GET"),
            ("/api/admin/mistake-drafts/{draft_item_id}", "PUT"),
            ("/api/admin/mistake-drafts/{draft_item_id}/reject", "POST"),
            ("/api/admin/mistake-drafts/{draft_item_id}/convert", "POST"),
            ("/api/admin/mistakes", "GET"),
            ("/api/admin/mistakes/{mistake_id}", "GET"),
            ("/api/admin/mistakes/{mistake_id}", "PUT"),
            ("/api/admin/mistakes/{mistake_id}", "DELETE"),
            ("/api/admin/review/items", "GET"),
            ("/api/admin/review/items/{item_id}/records", "GET"),
            ("/api/admin/review/items/{item_id}/submit", "POST"),
        }
        self.assertTrue(expected.issubset(contracts))
        self.assertFalse(
            any(
                path.startswith("/api/mistakes")
                or path.startswith("/api/review/items")
                for path, _method in contracts
            )
        )

    def test_every_new_route_depends_on_admin(self):
        prefixes = (
            "/api/admin/mistake-drafts",
            "/api/admin/mistakes",
            "/api/admin/review/items",
        )
        protected = [
            route
            for route in main.app.routes
            if route.path.startswith(prefixes)
        ]

        self.assertTrue(protected)
        for route in protected:
            calls = {dependency.call for dependency in route.dependant.dependencies}
            self.assertIn(get_current_admin, calls, route.path)

    def test_anonymous_requests_are_rejected(self):
        client = TestClient(main.app)
        for path in (
            "/api/admin/mistake-drafts",
            "/api/admin/mistakes",
            "/api/admin/review/items?due=true",
        ):
            self.assertEqual(client.get(path).status_code, 401, path)
