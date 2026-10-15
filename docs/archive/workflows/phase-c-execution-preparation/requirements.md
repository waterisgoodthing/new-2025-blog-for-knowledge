# Phase C Execution Preparation：需求

## 必须交付

- `migration-baseline.md`：当前 revision、head 状态、pending migration、历史链与风险。
- `schema-inventory.md`：13 个核心实体的表、字段、类型、nullable、index、foreign key、constraint。
- `data-baseline.md`：每个核心表的只读 row count、primary key 范围、created_at 与 updated_at 范围。
- `owner-mapping-readiness.md`：9 个指定实体的 owner 字段、身份证据、置信度、行动与风险，明确 explicit/inferred owner。
- `schema-authority-audit.md`：`create_all`、Alembic env/target_metadata、migration chain 与 drift 风险。
- `auth-test-matrix.md`：四类身份与六类对象的 allow/deny、当前实现状态和缺失测试。
- `phase-c-gate-checklist.md`：Phase B 已完成项、迁移前未完成项及 `Migration Gate = BLOCKED`。

## 质量要求

- 每项结论标注来源或验证状态：已验证、代码事实、文档事实、未验证或不可用。
- 不执行任何 schema/data/auth/deployment 写操作。
- 不执行备份或恢复命令；`pg_dump`、`pg_restore` 只作为 Gate 未完成项记录。
- 任何无法连接数据库或无法读取的证据必须明确写入报告，不得补猜。

## 非目标

不创建 migration，不修复 schema authority，不补 owner 字段，不修改权限实现，不运行升级/降级，不删除旧表，不执行 Phase D。
