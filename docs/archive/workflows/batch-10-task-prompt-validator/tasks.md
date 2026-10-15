# Tasks：Batch 10 Task / Prompt / Validator 管理

> 状态：**已批准（有条件）**
>
> 批准确约束：
> 1. Prompt Registry 不得 import 业务 service，避免循环依赖；Prompt 常量迁移到独立 prompt module。
> 2. AiTaskResult 只作为内部统一结果对象，外部 API 请求/响应 schema 不变。
> 3. router 必须显式适配 AiTaskResult，不把新内部结构泄露给旧端点。
> 4. 失败处理内部标准化为 AiErrorCode，但不得改变 HTTP 状态码和旧端点错误语义。
> 5. Grep 验收只要求生产 Gateway 调用处不再传裸 task_type 字符串；枚举定义、测试、文档、兼容映射允许保留字符串。
> 6. 本批不新增 migration、不新增 Prompt 管理数据库表、不做前端后台、不做成本统计/多供应商路由/完整 AI 审计/人工流转。
> 7. 不进入 Batch 11。
> 关联：[requirements.md](./requirements.md) | [design.md](./design.md)
> 规则：`[ ]` 待办 / `[x]` 完成；被阻塞或跳过项需注明原因。

## P0-01 AiTaskType 枚举 ✓

目标：把散落的 16 个 task_type 字符串收敛为统一枚举。

- [x] 新建 `backend/app/services/ai_task_types.py`。
- [x] 定义 `AiTaskType(str, Enum)`，覆盖全部 16 个 task_type（值见 design.md 第 2.2 节）。
- [x] 枚举值与现有字符串完全一致（如 `CAPTURE_DRAFT == "capture_draft"`）。
- [x] 新建 `backend/tests/test_ai_task_types.py`。
- [x] 测试枚举值数量、字符串值一致性。

完成标准：
- [x] 16 个枚举值全部定义。
- [x] `AiTaskType.CAPTURE_DRAFT == "capture_draft"` 为 `True`。
- [x] 测试通过（5 passed）。

## P0-02 AiTaskResult 与 AiErrorCode ✓

目标：定义标准化的 AI 任务结果和错误码。

- [x] 新建 `backend/app/services/ai_task_result.py`。
- [x] 定义 `AiErrorCode(str, Enum)`：empty_input / no_provider / timeout / provider_error / schema_error / parse_error / empty_result。
- [x] 定义 `AiTaskResult` dataclass：task_type / success / data / error_code / error_message_safe / prompt_version / gateway_result。
- [x] 新建 `backend/tests/test_ai_task_result.py`。
- [x] 测试 AiTaskResult 构造和字段访问。

完成标准：
- [x] AiErrorCode 覆盖 7 种错误码。
- [x] AiTaskResult 字段完整。
- [x] 测试通过（7 passed）。

## P0-03 输出 Schema 补充 ✓

目标：为缺少 Pydantic schema 的 AI 任务补充输出 schema。

- [x] 新建 `backend/app/schemas/ai_output.py`。
- [x] 定义 `RecognitionOutput`（capture_recognition 输出：`text: str`）。
- [x] 定义 `VariantOutput`（generate_variant 输出：question / correct_answer / analysis / difficulty / knowledge_points）。
- [x] 定义 `KnowledgeCardOutput`（generate_knowledge_card 输出：title / content / knowledge_points / subject）。
- [x] 定义 `RecommendationOutput`（recommendation 输出：title / reason / slug）。
- [x] 新建 `backend/tests/test_ai_output_schemas.py`。
- [x] 测试各 schema 的正常构造和校验失败场景。

完成标准：
- [x] 4 个新 schema 定义完成。
- [x] schema 字段与 Prompt 中要求的 JSON 格式一致。
- [x] 测试通过（11 passed）。

## P0-04 Prompt 模板注册表 ✓

目标：把散落在 7 个 service 中的 Prompt 常量收敛为统一注册表。

**约束：Prompt Registry 不得 import 业务 service，避免循环依赖。**

- [x] 新建 `backend/app/services/ai_prompts.py`：把全部 14 个 Prompt 常量从各 service 迁移到此独立 module（纯常量，不 import 业务 service）。
- [x] 新建 `backend/app/services/ai_prompt_registry.py`：从 `ai_prompts` 导入常量，定义注册表。
- [x] 定义 `PromptTemplate` frozen dataclass（字段见 design.md 第 2.3 节）。
- [x] 注册全部 16 个 task_type 的 PromptTemplate（含纯文本任务的 prompt 引用）。
- [x] 所有版本标记为 `"v1"`。
- [x] 提供 `get_prompt_template(task_type) -> PromptTemplate` 查询函数。
- [x] 各 service 改为从 `ai_prompts` 导入 Prompt 常量（替代本地定义）。
- [x] 新建 `backend/tests/test_ai_prompt_registry.py`。
- [x] 测试注册表覆盖全部 AiTaskType。
- [x] 测试每个 PromptTemplate 的 system_prompt 非空。
- [x] 测试 `ai_prompt_registry` 不 import 任何业务 service（import 检查）。

完成标准：
- [x] 16 个 PromptTemplate 全部注册。
- [x] `get_prompt_template(AiTaskType.CAPTURE_DRAFT)` 返回正确模板。
- [x] 测试通过（12 passed）。

## P0-05 统一 Validator ✓

目标：提供统一的 AI 输出校验入口。

- [x] 新建 `backend/app/services/ai_validator.py`。
- [x] 定义 `AiValidationResult` dataclass：success / data / error_code / error_message_safe。
- [x] 定义 `SCHEMA_MAP: dict[AiTaskType, type[BaseModel] | None]`，映射 task_type 到输出 schema。
- [x] 有 schema 的任务：MistakeDraftSuggestionV1 / RecognitionOutput / QuestionDraftResponse / ErrorInterpretationResponse / FinalAnalysisResponse / StructuredDiagramData / VariantOutput / KnowledgeCardOutput / RecommendationOutput。
- [x] 无 schema 的任务（纯文本）：diagram_fallback / netease_reason / prompt_test / repair_deterministic / analyze_mistake / analyze_text / knowledge_summary。
- [x] 实现 `validate_ai_output(task_type, raw) -> AiValidationResult`。
- [x] 新建 `backend/tests/test_ai_validator.py`。
- [x] 测试有 schema 任务的校验成功路径。
- [x] 测试有 schema 任务的校验失败路径（返回 schema_error）。
- [x] 测试无 schema 任务直接返回原始数据。

完成标准：
- [x] `validate_ai_output` 正确校验有 schema 的任务。
- [x] 校验失败返回 `error_code="schema_error"`。
- [x] 无 schema 任务不校验，直接返回。
- [x] 测试通过（19 passed）。

## P0-06 capture 模块迁移 ✓

目标：capture_ai_draft 和 capture_recognition 迁移为返回 AiTaskResult。

- [x] `capture_ai_draft.py`：task_type 改用 `AiTaskType.CAPTURE_DRAFT`。
- [x] `capture_ai_draft.py`：从 `get_prompt_template` 获取 system_prompt（已从 ai_prompts 导入）。
- [x] `capture_ai_draft.py`：用 `validate_ai_output` 替代手动 `_validate_suggestion`（保留兼容逻辑）。
- [x] `capture_ai_draft.py`：保留 `DraftResult` 作为返回类型（约束 2/3：AiTaskResult 为内部对象，不暴露给端点）。
- [x] `capture_recognition.py`：task_type 改用 `AiTaskType.CAPTURE_RECOGNITION`。
- [x] `capture_recognition.py`：从 `get_prompt_template` 获取 system_prompt（已从 ai_prompts 导入）。
- [x] `capture_recognition.py`：用 `validate_ai_output` 替代手动解析。
- [x] `capture_recognition.py`：保留 `RecognitionResult` 作为返回类型。
- [x] 检查 `capture_service.py` 对 DraftResult / RecognitionResult 的引用，无需适配（返回类型不变）。
- [x] router 无需改动（返回类型不变，端点响应 schema 不变）。
- [x] 不得改变 HTTP 状态码和旧端点错误语义。
- [x] 现有 `test_capture_service.py` 通过。

完成标准：
- [x] capture 模块 task_type 使用枚举 `.value`。
- [x] 现有 capture 测试通过。
- [x] error_code 行为不变。
- [x] 端点响应 schema 不变。

## P0-07 mistake_staged 模块迁移 ✓

目标：mistake_staged_service 的 task_type 改用枚举。

- [x] `mistake_staged_service.py`：task_type 改用枚举（3 个：MISTAKE_QUESTION_DRAFT / MISTAKE_ERROR_INTERPRETATION / MISTAKE_FINAL_ANALYSIS）。
- [x] `mistake_staged_service.py`：从 `ai_prompts` 导入 system_prompt（P0-04 已完成）。
- [x] 保留现有返回类型（dict + raise），约束 2/3/4：AiTaskResult 为内部对象，不暴露给端点，HTTP 语义不变。
- [x] 不得改变 HTTP 状态码和旧端点错误语义。
- [ ] ~~用 `validate_ai_output` 校验输出~~（deferred：mistake_staged 已有 normalize 逻辑，与 validator 集成需更细致测试）。

完成标准：
- [x] mistake_staged 模块 task_type 使用枚举 `.value`。
- [x] 现有端点行为不变。
- [x] 端点响应 schema 不变。

## P0-08 diagram 模块迁移 ✓

目标：diagram_service 的 task_type 改用枚举。

- [x] `diagram_service.py`：task_type 改用枚举（2 个：DIAGRAM_STRUCTURED / DIAGRAM_FALLBACK）。
- [x] `diagram_service.py`：从 `ai_prompts` 导入 system_prompt（P0-04 已完成）。
- [x] 保留现有返回类型（dict + raise），约束 2/3/4：AiTaskResult 为内部对象，不暴露给端点。
- [x] 不得改变 HTTP 状态码和旧端点错误语义。

完成标准：
- [x] diagram 模块 task_type 使用枚举 `.value`。
- [x] 现有端点行为不变。
- [x] 端点响应 schema 不变。

## P0-09 analyze / router 迁移 ✓

目标：ai_analyze_service 和 ai.py router 的 task_type 改用枚举。

- [x] `ai_analyze_service.py`：`repair_deterministic` 改用 `AiTaskType.REPAIR_DETERMINISTIC.value`（gateway_call + 默认参数）。
- [x] `ai_analyze_service.py`：`build_prompts_response()` 响应结构不变。
- [x] `ai.py` router：所有 `call_text("...")` / `call_vision("...")` 的 task_type 字符串改用枚举 `.value`（7 处）。
- [x] `/api/ai/prompts` 端点响应结构不变。
- [x] `ai_call_log.py` schema 无需改动（task_type 仍为字符串，枚举 `.value` 即字符串）。

完成标准：
- [x] router 中无 task_type 字符串字面量（Grep 验证通过）。
- [x] `/api/ai/prompts` 响应不变。
- [x] 现有端点行为不变。

## P0-10 辅助模块迁移 ✓

目标：recommendation 和 netease_service 的 task_type 改用枚举。

- [x] `recommendation.py`：task_type 改用 `AiTaskType.RECOMMENDATION.value`。
- [x] `netease_service.py`：task_type 改用 `AiTaskType.NETEASE_REASON.value`。
- [x] `recommendation.py`：从 `ai_prompts` 导入 system_prompt（P0-04 已完成）。

完成标准：
- [x] 辅助模块 task_type 使用枚举。
- [x] 现有行为不变。

## P0-11 验证 ✓

- [x] `pytest backend/tests/` — Batch 10 新增测试全部通过（66 passed），3 个预置失败与 Batch 10 无关（attachment_service / mistake_review_service 数据库连接问题）。
- [x] `npx tsc --noEmit` — 通过（前端无改动，确认无回归）。
- [x] Grep 确认生产 Gateway 调用处不再传裸 task_type 字符串（`call_(text|vision|general|stream)\(\s*["']` 匹配 0 处）。
- [x] 记录到 `validation.md`。

## P0-12 收口文档 ✓

- [x] 更新 `tasks.md` 勾选状态。
- [x] 记录到 `validation.md`。
- [x] 更新 `README.md` 状态。

## 推荐执行顺序

1. P0-01 AiTaskType 枚举
2. P0-02 AiTaskResult + AiErrorCode
3. P0-03 输出 Schema 补充
4. P0-04 Prompt 模板注册表（依赖 P0-01）
5. P0-05 统一 Validator（依赖 P0-01/03/04）
6. P0-06 capture 迁移（依赖 P0-01/02/04/05）
7. P0-07 mistake_staged 迁移（依赖 P0-01/02/04/05）
8. P0-08 diagram 迁移（依赖 P0-01/02/04/05）
9. P0-09 analyze/router 迁移（依赖 P0-01/04）
10. P0-10 辅助模块迁移（依赖 P0-01/04）
11. P0-11 验证
12. P0-12 收口

> 依赖关系：P0-04 依赖 P0-01。P0-05 依赖 P0-01/03/04。P0-06/07/08 依赖 P0-01/02/04/05，三者可并行。P0-09/10 依赖 P0-01/04。
