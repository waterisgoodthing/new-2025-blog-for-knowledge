"""Tests for AiTaskType enum — Batch 10 P0-01."""

from app.services.ai_task_types import AiTaskType


def test_ai_task_type_count():
    """枚举覆盖全部 16 个 task_type。"""
    members = list(AiTaskType)
    assert len(members) == 16


def test_ai_task_type_string_values():
    """枚举值与现有字符串完全一致。"""
    expected = {
        "capture_draft",
        "capture_recognition",
        "analyze_mistake",
        "analyze_text",
        "generate_variant",
        "generate_knowledge_card",
        "knowledge_summary",
        "prompt_test",
        "mistake_question_draft",
        "mistake_error_interpretation",
        "mistake_final_analysis",
        "diagram_structured",
        "diagram_fallback",
        "netease_reason",
        "recommendation",
        "repair_deterministic",
    }
    actual = {m.value for m in AiTaskType}
    assert actual == expected


def test_ai_task_type_str_compatibility():
    """str, Enum 双继承：枚举值等于字符串。"""
    assert AiTaskType.CAPTURE_DRAFT == "capture_draft"
    assert AiTaskType.CAPTURE_RECOGNITION == "capture_recognition"
    assert AiTaskType.ANALYZE_MISTAKE == "analyze_mistake"
    assert AiTaskType.REPAIR_DETERMINISTIC == "repair_deterministic"


def test_ai_task_type_hashable_as_string():
    """枚举可作为字典 key（字符串兼容）。"""
    d = {AiTaskType.CAPTURE_DRAFT: "test"}
    assert d["capture_draft"] == "test"


def test_ai_task_type_from_string():
    """从字符串构造枚举。"""
    assert AiTaskType("capture_draft") == AiTaskType.CAPTURE_DRAFT
    assert AiTaskType("recommendation") == AiTaskType.RECOMMENDATION
