# Risks

## RISK-B12-001：provider routing 规则扩大 Gateway 复杂度

- 类型：架构 / 可维护性
- 描述：Gateway 当前是薄封装，如果直接把 profile、routing、health、cost 都塞入 Gateway，会造成调用链复杂化。
- 影响：AI 调用稳定性、测试维护成本。
- 严重程度：高
- 当前状态：设计中
- 建议措施：Phase 12A 只引入 routing adapter，Gateway wrapper 合同保持不变。
- 是否进入下一轮需求：是

## RISK-B12-002：token usage 缺失导致成本统计不完整

- 类型：数据准确性
- 描述：当前未持久化 provider token usage；部分 provider 可能不返回 usage。
- 影响：成本面板不完整。
- 严重程度：高
- 当前状态：未处理
- 建议措施：actual usage nullable；unknown 明确展示；不得伪造。
- 是否进入下一轮需求：是

## RISK-B12-003：fallback chain 配置错误可能导致成本或延迟异常

- 类型：成本 / 性能
- 描述：错误的 fallback chain 可能优先调用高成本模型，或在失败时拉长 latency。
- 影响：调用成本、用户体验。
- 严重程度：高
- 当前状态：未处理
- 建议措施：fallback chain 加测试、max_cost/max_latency 先设计后启用。
- 是否进入下一轮需求：是

## RISK-B12-004：provider health check 与真实业务成功率不一致

- 类型：监控语义
- 描述：health probe 成功不代表业务 prompt/schema 成功；业务失败也可能不是 provider down。
- 影响：误判 provider 稳定性。
- 严重程度：中
- 当前状态：未处理
- 建议措施：health events 与 ai_call_logs 聚合分开展示。
- 是否进入下一轮需求：是

## RISK-B12-005：多供应商配置可能泄露 provider/model 策略

- 类型：安全 / 信息泄露
- 描述：管理端或 API 若暴露过多 provider/model/base_url 细节，可能泄露内部策略。
- 影响：安全边界、运维隐私。
- 严重程度：中
- 当前状态：未处理
- 建议措施：仅管理员可见；不显示 secret；必要时隐藏完整 base_url。
- 是否进入下一轮需求：是

## RISK-B12-006：管理端成本面板可能误导为精确账单

- 类型：产品 / 数据解释
- 描述：estimated cost 不是账单；unknown usage 不应展示为 0。
- 影响：错误决策。
- 严重程度：中
- 当前状态：未处理
- 建议措施：UI 明确 actual / estimated / unknown，显示免责声明。
- 是否进入下一轮需求：是

## RISK-B12-007：动态路由可能破坏 task_type 与 Prompt Registry 的稳定合同

- 类型：架构 / 合同
- 描述：若 routing rule 改变 json_mode/schema expectations，可能与 Prompt Registry 冲突。
- 影响：解析、校验、Run 状态。
- 严重程度：高
- 当前状态：未处理
- 建议措施：RoutingRule 只管 provider/model/fallback；schema/json_mode 仍由 Prompt Registry 决定。
- 是否进入下一轮需求：是

## RISK-B12-008：真实 provider 验证成本与速率限制风险

- 类型：外部依赖 / 成本
- 描述：health check、fallback 与真实 provider 验证可能触发费用或 rate limit。
- 影响：测试稳定性、成本。
- 严重程度：中
- 当前状态：未处理
- 建议措施：mock 测试为主；真实 provider 验证单独审批、限频、记录成本边界。
- 是否进入下一轮需求：是
