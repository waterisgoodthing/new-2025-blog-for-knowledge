# Requirements：Batch 10.1 Prompt Registry Runtime Integration

> 关联：[README.md](./README.md) | [design.md](./design.md) | [tasks.md](./tasks.md)

## 1. 背景

Batch 10 建立了 Prompt Registry 基础设施：

- `AiTaskType` 枚举（16 个值）
- `ai_prompts.py`（14 个 Prompt 常量）
- `ai_prompt_registry.py`（`PromptTemplate` + `PROMPT_REGISTRY` + `get_prompt_template()`）
- `ai_validator.py`（`validate_ai_output` + `SCHEMA_MAP`）

但 `get_prompt_template()` 在生产代码中 **0 处调用**。各 service 直接引用 `ai_prompts.py` 常量手动构建 messages，PromptTemplate 的元数据（version / preferred_provider / max_tokens / json_mode）未被运行时使用。

## 2. 功能需求

### FR-1：Message Builder

引入统一的 message 构建函数，从 registry 获取 system_prompt，替代各 service 手动引用常量构建 messages。

- **FR-1.1**：提供 `build_text_messages(task_type, user_content) -> list[dict]`，从 `get_prompt_template(task_type).system_prompt` 获取 system 消息。
- **FR-1.2**：提供 `build_vision_messages(task_type, content_parts) -> list[dict]`，支持 vision 路径（system + user content_parts）。
- **FR-1.3**：处理 `user_content_template` 字段——当 PromptTemplate 有 `user_content_template` 时（如 NETEASE_REASON），支持模板渲染。
- **FR-1.4**：动态 prompt 任务（`repair_deterministic` / `prompt_test`）的 `system_prompt` 为空字符串时，允许调用方显式传入 system_prompt override。

### FR-2：Gateway 参数从 Registry 读取

修改 gateway 函数签名，当 `max_tokens` / `preferred` / `json_mode` 未显式传时，从 registry 读取默认值。

- **FR-2.1**：`call_text(task_type, messages, *, max_tokens=None, preferred=None, json_mode=None, ...)` — 参数为 None 时从 `get_prompt_template(task_type)` 读取。
- **FR-2.2**：`call_vision(task_type, messages, *, max_tokens=None, ...)` — 同理。
- **FR-2.3**：`call_general(task_type, messages, *, max_tokens=None, json_mode=None, ...)` — 同理。
- **FR-2.4**：显式传参优先于 registry 默认值（向后兼容）。
- **FR-2.5**：`task_type` 参数类型从 `str` 改为 `AiTaskType`（枚举），内部 `.value` 转换。

### FR-3：prompt_version 记录到调用日志

- **FR-3.1**：`AiCallLog` 模型新增 `prompt_version` 字段（`String(20), nullable=True`）。
- **FR-3.2**：`_write_call_log()` 接收 `prompt_version` 参数并持久化。
- **FR-3.3**：gateway 从 `get_prompt_template(task_type).version` 获取版本号，传给 `_write_call_log()`。
- **FR-3.4**：新增 Alembic migration 添加 `prompt_version` 列。

### FR-4：收敛内联字符串

- **FR-4.1**：`ai.py` router 中的 `"你是一个严谨的错题图片识别与解题助手。请始终以 JSON 格式回复。"` 收敛到 registry（作为 `ANALYZE_MISTAKE` 任务的 system_prompt override 或新增 vision system message 常量）。
- **FR-4.2**：`mistake_staged_service.py` 中的 `QUESTION_DRAFT_VISION_SYSTEM_MESSAGE` 已在 `ai_prompts.py` 中，确认 registry 引用。

### FR-5：build_prompts_response 从 Registry 动态生成

- **FR-5.1**：`ai_analyze_service.py` 的 `build_prompts_response()` 从 `PROMPT_REGISTRY` 动态生成响应，而非手动引用各常量。
- **FR-5.2**：`/api/ai/prompts` 端点响应结构不变（字段名和格式保持兼容）。

### FR-6：各 Service 迁移到 Registry 驱动

以下 service 改为通过 `build_text_messages` / `build_vision_messages` 构建消息，不再直接引用 `ai_prompts.py` 常量：

- **FR-6.1**：`capture_ai_draft.py`
- **FR-6.2**：`capture_recognition.py`
- **FR-6.3**：`mistake_staged_service.py`
- **FR-6.4**：`diagram_service.py`
- **FR-6.5**：`ai_analyze_service.py`（build_prompts_response + stream）
- **FR-6.6**：`ai.py` router（analyze / analyze-text / generate-variant / knowledge-card / knowledge-summary / prompt-test）
- **FR-6.7**：`netease_service.py`
- **FR-6.8**：`recommendation.py`

## 3. 非功能需求

### NFR-1：不回归

- 所有现有端点的请求/响应 schema 不变。
- 所有现有 HTTP 状态码和错误语义不变。
- 所有现有测试不回归（允许因 signature 变更导致的测试适配）。

### NFR-2：向后兼容

- gateway 函数签名变更必须向后兼容（新参数有默认值 None，None 时从 registry 读取）。
- `call_text("capture_draft", messages)` 仍可工作（str 自动转枚举或保持 str 兼容）。

### NFR-3：无循环依赖

- Message builder 不得 import 业务 service。
- Gateway 不得 import 业务 service。

### NFR-4：可验证

- `get_prompt_template()` 在生产代码中至少有 8 处调用（每个迁移的 service 至少 1 处）。
- `ai_prompts.py` 常量的直接 import 只出现在 `ai_prompt_registry.py` 和 `ai_analyze_service.py`（build_prompts_response 动态生成时仍需引用）。

## 4. 约束

1. 不改变 `ai_prompts.py` 中的 Prompt 文本内容。
2. 不引入 Prompt 热更新 / A/B 测试 / 效果评估。
3. 不引入 few-shot examples / Prompt 测试集。
4. 不新增 Prompt 管理数据库表（`prompt_version` 字段除外）。
5. 不改变现有端点的请求/响应 schema 和 HTTP 状态码。
6. `AiCallLog.prompt_version` 字段 nullable=True，旧记录不受影响。
