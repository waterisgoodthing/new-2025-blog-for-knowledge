# Tasks — Stream Endpoint Simplification Closure

> 状态：**已完成并关闭**
>
> 本任务组关闭 RISK-B11-003 的方式是：正式可审计 AI 生成链路迁出伪流式 stream endpoint；旧 stream endpoint 保留为 deprecated / compatibility-only。此关闭不等于真实 provider token streaming 生命周期审计完成。

## Completed Scope

- [x] 审计 `analyze-stream` / `analyze-text-stream` endpoint、API client、前端调用与测试引用。
- [x] 比较 Stream Run Lifecycle 接入方案与正式链路非流式迁出方案。
- [x] 选择非流式迁出方案作为当前关闭路径。
- [x] 将正式错题 AI 生成链路改为已注册的非流式 `analyze` / `analyze-text` task。
- [x] 将旧 stream endpoint 标记为 deprecated / compatibility-only。
- [x] 兼容 stream endpoint 复用已注册 task type，避免未注册 stream task 绕过 Run/log 记录。
- [x] 验证 mock provider + 真实 Gateway / DB 写入 `ai_runs` 与 `ai_call_logs`。
- [x] 记录不声明真实 provider token streaming、client disconnect、partial output 或 generator exception 完整审计。
- [x] 更新 `audit.md`、`validation.md`、`handoff.md` 与本任务清单。

## Deferred Backlog

- [ ] 完整 provider token streaming 生命周期审计：后置，不阻塞当前系统冻结。
- [ ] client disconnect / generator exception 终态验证：后置，不阻塞当前系统冻结。
- [ ] partial output artifact 设计与清理策略：后置，不阻塞当前系统冻结。
- [ ] 真实 provider stream 补证：后置，不得用 mock 验证替代。
