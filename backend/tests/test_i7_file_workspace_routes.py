import unittest

import main
from fastapi.testclient import TestClient
from app.routers.auth import get_current_admin


class FileWorkspaceRouteTest(unittest.TestCase):
    def test_workspace_mutations_are_admin_only(self):
        routes = {
            (route.path, method)
            for route in main.app.routes
            for method in getattr(route, "methods", set())
        }
        expected = {
            ("/api/admin/workspace/files", "GET"),
            ("/api/admin/workspace/files/{attachment_id}/rename", "PATCH"),
            ("/api/admin/workspace/files/{attachment_id}/move", "PATCH"),
            ("/api/admin/workspace/files/{attachment_id}/trash", "POST"),
            ("/api/admin/workspace/files/{attachment_id}/restore", "POST"),
        }
        self.assertTrue(expected.issubset(routes))
        for route in main.app.routes:
            if route.path.startswith("/api/admin/workspace/files"):
                self.assertIn(get_current_admin, {dep.call for dep in route.dependant.dependencies})

    def test_anonymous_workspace_access_is_rejected(self):
        client = TestClient(main.app)
        response = client.get("/api/admin/workspace/files")
        self.assertEqual(response.status_code, 401)
