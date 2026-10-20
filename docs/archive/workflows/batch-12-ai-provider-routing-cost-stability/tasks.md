# Tasks — Batch 12 Provider Routing / Cost / Stability Closure

本清单记录 Batch 12 P0-01 ~ P0-15 的设计审查、Phase 12A/12B/12C/12D 实施结果，以及后置项边界。

状态说明：

- `[x] 设计审查完成；后置实现另列 backlog` 表示该设计项已关闭为本批审查结论，未实施部分不再作为当前阻塞。
- Phase 12A/12B/12C/12D 已在用户批准后实施并关闭。
- 未实施项已转入 deferred backlog：数据库化 provider/routing、真实 provider probe、health event 表、熔断、provider 临时禁用和在线编辑。
- 未经用户再次明确批准，不得新增 migration、数据库表、health probe、熔断、provider 临时禁用或前端在线编辑。

## Phase 12A 实施清单

用户已批准实施 Phase 12A Typed Provider/Routing Policy 最小实现。

实施边界：

- 不新增 migration。
- 不新增数据库表。
- 不做真实 provider 调用。
- 不修改前端页面。
- 不进入 Prompt 后台 / A/B / 热更新 / Prompt 评测。
- 不重新启用正式业务 stream 生成链路。
- 不伪造 token usage 或 cost。

### B12A-01

- [x] 已完成
- 任务名称：新增 provider/model/routing typed policy 合同
- 优先级：P0
- 来源需求：REQ-B12-001、REQ-B12-002
- 涉及文件：`backend/app/services/ai_routing_policy.py`、相关测试
- 修改内容：用代码级 dataclass/typed policy 表达 provider/model/routing，不新增表。
- 完成标准：能解析现有 task_type 的 primary provider/model/fallback chain，且 policy 不包含 secret 字段。
- 验证方式：`cd backend && .venv/bin/python -m pytest tests/test_ai_routing_policy.py -q`（3 passed）。
- 风险说明：policy 与 Prompt Registry 重叠时必须保持 Prompt Registry 负责 schema/json_mode。

### B12A-02

- [x] 已完成
- 任务名称：Gateway routing adapter 最小接入
- 优先级：P0
- 来源需求：REQ-B12-002、REQ-B12-003
- 涉及文件：`backend/app/services/ai_gateway.py`
- 修改内容：Gateway 从 typed routing policy 解析 preferred provider，但保持现有 wrapper 返回合同。
- 完成标准：`call_text`、`call_vision`、`call_general` 行为兼容，mock fallback tests 通过。
- 验证方式：`cd backend && .venv/bin/python -m pytest tests/test_ai_routing_policy.py -q`（3 passed）。
- 风险说明：不得绕过 `ai_call_logs` / `ai_runs`。

### B12A-03

- [x] 已完成
- 任务名称：ai_service fallback chain 最小适配
- 优先级：P0
- 来源需求：REQ-B12-003
- 涉及文件：`backend/app/services/ai_service.py`
- 修改内容：允许 `_call_with_fallback()` 接收显式 fallback chain，并保持旧 preferred 参数兼容。
- 完成标准：未传 fallback chain 时旧行为不变；传入 chain 时按 chain 顺序尝试 provider。
- 验证方式：`cd backend && .venv/bin/python -m pytest tests/test_ai_provider_models.py tests/test_ai_routing_policy.py -q`（7 passed）。
- 风险说明：不得改变 provider 调用协议或真实 provider 配置。

### B12A-04

- [x] 已完成
- 任务名称：验证与文档收口
- 优先级：P0
- 来源需求：REQ-B12-001 ~ REQ-B12-003
- 涉及文件：`validation.md`、`audit.md`、`handoff.md`
- 修改内容：记录实施文件、测试结果、未实施 12B/12C/12D 说明。
- 完成标准：验证命令结果可复核，风险与后置项清晰。
- 验证方式：targeted pytest、full backend pytest、`git diff --check` 均已执行；backend full suite `218 passed, 2 warnings`。
- 风险说明：若大脏树已有无关失败，必须标注为非本轮引入。

## Phase 12B 实施清单

用户已批准执行 12B Usage / Cost 可观测性设计与最小聚合。

实施边界：

- 不新增 migration。
- 不新增数据库表。
- 不修改 provider 调用逻辑。
- 不做真实 provider 调用。
- 不修改前端页面。
- 不伪造 token usage 或 cost。
- 不从 `ai_runs.output_data` 推导 usage/cost/health。

### B12B-01

- [x] 已完成
- 任务名称：Usage / Cost 最小聚合 schema 与 service
- 优先级：P0
- 来源需求：REQ-B12-004
- 涉及文件：`backend/app/schemas/ai_call_log.py`、`backend/app/services/ai_log_service.py`、相关测试
- 修改内容：基于 `ai_call_logs` 按日期、task_type、provider、model 聚合 call/success/failure/fallback/latency；token/cost 输出 unknown/null。
- 完成标准：聚合不依赖 `ai_runs`，不伪造 token/cost。
- 验证方式：`cd backend && .venv/bin/python -m pytest tests/test_ai_usage_cost_observability.py -q`（4 passed）。
- 风险说明：当前无 token usage 字段，成本只能明确 unknown，不能估算。

### B12B-02

- [x] 已完成
- 任务名称：Admin-only usage / cost observability route
- 优先级：P0
- 来源需求：REQ-B12-004、REQ-B12-006
- 涉及文件：`backend/app/routers/ai.py`、route contract tests
- 修改内容：提供管理端只读聚合 API，不改前端页面。
- 完成标准：匿名不可访问；响应不包含 input_summary、prompt、API key、authorization、cookie、secret、token、storage_key。
- 验证方式：`tests/test_ai_usage_cost_observability.py::AiUsageCostStatsContractTest`（route dependency 包含 `get_current_admin`）。
- 风险说明：新增观测 API 不应被误解为精确账单。

### B12B-03

- [x] 已完成
- 任务名称：12B 验证与文档收口
- 优先级：P0
- 来源需求：REQ-B12-004
- 涉及文件：`validation.md`、`audit.md`、`handoff.md`
- 修改内容：记录 12B 实施范围、测试结果、unknown usage/cost 边界和后置项。
- 完成标准：验证结果可复核，明确 12C/12D 未实施。
- 验证方式：targeted pytest（4 passed）、AI 相关回归（26 passed, 2 warnings）、backend full suite（222 passed, 2 warnings）、`git diff --check`。
- 风险说明：如果大脏树存在无关失败，需独立标注。

## Phase 12C 设计审查清单

用户要求执行 12C Provider Health / 降级治理设计审查。

本轮边界：

- 只做只读审计与设计文档。
- 不新增 migration。
- 不新增数据库表。
- 不修改 Gateway 运行逻辑。
- 不修改 provider 调用逻辑。
- 不做真实 provider 调用。
- 不修改前端页面。
- 不实施 health probe、熔断或临时禁用。

### B12C-DR-01

- [x] 设计审查完成；后置实现另列 backlog
- 任务名称：Provider health / 降级现状审计
- 优先级：P0
- 来源需求：REQ-B12-005
- 涉及文件：`backend/app/services/ai_service.py`、`backend/app/services/ai_routing_policy.py`、`backend/app/services/ai_log_service.py`、`backend/app/routers/ai.py`
- 修改内容：只读审计 provider status、fallback、retryable、usage/cost 聚合与 health 的边界。
- 完成标准：明确当前是否有真实 health、熔断、临时禁用和模型级降级。
- 验证方式：`rg` 与关键代码行号审计。
- 风险说明：配置状态容易被误读为 provider 可用性。

### B12C-DR-02

- [x] 设计审查完成；后置实现另列 backlog
- 任务名称：Health event 与 failure classification 设计
- 优先级：P0
- 来源需求：REQ-B12-005、REQ-B12-003
- 涉及文件：未来 health service / schema / tests
- 修改内容：设计 health event 字段、状态枚举、错误分类、safe message 边界。
- 完成标准：health event 不含 secret，不写入 `ai_runs`，不等同业务成功率。
- 验证方式：设计矩阵审查。
- 风险说明：provider error body 可能回显敏感信息，必须截断与清理。

### B12C-DR-03

- [x] 设计审查完成；后置实现另列 backlog
- 任务名称：降级 / 熔断策略设计
- 优先级：P0
- 来源需求：REQ-B12-005
- 涉及文件：未来 health policy / routing resolver / Gateway adapter
- 修改内容：设计连续失败阈值、冷却窗口、临时禁用、fallback 解释与恢复条件。
- 完成标准：不改变 Prompt Registry 合同，不绕过 typed routing policy，不绕过 `ai_call_logs`。
- 验证方式：mock provider tests 设计。
- 风险说明：错误阈值可能误伤短暂失败或导致高成本 fallback。

### B12C-DR-04

- [x] 设计审查完成；后置实现另列 backlog
- 任务名称：12C handoff 与下一步审批建议
- 优先级：P0
- 来源需求：handoff
- 涉及文件：`design.md`、`audit.md`、`validation.md`、`handoff.md`
- 修改内容：记录是否建议实施 12C、推荐最小范围、是否需要 migration、是否需要真实 provider 验证。
- 完成标准：下一轮可直接审批 12C 最小实现或继续停留设计债。
- 验证方式：文档审查、`git diff --check`。
- 风险说明：没有真实 provider 验证时不能宣称 provider health 已验证。

## Phase 12C 最小实现清单

用户已批准实施 12C 最小 Health Snapshot API。

实施边界：

- 不新增 migration。
- 不新增数据库表。
- 不做真实 provider probe。
- 不修改 provider 调用逻辑。
- 不修改前端页面。
- 不实现自动熔断或临时禁用。
- 不把 health 写入 `ai_runs`。

### B12C-01

- [x] 已完成
- 任务名称：Provider health snapshot schema / service
- 优先级：P0
- 来源需求：REQ-B12-005
- 涉及文件：`backend/app/schemas/ai_call_log.py`、`backend/app/services/ai_log_service.py`、相关测试
- 修改内容：基于 `ai_call_logs` recent 聚合 provider/model call/failure/fallback/latency，输出 `healthy/degraded/unknown` snapshot。
- 完成标准：不做真实 provider 调用；不从 `ai_runs` 推导；safe reason 不泄露敏感信息。
- 验证方式：`cd backend && .venv/bin/python -m pytest tests/test_ai_provider_health_snapshot.py -q`（4 passed）。
- 风险说明：业务失败率不等同真实 provider health，响应必须标明 snapshot source。

### B12C-02

- [x] 已完成
- 任务名称：Admin-only health snapshot route
- 优先级：P0
- 来源需求：REQ-B12-005、REQ-B12-006
- 涉及文件：`backend/app/routers/ai.py`、route contract tests
- 修改内容：新增只读 `GET /api/ai/provider-health-snapshot`，依赖 `get_current_admin`。
- 完成标准：匿名 401；不暴露 prompt、input_summary、API key、authorization、cookie、secret、token、storage_key。
- 验证方式：`tests/test_ai_provider_health_snapshot.py` route registration / anonymous access tests。
- 风险说明：snapshot 不能被宣称为真实 provider probe。

### B12C-03

- [x] 已完成
- 任务名称：12C 实施验证与文档收口
- 优先级：P0
- 来源需求：REQ-B12-005
- 涉及文件：`validation.md`、`audit.md`、`handoff.md`
- 修改内容：记录 12C 实施范围、测试结果、未实施 probe/熔断/禁用说明。
- 完成标准：验证结果可复核，12D 和真实 probe 后置项清晰。
- 验证方式：targeted pytest（4 passed）、AI 相关回归（31 passed, 2 warnings）、backend full suite（226 passed, 2 warnings）、`git diff --check`。
- 风险说明：如果大脏树存在无关失败，需独立标注。

## Phase 12D 实施清单

用户已批准实施 12D 管理端只读面板。

实施边界：

- 不新增 migration。
- 不新增数据库表。
- 不做真实 provider 调用。
- 不修改 provider 调用逻辑。
- 不做 Prompt 后台 / A/B / 热更新 / Prompt 评测。
- 不做在线编辑。
- 不向匿名用户暴露 provider/routing/cost/health 数据。

### B12D-01

- [x] 已完成
- 任务名称：前端 API typed client 扩展
- 优先级：P0
- 来源需求：REQ-B12-006
- 涉及文件：`src/lib/api/ai.ts`
- 修改内容：增加 provider status、usage/cost、health snapshot 响应类型与只读 GET 方法。
- 完成标准：类型不包含 secret、prompt、input_summary、API key、authorization、cookie、token、storage_key。
- 验证方式：`npx tsc --noEmit`。
- 风险说明：管理端展示字段必须与 backend schema 保持同步。

### B12D-02

- [x] 已完成
- 任务名称：/manage/ai 只读治理面板
- 优先级：P0
- 来源需求：REQ-B12-006
- 涉及文件：`src/app/manage/(workspace)/ai/page.tsx`
- 修改内容：展示 provider 配置状态、health snapshot、usage/cost snapshot，并保留原调用统计/日志。
- 完成标准：只读，无编辑按钮；loading/error/empty 正常；不展示敏感字段。
- 验证方式：typecheck/build。
- 风险说明：成本面板必须标注 unknown/null，不误导为精确账单。

### B12D-03

- [x] 已完成
- 任务名称：12D 验证与文档收口
- 优先级：P0
- 来源需求：REQ-B12-006
- 涉及文件：`validation.md`、`audit.md`、`handoff.md`
- 修改内容：记录修改文件、验证结果、未实施在线编辑/真实 probe/成本估算说明。
- 完成标准：验证结果可复核，后置项清晰。
- 验证方式：`npx tsc --noEmit`、`npm run build`、`git diff --check`。
- 风险说明：如 dirty tree 存在无关失败，必须独立标注。

## P0-01

- [x] 设计审查完成；后置实现另列 backlog
- 任务名称：AI Provider / Routing / Cost 现状审计
- 优先级：P0
- 来源需求：REQ-B12-001 ~ REQ-B12-005
- 涉及文件：`backend/app/config.py`、`backend/app/services/ai_service.py`、`backend/app/services/ai_gateway.py`、`backend/app/models/ai_call_log.py`、`backend/app/models/ai_run.py`、`backend/tests/`
- 修改内容：只读审计 provider 配置、fallback、task_type/provider、token/cost/budget/health/routing/熔断现状。
- 完成标准：形成证据表，明确缺口和不实施项。
- 验证方式：指定 `rg` 命令与关键文件行号。
- 风险说明：当前代码处于大脏工作区，需避免把既有改动误判为本批改动。

## P0-02

- [x] 设计审查完成；后置实现另列 backlog
- 任务名称：Batch 12 范围冻结与禁止项确认
- 优先级：P0
- 来源需求：硬约束
- 涉及文件：workflow docs
- 修改内容：冻结 Batch 12 不进入 Prompt 后台、A/B、热更新、stream 正式链路、实体自动写入等禁止项。
- 完成标准：requirements/design/handoff 均包含禁止项。
- 验证方式：文档审查。
- 风险说明：治理层很容易扩张成 Prompt 平台或计费平台。

## P0-03

- [x] 设计审查完成；后置实现另列 backlog
- 任务名称：ProviderProfile / ModelProfile 最小数据模型设计
- 优先级：P0
- 来源需求：REQ-B12-001
- 涉及文件：workflow design；未来可选 `backend/app/models/`、`backend/app/schemas/`、`backend/alembic/versions/`
- 修改内容：评估 provider/model profile 字段、secret 边界，以及 Phase 12A 是否应先用代码级 typed policy。
- 完成标准：明确 Phase 12A 首批建议使用 `ProviderPolicy` / `ModelPolicy` typed config，不新增表、不保存 API key。
- 验证方式：typed policy contract tests 设计；数据库模型仅作为后置候选。
- 风险说明：过早引入 price/context 字段和 migration 会扩大 Phase 12A 范围。

## P0-04

- [x] 设计审查完成；后置实现另列 backlog
- 任务名称：RoutingRule 最小合同设计
- 优先级：P0
- 来源需求：REQ-B12-002
- 涉及文件：workflow design；未来 typed routing policy / routing resolver
- 修改内容：设计 task_type primary provider/model、fallback_chain、capability 约束。
- 完成标准：建议 Phase 12A 先用 `RoutingPolicy` typed config 覆盖现有 Prompt Registry preferred_provider 的所有 task_type。
- 验证方式：task_type resolver tests。
- 风险说明：RoutingRule 与 Prompt Registry 重叠会破坏职责边界。

## P0-05

- [x] 设计审查完成；后置实现另列 backlog
- 任务名称：Gateway routing adapter 设计
- 优先级：P0
- 来源需求：REQ-B12-002、REQ-B12-003
- 涉及文件：`backend/app/services/ai_gateway.py`、未来 routing resolver
- 修改内容：设计 Gateway 未来如何读取 routing policy 并保持现有 wrapper 合同；本轮不修改 Gateway。
- 完成标准：`call_text/call_vision/call_general/call_stream` response contract 不变。
- 验证方式：mock provider route resolution tests。
- 风险说明：直接改 `_call_with_fallback()` 可能破坏已有 provider tests。

## P0-06

- [x] 设计审查完成；后置实现另列 backlog
- 任务名称：Fallback chain 显式化设计
- 优先级：P0
- 来源需求：REQ-B12-003
- 涉及文件：routing service、`ai_call_logs.attempts`
- 修改内容：设计 fallback chain 数据结构、retryable 分类、fallback reason。
- 完成标准：attempts 能解释尝试顺序、失败原因和最终 provider_used。
- 验证方式：429/500/timeout/mock provider attempts tests。
- 风险说明：配置错误可能导致高成本模型被意外优先调用。

## P0-07

- [x] 设计审查完成；后置实现另列 backlog
- 任务名称：Token usage / cost 统计可行性审计
- 优先级：P0
- 来源需求：REQ-B12-004
- 涉及文件：`ai_service._call_provider()`、provider response parser、`ai_call_logs`
- 修改内容：审计 provider 是否返回 usage，设计 actual/unknown/estimated 边界。
- 完成标准：明确不得按字符数伪造 token usage。
- 验证方式：provider response fixture tests。
- 风险说明：把 unknown 当 0 会误导成本面板。

## P0-08

- [x] 设计审查完成；后置实现另列 backlog
- 任务名称：UsageDaily 聚合设计
- 优先级：P0
- 来源需求：REQ-B12-004
- 涉及文件：未来 `ai_usage_daily` model/service/job
- 修改内容：设计每日聚合维度、幂等 upsert、latency/fallback/success 聚合。
- 完成标准：以 `ai_call_logs` 为事实源，不依赖 `ai_runs`。
- 验证方式：aggregation unit tests with fixture logs。
- 风险说明：时区和重复聚合可能造成统计偏差。

## P0-09

- [x] 设计审查完成；后置实现另列 backlog
- 任务名称：Provider health check 设计
- 优先级：P0
- 来源需求：REQ-B12-005
- 涉及文件：未来 health service、health events model
- 修改内容：设计 health probe、status、latency、safe error、事件保留策略。
- 完成标准：health check 不生成 ai_run，不等同业务成功率。
- 验证方式：mock health probe tests。
- 风险说明：真实 provider health 验证有成本与速率限制。

## P0-10

- [x] 设计审查完成；后置实现另列 backlog
- 任务名称：Failure classification 与 error safe message 设计
- 优先级：P0
- 来源需求：REQ-B12-003、REQ-B12-005
- 涉及文件：Gateway、ai_service、logs、health events
- 修改内容：设计 rate_limit、timeout、auth_error、provider_error、parse_error 等分类。
- 完成标准：错误可解释但不泄露 secret / request body / provider 原文敏感内容。
- 验证方式：error truncation and sanitization tests。
- 风险说明：provider error body 可能包含敏感回显。

## P0-11

- [x] 设计审查完成；后置实现另列 backlog
- 任务名称：与 ai_call_logs / ai_runs 的边界设计
- 优先级：P0
- 来源需求：关键设计边界
- 涉及文件：`ai_call_logs`、`ai_runs`、usage/cost/health docs
- 修改内容：冻结 technical facts 与 business audit facts 的边界。
- 完成标准：usage/cost/health 不从 `ai_runs.output_data` 取数。
- 验证方式：schema and service dependency review。
- 风险说明：混用事实源会导致审计、成本和人工流转语义混乱。

## P0-12

- [x] 设计审查完成；后置实现另列 backlog
- 任务名称：管理端只读面板设计
- 优先级：P0
- 来源需求：REQ-B12-006
- 涉及文件：`src/app/manage/(workspace)/ai/`、`src/lib/api/`
- 修改内容：设计 provider/routing/usage/health 只读 UI 与 admin-only API。
- 完成标准：匿名 401，不显示 secret，不提供在线编辑。
- 验证方式：frontend typecheck + browser admin/anon checks。
- 风险说明：只读面板可能被误解为实时账单或在线控制台。

## P0-13

- [x] 设计审查完成；后置实现另列 backlog
- 任务名称：验证矩阵设计
- 优先级：P0
- 来源需求：全部
- 涉及文件：backend tests、frontend tests、workflow validation
- 修改内容：设计 Phase 12A-D 的测试矩阵与真实 provider 验证边界。
- 完成标准：mock 与真实 provider 验证措辞分开。
- 验证方式：test plan review。
- 风险说明：mock provider 通过不能当作真实 provider 可用性的验收结论。

## P0-14

- [x] 设计审查完成；后置实现另列 backlog
- 任务名称：实施分期与审批建议
- 优先级：P0
- 来源需求：Batch 12 分期
- 涉及文件：workflow docs、future implementation workflows
- 修改内容：拆分 Phase 12A/12B/12C/12D，每阶段独立审批。
- 完成标准：Phase 12A 不含 usage/cost/health UI 大范围能力。
- 验证方式：scope review。
- 风险说明：一次性大爆炸会增加 migration、Gateway、UI、真实 provider 验证的耦合。

## P0-15

- [x] 设计审查完成；后置实现另列 backlog
- 任务名称：handoff 与下一步
- 优先级：P0
- 来源需求：handoff 要求
- 涉及文件：`handoff.md`
- 修改内容：输出推荐先实施阶段、typed policy / migration / model / Gateway / manage / provider 验证需求、与 RISK-B11-003 关系。
- 完成标准：用户可直接审批 Phase 12A 或要求调整。
- 验证方式：handoff review。
- 风险说明：设计完成不等于 Batch 12 已实现。
