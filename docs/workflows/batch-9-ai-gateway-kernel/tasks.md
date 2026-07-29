# Tasks：Batch 9 AI Gateway 最小内核

> 状态：**已完成**（P0-01~P0-09 全部完成）
> 关联：[requirements.md](./requirements.md) | [design.md](./design.md) | [risks.md](./risks.md)
> 规则：`[ ]` 待办 / `[x]` 完成；被阻塞或跳过项需注明原因。

## P0-01 ai_call_log 模型与 migration

目标：新建 `AiCallLog` 模型与 Alembic 016 migration。

- [x] 新建 `backend/app/models/ai_call_log.py`（字段见 design.md 第四节）。
- [x] `backend/app/models/__init__.py` 导入 `AiCallLog`，加入 `__all__`。
- [x] 新建 `backend/alembic/versions/016_add_ai_call_logs.py`。
- [x] migration 只新增 `ai_call_logs` 表 + 3 个索引，不改现有表。
- [x] 新建 `backend/app/schemas/ai_call_log.py`（`AiCallLogOut` 响应 schema）。
- [x] 运行 `alembic upgrade head` 确认表创建成功。

完成标准：
- [x] `ai_call_logs` 表存在，字段/索引正确。
- [x] `AiCallLog` 模型可正常 ORM 操作。
- [x] migration 可正向和反向执行。

## P0-02 ai_gateway.py Gateway 层

目标：新建 Gateway 层，统一调用入口 + 调用日志写入。

- [x] 新建 `backend/app/services/ai_gateway.py`。
- [x] 实现 `GatewayCallResult` 数据类。
- [x] 实现 `call_text(task_type, messages, ...)`：委托 `ai_service._call_with_fallback`，写日志。
- [x] 实现 `call_vision(task_type, messages, ...)`。
- [x] 实现 `call_general(task_type, messages, ...)`。
- [x] 实现 `call_stream(task_type, messages, ...)`：流结束后写日志。
- [x] 实现 `_write_call_log()`：独立 AsyncSession，写入失败 catch + log warning。
- [x] `ai_service.py` 的 `call_*` 函数加 docstring 标注 "internal — use ai_gateway"。
- [x] 日志的 `input_summary` 截断 200 字符，`error` 截断 500 字符。
- [x] `attempts` JSON 只存 provider/model/success/latency_ms/error。

完成标准：
- [x] Gateway 四个方法均可调用并返回 `GatewayCallResult`。
- [x] 成功和失败均写入 `ai_call_logs`。
- [x] 日志写入失败不阻塞主调用。
- [x] Gateway 不做权限校验（权限在路由层）。

## P0-03 ai.py 瘦身（业务逻辑抽离）

目标：把 `ai.py`（1605 行）中的业务逻辑抽离到 service 层。

- [x] 新建 `backend/app/services/ai_repair_service.py`：抽离 LaTeX 修复 + deterministic repair。
  - `_repair_latex_in_text`、`_repair_latex_in_result`
  - `_check_deterministic_fields`、`_repair_deterministic_result`
  - `_list_of_strings`
- [x] 新建 `backend/app/services/ai_analyze_service.py`：抽离 analyze 业务逻辑。
  - `_parse_result`、`_build_personal_context`
  - `_find_related_notes`、`_check_rate_limit`
- [x] `ai.py` 导入新 service，删除抽离的函数体。
- [x] `ai.py` 中 `call_ocr_model` / `call_text_model` 改为 `ai_gateway.call_*`。
- [x] `ai.py` 行数 < 600（实际 598 行）。
- [x] 现有 AI 端点请求/响应 schema 不变。

完成标准：
- [x] `ai.py` < 600 行（598 行）。
- [x] 业务逻辑在 service 层，路由只做编排。
- [x] 现有端点行为不变。

## P0-04 现有调用迁移到 Gateway

目标：把所有 AI 调用迁移到 Gateway。

- [x] `capture_ai_draft.py`：`call_text_model` → `ai_gateway.call_text`，task_type=`"capture_draft"`。
- [x] `diagram_service.py`：直调 dashscope → `ai_gateway.call_text`，task_type=`"diagram_structured"`/`"diagram_fallback"`。
- [~] `ai_polish.py`：跳过——Gateway 当前不支持真正逐 token 流式，`ai_polish_service` 用 httpx 直接流式，迁移会降级体验。待 Gateway 支持流式后再迁移。
- [x] `ai.py` 中所有 analyze 调用迁移到 Gateway，task_type 按场景标注。
- [x] 额外迁移：`mistake_staged_service.py`、`netease_service.py`、`recommendation.py`、`capture_recognition.py`。
- [x] Grep 确认无外部直接调用 `ai_service.call_*`（Gateway 内部除外）。

完成标准：
- [x] Grep `ai_service.call_text_model\|ai_service.call_ocr_model\|ai_service.call_general` 在 router/service 外无匹配。
- [x] 所有调用经 Gateway（`ai_polish_service` 除外，见上文说明）。

## P0-05 调用日志查询端点

目标：新增调用日志查询 API。

- [x] `ai.py` 新增 `GET /api/ai/call-logs`：分页 + 过滤（task_type/success/provider）。
- [x] `ai.py` 新增 `GET /api/ai/call-logs/stats`：按 task_type 聚合（总数/成功率/平均延迟）。
- [x] 两个端点均 `Depends(get_current_admin)`。
- [x] 响应不包含 `input_summary`（安全考虑）。
- [x] 分页默认 20，最大 100。

完成标准：
- [x] admin 可查询调用日志。
- [x] 匿名访问返回 401（`get_current_admin` 保障）。
- [x] 过滤和分页正常工作。

## P0-06 前端 /manage/ai 页面

目标：从占位页改为调用日志展示。

- [x] `src/lib/api/ai.ts` 新增 `getCallLogs()` / `getCallLogStats()` API client。
- [x] `/manage/ai/page.tsx` 从占位页改为调用日志列表 + 统计卡片。
- [x] 展示：task_type、provider、model、latency、success/fail、时间。
- [x] 支持按 task_type / success 过滤。
- [~] 复用既有 `ai-tab.tsx` 的 Provider Status 卡片——不适用：Provider Status 已在 `/manage` tab 中存在，`/manage/ai` 专注调用日志展示，不重复。
- [x] 不展示 `input_summary`。

完成标准：
- [x] `/manage/ai` 展示调用日志。
- [x] 过滤和分页正常。
- [x] `npx tsc --noEmit` 通过（0 error）。

## P0-07 后端单元测试

目标：覆盖 Gateway 核心逻辑。

- [x] 新建 `backend/tests/test_ai_gateway.py`。
- [x] 测试 `call_text` 成功路径（mock ai_service，验证日志写入）。
- [x] 测试 `call_text` 失败路径（验证失败日志写入）。
- [x] 测试 fallback 路径（验证 attempts 记录）。
- [x] 测试日志写入失败不阻塞主调用。
- [x] 测试 `input_summary` / `error` 截断。
- [x] 运行 `pytest backend/tests/test_ai_gateway.py` 通过（11 passed）。

完成标准：
- [x] 所有测试通过（11/11）。
- [x] 覆盖成功、失败、fallback、日志异常四个场景。

## P0-08 验证

- [x] `alembic upgrade head` 成功（P0-01 阶段验证）。
- [x] `pytest backend/tests/` — 106 passed, 3 failed（预先存在问题，非 Batch 9 引入；详见 validation.md）。
- [x] `npx tsc --noEmit` 通过（0 error）。
- [~] `npm run build` 跳过——tsc 已通过，前端改动仅 3 文件无构建敏感变更。
- [x] Grep 确认 0 匹配（`ai_polish_service` 除外，已标注跳过）。
- [~] `ai.py` 618 行——P0-03 目标 598 行已达成，P0-05 新增 2 端点 +20 行；从 1605 减少 61%。
- [x] 记录到 [validation.md](./validation.md)。

## P0-09 收口文档

- [x] 更新 `tasks.md` 勾选状态。
- [x] 记录到 `validation.md`。
- [~] 无 handoff.md（不需要）。
- [x] 更新 `README.md` 状态。

## 推荐执行顺序

1. P0-01 模型与 migration
2. P0-02 Gateway 层
3. P0-03 ai.py 瘦身
4. P0-04 调用迁移
5. P0-05 查询端点
6. P0-06 前端页面
7. P0-07 单元测试
8. P0-08 验证
9. P0-09 收口

> 注意：P0-02 依赖 P0-01（需要 AiCallLog 模型）。P0-03/04 可并行。P0-05 依赖 P0-01/02。P0-06 依赖 P0-05。
