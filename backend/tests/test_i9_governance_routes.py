import unittest
from datetime import datetime

import main
from fastapi.testclient import TestClient
from app.database import async_session
from app.routers.auth import get_current_admin
from app.services.governance_service import get_governance_summary


class GovernanceRouteTest(unittest.TestCase):
    def test_governance_summary_is_admin_only(self):
        route = next(route for route in main.app.routes if route.path == "/api/admin/governance/summary")
        self.assertIn(get_current_admin, {dep.call for dep in route.dependant.dependencies})
        self.assertEqual(TestClient(main.app).get(route.path).status_code, 401)


class GovernanceServiceTest(unittest.IsolatedAsyncioTestCase):
    async def test_summary_exposes_real_sources_and_explicit_unavailable_tasks(self):
        session = async_session()
        try:
            summary = await get_governance_summary(session)
        finally:
            await session.rollback()
            await session.close()
        payload = summary.model_dump(mode="json")
        self.assertTrue(datetime.fromisoformat(payload["generated_at"].replace("Z", "+00:00")))
        self.assertEqual(payload["ai"]["source"], "ai_runs + ai_call_logs")
        self.assertEqual(payload["statistics"]["source"], "questions + mistakes + review_items + attempts")
        self.assertEqual(payload["settings"]["source"], "admin_profiles")
        self.assertEqual(payload["tasks"]["status"], "unavailable")
        self.assertIsNone(payload["tasks"]["count"])
        self.assertEqual(payload["report"]["source"], "audit_logs")
