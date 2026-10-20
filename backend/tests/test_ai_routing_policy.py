import unittest
from dataclasses import fields
from unittest.mock import AsyncMock, patch

from app.services.ai_gateway import call_text
from app.services.ai_routing_policy import (
    ModelPolicy,
    ProviderPolicy,
    RoutingPolicy,
    resolve_routing_policy,
)
from app.services.ai_service import CallResult, ProviderAttempt
from app.services.ai_task_types import AiTaskType


class AiRoutingPolicyTest(unittest.TestCase):
    def test_policy_contracts_do_not_define_secret_fields(self):
        forbidden = {
            "api_key",
            "authorization",
            "cookie",
            "secret",
            "token",
            "storage_key",
        }

        for policy_cls in (ProviderPolicy, ModelPolicy, RoutingPolicy):
            field_names = {field.name.lower() for field in fields(policy_cls)}
            self.assertTrue(field_names.isdisjoint(forbidden), policy_cls.__name__)

    def test_analyze_text_resolves_to_explicit_fallback_chain(self):
        policy = resolve_routing_policy(AiTaskType.ANALYZE_TEXT)

        self.assertEqual(policy.task_type, AiTaskType.ANALYZE_TEXT.value)
        self.assertEqual(policy.primary_provider, "deepseek")
        self.assertEqual(policy.fallback_chain, ("deepseek", "qwen_general"))
        self.assertTrue(policy.require_json)
        self.assertFalse(policy.require_vision)


class GatewayRoutingPolicyTest(unittest.IsolatedAsyncioTestCase):
    async def test_call_text_passes_routing_policy_chain_to_fallback(self):
        mock_result = CallResult(
            data={"title": "ok"},
            attempts=[
                ProviderAttempt(
                    provider="deepseek",
                    model="deepseek-v4-pro",
                    success=True,
                )
            ],
            provider_used="deepseek",
            fallback_used=False,
        )

        with (
            patch(
                "app.services.ai_gateway._call_with_fallback",
                new_callable=AsyncMock,
                return_value=mock_result,
            ) as call_with_fallback,
            patch("app.services.ai_gateway._write_call_log", new_callable=AsyncMock),
            patch("app.services.ai_gateway._start_run_record", new_callable=AsyncMock),
            patch("app.services.ai_gateway._finish_run_record", new_callable=AsyncMock),
        ):
            await call_text(
                AiTaskType.ANALYZE_TEXT,
                [{"role": "user", "content": "题目文本"}],
            )

        self.assertEqual(
            call_with_fallback.await_args.kwargs["fallback_chain"],
            ("deepseek", "qwen_general"),
        )


if __name__ == "__main__":
    unittest.main()
