# Phase C Execution Preparation：设计

## 目标

以只读证据建立当前系统真实状态的可复核基线，为后续 Migration Gate 提供明确的通过条件、缺口与阻断风险。

## 证据来源

1. Phase A 审计文档，尤其是 `audit/migration-gate.md` 及同目录审计材料。
2. Phase B 的 `source-of-truth.md`、`owner-coverage-matrix.md`、`auth-boundary-design.md`、`schema-ownership.md`、`backup-validation-plan.md`、`validation.md`。
3. 当前仓库的 Alembic 源码、模型、router/依赖实现与配置声明。
4. 当前数据库的只读元数据与聚合统计（若连接可用）；不可用时必须记录为未验证，不以代码推断替代。

## 执行顺序

1. 冻结 Alembic revision/head/history。
2. 读取 schema 元数据并形成表、字段、索引、外键、约束清单。
3. 对核心表执行只读数据聚合，记录行数、主键范围和时间范围。
4. 逐实体建立 owner mapping readiness，区分 explicit owner 与 inferred owner。
5. 审计 `Base.metadata.create_all`、Alembic `env.py`、target metadata 与 migration chain。
6. 建立 public/authenticated user/admin/worker × entity 权限测试矩阵。
7. 汇总未完成证据，确认 Migration Gate 仍为 `BLOCKED`。

## 证据纪律

- 数据数量仅作为 baseline，不作为迁移正确性证明。
- 不把 `created_by` 自动解释为 `owner_id`。
- 不把模型声明、文档声明或环境变量声明当作数据库真实状态。
- 数据库、migration 与应用均保持只读；任何命令若有写入风险则跳过并记录。
- 现有 dirty worktree 不归属于本任务，不能被覆盖、清理或纳入结论。
