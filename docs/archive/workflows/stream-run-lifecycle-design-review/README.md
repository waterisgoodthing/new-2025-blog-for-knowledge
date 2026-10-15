# RISK-B11-003 Stream Lifecycle Design Review

## 任务目标

本任务组只做真实 SSE / stream 生命周期的设计审查，回答现有 stream endpoint
是否仍有必要、是否应接入 `ai_runs`、异常与断开应如何审计，以及 partial output
是否应持久化。

## 触及域

- 后端：AI shared infrastructure、`ai_runs` 审计边界。
- 前端：`write-mistake` 调用现状与 `manage/ai/runs` 潜在影响。
- 本轮实际写入：仅本 workflow 文档。

## 当前状态

**已关闭。关闭方式：正式可审计生成链路迁出伪流式 stream endpoint；旧 stream endpoint 保留为 deprecated / compatibility-only。**

- Batch 11 与 RISK-B11-004 的既有关闭结论不变。
- RISK-B11-003 已按 Stream Endpoint Simplification Patch 关闭。
- 本关闭不等于完成真实 provider token streaming 生命周期审计。
- 完整 provider token streaming、client disconnect、partial artifact 等能力已转入后置 backlog。
- 未调用真实 provider，未验证真实 provider token stream 生命周期。

## 核心结论

1. 两个 SSE endpoint 均有当前调用点，但只提供阶段性进度事件，不提供 provider
   逐 token 输出。
2. 已采用方案 B：不把现有伪流式 endpoint 扩展为正式 Stream Run 审计链路；正式可审计生成使用注册的非流式 task。
3. 两个 endpoint 及客户端正式链路已退化为普通非流式请求；只有未来确认逐 chunk 体验必须保留时，才单独审批真正 Stream Run Lifecycle Patch。
4. 不保存 partial output；若未来保留 stream，只在成功完成并通过解析后保存清理过的
   final output。
5. RISK-B11-003 已关闭，但 Batch 12 与最终文档不得据此宣称真实 provider token streaming 审计已完成。

## 文档导航

- [需求](requirements.md)
- [设计](design.md)
- [关闭任务](tasks.md)
- [审查清单](checklist.md)
- [风险](risks.md)
- [只读验证](validation.md)
- [交接](handoff.md)
