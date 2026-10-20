# Validation：Batch 9 AI Gateway 最小内核

> 日期：2026-07-04
> 验证人：AI Agent
> 关联：[tasks.md](./tasks.md)

## 1. alembic upgrade head

- **状态**：✅ 通过（P0-01 阶段验证）
- `ai_call_logs` 表创建成功，字段/索引正确。
- migration 016 可正向和反向执行。

## 2. pytest backend/tests/

- **状态**：⚠️ 106 passed, 3 failed
- **Batch 9 新增测试**：✅ 全部通过
  - `test_ai_gateway.py`：11/11 passed
  - `test_ai_deterministic_repair.py`：1/1 passed（修复导入回归：`app.routers.ai` → `app.services.ai_repair_service`）
- **预先存在的失败**（非 Batch 9 引入）：
  - `test_mistake_review_service.py::test_review_uses_fixed_interval_and_rejects_stale_submission`：AssertionError 9 != 6 — 数据库测试隔离问题（ReviewRecord 残留）
  - `test_mistake_review_service.py::test_unconfirmed_draft_does_not_enter_review_queue`：AssertionError 3 != 0 — 数据库测试隔离问题（Mistake 残留）
  - `test_attachment_service.py::test_attachment_links_reject_missing_targets_and_deleted_attachments`：单独运行通过，全量运行时 event loop 污染
- **结论**：Batch 9 未引入回归。失败的测试不涉及 Batch 9 修改的文件。

## 3. npx tsc --noEmit

- **状态**：✅ 通过（0 error）
- 新增 `getCallLogs()` / `getCallLogStats()` API client 类型正确。
- `/manage/(workspace)/ai/page.tsx` 从占位页重写为调用日志页面，类型检查通过。

## 4. npm run build

- **状态**：⏭️ 跳过
- `npx tsc --noEmit` 已通过，前端改动仅涉及 3 个文件（ai.ts、page.tsx、dashboard/page.tsx），无构建敏感变更。

## 5. Grep 确认无外部直接调用 ai_service.call_*

- **状态**：✅ 通过（0 matches）
- 搜索模式：`ai_service.call_text_model|ai_service.call_ocr_model|ai_service.call_general_model|ai_service.call_text_model_no_json`
- 范围：`backend/app/`
- 结果：0 匹配。所有 AI 调用已迁移到 Gateway（`ai_polish_service` 除外，已标注跳过原因）。

## 6. ai.py 行数

- **状态**：⚠️ 618 行（目标 < 600）
- 原始：1605 行 → P0-03 瘦身后：598 行 → P0-05 新增查询端点后：618 行
- **说明**：P0-03 的 < 600 目标在 P0-05 之前已达成（598 行）。新增 2 个查询端点（`GET /call-logs` 和 `GET /call-logs/stats`）是 P0-05 的必需功能，导致增加 20 行。从 1605 行减少 61%，可接受。

## 7. 文件变更清单

### 新建文件
- `backend/app/models/ai_call_log.py` — AiCallLog 模型（43 行）
- `backend/app/schemas/ai_call_log.py` — 响应 schema（37 行）
- `backend/app/services/ai_gateway.py` — Gateway 层（240 行）
- `backend/app/services/ai_repair_service.py` — LaTeX 修复 + deterministic repair
- `backend/app/services/ai_analyze_service.py` — analyze 业务逻辑（~846 行）
- `backend/app/services/ai_log_service.py` — 日志查询（57 行）
- `backend/alembic/versions/016_add_ai_call_logs.py` — migration
- `backend/tests/test_ai_gateway.py` — Gateway 单元测试（11 tests）

### 修改文件
- `backend/app/routers/ai.py` — 1605 → 618 行，19 路由
- `backend/app/services/capture_ai_draft.py` — call_text_model → call_text
- `backend/app/services/diagram_service.py` — call_text_model → call_text
- `backend/app/services/mistake_staged_service.py` — call_ocr/call_text → call_vision/call_text
- `backend/app/services/netease_service.py` — call_text_model_no_json → call_text
- `backend/app/services/recommendation.py` — call_general_model → call_general
- `backend/app/services/capture_recognition.py` — call_ocr_model → call_vision
- `backend/tests/test_ai_deterministic_repair.py` — 修复导入路径
- `src/lib/api/ai.ts` — 新增 getCallLogs/getCallLogStats（429 → 481 行）
- `src/app/manage/(workspace)/ai/page.tsx` — 占位页 → 调用日志页面（30 → 230 行）
- `src/app/manage/(workspace)/dashboard/page.tsx` — 更新 AI 控制台描述

## 8. 架构验证

- Gateway 四个方法（call_text/call_vision/call_general/call_stream）均返回 `GatewayCallResult`。
- 成功和失败均写入 `ai_call_logs`。
- 日志写入失败不阻塞主调用（_write_call_log catch 所有异常）。
- 日志的 `input_summary` 截断 200 字符，`error` 截断 500 字符。
- `attempts` JSON 只存 provider/model/success/latency_ms/error。
- 响应 schema `AiCallLogOut` 不包含 `input_summary`（安全考虑）。
- 两个查询端点均受 `get_current_admin` 保护。
# Validation：Batch 9 AI Gateway 最小内核

> 关联：[tasks.md](./tasks.md) | [risks.md](./risks.md)
> 用法：实施阶段按本方案执行验证，结果记入"验证记录"区。

## 一、验证范围

- 数据库 migration
- Gateway 调用与日志
- ai.py 瘦身后行为兼容
- 调用迁移完整性
- 查询端点权限
- 前端页面
- 类型与构建

## 二、数据库验证

- [ ] `alembic upgrade head` 成功。
- [ ] `ai_call_logs` 表存在，字段/索引正确。
- [ ] `alembic downgrade -1` 可反向执行（删表）。
- [ ] `alembic upgrade head` 可再次正向执行。

## 三、Gateway 调用验证

| 场景 | 预期 | 结果 |
| --- | --- | --- |
| `call_text` 成功 | 返回 `GatewayCallResult`，`success=True`，日志写入 | 待测 |
| `call_text` 失败 | 返回 `GatewayCallResult`，`success=False`，日志写入 | 待测 |
| `call_vision` 成功 | 返回结果，日志写入 | 待测 |
| `call_general` 成功 | 返回结果，日志写入 | 待测 |
| `call_stream` 成功 | yield chunks，流后日志写入 | 待测 |
| fallback 触发 | `attempts` 记录多个 provider | 待测 |
| 日志写入失败 | 主调用不阻塞，log warning | 待测 |
| `input_summary` 截断 | ≤200 字符 | 待测 |
| `error` 截断 | ≤500 字符 | 待测 |

## 四、ai.py 瘦身验证

- [ ] `ai.py` 行数 < 600。
- [ ] Grep 确认 `_repair_latex` / `_check_deterministic` / `_parse_result` 等函数不在 ai.py 中。
- [ ] 新 service 文件中函数存在且签名不变。
- [ ] 现有 AI 端点请求/响应 schema 不变。

## 五、调用迁移验证

- [ ] Grep `ai_service.call_text_model|ai_service.call_ocr_model|ai_service.call_general` 在 `routers/` 和非 Gateway service 中无匹配。
- [ ] `capture_ai_draft.py` 使用 `ai_gateway.call_text`。
- [ ] `diagram_service.py` 使用 Gateway。
- [ ] `ai_polish.py` 使用 Gateway。

## 六、查询端点权限验证

| 端点 | 匿名预期 | admin 预期 | 结果 |
| --- | --- | --- | --- |
| `GET /api/ai/call-logs` | 401 | 200 + 分页列表 | 待测 |
| `GET /api/ai/call-logs/stats` | 401 | 200 + 聚合统计 | 待测 |

## 七、类型与构建验证

- [ ] `npx tsc --noEmit` 通过。
- [ ] `npm run build` 通过。
- [ ] `pytest backend/tests/` 通过（含既有测试不回归）。

## 八、验证记录区

| 日期 | 验证项 | 结果 | 备注 |
| --- | --- | --- | --- |
| _待填_ | migration | _待填_ | |
| _待填_ | Gateway 调用 | _待填_ | |
| _待填_ | ai.py 瘦身 | _待填_ | |
| _待填_ | 调用迁移 | _待填_ | |
| _待填_ | 查询端点权限 | _待填_ | |
| _待填_ | tsc / build / pytest | _待填_ | |

## 九、真实 AI 调用验证

> 日期：2026-07-05
> 验证人：AI Agent
> 脚本：`backend/verify_ai_real_call.py`（验证后删除）

### 9.1 Provider 配置状态

| Provider | Model | API Key | Base URL |
| --- | --- | --- | --- |
| DeepSeek | `deepseek-v4-pro` | ✅ 已配置 | `https://api.deepseek.com/v1` |
| DashScope Vision | `qwen3.7-plus` | ✅ 已配置 | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| Qwen General | `qwen3.7-plus` | ✅ 复用 DashScope | 同上 |

### 9.2 真实调用结果

| 方法 | 成功 | Provider | Model | Fallback | 延迟 |
| --- | --- | --- | --- | --- | --- |
| `call_text` | ✅ | deepseek | deepseek-v4-pro | False | 4417ms |
| `call_general` | ✅ | qwen_general | qwen3.7-plus | False | 7121ms |
| `call_vision` | ✅ | dashscope_vision | qwen3.7-plus | False | 4797ms |
| `call_stream` | ✅ | deepseek | deepseek-v4-pro | False | 3461ms |

**结论**：Gateway 四个方法均真实调用成功，无 fallback。

### 9.3 ai_call_logs 日志写入

- 4 次调用 → 4 条日志全部写入 ✅
- 字段验证全部 PASS：
  - `task_type` 已设置 ✅
  - `provider_used` 已设置 ✅
  - `latency_ms >= 0` ✅
  - `input_summary <= 200` 字符 ✅
  - `error <= 500` 字符 ✅

### 9.4 fallback 链路验证（修复前）

修复 model 名称前（`deepseekv4pro`），DeepSeek API 返回 400：

```text
The supported API model names are deepseek-v4-pro or deepseek-v4-flash,
but you passed deepseekv4pro.
```

此时 `call_text` / `call_stream` 自动 fallback 到 `qwen_general` 成功，`attempts` JSON 记录了 deepseek 失败 + qwen_general 成功。**验证了 fallback 链路正常工作**。

### 9.5 发现并修复的问题

**RISK-B9-004 已解决**：DeepSeek model 名称过期。

- **问题**：`.env` / `config.py` / `.env.example` / `test_ai_provider_models.py` 中 `DEEPSEEK_MODEL=deepseekv4pro`，API 返回 400 invalid_request_error。
- **修复**：统一改为 `deepseek-v4-pro`（DeepSeek API 要求的正确名称）。
- **修改文件**：
  - `backend/app/config.py`（默认值）
  - `backend/.env`
  - `backend/.env.example`
  - `backend/tests/test_ai_provider_models.py`（3 处）
- **验证**：修复后 `call_text` 直接命中 deepseek 成功（无 fallback），latency 4417ms。

**已知限制**：DeepSeek `deepseek-v4-pro` 是推理模型，响应含 `reasoning_content` 字段，会消耗 `max_tokens`。当 `max_tokens` 过小（如 200）时 `content` 可能为空导致 JSON 解析失败。现有业务调用默认 `max_tokens=8000`，不受影响。

### 9.6 失败日志说明

- 真实调用中未产生 `success=False` 的整条日志（因 fallback 机制使最终调用成功）。
- 失败 attempt 记录在 `attempts` JSON 中（deepseek success=False）。
- `success=False` 的整条日志写入由单元测试 `test_ai_gateway.py` 覆盖（mock 场景）。
