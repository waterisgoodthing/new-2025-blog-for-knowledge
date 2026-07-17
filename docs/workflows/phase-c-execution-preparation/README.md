# Phase C：Execution Preparation

## 任务目标

在 Migration Gate 仍为 `BLOCKED` 的前提下，冻结当前数据库、schema、数据、owner、schema authority 与认证边界的只读证据，并生成后续 Migration Gate 所需的准备报告。

## 涉及架构线与领域

- 架构线：个人知识后端 FastAPI/PostgreSQL 线；同时审计其与静态博客/GitHub 导出 seam 的边界。
- 领域：`notes`、`questions`、`mistakes`、`review`、`attachments`、`AI`、`auth`、共享数据库基础设施。

## 当前状态

Phase B design completed；Migration Gate = `BLOCKED`。本任务仅允许只读检查与文档生成，未获批准前不执行 Phase C 报告生成任务。

## 文档

- [design.md](./design.md)
- [requirements.md](./requirements.md)
- [tasks.md](./tasks.md)

## Phase C+ Closure Design

在 Phase C 只读证据基础上，已生成 Migration Readiness Closure Design。该阶段仍只做设计与验证计划，不执行 migration、数据修改或权限修改：

- [schema-authority-convergence-plan.md](./schema-authority-convergence-plan.md)
- [owner-migration-design.md](./owner-migration-design.md)
- [backup-restore-validation-plan.md](./backup-restore-validation-plan.md)
- [auth-integration-test-plan.md](./auth-integration-test-plan.md)
- [migration-gate-closure-checklist.md](./migration-gate-closure-checklist.md)

## Phase C+1 Schema Authority Closure Audit

本阶段仅执行只读 repository/database metadata 与 migration history inspection，并生成：

- [schema-entrypoints.md](./schema-entrypoints.md)
- [alembic-metadata-coverage.md](./alembic-metadata-coverage.md)
- [schema-three-way-drift-report.md](./schema-three-way-drift-report.md)
- [schema-authority-decision.md](./schema-authority-decision.md)
- [schema-authority-validation.md](./schema-authority-validation.md)

## Phase C+2 Schema Provenance & Drift Closure Audit

本阶段只读审计输出：

- [migration-provenance-inventory.md](./migration-provenance-inventory.md)
- [guest-table-origin-report.md](./guest-table-origin-report.md)
- [schema-coverage-final-matrix.md](./schema-coverage-final-matrix.md)
- [column-drift-ownership-report.md](./column-drift-ownership-report.md)
- [index-drift-report.md](./index-drift-report.md)
- [schema-provenance-validation.md](./schema-provenance-validation.md)

Phase C 已生成：

- [migration-baseline.md](./migration-baseline.md)
- [schema-inventory.md](./schema-inventory.md)
- [data-baseline.md](./data-baseline.md)
- [owner-mapping-readiness.md](./owner-mapping-readiness.md)
- [schema-authority-audit.md](./schema-authority-audit.md)
- [auth-test-matrix.md](./auth-test-matrix.md)
- [phase-c-gate-checklist.md](./phase-c-gate-checklist.md)

## 禁止项

不修改业务代码、数据库、认证配置、部署配置或 migration；不执行 `alembic upgrade/downgrade`、`pg_dump`、`pg_restore`、删除旧表或生产数据写入。
