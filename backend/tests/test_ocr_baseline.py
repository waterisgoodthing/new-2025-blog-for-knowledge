"""OCR baseline harness — deterministic local path (PR-14 / W4-E02).

本基线通过**本地确定性路径**运行 10 个合成样本：fake adapter 成功路径 +
`call_vision` 失败注入（含各类 error code）。它不调用真实 provider，
因此**真实 provider 成功率在本环境为 NOT_VERIFIED**（见 evidence 报告）。

断言：10 个样本全部产生分类结果（failure_category 或成功），其中成功 1 个。
"""

import unittest
from unittest.mock import AsyncMock, patch

from app.services.ai_gateway import GatewayCallResult
from app.services.capture_recognition import recognize_image

MINIMAL_PNG = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00"
    b"\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x00\x03\x00\x01"
    b"\x5c\xcd\xff\x69\x00\x00\x00\x00IEND\xaeB`\x82"
)


def _gateway_success(data: dict) -> GatewayCallResult:
    return GatewayCallResult(
        data=data,
        provider_used="fake",
        model="fake",
        latency_ms=1,
        success=True,
        fallback_used=False,
        attempts=[],
    )


# (case_id, kwargs for recognize_image, patch mode, patch payload, expected)
BASELINE_CASES = [
    (
        "fake_success",
        {"use_fake": True, "fake_text": "示例题干文字"},
        None,
        None,
        (True, None, None),
    ),
    (
        "empty_input",
        {"image_bytes": b""},
        None,
        None,
        (False, "empty_input", "image_fetch"),
    ),
    (
        "no_provider",
        {},
        "side_effect",
        ValueError("No AI provider configured"),
        (False, "no_provider", "provider_auth"),
    ),
    (
        "timeout",
        {},
        "side_effect",
        RuntimeError("provider timeout"),
        (False, "timeout", "provider_timeout"),
    ),
    (
        "auth_401",
        {},
        "side_effect",
        RuntimeError("AI API error (401): invalid api_key sk-test"),
        (False, "provider_auth", "provider_auth"),
    ),
    (
        "invalid_model_404",
        {},
        "side_effect",
        RuntimeError("AI API error (404): model not found"),
        (False, "invalid_model", "invalid_model"),
    ),
    (
        "provider_error_unknown",
        {},
        "side_effect",
        RuntimeError("upstream service blew up"),
        (False, "provider_error", "unknown"),
    ),
    (
        "schema_error",
        {},
        "return_value",
        _gateway_success({"unexpected": "shape"}),
        (False, "schema_error", "schema_validation"),
    ),
    (
        "empty_result",
        {},
        "return_value",
        _gateway_success({"text": "   "}),
        (False, "empty_result", "invalid_response"),
    ),
    (
        "parse_error",
        {},
        "side_effect",
        Exception("boom"),
        (False, "parse_error", "invalid_response"),
    ),
]


class OcrBaselineHarnessTest(unittest.IsolatedAsyncioTestCase):
    async def _run_case(self, case) -> tuple[bool, str | None, str | None]:
        _, kwargs, patch_mode, payload, _ = case
        image_bytes = kwargs.get("image_bytes", MINIMAL_PNG)
        call_kwargs = {
            key: value for key, value in kwargs.items() if key != "image_bytes"
        }

        if patch_mode is None:
            result = await recognize_image(image_bytes, "image/png", **call_kwargs)
        else:
            mock = AsyncMock()
            if patch_mode == "side_effect":
                mock.side_effect = payload
            else:
                mock.return_value = payload
            with patch(
                "app.services.capture_recognition.call_vision",
                new=mock,
            ):
                result = await recognize_image(
                    image_bytes, "image/png", **call_kwargs
                )

        return result.success, result.error_code, result.failure_category

    async def test_ten_samples_are_all_classified(self):
        outcomes = []
        for case in BASELINE_CASES:
            case_id, _, _, _, expected = case
            observed = await self._run_case(case)
            with self.subTest(case=case_id):
                self.assertEqual(observed, expected)
            outcomes.append((case_id, observed))

        self.assertEqual(len(outcomes), 10)
        self.assertTrue(
            all(
                success or (category is not None)
                for _, (success, _, category) in outcomes
            ),
            "every sample must be classified (success or failure_category)",
        )
        success_count = sum(1 for _, (success, _, _) in outcomes if success)
        self.assertEqual(success_count, 1)

    async def test_baseline_has_ten_distinct_case_ids(self):
        case_ids = [case[0] for case in BASELINE_CASES]
        self.assertEqual(len(case_ids), 10)
        self.assertEqual(len(set(case_ids)), 10)


if __name__ == "__main__":
    unittest.main()
