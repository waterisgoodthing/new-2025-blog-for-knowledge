# Index Drift Report

日期：2026-07-14  
对象：`idx_notes_folder_id`。  
模式：只读 database/model/migration comparison。

## Evidence

| Layer | Evidence |
|---|---|
| Database | `pg_indexes` shows `idx_notes_folder_id`: non-unique btree on `notes(folder_id)` |
| Model | `Note.__table_args__` contains status, next-review partial, and search GIN indexes; it does not contain `idx_notes_folder_id` |
| Relationship | `Note.folder_id` references `folders.id` with `ON DELETE SET NULL`; `Folder.notes` relationship exists and is view-only |
| Migration upgrade | revision `005` explicitly creates `idx_notes_folder_id` after adding `notes.folder_id` |
| Migration downgrade | revision `005` explicitly drops `idx_notes_folder_id` |

## Required Answers

### 1. Current purpose

The index supports btree lookup/filtering by `notes.folder_id`, aligned with the folder relationship and likely folder-scoped note queries. Query-plan usage was not executed in this audit; performance importance is therefore `UNKNOWN`.

### 2. Why the database has it

The database has it because revision `005` contains an explicit `op.create_index("idx_notes_folder_id", "notes", ["folder_id"])` operation, and current `pg_indexes` confirms its presence. This proves migration history intent, not necessarily the last physical provisioning event.

### 3. Why metadata does not show it

Current `Note.__table_args__` omits the index. The evidence supports a model metadata omission or intentional model-history divergence; it does not support `metadata registration issue` because `Note` itself is visible in `Base.metadata` and Alembic target metadata. Final classification remains `unknown` pending an approved index policy.

### 4. Is it drift?

Yes, it is an observed three-way difference: database present, model metadata absent, migration upgrade present. Ownership classification is `unknown`, with candidate `model drift`/intentional metadata omission. No index deletion, creation, or migration modification is authorized.

## Closure Requirement

Review the approved query/index contract and historical model intent, then record whether the index should remain represented in metadata. Until approved, preserve the current index and keep Gate BLOCKED.

