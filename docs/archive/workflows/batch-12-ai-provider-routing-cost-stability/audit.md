# Audit — Batch 12 Design Review

## 审计性质

本轮从 Batch 12 P0-01 ~ P0-15 设计审查开始，并在用户逐步批准后实施 12A、12B、12C 最小 API 与 12D 管理端只读面板。

已批准执行：

```text
P0-01 至 P0-15 设计审查必答项
Phase 12A Typed Provider/Routing Policy 最小实现
Phase 12B Usage / Cost 可观测性最小聚合
Phase 12C Provider Health / 降级治理设计审查
Phase 12C 最小 Health Snapshot API
Phase 12D 管理端只读面板
```

未批准执行：

```text
数据库化 provider/model/routing
数据库化 ai_usage_daily
真实 provider health probe
自动熔断 / provider 临时禁用
provider/routing/cost/health 在线编辑
```

本轮未新增 migration、未新增数据库表、未做真实 provider 调用、未实施真实 health probe/熔断/在线编辑。

## 只读审计命令

```bash
git status --short
rg -n "provider|model|fallback|attempts|latency|cost|token|usage|budget|quota|rate" backend/app backend/tests
rg -n "deepseek|qwen|dashscope|openai|model" backend/app backend/tests .env.example README.md
rg -n "ai_call_logs|ai_runs|AiTaskType|task_type|prompt_version" backend/app backend/tests
nl -ba backend/app/config.py | sed -n '1,90p'
nl -ba backend/app/services/ai_service.py | sed -n '1,340p'
nl -ba backend/app/services/ai_gateway.py | sed -n '1,420p'
nl -ba backend/app/models/ai_call_log.py | sed -n '1,120p'
nl -ba backend/app/models/ai_run.py | sed -n '1,120p'
nl -ba backend/app/services/ai_prompt_registry.py | sed -n '1,285p'
nl -ba backend/app/services/ai_log_service.py | sed -n '1,100p'
nl -ba backend/.env.example | sed -n '1,120p'
```

## 现状证据表

| 审计项 | 当前事实 | 证据 |
|---|---|---|
| provider 配置 | provider key/base/model 仍来自 settings/env，不来自数据库 | `backend/app/config.py:15-25`，`backend/.env.example:29-43` |
| provider runtime list | `_get_providers()` 根据 key 是否存在组装 `deepseek`、`dashscope_vision`、`qwen_general` | `backend/app/services/ai_service.py:31-75` |
| provider capability | provider dict 内含 `capabilities`，例如 text/json/vision | `backend/app/services/ai_service.py:36-73` |
| fallback selection | `_select_providers()` 先按 capability 过滤，再把 preferred 排在前面 | `backend/app/services/ai_service.py:78-89` |
| fallback execution | `_call_with_fallback()` 顺序尝试 provider，记录 attempts，全部失败后抛错 | `backend/app/services/ai_service.py:140-202` |
| retryable 判定 | 当前按错误字符串匹配 `429/500/502/503/504/timeout/ConnectError` | `backend/app/services/ai_service.py:173-188` |
| task_type/provider 默认关系 | Prompt Registry 的 `preferred_provider` 记录 task 默认 provider | `backend/app/services/ai_prompt_registry.py:39-67`、`:69-242` |
| Gateway 读取默认值 | `_resolve_registry_defaults()` 从 Prompt Registry 读 max_tokens、preferred、json_mode、prompt_version | `backend/app/services/ai_gateway.py:204-238` |
| call_text | 使用 registry preferred 或 fallback preferred `deepseek` | `backend/app/services/ai_gateway.py:241-277` |
| call_vision | 当前硬编码 preferred `dashscope_vision` | `backend/app/services/ai_gateway.py:280-312` |
| call_general | 当前 preferred `qwen_general` | `backend/app/services/ai_gateway.py:315-349` |
| call_stream | 当前是非流式 wrapper，仍写 log/run；不是正式 provider token stream | `backend/app/services/ai_gateway.py:352-393` |
| ai_call_logs 字段 | 记录 task_type/provider/model/latency/success/error/fallback/attempts/input_summary/prompt_version | `backend/app/models/ai_call_log.py:11-43` |
| ai_call_logs 聚合 | 当前只聚合 total/success_count/avg_latency_ms | `backend/app/services/ai_log_service.py:35-56` |
| ai_runs 字段 | 记录业务 Run 状态、provider/model、validation/review、output/error/latency | `backend/app/models/ai_run.py:11-89` |
| token usage | 未发现 input_tokens/output_tokens/usage 持久化字段 | `rg` 结果未发现 AI usage 字段；`AiCallLog` 字段无 token |
| cost | 未发现 cost/price/estimated_cost 持久化字段；搜索到的 cost 多为题目文本或图解语义 | `rg` 结果；`ai_call_logs` 与 `ai_runs` 字段无 cost |
| budget/quota | 未发现 AI budget/quota 表或拒绝逻辑 | `rg` 结果未发现 AI budget/quota 实现 |
| rate limit | 只有 analyze service 的内存全局 rate limit；不是预算治理 | `backend/app/services/ai_analyze_service.py:27-38` |
| provider health | `get_provider_status()` 只返回配置状态，不执行真实 probe，不记录 event | `backend/app/services/ai_service.py:268-320` |
| model 禁用/降级 | 未发现 enabled/disabled model profile 或临时降级状态 | `rg` 结果 |
| per-task routing | 没有独立 routing rule；只有 Prompt Registry preferred_provider 与 Gateway wrapper default | `backend/app/services/ai_prompt_registry.py`、`backend/app/services/ai_gateway.py` |
| 熔断 | 未发现连续失败阈值、冷却窗口或临时禁用 provider/model | `rg` 结果 |
| 匿名访问 | 管理端 provider/routing/cost/health 未来必须 admin-only；本轮未新增 API | 本轮未改代码 |

## 设计审查回答

### 当前 provider 配置在哪里？

在 settings/env：`AI_*`、`DASHSCOPE_*`、`DEEPSEEK_*`。`ai_service._get_providers()` 将配置组装为运行时 provider list。

### 当前 fallback 链如何定义？

没有一等 fallback chain。当前由 `_select_providers(required_caps, preferred)` 对 provider list 排序，再由 `_call_with_fallback()` 顺序尝试。

### 当前 task_type 与 provider 的关系在哪里？

Prompt Registry 的 `preferred_provider` 目前承担 task_type 默认 provider 角色。Gateway 通过 `_resolve_registry_defaults()` 读取它。该设计让 Prompt 工程合同和 routing 策略耦合，Batch 12 应拆开。

### 当前是否记录 token usage？

未记录。不能在 Batch 12 中按字符数伪造 token。

### 当前是否记录 cost？

未记录。Batch 12B 可设计 estimated cost，但必须和 actual usage/cost 明确区分。

### 当前是否有预算限制？

没有 AI budget/quota。只有内存全局 rate limit，不能当预算治理。

### 当前是否有 provider health 状态？

只有配置状态，不是真实 health check，也没有 health event 历史。

### 当前是否有模型级别禁用或降级？

没有。

### 当前是否有 per-task 路由规则？

没有独立 RoutingRule。

### 当前是否有失败熔断？

没有连续失败阈值或熔断窗口。

## typed policy vs 数据库模型建议

结论：Phase 12A 建议先使用代码级 typed policy，不建议立即使用数据库模型。

原因：

1. 用户本轮硬约束明确禁止新增 migration 和数据库表。
2. 当前 provider/model 数量少，主要是把隐式 fallback 规则显式化，不需要一开始就引入表。
3. typed policy 可以先冻结 contract、测试 routing resolution、保持 Gateway wrapper 合同不变。
4. 后续若 12A typed policy 稳定，再在独立审批中迁移到 `ai_provider_profiles`、`ai_model_profiles`、`ai_routing_rules`。

建议的 typed policy 形态：

```text
ProviderPolicy:
  provider_key
  display_name
  capabilities
  default_model
  enabled_by_env_key
  timeout_seconds

ModelPolicy:
  provider_key
  model_name
  capabilities
  max_output_tokens
  price: null

RoutingPolicy:
  task_type
  primary_provider
  primary_model
  fallback_chain
  require_json
  require_vision
```

注意：typed policy 不保存 API key，只引用 env key 名称或 provider_key。

## P0 设计审查完成情况

| 任务 | 设计审查结论 |
|---|---|
| P0-01 | 已完成现状审计，证据见本文件 |
| P0-02 | 已确认硬约束和禁止项 |
| P0-03 | 建议数据模型后置，Phase 12A 先 typed policy |
| P0-04 | RoutingRule 最小合同已设计 |
| P0-05 | 设计阶段只做 adapter 设计；用户批准后已完成 Phase 12A 最小接入 |
| P0-06 | fallback chain 显式化进入 12A typed policy |
| P0-07 | token/cost 统计可行性结论：actual usage 缺失，禁止伪造 |
| P0-08 | UsageDaily 后置到 12B |
| P0-09 | Provider health 后置到 12C |
| P0-10 | failure classification 设计纳入 12A/12C 分界 |
| P0-11 | ai_call_logs 与 ai_runs 边界已冻结 |
| P0-12 | 管理端只读面板后置到 12D |
| P0-13 | 验证矩阵已设计，mock 与真实 provider 分开 |
| P0-14 | 分期建议已更新 |
| P0-15 | handoff 已更新 |

## 禁止项确认

本轮未做且后续未获再次批准前不得做：

- 新增 migration
- 新增数据库表
- 修改前端页面
- Prompt 后台 / A/B / 热更新 / Prompt 评测
- 正式业务 stream 生成链路
- 真实 provider 调用
- token/cost 伪造
- 从 `ai_runs.output_data` 推导 usage/cost/health
- 向匿名用户暴露 provider/routing/cost/health
- Phase 12D 实施
- 数据库化 `ai_usage_daily`
- estimated cost 计算
- 真实 provider health probe
- 自动熔断
- provider/model 临时禁用

## Phase 12A 实施审计

| 实施项 | 结果 | 证据 |
|---|---|---|
| typed policy 合同 | 已新增 `ProviderPolicy` / `ModelPolicy` / `RoutingPolicy`，不含 secret 字段 | `backend/app/services/ai_routing_policy.py`、`backend/tests/test_ai_routing_policy.py` |
| analyze_text routing | `analyze_text` 解析为 `deepseek -> qwen_general` | `tests/test_ai_routing_policy.py::test_analyze_text_resolves_to_explicit_fallback_chain` |
| Gateway adapter | Gateway 将 policy fallback chain 传给 `_call_with_fallback()` | `tests/test_ai_routing_policy.py::test_call_text_passes_routing_policy_chain_to_fallback` |
| fallback chain 排序 | `_call_with_fallback()` 接收显式 chain，并按 chain 顺序尝试 provider | `tests/test_ai_provider_models.py::test_explicit_fallback_chain_controls_provider_order` |
| 兼容性 | Gateway/provider/full backend tests 通过 | `218 passed, 2 warnings` |

实施边界：

- 没有新增表。
- 没有新增 migration。
- 没有保存 API key。
- 没有记录 token usage 或 cost。
- 没有做真实 provider 调用。
- 没有改前端页面。

## Phase 12B 实施审计

| 实施项 | 结果 | 证据 |
|---|---|---|
| usage/cost schema | 已新增 nullable token/cost 字段与 `usage_source=unknown` / `cost_source=unknown` | `backend/app/schemas/ai_call_log.py` |
| 最小聚合 service | 已基于 `ai_call_logs` 聚合 date/task/provider/model/call/success/failure/fallback/latency | `backend/app/services/ai_log_service.py::query_usage_cost_stats` |
| admin-only route | 已新增 `GET /api/ai/call-logs/usage-cost`，依赖 `get_current_admin` | `backend/app/routers/ai.py`、`tests/test_ai_usage_cost_observability.py` |
| no fake usage/cost | token/cost 输出 `None`，source 输出 `unknown` | `tests/test_ai_usage_cost_observability.py` |
| 兼容性 | AI 相关测试和 backend full suite 通过 | `26 passed, 2 warnings`；`222 passed, 2 warnings` |

实施边界：

- 没有新增 `ai_usage_daily` 表。
- 没有新增 migration。
- 没有从 `ai_runs.output_data` 推导 usage/cost。
- 没有估算 token。
- 没有估算成本。
- 没有修改前端页面。

## Phase 12C 设计审查

### 只读审计命令

```bash
rg -n "health|status|provider_status|get_provider_status|fallback|retryable|timeout|429|500|502|503|504|circuit|disable|enabled|degrad|degrade|降级|熔断|rate_limit|ConnectError" backend/app backend/tests
nl -ba backend/app/services/ai_service.py | sed -n '75,215p'
nl -ba backend/app/services/ai_service.py | sed -n '280,335p'
nl -ba backend/app/services/ai_routing_policy.py | sed -n '1,180p'
nl -ba backend/app/services/ai_log_service.py | sed -n '35,115p'
nl -ba backend/app/routers/ai.py | sed -n '390,430p'
```

### 现状证据表

| 审计项 | 当前事实 | 证据 |
|---|---|---|
| provider status | `get_provider_status()` 只返回配置状态，不执行 probe | `backend/app/services/ai_service.py:280-331` |
| fallback order | `_select_providers()` 支持 `fallback_chain` 排序，但不读取 health 状态 | `backend/app/services/ai_service.py:78-99` |
| retryable 判断 | `_call_with_fallback()` 使用字符串匹配 `429/500/502/503/504/timeout/ConnectError` | `backend/app/services/ai_service.py:184-199` |
| attempts | 每次 provider 尝试会记录 provider/model/success/latency/error | `backend/app/services/ai_service.py:163-213` |
| typed policy | `ProviderPolicy` / `RoutingPolicy` 记录能力与 fallback，不含 health 状态 | `backend/app/services/ai_routing_policy.py:19-48` |
| usage/cost 聚合 | 12B 可按 provider/model 聚合 success/fallback/latency，但不是 health probe | `backend/app/services/ai_log_service.py:60-115` |
| admin status route | `/api/ai/provider-status` 是 admin-only，但返回配置 status | `backend/app/routers/ai.py:392-396` |
| 熔断/临时禁用 | 未发现 circuit breaker、cooldown、disabled provider/model 状态 | `rg` 结果 |
| health event | 未发现 `ai_provider_health_events` 或等价持久化事件 | `rg` 结果 |

### 设计结论

- 12C 已完成设计审查，并在用户批准后实施最小 Health Snapshot API。
- 建议 12C 最小实现从代码级 health policy + error classification + `ai_call_logs` recent snapshot 开始。
- 不建议首批新增 `ai_provider_health_events` 表；若需要事件历史，应单独批准 migration。
- 不建议真实 provider probe 混入默认测试；真实 probe 有成本、速率限制和凭证风险。
- health 状态不能写入 `ai_runs`，也不能从 `ai_runs.output_data` 推导。

## Phase 12C 最小实现审计

| 实施项 | 结果 | 证据 |
|---|---|---|
| health snapshot schema | 已新增 `AiProviderHealthSnapshotItem` / response，不含 prompt/input/secret 字段 | `backend/app/schemas/ai_call_log.py:72-95` |
| health snapshot service | 已基于 `ai_call_logs` provider/model 聚合 failure/fallback/latency，source=`ai_call_logs_recent` | `backend/app/services/ai_log_service.py:133-180` |
| admin-only route | 已新增 `GET /api/ai/provider-health-snapshot`，依赖 `get_current_admin` | `backend/app/routers/ai.py:401-407` |
| 匿名保护 | 匿名请求返回 401 | `backend/tests/test_ai_provider_health_snapshot.py:78-82` |
| degraded 判定 | failure/fallback rate >= 0.30 标记 degraded | `backend/app/services/ai_log_service.py:14-26`、`backend/tests/test_ai_provider_health_snapshot.py:13-42` |
| 兼容性 | AI 相关测试和 backend full suite 通过 | `31 passed, 2 warnings`；`226 passed, 2 warnings` |

实施边界：

- 没有新增 `ai_provider_health_events` 表。
- 没有新增 migration。
- 没有执行真实 provider probe。
- 没有修改 provider 调用逻辑。
- 没有实现自动熔断。
- 没有实现 provider/model 临时禁用。

## Phase 12D 管理端只读面板审计

| 实施项 | 结果 | 证据 |
|---|---|---|
| 前端 typed API client | 已新增 `getProviderStatus()`、`getUsageCostStats()`、`getProviderHealthSnapshot()`，类型不含 secret/prompt/input 字段 | `src/lib/api/ai.ts` |
| `/manage/ai` provider 状态 | 已展示 provider name、model、role、configured、base_url_label | `src/app/manage/(workspace)/ai/page.tsx` |
| `/manage/ai` health snapshot | 已展示 provider/model/status/call/failure/fallback/latency/reason，标注不等同真实 probe | `src/app/manage/(workspace)/ai/page.tsx` |
| `/manage/ai` usage/cost snapshot | 已展示 call/success/failure/fallback/latency，token/cost 为 unknown/null 时明确不等于 0 或账单 | `src/app/manage/(workspace)/ai/page.tsx` |
| 只读边界 | 页面没有新增编辑按钮、保存动作、provider probe 触发器或配置修改入口 | `src/app/manage/(workspace)/ai/page.tsx` |
| 前端验证 | typecheck/build/diff check 通过 | `npx tsc --noEmit`；`npm run build`；`git diff --check` |

实施边界：

- 没有新增 migration。
- 没有新增数据库表。
- 没有修改 Gateway 运行逻辑。
- 没有修改 provider 调用逻辑。
- 没有执行真实 provider 调用或真实 health probe。
- 没有新增 provider/routing/cost/health 在线编辑。
- 没有伪造 token usage 或 cost。
- 没有从 `ai_runs.output_data` 推导 usage/cost/health。
