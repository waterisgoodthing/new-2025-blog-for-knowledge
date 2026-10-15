# Validation — B11-003 Stream Endpoint Simplification Patch

## 验证性质

本轮执行的是 **B11-003 Stream Endpoint Simplification Patch**，不是完整
provider token streaming 生命周期实现。

本轮目标是把正式业务生成链路从伪流式 SSE endpoint 迁出，统一走已注册、已接入
`ai_runs` / `ai_call_logs` 的非流式 Run 链路。旧 stream endpoint 保留为
deprecated compatibility-only。

未执行、未声称：

- 未实现真实 provider token stream。
- 未保存 partial output。
- 未进入 Batch 12。
- 未使用 `AUTH_BYPASS` 做验收。

## Stream 调用点审计命令

```bash
git status --short
rg -n "analyze-stream|analyze-text-stream|StreamingResponse|EventSource|text/event-stream" backend src docs/workflows/stream-run-lifecycle-design-review
rg -n "analyzeMistakeStream|analyzeTextStream|analyze\\(|analyzeText\\(|stream" src/lib/api/ai.ts src/app/write-mistake backend/app/routers/ai.py backend/app/services/ai_analyze_service.py backend/app/services/ai_gateway.py backend/tests src -g '!node_modules'
rg -n "analyzeMistakeStream|analyzeTextStream|/api/ai/analyze-stream|/api/ai/analyze-text-stream|StreamingResponse|EventSource|text/event-stream" backend src docs/workflows/stream-run-lifecycle-design-review
```

## 审计结果

### 后端 endpoint

| endpoint | 文件 | 当前状态 |
|---|---|---|
| `POST /api/ai/analyze` | `backend/app/routers/ai.py` | 正式图片分析链路，使用 `AiTaskType.ANALYZE_MISTAKE` |
| `POST /api/ai/analyze-text` | `backend/app/routers/ai.py` | 正式文本分析链路，使用 `AiTaskType.ANALYZE_TEXT` |
| `POST /api/ai/analyze-stream` | `backend/app/routers/ai.py` | 保留但 `deprecated=True`，compatibility-only |
| `POST /api/ai/analyze-text-stream` | `backend/app/routers/ai.py` | 保留但 `deprecated=True`，compatibility-only |

补丁后，compatibility-only stream endpoint 内部不再传入未注册的
`analyze_mistake_stream` / `analyze_text_stream` task_type；它们复用已注册的
`AiTaskType.ANALYZE_MISTAKE` / `AiTaskType.ANALYZE_TEXT`，避免兼容调用继续绕过
Gateway Run/log task 注册。

### 前端调用点

| 调用点 | 补丁前 | 补丁后 |
|---|---|---|
| `src/app/write-mistake/components/mistake-form.tsx` 图片上传分析 | `analyzeMistakeStream()` → `/api/ai/analyze-stream` | `analyzeMistake()` → `/api/ai/analyze` |
| `src/app/write-mistake/components/mistake-form.tsx` 文本粘贴分析 | `analyzeTextStream()` → `/api/ai/analyze-text-stream` | `analyzeText()` → `/api/ai/analyze-text` |
| `src/lib/api/ai.ts` | 保留 stream wrapper | stream wrapper 仍保留兼容；正式页面不再引用 |

`rg` 复查显示：

- `src/app/write-mistake/components/mistake-form.tsx` 不再引用
  `analyzeMistakeStream` / `analyzeTextStream`。
- `/api/ai/analyze-stream` / `/api/ai/analyze-text-stream` 仍只存在于 API wrapper、
  后端 deprecated route、测试和 workflow 文档证据中。
- 未发现 `EventSource` 调用。

另见 `backend/app/routers/ai_polish.py` 仍有 `text/event-stream`，但它属于写笔记
润色/标签建议能力，不属于本轮 `analyze-stream` / `analyze-text-stream` 风险关闭范围。

## 替代路径

正式错题生成路径现在为：

```text
MistakeForm
  -> src/lib/api/ai.ts analyzeMistake / analyzeText
  -> POST /api/ai/analyze / POST /api/ai/analyze-text
  -> ai_gateway.call_vision / ai_gateway.call_text
  -> ai_runs + ai_call_logs
  -> AnalyzeResponse
  -> MistakeForm.applyResult()
```

前端保留普通 loading 文案：

- 上传图片后：`正在上传图片...` → `正在调用 AI 模型分析...`
- 粘贴文本后：`正在分析文本...` → `正在调用 AI 模型分析...`

正式结果不再依赖 SSE `received/progress/result/done` 事件完成。

## ai_runs / ai_call_logs 落库验证

执行了一次 mock provider + 真实 Gateway / 真实数据库写入验证：

```bash
cd backend && .venv/bin/python - <<'PY'
# patch app.services.ai_gateway._call_with_fallback
# await call_text(AiTaskType.ANALYZE_TEXT, ..., input_summary="b11-003-stream-simplification-db-proof")
# query AiRun and AiCallLog by task_type + input_summary
PY
```

输出摘要：

```text
{
  'gateway_success': True,
  'run_task_type': 'analyze_text',
  'run_status': 'succeeded',
  'run_validation_status': 'not_applicable',
  'run_output_has_api_key': False,
  'run_output_has_authorization': False,
  'run_output_has_storage_key': False,
  'run_data_url_redacted': True,
  'call_log_task_type': 'analyze_text',
  'call_log_success': True,
  'call_log_provider': 'mock'
}
```

结论：

- `ai_runs` 已产生记录。
- `ai_call_logs` 已产生记录。
- Run 状态为 `succeeded`。
- 由于 `analyze_text` 当前是手动 parse schema，Run `validation_status` 为
  `not_applicable`，符合现有 Gateway 合同。
- `api_key`、`authorization`、`storage_key` 未进入 Run output。
- data URL 被清理为 `[redacted-data-url]`。

该验证未调用真实 provider，避免成本与外部不稳定性；未使用 `AUTH_BYPASS`。

## 自动化验证

### 针对性后端测试

```bash
cd backend && .venv/bin/python -m pytest tests/test_stream_endpoint_simplification.py tests/test_ai_gateway.py -ra
```

结果：

```text
17 passed, 2 warnings in 0.50s
```

新增/覆盖重点：

- stream endpoint 注册为 deprecated compatibility route。
- 正式 `/api/ai/analyze-text` 使用 `AiTaskType.ANALYZE_TEXT`。
- 正式 `/api/ai/analyze` 使用 `AiTaskType.ANALYZE_MISTAKE`。
- stream compatibility route 复用已注册 task type。
- `AiTaskType.ANALYZE_TEXT` 通过 Gateway 写 call log 并 finalize Run。

### 完整后端测试

#### 初次 B11-003 patch 后结果

初次执行完整 suite 时出现 1 个非 stream 失败：

```text
tests/test_mistake_review_service.py::MistakeReviewServiceTest::test_unconfirmed_draft_does_not_enter_review_queue
AttributeError: 'tuple' object has no attribute 'id'
```

#### Full Suite Regression Triage

复现命令：

```bash
cd backend && .venv/bin/python -m pytest tests/test_mistake_review_service.py::MistakeReviewServiceTest::test_unconfirmed_draft_does_not_enter_review_queue -vv
```

复现结果：失败稳定复现。

根因：

- `backend/app/services/review_item_service.py::list_due_items()` 的当前服务合同返回
  `(ReviewItem, Mistake)` tuple 列表。
- `backend/app/routers/review_items.py` 正在按该合同执行
  `for item, mistake in await review_item_service.list_due_items(db)`。
- 失败测试直接把返回元素当 `ReviewItem` 使用：`item.id`，因此遇到 tuple。
- 未发现 `(items, total)` 分页模式污染 review queue。
- 未发现共享数据库残留导致异常结构。
- 不是 B11-003 Stream Endpoint Simplification Patch 引入。

修复方式：

- 仅更新 `backend/tests/test_mistake_review_service.py`。
- 新增测试 helper `_review_item_ids()`，从 `(ReviewItem, Mistake)` tuple 中提取
  `ReviewItem.id`。
- 保持业务断言不变：未确认 draft 不得改变 due review queue。
- 未跳过、xfail、删除测试，未清空业务数据。

局部验证：

```bash
cd backend && .venv/bin/python -m pytest tests/test_mistake_review_service.py::MistakeReviewServiceTest::test_unconfirmed_draft_does_not_enter_review_queue -vv
```

结果：

```text
1 passed
```

```bash
cd backend && .venv/bin/python -m pytest tests/test_mistake_review_service.py -ra
```

结果：

```text
5 passed
```

最终完整 suite：

```bash
cd backend && .venv/bin/python -m pytest tests/ -ra
```

结果：

```text
214 passed, 2 warnings
```

### 前端类型检查

```bash
npx tsc --noEmit
```

结果：通过。

### 前端构建

```bash
npm run build
```

结果：通过。

构建输出包含既有提示：

- `baseline-browser-mapping` 数据超过两个月。
- Node `module.register()` deprecation warning。

未发现由本轮改动引入的构建失败。

### Diff 检查

```bash
git diff --check
```

结果：通过。

## 前端体验验证结论

基于类型检查、生产构建与代码路径审查：

- 原图片上传分析仍调用正式 AI 分析并填充表单。
- 原文本粘贴分析仍调用正式 AI 分析并填充表单。
- loading 从 SSE 分段事件退化为普通 loading 状态。
- 成功 toast 保留。
- 失败 toast 保留。
- AbortSignal 已传入非流式 `apiFetch`，取消行为不再依赖 SSE reader。
- 正式结果不再依赖 SSE 分段事件。

本轮未进行浏览器人工点击截图；未声称真实浏览器交互验收已完成。

## 敏感字段检查

本轮未新增 partial output 持久化。

落库验证确认 Run output 清理规则仍生效：

- 未保存 `api_key`
- 未保存 `authorization`
- 未保存 `storage_key`
- data URL 被 redacted

代码审查未发现新增保存 `replay_input`、绝对路径、cookie、secret、token 或完整图片
base64 的路径。

## 结论

B11-003 的目标路径已经完成：

- 正式错题图片/文本生成链路已脱离 `/api/ai/analyze-stream` 和
  `/api/ai/analyze-text-stream`。
- 正式生成统一走已注册非流式 Run 链路。
- 旧 stream endpoint 保留为 deprecated compatibility-only，不再作为正式业务生成主链路。
- 不保存 partial output。
- Run/log 落库与 output 清理已有证据。
- Full Suite Regression Triage 后 backend full suite 已恢复全绿：`214 passed,
  2 warnings`。
