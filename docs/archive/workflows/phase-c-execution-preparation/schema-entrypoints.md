# Schema Entry Points Audit

日期：2026-07-14  
范围：Phase C+1.1；个人知识后端 FastAPI/PostgreSQL 架构线。  
模式：只读 repository、migration history 与 database metadata inspection。

## Entry Point Inventory

| Entry | Location | Type | Risk | Evidence |
|---|---|---|---|---|
| `Base.metadata.create_all` | `backend/main.py:38-40`，`lifespan()` startup | application provisioning | HIGH：每次应用启动都可能尝试创建缺失表/结构；生产是否已实际改变 schema 未由本次证据证明 | `async with engine.begin()` + `await conn.run_sync(Base.metadata.create_all)` |
| Alembic online migration | `backend/alembic/env.py:36-49` | versioned migration execution | HIGH but intended authority：可执行 upgrade/downgrade；当前 revision `018 (head)`，history 单链 | `target_metadata = Base.metadata`；`run_migrations_online()` 使用 async connection |
| Alembic offline migration | `backend/alembic/env.py:27-34` | SQL generation/execution path | MEDIUM：可生成 migration SQL；本轮未执行 offline SQL | `run_migrations_offline()` 调用 `context.run_migrations()` |
| SQLAlchemy model metadata registration | `backend/app/database.py:14-16`、`backend/app/models/__init__.py` | metadata declaration/registration | MEDIUM：决定 `Base.metadata` 的可见对象；当前 env 依赖 package import side effect，覆盖关系不够显式 | `class Base(DeclarativeBase)`；models package imports 37 tables |
| `get_db()` session lifecycle | `backend/app/database.py:19-27` | application data transaction boundary | LOW for schema, HIGH for data writes：本身不改 schema，但 router/service 可通过 session commit 写数据 | context-managed `AsyncSession` with commit/rollback |
| Application health check | `backend/main.py:112-123` | read-only runtime check | LOW：执行 `SELECT 1`，不 provisioning schema | `session.execute(text("SELECT 1"))` |
| Direct SQL / DDL outside listed paths | repository-wide | UNKNOWN | 需要 repository-wide 搜索与 deployment/runtime audit 才能排除；本次未发现新增证据，但不能从当前清单推断不存在 | 本次仅审计指定 backend/database/migration/model 路径；未执行写操作 |

## Current Authority Finding

当前存在两个可能影响 database schema 的入口：应用启动 `create_all` 与 Alembic migration chain。`Base.metadata` 是声明来源，但不是版本化 authority；因此当前状态仍是：

```text
Application create_all
        +
Alembic migration chain
        =
multiple schema authority
```

目标应收敛为 Alembic-only。该目标尚未实施，本报告不修改 `backend/main.py` 或任何 migration。

## Execution Boundary

已执行的 Alembic 命令仅为 `current`、`history --verbose` 与 `check`；数据库查询仅为 SELECT 元数据/统计查询。未执行 upgrade、downgrade、DDL 或 DML。

