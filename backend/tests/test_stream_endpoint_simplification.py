"""RISK-B11-003 stream endpoint simplification contract tests."""

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import main
from app.routers import ai as ai_router
from app.schemas.ai import AnalyzeRequest, ImageInput, TextAnalyzeRequest
from app.services.ai_gateway import GatewayCallResult
from app.services.ai_task_types import AiTaskType


def _gateway_result() -> GatewayCallResult:
    return GatewayCallResult(
        data={"title": "ok"},
        provider_used="test-provider",
        model="test-model",
        latency_ms=12,
        success=True,
        fallback_used=False,
        attempts=[
            {
                "provider": "test-provider",
                "model": "test-model",
                "success": True,
                "latency_ms": 12,
                "error": "",
            }
        ],
    )


async def _empty_sse_events():
    if False:
        yield ""


class StreamEndpointSimplificationTest(unittest.IsolatedAsyncioTestCase):
    def test_stream_endpoints_are_registered_as_deprecated_compatibility_routes(self):
        stream_routes = {
            route.path: route
            for route in main.app.routes
            if route.path in {"/api/ai/analyze-stream", "/api/ai/analyze-text-stream"}
        }

        self.assertEqual(
            set(stream_routes),
            {"/api/ai/analyze-stream", "/api/ai/analyze-text-stream"},
        )
        for route in stream_routes.values():
            self.assertTrue(route.deprecated, route.path)

    async def test_formal_text_analysis_uses_registered_non_stream_task(self):
        parsed = {"title": "parsed"}

        with (
            patch("app.routers.ai.audit_action", new_callable=AsyncMock),
            patch(
                "app.routers.ai.call_text",
                new_callable=AsyncMock,
                return_value=_gateway_result(),
            ) as call_text,
            patch(
                "app.routers.ai.analyze_and_parse",
                new_callable=AsyncMock,
                return_value=parsed,
            ),
        ):
            result = await ai_router.analyze_text(
                TextAnalyzeRequest(text="题目文本"),
                MagicMock(),
                _admin=object(),
                db=MagicMock(),
                session_token=None,
            )

        self.assertIs(result, parsed)
        call_text.assert_awaited_once()
        self.assertEqual(call_text.await_args.args[0], AiTaskType.ANALYZE_TEXT)

    async def test_formal_image_analysis_uses_registered_non_stream_task(self):
        parsed = {"title": "parsed"}

        with (
            patch("app.routers.ai.audit_action", new_callable=AsyncMock),
            patch(
                "app.routers.ai.call_vision",
                new_callable=AsyncMock,
                return_value=_gateway_result(),
            ) as call_vision,
            patch(
                "app.routers.ai.analyze_and_parse",
                new_callable=AsyncMock,
                return_value=parsed,
            ),
        ):
            result = await ai_router.analyze_mistake(
                AnalyzeRequest(
                    images=[ImageInput(base64="ZmFrZQ==", mime_type="image/png")]
                ),
                MagicMock(),
                _admin=object(),
                db=MagicMock(),
                session_token=None,
            )

        self.assertIs(result, parsed)
        call_vision.assert_awaited_once()
        self.assertEqual(call_vision.await_args.args[0], AiTaskType.ANALYZE_MISTAKE)

    async def test_stream_compatibility_routes_reuse_registered_task_types(self):
        with (
            patch("app.routers.ai.audit_action", new_callable=AsyncMock),
            patch(
                "app.routers.ai.stream_analyze_events",
                return_value=_empty_sse_events(),
            ) as stream_analyze_events,
        ):
            await ai_router.analyze_text_stream(
                TextAnalyzeRequest(text="题目文本"),
                MagicMock(),
                _admin=object(),
                db=MagicMock(),
                session_token=None,
            )
            await ai_router.analyze_mistake_stream(
                AnalyzeRequest(
                    images=[ImageInput(base64="ZmFrZQ==", mime_type="image/png")]
                ),
                MagicMock(),
                _admin=object(),
                db=MagicMock(),
                session_token=None,
            )

        first_call, second_call = stream_analyze_events.call_args_list
        self.assertEqual(first_call.args[2], AiTaskType.ANALYZE_TEXT)
        self.assertEqual(second_call.args[2], AiTaskType.ANALYZE_MISTAKE)
