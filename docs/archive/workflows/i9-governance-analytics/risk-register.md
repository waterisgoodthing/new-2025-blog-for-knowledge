# I9 风险登记

| 风险 | 状态 | 处置 |
|---|---|---|
| 模拟数据伪造完成 | CLOSED | 指标来自治理 API 与只读 SQL；任务无持久化模型时明确 unavailable |
| AI 绕过人工确认 | CLOSED | AI 页面只读 `ai_runs`，页面明确人工确认不会直接写正式对象 |
| provider/凭证依赖 | CLOSED | 未调用真实 provider；已有失败记录可见 |
| 前端全量 Capture 测试路由上下文失败 | OPEN / EXISTING | `invariant expected app router to be mounted`；不属于 I9，后续独立修复 |
| 后端 unittest 异步连接跨 event-loop | OPEN / EXISTING | Dashboard/FileWorkspace 组合出现 asyncpg loop 绑定错误；不以 I9 结论覆盖 |
