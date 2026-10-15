# Validation

## 验证性质

本轮先完成 Batch 12 P0-01 至 P0-15 设计审查阶段，随后在用户明确批准后实施 Phase 12A Typed Provider/Routing Policy 最小内核，继续实施 Phase 12B Usage / Cost 可观测性最小聚合，完成 Phase 12C Provider Health / 降级治理设计审查并实施 12C 最小 Health Snapshot API，最后实施 Phase 12D 管理端只读面板。

本轮未新增 migration，未新增数据库表，未做真实 provider 调用，未实现真实 health probe / 熔断 / 临时禁用，未提供 provider/routing/cost/health 在线编辑。

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

## 搜索结果摘要

### provider 配置

- `backend/app/config.py` 定义 `AI_API_KEY`、`AI_BASE_URL`、`AI_MODEL`、`DASHSCOPE_API_KEY`、`DASHSCOPE_BASE_URL`、`DASHSCOPE_MODEL`、`DEEPSEEK_API_KEY`、`DEEPSEEK_BASE_URL`、`DEEPSEEK_MODEL`。
- `backend/.env.example` 提供对应模板。
- `backend/app/services/ai_service.py::_get_providers()` 根据 settings 组装 provider list。

### fallback

- `ai_service._select_providers(required_caps, preferred)` 根据 capabilities 过滤 provider，并把 preferred provider 排在前面。
- `ai_service._call_with_fallback()` 顺序调用 provider，记录 attempts。
- retryable 目前是字符串匹配 `429/500/502/503/504/timeout/ConnectError`。
- 未发现数据库化 fallback chain。

### task_type / provider

- `ai_prompt_registry.PromptTemplate` 包含 `preferred_provider` 与 `max_tokens`。
- `ai_gateway._resolve_registry_defaults()` 读取 Prompt Registry 的 preferred_provider、json_mode、max_tokens、prompt_version。
- `call_vision()` 仍硬编码使用 `dashscope_vision`。
- 未发现独立 `ai_routing_rules`。

### ai_call_logs

- `ai_call_logs` 字段包含 task_type、provider_used、model、latency_ms、success、error、fallback_used、attempts、input_summary、prompt_version、created_at。
- `ai_log_service.query_call_log_stats()` 当前只聚合 total、success_count、avg_latency_ms。
- 未发现 token/cost 聚合。

### ai_runs

- `ai_runs` 字段包含业务审计状态、provider/model、prompt_version、input_summary、output_data、error、latency、review 状态。
- `ai_runs` 不应作为 Batch 12 cost/usage 事实源。

## 当前现状结论

| 项 | 结论 |
|---|---|
| provider 配置 | env/settings + `_get_providers()` |
| fallback 链 | capability + preferred 排序后顺序尝试 |
| token usage | 未记录 |
| cost | 未记录 |
| budget/quota | 未发现 |
| provider health | 只有配置状态，无真实 health event |
| model 禁用/降级 | 未发现 |
| per-task routing | Prompt Registry preferred_provider，未独立 |
| 熔断 | 未发现连续失败阈值或临时禁用 |

## P0 设计审查结论

| P0 项 | 结论 |
|---|---|
| P0-01 现状审计 | 已完成只读审计，详见 `audit.md` |
| P0-02 范围冻结 | 设计审查阶段不实施代码；用户批准后仅实施 Phase 12A |
| P0-03 Provider/Model 设计 | 建议 Phase 12A 先用代码级 typed policy，不建表 |
| P0-04 RoutingRule 设计 | 建议 `RoutingPolicy` 先表达 task_type/provider/model/fallback |
| P0-05 Gateway adapter 设计 | 后续实施时最小接入，不改公开返回合同 |
| P0-06 fallback 显式化 | 先用 typed fallback chain，mock 测试顺序 |
| P0-07 token/cost 审计 | 当前无 token/cost 持久化，不得伪造 |
| P0-08 UsageDaily 设计 | 后置 Phase 12B，数据源为 `ai_call_logs` |
| P0-09 Health 设计 | 后置 Phase 12C，health 不等于业务成功率 |
| P0-10 safe error | 继续要求 safe/truncated error，不记录 secret |
| P0-11 logs/runs 边界 | `ai_call_logs` 是技术事实源，`ai_runs` 是业务审计事实源 |
| P0-12 管理端 | 后置 Phase 12D，只读且 admin-only |
| P0-13 验证矩阵 | 以 type/unit/mock contract tests 为主 |
| P0-14 分期建议 | 12A typed policy；12B usage/cost；12C health；12D read-only UI |
| P0-15 handoff | 已更新 `handoff.md` |

## Phase 12A 实施结果

### 修改范围

- 新增 `backend/app/services/ai_routing_policy.py`：代码级 `ProviderPolicy` / `ModelPolicy` / `RoutingPolicy`。
- 更新 `backend/app/services/ai_gateway.py`：Gateway 从 typed routing policy 解析 preferred provider 与 fallback chain；保持 wrapper 返回合同不变。
- 更新 `backend/app/services/ai_service.py`：`_call_with_fallback()` 可接收显式 fallback chain；未传时保持旧 preferred 排序行为。
- 更新 `backend/tests/test_ai_routing_policy.py`：覆盖 no-secret policy contract、`analyze_text` route resolution、Gateway 传递 fallback chain。
- 更新 `backend/tests/test_ai_provider_models.py`：覆盖显式 fallback chain 控制 provider 顺序。

### 验证命令与结果

```bash
cd backend && .venv/bin/python -m pytest tests/test_ai_routing_policy.py -q
# 3 passed

cd backend && .venv/bin/python -m pytest tests/test_ai_provider_models.py tests/test_ai_routing_policy.py -q
# 7 passed

cd backend && .venv/bin/python -m pytest tests/test_ai_gateway.py tests/test_ai_provider_models.py tests/test_ai_routing_policy.py -ra
# 20 passed, 2 warnings

cd backend && .venv/bin/python -m pytest tests/ -ra
# 218 passed, 2 warnings
```

warnings 来自既有 `test_ai_gateway.py` AsyncMock warning；本轮未修改该 warning 所在测试逻辑。

## Phase 12B 实施结果

### 修改范围

- 更新 `backend/app/schemas/ai_call_log.py`：新增 `AiUsageCostStatsItem` / `AiUsageCostStatsResponse`。
- 更新 `backend/app/services/ai_log_service.py`：新增 `query_usage_cost_stats()`，基于 `ai_call_logs` 按日期、task_type、provider、model 聚合。
- 更新 `backend/app/routers/ai.py`：新增 admin-only `GET /api/ai/call-logs/usage-cost`。
- 新增 `backend/tests/test_ai_usage_cost_observability.py`：覆盖聚合输出、unknown usage/cost、route admin dependency。

### 聚合字段

| 字段 | 来源 |
|---|---|
| `date` | `ai_call_logs.created_at` cast to date |
| `task_type` | `ai_call_logs.task_type` |
| `provider` | `ai_call_logs.provider_used` |
| `model` | `ai_call_logs.model` |
| `call_count` | count |
| `success_count` | success=true count |
| `failure_count` | call_count - success_count |
| `fallback_count` | fallback_used=true count |
| `avg_latency_ms` | avg latency |
| `input_tokens` / `output_tokens` | `None`，当前未持久化 actual usage |
| `estimated_cost` / `currency` | `None`，当前不估算成本 |
| `usage_source` / `cost_source` | `unknown` |

### 验证命令与结果

```bash
cd backend && .venv/bin/python -m pytest tests/test_ai_usage_cost_observability.py -q
# 4 passed

cd backend && .venv/bin/python -m pytest tests/test_ai_usage_cost_observability.py tests/test_ai_run_call_log_compatibility.py tests/test_ai_gateway.py tests/test_ai_provider_models.py tests/test_ai_routing_policy.py -ra
# 26 passed, 2 warnings

cd backend && .venv/bin/python -m pytest tests/ -ra
# 222 passed, 2 warnings
```

warnings 仍来自既有 `test_ai_gateway.py` AsyncMock warning。

## Phase 12C 设计审查结果

### 只读审计命令

```bash
rg -n "health|status|provider_status|get_provider_status|fallback|retryable|timeout|429|500|502|503|504|circuit|disable|enabled|degrad|degrade|降级|熔断|rate_limit|ConnectError" backend/app backend/tests
nl -ba backend/app/services/ai_service.py | sed -n '75,215p'
nl -ba backend/app/services/ai_service.py | sed -n '280,335p'
nl -ba backend/app/services/ai_routing_policy.py | sed -n '1,180p'
nl -ba backend/app/services/ai_log_service.py | sed -n '35,115p'
nl -ba backend/app/routers/ai.py | sed -n '390,430p'
```

### 结论

| 项 | 设计审查结论 |
|---|---|
| provider health | 当前只有配置状态，无真实 probe / event |
| fallback | 已有 typed fallback chain，但不读取 health 状态 |
| retryable | 当前为字符串匹配，需后续抽出 failure classification |
| 熔断 | 未发现 circuit breaker / cooldown / 临时禁用 |
| model 降级 | 未发现模型级 disabled/degraded 状态 |
| 事实源 | health snapshot 可参考 `ai_call_logs`，但不能等同业务成功率 |
| ai_runs 边界 | health 不写入 `ai_runs`，不从 `ai_runs.output_data` 推导 |
| 推荐实现 | 后续若批准，先做代码级 health policy + safe error classification + recent snapshot |

本轮未执行：

- 未新增 health probe。
- 未新增 health event 表。
- 未新增 migration。
- 未修改 Gateway/provider 调用逻辑。
- 未做真实 provider 调用。
- 未声明真实 provider health 已验证。

## Phase 12C 最小 Health Snapshot API 实施结果

### 修改范围

- 更新 `backend/app/schemas/ai_call_log.py`：新增 `AiProviderHealthSnapshotItem` / `AiProviderHealthSnapshotResponse`。
- 更新 `backend/app/services/ai_log_service.py`：新增 `query_provider_health_snapshot()`，基于 `ai_call_logs` 按 provider/model 聚合 recent health snapshot。
- 更新 `backend/app/routers/ai.py`：新增 admin-only `GET /api/ai/provider-health-snapshot`。
- 新增 `backend/tests/test_ai_provider_health_snapshot.py`：覆盖 degraded 状态、safe schema、admin-only route、匿名 401。

### Snapshot 字段

| 字段 | 来源 |
|---|---|
| `provider` | `ai_call_logs.provider_used` |
| `model` | `ai_call_logs.model` |
| `status` | 基于 failure/fallback 阈值的 snapshot：`healthy` / `degraded` / `unknown` |
| `call_count` | count |
| `success_count` | success=true count |
| `failure_count` | call_count - success_count |
| `fallback_count` | fallback_used=true count |
| `failure_rate` | failure_count / call_count |
| `fallback_rate` | fallback_count / call_count |
| `avg_latency_ms` | avg latency |
| `source` | `ai_call_logs_recent` |
| `reason` | safe threshold reason，不含 prompt/input/secret |

### 验证命令与结果

```bash
cd backend && .venv/bin/python -m pytest tests/test_ai_provider_health_snapshot.py -q
# 4 passed

cd backend && .venv/bin/python -m pytest tests/test_ai_provider_health_snapshot.py tests/test_ai_usage_cost_observability.py tests/test_ai_run_call_log_compatibility.py tests/test_ai_gateway.py tests/test_ai_provider_models.py tests/test_ai_routing_policy.py -ra
# 31 passed, 2 warnings

cd backend && .venv/bin/python -m pytest tests/ -ra
# 226 passed, 2 warnings
```

warnings 仍来自既有 `test_ai_gateway.py` AsyncMock warning。

## 未实施说明

- 未新增 migration。
- 未新增数据库表。
- 未修改 provider HTTP 调用协议。
- 未修改 provider env 配置。
- 未运行真实 provider health check。
- 未实现自动熔断。
- 未实现 provider/model 临时禁用。
- 未实施数据库化 `ai_usage_daily`。
- 未实施真实 token usage 持久化。
- 未实施 estimated cost 计算。
- 未实施 provider health event。
- 未实施 provider/routing/cost/health 在线编辑。
- 未使用 `ai_runs.output_data` 推导 usage/cost/health。

## 结论边界

本轮完成的是 Batch 12 已批准分阶段最小实现，不等于 Batch 12 全部治理闭环：

- provider/model/routing 已有代码级 typed policy。
- 数据库化 provider/model/routing 仍后置。
- usage/cost 已完成无表最小聚合；真实 token usage、estimated cost、`ai_usage_daily` 表仍后置。
- health check 与降级治理已完成设计审查；最小 Health Snapshot API 已完成；真实 probe/熔断/禁用仍待单独批准。
- 管理端只读展示已在 Phase 12D 完成；在线编辑仍后置。
- 未执行真实 provider health 验证。

## Phase 12D 管理端只读面板实施结果

### 修改范围

- 更新 `src/lib/api/ai.ts`：新增 provider status、usage/cost stats、provider health snapshot 的前端响应类型与只读 GET 方法。
- 更新 `src/app/manage/(workspace)/ai/page.tsx`：在 `/manage/ai` 增加只读治理区块，展示 provider 配置状态、health snapshot、usage/cost snapshot，并保留原调用统计和调用日志。
- 更新 workflow 文档：记录 12D 验证结果、审计结论和 handoff 边界。

### 展示字段边界

| 区块 | 展示内容 | 明确不展示 |
|---|---|---|
| Provider 状态 | provider name、model、role、configured、base_url_label | API key、authorization、cookie、secret、token、真实 base URL secret |
| Health Snapshot | provider、model、status、call/failure/fallback/latency、source/reason | prompt、input_summary、replay_input、storage_key、provider error body 原文 |
| Usage / Cost Snapshot | date、task_type、provider、model、call/success/failure/fallback/latency、token/cost unknown/null | 精确账单声明、伪造 token、伪造 cost、ai_runs.output_data 推导 |

### 验证命令与结果

```bash
npx tsc --noEmit
# passed

npm run build
# passed；Next.js route 列表包含 /manage/ai

git diff --check
# passed
```

build 输出包含既有提示：`baseline-browser-mapping` 数据超过两个月、Node `module.register()` deprecation warning。它们不是本轮 12D 修改引入的失败，构建最终成功。

### 未实施说明

- 未新增 migration。
- 未新增数据库表。
- 未修改 Gateway 运行逻辑。
- 未修改 provider 调用逻辑。
- 未做真实 provider 调用或真实 health probe。
- 未实现 provider/routing/cost/health 在线编辑。
- 未实现自动熔断、cooldown 或 provider/model 临时禁用。
- 未伪造 token usage 或 cost。
- 未从 `ai_runs.output_data` 推导 usage/cost/health。
- 未重新启用正式业务 stream 生成链路。
