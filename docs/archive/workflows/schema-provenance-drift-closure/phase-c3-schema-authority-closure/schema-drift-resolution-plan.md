# Schema Drift Resolution Plan

Date: 2026-07-14  
Mode: read-only design; no nullable, index, model, or migration change authorized.

## Resolution matrix

| Object | Database state | Model state | Migration state | Candidate owner | Final recommendation | Required evidence |
|---|---|---|---|---|---|---|
| `folders.sort_order` | `integer`, nullable `YES`, default `0`; current NULL count `0/2` | `Integer`, inferred non-null, Python default `0`; no model server default | Revision `005` creates the column with server default `0` and omits `nullable` | `unknown`; possible model intent mismatch or historical migration/database semantics | Preserve current database state; classify semantic ownership as `unknown`; require a future approved migration only after NULL policy is decided | Approved ordering contract; historical NULL/write-path review; exact DDL/default comparison; owner approval of nullable semantics |
| `folders.created_at` | `timestamp without time zone`, nullable `YES`, default `now()`; current NULL count `0/2` | `DateTime`, inferred non-null, server default `now()` | Revision `005` creates DateTime with `now()` and omits `nullable` | `unknown`; timestamp nullability and lifecycle semantics are not separately approved | Preserve current state and retain unknown ownership; do not set NOT NULL based on the zero-count snapshot | Creation timestamp contract; historical/import path review; NULL policy; timezone and API compatibility review |
| `folders.updated_at` | `timestamp without time zone`, nullable `YES`, default `now()`; current NULL count `0/2` | `DateTime`, inferred non-null, server default `now()`, `onupdate` behavior | Revision `005` creates DateTime with `now()` and omits `nullable` | `unknown`; update semantics may belong to model/runtime but nullable intent is unresolved | Preserve current state; resolve update/nullability semantics in a separately approved future design | Update behavior evidence; historical rows/imports; write-path review; API serialization contract; owner approval |
| `notes.sort_order` | `integer`, nullable `YES`, default `0`; current NULL count `0/13` | `Integer`, inferred non-null, Python default `0`; no model server default | Revision `005` adds the column with server default `0` and omits `nullable` | `unknown`; active ordering behavior exists but nullable authority is unresolved | Preserve current state; retain unknown ownership; no direct NOT NULL recommendation | Note ordering contract; folder/unfoldered write-path review; historical NULL check; owner approval of default/nullable semantics |
| `idx_notes_folder_id` | Present non-unique btree index on `notes(folder_id)` | `Note.folder_id` and `Folder.notes` relationship exist; `Note.__table_args__` omits this index | Revision `005` explicitly creates it; downgrade explicitly drops it | Migration/history intent is known; model metadata ownership is unresolved | `keep_existing_index`; later decide whether to add model declaration for metadata parity; do not remove or recreate now | Approved query/index contract; query-plan or workload evidence; model metadata policy; migration autogenerate review after approval |

## Nullable resolution rule

All four current NULL counts are zero. That lowers immediate data-cleanup evidence but does not make a nullable database column equivalent to a non-null model declaration. A future constraint change must not be inferred from current counts alone and must not be designed as an automatic `ALTER COLUMN SET NOT NULL` action.

The historical migration's omitted `nullable` argument is evidence of how revision `005` was authored, not proof that the database or model is the approved owner. The candidate owner remains `unknown` until business semantics and historical/write-path evidence are approved.

## Index resolution rule

Revision `005` provides positive creation intent for `idx_notes_folder_id`, and the relationship/query path gives it a plausible operational purpose. Query-plan usage was not part of this design pass. The safe design posture is therefore to preserve the existing index. Any model declaration or migration cleanup must be a later, explicitly approved action.

## Execution order for a future approved phase

1. Confirm owner and target semantics for each item.
2. Gather required evidence and record data/risk impact.
3. Approve the target model/database contract.
4. Design, review, and approve any required migration.
5. Run migration only under the separate migration governance process.
6. Re-run metadata comparison and `alembic check` as verification.

No step above authorizes execution in Phase C+3. Until the sequence is approved, these objects remain unresolved blockers.
