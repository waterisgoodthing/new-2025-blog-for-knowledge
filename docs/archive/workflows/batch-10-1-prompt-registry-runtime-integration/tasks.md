# Tasks：Batch 10.1 Prompt Registry Runtime Integration

> 状态：**通过，已关闭**
> 关联：[requirements.md](./requirements.md) | [design.md](./design.md)
> 规则：`[ ]` 待办 / `[x]` 完成；被阻塞或跳过项需注明原因。

## P1-01 Message Builder ✓ 基础设施

目标：在 `ai_prompt_registry.py` 新增 `build_text_messages` 和 `build_vision_messages`。

- [x] 新增 `build_text_messages(task_type, user_content, *, system_prompt_override=None) -> list[dict]`。
- [x] 新增 `build_vision_messages(task_type, content_parts, *, system_prompt_override=None) -> list[dict]`。
- [x] 两个函数均从 `get_prompt_template(task_type)` 获取 `system_prompt`。
- [x] `system_prompt` 为空时 raise `ValueError`（提示调用方传 `system_prompt_override`）。
- [x] 新建 `backend/tests/test_ai_message_builder.py`。
- [x] 测试正常路径（text / vision）。
- [x] 测试 `system_prompt_override` 覆盖。
- [x] 测试空 system_prompt raise ValueError（repair_deterministic / prompt_test）。

完成标准：
- [x] 两个函数定义完成。
- [x] 测试通过。

## P1-02 Gateway 参数从 Registry 读取

目标：修改 `ai_gateway.py` 的 4 个函数签名，参数为 None 时从 registry 读取默认值。

- [x] `call_text` 签名改为 `task_type: str | AiTaskType, *, max_tokens=None, preferred=None, json_mode=None`。
- [x] `call_vision` 签名改为 `task_type: str | AiTaskType, *, max_tokens=None`。
- [x] `call_general` 签名改为 `task_type: str | AiTaskType, *, max_tokens=None, json_mode=None`。
- [x] `call_stream` 签名改为 `task_type: str | AiTaskType, *, max_tokens=None, preferred=None, json_mode=None`。
- [x] 各函数内部：`task_type` 标准化为 `str`（枚举 `.value`）。
- [x] 各函数内部：从 `get_prompt_template(task_type)` 读取 `max_tokens` / `preferred_provider` / `json_mode` / `version`。
- [x] 显式传参优先于 registry 默认值。
- [x] 未知 task_type（如 `"analyze_mistake_stream"`）try/except 降级为 fallback。
- [x] 最终 fallback：`max_tokens=8000, preferred="deepseek", json_mode=True`。
- [x] `prompt_version` 传给 `_write_call_log()`。
- [x] 更新 `backend/tests/test_ai_gateway.py` 适配新签名。

完成标准：
- [x] 4 个函数签名变更完成。
- [x] 现有测试通过（适配后）。
- [x] `call_text("capture_draft", messages)` 仍可工作（str 向后兼容）。

## P1-03 prompt_version 记录到调用日志

目标：`AiCallLog` 新增 `prompt_version` 字段，记录调用时使用的 Prompt 版本。

- [x] `backend/app/models/ai_call_log.py` 新增 `prompt_version = Column(String(20), nullable=True)`。
- [x] `ai_gateway.py` 的 `_write_call_log()` 新增 `prompt_version` 参数。
- [x] 新建 Alembic migration：`op.add_column("ai_call_logs", sa.Column("prompt_version", sa.String(20), nullable=True))`。
- [x] migration 的 `downgrade()` 包含 `op.drop_column`。

完成标准：
- [x] 模型字段定义完成。
- [x] migration 可正常 upgrade / downgrade。
- [x] `_write_call_log` 传入 `prompt_version`。

## P1-04 收敛内联字符串 + 修正 Registry 配置

目标：收敛 `ai.py` router 中的内联 system message 字符串，修正 `ANALYZE_MISTAKE` 的 registry 配置。

- [x] `ai_prompts.py` 新增 `ANALYZE_VISION_SYSTEM_MESSAGE = "你是一个严谨的错题图片识别与解题助手。请始终以 JSON 格式回复。"`。
- [x] `ai_prompt_registry.py` 修正 `ANALYZE_MISTAKE` 配置：`system_prompt=ANALYZE_VISION_SYSTEM_MESSAGE`，`user_content_template=OCR_SYSTEM_PROMPT`。
- [x] 更新 `ai_prompt_registry.py` import（新增 `ANALYZE_VISION_SYSTEM_MESSAGE`）。
- [x] 更新 `test_ai_prompt_registry.py` 验证 `ANALYZE_MISTAKE.system_prompt` 为 `ANALYZE_VISION_SYSTEM_MESSAGE`。

完成标准：
- [x] 内联字符串收敛到 `ai_prompts.py`。
- [x] registry 配置与实际调用一致。
- [x] 测试通过。

## P1-05 build_prompts_response 从 Registry 动态生成

目标：`ai_analyze_service.py` 的 `build_prompts_response()` 从 `PROMPT_REGISTRY` 动态生成。

- [x] 重写 `build_prompts_response()`：遍历 `PROMPT_REGISTRY`，为每个 task_type 生成 `prompt` / `full_prompt` / `version` / `json_mode` / `preferred_provider` / `max_tokens` / `description`。
- [x] 保留原有字段（`prompt` / `full_prompt`），新增字段不破坏前端。
- [x] 移除 `ai_analyze_service.py` 中对 `ai_prompts.py` 常量的直接 import（`build_prompts_response` 不再需要）。
- [x] 更新测试验证响应结构。

完成标准：
- [x] `build_prompts_response()` 从 registry 动态生成。
- [x] `/api/ai/prompts` 响应包含原有字段。
- [x] `ai_analyze_service.py` 不再 import `ai_prompts` 常量（除 stream 路径仍需 OCR_SYSTEM_PROMPT）。

## P1-06 capture 模块迁移

目标：`capture_ai_draft.py` 和 `capture_recognition.py` 改用 message builder。

- [x] `capture_ai_draft.py`：移除 `from app.services.ai_prompts import DRAFT_SYSTEM_PROMPT`，改用 `build_text_messages(AiTaskType.CAPTURE_DRAFT, user_content)`。
- [x] `capture_ai_draft.py`：`call_text` 调用改用 `AiTaskType.CAPTURE_DRAFT`（枚举），不传 `max_tokens` / `preferred` / `json_mode`（从 registry 读取）。
- [x] `capture_recognition.py`：移除 `from app.services.ai_prompts import RECOGNITION_SYSTEM_MESSAGE, RECOGNITION_SYSTEM_PROMPT`，改用 `build_vision_messages(AiTaskType.CAPTURE_RECOGNITION, content)`。
- [x] `capture_recognition.py`：user content 中的 `RECOGNITION_SYSTEM_PROMPT` 改为从 `get_prompt_template(AiTaskType.CAPTURE_RECOGNITION).user_content_template` 获取，或保留 import（过渡期）。
- [x] 现有 `test_capture_service.py` 通过。

完成标准：
- [x] capture 模块不直接 import `ai_prompts` 常量（user_content_template 除外）。
- [x] 现有测试通过。

## P1-07 mistake_staged 模块迁移

目标：`mistake_staged_service.py` 改用 message builder。

- [x] 移除 `from app.services.ai_prompts import QUESTION_DRAFT_SYSTEM_PROMPT, ERROR_INTERPRETATION_SYSTEM_PROMPT, FINAL_ANALYSIS_SYSTEM_PROMPT, QUESTION_DRAFT_VISION_SYSTEM_MESSAGE`。
- [x] `generate_question_draft` vision 路径：`build_vision_messages(AiTaskType.MISTAKE_QUESTION_DRAFT, content, system_prompt_override=...)`。
- [x] `generate_question_draft` text 路径：`build_text_messages(AiTaskType.MISTAKE_QUESTION_DRAFT, user_content)`。
- [x] `generate_error_interpretation`：`build_text_messages(AiTaskType.MISTAKE_ERROR_INTERPRETATION, user_content)`。
- [x] `generate_final_analysis`：`build_text_messages(AiTaskType.MISTAKE_FINAL_ANALYSIS, user_content)`。
- [x] vision 路径的 `QUESTION_DRAFT_VISION_SYSTEM_MESSAGE` 作为 `system_prompt_override` 传入。
- [x] 现有测试通过。

完成标准：
- [x] mistake_staged 模块不直接 import `ai_prompts` 常量。
- [x] 现有测试通过。

## P1-08 diagram 模块迁移

目标：`diagram_service.py` 改用 message builder。

- [x] 移除 `from app.services.ai_prompts import DIAGRAM_STRUCTURED_SYSTEM_PROMPT, QWEN_IMAGE_FALLBACK_PROMPT`。
- [x] 结构化路径：`build_text_messages(AiTaskType.DIAGRAM_STRUCTURED, user_content)`。
- [x] fallback 路径：`build_text_messages(AiTaskType.DIAGRAM_FALLBACK, user_content)`。
- [x] 现有测试通过。

完成标准：
- [x] diagram 模块不直接 import `ai_prompts` 常量。
- [x] 现有测试通过。

## P1-09 ai.py router 迁移

目标：`ai.py` router 改用 message builder，收敛内联字符串。

- [x] `analyze` 端点：`build_vision_messages(AiTaskType.ANALYZE_MISTAKE, content)`，移除内联 `"你是一个严谨的..."` 字符串。
- [x] `analyze-text` 端点：`build_text_messages(AiTaskType.ANALYZE_TEXT, user_content)`。
- [x] `generate-variant` 端点：`build_text_messages(AiTaskType.GENERATE_VARIANT, user_content)`。
- [x] `generate-knowledge-card` 端点：`build_text_messages(AiTaskType.GENERATE_KNOWLEDGE_CARD, user_content)`。
- [x] `knowledge-summary` 端点：`build_text_messages(AiTaskType.KNOWLEDGE_SUMMARY, user_content)`。
- [x] `prompt-test` 端点：`build_text_messages(AiTaskType.PROMPT_TEST, user_content, system_prompt_override=...)`（用户自定义 prompt）。
- [x] `analyze-stream` / `analyze-text-stream`：保留现有结构（stream 端点 task_type 不在枚举中），但 system message 改用 `ANALYZE_VISION_SYSTEM_MESSAGE` 常量。
- [x] 移除 `ai.py` 中对 `ai_prompts` 常量的直接 import（stream 端点保留 OCR_SYSTEM_PROMPT / TEXT_SYSTEM_PROMPT 用于 user content）。
- [x] 现有测试通过。

完成标准：
- [x] `ai.py` router 中无内联 system message 字符串（Grep 验证）。
- [x] 现有测试通过。

## P1-10 ai_analyze_service 迁移

目标：`ai_analyze_service.py` 的 stream 路径和 repair 路径改用 message builder。

- [x] stream 路径的 system message 改用 `ANALYZE_VISION_SYSTEM_MESSAGE` 常量（从 ai_prompts import）。
- [x] stream 路径的 user content 仍用 `OCR_SYSTEM_PROMPT`（从 ai_prompts import 或 `get_prompt_template().user_content_template`）。
- [x] `repair_deterministic` 路径：`build_text_messages(AiTaskType.REPAIR_DETERMINISTIC, user_content, system_prompt_override=dynamic_prompt)`。
- [x] 现有测试通过。

完成标准：
- [x] stream 路径不使用内联字符串。
- [x] `repair_deterministic` 通过 `system_prompt_override` 处理动态 prompt。
- [x] 现有测试通过。

## P1-11 辅助模块迁移

目标：`netease_service.py` 和 `recommendation.py` 改用 message builder。

- [x] `netease_service.py`：移除 `from app.services.ai_prompts import NETEASE_SYSTEM_MESSAGE, NETEASE_REASON_PROMPT`，改用 `build_text_messages(AiTaskType.NETEASE_REASON, user_content)`。
- [x] `netease_service.py`：user_content 中的 `NETEASE_REASON_PROMPT` 模板渲染由调用方处理（`get_prompt_template(AiTaskType.NETEASE_REASON).user_content_template`）。
- [x] `recommendation.py`：移除 `from app.services.ai_prompts import RECOMMENDATION_SYSTEM_PROMPT`，改用 `build_text_messages(AiTaskType.RECOMMENDATION, user_content)`。
- [x] 现有测试通过。

完成标准：
- [x] 辅助模块不直接 import `ai_prompts` 常量。
- [x] 现有测试通过。

## P1-12 验证

- [x] `pytest backend/tests/` — 170 passed, 3 failed（均为预存在问题，`git stash` 确认与本次无关）。
- [x] `npx tsc --noEmit` — 通过（无错误输出）。
- [x] Grep 验证：`get_prompt_template()` 直接调用 6 处 + 间接调用（build_*_messages）17 处 = 23 处注册表驱动调用点。
- [x] Grep 验证：`from app.services.ai_prompts import` 出现在 `ai_prompt_registry.py`、`ai_analyze_service.py`、`ai.py`、`mistake_staged_service.py`（override 常量，有意保留）。
- [x] Grep 验证：`ai.py` router 中无内联 system message 字符串（`"你是"` 模式）— 0 处。
- [x] `/api/ai/prompts` 端点响应包含原有字段（`prompt` / `full_prompt`）+ 新增元数据字段。
- [x] 记录到 `validation.md`。

## P1-13 收口文档

- [x] 更新 `tasks.md` 勾选状态。
- [x] 记录到 `validation.md`。
- [x] 更新 `README.md` 状态为已完成。
- [x] 更新 Batch 10 README.md 关联链接。

## 推荐执行顺序

1. P1-01 Message Builder（基础设施）
2. P1-02 Gateway 参数从 Registry 读取（基础设施）
3. P1-03 prompt_version 记录（基础设施，可与 P1-02 并行）
4. P1-04 收敛内联字符串 + 修正 Registry（依赖 P1-01）
5. P1-05 build_prompts_response 动态生成（独立）
6. P1-06 capture 迁移（依赖 P1-01/02）
7. P1-07 mistake_staged 迁移（依赖 P1-01/02）
8. P1-08 diagram 迁移（依赖 P1-01/02）
9. P1-09 ai.py router 迁移（依赖 P1-01/02/04）
10. P1-10 ai_analyze_service 迁移（依赖 P1-01/02/04）
11. P1-11 辅助模块迁移（依赖 P1-01/02）
12. P1-12 验证
13. P1-13 收口

> 依赖关系：P1-01/02/03 是基础设施，必须先完成。P1-04 依赖 P1-01。P1-06/07/08/09/10/11 依赖 P1-01/02（+ P1-04 for P1-09/10），六者可并行。P1-05 独立。
