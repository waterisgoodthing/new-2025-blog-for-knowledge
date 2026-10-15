"""统一 AI 输出校验器 — Batch 10 P0-05。

提供统一的 AI 输出校验入口 validate_ai_output()。
有 schema 的任务用 Pydantic 校验；无 schema 的任务直接返回原始数据。

约束：
- 不 import 业务 service，避免循环依赖。
- 校验失败返回 error_code 字符串，不抛异常。
- 不改变 HTTP 状态码和旧端点错误语义。
"""

import json
from dataclasses import dataclass

from pydantic import BaseModel

from app.schemas.ai import (
    ErrorInterpretationResponse,
    FinalAnalysisResponse,
    QuestionDraftResponse,
    StructuredDiagramData,
)
from app.schemas.ai_output import (
    KnowledgeCardOutput,
    RecommendationOutput,
    RecognitionOutput,
    VariantOutput,
)
from app.schemas.capture import MistakeDraftSuggestionV1
from app.services.ai_task_result import AiErrorCode
from app.services.ai_task_types import AiTaskType


@dataclass
class AiValidationResult:
    """AI 输出校验结果。"""

    success: bool
    data: dict | str | None = None
    error_code: str | None = None
    error_message_safe: str | None = None


# --- Schema 映射 ---

SCHEMA_MAP: dict[AiTaskType, type[BaseModel] | None] = {
    # --- 有 schema 的任务 (9) ---
    AiTaskType.CAPTURE_DRAFT: MistakeDraftSuggestionV1,
    AiTaskType.CAPTURE_RECOGNITION: RecognitionOutput,
    AiTaskType.MISTAKE_QUESTION_DRAFT: QuestionDraftResponse,
    AiTaskType.MISTAKE_ERROR_INTERPRETATION: ErrorInterpretationResponse,
    AiTaskType.MISTAKE_FINAL_ANALYSIS: FinalAnalysisResponse,
    AiTaskType.DIAGRAM_STRUCTURED: StructuredDiagramData,
    AiTaskType.GENERATE_VARIANT: VariantOutput,
    AiTaskType.GENERATE_KNOWLEDGE_CARD: KnowledgeCardOutput,
    AiTaskType.RECOMMENDATION: RecommendationOutput,
    # --- 无 schema 的任务 (7) — 纯文本或需手动 parse ---
    AiTaskType.ANALYZE_MISTAKE: None,
    AiTaskType.ANALYZE_TEXT: None,
    AiTaskType.KNOWLEDGE_SUMMARY: None,
    AiTaskType.PROMPT_TEST: None,
    AiTaskType.DIAGRAM_FALLBACK: None,
    AiTaskType.NETEASE_REASON: None,
    AiTaskType.REPAIR_DETERMINISTIC: None,
}


def validate_ai_output(task_type: AiTaskType, raw: dict | str | None) -> AiValidationResult:
    """统一 AI 输出校验入口。

    - 有 schema 的任务：用 Pydantic 校验，失败返回 schema_error / parse_error。
    - 无 schema 的任务：直接返回原始数据。
    - 不抛异常，调用方通过 success 字段判断。
    """
    schema = SCHEMA_MAP.get(task_type)

    if schema is None:
        return AiValidationResult(success=True, data=raw)

    if raw is None:
        return AiValidationResult(
            success=False,
            data=None,
            error_code=AiErrorCode.EMPTY_RESULT.value,
            error_message_safe=f"Empty result for {task_type.value}",
        )

    data = raw
    if isinstance(raw, str):
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return AiValidationResult(
                success=False,
                data=raw,
                error_code=AiErrorCode.PARSE_ERROR.value,
                error_message_safe=f"Failed to parse JSON for {task_type.value}",
            )

    if not isinstance(data, dict):
        return AiValidationResult(
            success=False,
            data=raw,
            error_code=AiErrorCode.SCHEMA_ERROR.value,
            error_message_safe=f"Expected dict for {task_type.value}, got {type(data).__name__}",
        )

    try:
        schema(**data)
        return AiValidationResult(success=True, data=data)
    except Exception as e:
        return AiValidationResult(
            success=False,
            data=data,
            error_code=AiErrorCode.SCHEMA_ERROR.value,
            error_message_safe=str(e)[:200],
        )
