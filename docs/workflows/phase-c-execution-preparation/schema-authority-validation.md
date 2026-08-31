# Schema Authority Validation

日期：2026-07-14  
状态：审计验证完成；Migration Gate 仍为 `BLOCKED`。

## Executed

### Repository inspection

- `git status --short`
- 读取 `AGENTS.md`
- 检查 `backend/main.py`
- 检查 `backend/app/database.py`
- 检查 `backend/app/models/*.py` 与 `backend/app/models/__init__.py`
- 检查 `backend/alembic/env.py`
- 静态检查 `backend/alembic/versions/*.py` 的 revision、`create_table`、index/constraint operations

### Migration history inspection

在 `backend/` 工作目录执行：

```text
PYTHONPATH=. .venv/bin/alembic current
PYTHONPATH=. .venv/bin/alembic history --verbose
PYTHONPATH=. .venv/bin/alembic check
```

结果：`018 (head)`；history 为单链；`alembic check` EXPECTED FAIL/BLOCKING，复现 4 个 nullable drift 与 `idx_notes_folder_id` removed-index drift。

### Metadata inspection

只读 Python inspection 观察到：

- `Base.metadata` 37 tables；
- 仅导入 `app.models.note` 的干净进程也得到 37 tables，证明当前覆盖依赖 package `__init__` side effect；
- migration static inventory 35 `create_table` tables；
- model-only tables：`guest_messages`、`guest_message_bans`；
- database public tables 38，包含 37 model tables + `alembic_version`。

### Database metadata queries

只执行 SELECT：

- `information_schema.columns`
- `pg_indexes`
- `pg_constraint`
- `pg_tables`

已核对 focused `folders`/`notes` columns、defaults、nullable、indexes、PK/FK，并记录全库 constraint/index/column counts。

## Not Executed

```text
No migration executed.
No schema modified.
No database write executed.
No CREATE/ALTER/DROP executed.
No INSERT/UPDATE/DELETE executed.
No alembic upgrade executed.
No alembic downgrade executed.
No model/backend/config/auth/deployment file modified.
No pg_dump or pg_restore executed.
```

## Validation Result

| Check | Result | Evidence |
|---|---|---|
| schema entrypoint audit | PASS as audit / not closed | `schema-entrypoints.md` |
| metadata coverage audit | BLOCKED | 37 runtime tables vs 35 migration create records; guest message provenance unresolved |
| three-way drift audit | BLOCKED | 5 known drift items remain `unknown` |
| authority decision | DESIGNED only | Alembic-only target proposed, not implemented |
| write boundary | PASS | no DDL/DML/migration execution |
| Migration Gate | BLOCKED | P0 schema authority evidence not closed |

