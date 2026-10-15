# Design Review

## 1. 现状结论

### Endpoint 与调用

| Stream endpoint | 调用位置 | 是否仍使用 | 是否必须保留 | 证据 |
|---|---|---:|---:|---|
| `POST /api/ai/analyze-stream` | `src/lib/api/ai.ts:96-169`，由 `src/app/write-mistake/components/mistake-form.tsx:154-199` 的图片上传流程调用 | 是 | 否；当前体验可由非流式请求加 loading 状态替代 | router 使用 `StreamingResponse`；client 读取 SSE；UI 只消费 `received/progress/result/error/done` |
| `POST /api/ai/analyze-text-stream` | `src/lib/api/ai.ts:171-235`，由 `src/app/write-mistake/components/mistake-form.tsx:228-256` 调用 | 是 | 否；当前体验可由非流式请求加 loading 状态替代 | 同上，未见逐 token 内容消费 |

`src/app/manage/ai` 与 `src/app/manage/ai/runs` 在当前 App Router 结构中不存在；
实际路径为 `src/app/manage/(workspace)/ai` 与其 `runs/` 子路由。

### 真实流式程度

`stream_analyze_events()` 先发送阶段事件，随后 `await gateway_call(...)`，provider
调用结束后才解析并发送一个完整 `result`。没有 provider chunk 被向客户端转发。
`ai_gateway.call_stream()` 自身也明确是同步包装，当前 endpoint 实际调用的还是
`call_vision` / `call_text`，并未调用 `call_stream()`。

因此现状是“使用 SSE 传送阶段进度的同步分析”，不是逐 token stream。

## 2. 方案比较

### 方案 A：接入 `ai_runs`

优点：

- endpoint、provider、parser 与交付阶段可形成统一审计记录。
- `/manage/ai/runs` 可观察中断和解析失败。

代价与风险：

- 现有 generator 传入 `analyze_mistake_stream` /
  `analyze_text_stream`，二者不在 `AiTaskType`，Gateway 的 `_start_run_record()`
  会跳过 Run 创建。
- 若外层再创建 Run，内层注册 task 也创建 Run，容易形成重复 Run 或父子语义不清。
- 当前状态约束只有 `running/succeeded/failed`，没有 `created`、`cancelled` 或
  `interrupted`。
- 当前没有 `ai_run_artifacts` 模型或表；新增 artifact 会显著扩大范围。
- 为阶段性 progress SSE 建立完整 stream 编排，收益低于复杂度。

### 方案 B：暂不接入 `ai_runs`（推荐）

- 现有 SSE endpoint 继续作为兼容体验能力，但不作为正式 AI Run 审计链路。
- 所有需要正式审计的生成必须使用注册的 `AiTaskType` 非流式路径。
- 后续单独审批一个实施批，优先把错题编辑器切换到 `/analyze` 与
  `/analyze-text`，以普通 loading/阶段文案替代 SSE；确认无调用后再退役 stream
  endpoint。
- 只有产品明确要求逐 token / chunk 体验时，才实施真正的 Stream Run Lifecycle
  Patch。

推荐原因：当前 UI 没有逐 token 依赖，provider 也没有真实 stream；先退化为非流式
可复用 Batch 11 已验证的 Run finalize 合同，避免为伪流式引入新状态、migration、
artifact 表和敏感数据面。

## 3. 若未来选择方案 A：最小状态机

### 概念状态与最小持久化映射

```text
created (请求已接收，尚未持久化)
  -> running (Run 已提交)
      -> succeeded (provider + parser + final delivery 已完成)
      -> failed (provider error / parser error / generator exception)
      -> interrupted (client disconnect / cancellation)
```

为避免 migration，第一版可把概念 `interrupted` 持久化为：

```text
status = failed
error_code = stream_interrupted
```

`created` 是提交前瞬态，不进入数据库。若业务必须直接筛选 cancelled/interrupted，
才新增状态枚举与 migration；不建议在最小补丁中这样做。

### 转换合同

| 事件 | 检测方式 | Run 结果 | validation_status | review_status |
|---|---|---|---|---|
| start | request 校验通过后、首个 SSE event 前 | `running` | `pending` | 依 task 设置 `pending` 或 `not_required` |
| chunk/progress | yield 成功 | 不改变状态，不落 partial | `pending` | 不变 |
| provider error | Gateway 返回失败或抛出 provider 分类异常 | `failed`, `provider_error` | `not_applicable` | `not_required` |
| parser error | provider 已完成，但 repair/parse/schema 失败 | `failed`, `parser_error` | `failed` | `not_required` |
| generator exception | generator 外层捕获非取消异常 | `failed`, `stream_generator_error` | 解析前为 `not_applicable`，解析后按结果 | `not_required` |
| client disconnect | `await request.is_disconnected()`，并捕获 `asyncio.CancelledError`；两者均须在 `finally` 收口 | 概念 `interrupted`；最小映射为 `failed/stream_interrupted` | 未完成解析为 `not_applicable` | `not_required` |
| normal finalize | final result 已清理、解析成功，且 generator 正常完成 | `succeeded` | `passed`；无结构校验时 `not_applicable`，不可使用含糊的 `skipped` 新值 | 按 task；可人工审查则 `pending`，否则 `not_required` |

关键语义：provider 成功不等于 stream succeeded。只有 parser 成功并完成 final
事件交付后，Run 才能 `succeeded`。

## 4. Partial output 决策

选择方案 A：**不保存 partial output**。

- 只在流结束、parser 成功后保存 final output。
- client disconnect 时只记录安全的中断元数据，不保存已产生片段。
- 不按 chunk 更新数据库，不创建 partial artifact。

理由：当前根本没有 provider partial chunk；即使未来有，持久化会扩大个人题目内容与
模型原文的敏感数据面，并引入写放大、清理、保留期和并发一致性问题。

## 5. Final artifact 设计

当前模型只有 `ai_runs.output_data`，没有 `ai_run_artifacts`。最小实施应继续使用
`output_data`，不新增 artifact 表或 migration。

若未来另行批准 artifact 模型，建议合同为：

- `artifact_type`: `stream_final_output`
- `content_json`: parser 成功后的结构化结果
- `content_text`: 默认 `null`，避免保留 provider 原文
- `schema_name`: 对应注册 schema；手工 parser 可使用明确版本名，例如
  `AnalyzeResponseV1`
- `validation_status`: `passed` 或 `not_applicable`
- `ai_run_artifacts`: 仅在该表经独立需求和 migration 批准后使用
- 详情页：只允许管理员查看经递归清理的 final result

写入前复用并加强 `sanitize_run_output()`；除键名过滤外，还需防止嵌套 header、
Bearer 值、绝对路径、data URL 与原始输入被包装在普通字段中。

严禁保存 API Key、authorization、cookie、secret、token、storage_key、绝对路径、
data URL、完整 replay input、图片 base64 或敏感原文。

## 6. 前端影响

- 当前两个 stream API 都被 `MistakeForm` 使用，显示阶段文案并支持
  `AbortController`。
- UI 不消费逐 token/chunk；可改用普通请求与现有 `analyzing/phaseText` 状态。
- 方案 B 不需要向编辑器显示 `run_id`。
- 后续替换时，网络中断和用户取消应给出不同提示；当前 AbortError 被静默返回。
- 方案 B 不应在 `/manage/ai/runs` 展示这些兼容 SSE 请求，也不需要 stream 标签。
- 若未来选择方案 A，Run 会自然进入现有列表；若沿用 `failed +
  stream_interrupted`，无需新状态标签，但详情应显示安全的 error code。只有新增
  `interrupted` 枚举时才需要 API 类型、筛选器和状态文案联动修改。

## 7. 实施边界建议

首选后续实施批：

1. 将两个客户端调用切换到已注册的非流式 endpoint。
2. 保留明确的 loading、取消与错误体验。
3. 增加客户端与后端合同测试。
4. 确认无调用后再决定删除或弃用两个 SSE endpoint。

备选真正流式实施批必须独立审批，并包含 generator `finally`、断连测试、parser
终态、Run 去重与敏感数据检查。
