# Phase C Execution Preparation：任务清单

状态：已批准执行；仅限只读审计与文档生成。

- [x] C-01 Database Baseline Freeze：只读确认 Alembic 状态、schema inventory 与 data baseline，生成对应三份报告。
- [x] C-02 Owner Mapping Preparation：按指定实体生成 owner mapping readiness，区分 explicit owner 与 inferred owner。
- [x] C-03 Schema Authority Audit：只读审计 `backend/main.py`、Alembic env/target metadata 与 migration chain。
- [x] C-04 Authentication Boundary Test Preparation：生成四类身份 × 六类对象的权限测试矩阵并记录缺失测试。
- [x] C-05 Migration Gate Checklist：汇总 Phase B 已完成证据、未完成证据与阻断项，保持 Gate 为 `BLOCKED`。
- [x] C-06 Validation：仅验证本轮生成文档的完整性、只读声明和未触碰业务代码/数据库的证据，并写入 `validation.md`。

## 执行规则

每完成一个任务项，必须立即在本文件将对应 checkbox 标记为 `[x]`，并再开始下一项。若证据不可用，标记为 blocked/deferred 并记录原因；不得用推断替代缺失证据。

## 审批门

请用户明确批准本任务清单或指定阶段后，才可开始 C-01。当前 Migration Gate 仍为 `BLOCKED`。

## Phase C+1 Schema Authority Closure Audit

- [x] C+1.1 Schema Authority Entry Audit：审计 application、database、models 与 Alembic schema entrypoints。
- [x] C+1.2 Alembic Metadata Coverage Audit：核对 model registry、Base.metadata、target_metadata 与 migration history 覆盖。
- [x] C+1.3 Three-Way Drift Audit：只读对比 database schema、SQLAlchemy metadata 与 migration history，保留 UNKNOWN 分类。
- [x] C+1.4 Schema Authority Decision：形成 Alembic-only 目标和后续设计变更边界，不执行实施。
- [x] C+1.5 Schema Authority Validation：记录执行/未执行命令、证据与 Gate 状态。

Phase C+1 发现：runtime metadata 37 张模型表，migration history 静态 create-table inventory 35 张；`guest_messages` 与 `guest_message_bans` provenance 未闭合；既有 5 项 drift 仍存在。因此不允许进入 Phase D，Migration Gate 保持 `BLOCKED`。

## Phase C+2 Schema Provenance & Drift Closure Audit

- [x] C+2.1 Migration Provenance Inventory：静态盘点 revisions、parent、表/列/索引/约束操作。
- [x] C+2.2 Guest Tables Origin Investigation：搜索模型、router、docs、scripts/deployment 与 migration provenance。
- [x] C+2.3 Complete Migration Coverage Matrix：覆盖 model、Base.metadata、migration history 与 database tables。
- [x] C+2.4 Drift Ownership Analysis：记录四个 column drift 的 database/model/migration/NULL 证据并保留 unknown。
- [x] C+2.5 Index Drift Analysis：核对 `idx_notes_folder_id` 的 database/model/migration 三方证据。
- [x] C+2.6 Validation Report：记录只读命令、未执行边界与 Gate 状态。

Phase C+2 结论：guest tables 的当前物理 provenance 仍为 `UNKNOWN`；四个 column drift 与一个 index drift 的 ownership classification 仍为 `unknown`；Migration Gate 保持 `BLOCKED`。
