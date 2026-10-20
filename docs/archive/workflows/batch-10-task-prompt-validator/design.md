# Design：Batch 10 Task / Prompt / Validator 管理

> 关联：[requirements.md](./requirements.md) | [tasks.md](./tasks.md)
> 前置：[Batch 9 design](../batch-9-ai-gateway-kernel/design.md)

## 1. 问题分析

### 1.1 现状

Batch 9 完成了 AI Gateway 最小内核，所有 AI 调用已统一经 `ai_gateway.call_*` 入口，调用日志写入 `ai_call_logs`。但 Gateway 之上的任务管理层存在以下问题：

**task_type 字符串散落**：16 个 task_type 字符串硬编码在各 service 和 router 中，无统一定义，容易拼写错误，无法枚举查询。

现有 task_type 全集（从 Grep 结果汇总）：

| task_type | 调用位置 | 调用方式 |
|-----------|---------|---------|
| `capture_draft` | capture_ai_draft.py | call_text |
| `capture_recognition` | capture_recognition.py | call_vision |
| `analyze_mistake` | ai.py (router) | call_vision |
| `analyze_text` | ai.py (router) | call_text |
| `generate_variant` | ai.py (router) | call_text |
| `generate_knowledge_card` | ai.py (router) | call_text |
| `knowledge_summary` | ai.py (router) | call_text |
| `prompt_test` | ai.py (router) | call_text/call_vision |
| `mistake_question_draft` | mistake_staged_service.py | call_vision/call_text |
| `mistake_error_interpretation` | mistake_staged_service.py | call_text |
| `mistake_final_analysis` | mistake_staged_service.py | call_text |
| `diagram_structured` | diagram_service.py | call_text |
| `diagram_fallback` | diagram_service.py | call_text (json_mode=False) |
| `netease_reason` | netease_service.py | call_text (json_mode=False) |
| `repair_deterministic` | ai_analyze_service.py | call_text |
| `recommendation` | recommendation.py | call_general |

**Prompt 常量散落**：Prompt 文本分散在 7 个 service 文件中，无版本号，无法集中查询当前使用的 Prompt 版本。

| Prompt 常量 | 所在文件 |
|-------------|---------|
| OCR_SYSTEM_PROMPT | ai_analyze_service.py |
| TEXT_SYSTEM_PROMPT | ai_analyze_service.py |
| VARIANT_SYSTEM_PROMPT | ai_analyze_service.py |
| KNOWLEDGE_CARD_SYSTEM_PROMPT | ai_analyze_service.py |
| KNOWLEDGE_SUMMARY_SYSTEM_PROMPT | ai_analyze_service.py |
| DRAFT_SYSTEM_PROMPT | capture_ai_draft.py |
| RECOGNITION_SYSTEM_PROMPT | capture_recognition.py |
| SYSTEM_PROMPT | recommendation.py |
| RECOMMENDATION_REASON_PROMPT | netease_service.py |
| QUESTION_DRAFT_SYSTEM_PROMPT | mistake_staged_service.py |
| ERROR_INTERPRETATION_SYSTEM_PROMPT | mistake_staged_service.py |
| FINAL_ANALYSIS_SYSTEM_PROMPT | mistake_staged_service.py |
| DIAGRAM_STRUCTURED_SYSTEM_PROMPT | diagram_service.py |
| QWEN_IMAGE_FALLBACK_PROMPT | diagram_service.py |

**输出验证不统一**：部分任务有 Pydantic schema 校验，部分任务只有手动解析，缺少统一校验入口。

| 任务 | 现有验证方式 | Pydantic schema |
|------|-------------|-----------------|
| capture_draft | 手动 `_validate_suggestion` + Pydantic | MistakeDraftSuggestionV1 |
| capture_recognition | 手动 `result.get("text")` | 无 |
| analyze_mistake/text | `parse_result` 手动解析 | AnalyzeResponse（最终输出） |
| mistake_question_draft | `_normalize_question_draft` 手动 | QuestionDraftResponse（最终输出） |
| mistake_error_interpretation | 手动 `result.get(...)` | ErrorInterpretationResponse（最终输出） |
| mistake_final_analysis | 手动 `result.get(...)` | FinalAnalysisResponse（最终输出） |
| diagram_structured | 手动逐字段解析 | StructuredDiagramData（已有但未用于校验） |
| diagram_fallback | 纯文本 | 无（不需要） |
| generate_variant | 手动 | 无 |
| generate_knowledge_card | 手动 | 无 |
| knowledge_summary | `parse_summary_blocks` | CitationBlock |
| netease_reason | 纯文本 | 无（不需要） |
| recommendation | 手动 | 无 |
| repair_deterministic | 手动 | 无 |
| prompt_test | 用户自定义 | 无（不需要） |

**失败处理不统一**：capture 模块已有 `DraftResult` / `RecognitionResult` 标准化雏形（带 error_code），但 mistake_staged / diagram / analyze 模块直接 `raise RuntimeError`，无 error_code。

### 1.2 目标

在 Gateway 之上建立结构化任务管理层，不改变 Gateway 本身，不改变现有端点合同。

## 2. 架构设计

### 2.1 新增模块

```
backend/app/services/
  ai_task_types.py        # AiTaskType 枚举
  ai_prompt_registry.py   # PromptTemplate + PROMPT_REGISTRY
  ai_validator.py         # 统一输出校验入口
  ai_task_result.py       # AiTaskResult + AiErrorCode 标准化结果
```

### 2.2 AiTaskType 枚举

使用 `str, Enum` 双继承，保持与 `ai_call_logs.task_type` (String(50)) 的字符串兼容。

```python
# ai_task_types.py
from enum import Enum

class AiTaskType(str, Enum):
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
```

### 2.3 PromptTemplate 与注册表

```python
# ai_prompt_registry.py
from dataclasses import dataclass

@dataclass(frozen=True)
class PromptTemplate:
    task_type: AiTaskType
    version: str               # "v1", "v2", ...
    system_prompt: str         # Prompt 文本（引用现有常量）
    output_schema_name: str | None  # 对应的 Pydantic schema 类名
    json_mode: bool            # 是否要求 JSON 输出
    preferred_provider: str | None  # "deepseek" / "dashscope_vision" / "qwen_general"
    max_tokens: int            # 默认 max_tokens
    description: str           # 人类可读描述

PROMPT_REGISTRY: dict[AiTaskType, PromptTemplate] = { ... }
```

Prompt 文本策略：**引用现有常量，不移动文本**。registry 从各 service 导入 Prompt 常量并注册。这样最小化改动，版本管理集中在 registry。

版本号策略：当前所有 Prompt 标记为 `"v1"`。未来修改某个 Prompt 时，可在 registry 中新增 v2 条目并切换引用。

### 2.4 输出 Schema 补充

新建 `backend/app/schemas/ai_output.py`，为缺少 schema 的任务补充：

```python
# ai_output.py

class RecognitionOutput(BaseModel):
    """capture_recognition 输出"""
    text: str

class VariantOutput(BaseModel):
    """generate_variant 输出"""
    question: str
    correct_answer: str
    analysis: str
    difficulty: str = "medium"
    knowledge_points: str = ""

class KnowledgeCardOutput(BaseModel):
    """generate_knowledge_card 输出"""
    title: str
    content: str
    knowledge_points: str = ""
    subject: str = ""

class RecommendationOutput(BaseModel):
    """recommendation 输出"""
    title: str = ""
    reason: str = ""
    slug: str = ""
```

已有 schema 复用（不新建）：
- `MistakeDraftSuggestionV1` — capture_draft
- `QuestionDraftResponse` — mistake_question_draft
- `ErrorInterpretationResponse` — mistake_error_interpretation
- `FinalAnalysisResponse` — mistake_final_analysis
- `StructuredDiagramData` — diagram_structured
- `AnalyzeResponse` — analyze_mistake/analyze_text（最终输出，AI 原始输出需手动 parse）
- `CitationBlock` — knowledge_summary

无 schema（纯文本输出，不需要）：
- diagram_fallback
- netease_reason
- prompt_test

### 2.5 统一 Validator

```python
# ai_validator.py
from pydantic import BaseModel, ValidationError

@dataclass
class AiValidationResult:
    success: bool
    data: dict | str | None
    error_code: str | None = None
    error_message_safe: str | None = None

# task_type → Pydantic schema 映射
SCHEMA_MAP: dict[AiTaskType, type[BaseModel] | None] = { ... }

def validate_ai_output(task_type: AiTaskType, raw: dict | str) -> AiValidationResult:
    """统一输出校验入口。

    - 有 schema 的任务：Pydantic 校验，失败返回 schema_error。
    - 无 schema 的任务（纯文本）：直接返回原始数据。
    - AnalyzeResponse 等需要手动 parse 的任务：不在本层校验，由各 service 的 parse 函数处理。
    """
    schema = SCHEMA_MAP.get(task_type)
    if schema is None:
        return AiValidationResult(success=True, data=raw)
    try:
        validated = schema.model_validate(raw)
        return AiValidationResult(success=True, data=validated.model_dump())
    except ValidationError as e:
        return AiValidationResult(
            success=False, data=None,
            error_code="schema_error",
            error_message_safe="AI output failed schema validation",
        )
```

### 2.6 AiTaskResult 标准化结果

```python
# ai_task_result.py
from dataclasses import dataclass
from app.services.ai_gateway import GatewayCallResult

class AiErrorCode(str, Enum):
    EMPTY_INPUT = "empty_input"
    NO_PROVIDER = "no_provider"
    TIMEOUT = "timeout"
    PROVIDER_ERROR = "provider_error"
    SCHEMA_ERROR = "schema_error"
    PARSE_ERROR = "parse_error"
    EMPTY_RESULT = "empty_result"

@dataclass
class AiTaskResult:
    task_type: AiTaskType
    success: bool
    data: dict | str | None
    error_code: str | None = None
    error_message_safe: str | None = None
    prompt_version: str | None = None
    gateway_result: GatewayCallResult | None = None
```

### 2.7 失败处理标准化

**原则**：AI 失败不抛异常给调用方，返回 `AiTaskResult(success=False)`，调用方根据 error_code 决定进入草稿还是错误状态。

| error_code | 含义 | 处理方式 |
|-----------|------|---------|
| empty_input | 输入为空 | 草稿区保留，提示用户补充输入 |
| no_provider | 无 AI 供应商配置 | 错误状态，提示配置 |
| timeout | 调用超时 | 错误状态，可重试 |
| provider_error | 供应商返回错误 | 错误状态，可重试 |
| schema_error | AI 输出不符合 schema | 草稿区保留原始输出，提示人工校验 |
| parse_error | 输出解析失败 | 错误状态，记录日志 |
| empty_result | 返回空内容 | 草稿区保留，提示重试 |

**不直接写正式业务实体**：所有 AI 结果（无论成功或失败）只进入：
- `capture_items` 草稿区（capture 域）
- 分阶段错题草稿（mistake 域）
- AI 调用日志（ai_call_logs）
- HTTP 响应（即时调用）

不直接写入 `notes` 表或 `mistake_drafts` 表。

## 3. 集成策略

### 3.1 渐进式迁移

不一次性重写所有 service，而是：

1. 先建新模块（ai_task_types, ai_prompt_registry, ai_validator, ai_task_result）
2. capture 模块迁移（已有标准化雏形，改动最小）
3. mistake_staged 模块迁移（从 raise 改为 AiTaskResult）
4. diagram 模块迁移
5. analyze/router 模块迁移（最复杂，最后做）
6. 辅助模块（recommendation, netease）迁移

### 3.2 不改变的内容

- `ai_gateway.py` 的四个方法签名不变
- 现有 AI 端点的请求/响应 schema 不变
- `ai_call_logs` 表结构不变
- 现有 Prompt 文本内容不变（只是多了 registry 引用）

## 4. 文件清单

### 新建

| 文件 | 职责 |
|------|------|
| `backend/app/services/ai_task_types.py` | AiTaskType 枚举 |
| `backend/app/services/ai_prompt_registry.py` | PromptTemplate + PROMPT_REGISTRY |
| `backend/app/services/ai_validator.py` | validate_ai_output 统一校验 |
| `backend/app/services/ai_task_result.py` | AiTaskResult + AiErrorCode |
| `backend/app/schemas/ai_output.py` | 补充输出 schema |
| `backend/tests/test_ai_task_types.py` | 枚举完整性测试 |
| `backend/tests/test_ai_prompt_registry.py` | 注册表完整性测试 |
| `backend/tests/test_ai_validator.py` | 校验器测试 |

### 修改

| 文件 | 改动 |
|------|------|
| `capture_ai_draft.py` | task_type 改用枚举，返回 AiTaskResult |
| `capture_recognition.py` | task_type 改用枚举，返回 AiTaskResult |
| `mistake_staged_service.py` | task_type 改用枚举，返回 AiTaskResult |
| `diagram_service.py` | task_type 改用枚举，返回 AiTaskResult |
| `ai_analyze_service.py` | task_type 改用枚举，PROMPT_TEMPLATES 改为引用 registry |
| `recommendation.py` | task_type 改用枚举 |
| `netease_service.py` | task_type 改用枚举 |
| `ai.py` (router) | task_type 改用枚举 |
| `ai_call_log.py` (schema) | task_type 注释标注使用 AiTaskType |

## 5. 数据流

```
调用方 (router/service)
  ↓
ai_prompt_registry.get_template(task_type)  →  PromptTemplate
  ↓
构建 messages = [{system: template.system_prompt}, {user: ...}]
  ↓
ai_gateway.call_text/vision(task_type.value, messages, ...)
  ↓
GatewayCallResult
  ↓
ai_validator.validate_ai_output(task_type, gw.data)  →  AiValidationResult
  ↓
AiTaskResult(success, data, error_code, prompt_version, gateway_result)
  ↓
调用方根据 error_code 决定进入草稿还是错误状态
```
