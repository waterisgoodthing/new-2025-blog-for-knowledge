# Schema Authority Convergence Plan

日期：2026-07-13  
范围：Phase C+ Migration Readiness Closure Design  
状态：设计完成；未执行 schema、migration 或应用代码修改。

## 1. Current State

### 1.1 Alembic

已有基线证明 Alembic 当前 revision 为 `018`，`018` 为 `head`，历史为单链。该位置事实不能证明实际数据库 schema 与 model/metadata 一致。

`alembic check` 当前失败，报告了 5 项 drift：

| Drift | 当前证据 | 本阶段判定 |
|---|---|---|
| `folders.sort_order` nullable mismatch | database 与 model 的 nullable 声明不同 | UNKNOWN：需三方对账后再判定 database/model/migration 缺口 |
| `folders.created_at` nullable mismatch | database 与 model 的 nullable 声明不同 | UNKNOWN：需三方对账后再判定 |
| `folders.updated_at` nullable mismatch | database 与 model 的 nullable 声明不同 | UNKNOWN：需三方对账后再判定 |
| `notes.sort_order` nullable mismatch | database 与 model 的 nullable 声明不同 | UNKNOWN：需三方对账后再判定 |
| `idx_notes_folder_id` | database 存在，而 autogenerate 认为 metadata 中已移除 | UNKNOWN：需核对索引语义、命名、migration 历史和 metadata 注册 |

### 1.2 `create_all` 影响范围

证据文件确认 `backend/main.py` 的 application lifespan 调用 `Base.metadata.create_all`。这使应用启动成为潜在的 schema provisioning 入口，能够尝试创建缺失表/结构；其是否已对当前生产库造成具体变更，现有证据未证明，标记为 UNKNOWN。

Alembic `env.py` 同时以 `Base.metadata` 作为 target metadata 执行版本化 migration。`backend/app/models/__init__.py` 注册完整模型集合，但 `env.py` 的显式 import 覆盖范围不透明，`managed_content_entries`、`ai_call_logs`、`ai_runs`、`capture_items`、session/audit 等模型是否全部进入 autogenerate 对照，必须另做受控 coverage report，当前为 UNKNOWN。

### 1.3 Drift 类型

当前 drift 属于 nullable declaration drift 与 index/metadata drift。它们不能被直接解释为“数据库错误”或“模型错误”；也不能通过启动 `create_all`、自动生成 migration 或直接改模型来掩盖。当前 schema authority 结论仍为“不唯一”，Migration Gate 继续 BLOCKED。

## 2. Target Architecture

目标是单一、可审计的 schema authority：

```text
Application
     |
     v
Alembic Migration
     |
     v
Database Schema
```

约束如下：

1. Alembic migration chain 是唯一的 schema provisioning 与变更入口。
2. 应用启动只执行 revision/health/readiness 检查，不执行 `create_all`、upgrade 或 downgrade。
3. 新 migration 只能在 drift 三方对账、owner/备份/权限 Gate 关闭后另行设计并获批。
4. 测试建库使用隔离 fixture 或明确的测试 schema 策略；不得以生产启动路径的 `create_all` 作为测试策略的隐式依据。

## 3. Migration Risk Analysis

### 删除 `create_all` 的风险

- 本地空库或未初始化测试库可能在应用启动时不再自动生成表，导致启动/测试失败；具体受影响环境和脚本当前未在证据中验证，UNKNOWN。
- 隐藏依赖 `create_all` 的开发流程可能暴露未纳入 migration chain 的模型或表。
- 已存在的 drift 不会因删除入口而消失，反而会被更早暴露；这属于预期的可见性提升，不是修复证据。

### 本地开发策略

推荐：显式创建隔离本地数据库后执行已批准的 Alembic chain；应用启动不负责建库。若需要快速测试，使用专用 test fixture/临时数据库，并记录其 schema 来源。具体 fixture 命令、数据库命名和清理方式当前未由证据提供，UNKNOWN，进入 Phase D 前须补齐。

### 测试环境策略

测试环境应从干净数据库或新鲜恢复副本开始，以 Alembic 迁移到目标 revision，再运行 schema、数据、API 和权限测试。共享数据库不得作为 destructive downgrade 或 owner backfill 的测试对象。

### 生产环境策略

生产部署前由发布流程显式执行已批准的 migration，并记录 revision、备份、恢复演练和 smoke evidence。应用启动只检查 revision/readiness；生产环境不得依赖 `create_all` 自动补齐 schema。生产当前是否已按此策略运行，现有证据未证明，UNKNOWN。

## 4. Drift Resolution Strategy

本表是归因与验证设计，不是 migration 生成指令。

| Drift | 先行核对 | 允许的分类结果 | 关闭条件 |
|---|---|---|---|
| `folders.sort_order` nullable | database column metadata、完整 model 声明、所有历史 migration、业务写入/读取假设 | database drift / model error / migration missing / metadata registration issue / UNKNOWN | 有逐项三方 diff、数据可空性影响评估、owner 批准的分类；未分类不得生成 migration |
| `folders.created_at` nullable | 同上，另核对默认值和既有 NULL 行 | database drift / model error / migration missing / metadata registration issue / UNKNOWN | 证明 NULL 行数量、来源与兼容策略；现有基线未提供 NULL 行证据，故当前 UNKNOWN |
| `folders.updated_at` nullable | 同上，另核对更新时间写入路径 | database drift / model error / migration missing / metadata registration issue / UNKNOWN | 证明 NULL 行与应用行为；未完成前不得强制 NOT NULL |
| `notes.sort_order` nullable | notes/folders 关系、历史 migration、排序 API/查询、NULL 语义 | database drift / model error / migration missing / metadata registration issue / UNKNOWN | 证明排序规则和 NULL 行处理；不能以默认值推断业务正确性 |
| `idx_notes_folder_id` | pg index definition、model `Index`/relationship、migration 创建/删除历史、索引是否被重命名 | database index drift / model omission / stale migration expectation / metadata registration issue / UNKNOWN | 形成 exact DDL 与性能/约束用途对账；未对账前不得删除或重建 |

### Required read-only closure evidence

1. Alembic revision 与每个相关 migration 的 exact SQL/operation inventory。
2. 完整 `Base.metadata` 表/索引/约束注册清单及 `env.py` import coverage。
3. 当前 database exact column/index definition 与 nullable/NULL-row 统计。
4. 三方 diff report：database vs model metadata vs migration history。
5. 每项 drift 的责任分类、风险批准、是否需要后续 migration 的决定。
6. `alembic check` clean 的验证记录；若仍非 clean，Gate 不得解锁。

禁止事项：本设计阶段不创建 migration、不执行 upgrade/downgrade、不调用 `create_all`，不修改模型或应用启动代码。

