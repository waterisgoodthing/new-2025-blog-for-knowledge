# Personal Learning System V2 统一大方案

## 任务目标

将既有 Personal Learning System V2 目标架构、MVP 阶段基线与 2026-07-20 的 UI、内容、文件系统和迁移方案合并为一套唯一、可分阶段审批和验收的主方案。

## 影响架构线

- Frontend / original blog：`src/`
- Personal learning backend：`backend/`
- Shared infrastructure：认证、公开/管理 API 边界、附件存储、备份恢复、发布与搜索基础设施

I0–I2 仅完成规划、审计和隔离验证；已批准的 I3 则修改了学习后端、前端私有管理页和 Alembic migration，并只在恢复出的隔离数据库中迁移验证。未修改源库、生产数据或部署状态。

## 当前状态

`I0–I10 TECHNICAL PASS / I10 GATE BLOCKED; I11 APPROVED / OWNER GATE BLOCKED`。I7 文件工作区、I8 Markdown/版本/WikiLink/反链/权限搜索、I9 治理页面和 I10 源库只读 clone dry-run 均有主验证与独立交叉验证；I10 的 owner/backfill 责任仍未收敛。I11 单独批准已于 2026-07-26 收到，但 E-05/E-06 尚未执行；生产部署、源库迁移和权威切换未授权。

本工作区的规划已根据 2026-07-20 审查细化；细化本身不代表 A–F 任何实施项获批或完成。

## 文档

- [统一主方案](./master-plan.md)
- [设计边界](./design.md)
- [需求与验收](./requirements.md)
- [任务清单](./tasks.md)
- [递进执行计划](./incremental-plan.md)
- [I0 冻结审查与来源索引](./i0-freeze-audit.md)
- [I1 边界与恢复审计](./i1-boundary-recovery-audit.md)
- [I2 最小学习闭环浏览器验证](./i2-learning-loop-validation.md)
- [I3 文件化计划](./i3-attempt-capture-plan.md)
- [I3 现状发现](./i3-attempt-capture-findings.md)
- [I3 进度](./i3-attempt-capture-progress.md)
- [I4 文件化计划](./i4-dashboard-navigation-plan.md)
- [I4 现状发现](./i4-dashboard-navigation-findings.md)
- [I4 进度](./i4-dashboard-navigation-progress.md)
- [I4 closure-fix 计划](./i4-closure-fix-plan.md)
- [I4 closure-fix 现状](./i4-closure-fix-findings.md)
- [I4 closure-fix 进度](./i4-closure-fix-progress.md)
- [I5 准备计划](./i5-preparation-plan.md)
- [I5 准备现状](./i5-preparation-findings.md)
- [I5 准备设计](./i5-preparation-design.md)
- [I5 准备需求](./i5-preparation-requirements.md)
- [I5 准备任务清单](./i5-preparation-tasks.md)
- [I5 准备进度](./i5-preparation-progress.md)
- [I5 资料设置 ADR](./i5-profile-settings-adr.md)
- [I6 采集到草稿深化链路](../i6-capture-draft-chain/README.md)
- [本轮文档校验](./validation.md)
- [旧方案审查依据](../../architecture/personal-learning-system-v2.md)
- [MVP 范围基线](../../architecture/mvp-scope.md)
- [现有迁移门槛](../personal-learning-system-v2/audit/migration-gate.md)

## 事实来源与文档层级

1. 本工作区中的 `master-plan.md`、`design.md`、`requirements.md` 和 `tasks.md` 是**待批准的目标设计**，不是当前实现事实。
2. 当前实现事实必须以代码、数据库只读审计、浏览器验收和带日期的验证记录为准。
3. `docs/architecture/personal-learning-system-v2.md` 是既有目标架构；`docs/architecture/mvp-scope.md` 是既有 MVP 范围基线。两者都不是当前运行时事实的替代品。
4. `../personal-learning-system-v2/audit/migration-gate.md` 是历史审查依据。其 revision、恢复证据和风险结论必须在 Phase 0 的 B-03/B-04 中重新验证，不能直接用作当前数据库状态证明。
5. A-04 完成前，上述文件之间如有术语或模型差异，以本工作区的“待决策/待核验”状态处理，不得据此推断已经迁移、切换或删除旧能力。I0 的实际盘点见 [I0 冻结审查与来源索引](./i0-freeze-audit.md)。
