# Schema Authority Audit

日期：2026-07-13  
范围：`backend/main.py`、`backend/alembic/env.py`、`backend/app/database.py`、模型注册与 migration chain。仅审计，不修改。

## 1. 是否存在多个 schema 修改入口？

是。

### 入口 A：应用启动 `Base.metadata.create_all`

`backend/main.py:41-42` 的 lifespan 在应用启动时执行：

```python
async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
```

这会尝试创建缺失表/结构。它不是版本化 migration，却能影响数据库 schema，因此应用启动与 Alembic 共同成为潜在 schema provisioning 入口。

### 入口 B：Alembic migration chain

`backend/alembic/env.py` 设置 `config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)`，并以 `target_metadata = Base.metadata` 配置 offline/online migration。`run_migrations_online()` 通过 Alembic context 执行版本化变更。

当前链已到 `018 (head)`，包含 001–018 及两个历史 hash revision。

## 2. target metadata 覆盖风险

`backend/app/models/__init__.py` 注册了完整模型集合，包括 `ManagedContentEntry`、`AiCallLog`、`AiRun`、`CaptureItem`、session/audit 等；但 `backend/alembic/env.py` 只显式导入了 note、music、recommendation、taxonomy、question、mistake、review、attachment 模块。

因此存在以下风险：

- Alembic target metadata 的注册覆盖不明显，不能仅凭 `Base.metadata` 名称认为所有模型都纳入 autogenerate。
- `managed_content_entries`、`ai_call_logs`、`ai_runs`、`capture_items`、session/audit 等模型没有在 env.py 中显式导入，必须做一次受控的三方 metadata/schema/migration coverage 核对。
- `alembic check` 已报告 nullable/index drift，证明当前 schema 与 target metadata/模型约束不一致；它不是 clean baseline。

## 3. 已验证 drift

只读执行 `PYTHONPATH=. .venv/bin/alembic check` 失败并报告：

- `folders.sort_order` nullable 差异
- `folders.created_at` nullable 差异
- `folders.updated_at` nullable 差异
- `notes.sort_order` nullable 差异
- `idx_notes_folder_id` 被 autogenerate 视为 removed index

在 drift 未解释前，不能创建新 migration，也不能用 `create_all` 掩盖差异。

## 4. migration chain 风险

历史 downgrade 包含 `drop_table`、`drop_column`、关联清理 SQL、`CASCADE`、`RESTRICT` 与 `SET NULL`。尤其 018 downgrade 会删除 `ai_runs`。这不代表 migration 代码本身应在本轮改动，但证明生产 downgrade 必须被禁止，且只能在隔离恢复库演练。

## 5. 后续修复建议

1. 将 Alembic migration 明确设为唯一 schema authority；应用 lifespan 不再承担生产 schema provisioning。
2. 在隔离环境补做完整模型注册/target metadata 覆盖清单，明确所有模型是否纳入 Alembic 对照；不要直接通过新增 import 或 migration 消除未知 drift。
3. 对数据库实际 schema、Alembic revision、完整 `Base.metadata` 做三方 drift report，逐项决定“已有 migration 事实 / 模型错误 / 数据库漂移 / 需要新 migration”。
4. 将 `alembic check` 修复为 clean 后，才允许设计下一份 migration；不得把 `alembic check` 失败当作 pending migration 自动执行。
5. 应用启动只做 revision/health 检查，不自动 `create_all`、upgrade 或 downgrade；本地测试若需建表，应隔离到明确 test fixture。
6. 任何 downgrade 只在新鲜 dump 恢复的临时数据库中执行，记录 schema、数据、附件与业务 smoke evidence。

结论：当前存在多个 schema 影响入口，schema authority 不唯一；Migration Gate 维持 `BLOCKED`。
