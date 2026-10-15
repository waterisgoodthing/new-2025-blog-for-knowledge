# Design

## 总体设计

Batch 12 在现有 AI Gateway 上增加治理层。当前已完成 Phase 12A 代码级 typed policy、Phase 12B usage/cost 无表最小聚合、Phase 12C provider health / 降级治理设计审查与最小 Health Snapshot API。数据库模型仍作为未来可选项，不在本轮新增 migration 或数据库表。

```text
Prompt Registry
  -> task_type / prompt_version / schema / json_mode / max_tokens

Typed Routing Policy (Phase 12A completed)
  -> task_type / primary provider / primary model / fallback chain / capability / policy

Database Routing Tables (future optional)
  -> after typed policy is proven and separately approved

AI Gateway
  -> resolve task contract + routing policy
  -> provider call / fallback
  -> ai_call_logs
  -> ai_runs

Usage / Health
  -> aggregate from ai_call_logs
  -> usage/cost unknown/null when actual usage is absent
  -> provider health snapshot from ai_call_logs recent facts
  -> provider health events remain future optional design
  -> manage read-only panel remains Phase 12D
```

## 关键边界

### ai_call_logs 与 ai_runs

- `ai_call_logs` = 技术调用事实源。
- `ai_runs` = 业务审计事实源。
- Batch 12 usage/cost/health 优先基于 `ai_call_logs`。
- Batch 12 不得把 `ai_runs` 当作成本统计事实源。

原因：

- 一次业务 Run 可能包含 repair 或 fallback 等多个技术调用。
- cost/usage 属于 provider 调用事实，而不是人工审核事实。
- `ai_runs.output_data` 可能是业务结果，不适合作为 usage/cost 数据源。

### Routing 与 Prompt Registry

- Prompt Registry 负责 task_type 的 Prompt 工程合同：prompt_version、schema、json_mode、max_tokens、message builder。
- Routing Rule 负责 task_type 的 provider/model/fallback 策略。
- 二者可通过 `task_type` 关联，但不得互相内嵌。

Phase 12A 可保留 Prompt Registry 的 `preferred_provider` 作为兼容默认值，但新增 RoutingRule 后，应逐步把 provider 策略迁出 Prompt Registry。

### Cost 统计

- 如果 provider 返回 token usage，则记录真实 usage。
- 如果 provider 不返回 token usage，只能记录 `unknown` / `null`。
- 不得按字符数伪造 token usage。
- 可以单独设计 `estimated_tokens`，但必须与 `actual_input_tokens` / `actual_output_tokens` 区分。
- `estimated_cost` 必须带 `cost_source`，例如 `actual_usage`、`estimated_usage`、`unknown`。

### Health Check

- health check 不等于真实业务成功率。
- health check 只表达 provider/model 当前可用性。
- 业务调用失败率仍应从 `ai_call_logs` 聚合。
- health check 失败不应直接生成 `ai_run`。
- health / 降级状态不得从 `ai_runs.output_data` 推导。

## 当前系统事实

| 维度 | 当前实现 |
|---|---|
| provider env | `AI_*`、`DASHSCOPE_*`、`DEEPSEEK_*` in `backend/app/config.py` |
| provider runtime list | `ai_service._get_providers()` |
| fallback | `ai_service._select_providers()` + `_call_with_fallback()` 顺序尝试 |
| retryable | 字符串匹配 `429/500/502/503/504/timeout/ConnectError` |
| task provider | Prompt Registry `preferred_provider` + Gateway fallback defaults |
| call logs | `ai_call_logs` 记录 provider/model/latency/success/error/fallback/attempts |
| runs | `ai_runs` 记录业务审计状态 |
| token usage | 未持久化 |
| cost | 未持久化 |
| budget/quota | 未发现 |
| health | `get_provider_status()` 仅配置状态，不是真实 health |
| model disable | 未发现 |
| circuit breaker | 未发现 |

## Phase 12A 推荐：先使用代码级 typed policy

本轮结论：Phase 12A 不建议立即使用数据库模型，建议先使用代码级 typed policy。

原因：

1. 本轮硬约束禁止新增 migration 和数据库表。
2. 当前 provider/model 数量有限，主要治理目标是把隐式 provider/fallback 策略显式化。
3. typed policy 可以用类型、单测和审查先稳定 contract，避免过早引入表结构。
4. 后续若确实需要运行时配置或管理端展示，再单独审批数据库模型。

推荐 typed policy 合同：

| Policy | 字段 | 说明 |
|---|---|---|
| ProviderPolicy | `provider_key`、`display_name`、`capabilities`、`default_model`、`enabled_by_env_key`、`timeout_seconds` | 只引用 env key 名称，不保存 secret |
| ModelPolicy | `provider_key`、`model_name`、`capabilities`、`max_output_tokens`、`price=null` | Phase 12A 不启用 cost |
| RoutingPolicy | `task_type`、`primary_provider`、`primary_model`、`fallback_chain`、`require_json`、`require_vision` | 表达 task_type 路由与 fallback |

typed policy 的验证方式：

- task_type route resolution unit tests
- provider capability matching tests
- fallback order mock tests
- Prompt Registry boundary tests
- no-secret policy tests

typed policy 不做：

- 不保存 API key。
- 不做在线编辑。
- 不做 usage/cost 聚合。
- 不做 provider health check。
- 不做真实 provider 调用。

## 未来数据模型评估

### ai_provider_profiles

候选字段：

- id
- provider_key
- display_name
- enabled
- supports_text
- supports_vision
- supports_stream
- default_model
- priority
- rate_limit_per_minute
- timeout_seconds
- created_at
- updated_at

建议：后置到数据库化实施阶段。它是把 env/hardcode 显式化的最小表，但不建议在当前 Phase 12A 立即落库。

不保存：

- API key
- authorization
- cookie
- secret
- token

API key 仍来自环境变量或 secrets manager，profile 只保存 provider_key 与能力策略。

### ai_model_profiles

候选字段：

- id
- provider_key
- model_name
- display_name
- enabled
- capability_text
- capability_vision
- capability_json
- capability_stream
- input_token_price
- output_token_price
- currency
- context_window
- max_output_tokens
- created_at
- updated_at

建议：后置到数据库化实施阶段。若 Phase 12A 采用 typed policy，可先仅在代码中表达 model capability，price 字段暂不启用。

### ai_routing_rules

候选字段：

- id
- task_type
- primary_provider
- primary_model
- fallback_chain_json
- require_vision
- require_json
- max_latency_ms
- max_cost_per_call
- enabled
- created_at
- updated_at

建议：先以 typed policy 表达，后续如需后台只读展示或运行时配置，再单独批准落库。`max_cost_per_call` 只保留设计概念，等 Phase 12B 有 usage/cost 后再讨论 enforcement。

### ai_usage_daily

候选字段：

- id
- date
- task_type
- provider
- model
- call_count
- success_count
- failure_count
- fallback_count
- input_tokens
- output_tokens
- estimated_cost
- created_at
- updated_at

建议：Phase 12B 实施。数据源应优先来自 `ai_call_logs`，token/cost 为 nullable。若 token unknown，不得写 0 伪装为无成本。

### ai_provider_health_events

候选字段：

- id
- provider
- model
- status
- error_code
- error_message_safe
- latency_ms
- created_at

建议：Phase 12C 实施。health event 是探测事实，不是业务调用事实。

## 最小可落地建议

Phase 12A 最小落地建议：

1. `ProviderPolicy` typed config
2. `ModelPolicy` typed config
3. `RoutingPolicy` typed config
4. routing resolver service
5. Gateway adapter design for later implementation

暂不落地：

- `ai_provider_profiles`
- `ai_model_profiles`
- `ai_routing_rules`

不建议 Phase 12A 同时引入：

- migration
- 数据库表
- `ai_usage_daily`
- `ai_provider_health_events`
- 管理端在线编辑
- cost enforcement

## Batch 12 分期

### Phase 12A：Provider Profile 与 Routing Rule 最小内核

目标：

- 把硬编码 provider/fallback 配置显式化。
- 支持 task_type 级别 primary provider/model 与 fallback chain。
- 不引入后台 UI。
- 不做复杂成本统计。

Phase 12A 已按以下最小范围实施：

- typed policy module
- routing resolver service
- Gateway routing adapter
- tests for fallback ordering and compatibility defaults

不建议 Phase 12A 实施数据库表。数据库化可作为 Phase 12A.2 或 12B 前置另行审批。

### Phase 12B：Usage / Cost 统计

目标：

- 基于 `ai_call_logs` 聚合每日调用量、成功率、fallback 次数、latency。
- 如果 provider 返回 token usage，记录 actual usage。
- 如 provider 暂不返回 token usage，标记 unknown/null，不伪造。

当前状态：

- 已完成无表最小聚合。
- 已新增 admin-only `GET /api/ai/call-logs/usage-cost`。
- 当前未持久化 actual token usage，因此 `input_tokens`、`output_tokens`、`estimated_cost`、`currency` 均为 `null`。
- `usage_source` 与 `cost_source` 固定为 `unknown`。
- `ai_usage_daily` 表、estimated cost、budget/quota enforcement 仍后置。

### Phase 12C：Health Check 与降级治理

目标：

- provider 健康状态记录。
- 连续失败阈值。
- 临时禁用 provider/model。
- fallback 策略可解释。

当前 12C 状态：

- 当前 `get_provider_status()` 只返回 key 是否配置、model、base_url label 和 role，不执行真实 probe，也不记录 health event。
- 当前 fallback 只基于 `fallback_chain` / `preferred` 排序与 retryable 错误字符串继续尝试，不存在连续失败阈值、冷却窗口或临时禁用状态。
- 12B 的 usage/cost 聚合可以提供业务调用失败率与 fallback 次数，但不能等同 provider health。
- 已新增 admin-only `GET /api/ai/provider-health-snapshot`，基于 `ai_call_logs` recent facts 输出 provider/model health snapshot。
- 当前不建议直接把 health 状态写入 Gateway 主路径；若后续需要自动降级，应先设计独立 health policy/resolver，由 Gateway 只读取安全的只读决策。

建议最小状态：

| 状态 | 含义 | 进入条件 | 退出条件 |
|---|---|---|---|
| `unknown` | 未探测或无足够样本 | 默认状态 / 新 provider | 首次 probe 或业务样本达到阈值 |
| `healthy` | 当前可用 | mock/真实 probe 成功，或业务调用失败率低于阈值 | 连续失败或 probe 失败 |
| `degraded` | 可用但不稳定，应优先 fallback | 连续可重试错误、超时、5xx 或高延迟 | 冷却期后成功 probe / 成功业务调用 |
| `disabled` | 暂时不参与 primary/fallback | auth error、配置错误、人工禁用、严重连续失败 | 人工恢复或冷却后验证通过 |

建议 failure classification：

| 分类 | 示例 | 是否可重试 | 说明 |
|---|---|---|---|
| `rate_limit` | 429 | 是 | 可触发 fallback 和冷却 |
| `timeout` | timeout / timed out | 是 | 可触发 fallback 和 degraded |
| `provider_5xx` | 500/502/503/504 | 是 | 可触发 fallback |
| `auth_error` | 401/403/provider auth | 否 | 应 fail closed，可能进入 disabled |
| `bad_request` | 400/schema/request too large | 否 | 多数是调用方问题，不应判定 provider down |
| `parse_error` | JSON parse failed | 条件重试 | provider 成功但输出不可用，语义不同于 provider down |
| `network_error` | ConnectError/DNS/TLS | 是 | 可触发 fallback |
| `unknown_error` | 其它异常 | 条件重试 | safe message 截断后记录 |

已完成 12C 最小实现范围：

1. 基于 `ai_call_logs` 的 provider/model recent health snapshot。
2. `healthy/degraded/unknown` snapshot 状态。
3. admin-only health snapshot API。
4. schema / service / route contract tests。

后续建议范围（如后续单独批准）：

1. 代码级 `ProviderHealthPolicy`，不建表。
2. `classify_provider_error(error: str, status_code: int | None)` safe 分类函数。
3. 可选内存级 cooldown policy，仅用于 mock tests，不持久化。
4. Gateway routing adapter 可选接入 health decision，但需单独审批。

不建议 12C 首批实施：

- 真实 provider probe。
- 自动长期禁用 provider/model。
- 新增 `ai_provider_health_events` 表。
- 修改 Gateway 调用协议。
- 把 health 状态写入 `ai_runs`。
- 基于 health 自动调用高成本 fallback，除非有明确 cost guard。

### Phase 12D：管理端只读面板

目标：

- `/manage/ai` 增加 provider/routing/usage/health 只读展示。
- 不做在线编辑。
- 不做 Prompt 后台。

## 验证矩阵

| 能力 | 验证方式 |
|---|---|
| provider typed policy | type/unit tests; no secret fields |
| routing rule | resolver unit tests by task_type |
| fallback chain | mock provider attempts order tests |
| ai_call_logs 边界 | log fields include usage policy but no secrets |
| ai_runs 边界 | Run status/review 不因 usage 聚合改变 |
| token unknown | provider no usage 时字段为 null/unknown |
| health | mock health probe event, no ai_run |
| manage read-only | anonymous 401，admin-only display |

## 安全设计

- provider API key 不入库。
- attempts/error 继续只存 safe/truncated error。
- 管理端不得显示 base_url secret query、Authorization、cookie、token。
- 成本面板必须标注 estimated/unknown，不等同真实账单。
