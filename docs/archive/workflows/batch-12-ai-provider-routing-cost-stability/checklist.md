# Checklist

## 文档完整性

- [x] README.md 已创建
- [x] requirements.md 已创建
- [x] design.md 已创建
- [x] tasks.md 已创建
- [x] checklist.md 已创建
- [x] risks.md 已创建
- [x] validation.md 已创建
- [x] handoff.md 已创建

## 范围约束

- [x] 本轮修改 backend AI shared infrastructure、manage AI 只读面板与 workflow 文档
- [x] 本轮未新增 migration
- [x] 本轮未新增数据库表
- [x] 本轮已实施 Phase 12A typed policy 最小内核
- [x] 本轮已实施 Phase 12B usage/cost 无表最小聚合
- [x] 本轮已完成 Phase 12C provider health / 降级治理设计审查
- [x] 本轮已实施 Phase 12C 最小 Health Snapshot API
- [x] 本轮已实施 Phase 12D 管理端只读面板
- [x] P0-01 至 P0-15 已完成设计审查
- [x] 明确不做 Prompt 后台 / A/B / 热更新 / 效果评测
- [x] 明确不重新启用正式业务 stream 生成链路
- [x] 明确不伪造 token usage / cost
- [x] 明确不从 `ai_runs.output_data` 推导 usage/cost/health

## 设计覆盖

- [x] 记录当前 provider 配置位置
- [x] 记录当前 fallback 链
- [x] 记录 task_type 与 provider 当前关系
- [x] 记录 token usage / cost / budget / health 缺口
- [x] 设计 ai_call_logs 与 ai_runs 边界
- [x] 设计 Routing 与 Prompt Registry 边界
- [x] 设计 Cost 统计边界
- [x] 设计 Health Check 边界
- [x] 明确 Phase 12A 首批建议使用代码级 typed policy，不先建表
- [x] 明确 Phase 12B 只做无表聚合，actual token/cost unknown 时保持 null
- [x] 明确 Phase 12C 已实施 health snapshot，但不实施真实 health probe / 熔断 / 降级
- [x] 明确 Phase 12D 只读展示 provider / usage-cost / health，不提供在线编辑或真实 probe

## 审批状态

- [x] Phase 12A 未从 P0 设计审查自动实施，而是在用户明确批准后实施
- [x] Phase 12A 已在用户批准后实施
- [x] Phase 12B 已在用户批准后实施
- [x] Phase 12C 最小 Health Snapshot API 已在用户批准后实施
- [x] Phase 12D 管理端只读面板已在用户批准后实施
