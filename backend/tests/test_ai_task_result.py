"""Tests for AiTaskResult and AiErrorCode — Batch 10 P0-02."""

from app.services.ai_task_result import AiErrorCode, AiTaskResult
from app.services.ai_task_types import AiTaskType


def test_ai_error_code_count():
    """AiErrorCode 覆盖 7 种错误码。"""
    members = list(AiErrorCode)
    assert len(members) == 7


def test_ai_error_code_values():
    """错误码值与现有 capture 模块字符串一致。"""
    expected = {
        "empty_input",
        "no_provider",
        "timeout",
        "provider_error",
        "schema_error",
        "parse_error",
        "empty_result",
    }
    actual = {m.value for m in AiErrorCode}
    assert actual == expected


def test_ai_error_code_str_compatibility():
    """str, Enum 双继承。"""
    assert AiErrorCode.EMPTY_INPUT == "empty_input"
    assert AiErrorCode.SCHEMA_ERROR == "schema_error"


def test_ai_task_result_success():
    """成功结果构造。"""
    result = AiTaskResult.success_result(
        AiTaskType.CAPTURE_DRAFT,
        {"question_text": "test"},
        prompt_version="v1",
    )
    assert result.success is True
    assert result.task_type == AiTaskType.CAPTURE_DRAFT
    assert result.data == {"question_text": "test"}
    assert result.error_code is None
    assert result.error_message_safe is None
    assert result.prompt_version == "v1"


def test_ai_task_result_failure():
    """失败结果构造。"""
    result = AiTaskResult.failure_result(
        AiTaskType.CAPTURE_RECOGNITION,
        AiErrorCode.TIMEOUT.value,
        "Recognition timed out",
    )
    assert result.success is False
    assert result.task_type == AiTaskType.CAPTURE_RECOGNITION
    assert result.data is None
    assert result.error_code == "timeout"
    assert result.error_message_safe == "Recognition timed out"


def test_ai_task_result_with_gateway_result():
    """带 gateway_result 的结果。"""
    result = AiTaskResult.success_result(
        AiTaskType.ANALYZE_MISTAKE,
        {"title": "test"},
        prompt_version="v1",
        gateway_result=None,
    )
    assert result.gateway_result is None
    assert result.success is True


def test_ai_task_result_failure_with_data():
    """失败结果可携带原始数据（如 schema_error 时保留原始输出）。"""
    result = AiTaskResult.failure_result(
        AiTaskType.GENERATE_VARIANT,
        AiErrorCode.SCHEMA_ERROR.value,
        "AI output failed schema validation",
        data={"raw": "output"},
    )
    assert result.success is False
    assert result.data == {"raw": "output"}
    assert result.error_code == "schema_error"
