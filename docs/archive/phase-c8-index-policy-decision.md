# Phase C+8 Index Policy Decision

Date: 2026-07-14
Object: `idx_notes_folder_id`

## Evidence

- Current database: non-unique btree index on `notes(folder_id)`.
- ORM metadata: `Note.folder_id` exists, but `Note.__table_args__` omits this index.
- Alembic history: revision `005` explicitly creates the index and its downgrade drops it.
- Query need: folder-scoped note paths filter by `Note.folder_id`; query-plan and workload evidence are not available.
- Migration risk: `alembic check` reports the index as removed from model metadata; deletion could regress lookup and contradict migration intent.

## Candidate evaluation

### Candidate A: ORM metadata declaration

Preserve the physical index and later add a model metadata declaration. This provides declarative parity, but requires a named notes/schema owner, workload evidence, model review, and Alembic comparison review.

### Candidate B: physical index governance exception

Preserve the physical index without ORM declaration. This avoids a model change but requires a documented exception, ownership, and a future drift-check rule protecting the index.

### Candidate C: removal

Not allowed. Removal requires workload evidence, owner approval, migration impact, rollback, and verification. No deletion or recreation is authorized.

## Decision status

Provisional recommendation: **Candidate A in principle**, immediate action: preserve the existing physical index.

| Required item | Status |
|---|---|
| Index/schema owner | Unassigned |
| Workload/query-plan evidence | Missing |
| Model change approval | Not approved |
| Migration impact review | Not complete |
| Rollback plan | Not approved |

Because the owner and workload evidence are missing, no candidate is finally approved for implementation. Migration Gate remains `BLOCKED`.
