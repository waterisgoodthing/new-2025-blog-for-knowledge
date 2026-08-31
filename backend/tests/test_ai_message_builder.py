"""Tests for ai_prompt_registry message builders — Batch 10.1 P1-01.

覆盖：
- build_text_messages 正常路径
- build_vision_messages 正常路径
- system_prompt_override 覆盖
- 空 system_prompt raise ValueError（repair_deterministic / prompt_test）
"""

import pytest

from app.services.ai_prompt_registry import (
    build_text_messages,
    build_vision_messages,
    get_prompt_template,
    render_user_content,
)
from app.services.ai_task_types import AiTaskType


class TestBuildTextMessages:
    """build_text_messages 测试。"""

    def test_text_messages_normal_path(self):
        """正常路径：从 registry 获取 system_prompt 构建 messages。"""
        messages = build_text_messages(AiTaskType.CAPTURE_DRAFT, "识别到的题目文字")

        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "识别到的题目文字"
        # system_prompt 来自 registry
        tmpl = get_prompt_template(AiTaskType.CAPTURE_DRAFT)
        assert messages[0]["content"] == tmpl.system_prompt

    def test_text_messages_with_override(self):
        """system_prompt_override 覆盖 registry 的 system_prompt。"""
        messages = build_text_messages(
            AiTaskType.CAPTURE_DRAFT,
            "user content",
            system_prompt_override="custom system prompt",
        )

        assert messages[0]["content"] == "custom system prompt"
        assert messages[1]["content"] == "user content"

    def test_text_messages_empty_system_prompt_raises(self):
        """空 system_prompt 且无 override 时 raise ValueError。"""
        with pytest.raises(ValueError, match="system_prompt is empty"):
            build_text_messages(AiTaskType.REPAIR_DETERMINISTIC, "user content")

    def test_text_messages_prompt_test_empty_system_prompt_raises(self):
        """PROMPT_TEST 的 system_prompt 为空，不传 override 时 raise。"""
        with pytest.raises(ValueError, match="system_prompt is empty"):
            build_text_messages(AiTaskType.PROMPT_TEST, "user content")

    def test_text_messages_empty_system_prompt_with_override_ok(self):
        """空 system_prompt 但有 override 时不报错。"""
        messages = build_text_messages(
            AiTaskType.REPAIR_DETERMINISTIC,
            "user content",
            system_prompt_override="dynamic repair prompt",
        )

        assert messages[0]["content"] == "dynamic repair prompt"


class TestBuildVisionMessages:
    """build_vision_messages 测试。"""

    def test_vision_messages_normal_path(self):
        """正常路径：从 registry 获取 system_prompt 构建 vision messages。"""
        content_parts = [
            {"type": "text", "text": "识别文字"},
            {"type": "image_url", "image_url": {"url": "data:image/png;base64,abc"}},
        ]
        messages = build_vision_messages(AiTaskType.CAPTURE_RECOGNITION, content_parts)

        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == content_parts
        # system_prompt 来自 registry
        tmpl = get_prompt_template(AiTaskType.CAPTURE_RECOGNITION)
        assert messages[0]["content"] == tmpl.system_prompt

    def test_vision_messages_with_override(self):
        """system_prompt_override 覆盖 registry 的 system_prompt。"""
        content_parts = [{"type": "text", "text": "test"}]
        messages = build_vision_messages(
            AiTaskType.CAPTURE_RECOGNITION,
            content_parts,
            system_prompt_override="custom vision system",
        )

        assert messages[0]["content"] == "custom vision system"

    def test_vision_messages_use_registered_vision_prompt_before_text_prompt(self):
        content_parts = [{"type": "text", "text": "question"}]

        messages = build_vision_messages(
            AiTaskType.MISTAKE_QUESTION_DRAFT,
            content_parts,
        )

        template = get_prompt_template(AiTaskType.MISTAKE_QUESTION_DRAFT)
        assert messages[0]["content"] == template.vision_system_prompt
        assert messages[0]["content"] != template.system_prompt

    def test_vision_messages_empty_system_prompt_raises(self):
        """空 system_prompt 且无 override 时 raise ValueError。"""
        content_parts = [{"type": "text", "text": "test"}]
        with pytest.raises(ValueError, match="system_prompt is empty"):
            build_vision_messages(AiTaskType.PROMPT_TEST, content_parts)

    def test_vision_messages_empty_system_prompt_with_override_ok(self):
        """空 system_prompt 但有 override 时不报错。"""
        content_parts = [{"type": "text", "text": "test"}]
        messages = build_vision_messages(
            AiTaskType.REPAIR_DETERMINISTIC,
            content_parts,
            system_prompt_override="dynamic repair prompt",
        )

        assert messages[0]["content"] == "dynamic repair prompt"


class TestRenderUserContent:
    """User-content templates enforce a safe variable contract."""

    def test_renders_declared_variables(self):
        rendered = render_user_content(
            AiTaskType.NETEASE_REASON,
            {"song_info": "Song A"},
        )

        assert "Song A" in rendered
        assert "{song_info}" not in rendered

    @pytest.mark.parametrize(
        ("variables", "expected_name"),
        [
            ({}, "song_info"),
            ({"song_info": "secret-value", "extra": "hidden-value"}, "extra"),
        ],
    )
    def test_rejects_invalid_variable_contract_without_values(
        self,
        variables,
        expected_name,
    ):
        with pytest.raises(ValueError) as error:
            render_user_content(AiTaskType.NETEASE_REASON, variables)

        message = str(error.value)
        assert expected_name in message
        assert "secret-value" not in message
        assert "hidden-value" not in message

    def test_rejects_task_without_user_content_template(self):
        with pytest.raises(ValueError, match="capture_draft"):
            render_user_content(AiTaskType.CAPTURE_DRAFT, {})
