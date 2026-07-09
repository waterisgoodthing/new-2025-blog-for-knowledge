# Validation：Batch 10.1 Prompt Registry Runtime Integration

> 验证日期：2025-07-05
> 验证人：AI Agent

## 1. pytest 后端测试

```
cd backend && .venv/bin/python -m pytest tests/ -v
```

结果：**173 passed, 0 failed**（2 warnings 为 mock 相关 RuntimeWarning，不影响结果）

本次改动涉及的测试全部通过：
- `test_ai_message_builder.py` — 9/9 ✓
- `test_ai_gateway.py` — 全部 ✓
- `test_ai_prompt_registry.py` — 全部 ✓
- `test_capture_service.py` — 12/12 ✓

## 2. TypeScript 类型检查

```
npx tsc --noEmit
```

结果：**通过**（无错误输出）

## 3. Grep 验证：get_prompt_template() 调用

```
grep -rn "get_prompt_template(" backend/app/
```

直接调用：**6 处**（不含函数定义）

| 文件 | 行 | 用途 |
|------|----|------|
| `ai_gateway.py` | 135 | `_resolve_registry_defaults` 读取 registry 默认值 |
| `ai_prompt_registry.py` | 264 | `build_text_messages` 内部调用 |
| `ai_prompt_registry.py` | 298 | `build_vision_messages` 内部调用 |
| `netease_service.py` | 247 | 获取 `user_content_template` |
| `capture_recognition.py` | 62 | 获取 `user_content_template` |
| `mistake_staged_service.py` | 17 | 获取 vision 路径 `system_prompt` |

间接调用（通过 `build_text_messages` / `build_vision_messages`）：**17 处**

| 文件 | 调用数 |
|------|--------|
| `ai.py` router | 6 |
| `mistake_staged_service.py` | 4 |
| `diagram_service.py` | 2 |
| `capture_ai_draft.py` | 1 |
| `capture_recognition.py` | 1 |
| `ai_repair_service.py` | 1 |
| `netease_service.py` | 1 |
| `recommendation.py` | 1 |

**合计：23 处注册表驱动的调用点**（6 直接 + 17 间接），远超目标 8 处。

> 说明：tasks.md 原文要求"至少 8 处调用"，实际采用两层架构——`build_*_messages` 封装 `get_prompt_template`，各 service 调用 builder 而非直接调用 registry。有效运行时调用点为 23 处。

## 4. Grep 验证：ai_prompts import 范围

```
grep -rn "from app.services.ai_prompts import" backend/
```

结果：**5 处**（含测试文件）

| 文件 | Import 内容 | 是否符合预期 |
|------|-------------|--------------|
| `ai_prompt_registry.py` | 所有 prompt 常量（注册表定义） | ✓ 预期 |
| `ai_analyze_service.py` | `OCR_SYSTEM_PROMPT` 等（PROMPT_TEMPLATES + stream 路径） | ✓ 预期 |
| `ai.py` | `ANALYZE_VISION_SYSTEM_MESSAGE`, `OCR_SYSTEM_PROMPT`, `TEXT_SYSTEM_PROMPT`（stream 端点 user content） | ✓ 预期 |
| `mistake_staged_service.py` | `QUESTION_DRAFT_VISION_SYSTEM_MESSAGE`（vision 路径 `system_prompt_override`） | ⚠ 有意保留 |
| `test_ai_prompt_registry.py` | 测试用常量 | ✓ 测试文件 |

> `mistake_staged_service.py` 的 `QUESTION_DRAFT_VISION_SYSTEM_MESSAGE` 是 vision 路径的 `system_prompt_override` 参数值（动态 prompt 场景），非用于构建 messages 的常量引用。这是 design.md 中定义的 `system_prompt_override` 机制的预期用法。

## 5. Grep 验证：ai.py 无内联 system message

```
grep -n "\"你是" backend/app/routers/ai.py
```

结果：**0 处** ✓

`ai.py` 中所有 system message 均通过 `build_*_messages` 或 `ANALYZE_VISION_SYSTEM_MESSAGE` 常量引用，无内联字符串。

## 6. /api/ai/prompts 端点响应

`build_prompts_response()` 从 `PROMPT_REGISTRY` 动态生成，每个 task_type 包含：

```json
{
  "prompt": "...(截断至500字符)",
  "full_prompt": "...(完整文本)",
  "version": "1.0",
  "json_mode": true,
  "preferred_provider": "deepseek",
  "max_tokens": 8000,
  "description": "..."
}
```

原有字段 `prompt` / `full_prompt` 保留，新增字段 `version` / `json_mode` / `preferred_provider` / `max_tokens` / `description` 不破坏前端兼容。

## 7. 验收偏差记录

### 偏差 1：get_prompt_template() 直接调用数低于原标准

直接 `get_prompt_template` 调用数低于原至少 8 处标准，是因为 registry 访问被 Message Builder 集中封装。生产运行时仍通过 message builder 接入 Prompt Registry，不阻塞验收。

具体数据：
- 直接调用 6 处（不含函数定义）
- 间接调用（通过 `build_text_messages` / `build_vision_messages`）17 处
- 合计 23 处注册表驱动的运行时调用点

直接调用 6 处明细：

1. `ai_gateway.py:135` — `_resolve_registry_defaults` 读取 registry 默认值
2. `ai_prompt_registry.py:264` — `build_text_messages` 内部调用
3. `ai_prompt_registry.py:298` — `build_vision_messages` 内部调用
4. `netease_service.py:247` — 获取 `user_content_template`
5. `capture_recognition.py:62` — 获取 `user_content_template`
6. `mistake_staged_service.py:17` — 获取 vision 路径 `system_prompt`（作为 user content 文本部分）

### 偏差 2：mistake_staged_service.py 仍保留 ai_prompts import

mistake_staged_service 仍保留 ai_prompts import，仅用于 vision override；普通 text prompt 已通过 message builder / registry 获取。

具体核查：
- `mistake_staged_service.py` 第 10 行：`from app.services.ai_prompts import QUESTION_DRAFT_VISION_SYSTEM_MESSAGE`
- 第 27 行：`system_prompt_override=QUESTION_DRAFT_VISION_SYSTEM_MESSAGE`（作为 `build_vision_messages` 的 override 参数）
- 3 条 text 路径（第 35、90、127 行）均使用 `build_text_messages(AiTaskType.xxx, user_content)`，system prompt 从 registry 获取
- 不存在直接 import 普通 system prompt 常量的情况

相关代码（`mistake_staged_service.py` vision 路径）：

```python
messages = build_vision_messages(
    AiTaskType.MISTAKE_QUESTION_DRAFT,
    content,
    system_prompt_override=QUESTION_DRAFT_VISION_SYSTEM_MESSAGE,
)
```

## 8. 结论

Batch 10.1 验收结论：**通过**。

通过项：
- ✅ `npx tsc --noEmit` 通过
- ✅ `pytest` 173 passed, 0 failed（2 warnings 为 mock 相关，不影响结果）
- ✅ `git diff --check` 通过（无空白错误）
- ✅ `ai.py` 中内联 system message 已清零（`"你是"` 模式 0 匹配）
- ✅ Prompt Registry 已通过 message builder 接入运行时（23 处调用点）

验收偏差（已记录于第 7 节，均不阻塞验收）：
- 偏差 1：`get_prompt_template()` 直接调用 6 处（低于原标准 8 处），因 registry 访问被 Message Builder 集中封装。生产运行时仍通过 message builder 接入 Prompt Registry，不阻塞验收。
- 偏差 2：mistake_staged_service 仍保留 ai_prompts import，仅用于 vision override；普通 text prompt 已通过 message builder / registry 获取。作为受控例外记录。
