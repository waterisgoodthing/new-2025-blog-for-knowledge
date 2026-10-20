# Requirements：Batch 10 Task / Prompt / Validator 管理

> 关联：[design.md](./design.md) | [tasks.md](./tasks.md)

## 1. 背景

Batch 9 完成了 AI Gateway 最小内核，所有 AI 调用已统一经 Gateway 入口，调用日志写入 `ai_call_logs`。但 Gateway 之上的任务管理层仍处于原始状态：task_type 是散落的字符串、Prompt 常量分布在 7 个文件中无版本管理、输出校验方式不统一、失败处理有的返回 error_code 有的直接 raise。

Batch 10 的目标是在 Gateway 之上建立结构化任务管理层，使 AI 调用链从"能跑"升级为"可管理"。

## 2. 功能需求

### R1：AI 任务类型定义

- **R1.1** 新建 `AiTaskType` 枚举，覆盖当前所有 16 个 task_type。
- **R1.2** 枚举值必须与 `ai_call_logs.task_type` 现有字符串完全一致，不改变现有日志数据。
- **R1.3** 枚举使用 `str, Enum` 双继承，保证 `AiTaskType.CAPTURE_DRAFT == "capture_draft"` 为 `True`。
- **R1.4** 所有 service 和 router 中的 task_type 字符串字面量改为枚举引用。

### R2：Prompt 模板版本管理

- **R2.1** 新建 `PromptTemplate` 数据类，包含：task_type, version, system_prompt, output_schema_name, json_mode, preferred_provider, max_tokens, description。
- **R2.2** 新建 `PROMPT_REGISTRY` 注册表，映射每个 AiTaskType 到其 PromptTemplate。
- **R2.3** 当前所有 Prompt 标记为版本 `"v1"`。
- **R2.4** Prompt 文本引用现有常量，不移动文本内容，不修改 Prompt 文本本身。
- **R2.5** 提供 `get_prompt_template(task_type) -> PromptTemplate` 查询函数。
- **R2.6** `ai_analyze_service.py` 中现有 `PROMPT_TEMPLATES` dict 改为从 registry 派生，保持 `/prompts` 端点响应不变。

### R3：输出 Schema / Validator

- **R3.1** 新建 `backend/app/schemas/ai_output.py`，为缺少 schema 的任务补充 Pydantic 输出 schema：
  - `RecognitionOutput` — capture_recognition
  - `VariantOutput` — generate_variant
  - `KnowledgeCardOutput` — generate_knowledge_card
  - `RecommendationOutput` — recommendation
- **R3.2** 复用现有 schema：MistakeDraftSuggestionV1, QuestionDraftResponse, ErrorInterpretationResponse, FinalAnalysisResponse, StructuredDiagramData。
- **R3.3** 新建 `ai_validator.py`，提供 `validate_ai_output(task_type, raw) -> AiValidationResult` 统一校验入口。
- **R3.4** 有 schema 的任务：Pydantic 校验，失败返回 `schema_error`。
- **R3.5** 无 schema 的任务（纯文本输出）：直接返回原始数据，不校验。
- **R3.6** 需要手动 parse 的任务（analyze_mistake/text, knowledge_summary）：不在 validator 层校验，由各 service 的 parse 函数处理，validator 只负责"简单 schema 校验"。

### R4：失败结果进入草稿或错误状态

- **R4.1** 新建 `AiTaskResult` 数据类，包含：task_type, success, data, error_code, error_message_safe, prompt_version, gateway_result。
- **R4.2** 新建 `AiErrorCode` 枚举：empty_input, no_provider, timeout, provider_error, schema_error, parse_error, empty_result。
- **R4.3** capture 模块（capture_ai_draft, capture_recognition）迁移为返回 AiTaskResult。
- **R4.4** mistake_staged 模块从 `raise RuntimeError` 改为返回 AiTaskResult。
- **R4.5** diagram 模块从 `raise RuntimeError` 改为返回 AiTaskResult。
- **R4.6** AI 失败不阻塞业务：调用方根据 error_code 决定进入草稿还是错误状态。
- **R4.7** AI 结果不直接写入 `notes` 表或 `mistake_drafts` 表，只进入草稿区或 HTTP 响应。

## 3. 非功能需求

### N1：不改变现有合同

- **N1.1** 现有 AI 端点的请求/响应 Pydantic schema 不变。
- **N1.2** `ai_gateway.py` 的四个方法签名不变。
- **N1.3** `ai_call_logs` 表结构不变。
- **N1.4** 现有 Prompt 文本内容不变。

### N2：向后兼容

- **N2.1** `ai_call_logs` 中已有的 task_type 字符串数据仍可正常查询。
- **N2.2** `/api/ai/prompts` 端点响应结构不变。

### N3：测试覆盖

- **N3.1** 新增模块需有单元测试。
- **N3.2** 现有测试（test_ai_gateway.py 等）需继续通过。
- **N3.3** `npx tsc --noEmit` 需通过（前端无改动，但需确认无回归）。

## 4. 边界

### 4.1 不做

- 不建设 Prompt 管理后台 UI（管理端页面）。
- 不做多供应商路由或成本统计（Batch 12）。
- 不建设完整 AI 审计事件系统（Batch 11）。
- 不改变现有 AI 端点的请求/响应合同。
- 不直接写正式业务实体（Note / mistake_drafts）。
- 不引入新的数据库表或 migration。
- 不修改 Prompt 文本内容本身。

### 4.2 不触及

- `ai_gateway.py` 内部实现不变。
- `ai_service.py` 内部实现不变。
- `ai_repair_service.py` 内部实现不变。
- 前端代码不变（除非 TypeScript 类型同步需要）。

## 5. 验收标准

- [ ] `AiTaskType` 枚举覆盖全部 16 个 task_type，值与现有字符串一致。
- [ ] `PROMPT_REGISTRY` 注册全部 16 个 task_type 的 PromptTemplate。
- [ ] `ai_output.py` 补充 4 个新输出 schema。
- [ ] `validate_ai_output` 能正确校验有 schema 的任务。
- [ ] `AiTaskResult` 和 `AiErrorCode` 标准化失败处理。
- [ ] capture / mistake_staged / diagram 模块迁移为返回 AiTaskResult。
- [ ] 现有 AI 端点行为不变。
- [ ] 新增单元测试全部通过。
- [ ] 现有测试无回归。
- [ ] `npx tsc --noEmit` 通过。
