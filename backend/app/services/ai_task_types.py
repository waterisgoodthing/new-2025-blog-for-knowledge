"""AI 任务类型枚举 — Batch 10。

把散落在各 service 和 router 中的 task_type 字符串收敛为统一枚举。
枚举值与 ai_call_logs.task_type 现有字符串完全一致，保持向后兼容。
"""

from enum import Enum


class AiTaskType(str, Enum):
    """AI 任务类型枚举。

    使用 str, Enum 双继承，保证 AiTaskType.CAPTURE_DRAFT == "capture_draft" 为 True。
    与 ai_call_logs.task_type (String(50)) 字符串兼容。
    """

    # capture 域
    CAPTURE_DRAFT = "capture_draft"
    CAPTURE_RECOGNITION = "capture_recognition"

    # analyze 域
    ANALYZE_MISTAKE = "analyze_mistake"
    ANALYZE_TEXT = "analyze_text"
    GENERATE_VARIANT = "generate_variant"
    GENERATE_KNOWLEDGE_CARD = "generate_knowledge_card"
    KNOWLEDGE_SUMMARY = "knowledge_summary"
    PROMPT_TEST = "prompt_test"

    # staged mistake 域
    MISTAKE_QUESTION_DRAFT = "mistake_question_draft"
    MISTAKE_ERROR_INTERPRETATION = "mistake_error_interpretation"
    MISTAKE_FINAL_ANALYSIS = "mistake_final_analysis"

    # diagram 域
    DIAGRAM_STRUCTURED = "diagram_structured"
    DIAGRAM_FALLBACK = "diagram_fallback"

    # 辅助域
    NETEASE_REASON = "netease_reason"
    RECOMMENDATION = "recommendation"
    REPAIR_DETERMINISTIC = "repair_deterministic"
