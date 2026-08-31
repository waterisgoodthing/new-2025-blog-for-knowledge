import unittest

import main
from fastapi.testclient import TestClient
from app.routers.auth import get_current_admin


class SearchRouteTest(unittest.TestCase):
    def test_search_is_admin_only_and_versions_backlinks_are_registered(self):
        routes = {(route.path, method) for route in main.app.routes for method in getattr(route, "methods", set())}
        self.assertIn(("/api/admin/search", "POST"), routes)
        self.assertIn(("/api/notes/{slug}/versions", "GET"), routes)
        self.assertIn(("/api/notes/{slug}/backlinks", "GET"), routes)
        self.assertEqual(TestClient(main.app).post("/api/admin/search", json={"query": "x"}).status_code, 401)
        route = next(route for route in main.app.routes if route.path == "/api/admin/search")
        self.assertIn(get_current_admin, {dep.call for dep in route.dependant.dependencies})
