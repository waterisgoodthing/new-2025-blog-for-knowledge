"""F05/F07 cross-layer AI error sanitization tests.

Provider transport is mocked everywhere (no network). The tests prove that the
native lower-layer failures keep their category across every layer and that a
synthetic provider secret never leaks into exception text, warning logs, the
gateway failure result, or the persisted ``ai_call_logs`` / ``ai_runs`` rows.

Covered:
- ``httpx.ReadTimeout``            -> ``provider_timeout`` (not ``unknown``)
- non-JSON 200 body                -> ``invalid_response`` (not ``unknown``)
- 401/404/5xx status classification
- ``_call_with_fallback`` exhaustion preserves the last category and drops the
  raw-response error trail
- OCR ``recognize_image`` surfaces ``provider_timeout`` / ``parse_error``
- synthetic secret marker never appears in logs or persisted error strings
"""

import json
import unittest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
from sqlalchemy import delete, select

from app.database import async_session, engine
from app.models.ai_call_log import AiCallLog
from app.models.ai_run import AiRun
from app.schemas.capture import CaptureDraftInput
from app.services.ai_gateway import (
    _build_failure_result,
    call_vision,
)
from app.services.ai_service import (
    ALLOWED_ERROR_CATEGORIES,
    AIProviderError,
    _call_provider,
    _call_with_fallback,
    _parse_json_response,
)
from app.services.ai_task_types import AiTaskType
from app.services.capture_ai_draft import draft_mistake
from app.services.capture_recognition import recognize_image

MINIMAL_PNG = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00"
    b"\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x00\x03\x00\x01"
    b"\x5c\xcd\xff\x69\x00\x00\x00\x00IEND\xaeB`\x82"
)

SECRET = "sk-live-SECRET-MARKER-4f7a9c"
PROVIDER = {
    "name": "dashscope_vision",
    "key": "test-key",
    "base_url": "https://ai.invalid",
    "model": "qwen-test",
    "capabilities": {"vision", "json"},
}
FALLBACK_PROVIDER = {
    "name": "qwen_general",
    "key": "test-key-2",
    "base_url": "https://ai.invalid",
    "model": "qwen-test-2",
    "capabilities": {"vision", "json"},
}
VISION_CAPS = {"vision", "json"}
JSON_FORMAT = {"type": "json_object"}


def _ok_response(content: str) -> MagicMock:
    response = MagicMock(spec=httpx.Response)
    response.status_code = 200
    response.json.return_value = {"choices": [{"message": {"content": content}}]}
    return response


def _http_response(status_code: int, text: str = "") -> MagicMock:
    response = MagicMock(spec=httpx.Response)
    response.status_code = status_code
    response.text = text
    response.json.side_effect = json.JSONDecodeError("not json", text, 0)
    return response


def _patched_client(post) -> MagicMock:
    client = AsyncMock()
    client.__aenter__.return_value = client
    client.__aexit__.return_value = False
    client.post = post
    return MagicMock(return_value=client)


class ProviderTransportClassificationTest(unittest.IsolatedAsyncioTestCase):
    async def _call(self, post):
        with patch("app.services.ai_service.httpx.AsyncClient", _patched_client(post)):
            return await _call_provider(
                PROVIDER, [{"role": "user", "content": "hi"}], 10
            )

    async def test_read_timeout_maps_to_provider_timeout(self):
        with self.assertRaises(AIProviderError) as ctx:
            await self._call(AsyncMock(side_effect=httpx.ReadTimeout("")))
        self.assertEqual(ctx.exception.category, "provider_timeout")
        self.assertIn(ctx.exception.category, ALLOWED_ERROR_CATEGORIES)
        self.assertEqual(str(ctx.exception), "AI provider timeout")

    async def test_connect_error_maps_to_provider_timeout(self):
        with self.assertRaises(AIProviderError) as ctx:
            await self._call(AsyncMock(side_effect=httpx.ConnectError("boom")))
        self.assertEqual(ctx.exception.category, "provider_timeout")

    async def test_auth_status_maps_to_provider_auth_without_body(self):
        body = json.dumps(
            {
                "error": {
                    "message": f"invalid api_key {SECRET}",
                    "authorization": f"Bearer {SECRET}",
                }
            }
        )
        with self.assertRaises(AIProviderError) as ctx:
            await self._call(AsyncMock(return_value=_http_response(401, body)))
        self.assertEqual(ctx.exception.category, "provider_auth")
        self.assertNotIn(SECRET, str(ctx.exception))
        self.assertNotIn(body, str(ctx.exception))

    async def test_404_maps_to_invalid_model(self):
        with self.assertRaises(AIProviderError) as ctx:
            await self._call(AsyncMock(return_value=_http_response(404)))
        self.assertEqual(ctx.exception.category, "invalid_model")

    async def test_500_maps_to_provider_error(self):
        with self.assertRaises(AIProviderError) as ctx:
            await self._call(AsyncMock(return_value=_http_response(503)))
        self.assertEqual(ctx.exception.category, "provider_error")


class ParseClassificationTest(unittest.IsolatedAsyncioTestCase):
    def test_non_json_content_raises_invalid_response_without_content(self):
        raw_content = f"<html>{SECRET} definitely not json{{{{</html>"
        data = {"choices": [{"message": {"content": raw_content}}]}
        with self.assertRaises(AIProviderError) as ctx:
            _parse_json_response(data)
        self.assertEqual(ctx.exception.category, "invalid_response")
        self.assertEqual(str(ctx.exception), "Failed to parse AI response")
        self.assertNotIn(SECRET, str(ctx.exception))

    def test_missing_choices_raises_invalid_response(self):
        with self.assertRaises(AIProviderError) as ctx:
            _parse_json_response({"unexpected": SECRET})
        self.assertEqual(ctx.exception.category, "invalid_response")
        self.assertNotIn(SECRET, str(ctx.exception))


class FallbackCategoryPreservationTest(unittest.IsolatedAsyncioTestCase):
    async def _exhaust(self, post):
        with (
            patch("app.services.ai_service.httpx.AsyncClient", _patched_client(post)),
            patch(
                "app.services.ai_service._get_providers",
                return_value=[PROVIDER, FALLBACK_PROVIDER],
            ),
        ):
            with self.assertRaises(AIProviderError) as ctx:
                await _call_with_fallback(
                    VISION_CAPS,
                    [{"role": "user", "content": "hi"}],
                    10,
                    response_format=JSON_FORMAT,
                )
        return ctx.exception

    async def test_exhaustion_preserves_timeout_category(self):
        exc = await self._exhaust(AsyncMock(side_effect=httpx.ReadTimeout("")))
        self.assertEqual(exc.category, "provider_timeout")
        self.assertEqual(str(exc), "All AI providers failed")
        self.assertEqual(len(exc.attempts), 2)
        for attempt in exc.attempts:
            self.assertFalse(attempt.success)
            self.assertIn(attempt.error, ALLOWED_ERROR_CATEGORIES)
            self.assertNotIn(SECRET, attempt.error)

    async def test_non_json_body_preserves_invalid_response_category(self):
        exc = await self._exhaust(
            AsyncMock(return_value=_ok_response("not-json{{{"))
        )
        self.assertEqual(exc.category, "invalid_response")
        for attempt in exc.attempts:
            self.assertEqual(attempt.error, "invalid_response")

    async def test_401_body_never_enters_attempts(self):
        body = json.dumps({"error": f"api_key {SECRET}"})
        exc = await self._exhaust(AsyncMock(return_value=_http_response(401, body)))
        self.assertEqual(exc.category, "provider_auth")
        self.assertNotIn(SECRET, json.dumps([a.error for a in exc.attempts]))
        self.assertNotIn(SECRET, str(exc))


class GatewayFailureResultTest(unittest.TestCase):
    def test_failure_result_carries_category(self):
        result = _build_failure_result(
            AIProviderError("provider_timeout", "AI provider timeout"), 5
        )
        self.assertFalse(result.success)
        self.assertEqual(result.failure_category, "provider_timeout")
        self.assertEqual(result.error, "AI provider timeout")

    def test_generic_exception_has_no_category(self):
        result = _build_failure_result(RuntimeError("provider unavailable"), 5)
        self.assertIsNone(result.failure_category)
        self.assertEqual(result.error, "provider unavailable")


class OcrCrossLayerClassificationTest(unittest.IsolatedAsyncioTestCase):
    async def _recognize(self, post):
        with (
            patch("app.services.ai_service.httpx.AsyncClient", _patched_client(post)),
            patch(
                "app.services.ai_service._get_providers",
                return_value=[PROVIDER, FALLBACK_PROVIDER],
            ),
            patch(
                "app.services.ai_gateway._start_run_record",
                new_callable=AsyncMock,
                return_value=None,
            ),
            patch(
                "app.services.ai_gateway._write_call_log",
                new_callable=AsyncMock,
            ) as write_log,
        ):
            result = await recognize_image(
                MINIMAL_PNG, "image/png", capture_id="cap-1"
            )
        return result, write_log

    async def test_native_read_timeout_surfaces_provider_timeout(self):
        result, write_log = await self._recognize(
            AsyncMock(side_effect=httpx.ReadTimeout(""))
        )
        self.assertFalse(result.success)
        self.assertEqual(result.failure_category, "provider_timeout")
        self.assertEqual(result.error_code, "timeout")
        logged = write_log.await_args.args[1]
        self.assertEqual(logged.failure_category, "provider_timeout")

    async def test_non_json_body_surfaces_invalid_response(self):
        result, write_log = await self._recognize(
            AsyncMock(return_value=_ok_response("not-json{{{"))
        )
        self.assertFalse(result.success)
        self.assertEqual(result.failure_category, "invalid_response")
        self.assertEqual(result.error_code, "parse_error")
        logged = write_log.await_args.args[1]
        self.assertEqual(logged.failure_category, "invalid_response")
        self.assertNotIn(SECRET, logged.error or "")


class DraftCrossLayerClassificationTest(unittest.IsolatedAsyncioTestCase):
    """F05 draft path: gateway ``failure_category`` must survive to error_code.

    The provider transport is mocked; the draft adapter calls the real gateway,
    so this proves the structured category is preferred over ``gw.error`` text
    sniffing (which collapses to ``unknown`` once the body/status is stripped).
    """

    async def _draft(self, post):
        with (
            patch("app.services.ai_service.httpx.AsyncClient", _patched_client(post)),
            patch(
                "app.services.ai_service._get_providers",
                return_value=[PROVIDER, FALLBACK_PROVIDER],
            ),
            patch(
                "app.services.ai_gateway._start_run_record",
                new_callable=AsyncMock,
                return_value=None,
            ),
            patch(
                "app.services.ai_gateway._write_call_log",
                new_callable=AsyncMock,
            ),
        ):
            return await draft_mistake(
                CaptureDraftInput(recognized_text="题目文字"),
                capture_id="cap-draft",
            )

    async def test_native_read_timeout_surfaces_provider_timeout(self):
        with self.assertLogs(
            "app.services.capture_ai_draft", level="WARNING"
        ) as captured:
            result = await self._draft(AsyncMock(side_effect=httpx.ReadTimeout("")))
        self.assertFalse(result.success)
        self.assertEqual(result.error_code, "timeout")
        self.assertEqual(result.error_message_safe, "AI draft timed out")
        output = "\n".join(captured.output)
        self.assertIn("category=provider_timeout", output)
        self.assertIn("code=timeout", output)

    async def test_non_json_body_surfaces_invalid_response(self):
        with self.assertLogs(
            "app.services.capture_ai_draft", level="WARNING"
        ) as captured:
            result = await self._draft(
                AsyncMock(return_value=_ok_response("not-json{{{"))
            )
        self.assertFalse(result.success)
        self.assertEqual(result.error_code, "parse_error")
        self.assertEqual(result.error_message_safe, "AI response could not be parsed")
        output = "\n".join(captured.output)
        self.assertIn("category=invalid_response", output)
        self.assertIn("code=parse_error", output)
        self.assertNotIn(SECRET, output)


class SecretSanitizationTest(unittest.IsolatedAsyncioTestCase):
    async def test_secret_never_appears_in_logs_or_gateway_result(self):
        provider_body = (
            '{"error":{"message":"invalid api_key ' + SECRET + '",'
            '"authorization":"Bearer ' + SECRET + '"}}'
        )
        with (
            patch(
                "app.services.ai_service.httpx.AsyncClient",
                _patched_client(AsyncMock(return_value=_http_response(401, provider_body))),
            ),
            patch(
                "app.services.ai_service._get_providers",
                return_value=[PROVIDER, FALLBACK_PROVIDER],
            ),
            patch(
                "app.services.ai_gateway._start_run_record",
                new_callable=AsyncMock,
                return_value=None,
            ),
            patch(
                "app.services.ai_gateway._write_call_log",
                new_callable=AsyncMock,
            ) as write_log,
        ):
            with self.assertLogs(level="WARNING") as captured:
                result = await recognize_image(
                    MINIMAL_PNG, "image/png", capture_id="cap-secret"
                )

        output = "\n".join(captured.output)
        self.assertFalse(result.success)
        self.assertNotIn(SECRET, output)
        self.assertNotIn(provider_body, output)
        self.assertNotIn("api_key", output)
        self.assertNotIn("authorization", output)
        self.assertIn("category=provider_auth", output)

        logged = write_log.await_args.args[1]
        self.assertEqual(logged.failure_category, "provider_auth")
        self.assertNotIn(SECRET, logged.error or "")
        self.assertNotIn(SECRET, json.dumps(logged.attempts))


class PersistedErrorSanitizationTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.addAsyncCleanup(engine.dispose)
        self.marker = f"f07-error-chain-{uuid.uuid4()}"
        self.addAsyncCleanup(self._purge)

    async def _purge(self):
        async with async_session() as session:
            await session.execute(
                delete(AiCallLog).where(AiCallLog.input_summary == self.marker)
            )
            await session.execute(
                delete(AiRun).where(AiRun.input_summary == self.marker)
            )
            await session.commit()

    async def test_provider_body_never_persisted_to_logs_or_runs(self):
        provider_body = (
            '{"error":{"message":"invalid api_key ' + SECRET + '"}}'
        )
        with (
            patch(
                "app.services.ai_service.httpx.AsyncClient",
                _patched_client(AsyncMock(return_value=_http_response(401, provider_body))),
            ),
            patch(
                "app.services.ai_service._get_providers",
                return_value=[PROVIDER],
            ),
        ):
            gw = await call_vision(
                AiTaskType.CAPTURE_RECOGNITION,
                [{"role": "user", "content": "x"}],
                input_summary=self.marker,
            )

        self.assertFalse(gw.success)
        self.assertEqual(gw.failure_category, "provider_auth")
        self.assertNotIn(SECRET, gw.error or "")
        self.assertNotIn(SECRET, json.dumps(gw.attempts))

        async with async_session() as session:
            log = (
                await session.execute(
                    select(AiCallLog).where(AiCallLog.input_summary == self.marker)
                )
            ).scalars().first()
            run = (
                await session.execute(
                    select(AiRun).where(AiRun.input_summary == self.marker)
                )
            ).scalars().first()

        self.assertIsNotNone(log)
        self.assertIsNotNone(run)
        self.assertNotIn(SECRET, log.error or "")
        self.assertNotIn(SECRET, json.dumps(log.attempts or []))
        self.assertNotIn(SECRET, run.error_message_safe or "")
        self.assertEqual(run.error_code, "provider_auth")
        self.assertEqual(run.status, "failed")


if __name__ == "__main__":
    unittest.main()
