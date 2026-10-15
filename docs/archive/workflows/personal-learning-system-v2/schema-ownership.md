# Phase B：Schema Ownership

状态：设计完成，未修改 `backend/main.py`、Alembic 或数据库。  
问题：当前 `backend/alembic/env.py` 将 `Base.metadata` 作为 Alembic target metadata，同时 `backend/main.py` lifespan 在启动时执行 `Base.metadata.create_all`，形成两个可能影响 schema 的入口。

## 唯一 authority 决策

Alembic migration 是唯一 schema authority。

```text
model metadata  -> 描述和校验目标结构
Alembic         -> 唯一创建、修改、删除生产 schema 的机制
application     -> 只连接已迁移 schema，不 create_all
```

`Base.metadata` 继续作为模型声明、迁移 autogenerate 对照和测试元数据来源，但不再被解释为运行时 schema provisioning authority。应用启动不得通过 `create_all` 自动补表、补列或掩盖 migration 漂移。

## 运行规则

1. 部署前在临时环境执行 `alembic upgrade head`，再启动应用；生产启动只检查当前 revision 与预期 head，不自动升级或建表。
2. migration 必须具备可审查的 upgrade/downgrade，危险 downgrade 只能在临时恢复库演练，不能用生产库验证。
3. model 变更必须同时有 schema、migration、API contract 和测试证据；没有 migration 的 model 变更视为 schema drift。
4. `create_all` 若为本地测试所需，应隔离到明确的 test fixture/database，并在文档中标注不适用于生产；不得保留为应用 lifespan 的隐式补救。
5. Alembic 版本、数据库实际列/约束/索引和 `Base.metadata` 做三方 drift check；不一致时状态为 `BLOCKED`。

## 018 恢复约束

Migration 018 创建 `ai_runs`，包含状态校验、review 状态、parent run 自引用、索引和 `downgrade -> drop_table('ai_runs')`。任何 018 恢复验证必须：

- 在 pg_dump 副本或临时恢复库执行，不在当前生产/开发共享库直接 downgrade。
- 先保存 018 之前与之后的 schema revision、ai_runs 行数、关键字段/索引/约束清单。
- 演练 `018 upgrade`、业务读写 smoke check、备份恢复、必要时在临时副本演练 downgrade，再回到 018 head。
- 证明 `ai_runs` 与 `ai_call_logs` 的审计粒度都可恢复，且敏感字段过滤规则未因恢复丢失。

## Schema change gate

任何后续 schema 执行必须同时具备：迁移设计批准、备份新鲜度与 checksum、临时恢复成功、owner/权限测试、upgrade/downgrade 记录、应用启动不依赖 `create_all`、以及明确回滚窗口。仅有 Alembic `018 (head)` 不能证明 schema 已安全可迁移。
