# Requirements

## 背景

Batch 9-11 已完成 AI 基础链路：Gateway、Prompt Registry、Validator、`ai_call_logs`、`ai_runs`、Run 审计与人工流转。Batch 12 的任务是把 provider、model、fallback、usage/cost 与 health 从隐式工程逻辑推进到显式治理层。

本轮先完成设计审查，随后在用户批准后实施 Phase 12A Typed Provider/Routing Policy 最小内核。

本轮 P0-01 至 P0-15 是设计审查阶段必答项；Phase 12A 已单独获批并实施；Phase 12B 已单独获批并完成无表最小聚合；Phase 12C 已完成设计审查并实施最小 Health Snapshot API；Phase 12D 仍需后续审批。

## 当前基础事实

1. AI Gateway 已存在，并支持 `call_text` / `call_general` / `call_vision` / `call_stream` wrapper。
2. `ai_call_logs` 已记录 provider、model、latency、success、fallback、attempts、input_summary、prompt_version 等技术调用信息。
3. `ai_runs` 已记录业务 Run 审计状态，包括 task_type、provider/model、status、validation_status、review_status、output_data、error、latency。
4. Prompt Registry 已提供 task_type、prompt_version、schema、json_mode、preferred_provider、max_tokens 等工程合同。
5. 正式可审计 AI 生成已统一走非流式 Run 链路。
6. 旧 stream endpoint 已 deprecated / compatibility-only。
7. Batch 12 不得重新引入正式业务对伪流式 endpoint 的依赖。

## 只读审计问题与现状答案

| 问题 | 当前答案 |
|---|---|
| 当前 provider 配置在哪里？ | `backend/app/config.py` 与 `backend/.env.example` 中的 `AI_*`、`DASHSCOPE_*`、`DEEPSEEK_*`；运行时由 `backend/app/services/ai_service.py::_get_providers()` 组装。 |
| 当前 fallback 链如何定义？ | `_select_providers(required_caps, preferred)` 先按 capabilities 过滤，再把 preferred provider 排在最前；`_call_with_fallback()` 顺序尝试 provider。没有数据库配置、没有显式 chain 对象。 |
| 当前 task_type 与 provider 的关系在哪里？ | Prompt Registry 的 `preferred_provider` 记录在 `PromptTemplate`；Gateway `_resolve_registry_defaults()` 读取它；`call_vision()` 仍硬编码 preferred `dashscope_vision`。 |
| 当前是否记录 token usage？ | 未发现 actual input/output token 持久化字段。 |
| 当前是否记录 cost？ | 未发现 cost 字段或 cost 聚合。 |
| 当前是否有预算限制？ | 未发现 budget/quota 表或预算拒绝逻辑；只有 `ai_analyze_service.check_rate_limit()` 的内存全局请求频率限制。 |
| 当前是否有 provider health 状态？ | `get_provider_status()` 只返回配置状态，不执行真实 health check，也不记录健康事件。 |
| 当前是否有模型级别禁用或降级？ | 未发现 enabled/disabled model profile；provider 是否可用取决于 key 是否配置。 |
| 当前是否有 per-task 路由规则？ | 只有 Prompt Registry 的 preferred_provider 与 Gateway wrapper fallback 默认值，未发现独立 RoutingRule。 |
| 当前是否有失败熔断？ | `_call_with_fallback()` 会对 retryable error 尝试下一个 provider，但没有连续失败阈值、熔断窗口或临时禁用状态。 |

## 功能需求

### REQ-B12-001 Provider / Model 显式配置

- 输入：现有 env provider 与 model 配置、provider capability。
- 处理：设计 ProviderPolicy / ModelPolicy typed config，并评估未来 ProviderProfile / ModelProfile 数据模型。
- 输出：Phase 12A 首批推荐代码级 typed policy；数据库模型作为后置候选。
- 失败处理：缺少 provider key 时必须 fail closed，不得暴露 secret。
- 验收：能表达当前 deepseek、dashscope_vision、qwen_general 三类 provider/model。

### REQ-B12-002 task_type 路由规则

- 输入：task_type、required capabilities、Prompt Registry defaults。
- 处理：设计 RoutingPolicy typed config，将 provider/model/fallback 从 Prompt Registry 职责中分离。
- 输出：task_type 级别 primary provider/model 与 fallback_chain；数据库 RoutingRule 后置。
- 失败处理：规则缺失时回退到现有 Prompt Registry preferred_provider，不破坏当前调用。
- 验收：能表达 `analyze_text -> deepseek`、`analyze_mistake -> dashscope_vision`、`recommendation -> qwen_general`。

### REQ-B12-003 Fallback 显式化

- 输入：provider attempts、错误类别、routing rule。
- 处理：设计显式 fallback chain 与 retryable 分类。
- 输出：可审计 attempts 与 fallback reason。
- 失败处理：所有 provider 失败时只返回 safe error，不暴露 API response 原文中的敏感信息。
- 验收：attempts 中能解释每次尝试与最终 provider_used。

### REQ-B12-004 Usage / Cost 统计

- 输入：`ai_call_logs` 技术调用事实、provider 返回 usage（如有）。
- 处理：按日聚合 call_count、success_count、failure_count、fallback_count、latency、token usage、estimated_cost。
- 输出：Phase 12B 可选 `ai_usage_daily` 或等价聚合视图。
- 失败处理：provider 不返回 token usage 时记录 unknown/null，不得伪造。
- 验收：actual_tokens 与 estimated_tokens 明确区分。

### REQ-B12-005 Health / 降级治理

- 输入：health check 结果与业务调用失败事实。
- 处理：设计 provider/model health event、failure classification、连续失败阈值与临时降级策略。
- 输出：当前 provider/model 可用性、降级建议与健康事件历史设计。
- 失败处理：health check 失败不等于业务调用失败，不能直接污染 `ai_runs`。
- 验收：health 与 `ai_call_logs` 成功率有清晰边界。

12C 设计审查结论：

- 当前 `get_provider_status()` 只代表配置状态。
- 当前无真实 health probe、health event、熔断、cooldown 或 provider/model 临时禁用。
- 已完成基于 `ai_call_logs` 的 recent health snapshot。
- 后续最小实现建议继续做代码级 health policy、safe error classification、可选 cooldown。
- `ai_provider_health_events` 表和真实 provider probe 均需单独审批。

### REQ-B12-006 管理端只读展示

- 输入：provider profiles、routing rules、usage/cost、health events。
- 处理：设计 `/manage/ai` 只读面板，不做在线编辑。
- 输出：管理员可查看 provider/routing/usage/health。
- 失败处理：匿名用户不得访问 provider/routing/cost 数据。
- 验收：后台只读展示不泄露 API key、authorization、cookie、secret、token、storage_key。

## 非功能需求

- 安全：不得保存 API key；不得把敏感字段写入日志或响应。
- 审计：`ai_call_logs` 仍为技术调用事实源；`ai_runs` 仍为业务审计事实源。
- 成本：不得伪造 token usage 或 cost。
- 兼容：不得破坏现有 Gateway、Prompt Registry、Run 列表与 AI endpoint response schema。
- 可维护：分阶段实施，避免一次性引入过多表和后台能力。

## 硬边界

Batch 12 不得：

- 在本轮新增 migration
- 在本轮新增数据库表
- 在本轮修改 Gateway 运行逻辑
- 在本轮修改 provider 调用逻辑
- 在本轮修改前端页面
- 进入 Prompt 后台
- 做 Prompt A/B、热更新、效果评测
- 重新启用正式业务 stream 生成链路
- 宣称已实现完整 provider token streaming 审计
- 让 AI 输出直接写正式 question / mistake / review_item
- 绕过 `ai_runs`
- 删除 `ai_call_logs` 或 `ai_runs`
- 保存 API key
- 伪造 token usage 或 cost
- 从 `ai_runs.output_data` 推导 usage/cost/health
- 把 mock provider 验证写成真实 provider 验证
- 修改公开 API
- 向匿名用户暴露 provider/routing/cost 数据
