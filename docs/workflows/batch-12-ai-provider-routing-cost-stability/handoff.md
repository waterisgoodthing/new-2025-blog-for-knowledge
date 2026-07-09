# Handoff

## Phase 12A 当前状态

Phase 12A Typed Provider/Routing Policy 最小内核已完成最小实现。

已包含：

- 代码级 `ProviderPolicy` typed config。
- 代码级 `ModelPolicy` typed config。
- 代码级 `RoutingPolicy` typed config。
- routing resolver contract。
- 显式 fallback chain 解析。
- 兼容现有 Prompt Registry `preferred_provider` 默认值。
- 后端 contract tests / mock fallback order tests。

不包括：

- provider health check。
- 管理端 UI。
- Prompt 后台。
- migration。
- 数据库表。
- 真实 provider 调用。

## Phase 12B 当前状态

Phase 12B Usage / Cost 可观测性最小聚合已完成。

已包含：

- 基于 `ai_call_logs` 的无表聚合。
- 按日期、task_type、provider、model 聚合 call_count、success_count、failure_count、fallback_count、avg_latency_ms。
- admin-only `GET /api/ai/call-logs/usage-cost`。
- token/cost 字段 nullable，并明确 `usage_source=unknown`、`cost_source=unknown`。

不包括：

- `ai_usage_daily` 数据库表。
- migration。
- provider actual token usage 持久化。
- estimated cost 计算。
- 预算/限额 enforcement。
- 管理端页面。
- 真实 provider 调用。

## Phase 12C 当前状态

Phase 12C Provider Health / 降级治理已完成设计审查，并已实施最小 Health Snapshot API。

设计审查结论：

- 当前 `get_provider_status()` 只是配置状态，不是真实 health。
- 当前 fallback chain 不读取 provider health 状态。
- 当前没有 health event、连续失败阈值、冷却窗口、临时禁用或模型级降级。
- 12B 的 usage/cost 聚合可以展示业务失败率与 fallback 次数，但不等同 provider health。

已实施：

- 基于 `ai_call_logs` 的 provider/model recent health snapshot。
- admin-only `GET /api/ai/provider-health-snapshot`。
- `healthy/degraded/unknown` snapshot 状态。
- 匿名 401 与 safe schema 测试。

仍未实施：

- 真实 provider probe。
- `ai_provider_health_events` 表。
- migration。
- 自动熔断 / cooldown。
- provider/model 临时禁用。
- Gateway 根据 health 自动跳过 provider。

推荐后续实现：

1. `classify_provider_error()` safe 分类。
2. 代码级 `ProviderHealthPolicy` thresholds。
3. mock tests 验证 rate limit / timeout / 5xx / auth_error / parse_error 分类。
4. 可选内存级 cooldown，仅在明确批准后接入 Gateway routing。

## 是否需要 migration

本轮没有新增 migration。

原因：

- 当前用户硬约束明确禁止新增 migration。
- Phase 12A 的主要目标是把隐式 provider/fallback 策略显式化，代码级 typed policy 已足够支撑最小治理内核。
- 数据库化会扩大迁移、管理端权限、匿名暴露、防误编辑等问题，应作为后续独立审批项。

## 是否需要新增模型表

本轮没有新增模型表。

建议先用代码级 typed policy 表达：

- `ProviderPolicy`
- `ModelPolicy`
- `RoutingPolicy`

数据库表后置到单独审批的数据库化阶段，可选候选包括：

- `ai_provider_profiles`
- `ai_model_profiles`
- `ai_routing_rules`
- `ai_usage_daily`
- `ai_provider_health_events`

其中 `ai_usage_daily` 仍未落库；本轮 12B 仅做无表聚合。`ai_provider_health_events` 属于 12C 的后续可选数据库化阶段，本轮 12C 设计审查不建议首批建表。

## 是否需要改 Gateway

本轮已做 Gateway 最小 routing adapter 接入，并保持：

- 不改变 `call_text` / `call_general` / `call_vision` / `call_stream` 的返回合同。
- 不绕过 `ai_call_logs`。
- 不绕过 `ai_runs`。
- 不重新启用正式业务 stream 生成链路。
- 不把 usage/cost/health 从 `ai_runs.output_data` 推导。

## 是否需要改管理端

Phase 12D 已在用户批准后完成 `/manage/ai` provider/routing/usage/health 只读面板。

当前状态：

- `/manage/ai` 已展示 provider 配置状态。
- `/manage/ai` 已展示基于 `ai_call_logs` 的 usage/cost snapshot。
- `/manage/ai` 已展示基于 `ai_call_logs` recent 聚合的 health snapshot。
- 面板只读，不提供在线编辑、保存、provider probe、熔断开关或配置修改入口。
- token usage / cost 仍按 backend 响应展示 `unknown/null`，不伪造，不声明为精确账单。

## 是否需要真实 provider 验证

Phase 12A/12B 本轮不做真实 provider 调用。12A 使用 mock provider tests 验证 route resolution 与 fallback order；12B 使用 service/route contract tests 验证聚合与 admin-only 边界。

12C 最小 Health Snapshot API 同样不做真实 provider 调用。若后续要做真实 health probe，必须单独审批 provider、频率、成本和失败处理口径。

真实 provider 验证建议单独审批，原因：

- 有成本风险。
- 有速率限制风险。
- health check 与业务成功率语义不同。

## 是否阻塞当前业务使用

不阻塞当前业务使用。

当前正式可审计 AI 生成已走非流式 Run 链路，Batch 12 是治理增强，不是修复主链路阻塞。

## 与 RISK-B11-003 的关系

RISK-B11-003 已关闭，关闭方式是正式链路迁出伪流式 stream endpoint。

Batch 12 不得重新引入正式业务对 `/api/ai/analyze-stream` 或 `/api/ai/analyze-text-stream` 的依赖，也不得宣称完整 provider token streaming 审计已完成。

## 下一步审批建议

建议下一步不要直接扩张到大而全的 Batch 12，而是选择其中一个后续阶段单独审批：

```text
批准执行 Batch 12C Failure Classification / Cooldown 设计与最小实现
```

建议该审批继续明确：不新增 migration、不做真实 provider probe、先使用 `ai_call_logs` recent snapshot 和 mock tests。

如要推进数据库化 provider/model/routing、`ai_usage_daily` 或 `ai_provider_health_events`，应单独审批是否允许新增 migration 与模型表。

12D 完成后，管理端已经具备只读观测入口。后续若继续推进，建议优先选择：

1. `Batch 12C Failure Classification / Cooldown`：仍可不新增表，先用 mock tests 和代码级 policy。
2. `Batch 12B Actual Token Usage Capture`：仅在 provider 返回真实 usage 时记录，不按字符估算。
3. 数据库化 provider/model/routing：必须单独批准 migration、权限边界和只读/编辑策略。
