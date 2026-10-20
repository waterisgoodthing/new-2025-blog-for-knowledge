# Design：Batch 10.1 Prompt Registry Runtime Integration

> 关联：[README.md](./README.md) | [requirements.md](./requirements.md) | [tasks.md](./tasks.md)

## 1. 架构概览

```
┌─────────────────────────────────────────────────────────┐
│  ai_prompt_registry.py                                  │
│  ┌───────────────────────────────────────────────────┐  │
│  │  PROMPT_REGISTRY (16 PromptTemplate)              │  │
│  │  get_prompt_template(task_type) -> PromptTemplate │  │
│  │  build_text_messages(task_type, user_content) ◄── 新增  │
│  │  build_vision_messages(task_type, parts)    ◄── 新增  │
│  └───────────────────────────────────────────────────┘  │
└───────────┬─────────────────────────────────────────────┘
            │ import (单向，无循环)
┌───────────▼──────────┐    ┌──────────────────────────────┐
│  ai_gateway.py       │    │  各 service                   │
│  call_text()         │◄──│  capture_ai_draft.py          │
│  call_vision()       │   │  capture_recognition.py       │
│  call_general()      │   │  mistake_staged_service.py    │
│  (参数 None 时       │   │  diagram_service.py           │
│   从 registry 读取)  │   │  ai_analyze_service.py        │
│                      │   │  ai.py router                 │
│  _write_call_log()   │   │  netease_service.py           │
│  (记录 prompt_version)│  │  recommendation.py            │
└──────────────────────┘   └──────────────────────────────┘
```

核心变更：service 不再直接 import `ai_prompts.py` 常量，改为通过 `build_text_messages()` / `build_vision_messages()` 构建 messages；gateway 参数为 None 时从 registry 读取默认值。

## 2. 核心组件设计

### 2.1 Message Builder（新增到 ai_prompt_registry.py）

```python
def build_text_messages(
    task_type: AiTaskType,
    user_content: str,
    *,
    system_prompt_override: str | None = None,
) -> list[dict]:
    """从 registry 获取 system_prompt，构建 text messages。

    - system_prompt_override: 动态 prompt 任务（repair_deterministic / prompt_test）
      的 system_prompt 为空时，调用方显式传入。
    - user_content_template 不在此处理（由调用方自行渲染模板后传入 user_content）。
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

    content_parts 是 user content 的多模态结构，如：
    [{"type": "text", "text": "..."}, {"type": "image_url", "image_url": {...}}]
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
        {"role": "user", "content": content_parts},
    ]
```

**设计决策**：
- `user_content_template` 渲染由调用方处理，而非 builder。原因：各任务的模板参数不同（NETEASE 用 `{song_info}`，其他无模板），builder 不应感知业务参数。
- `system_prompt_override` 处理动态 prompt 任务（repair_deterministic / prompt_test），它们的 `system_prompt` 为空字符串。

### 2.2 Gateway 参数从 Registry 读取

修改 `ai_gateway.py` 的 `call_text` / `call_vision` / `call_general` / `call_stream`：

```python
from app.services.ai_prompt_registry import get_prompt_template
from app.services.ai_task_types import AiTaskType

async def call_text(
    task_type: str | AiTaskType,
    messages: list[dict],
    *,
    max_tokens: int | None = None,
    preferred: str | None = None,
    json_mode: bool | None = None,
    input_summary: str | None = None,
) -> GatewayCallResult:
    """文本模型调用。参数为 None 时从 registry 读取默认值。"""
    # 标准化 task_type
    task_type_str = task_type.value if isinstance(task_type, AiTaskType) else task_type

    # 从 registry 读取默认值
    prompt_version = None
    try:
        tt = AiTaskType(task_type_str) if isinstance(task_type, str) else task_type
        template = get_prompt_template(tt)
        if max_tokens is None:
            max_tokens = template.max_tokens
        if preferred is None:
            preferred = template.preferred_provider
        if json_mode is None:
            json_mode = template.json_mode
        prompt_version = template.version
    except (ValueError, KeyError):
        pass  # 未知 task_type，使用最终 fallback

    # 最终 fallback
    if max_tokens is None:
        max_tokens = 8000
    if preferred is None:
        preferred = "deepseek"
    if json_mode is None:
        json_mode = True

    # ... 调用底层 _call_with_fallback
    # ... 写日志时传入 prompt_version
    await _write_call_log(task_type_str, gw_result, input_summary, prompt_version)
    return gw_result
```

**关键点**：
- `task_type` 接受 `str | AiTaskType`，向后兼容。
- 参数为 `None` 时从 registry 读取；显式传参优先（FR-2.4）。
- `prompt_version` 从 registry 获取，传给 `_write_call_log()`。
- 未知 task_type（如 stream 的 `"analyze_mistake_stream"`）不报错，使用 fallback。

### 2.3 prompt_version 记录到调用日志

**模型变更**：

```python
# backend/app/models/ai_call_log.py
class AiCallLog(Base):
    __tablename__ = "ai_call_logs"
    # ... 现有字段
    prompt_version = Column(String(20), nullable=True)  # 新增
```

**_write_call_log 变更**：

```python
async def _write_call_log(
    task_type: str,
    result: GatewayCallResult,
    input_summary: str | None,
    prompt_version: str | None = None,  # 新增
) -> None:
    # ...
    log = AiCallLog(
        # ... 现有字段
        prompt_version=prompt_version,
    )
```

**Alembic migration**：

```python
def upgrade():
    op.add_column("ai_call_logs", sa.Column("prompt_version", sa.String(20), nullable=True))

def downgrade():
    op.drop_column("ai_call_logs", "prompt_version")
```

### 2.4 收敛内联字符串

**问题**：`ai.py` router 的 analyze 端点使用内联字符串 `"你是一个严谨的错题图片识别与解题助手。请始终以 JSON 格式回复。"` 作为 system message，OCR_SYSTEM_PROMPT 放在 user content 中。

**当前 registry 配置错误**：`ANALYZE_MISTAKE` 的 `system_prompt` 设为 `OCR_SYSTEM_PROMPT`（140 行详细指令），但实际调用时 system message 是简短字符串，OCR_SYSTEM_PROMPT 在 user content 中。

**修正方案**：

1. 在 `ai_prompts.py` 新增常量（不修改现有常量）：
```python
ANALYZE_VISION_SYSTEM_MESSAGE = "你是一个严谨的错题图片识别与解题助手。请始终以 JSON 格式回复。"
```

2. 修正 registry 中 `ANALYZE_MISTAKE` 的配置：
```python
AiTaskType.ANALYZE_MISTAKE: PromptTemplate(
    # ...
    system_prompt=ANALYZE_VISION_SYSTEM_MESSAGE,  # 改为简短消息
    user_content_template=OCR_SYSTEM_PROMPT,      # 详细指令在 user content
    # ...
),
```

3. `ai.py` analyze 端点改用 `build_vision_messages()`：
```python
content = [{"type": "text", "text": OCR_SYSTEM_PROMPT}]
# ... 添加图片
messages = build_vision_messages(AiTaskType.ANALYZE_MISTAKE, content)
```

**注意**：这改变了 registry 中 `ANALYZE_MISTAKE.system_prompt` 的值（从 OCR_SYSTEM_PROMPT 改为简短消息），但不改变实际调用时的 messages 结构（system 仍是简短消息，user content 仍是 OCR_SYSTEM_PROMPT）。

### 2.5 build_prompts_response 从 Registry 动态生成

**当前**：`build_prompts_response()` 手动引用各常量构建响应。

**改为**：从 `PROMPT_REGISTRY` 动态生成：

```python
def build_prompts_response() -> dict:
    """从 PROMPT_REGISTRY 动态生成 /api/ai/prompts 响应。"""
    prompts = {}
    for task_type, template in PROMPT_REGISTRY.items():
        key = task_type.value
        sp = template.system_prompt or template.user_content_template or ""
        prompts[key] = {
            "prompt": sp[:500] + "..." if len(sp) > 500 else sp,
            "full_prompt": sp,
            "version": template.version,
            "json_mode": template.json_mode,
            "preferred_provider": template.preferred_provider,
            "max_tokens": template.max_tokens,
            "description": template.description,
        }
    return {"prompts": prompts}
```

**注意**：响应结构可能新增字段（version / json_mode / preferred_provider / max_tokens / description），但不删除现有字段（prompt / full_prompt），保持向前兼容。

## 3. 调用模式对比

### 3.1 迁移前（当前）

```python
# capture_ai_draft.py
from app.services.ai_prompts import DRAFT_SYSTEM_PROMPT

messages = [
    {"role": "system", "content": DRAFT_SYSTEM_PROMPT},
    {"role": "user", "content": user_content},
]
gw = await call_text(AiTaskType.CAPTURE_DRAFT.value, messages, input_summary=...)
```

### 3.2 迁移后（目标）

```python
# capture_ai_draft.py
from app.services.ai_prompt_registry import build_text_messages
from app.services.ai_task_types import AiTaskType

messages = build_text_messages(AiTaskType.CAPTURE_DRAFT, user_content)
gw = await call_text(AiTaskType.CAPTURE_DRAFT, messages, input_summary=...)
# max_tokens / preferred / json_mode 从 registry 读取，无需显式传
```

## 4. 各 Service 迁移策略

| Service | 当前模式 | 迁移后模式 | 特殊处理 |
|---------|----------|------------|----------|
| capture_ai_draft | text: DRAFT_SYSTEM_PROMPT | `build_text_messages(CAPTURE_DRAFT, ...)` | 无 |
| capture_recognition | vision: RECOGNITION_SYSTEM_MESSAGE + RECOGNITION_SYSTEM_PROMPT in user content | `build_vision_messages(CAPTURE_RECOGNITION, content)` | user_content_template 已在 registry |
| mistake_staged | vision+text: QUESTION_DRAFT_SYSTEM_PROMPT / QUESTION_DRAFT_VISION_SYSTEM_MESSAGE | `build_vision_messages` / `build_text_messages` | vision 路径用 QUESTION_DRAFT_VISION_SYSTEM_MESSAGE as system_prompt_override |
| diagram | text: DIAGRAM_STRUCTURED_SYSTEM_PROMPT / QWEN_IMAGE_FALLBACK_PROMPT | `build_text_messages` | fallback 是纯文本，json_mode=False |
| ai_analyze_service | text: 多个 prompt + build_prompts_response | `build_text_messages` + 动态 build_prompts_response | repair_deterministic 用 system_prompt_override |
| ai.py router | vision+text: OCR_SYSTEM_PROMPT + 内联字符串 | `build_vision_messages` / `build_text_messages` | 收敛内联字符串 |
| netease_service | text: NETEASE_SYSTEM_MESSAGE + NETEASE_REASON_PROMPT | `build_text_messages` | user_content_template 渲染由调用方处理 |
| recommendation | text: RECOMMENDATION_SYSTEM_PROMPT | `build_text_messages` | 无 |

## 5. 风险与缓解

| 风险 | 缓解 |
|------|------|
| gateway signature 变更导致测试失败 | 参数改为 keyword-only 且默认 None，向后兼容 |
| registry 中 ANALYZE_MISTAKE 配置修正改变行为 | 实际调用时 messages 结构不变，只是 registry 元数据修正 |
| build_prompts_response 新增字段破坏前端 | 只新增字段不删除，前端忽略未知字段 |
| 动态 prompt 任务 system_prompt 为空 | `system_prompt_override` 参数处理 |
| 未知 task_type（stream 端点）在 gateway 中查找 registry 失败 | try/except 降级为 fallback 默认值 |

## 6. 验证策略

- `get_prompt_template()` 在生产代码中至少 8 处调用（Grep 验证）
- `ai_prompts.py` 直接 import 只出现在 `ai_prompt_registry.py`（Grep 验证）
- `ai.py` router 中无内联 system message 字符串（Grep 验证）
- 现有测试全部通过（允许因 signature 变更适配测试）
- `npx tsc --noEmit` 通过
- `/api/ai/prompts` 端点响应包含原有字段
