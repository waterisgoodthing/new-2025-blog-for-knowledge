"""Capture failure taxonomy — derived classification over the existing error vocabulary.

本模块不引入新的持久化列，只把既有 error_code 字符串映射为稳定的
`CaptureFailureCategory`，供 capture DTO 派生字段与分类日志使用（W4-E01/W4-E02）。

`image_format` 目前没有直接对应的 error_code 来源，保留为将来扩展的枚举值；
未知 code 一律落到 `unknown`，不抛异常。
"""

from enum import Enum


class CaptureFailureCategory(str, Enum):
    """采集识别失败的稳定分类。"""

    PROVIDER_AUTH = "provider_auth"
    PROVIDER_TIMEOUT = "provider_timeout"
    INVALID_MODEL = "invalid_model"
    INVALID_RESPONSE = "invalid_response"
    SCHEMA_VALIDATION = "schema_validation"
    IMAGE_FETCH = "image_fetch"
    IMAGE_FORMAT = "image_format"
    UNKNOWN = "unknown"


_ERROR_CODE_CATEGORY: dict[str, CaptureFailureCategory] = {
    "no_provider": CaptureFailureCategory.PROVIDER_AUTH,
    "provider_auth": CaptureFailureCategory.PROVIDER_AUTH,
    "invalid_model": CaptureFailureCategory.INVALID_MODEL,
    "timeout": CaptureFailureCategory.PROVIDER_TIMEOUT,
    "schema_error": CaptureFailureCategory.SCHEMA_VALIDATION,
    "parse_error": CaptureFailureCategory.INVALID_RESPONSE,
    "empty_result": CaptureFailureCategory.INVALID_RESPONSE,
    "attachment_missing": CaptureFailureCategory.IMAGE_FETCH,
    "empty_input": CaptureFailureCategory.IMAGE_FETCH,
}


def categorize_failure(error_code: str | None) -> CaptureFailureCategory:
    """把既有 error_code 映射为失败分类；未识别/None -> unknown。"""
    if error_code is None:
        return CaptureFailureCategory.UNKNOWN
    return _ERROR_CODE_CATEGORY.get(error_code, CaptureFailureCategory.UNKNOWN)


# Structured provider-failure categories produced by ai_service.AIProviderError
# and surfaced through ai_gateway.GatewayCallResult.failure_category. Preferring
# this mapping over text sniffing keeps native transport errors and malformed
# responses classified correctly across layers (F05).
_PROVIDER_CATEGORY_MAP: dict[str, CaptureFailureCategory] = {
    "provider_auth": CaptureFailureCategory.PROVIDER_AUTH,
    "provider_timeout": CaptureFailureCategory.PROVIDER_TIMEOUT,
    "invalid_model": CaptureFailureCategory.INVALID_MODEL,
    "invalid_response": CaptureFailureCategory.INVALID_RESPONSE,
    "provider_error": CaptureFailureCategory.UNKNOWN,
    "no_provider": CaptureFailureCategory.PROVIDER_AUTH,
}


def categorize_provider_category(
    category: str | None,
) -> CaptureFailureCategory | None:
    """把结构化 provider 分类映射为 CaptureFailureCategory。

    仅接受 AIProviderError / gateway 定义的稳定分类；未知或缺失返回 None，
    以便调用方回退到 ``categorize_provider_error`` 字符串嗅探。
    """
    if not category:
        return None
    return _PROVIDER_CATEGORY_MAP.get(category)


_AUTH_MARKERS = (
    "401",
    "403",
    "429",
    "quota",
    "apikey",
    "api key",
    "api_key",
    "invalid key",
    "unauthorized",
    "forbidden",
    "authentication",
)
_INVALID_MODEL_MARKERS = ("404", "model not found", "model_not_found", "unknown model")
_TIMEOUT_MARKERS = ("timeout", "timed out", "connect")


def categorize_provider_error(message: str) -> CaptureFailureCategory:
    """从 provider 错误字符串推断分类。

    顺序：鉴权/额度 -> 模型无效 -> 超时/连接 -> unknown。
    仅做子串嗅探，不解析原始响应、不抛出异常。
    """
    text = (message or "").lower()
    if any(marker in text for marker in _AUTH_MARKERS):
        return CaptureFailureCategory.PROVIDER_AUTH
    if any(marker in text for marker in _INVALID_MODEL_MARKERS):
        return CaptureFailureCategory.INVALID_MODEL
    if any(marker in text for marker in _TIMEOUT_MARKERS):
        return CaptureFailureCategory.PROVIDER_TIMEOUT
    return CaptureFailureCategory.UNKNOWN
