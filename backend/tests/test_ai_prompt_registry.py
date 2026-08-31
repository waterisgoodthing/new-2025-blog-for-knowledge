"""Tests for ai_prompt_registry — Batch 10 P0-04."""

import importlib
import sys

from app.services.ai_prompt_registry import PROMPT_REGISTRY, get_prompt_template
from app.services.ai_task_types import AiTaskType


def test_registry_covers_all_task_types():
    """注册表覆盖全部 16 个 AiTaskType。"""
    for task_type in AiTaskType:
        assert task_type in PROMPT_REGISTRY, f"Missing {task_type} in PROMPT_REGISTRY"


def test_registry_count():
    """注册表数量等于 AiTaskType 数量。"""
    assert len(PROMPT_REGISTRY) == len(list(AiTaskType))


def test_versions_follow_static_and_dynamic_policy():
    """Batch 10.2 static prompts are v2; caller-supplied dynamic prompts remain v1."""
    for template in PROMPT_REGISTRY.values():
        assert template.version == ("v1" if template.dynamic_prompt else "v2")


def test_system_prompt_non_empty():
    """每个 PromptTemplate 的 system_prompt 非空（除 PROMPT_TEST 和 REPAIR_DETERMINISTIC）。"""
    skip = {AiTaskType.PROMPT_TEST, AiTaskType.REPAIR_DETERMINISTIC}
    for task_type, template in PROMPT_REGISTRY.items():
        if task_type in skip:
            continue
        assert template.system_prompt, f"Empty system_prompt for {task_type}"


def test_get_prompt_template():
    """get_prompt_template 返回正确模板。"""
    tmpl = get_prompt_template(AiTaskType.CAPTURE_DRAFT)
    assert tmpl.task_type == AiTaskType.CAPTURE_DRAFT
    assert tmpl.version == "v2"
    assert "错题分析助手" in tmpl.system_prompt


def test_get_prompt_template_raises_for_unknown():
    """未知 task_type 抛出 KeyError。"""
    import pytest
    with pytest.raises(KeyError):
        get_prompt_template("nonexistent")


def test_capture_recognition_has_user_content_template():
    """capture_recognition 有 user_content_template。"""
    tmpl = get_prompt_template(AiTaskType.CAPTURE_RECOGNITION)
    assert tmpl.user_content_template is not None
    assert "图片文字识别助手" in tmpl.user_content_template


def test_netease_reason_has_user_content_template():
    """netease_reason 有 user_content_template。"""
    tmpl = get_prompt_template(AiTaskType.NETEASE_REASON)
    assert tmpl.user_content_template is not None
    assert "{song_info}" in tmpl.user_content_template


def test_json_mode_flags():
    """json_mode 标记正确。"""
    assert PROMPT_REGISTRY[AiTaskType.CAPTURE_DRAFT].json_mode is True
    assert PROMPT_REGISTRY[AiTaskType.DIAGRAM_FALLBACK].json_mode is False
    assert PROMPT_REGISTRY[AiTaskType.NETEASE_REASON].json_mode is False


def test_preferred_providers():
    """preferred_provider 设置正确。"""
    assert PROMPT_REGISTRY[AiTaskType.CAPTURE_DRAFT].preferred_provider == "deepseek"
    assert PROMPT_REGISTRY[AiTaskType.CAPTURE_RECOGNITION].preferred_provider == "dashscope_vision"
    assert PROMPT_REGISTRY[AiTaskType.RECOMMENDATION].preferred_provider == "qwen_general"


def test_output_schema_names():
    """output_schema_name 设置正确。"""
    assert PROMPT_REGISTRY[AiTaskType.CAPTURE_DRAFT].output_schema_name == "MistakeDraftSuggestionV1"
    assert PROMPT_REGISTRY[AiTaskType.CAPTURE_RECOGNITION].output_schema_name == "RecognitionOutput"
    assert PROMPT_REGISTRY[AiTaskType.ANALYZE_MISTAKE].output_schema_name is None
    assert PROMPT_REGISTRY[AiTaskType.DIAGRAM_FALLBACK].output_schema_name is None


def test_analyze_mistake_uses_vision_system_message():
    """ANALYZE_MISTAKE 的 system_prompt 为 ANALYZE_VISION_SYSTEM_MESSAGE，user_content_template 为 OCR_SYSTEM_PROMPT。"""
    from app.services.ai_prompts import (
        ANALYZE_VISION_SYSTEM_MESSAGE,
        OCR_SYSTEM_PROMPT,
        standardize_prompt,
    )

    tmpl = get_prompt_template(AiTaskType.ANALYZE_MISTAKE)
    assert tmpl.system_prompt == standardize_prompt(ANALYZE_VISION_SYSTEM_MESSAGE)
    assert tmpl.user_content_template == OCR_SYSTEM_PROMPT


def test_prompt_template_metadata_contracts():
    """Batch 10.2 metadata explicitly describes variables, vision, and dynamic prompts."""
    netease = get_prompt_template(AiTaskType.NETEASE_REASON)
    question_draft = get_prompt_template(AiTaskType.MISTAKE_QUESTION_DRAFT)
    prompt_test = get_prompt_template(AiTaskType.PROMPT_TEST)
    repair = get_prompt_template(AiTaskType.REPAIR_DETERMINISTIC)

    assert netease.input_variables == ("song_info",)
    assert question_draft.vision_system_prompt
    assert prompt_test.dynamic_prompt is True
    assert repair.dynamic_prompt is True


def test_prompt_template_new_metadata_has_safe_defaults():
    """Existing construction remains compatible because new metadata is optional."""
    template = type(get_prompt_template(AiTaskType.CAPTURE_DRAFT))(
        task_type=AiTaskType.CAPTURE_DRAFT,
        version="v1",
        system_prompt="system",
        output_schema_name=None,
        json_mode=False,
        preferred_provider=None,
        max_tokens=100,
        description="test",
    )

    assert template.input_variables == ()
    assert template.vision_system_prompt is None
    assert template.dynamic_prompt is False


def test_registry_does_not_import_business_services():
    """ai_prompt_registry 不 import 任何业务 service（避免循环依赖）。"""
    business_services = [
        "app.services.capture_ai_draft",
        "app.services.capture_recognition",
        "app.services.mistake_staged_service",
        "app.services.diagram_service",
        "app.services.ai_analyze_service",
        "app.services.recommendation",
        "app.services.netease_service",
    ]

    # 清除 ai_prompt_registry 和所有业务 service 模块
    # （其他测试可能已经加载了业务 service 到 sys.modules）
    mods_to_clear = [
        k for k in sys.modules
        if k.startswith("app.services.ai_prompt_registry")
    ]
    for k in business_services:
        mods_to_clear.append(k)
    saved_modules = {
        name: sys.modules[name]
        for name in mods_to_clear
        if name in sys.modules
    }
    try:
        for name in mods_to_clear:
            sys.modules.pop(name, None)

        # 重新导入并检查 sys.modules 中没有业务 service
        importlib.import_module("app.services.ai_prompt_registry")

        for svc in business_services:
            assert svc not in sys.modules, f"ai_prompt_registry imported business service: {svc}"
    finally:
        for name in mods_to_clear:
            sys.modules.pop(name, None)
        sys.modules.update(saved_modules)
