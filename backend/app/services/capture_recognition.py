"""Capture recognition adapter — Batch 8 窄调用边界。

只封装单图 OCR/多模态识别，不建设多供应商管理、模型路由或生产级队列。
Batch 9 可用统一 gateway adapter 替换本模块实现，而不改变 capture 领域合同。
"""

import base64
import logging
from dataclasses import dataclass

from app.services.ai_gateway import call_vision
from app.services.ai_prompt_registry import build_vision_messages, render_user_content
from app.services.ai_task_types import AiTaskType
from app.services.ai_validator import validate_ai_output
from app.services.capture_failure_taxonomy import (
    CaptureFailureCategory,
    categorize_failure,
    categorize_provider_category,
    categorize_provider_error,
)

logger = logging.getLogger(__name__)


# 超时由底层 httpx.AsyncClient(timeout=120) 控制；这里不引入额外队列。
#
# 安全约定：本模块的 warning 日志**只记录分类、错误码与 capture_id**。
# ai_service 已把 provider 失败收敛为 AIProviderError（只带分类/状态，不带
# 原始响应体），gateway 通过 failure_category 透传；本模块优先使用该结构化
# 分类，只有在缺失时才回退到 categorize_provider_error 本地嗅探。任何情况下
# 都不得把异常字符串写入日志。


@dataclass
class RecognitionResult:
    """识别结果。"""

    recognized_text: str
    success: bool
    error_code: str | None = None
    error_message_safe: str | None = None
    failure_category: str | None = None
    raw_output: dict | None = None  # 仅内部日志，不进入前端 DTO


async def recognize_image(
    image_bytes: bytes,
    mime_type: str,
    *,
    use_fake: bool = False,
    fake_text: str = "",
    capture_id: str | None = None,
) -> RecognitionResult:
    """对单张图片执行 OCR/多模态识别。

    - use_fake=True 时返回 fake_text，用于无真实凭据时的 service/schema/状态机测试。
    - 真实调用时封装 call_ocr_model，不感知供应商路由。
    - 失败返回 error_code，不抛异常给 capture service。
    """
    if use_fake:
        return RecognitionResult(
            recognized_text=fake_text,
            success=True,
            raw_output={"_fake": True},
        )

    if not image_bytes:
        return RecognitionResult(
            recognized_text="",
            success=False,
            error_code="empty_input",
            error_message_safe="Image bytes are empty",
            failure_category=categorize_failure("empty_input").value,
        )

    try:
        recognition_prompt = render_user_content(
            AiTaskType.CAPTURE_RECOGNITION,
            {},
        )
        content = [
            {"type": "text", "text": recognition_prompt},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{base64.b64encode(image_bytes).decode()}"
                },
            },
        ]
        messages = build_vision_messages(AiTaskType.CAPTURE_RECOGNITION, content)
        gw = await call_vision(
            AiTaskType.CAPTURE_RECOGNITION,
            messages,
            target_type="Capture" if capture_id is not None else None,
            target_id=capture_id,
        )
        if not gw.success:
            err = gw.error or ""
            if "no provider" in err.lower() or "not configured" in err.lower():
                raise ValueError(err)
            category = _resolve_provider_category(gw.failure_category, err)
            return _provider_failure_result(category, capture_id)
        result = gw.data
        validation = validate_ai_output(AiTaskType.CAPTURE_RECOGNITION, result)
        if not validation.success:
            return RecognitionResult(
                recognized_text="",
                success=False,
                error_code=validation.error_code,
                error_message_safe=validation.error_message_safe,
                failure_category=categorize_failure(validation.error_code).value,
                raw_output=result if isinstance(result, dict) else None,
            )
        text = str(result.get("text", "")).strip()
        if not text:
            return RecognitionResult(
                recognized_text="",
                success=False,
                error_code="empty_result",
                error_message_safe="Recognition returned empty text",
                failure_category=categorize_failure("empty_result").value,
                raw_output=result,
            )
        return RecognitionResult(
            recognized_text=text,
            success=True,
            raw_output=result,
        )
    except ValueError:
        # No AI provider configured
        category = categorize_failure("no_provider")
        logger.warning(
            "Recognition failed category=%s code=%s capture_id=%s",
            category.value,
            "no_provider",
            capture_id,
        )
        return RecognitionResult(
            recognized_text="",
            success=False,
            error_code="no_provider",
            error_message_safe="No AI provider configured",
            failure_category=category.value,
        )
    except RuntimeError as e:
        # 优先使用结构化分类；缺失时回退本地嗅探。异常文本绝不进日志或 DTO。
        category = _resolve_provider_category(getattr(e, "category", None), str(e))
        return _provider_failure_result(category, capture_id)
    except Exception:
        category = categorize_failure("parse_error")
        logger.warning(
            "Recognition failed category=%s code=%s capture_id=%s",
            category.value,
            "parse_error",
            capture_id,
        )
        return RecognitionResult(
            recognized_text="",
            success=False,
            error_code="parse_error",
            error_message_safe="Failed to parse recognition result",
            failure_category=category.value,
        )


def _resolve_provider_category(
    explicit: str | None, message: str
) -> CaptureFailureCategory:
    """优先使用结构化 provider 分类，缺失时回退到字符串嗅探。"""
    mapped = categorize_provider_category(explicit)
    if mapped is not None:
        return mapped
    return categorize_provider_error(message)


def _provider_failure_result(
    category: CaptureFailureCategory, capture_id: str | None
) -> RecognitionResult:
    """记录脱敏 warning 并构造 provider 失败结果。"""
    error_code, error_message_safe = _provider_failure_error_fields(category)
    logger.warning(
        "Recognition failed category=%s code=%s capture_id=%s",
        category.value,
        error_code,
        capture_id,
    )
    return RecognitionResult(
        recognized_text="",
        success=False,
        error_code=error_code,
        error_message_safe=error_message_safe,
        failure_category=category.value,
    )


def _provider_failure_error_fields(
    category: CaptureFailureCategory,
) -> tuple[str, str]:
    """把 provider 失败分类映射为稳定的 error_code / 安全错误信息。

    泛化的 provider 失败仍落到 `provider_error`（分类为 unknown），保持既有
    failure-matrix 合同；只有能明确归因的失败才使用更细的 error_code。
    """
    if category is CaptureFailureCategory.PROVIDER_TIMEOUT:
        return "timeout", "Recognition timed out"
    if category is CaptureFailureCategory.PROVIDER_AUTH:
        return "provider_auth", "AI provider authentication failed"
    if category is CaptureFailureCategory.INVALID_MODEL:
        return "invalid_model", "AI model unavailable"
    if category is CaptureFailureCategory.INVALID_RESPONSE:
        return "parse_error", "AI response could not be parsed"
    return "provider_error", "AI provider error"
