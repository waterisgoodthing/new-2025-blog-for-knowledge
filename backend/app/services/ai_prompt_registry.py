"""AI Prompt 模板注册表 — Batch 10 P0-04。

从 ai_prompts 导入常量，定义 PromptTemplate 和 PROMPT_REGISTRY。
本 module 不 import 任何业务 service，避免循环依赖。

PromptTemplate.system_prompt 是该任务使用的 system 消息内容。
对于将详细指令放在 user content 中的任务（如 capture_recognition），
user_content_template 字段记录 user content 中使用的 Prompt 模板。
"""

from dataclasses import dataclass, replace
from string import Formatter
from typing import Mapping

from app.services.ai_prompts import (
    ANALYZE_VISION_SYSTEM_MESSAGE,
    DIAGRAM_STRUCTURED_SYSTEM_PROMPT,
    DRAFT_SYSTEM_PROMPT,
    ERROR_INTERPRETATION_SYSTEM_PROMPT,
    FINAL_ANALYSIS_SYSTEM_PROMPT,
    KNOWLEDGE_CARD_SYSTEM_PROMPT,
    KNOWLEDGE_SUMMARY_SYSTEM_PROMPT,
    NETEASE_REASON_PROMPT,
    NETEASE_SYSTEM_MESSAGE,
    OCR_SYSTEM_PROMPT,
    QWEN_IMAGE_FALLBACK_PROMPT,
    QUESTION_DRAFT_SYSTEM_PROMPT,
    QUESTION_DRAFT_VISION_SYSTEM_MESSAGE,
    RECOGNITION_SYSTEM_MESSAGE,
    RECOGNITION_SYSTEM_PROMPT,
    RECOMMENDATION_SYSTEM_PROMPT,
    TEXT_SYSTEM_PROMPT,
    VARIANT_SYSTEM_PROMPT,
    standardize_prompt,
)
from app.services.ai_task_types import AiTaskType


@dataclass(frozen=True)
class PromptTemplate:
    """AI 任务的 Prompt 模板。

    Attributes:
        task_type: 任务类型枚举
        version: Prompt 版本号（如 "v1"）
        system_prompt: system 消息内容
        output_schema_name: 对应的 Pydantic schema 类名（None 表示无 schema 或需手动 parse）
        json_mode: 是否要求 JSON 输出
        preferred_provider: 首选供应商（"deepseek" / "dashscope_vision" / "qwen_general"）
        max_tokens: 默认 max_tokens
        description: 人类可读描述
        user_content_template: user content 中使用的 Prompt 模板（如有）
    """

    task_type: AiTaskType
    version: str
    system_prompt: str
    output_schema_name: str | None
    json_mode: bool
    preferred_provider: str | None
    max_tokens: int
    description: str
    user_content_template: str | None = None
    input_variables: tuple[str, ...] = ()
    vision_system_prompt: str | None = None
    dynamic_prompt: bool = False


PROMPT_REGISTRY: dict[AiTaskType, PromptTemplate] = {
    # capture 域
    AiTaskType.CAPTURE_DRAFT: PromptTemplate(
        task_type=AiTaskType.CAPTURE_DRAFT,
        version="v1",
        system_prompt=DRAFT_SYSTEM_PROMPT,
        output_schema_name="MistakeDraftSuggestionV1",
        json_mode=True,
        preferred_provider="deepseek",
        max_tokens=8000,
        description="从识别文本和用户错因生成结构化错题草稿",
    ),
    AiTaskType.CAPTURE_RECOGNITION: PromptTemplate(
        task_type=AiTaskType.CAPTURE_RECOGNITION,
        version="v1",
        system_prompt=RECOGNITION_SYSTEM_MESSAGE,
        output_schema_name="RecognitionOutput",
        json_mode=True,
        preferred_provider="dashscope_vision",
        max_tokens=4000,
        description="从图片中提取所有可见文字内容",
        user_content_template=RECOGNITION_SYSTEM_PROMPT,
    ),
    # analyze 域
    AiTaskType.ANALYZE_MISTAKE: PromptTemplate(
        task_type=AiTaskType.ANALYZE_MISTAKE,
        version="v1",
        system_prompt=ANALYZE_VISION_SYSTEM_MESSAGE,
        output_schema_name=None,
        json_mode=True,
        preferred_provider="dashscope_vision",
        max_tokens=8000,
        description="从错题图片中提取题目信息并解题（手动 parse）",
        user_content_template=OCR_SYSTEM_PROMPT,
    ),
    AiTaskType.ANALYZE_TEXT: PromptTemplate(
        task_type=AiTaskType.ANALYZE_TEXT,
        version="v1",
        system_prompt=TEXT_SYSTEM_PROMPT,
        output_schema_name=None,
        json_mode=True,
        preferred_provider="deepseek",
        max_tokens=8000,
        description="分析文本题目，给出答案和解析（手动 parse）",
    ),
    AiTaskType.GENERATE_VARIANT: PromptTemplate(
        task_type=AiTaskType.GENERATE_VARIANT,
        version="v1",
        system_prompt=VARIANT_SYSTEM_PROMPT,
        output_schema_name="VariantOutput",
        json_mode=True,
        preferred_provider="deepseek",
        max_tokens=8000,
        description="根据知识点和学科生成变式练习题",
    ),
    AiTaskType.GENERATE_KNOWLEDGE_CARD: PromptTemplate(
        task_type=AiTaskType.GENERATE_KNOWLEDGE_CARD,
        version="v1",
        system_prompt=KNOWLEDGE_CARD_SYSTEM_PROMPT,
        output_schema_name="KnowledgeCardOutput",
        json_mode=True,
        preferred_provider="deepseek",
        max_tokens=8000,
        description="生成结构化知识卡片",
    ),
    AiTaskType.KNOWLEDGE_SUMMARY: PromptTemplate(
        task_type=AiTaskType.KNOWLEDGE_SUMMARY,
        version="v1",
        system_prompt=KNOWLEDGE_SUMMARY_SYSTEM_PROMPT,
        output_schema_name=None,
        json_mode=True,
        preferred_provider="deepseek",
        max_tokens=8000,
        description="带引用的知识总结（手动 parse）",
    ),
    AiTaskType.PROMPT_TEST: PromptTemplate(
        task_type=AiTaskType.PROMPT_TEST,
        version="v1",
        system_prompt="",
        output_schema_name=None,
        json_mode=True,
        preferred_provider="deepseek",
        max_tokens=2000,
        description="用户自定义 Prompt 测试",
        dynamic_prompt=True,
    ),
    # staged mistake 域
    AiTaskType.MISTAKE_QUESTION_DRAFT: PromptTemplate(
        task_type=AiTaskType.MISTAKE_QUESTION_DRAFT,
        version="v1",
        system_prompt=QUESTION_DRAFT_SYSTEM_PROMPT,
        output_schema_name="QuestionDraftResponse",
        json_mode=True,
        preferred_provider="deepseek",
        max_tokens=8000,
        description="从图片/文本中提取题目信息，不推断错因",
        vision_system_prompt=QUESTION_DRAFT_VISION_SYSTEM_MESSAGE,
    ),
    AiTaskType.MISTAKE_ERROR_INTERPRETATION: PromptTemplate(
        task_type=AiTaskType.MISTAKE_ERROR_INTERPRETATION,
        version="v1",
        system_prompt=ERROR_INTERPRETATION_SYSTEM_PROMPT,
        output_schema_name="ErrorInterpretationResponse",
        json_mode=True,
        preferred_provider="deepseek",
        max_tokens=8000,
        description="理解学生自述的错因，给出结构化解读",
    ),
    AiTaskType.MISTAKE_FINAL_ANALYSIS: PromptTemplate(
        task_type=AiTaskType.MISTAKE_FINAL_ANALYSIS,
        version="v1",
        system_prompt=FINAL_ANALYSIS_SYSTEM_PROMPT,
        output_schema_name="FinalAnalysisResponse",
        json_mode=True,
        preferred_provider="deepseek",
        max_tokens=8000,
        description="基于已采纳的错因理解生成最终分析",
    ),
    # diagram 域
    AiTaskType.DIAGRAM_STRUCTURED: PromptTemplate(
        task_type=AiTaskType.DIAGRAM_STRUCTURED,
        version="v1",
        system_prompt=DIAGRAM_STRUCTURED_SYSTEM_PROMPT,
        output_schema_name="StructuredDiagramData",
        json_mode=True,
        preferred_provider="deepseek",
        max_tokens=8000,
        description="生成结构化图解数据",
    ),
    AiTaskType.DIAGRAM_FALLBACK: PromptTemplate(
        task_type=AiTaskType.DIAGRAM_FALLBACK,
        version="v1",
        system_prompt=QWEN_IMAGE_FALLBACK_PROMPT,
        output_schema_name=None,
        json_mode=False,
        preferred_provider="deepseek",
        max_tokens=8000,
        description="生成图片生成模型的英文 prompt（纯文本）",
    ),
    # 辅助域
    AiTaskType.NETEASE_REASON: PromptTemplate(
        task_type=AiTaskType.NETEASE_REASON,
        version="v1",
        system_prompt=NETEASE_SYSTEM_MESSAGE,
        output_schema_name=None,
        json_mode=False,
        preferred_provider="deepseek",
        max_tokens=300,
        description="生成音乐推荐理由（纯文本）",
        user_content_template=NETEASE_REASON_PROMPT,
        input_variables=("song_info",),
    ),
    AiTaskType.RECOMMENDATION: PromptTemplate(
        task_type=AiTaskType.RECOMMENDATION,
        version="v1",
        system_prompt=RECOMMENDATION_SYSTEM_PROMPT,
        output_schema_name="RecommendationOutput",
        json_mode=True,
        preferred_provider="qwen_general",
        max_tokens=500,
        description="推荐今天最值得关注的一项内容",
    ),
    AiTaskType.REPAIR_DETERMINISTIC: PromptTemplate(
        task_type=AiTaskType.REPAIR_DETERMINISTIC,
        version="v1",
        system_prompt="",
        output_schema_name=None,
        json_mode=True,
        preferred_provider="deepseek",
        max_tokens=8000,
        description="修复 AI 输出中的模糊词语（动态构建 prompt）",
        dynamic_prompt=True,
    ),
}


# Batch 10.2: static runtime prompts use one auditable structure. Dynamic prompts
# are supplied by their callers and remain versioned independently.
PROMPT_REGISTRY = {
    task_type: template
    if template.dynamic_prompt
    else replace(
        template,
        version="v2",
        system_prompt=standardize_prompt(template.system_prompt),
        vision_system_prompt=(
            standardize_prompt(template.vision_system_prompt)
            if template.vision_system_prompt
            else None
        ),
    )
    for task_type, template in PROMPT_REGISTRY.items()
}


def get_prompt_template(task_type: AiTaskType) -> PromptTemplate:
    """查询 task_type 对应的 PromptTemplate。

    Raises:
        KeyError: 如果 task_type 未注册。
    """
    return PROMPT_REGISTRY[task_type]


def render_user_content(
    task_type: AiTaskType,
    variables: Mapping[str, object],
) -> str:
    """Render a registered user template without exposing variable values in errors."""

    template = get_prompt_template(task_type)
    source = template.user_content_template
    if source is None:
        raise ValueError(f"No user content template registered for {task_type.value}")

    expected = set(template.input_variables)
    provided = set(variables)
    missing = sorted(expected - provided)
    extra = sorted(provided - expected)
    if missing:
        raise ValueError(
            f"Missing variables for {task_type.value}: {', '.join(missing)}"
        )
    if extra:
        raise ValueError(
            f"Unexpected variables for {task_type.value}: {', '.join(extra)}"
        )
    if not expected:
        return source

    rendered = source.format_map(dict(variables))
    residual = {
        field_name
        for _, field_name, _, _ in Formatter().parse(rendered)
        if field_name
    }
    if residual:
        raise ValueError(
            f"Unresolved variables for {task_type.value}: {', '.join(sorted(residual))}"
        )
    return rendered


def build_text_messages(
    task_type: AiTaskType,
    user_content: str,
    *,
    system_prompt_override: str | None = None,
) -> list[dict]:
    """从 registry 获取 system_prompt，构建 text messages。

    Args:
        task_type: 任务类型枚举
        user_content: user 消息内容（已渲染好的文本）
        system_prompt_override: 动态 prompt 任务的 system_prompt override。
            当 PromptTemplate.system_prompt 为空时（如 repair_deterministic /
            prompt_test），调用方必须显式传入。

    Returns:
        [{"role": "system", ...}, {"role": "user", ...}]

    Raises:
        ValueError: system_prompt 为空且未提供 override
    """
    template = get_prompt_template(task_type)
    system_prompt = system_prompt_override or template.system_prompt
    if not system_prompt:
        raise ValueError(
            f"system_prompt is empty for {task_type.value}; "
            "provide system_prompt_override"
        )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]


def build_vision_messages(
    task_type: AiTaskType,
    content_parts: list[dict],
    *,
    system_prompt_override: str | None = None,
) -> list[dict]:
    """从 registry 获取 system_prompt，构建 vision messages。

    Args:
        task_type: 任务类型枚举
        content_parts: user content 的多模态结构，如
            [{"type": "text", "text": "..."},
             {"type": "image_url", "image_url": {...}}]
        system_prompt_override: 动态 prompt 任务的 system_prompt override。

    Returns:
        [{"role": "system", ...}, {"role": "user", "content": content_parts}]

    Raises:
        ValueError: system_prompt 为空且未提供 override
    """
    template = get_prompt_template(task_type)
    system_prompt = (
        system_prompt_override
        or template.vision_system_prompt
        or template.system_prompt
    )
    if not system_prompt:
        raise ValueError(
            f"system_prompt is empty for {task_type.value}; "
            "provide system_prompt_override"
        )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": content_parts},
    ]
