"""AI provider/model routing typed policy — Batch 12A.

This module is intentionally code-level policy only:

- no database tables
- no migrations
- no API keys or secrets
- no runtime provider calls

Prompt Registry remains responsible for prompt/schema/json_mode contracts.
RoutingPolicy only expresses provider/model/fallback preferences by task_type.
"""

from dataclasses import dataclass

from app.services.ai_task_types import AiTaskType


@dataclass(frozen=True)
class ProviderPolicy:
    provider_key: str
    display_name: str
    capabilities: frozenset[str]
    default_model: str
    enabled_by_env_key: str
    timeout_seconds: int = 120


@dataclass(frozen=True)
class ModelPolicy:
    provider_key: str
    model_name: str
    display_name: str
    capabilities: frozenset[str]
    max_output_tokens: int | None = None
    input_token_price: None = None
    output_token_price: None = None
    currency: None = None


@dataclass(frozen=True)
class RoutingPolicy:
    task_type: str
    primary_provider: str
    primary_model: str | None
    fallback_chain: tuple[str, ...]
    require_json: bool
    require_vision: bool = False


PROVIDER_POLICIES: dict[str, ProviderPolicy] = {
    "deepseek": ProviderPolicy(
        provider_key="deepseek",
        display_name="DeepSeek",
        capabilities=frozenset({"text", "json"}),
        default_model="deepseek-v4-pro",
        enabled_by_env_key="DEEPSEEK_API_KEY",
    ),
    "dashscope_vision": ProviderPolicy(
        provider_key="dashscope_vision",
        display_name="DashScope Vision",
        capabilities=frozenset({"vision", "json"}),
        default_model="qwen3.7-plus",
        enabled_by_env_key="DASHSCOPE_API_KEY",
    ),
    "qwen_general": ProviderPolicy(
        provider_key="qwen_general",
        display_name="Qwen General",
        capabilities=frozenset({"text", "vision", "json"}),
        default_model="qwen3.7-plus",
        enabled_by_env_key="DASHSCOPE_API_KEY_OR_AI_API_KEY",
    ),
}


MODEL_POLICIES: dict[tuple[str, str], ModelPolicy] = {
    ("deepseek", "deepseek-v4-pro"): ModelPolicy(
        provider_key="deepseek",
        model_name="deepseek-v4-pro",
        display_name="DeepSeek V4 Pro",
        capabilities=frozenset({"text", "json"}),
        max_output_tokens=8000,
    ),
    ("dashscope_vision", "qwen3.7-plus"): ModelPolicy(
        provider_key="dashscope_vision",
        model_name="qwen3.7-plus",
        display_name="Qwen 3.7 Plus Vision",
        capabilities=frozenset({"vision", "json"}),
        max_output_tokens=8000,
    ),
    ("qwen_general", "qwen3.7-plus"): ModelPolicy(
        provider_key="qwen_general",
        model_name="qwen3.7-plus",
        display_name="Qwen 3.7 Plus",
        capabilities=frozenset({"text", "vision", "json"}),
        max_output_tokens=8000,
    ),
}


def _text_policy(task_type: AiTaskType, *, require_json: bool = True) -> RoutingPolicy:
    return RoutingPolicy(
        task_type=task_type.value,
        primary_provider="deepseek",
        primary_model="deepseek-v4-pro",
        fallback_chain=("deepseek", "qwen_general"),
        require_json=require_json,
    )


def _vision_policy(task_type: AiTaskType) -> RoutingPolicy:
    return RoutingPolicy(
        task_type=task_type.value,
        primary_provider="dashscope_vision",
        primary_model="qwen3.7-plus",
        fallback_chain=("dashscope_vision", "qwen_general"),
        require_json=True,
        require_vision=True,
    )


def _general_policy(task_type: AiTaskType, *, require_json: bool = True) -> RoutingPolicy:
    return RoutingPolicy(
        task_type=task_type.value,
        primary_provider="qwen_general",
        primary_model="qwen3.7-plus",
        fallback_chain=("qwen_general", "deepseek"),
        require_json=require_json,
    )


ROUTING_POLICIES: dict[str, RoutingPolicy] = {
    AiTaskType.CAPTURE_DRAFT.value: _text_policy(AiTaskType.CAPTURE_DRAFT),
    AiTaskType.CAPTURE_RECOGNITION.value: _vision_policy(AiTaskType.CAPTURE_RECOGNITION),
    AiTaskType.ANALYZE_MISTAKE.value: _vision_policy(AiTaskType.ANALYZE_MISTAKE),
    AiTaskType.ANALYZE_TEXT.value: _text_policy(AiTaskType.ANALYZE_TEXT),
    AiTaskType.GENERATE_VARIANT.value: _text_policy(AiTaskType.GENERATE_VARIANT),
    AiTaskType.GENERATE_KNOWLEDGE_CARD.value: _text_policy(
        AiTaskType.GENERATE_KNOWLEDGE_CARD
    ),
    AiTaskType.KNOWLEDGE_SUMMARY.value: _text_policy(AiTaskType.KNOWLEDGE_SUMMARY),
    AiTaskType.PROMPT_TEST.value: _text_policy(AiTaskType.PROMPT_TEST),
    AiTaskType.MISTAKE_QUESTION_DRAFT.value: _text_policy(
        AiTaskType.MISTAKE_QUESTION_DRAFT
    ),
    AiTaskType.MISTAKE_ERROR_INTERPRETATION.value: _text_policy(
        AiTaskType.MISTAKE_ERROR_INTERPRETATION
    ),
    AiTaskType.MISTAKE_FINAL_ANALYSIS.value: _text_policy(
        AiTaskType.MISTAKE_FINAL_ANALYSIS
    ),
    AiTaskType.DIAGRAM_STRUCTURED.value: _text_policy(AiTaskType.DIAGRAM_STRUCTURED),
    AiTaskType.DIAGRAM_FALLBACK.value: _text_policy(
        AiTaskType.DIAGRAM_FALLBACK, require_json=False
    ),
    AiTaskType.NETEASE_REASON.value: _text_policy(
        AiTaskType.NETEASE_REASON, require_json=False
    ),
    AiTaskType.RECOMMENDATION.value: _general_policy(AiTaskType.RECOMMENDATION),
    AiTaskType.REPAIR_DETERMINISTIC.value: _text_policy(
        AiTaskType.REPAIR_DETERMINISTIC
    ),
}


def resolve_routing_policy(task_type: str | AiTaskType) -> RoutingPolicy:
    task_type_str = task_type.value if isinstance(task_type, AiTaskType) else task_type
    policy = ROUTING_POLICIES.get(task_type_str)
    if policy is not None:
        return policy
    return RoutingPolicy(
        task_type=task_type_str,
        primary_provider="deepseek",
        primary_model="deepseek-v4-pro",
        fallback_chain=("deepseek", "qwen_general"),
        require_json=True,
    )
