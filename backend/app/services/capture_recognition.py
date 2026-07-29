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

logger = logging.getLogger(__name__)


# 超时由底层 httpx.AsyncClient(timeout=120) 控制；这里不引入额外队列。


@dataclass
class RecognitionResult:
    """识别结果。"""

    recognized_text: str
    success: bool
    error_code: str | None = None
    error_message_safe: str | None = None
    raw_output: dict | None = None  # 仅内部日志，不进入前端 DTO


async def recognize_image(
    image_bytes: bytes,
    mime_type: str,
    *,
    use_fake: bool = False,
    fake_text: str = "",
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
        gw = await call_vision(AiTaskType.CAPTURE_RECOGNITION, messages)
        if not gw.success:
            err = gw.error or ""
            if "no provider" in err.lower() or "not configured" in err.lower():
                raise ValueError(err)
            raise RuntimeError(err)
        result = gw.data
        validation = validate_ai_output(AiTaskType.CAPTURE_RECOGNITION, result)
        if not validation.success:
            return RecognitionResult(
                recognized_text="",
                success=False,
                error_code=validation.error_code,
                error_message_safe=validation.error_message_safe,
                raw_output=result if isinstance(result, dict) else None,
            )
        text = str(result.get("text", "")).strip()
        if not text:
            return RecognitionResult(
                recognized_text="",
                success=False,
                error_code="empty_result",
                error_message_safe="Recognition returned empty text",
                raw_output=result,
            )
        return RecognitionResult(
            recognized_text=text,
            success=True,
            raw_output=result,
        )
    except ValueError as e:
        # No AI provider configured
        logger.warning("Recognition failed (no provider): %s", str(e)[:200])
        return RecognitionResult(
            recognized_text="",
            success=False,
            error_code="no_provider",
            error_message_safe="No AI provider configured",
        )
    except RuntimeError as e:
        err_str = str(e)[:200]
        is_timeout = "timeout" in err_str.lower() or "timed out" in err_str.lower()
        logger.warning("Recognition failed (provider error): %s", err_str)
        return RecognitionResult(
            recognized_text="",
            success=False,
            error_code="timeout" if is_timeout else "provider_error",
            error_message_safe="AI provider error" if not is_timeout else "Recognition timed out",
        )
    except Exception as e:
        err_str = str(e)[:200]
        logger.warning("Recognition failed (unexpected): %s", err_str)
        return RecognitionResult(
            recognized_text="",
            success=False,
            error_code="parse_error",
            error_message_safe="Failed to parse recognition result",
        )
