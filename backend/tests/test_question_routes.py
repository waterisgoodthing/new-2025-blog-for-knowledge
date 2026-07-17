import unittest

import main
from app.routers.auth import get_current_admin


class QuestionRouteContractTest(unittest.TestCase):
    def test_admin_routes_include_direct_question_crud(self):
        contracts = {
            (route.path, method)
            for route in main.app.routes
            for method in getattr(route, "methods", set())
        }

        self.assertIn(("/api/admin/drafts/questions", "POST"), contracts)
        self.assertIn(("/api/admin/drafts/{draft_item_id}/convert", "POST"), contracts)
        self.assertIn(("/api/admin/questions", "GET"), contracts)
        self.assertIn(("/api/admin/questions", "POST"), contracts)
        self.assertIn(("/api/admin/questions/{question_id}", "PUT"), contracts)
        self.assertIn(("/api/admin/questions/{question_id}", "PATCH"), contracts)
        self.assertIn(("/api/admin/questions/{question_id}", "DELETE"), contracts)

    def test_every_draft_and_question_route_depends_on_admin(self):
        protected = [
            route
            for route in main.app.routes
            if route.path.startswith("/api/admin/drafts")
            or route.path.startswith("/api/admin/questions")
        ]

        self.assertTrue(protected)
        for route in protected:
            calls = {dependency.call for dependency in route.dependant.dependencies}
            self.assertIn(get_current_admin, calls, route.path)
