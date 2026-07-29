"""Capture AI draft adapter — Batch 8 窄调用边界。

封装 call_text_model 生成题面/解析/错因/知识点建议草稿。
不建设 Prompt 管理后台、Validator 管理、完整 AI 审计或成本统计。
所有输出进入 capture 草稿区并允许人工编辑，不直接写正式数据。
"""

import logging
from dataclasses import dataclass

from pydantic import ValidationError

from app.schemas.capture import (
    CaptureDraftInput,
    KnowledgePointSuggestion,
    MistakeDraftSuggestionV1,
    SubjectSuggestion,
)
from app.services.ai_gateway import call_text
from app.services.ai_prompt_registry import build_text_messages
from app.services.ai_task_types import AiTaskType
from app.services.ai_validator import validate_ai_output

logger = logging.getLogger(__name__)


@dataclass
class DraftResult:
    """AI 草稿生成结果。"""

    suggestion: MistakeDraftSuggestionV1 | None
    success: bool
    error_code: str | None = None
    error_message_safe: str | None = None


async def draft_mistake(
    draft_input: CaptureDraftInput,
    *,
    use_fake: bool = False,
) -> DraftResult:
    """从识别文本和用户错因生成结构化错题草稿。

    - use_fake=True 时返回固定假数据，用于无真实凭据时的测试。
    - 真实调用时封装 call_text_model，不感知供应商路由。
    - schema 校验失败视为 AI 阶段失败，不写入 mistake_drafts。
    """
    if use_fake:
        return DraftResult(
            suggestion=MistakeDraftSuggestionV1(
                question_text="[fake] 题面草稿",
                analysis_text="[fake] 解析草稿",
                error_summary="[fake] 错因总结",
                subject_suggestion=SubjectSuggestion(
                    id=None, label="fake 学科", confidence=0.5
                ),
                knowledge_point_suggestions=[
                    KnowledgePointSuggestion(
                        id=None, label="fake 知识点", confidence=0.5
                    )
                ],
                warnings=["fake warning"],
            ),
            success=True,
        )

    if not draft_input.recognized_text.strip():
        return DraftResult(
            suggestion=None,
            success=False,
            error_code="empty_input",
            error_message_safe="Recognized text is empty",
        )

    try:
        user_content = f"识别到的题目文字：\n{draft_input.recognized_text}"
        if draft_input.user_error_context:
            user_content += f"\n\n学生自述错因：\n{draft_input.user_error_context}"
        if draft_input.subject_label:
            user_content += f"\n\n学科上下文：{draft_input.subject_label}"

        messages = build_text_messages(AiTaskType.CAPTURE_DRAFT, user_content)
        gw = await call_text(AiTaskType.CAPTURE_DRAFT, messages, input_summary=draft_input.recognized_text[:200])
        if not gw.success:
            err = gw.error or ""
            if "no provider" in err.lower() or "not configured" in err.lower():
                raise ValueError(err)
            raise RuntimeError(err)
        raw = gw.data
        validation = validate_ai_output(AiTaskType.CAPTURE_DRAFT, raw)
        if validation.success:
            suggestion = _validate_suggestion(raw)
            return DraftResult(suggestion=suggestion, success=True)
        # Fallback: validate_ai_output may reject edge-case formats _validate_suggestion can normalize
        try:
            suggestion = _validate_suggestion(raw)
            return DraftResult(suggestion=suggestion, success=True)
        except Exception:
            return DraftResult(
                suggestion=None,
                success=False,
                error_code=validation.error_code,
                error_message_safe=validation.error_message_safe,
            )
    except ValidationError as e:
        logger.warning("AI draft schema validation failed: %s", str(e)[:200])
        return DraftResult(
            suggestion=None,
            success=False,
            error_code="schema_error",
            error_message_safe="AI output failed schema validation",
        )
    except ValueError as e:
        logger.warning("AI draft failed (no provider): %s", str(e)[:200])
        return DraftResult(
            suggestion=None,
            success=False,
            error_code="no_provider",
            error_message_safe="No AI provider configured",
        )
    except RuntimeError as e:
        err_str = str(e)[:200]
        is_timeout = "timeout" in err_str.lower() or "timed out" in err_str.lower()
        logger.warning("AI draft failed (provider error): %s", err_str)
        return DraftResult(
            suggestion=None,
            success=False,
            error_code="timeout" if is_timeout else "provider_error",
            error_message_safe="AI provider error"
            if not is_timeout
            else "AI draft timed out",
        )
    except Exception as e:
        err_str = str(e)[:200]
        logger.warning("AI draft failed (unexpected): %s", err_str)
        return DraftResult(
            suggestion=None,
            success=False,
            error_code="parse_error",
            error_message_safe="Failed to parse AI draft result",
        )


def _validate_suggestion(raw: dict) -> MistakeDraftSuggestionV1:
    """将原始 AI 输出校验为 MistakeDraftSuggestionV1。"""
    subject_raw = raw.get("subject_suggestion")
    subject = None
    if isinstance(subject_raw, dict) and subject_raw:
        subject = SubjectSuggestion(
            id=subject_raw.get("id"),
            label=subject_raw.get("label"),
            confidence=subject_raw.get("confidence"),
        )

    kp_raw = raw.get("knowledge_point_suggestions", [])
    if isinstance(kp_raw, str):
        kp_raw = [{"id": None, "label": kp_raw, "confidence": None}]
    kp_list = []
    for item in kp_raw:
        if isinstance(item, dict):
            kp_list.append(
                KnowledgePointSuggestion(
                    id=item.get("id"),
                    label=str(item.get("label", "")),
                    confidence=item.get("confidence"),
                )
            )
        elif isinstance(item, str):
            kp_list.append(KnowledgePointSuggestion(id=None, label=item, confidence=None))

    warnings_raw = raw.get("warnings", [])
    if isinstance(warnings_raw, str):
        warnings_raw = [warnings_raw]

    return MistakeDraftSuggestionV1(
        question_text=str(raw.get("question_text", "")),
        analysis_text=str(raw.get("analysis_text", "")),
        error_summary=str(raw.get("error_summary", "")),
        subject_suggestion=subject,
        knowledge_point_suggestions=kp_list,
        warnings=[str(w) for w in warnings_raw] if isinstance(warnings_raw, list) else [],
    )
