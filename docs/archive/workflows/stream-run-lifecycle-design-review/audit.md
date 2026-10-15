# Audit — RISK-B11-003

## 审计对象

风险：

```text
RISK-B11-003：真实 SSE / stream 生命周期未完整审计
```

本批批准方案：

```text
B11-003 Stream Endpoint Simplification Patch
```

目标不是实现完整 Stream Run Lifecycle，而是消除正式业务生成链路对伪流式 SSE
endpoint 的依赖，让正式可审计 AI 生成统一走已接入 `ai_runs` 的非流式 task。

## 审计结论

RISK-B11-003 本批可关闭，关闭方式为：

```text
正式业务生成链路已从伪流式 stream endpoint 迁出；
旧 stream endpoint 被降级为 deprecated compatibility-only；
正式可审计 AI 生成走非流式 Run 链路。
```

这不是对真实 provider streaming 生命周期的完成声明。

## 关闭依据

### 1. 正式前端调用已迁出 stream endpoint

`src/app/write-mistake/components/mistake-form.tsx`：

- 图片上传分析由 `analyzeMistakeStream()` 改为 `analyzeMistake()`。
- 文本粘贴分析由 `analyzeTextStream()` 改为 `analyzeText()`。

正式调用目标变为：

- `POST /api/ai/analyze`
- `POST /api/ai/analyze-text`

不再依赖：

- `POST /api/ai/analyze-stream`
- `POST /api/ai/analyze-text-stream`

### 2. 旧 stream endpoint 已降级

`backend/app/routers/ai.py`：

- `POST /api/ai/analyze-stream` 标记为 `deprecated=True`。
- `POST /api/ai/analyze-text-stream` 标记为 `deprecated=True`。

两者保留为 compatibility-only，不作为正式可审计生成主链路。

### 3. 兼容 stream task_type 不再使用未注册 stream 名称

旧 endpoint 内部不再传入：

- `analyze_mistake_stream`
- `analyze_text_stream`

改为复用：

- `AiTaskType.ANALYZE_MISTAKE`
- `AiTaskType.ANALYZE_TEXT`

这样即使兼容 endpoint 被旧客户端误用，其 provider 调用也不会继续因为未知
task_type 绕过已注册 task 的 Gateway Run/log 记录。

### 4. ai_runs / ai_call_logs 有落库证据

使用 mock provider 走真实 Gateway 与真实数据库写入，验证：

- `ai_runs.task_type = analyze_text`
- `ai_runs.status = succeeded`
- `ai_runs.validation_status = not_applicable`
- `ai_call_logs.task_type = analyze_text`
- `ai_call_logs.success = True`
- output 清理移除了 `api_key`、`authorization`、`storage_key`
- data URL 被 redacted

该验证不使用真实 provider，不使用 `AUTH_BYPASS`。

### 5. 测试覆盖

新增/相关测试：

- `backend/tests/test_stream_endpoint_simplification.py`
- `backend/tests/test_ai_gateway.py`

针对性结果：

```text
17 passed
```

覆盖：

- stream route deprecated contract。
- 正式文本/图片分析使用注册非流式 task type。
- stream compatibility route 复用注册 task type。
- `analyze_text` 通过 Gateway 写 call log 并 finalize Run。

## 未声明事项

本审计不声明以下事项：

- 不声明实现了真正 provider token streaming。
- 不声明验证了真实 SSE client disconnect。
- 不声明保存了 partial output。
- 不声明 stream generator exception 已有完整 Run lifecycle。
- 不声明进入 Batch 12。

## 仍然存在但已降级的事实

`/api/ai/analyze-stream` 和 `/api/ai/analyze-text-stream` 仍存在，原因是兼容旧调用。

它们的状态是：

```text
deprecated / compatibility-only / removed from formal generation path
```

如果未来产品重新要求真正逐 token 或分段输出，应另建并审批 Stream Run Lifecycle
Patch，不应把当前 compatibility endpoint 当作已完成的 provider streaming。

## Full Suite Regression Triage

初次 B11-003 patch 后，完整 backend suite 暴露 1 个失败：

```bash
cd backend && .venv/bin/python -m pytest tests/ -ra
```

```text
213 passed, 1 failed, 2 warnings
```

失败项：

```text
tests/test_mistake_review_service.py::MistakeReviewServiceTest::test_unconfirmed_draft_does_not_enter_review_queue
AttributeError: 'tuple' object has no attribute 'id'
```

复现命令：

```bash
cd backend && .venv/bin/python -m pytest tests/test_mistake_review_service.py::MistakeReviewServiceTest::test_unconfirmed_draft_does_not_enter_review_queue -vv
```

根因：

- `list_due_items()` 当前返回 `(ReviewItem, Mistake)` tuple 列表。
- router 已按 tuple 合同展开。
- 测试按旧的 bare `ReviewItem` 形态读取 `.id`。
- 该失败不属于 B11-003 stream simplification 引入，也不是 AI Gateway、Prompt
  Registry、provider 配置或 stream 主链路污染。

修复：

- 仅修改 `backend/tests/test_mistake_review_service.py`。
- 测试新增 `_review_item_ids()`，按当前服务合同从 tuple 中提取 `ReviewItem.id`。
- 未跳过、xfail 或删除断言。
- 业务断言仍为：未确认 draft 不进入 review queue。

验证：

```bash
cd backend && .venv/bin/python -m pytest tests/test_mistake_review_service.py::MistakeReviewServiceTest::test_unconfirmed_draft_does_not_enter_review_queue -vv
cd backend && .venv/bin/python -m pytest tests/test_mistake_review_service.py -ra
cd backend && .venv/bin/python -m pytest tests/test_stream_endpoint_simplification.py tests/test_ai_gateway.py -ra
cd backend && .venv/bin/python -m pytest tests/ -ra
npx tsc --noEmit
npm run build
git diff --check
```

结果：

- 单个复现用例：`1 passed`
- `test_mistake_review_service.py`：`5 passed`
- B11-003 stream/Gateway 相关测试：`17 passed, 2 warnings`
- backend full suite：`214 passed, 2 warnings`
- `npx tsc --noEmit`：通过
- `npm run build`：通过
- `git diff --check`：通过

## 最终判定

RISK-B11-003：正式关闭。

关闭理由：正式可审计 AI 生成已经脱离伪流式 endpoint，统一走非流式 Run 链路；
旧 stream endpoint 仅保留 deprecated compatibility-only 状态，并且兼容调用不再使用
未注册 stream task_type。Full Suite Regression Triage 后，backend full suite 已恢复全绿。
