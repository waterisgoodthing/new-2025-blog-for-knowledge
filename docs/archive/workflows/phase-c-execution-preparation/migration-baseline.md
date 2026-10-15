# Database Migration Baseline

日期：2026-07-13  
数据库检查方式：`PYTHONPATH=. .venv/bin/alembic current/history/check`，均为只读检查。

## 当前状态

| 项目 | 结果 | 判定 |
|---|---|---|
| 当前 revision | `018` | 已验证 |
| head | `018 (head)` | 已验证 |
| 当前是否落后 head | 否 | 已验证 |
| migration history | 单链 `001 -> 002 -> 003 -> 1119bee5a419 -> 0ec85724afb9 -> 004 -> ... -> 018` | 已验证 |
| pending migration | Alembic 版本表未显示 pending；但 `alembic check` 检出 model/database drift | 不可视为通过 |

## Migration history

| Revision | Parent | 主题 |
|---|---|---|
| 001 | base | initial schema |
| 002 | 001 | notes status |
| 003 | 1119bee5a419 | restore notes status index |
| 1119bee5a419 | 0ec85724afb9 | notes images |
| 0ec85724afb9 | 002 | users admin field |
| 004 | 003 | notes ai_metadata |
| 005 | 004 | folders |
| 006 | 005 | admin sessions/passkeys/passwords |
| 007 | 006 | folder cascade change |
| 008 | 007 | audit logs |
| 009 | 008 | music daily tables |
| 010 | 009 | managed content entries |
| 011 | 010 | subject taxonomy |
| 012 | 011 | question drafts and questions |
| 013 | 012 | mistakes and review |
| 014 | 013 | attachments |
| 015 | 014 | capture items |
| 016 | 015 | AI call logs |
| 017 | 016 | prompt version |
| 018 | 017 | AI runs |

## Drift evidence

`PYTHONPATH=. .venv/bin/alembic check` failed with new upgrade operations:

- `folders.sort_order` database nullable vs model non-nullable
- `folders.created_at` database nullable vs model non-nullable
- `folders.updated_at` database nullable vs model non-nullable
- `notes.sort_order` database nullable vs model non-nullable
- database contains `idx_notes_folder_id`, while autogenerate reports it as removed from metadata

这是 schema authority 风险，不是本轮修复项。由于 drift check 未通过，Migration Gate 不能前进。

## 风险说明

1. `018 (head)` 只证明版本链位置，不能证明实际 schema 与 model 一致。
2. 当前 schema 同时受到 Alembic 与应用启动 `Base.metadata.create_all()` 的潜在影响。
3. 在 drift、备份恢复和 owner/权限证据闭合前，不得执行 upgrade、downgrade 或新 migration。

结论：`Migration Gate = BLOCKED`。
