import unittest
from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock

import main
from fastapi.testclient import TestClient

from app.routers.auth import get_current_admin
from app.schemas.ai_call_log import AiUsageCostStatsItem
from app.services.ai_log_service import query_usage_cost_stats


class AiUsageCostStatsServiceTest(unittest.IsolatedAsyncioTestCase):
    async def test_usage_cost_stats_aggregate_counts_and_mark_unknown_usage(self):
        db = AsyncMock()
        db.execute.return_value = [
            SimpleNamespace(
                day=date(2026, 7, 8),
                task_type="analyze_text",
                provider_used="deepseek",
                model="deepseek-v4-pro",
                call_count=3,
                success_count=2,
                fallback_count=1,
                avg_latency_ms=123.45,
            )
        ]

        items = await query_usage_cost_stats(db)

        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertEqual(item["date"], "2026-07-08")
        self.assertEqual(item["task_type"], "analyze_text")
        self.assertEqual(item["provider"], "deepseek")
        self.assertEqual(item["model"], "deepseek-v4-pro")
        self.assertEqual(item["call_count"], 3)
        self.assertEqual(item["success_count"], 2)
        self.assertEqual(item["failure_count"], 1)
        self.assertEqual(item["fallback_count"], 1)
        self.assertEqual(item["avg_latency_ms"], 123.5)
        self.assertIsNone(item["input_tokens"])
        self.assertIsNone(item["output_tokens"])
        self.assertIsNone(item["estimated_cost"])
        self.assertEqual(item["usage_source"], "unknown")
        self.assertEqual(item["cost_source"], "unknown")


class AiUsageCostStatsContractTest(unittest.TestCase):
    def test_usage_cost_schema_has_unknown_nullable_usage_fields(self):
        fields = set(AiUsageCostStatsItem.model_fields)

        self.assertEqual(
            fields,
            {
                "date",
                "task_type",
                "provider",
                "model",
                "call_count",
                "success_count",
                "failure_count",
                "fallback_count",
                "avg_latency_ms",
                "input_tokens",
                "output_tokens",
                "estimated_cost",
                "currency",
                "usage_source",
                "cost_source",
            },
        )

    def test_usage_cost_route_is_registered_and_admin_only(self):
        route = next(
            route
            for route in main.app.routes
            if route.path == "/api/ai/call-logs/usage-cost"
            and "GET" in getattr(route, "methods", set())
        )

        calls = {dependency.call for dependency in route.dependant.dependencies}
        self.assertIn(get_current_admin, calls)

    def test_anonymous_usage_cost_route_is_rejected(self):
        client = TestClient(main.app)
        response = client.get("/api/ai/call-logs/usage-cost")

        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
