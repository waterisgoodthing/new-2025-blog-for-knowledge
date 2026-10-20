"""Capture failure taxonomy unit tests (PR-14).

覆盖：
- error_code → CaptureFailureCategory 的完整映射
- provider 错误字符串嗅探
- 分类日志脱敏（API key 绝不出现在日志输出）
- recognition adapter 在失败分支填充 failure_category
"""

import unittest
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

from app.schemas.capture import CaptureOut
from app.services.capture_failure_taxonomy import (
    CaptureFailureCategory,
    categorize_failure,
    categorize_provider_error,
)
from app.services.capture_recognition import recognize_image

MINIMAL_PNG = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00"
    b"\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x00\x03\x00\x01"
    b"\x5c\xcd\xff\x69\x00\x00\x00\x00IEND\xaeB`\x82"
)

LOGGER_NAME = "app.services.capture_recognition"


class TaxonomyMappingTest(unittest.TestCase):
    def test_enum_exposes_exactly_eight_categories(self):
        self.assertEqual(
            {category.value for category in CaptureFailureCategory},
            {
                "provider_auth",
                "provider_timeout",
                "invalid_model",
                "invalid_response",
                "schema_validation",
                "image_fetch",
                "image_format",
                "unknown",
            },
        )

    def test_error_code_is_mapped_to_expected_category(self):
        cases = [
            ("no_provider", CaptureFailureCategory.PROVIDER_AUTH),
            ("provider_auth", CaptureFailureCategory.PROVIDER_AUTH),
            ("invalid_model", CaptureFailureCategory.INVALID_MODEL),
            ("timeout", CaptureFailureCategory.PROVIDER_TIMEOUT),
            ("schema_error", CaptureFailureCategory.SCHEMA_VALIDATION),
            ("parse_error", CaptureFailureCategory.INVALID_RESPONSE),
            ("empty_result", CaptureFailureCategory.INVALID_RESPONSE),
            ("attachment_missing", CaptureFailureCategory.IMAGE_FETCH),
            ("empty_input", CaptureFailureCategory.IMAGE_FETCH),
            ("provider_error", CaptureFailureCategory.UNKNOWN),
            (None, CaptureFailureCategory.UNKNOWN),
            ("some_future_code", CaptureFailureCategory.UNKNOWN),
        ]
        for error_code, expected in cases:
            with self.subTest(error_code=error_code):
                self.assertEqual(categorize_failure(error_code), expected)

    def test_category_is_str_enum(self):
        self.assertEqual(
            CaptureFailureCategory.PROVIDER_AUTH,
            "provider_auth",
        )

    def test_image_format_is_a_declared_but_unmapped_category(self):
        self.assertEqual(
            CaptureFailureCategory.IMAGE_FORMAT.value,
            "image_format",
        )
        self.assertEqual(
            categorize_failure("image_format"),
            CaptureFailureCategory.UNKNOWN,
        )


class ProviderErrorSniffTest(unittest.TestCase):
    def test_provider_error_strings(self):
        cases = [
            ("AI API error (401): unauthorized", CaptureFailureCategory.PROVIDER_AUTH),
            ("HTTP 403 Forbidden", CaptureFailureCategory.PROVIDER_AUTH),
            ("HTTP 429 too many requests", CaptureFailureCategory.PROVIDER_AUTH),
            ("quota exceeded", CaptureFailureCategory.PROVIDER_AUTH),
            ("invalid api_key provided", CaptureFailureCategory.PROVIDER_AUTH),
            ("apikey missing", CaptureFailureCategory.PROVIDER_AUTH),
            ("invalid key", CaptureFailureCategory.PROVIDER_AUTH),
            ("HTTP 404 model not found", CaptureFailureCategory.INVALID_MODEL),
            ("model not found", CaptureFailureCategory.INVALID_MODEL),
            ("request timeout", CaptureFailureCategory.PROVIDER_TIMEOUT),
            ("connection timed out", CaptureFailureCategory.PROVIDER_TIMEOUT),
            ("ConnectError: connection refused", CaptureFailureCategory.PROVIDER_TIMEOUT),
            ("totally unrecognized failure", CaptureFailureCategory.UNKNOWN),
            ("", CaptureFailureCategory.UNKNOWN),
        ]
        for message, expected in cases:
            with self.subTest(message=message):
                self.assertEqual(categorize_provider_error(message), expected)


class RecognitionCategoryPopulationTest(unittest.IsolatedAsyncioTestCase):
    async def test_empty_input_is_image_fetch(self):
        result = await recognize_image(b"", "image/png")
        self.assertFalse(result.success)
        self.assertEqual(result.error_code, "empty_input")
        self.assertEqual(result.failure_category, "image_fetch")

    async def test_no_provider_is_provider_auth(self):
        with patch(
            "app.services.capture_recognition.call_vision",
            new=AsyncMock(side_effect=ValueError("No AI provider configured")),
        ):
            result = await recognize_image(MINIMAL_PNG, "image/png")

        self.assertFalse(result.success)
        self.assertEqual(result.error_code, "no_provider")
        self.assertEqual(result.failure_category, "provider_auth")

    async def test_timeout_is_provider_timeout(self):
        with patch(
            "app.services.capture_recognition.call_vision",
            new=AsyncMock(side_effect=RuntimeError("provider timeout")),
        ):
            result = await recognize_image(MINIMAL_PNG, "image/png")

        self.assertEqual(result.error_code, "timeout")
        self.assertEqual(result.failure_category, "provider_timeout")

    async def test_auth_provider_error_maps_to_provider_auth_code(self):
        with patch(
            "app.services.capture_recognition.call_vision",
            new=AsyncMock(side_effect=RuntimeError("AI API error (401): bad key")),
        ):
            result = await recognize_image(MINIMAL_PNG, "image/png")

        self.assertEqual(result.error_code, "provider_auth")
        self.assertEqual(result.failure_category, "provider_auth")
        self.assertEqual(
            result.error_message_safe, "AI provider authentication failed"
        )

    async def test_invalid_model_provider_error_maps_to_invalid_model_code(self):
        with patch(
            "app.services.capture_recognition.call_vision",
            new=AsyncMock(side_effect=RuntimeError("HTTP 404 model not found")),
        ):
            result = await recognize_image(MINIMAL_PNG, "image/png")

        self.assertEqual(result.error_code, "invalid_model")
        self.assertEqual(result.failure_category, "invalid_model")
        self.assertEqual(result.error_message_safe, "AI model unavailable")

    async def test_generic_provider_error_keeps_provider_error_code(self):
        with patch(
            "app.services.capture_recognition.call_vision",
            new=AsyncMock(side_effect=RuntimeError("upstream service blew up")),
        ):
            result = await recognize_image(MINIMAL_PNG, "image/png")

        self.assertEqual(result.error_code, "provider_error")
        self.assertEqual(result.failure_category, "unknown")
        self.assertEqual(result.error_message_safe, "AI provider error")

    async def test_parse_error_is_invalid_response(self):
        with patch(
            "app.services.capture_recognition.call_vision",
            new=AsyncMock(side_effect=Exception("boom")),
        ):
            result = await recognize_image(MINIMAL_PNG, "image/png")

        self.assertEqual(result.error_code, "parse_error")
        self.assertEqual(result.failure_category, "invalid_response")


class LogSanitizationTest(unittest.IsolatedAsyncioTestCase):
    async def test_provider_body_secret_never_appears_in_log_output(self):
        secret = "sk-live-ABC123SECRETKEY"
        provider_body = (
            '{"error":{"message":"invalid api_key ' + secret + '",'
            '"authorization":"Bearer ' + secret + '"}}'
        )
        with patch(
            "app.services.capture_recognition.call_vision",
            new=AsyncMock(
                side_effect=RuntimeError(
                    f"AI API error (401): {provider_body}"
                )
            ),
        ):
            with self.assertLogs(LOGGER_NAME, level="WARNING") as captured:
                result = await recognize_image(
                    MINIMAL_PNG,
                    "image/png",
                    capture_id="capture-abc",
                )

        output = "\n".join(captured.output)
        self.assertFalse(result.success)
        self.assertNotIn(secret, output)
        self.assertNotIn(provider_body, output)
        self.assertNotIn("api_key", output)
        self.assertNotIn("authorization", output)
        self.assertIn("category=provider_auth", output)
        self.assertIn("code=provider_auth", output)
        self.assertIn("capture_id=capture-abc", output)

    async def test_log_line_contains_only_category_code_and_capture_id(self):
        with patch(
            "app.services.capture_recognition.call_vision",
            new=AsyncMock(side_effect=ValueError("No AI provider configured")),
        ):
            with self.assertLogs(LOGGER_NAME, level="WARNING") as captured:
                await recognize_image(
                    MINIMAL_PNG,
                    "image/png",
                    capture_id="capture-xyz",
                )

        output = "\n".join(captured.output)
        self.assertIn("category=provider_auth", output)
        self.assertIn("code=no_provider", output)
        self.assertIn("capture_id=capture-xyz", output)
        self.assertNotIn("No AI provider configured", output)


def _failed_capture(**overrides) -> CaptureOut:
    now = datetime.now(timezone.utc)
    payload = {
        "id": uuid.uuid4(),
        "source_attachment_id": uuid.uuid4(),
        "status": "failed",
        "recognized_text": None,
        "user_error_context": None,
        "question_draft_text": None,
        "analysis_draft_text": None,
        "error_summary_draft": None,
        "subject_id": None,
        "knowledge_point_suggestions": [],
        "model_output_version": "v1",
        "attempt_count": 1,
        "last_stage": "recognize",
        "error_code": None,
        "error_message_safe": None,
        "started_at": now,
        "finished_at": now,
        "mistake_draft_item_id": None,
        "created_by": None,
        "created_at": now,
        "updated_at": now,
    }
    payload.update(overrides)
    return CaptureOut(**payload)


class DtoFailureCategorySerializationTest(unittest.TestCase):
    """F1/F5: DTO 序列化的 failure_category 必须反映 error_code，而非恒为 unknown。"""

    def test_specific_error_codes_surface_specific_categories(self):
        cases = [
            ("provider_auth", "provider_auth"),
            ("invalid_model", "invalid_model"),
            ("timeout", "provider_timeout"),
            ("no_provider", "provider_auth"),
            ("provider_error", "unknown"),
        ]
        for error_code, expected in cases:
            with self.subTest(error_code=error_code):
                capture = _failed_capture(error_code=error_code)
                self.assertEqual(
                    capture.model_dump()["failure_category"], expected
                )
                self.assertEqual(capture.failure_category, expected)

    def test_non_failed_status_has_no_category(self):
        capture = _failed_capture(status="recognized", error_code="provider_auth")
        self.assertIsNone(capture.model_dump()["failure_category"])


if __name__ == "__main__":
    unittest.main()
