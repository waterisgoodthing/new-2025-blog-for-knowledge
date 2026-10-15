# Migration Provenance Inventory

日期：2026-07-14  
范围：`backend/alembic/versions/*` 静态分析；不执行 migration。

## Inventory Method

静态读取每个 revision 文件的 `revision`/`down_revision` 与 `upgrade`/`downgrade` 中的 Alembic operations，覆盖：`create_table`、`drop_table`、`add_column`、`drop_column`、`alter_column`、`create_index`、`drop_index`、foreign-key/constraint/check/unique operations。

## Revision Chain and Operations

| Revision | Parent | Upgrade schema operations (summary) | Downgrade operations (summary) |
|---|---|---|---|
| `001` | base | create users/tags/subjects/categories/notes/note_tags/music_items/recommendations; create notes indexes | drop the same tables/indexes |
| `002` | `001` | add `notes.status`; create `idx_notes_status` | drop index/column |
| `003` | `1119bee5a419` | create `idx_notes_status` | drop index |
| `1119bee5a419` | `0ec85724afb9` | add `notes.images` | drop column |
| `0ec85724afb9` | `002` | add `users.is_admin` | drop column |
| `004` | `003` | add `notes.ai_metadata` | drop column |
| `005` | `004` | create `folders`; add `notes.folder_id`, `notes.sort_order`; create folder/notes-folder indexes | drop notes folder columns/indexes and folders |
| `006` | `005` | alter passkey column; create admin sessions/passkeys/passwords | drop those tables/indexes |
| `007` | `006` | change folder parent FK to `ON DELETE SET NULL` | drop/recreate prior constraint semantics |
| `008` | `007` | create `audit_logs` and 3 indexes | drop indexes/table |
| `009` | `008` | create music daily/config tables and indexes | drop indexes/tables |
| `010` | `009` | create `managed_content_entries` | drop table |
| `011` | `010` | alter subjects; create chapters/knowledge points/links and indexes | drop created objects/subject columns |
| `012` | `011` | create draft/question/question-source tables, indexes, checks/FKs | drop created tables |
| `013` | `012` | create mistake/review tables, indexes, checks | drop created tables/constraints |
| `014` | `013` | create attachments/attachment_links, indexes, checks/FKs | drop created tables |
| `015` | `014` | create `capture_items`, indexes, checks/FKs | drop indexes/table |
| `016` | `015` | create `ai_call_logs`, indexes | drop indexes/table |
| `017` | `016` | add `ai_call_logs.prompt_version` | drop column |
| `018` | `017` | create `ai_runs`, indexes, checks/FK | drop table |

The chain is `001 -> 002 -> 0ec85724afb9 -> 1119bee5a419 -> 003 -> ... -> 018`; current database revision is `018 (head)`.

## Object Provenance Matrix

| Database Object | Model Exists | Migration Create | Migration Revision | Provenance Status |
|---|---:|---:|---|---|
| `guest_messages` | yes | no record found | — | UNKNOWN; repository evidence points to dev `create_all` path, current DB origin unproven |
| `guest_message_bans` | yes | no record found | — | UNKNOWN; repository evidence points to dev `create_all` path, current DB origin unproven |
| All other 35 model tables | yes | yes | `001`–`018` as applicable | migration provenance present, subject to drift/coverage validation |
| `alembic_version` | no application model | Alembic-managed | current `018` | expected migration bookkeeping table |

## Finding

`guest_messages` and `guest_message_bans` are not present in the versioned Alembic create-table inventory. This report does not classify them as definitively create_all-created, manually-created, or externally-provisioned because current database provenance logs are unavailable. Their provenance remains `UNKNOWN` and blocks migration readiness.

