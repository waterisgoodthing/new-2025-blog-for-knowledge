import unittest

import main
from fastapi.testclient import TestClient

from app.routers.auth import get_current_admin


class AttachmentRouteContractTest(unittest.TestCase):
    def test_private_contracts_are_registered_without_public_attachment_api(self):
        contracts = {
            (route.path, method)
            for route in main.app.routes
            for method in getattr(route, "methods", set())
        }

        expected = {
            ("/api/admin/attachments", "GET"),
            ("/api/admin/attachments", "POST"),
            ("/api/admin/attachments/{attachment_id}", "GET"),
            ("/api/admin/attachments/{attachment_id}", "DELETE"),
            ("/api/admin/attachments/{attachment_id}/content", "GET"),
            ("/api/admin/attachment-links", "GET"),
            ("/api/admin/attachment-links", "POST"),
            ("/api/admin/attachment-links/{link_id}", "DELETE"),
        }

        self.assertTrue(expected.issubset(contracts))
        self.assertFalse(
            any(path.startswith("/api/attachments") for path, _method in contracts)
        )

    def test_every_attachment_route_depends_on_admin(self):
        protected = [
            route
            for route in main.app.routes
            if route.path.startswith("/api/admin/attachments")
            or route.path.startswith("/api/admin/attachment-links")
        ]

        self.assertTrue(protected)
        for route in protected:
            calls = {dependency.call for dependency in route.dependant.dependencies}
            self.assertIn(get_current_admin, calls, route.path)

    def test_anonymous_requests_are_rejected(self):
        client = TestClient(main.app)
        for path in (
            "/api/admin/attachments",
            "/api/admin/attachments/00000000-0000-0000-0000-000000000000",
            "/api/admin/attachments/00000000-0000-0000-0000-000000000000/content",
            "/api/admin/attachment-links",
        ):
            self.assertEqual(client.get(path).status_code, 401, path)
