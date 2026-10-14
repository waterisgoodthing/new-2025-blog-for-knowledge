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
from app.services.capture_failure_taxonomy import (
    CaptureFailureCategory,
    categorize_failure,
    categorize_provider_category,
    categorize_provider_error,
)

logger = logging.getLogger(__name__)

# 安全约定：warning 日志只记录分类、错误码与 capture_id。provider 异常文本可能
# 内嵌原始响应体 / 凭据，绝不写入日志。
#
# F05: ai_service 已把 provider 失败收敛为 AIProviderError（只带分类/状态），
# gateway 通过 failure_category 透传。本模块优先使用该结构化分类，只有缺失时才
# 回退到 categorize_provider_error 本地嗅探（与 capture_recognition 一致）。


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
    capture_id: str | None = None,
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
        gw = await call_text(
            AiTaskType.CAPTURE_DRAFT,
            messages,
            input_summary=draft_input.recognized_text[:200],
            target_type="Capture" if capture_id is not None else None,
            target_id=capture_id,
        )
        if not gw.success:
            err = gw.error or ""
            if "no provider" in err.lower() or "not configured" in err.lower():
                raise ValueError(err)
            category = _resolve_provider_category(gw.failure_category, err)
            return _draft_provider_failure_result(category, capture_id)
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
    except ValidationError:
        code = "schema_error"
        category = categorize_failure(code).value
        logger.warning(
            "AI draft failed category=%s code=%s capture_id=%s",
            category,
            code,
            capture_id,
        )
        return DraftResult(
            suggestion=None,
            success=False,
            error_code=code,
            error_message_safe="AI output failed schema validation",
        )
    except ValueError:
        code = "no_provider"
        category = categorize_failure(code).value
        logger.warning(
            "AI draft failed category=%s code=%s capture_id=%s",
            category,
            code,
            capture_id,
        )
        return DraftResult(
            suggestion=None,
            success=False,
            error_code=code,
            error_message_safe="No AI provider configured",
        )
    except RuntimeError as e:
        # 优先使用结构化分类；缺失时回退本地嗅探。异常文本绝不进日志或 DTO。
        category = _resolve_provider_category(getattr(e, "category", None), str(e))
        return _draft_provider_failure_result(category, capture_id)
    except Exception:
        code = "parse_error"
        category = categorize_failure(code).value
        logger.warning(
            "AI draft failed category=%s code=%s capture_id=%s",
            category,
            code,
            capture_id,
        )
        return DraftResult(
            suggestion=None,
            success=False,
            error_code=code,
            error_message_safe="Failed to parse AI draft result",
        )


def _resolve_provider_category(
    explicit: str | None, message: str
) -> CaptureFailureCategory:
    """优先使用结构化 provider 分类，缺失时回退到字符串嗅探。"""
    mapped = categorize_provider_category(explicit)
    if mapped is not None:
        return mapped
    return categorize_provider_error(message)


def _draft_provider_failure_result(
    category: CaptureFailureCategory, capture_id: str | None
) -> DraftResult:
    """记录脱敏 warning 并构造 provider 失败结果。"""
    error_code, error_message_safe = _draft_provider_failure_fields(category)
    logger.warning(
        "AI draft failed category=%s code=%s capture_id=%s",
        category.value,
        error_code,
        capture_id,
    )
    return DraftResult(
        suggestion=None,
        success=False,
        error_code=error_code,
        error_message_safe=error_message_safe,
    )


def _draft_provider_failure_fields(
    category: CaptureFailureCategory,
) -> tuple[str, str]:
    """把 provider 失败分类映射为稳定的 error_code / 安全错误信息。

    泛化失败仍落到 `provider_error`（分类 unknown），保持既有 error_code 合同；
    可归因失败使用既有细分 error_code（timeout / provider_auth / invalid_model /
    parse_error），与 capture_recognition 的映射保持一致。
    """
    if category is CaptureFailureCategory.PROVIDER_TIMEOUT:
        return "timeout", "AI draft timed out"
    if category is CaptureFailureCategory.PROVIDER_AUTH:
        return "provider_auth", "AI provider authentication failed"
    if category is CaptureFailureCategory.INVALID_MODEL:
        return "invalid_model", "AI model unavailable"
    if category is CaptureFailureCategory.INVALID_RESPONSE:
        return "parse_error", "AI response could not be parsed"
    return "provider_error", "AI provider error"


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
