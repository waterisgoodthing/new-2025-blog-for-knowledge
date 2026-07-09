# Batch 12 — AI Provider Routing / Cost / Stability

## 目标

创建 Batch 12 多供应商、路由、成本与稳定性治理任务组。

本轮先创建 workflow 文档和任务设计；随后在用户批准后实施 Phase 12A Typed Provider/Routing Policy 最小内核，继续实施 Phase 12B Usage / Cost 可观测性最小聚合，完成 Phase 12C Provider Health / 降级治理设计审查并实施 12C 最小 Health Snapshot API，最后实施 Phase 12D 管理端只读面板。

本轮仍不新增 migration、不新增数据库表、不做真实 provider 调用、不提供在线编辑。

## 当前状态

- Batch 11 AI Run 审计与人工流转已通过并关闭。
- RISK-B11-001 已关闭：Run 管理页、分页、accept/reject、revision 409、匿名 401、敏感字段检查已验证。
- RISK-B11-004 已关闭：真实同步 provider 端到端 Run 审计已验证。
- RISK-B11-003 已关闭：正式可审计 AI 生成已脱离伪流式 stream endpoint；旧 stream endpoint 仅 deprecated / compatibility-only。
- backend full suite 已恢复全绿，当前验证结果：`226 passed / 2 warnings`。
- 当前 AI 基础能力包括 AI Gateway、`ai_call_logs`、`ai_runs`、Prompt Registry、Message Builder、Prompt Standard、Validator、Run 审计与人工流转，以及 `/manage/ai` provider / usage / health 只读治理面板。

## 触及域

- backend AI shared infrastructure
- manage / AI admin read-only panel
- workflow documentation

## Batch 12 定位

Batch 12 建立 AI 平台治理层，只做工程化治理，不做 Prompt 后台。

核心方向：

- 多供应商治理
- 模型路由规则
- provider health check
- fallback 策略显式化
- 调用成本与用量统计
- 预算与限额保护
- 稳定性监控
- 降级策略

不处理：

- 完整 stream 生命周期审计
- Prompt 管理后台
- Prompt A/B 测试
- Prompt 热更新
- Prompt 效果评测平台
- 业务推荐算法
- 正式实体自动写入

## 文件

- [requirements.md](./requirements.md)
- [design.md](./design.md)
- [tasks.md](./tasks.md)
- [checklist.md](./checklist.md)
- [risks.md](./risks.md)
- [validation.md](./validation.md)
- [handoff.md](./handoff.md)

## 当前结论

本轮 P0-01 至 P0-15 已完成设计审查阶段；Phase 12A Typed Provider/Routing Policy 最小实现已完成；Phase 12B Usage / Cost 可观测性最小聚合已完成；Phase 12C Provider Health / 降级治理设计审查与最小 Health Snapshot API 已完成；Phase 12D 管理端只读面板已完成。

设计审查结论：

- Phase 12A 已采用代码级 typed policy：`ProviderPolicy`、`ModelPolicy`、`RoutingPolicy`。
- Phase 12A 未新增 migration 或数据库表。
- Phase 12B 已基于 `ai_call_logs` 完成无表聚合，并新增 admin-only `/api/ai/call-logs/usage-cost`。
- token/cost 当前仍为 `unknown/null`，不伪造。
- 12C 已新增 admin-only `/api/ai/provider-health-snapshot`，基于 `ai_call_logs` recent snapshot；真实 health probe、health event、熔断和临时禁用仍未实施。
- `/manage/ai` 已展示 provider 配置状态、usage/cost snapshot、health snapshot，并保留原调用统计/日志。
- 12D 面板仅只读展示，不提供 provider/routing/cost/health 在线编辑。
- 不重新启用正式业务 stream 生成链路。
