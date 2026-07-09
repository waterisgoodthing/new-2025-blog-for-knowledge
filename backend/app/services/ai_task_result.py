"""AI 任务标准化结果 — Batch 10 P0-02。

AiTaskResult 是内部统一结果对象，不直接暴露给外部 API。
外部 API 请求/响应 schema 保持不变，router 层负责适配。

AiErrorCode 标准化失败处理，但不改变 HTTP 状态码和旧端点错误语义。
"""

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.services.ai_gateway import GatewayCallResult
    from app.services.ai_task_types import AiTaskType


class AiErrorCode(str, Enum):
    """AI 任务错误码。

    与现有 capture 模块的 error_code 字符串保持一致，
    不改变 HTTP 状态码和旧端点错误语义。
    """

    EMPTY_INPUT = "empty_input"
    NO_PROVIDER = "no_provider"
    TIMEOUT = "timeout"
    PROVIDER_ERROR = "provider_error"
    SCHEMA_ERROR = "schema_error"
    PARSE_ERROR = "parse_error"
    EMPTY_RESULT = "empty_result"


@dataclass
class AiTaskResult:
    """AI 任务的标准化结果。

    内部使用，不直接暴露给外部 API。
    router 层负责从 AiTaskResult 提取数据并构造端点响应。

    Attributes:
        task_type: 任务类型枚举
        success: 是否成功
        data: 校验后的数据（dict 或 str），失败时为 None
        error_code: 失败时的错误码（AiErrorCode 值），成功时为 None
        error_message_safe: 面向用户的安全错误信息（不含敏感细节）
        prompt_version: 使用的 Prompt 版本（如 "v1"）
        gateway_result: Gateway 调用结果（含 provider/model/latency 等元数据）
    """

    task_type: "AiTaskType"
    success: bool
    data: dict | str | None = None
    error_code: str | None = None
    error_message_safe: str | None = None
    prompt_version: str | None = None
    gateway_result: "GatewayCallResult | None" = None

    @staticmethod
    def success_result(
        task_type: "AiTaskType",
        data: dict | str | None,
        *,
        prompt_version: str | None = None,
        gateway_result: "GatewayCallResult | None" = None,
    ) -> "AiTaskResult":
        """构造成功结果。"""
        return AiTaskResult(
            task_type=task_type,
            success=True,
            data=data,
            prompt_version=prompt_version,
            gateway_result=gateway_result,
        )

    @staticmethod
    def failure_result(
        task_type: "AiTaskType",
        error_code: str,
        error_message_safe: str,
        *,
        prompt_version: str | None = None,
        gateway_result: "GatewayCallResult | None" = None,
        data: dict | str | None = None,
    ) -> "AiTaskResult":
        """构造失败结果。"""
        return AiTaskResult(
            task_type=task_type,
            success=False,
            data=data,
            error_code=error_code,
            error_message_safe=error_message_safe,
            prompt_version=prompt_version,
            gateway_result=gateway_result,
        )
