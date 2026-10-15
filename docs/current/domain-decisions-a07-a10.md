# 领域语义裁决记录（A07 / A09 / A10）与 DR-B06 评估

日期：2026-10-13。Lead：opencode（Primary Owner）。来源：`audits/ARCHITECTURE_AUDIT.md` A07/A09/A10、`architecture/DESIGN_RATIONALE_REVIEW.md` DR-B06。

本记录落实"先选择、再实现"的要求；凡需 schema 迁移或产品决策者，明确记为 DECIDED/DEFERRED，不擅自迁移或新建模型。

## A07 — 历史 KP 归因
- **现状（源码事实）**：`Attempt` 无题目版本/KP 快照；`kp_analytics_service` 用当前 `QuestionKnowledgePoint` join 历史 practice `Attempt`。因此改题目的 KP 会重新归因历史作答。
- **裁决**：**保留"当前内容归因"**；不新增作答时快照。
- **理由**：作答时快照需 schema 变更 + 存量回填（G2），属难以逆转的数据操作；无证据表明该归因已造成实际错误。审计亦要求"先选择归因口径，不立即新建复杂事件系统"。
- **影响与边界**：历史作答随当前 KP 变化而重新归因，已如实记录；如需快照，另立 G2 迁移并单独授权。
- **状态**：DECIDED（不实现快照）。

## A09 — Practice 判答语义
- **现状**：Practice 值等同判答（`attempt_service`）；Review 三态判定（自动/半自动/人工）。
- **裁决**：**维持两种语义并存**，不统一。
- **理由**：属于原修复"第二阶段"（D07/FW05 判分合同 → N05），非当前发布阻断；统一需先定判分合同。
- **状态**：DECIDED（延后统一）。

## A10 — KP 掌握度 / 持久学习计划
- **现状**：无独立 KP mastery/BKT，无持久 StudyPlan/StudyTask；已有 `ReviewItem.mastered` 与 KP 统计。
- **裁决**：**明确不作为当前目标**（项目自身定义为 NOT_IMPLEMENTED / 远期能力）。
- **状态**：DEFERRED（非目标，需产品决策才立项）。

## DR-B06 — Dashboard 聚合
- **现状（已核实）**：`dashboard_service` 分块查询、按块局部 `rollback`，并区分 `ready` / `empty` / `unavailable`（如 `practice_available`、`storage_status`）；查询为串行。
- **裁决**：**保留串行**（符合 ADR003 "先测延迟" 指引）；"区分无任务 vs 模块不可用"已满足。
- **约束（若将来并行）**：每个并发分支必须用独立 session，不得对同一 `AsyncSession` 直接 `gather`。
- **状态**：REVIEWED — 无需代码变更。
