# Schema Drift Decision Package

Date: 2026-07-14  
Scope: `folders.sort_order`, `folders.created_at`, `folders.updated_at`, `notes.sort_order`, `idx_notes_folder_id`

## Column decision matrix

| Field | Current DB | Current Model | Migration History | Decision |
|---|---|---|---|---|
| `folders.sort_order` | `integer`, nullable `YES`, default `0`; NULL `0/2` | `Integer`, typed non-null, Python default `0`; model has no server default | Revision `005` creates it with server default `0` and omits `nullable` | `retain_unknown` |
| `folders.created_at` | `timestamp without time zone`, nullable `YES`, default `now()`; NULL `0/2` | `DateTime`, typed non-null, server default `now()` | Revision `005` creates it with server default `now()` and omits `nullable` | `retain_unknown` |
| `folders.updated_at` | `timestamp without time zone`, nullable `YES`, default `now()`; NULL `0/2` | `DateTime`, typed non-null, server default `now()` and `onupdate` | Revision `005` creates it with server default `now()` and omits `nullable` | `retain_unknown` |
| `notes.sort_order` | `integer`, nullable `YES`, default `0`; NULL `0/13` | `Integer`, typed non-null, Python default `0`; model has no server default | Revision `005` adds it with server default `0` and omits `nullable` | `retain_unknown` |
| `idx_notes_folder_id` | Present non-unique btree on `notes(folder_id)` | `Note.folder_id` exists, but `Note.__table_args__` does not declare this index | Revision `005` explicitly creates it and downgrade explicitly drops it | `keep_existing_index` |

## Nullable analysis

1. **Current NULL data:** all four current NULL counts are zero. This is a data snapshot, not proof that NULL is forbidden historically or in every write path.
2. **Migration intent:** revision `005` supplies defaults but omits `nullable`, while the model metadata currently yields non-null comparison expectations. `alembic check` reports four `modify_nullable` operations.
3. **Business dependency:** folder ordering is actively read and written by `backend/app/routers/folders.py`; notes ordering is accepted, filtered, and ordered by `backend/app/routers/notes.py`. Folder timestamps are returned and used in the model, while their nullable contract is not separately documented.
4. **Risk:** changing to non-null could fail on future or historical NULL rows and would be a schema write; changing the model/database toward nullable could weaken typed/runtime assumptions. Zero current NULL rows lowers immediate cleanup risk only. No `ALTER COLUMN SET NOT NULL` is recommended or authorized by this package.

## Index analysis

- **Creation intent:** revision `005` creates `idx_notes_folder_id` immediately after adding the nullable `folder_id` foreign key; downgrade drops it.
- **Current query relationship:** folder-scoped note selection filters on `Note.folder_id`; `Folder.notes` is a view-only relationship. The index aligns with that access path. Query-plan usage was not executed.
- **Model expression:** the model should likely express the index for metadata parity, but that is a future model/migration decision and is not implemented here.
- **Deletion risk:** removing it could regress folder-scoped reads and would contradict the explicit migration intent. Preserve it until approved policy exists.

The index action is therefore `keep_existing_index`; any later model declaration requires separate approval. It is not an instruction to modify the index.

## Required future decision

The four columns remain `retain_unknown` until an owner approves NULL versus non-NULL semantics, validates historical/write-path assumptions, and authorizes a future migration design. The index remains preserved pending an approved metadata parity decision. Migration Gate remains `BLOCKED`.
