import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.config import Settings
from app.services import ai_service


def _settings(**overrides):
    values = {
        "AI_API_KEY": "",
        "AI_BASE_URL": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "AI_MODEL": "qwen3.7-plus",
        "DASHSCOPE_API_KEY": "dashscope-key",
        "DASHSCOPE_BASE_URL": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "DASHSCOPE_MODEL": "qwen3.7-plus",
        "DEEPSEEK_API_KEY": "deepseek-key",
        "DEEPSEEK_BASE_URL": "https://api.deepseek.com/v1",
        "DEEPSEEK_MODEL": "deepseek-v4-pro",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


class AiProviderModelTest(unittest.IsolatedAsyncioTestCase):
    async def test_default_settings_use_requested_models(self):
        settings = Settings(_env_file=None)

        self.assertEqual(settings.DEEPSEEK_MODEL, "deepseek-v4-pro")
        self.assertEqual(settings.DASHSCOPE_MODEL, "qwen3.7-plus")

    async def test_provider_status_reports_requested_text_and_vision_models(self):
        with patch.object(ai_service, "get_settings", return_value=_settings()):
            providers = await ai_service.get_provider_status()

        by_name = {provider["name"]: provider for provider in providers}
        self.assertEqual(by_name["Qwen3.7 Plus Vision"]["model"], "qwen3.7-plus")
        self.assertEqual(by_name["DeepSeek"]["model"], "deepseek-v4-pro")

    async def test_ocr_call_prefers_qwen37_plus_for_vision(self):
        captured_models = []

        async def fake_call_provider(provider, messages, max_tokens, response_format=None):
            captured_models.append(provider["model"])
            return {"choices": [{"message": {"content": "{\"ok\": true}"}}]}

        with (
            patch.object(ai_service, "get_settings", return_value=_settings()),
            patch.object(ai_service, "_call_provider", side_effect=fake_call_provider),
        ):
            result = await ai_service.call_ocr_model([{"role": "user", "content": "image"}])

        self.assertEqual(result, {"ok": True})
        self.assertEqual(captured_models, ["qwen3.7-plus"])

    async def test_explicit_fallback_chain_controls_provider_order(self):
        captured_providers = []

        async def fake_call_provider(provider, messages, max_tokens, response_format=None):
            captured_providers.append(provider["name"])
            return {"choices": [{"message": {"content": "{\"ok\": true}"}}]}

        with (
            patch.object(ai_service, "get_settings", return_value=_settings()),
            patch.object(ai_service, "_call_provider", side_effect=fake_call_provider),
        ):
            result = await ai_service._call_with_fallback(
                required_caps={"text"},
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=100,
                response_format={"type": "json_object"},
                preferred="deepseek",
                fallback_chain=("qwen_general", "deepseek"),
                parse_json=True,
            )

        self.assertEqual(result.data, {"ok": True})
        self.assertEqual(result.provider_used, "qwen_general")
        self.assertEqual(captured_providers, ["qwen_general"])


if __name__ == "__main__":
    unittest.main()
