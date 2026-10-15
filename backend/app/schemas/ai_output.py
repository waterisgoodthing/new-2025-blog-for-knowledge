"""AI 输出 Schema 补充 — Batch 10 P0-03。

为缺少 Pydantic schema 的 AI 任务补充输出 schema。
这些 schema 用于 ai_validator 统一校验 AI 原始输出。

已有 schema（在 ai.py / capture.py 中定义，不在此重复）：
- MistakeDraftSuggestionV1  — capture_draft
- QuestionDraftResponse     — mistake_question_draft
- ErrorInterpretationResponse — mistake_error_interpretation
- FinalAnalysisResponse     — mistake_final_analysis
- StructuredDiagramData     — diagram_structured
- AnalyzeResponse           — analyze_mistake/analyze_text（最终输出，AI 原始输出需手动 parse）
"""

from pydantic import BaseModel, Field


class RecognitionOutput(BaseModel):
    """capture_recognition 输出 schema。

    对应 RECOGNITION_SYSTEM_PROMPT 要求的 JSON 格式：
    {"text": "图片中识别到的全部文字内容"}
    """

    text: str


class VariantOutput(BaseModel):
    """generate_variant 输出 schema。

    对应 VARIANT_SYSTEM_PROMPT 要求的 JSON 格式。
    """

    question: str
    correct_answer: str
    analysis: str
    difficulty: str = "medium"
    knowledge_points: str = ""


class KnowledgeCardOutput(BaseModel):
    """generate_knowledge_card 输出 schema。

    对应 KNOWLEDGE_CARD_SYSTEM_PROMPT 要求的 JSON 格式。
    """

    title: str
    content: str
    knowledge_points: str = ""
    subject: str = ""


class RecommendationOutput(BaseModel):
    """recommendation 输出 schema。

    对应 recommendation.py SYSTEM_PROMPT 要求的 JSON 格式。
    """

    title: str = ""
    type: str = "note"
    reason: str = ""
    target: str = ""
    actionLabel: str = ""
