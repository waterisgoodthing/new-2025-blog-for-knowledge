# Phase C+11 Index Resolution

Date: 2026-07-15
Object: `idx_notes_folder_id`

| Evidence area | Current state | Status |
|---|---|---|
| Physical index | Existing non-unique btree index on `notes(folder_id)` | Present |
| Migration intent | Revision `005` creates the index | Known |
| ORM metadata | Index is not currently expressed in SQLAlchemy metadata | Drift remains |
| Query usage | Folder-scoped access by `Note.folder_id` is evidenced | `PENDING` workload validation |
| Query plan | No approved production query-plan evidence | `BLOCKED` |
| Owner | No named schema/business owner | `BLOCKED` |
| Migration impact | Deletion/recreation/model declaration impact is not approved | `BLOCKED` |

## Candidates

- Candidate A: declare the index in ORM metadata after owner and workload approval.
- Candidate B: retain the physical index under a documented governance exception.
- Candidate C: remove it. This is not permitted without explicit approval and evidence.

## Result

```text
Index Resolution = BLOCKED
```

The existing physical index must be preserved for now. No model change, deletion, or recreation is authorized.
