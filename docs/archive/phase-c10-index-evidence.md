# Phase C+10 Index Evidence

Date: 2026-07-15
Object: `idx_notes_folder_id`
Status: blocked; no index change approved.

| Item | Evidence | Status |
|---|---|---|
| Owner | No named schema/notes owner | `BLOCKED` |
| Query usage | Folder-scoped paths filter by `Note.folder_id` | `PENDING` workload validation |
| Workload evidence | No production frequency or workload record | `BLOCKED` |
| Query-plan evidence | No query-plan inspection recorded | `BLOCKED` |
| Migration impact | Revision `005` creates the index; `alembic check` reports model omission; deletion risk not approved | `BLOCKED` |
| Candidate A | Preserve physical index and later declare in ORM metadata | Provisional only |
| Candidate B | Preserve physical index under governance exception | Not approved |
| Candidate C | Remove index | Forbidden |

## Decision boundary

Preserve the existing physical index. No deletion, recreation, or model declaration is authorized until owner, workload, query-plan, migration, rollback, and verification evidence is complete.
