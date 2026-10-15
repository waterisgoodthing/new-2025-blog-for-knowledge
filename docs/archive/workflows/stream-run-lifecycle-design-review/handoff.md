# Handoff — B11-003 Stream Endpoint Simplification Patch

## 当前状态

本批已执行并完成：

```text
B11-003 Stream Endpoint Simplification Patch
```

stream endpoint 当前状态：

```text
deprecated / compatibility-only / removed from formal generation path
```

正式错题图片/文本 AI 生成已切换到：

- `POST /api/ai/analyze`
- `POST /api/ai/analyze-text`

不再由以下 endpoint 承担正式业务生成：

- `POST /api/ai/analyze-stream`
- `POST /api/ai/analyze-text-stream`

## 是否建议继续实施完整 Stream Run Lifecycle Patch

当前不建议立即实施。

原因：

- 当前 UI 没有逐 token 内容渲染需求。
- 原 stream endpoint 只是阶段性 SSE / 伪流式进度事件。
- 正式可审计生成已经走非流式 Run 链路。
- 实现完整 stream lifecycle 会引入断连、generator 终态、partial artifact、状态枚举等额外复杂度。

如未来重新需要真正 provider streaming，应另起独立 workflow，并重新审批。

## 推荐后续范围

短期后续只建议做轻量清理：

1. 观察是否还有外部旧客户端调用 deprecated stream endpoint。
2. 若无兼容需求，再单独批准删除 stream wrapper 与后端 deprecated route。

不建议混入：

- Batch 12。
- 成本统计。
- 多供应商路由。
- Prompt 后台。
- A/B 测试。
- partial output artifact。

## Partial output

不建议保存 partial output。

本批未保存 partial output，也未新增 artifact 表或 artifact 写入。

## Migration / 状态枚举

本批不需要新增 migration。

本批不需要修改 `ai_run` 状态枚举。

原因：推荐路径是让正式生成走现有非流式 Run 链路；旧 stream endpoint 仅兼容保留，
不引入 `cancelled` / `interrupted` 一等状态。

## 前端改动

已完成：

- `MistakeForm` 图片分析改用 `analyzeMistake()`。
- `MistakeForm` 文本分析改用 `analyzeText()`。
- 非流式 API wrapper 支持可选 `AbortSignal`。
- loading / success / error / retry 体验保留为普通请求状态。

不需要在 `/manage/ai/runs` 新增 stream 状态标签。

## 后端改动

已完成：

- `POST /api/ai/analyze-stream` 标记 deprecated。
- `POST /api/ai/analyze-text-stream` 标记 deprecated。
- compatibility stream route 内部复用注册 task type：
  - `AiTaskType.ANALYZE_MISTAKE`
  - `AiTaskType.ANALYZE_TEXT`

未完成也不应在本批完成：

- 真正 provider token streaming。
- SSE client disconnect 终态。
- stream generator `finally` Run lifecycle。
- partial artifact。

## 验证摘要

通过：

- `cd backend && .venv/bin/python -m pytest tests/test_stream_endpoint_simplification.py tests/test_ai_gateway.py -ra`
- `npx tsc --noEmit`
- `npm run build`
- `git diff --check`
- mock provider + 真实 Gateway / DB 写入验证 `ai_runs` 与 `ai_call_logs`

Full Suite Regression Triage：

- 已定位 `test_unconfirmed_draft_does_not_enter_review_queue` 失败根因：测试未按
  `list_due_items()` 当前 `(ReviewItem, Mistake)` tuple 合同读取 id。
- 已通过最小测试修复恢复业务断言。
- `cd backend && .venv/bin/python -m pytest tests/test_mistake_review_service.py -ra`：
  `5 passed`
- 完整 backend suite：`214 passed, 2 warnings`

## 是否阻塞 Batch 12

不阻塞 Batch 12。

但进入 Batch 12 时应保留以下事实：

- RISK-B11-003 关闭方式是“正式链路迁出伪流式 endpoint”，不是“完整 provider stream
  lifecycle 已实现”。
- deprecated stream endpoint 仍存在，状态为 compatibility-only。
- 如未来重新启用正式 streaming，需要新的 Stream Run Lifecycle workflow。
