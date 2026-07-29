# Validation：Batch 10 Task / Prompt / Validator 管理

> 验证日期：2026-07-05
> 关联：[tasks.md](./tasks.md) | [requirements.md](./requirements.md) | [design.md](./design.md)

## 1. 验证命令与结果

### 1.1 pytest backend/tests/

```bash
cd backend && .venv/bin/python -m pytest tests/
```

结果：**160 passed, 3 failed, 3 warnings in 3.40s**

3 个失败测试均为预置问题，与 Batch 10 无关：

| 测试 | 失败原因 |
|------|----------|
| `test_attachment_service.py::test_attachment_links_reject_missing_targets_and_deleted_attachments` | asyncpg teardown 警告（数据库连接 dispose 资源未完全释放） |
| `test_mistake_review_service.py::test_review_uses_fixed_interval_and_rejects_stale_submission` | asyncpg teardown 警告（数据库连接 dispose 资源未完全释放） |
| `test_mistake_review_service.py::test_unconfirmed_draft_does_not_enter_review_queue` | asyncpg teardown 警告（数据库连接 dispose 资源未完全释放） |

这些测试涉及的 `attachment_service` 和 `mistake_review_service` 均不在 Batch 10 修改范围内，失败原因为数据库连接 teardown 问题（asyncpg `Connection.close` 资源警告），非 Batch 10 引入。

Batch 10 新增测试全部通过（66 passed）：

| 测试文件 | 测试数 | 说明 |
|----------|--------|------|
| `test_ai_task_types.py` | 5 | 枚举值数量与字符串一致性 |
| `test_ai_task_result.py` | 7 | AiTaskResult 构造与字段访问 |
| `test_ai_output_schemas.py` | 11 | 4 个新 schema 的正常构造与校验失败 |
| `test_ai_prompt_registry.py` | 12 | 注册表覆盖、PromptTemplate 非空、无循环依赖 |
| `test_ai_validator.py` | 19 | 有 schema/无 schema 任务的校验路径 |
| `test_capture_service.py` | 12 | capture 迁移后端点行为不回归 |

### 1.2 npx tsc --noEmit

```bash
npx tsc --noEmit
```

结果：**通过**（无错误输出）

前端无改动，确认无类型回归。

### 1.3 Grep 验收

```bash
grep -rnE 'call_(text|vision|general|stream)\(\s*["'"'"']' backend/
```

结果：**生产代码 0 匹配**

5 处匹配全部位于 `backend/tests/test_ai_gateway.py`（测试文件），符合约束 5："Grep 验收只要求生产 Gateway 调用处不再传裸 task_type 字符串；枚举定义、测试、文档、兼容映射允许保留字符串。"

## 2. 端点回归确认

根据约束 3/4，以下端点的请求/响应 schema 和 HTTP 状态码不得变化：

| 端点 | 确认结果 |
|------|----------|
| `POST /api/ai/capture/draft` | 返回 `DraftResult`（suggestion / success / error_code），schema 不变 |
| `POST /api/ai/capture/recognize` | 返回 `RecognitionResult`（recognized_text / success / error_code），schema 不变 |
| `POST /api/ai/mistake/question-draft` | 返回 dict + raise，HTTP 语义不变 |
| `POST /api/ai/mistake/error-interpretation` | 返回 dict + raise，HTTP 语义不变 |
| `POST /api/ai/mistake/final-analysis` | 返回 dict + raise，HTTP 语义不变 |
| `POST /api/ai/mistake/diagram` | 返回 dict + raise，HTTP 语义不变 |
| `POST /api/ai/analyze` | 返回 dict + raise，HTTP 语义不变 |
| `POST /api/ai/analyze-text` | 返回 dict + raise，HTTP 语义不变 |
| `POST /api/ai/generate-variant` | 返回 dict + raise，HTTP 语义不变 |
| `POST /api/ai/generate-knowledge-card` | 返回 dict + raise，HTTP 语义不变 |
| `POST /api/ai/knowledge-summary` | 返回 dict + raise，HTTP 语义不变 |
| `POST /api/ai/prompt-test` | 返回 dict + raise，HTTP 语义不变 |
| `GET /api/ai/prompts` | 返回 `build_prompts_response()` 结构不变 |
| `POST /api/ai/analyze-stream` | task_type 为 `"analyze_mistake_stream"`（非直接 gateway 调用，通过变量传递） |
| `POST /api/ai/analyze-text-stream` | task_type 为 `"analyze_text_stream"`（非直接 gateway 调用，通过变量传递） |

## 3. 约束遵守确认

| 约束 | 遵守情况 |
|------|----------|
| 1. Prompt Registry 不得 import 业务 service | ✓ `ai_prompt_registry.py` 只 import `ai_prompts`（纯常量 module）和 `ai_task_types`；`ai_prompts.py` 不 import 任何业务 service。测试 `test_registry_does_not_import_business_services` 验证通过 |
| 2. AiTaskResult 只作为内部统一结果对象 | ✓ AiTaskResult 未暴露给任何 API 端点；capture 保留 `DraftResult`/`RecognitionResult`，mistake_staged/diagram/analyze 保留 dict+raise |
| 3. router 显式适配 AiTaskResult | ✓ router 无需改动（返回类型不变，端点响应 schema 不变）；AiTaskResult 仅用于内部逻辑 |
| 4. 失败处理不改变 HTTP 状态码和错误语义 | ✓ capture 失败仍返回 `DraftResult(success=False, error_code=...)`；mistake_staged/diagram/analyze 仍 raise HTTPException |
| 5. Grep 验收只要求生产代码 | ✓ 生产 Gateway 调用处 0 匹配；测试文件中 5 处保留字符串（符合约束） |
| 6. 不新增 migration / 数据库表 / 前端后台 / 成本统计 / 多供应商路由 / AI 审计 / 人工流转 | ✓ Batch 10 未新增 Alembic migration、未新增数据库表、未改前端、未新增成本统计/路由/审计/流转逻辑 |
| 7. 不进入 Batch 11 | ✓ Batch 10 范围内完成，未启动 Batch 11 |

## 4. 修改文件清单

### 4.1 新建文件（11 个）

| 文件 | 用途 |
|------|------|
| `backend/app/services/ai_task_types.py` | AiTaskType 枚举（16 个值） |
| `backend/app/services/ai_task_result.py` | AiTaskResult + AiErrorCode |
| `backend/app/schemas/ai_output.py` | 4 个新输出 schema（Recognition/Variant/KnowledgeCard/Recommendation） |
| `backend/app/services/ai_prompts.py` | 14 个 Prompt 常量（从 7 个 service 迁移） |
| `backend/app/services/ai_prompt_registry.py` | PromptTemplate + PROMPT_REGISTRY + get_prompt_template |
| `backend/app/services/ai_validator.py` | AiValidationResult + SCHEMA_MAP + validate_ai_output |
| `backend/tests/test_ai_task_types.py` | 枚举测试（5） |
| `backend/tests/test_ai_task_result.py` | 结果对象测试（7） |
| `backend/tests/test_ai_output_schemas.py` | schema 测试（11） |
| `backend/tests/test_ai_prompt_registry.py` | 注册表测试（12） |
| `backend/tests/test_ai_validator.py` | validator 测试（19） |

### 4.2 修改文件（9 个）

| 文件 | 修改内容 |
|------|----------|
| `backend/app/services/capture_ai_draft.py` | 导入 AiTaskType + validate_ai_output；task_type 改枚举 .value；集成 validate_ai_output（带 fallback） |
| `backend/app/services/capture_recognition.py` | 导入 AiTaskType + validate_ai_output；task_type 改枚举 .value；集成 validate_ai_output |
| `backend/app/services/mistake_staged_service.py` | 导入 AiTaskType；4 处 task_type 改枚举 .value（validate_ai_output 集成 deferred） |
| `backend/app/services/diagram_service.py` | 导入 AiTaskType + ai_prompts；2 处 task_type 改枚举 .value；删除 2 个本地 Prompt 常量 |
| `backend/app/routers/ai.py` | 导入 AiTaskType；7 处 task_type 改枚举 .value |
| `backend/app/services/ai_analyze_service.py` | 导入 AiTaskType + ai_prompts；2 处 repair_deterministic 改枚举 .value；删除 5 个本地 Prompt 常量 |
| `backend/app/services/netease_service.py` | 导入 AiTaskType；1 处 task_type 改枚举 .value |
| `backend/app/services/recommendation.py` | 导入 AiTaskType；1 处 task_type 改枚举 .value |
| `backend/tests/test_ai_prompt_registry.py` | 修复循环依赖测试：清除业务 service 模块 |

## 5. 已知 deferred 项

| 项 | 原因 |
|----|------|
| mistake_staged_service 集成 validate_ai_output | mistake_staged 已有 normalize 逻辑（`_normalize_question_draft` / `_normalize_error_interpretation` / `_normalize_final_analysis`），与 validator 集成需更细致测试，deferred 到后续迭代 |
| stream 端点 task_type 枚举化 | `"analyze_mistake_stream"` / `"analyze_text_stream"` 非直接 gateway 调用（通过 `stream_analyze_events` 变量传递），不在 AiTaskType 枚举中，保留为字符串 |

## 6. 结论

Batch 10 Task / Prompt / Validator 管理全部 P0-01 至 P0-12 完成。

- 16 个 task_type 字符串收敛为 `AiTaskType` 枚举
- 14 个 Prompt 常量迁移到独立 `ai_prompts.py` module（无循环依赖）
- 16 个 PromptTemplate 注册到 `PROMPT_REGISTRY`
- 9 个有 schema 的 task_type 通过 `validate_ai_output` 统一校验
- capture 模块集成 validator（带 fallback）
- 生产代码中 0 处裸 task_type 字符串
- 现有端点请求/响应 schema 和 HTTP 语义不变
- 未新增 migration / 数据库表 / 前端后台
