import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock

import main
from fastapi.testclient import TestClient

from app.routers.auth import get_current_admin
from app.schemas.ai_call_log import AiProviderHealthSnapshotItem
from app.services.ai_log_service import query_provider_health_snapshot


class AiProviderHealthSnapshotServiceTest(unittest.IsolatedAsyncioTestCase):
    async def test_health_snapshot_marks_high_failure_provider_degraded(self):
        db = AsyncMock()
        db.execute.return_value = [
            SimpleNamespace(
                provider_used="deepseek",
                model="deepseek-v4-pro",
                call_count=10,
                success_count=6,
                fallback_count=4,
                avg_latency_ms=1500.49,
            )
        ]

        items = await query_provider_health_snapshot(db)

        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertEqual(item["provider"], "deepseek")
        self.assertEqual(item["model"], "deepseek-v4-pro")
        self.assertEqual(item["status"], "degraded")
        self.assertEqual(item["call_count"], 10)
        self.assertEqual(item["success_count"], 6)
        self.assertEqual(item["failure_count"], 4)
        self.assertEqual(item["fallback_count"], 4)
        self.assertEqual(item["failure_rate"], 0.4)
        self.assertEqual(item["fallback_rate"], 0.4)
        self.assertEqual(item["avg_latency_ms"], 1500.5)
        self.assertEqual(item["source"], "ai_call_logs_recent")
        self.assertIn("failure_rate", item["reason"])


class AiProviderHealthSnapshotContractTest(unittest.TestCase):
    def test_health_snapshot_schema_has_safe_observability_fields(self):
        fields = set(AiProviderHealthSnapshotItem.model_fields)

        self.assertEqual(
            fields,
            {
                "provider",
                "model",
                "status",
                "call_count",
                "success_count",
                "failure_count",
                "fallback_count",
                "failure_rate",
                "fallback_rate",
                "avg_latency_ms",
                "source",
                "reason",
            },
        )

    def test_health_snapshot_route_is_registered_and_admin_only(self):
        route = next(
            route
            for route in main.app.routes
            if route.path == "/api/ai/provider-health-snapshot"
            and "GET" in getattr(route, "methods", set())
        )

        calls = {dependency.call for dependency in route.dependant.dependencies}
        self.assertIn(get_current_admin, calls)

    def test_anonymous_health_snapshot_route_is_rejected(self):
        client = TestClient(main.app)
        response = client.get("/api/ai/provider-health-snapshot")

        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
