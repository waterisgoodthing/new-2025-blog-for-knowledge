# 需求与验收

- REQ-FINAL-01：四文件后端组合测试在同一隔离策略下无 `Future attached to a different loop`、`another operation is in progress`、未 await cleanup 或跨 loop engine 错误。
- REQ-FINAL-02：独立 learning/activity/storage 故障均有持久化回归测试并通过。
- REQ-FINAL-03：正常 commit、异常 rollback、关闭和后续查询恢复均有真实 dependency 测试。
- REQ-FINAL-04：viewport 不再禁用用户缩放；移动端浏览器检查通过。
- REQ-FINAL-05：真实隔离数据库只读确认 `current=022`、`heads=022`；后端组合套件全绿。
- REQ-FINAL-06：前端完整定向套件、TypeScript、生产构建和 390×844/1280×800/1440×900 证据通过。
- REQ-FINAL-07：closure-fix-2 的 tasks/validation 测试数量、状态、数据库 revision、浏览器截图和阻断结论与本批次实际输出一致。

## 明确不包含

不新增 migration，不自动执行 migration，不修改生产配置，不部署、不推送、不触碰源库；若没有现成 022 隔离目标，任务停在 `BLOCKED` 并报告需要的外部状态。
