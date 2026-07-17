# Migration Strategy

## Status

P0-02 completed as a plan on 2026-07-15. Implementation follows this strategy after `tasks.md` approval.

## Target

Align existing applied taxonomy schema with the updated frozen Batch 2 model:

```text
subjects
  id
  name
  description
  status
  sort_order
  created_at
  updated_at

knowledge_points
  id
  subject_id
  parent_id
  name
  description
  status
  sort_order
  created_at
  updated_at
```

No `owner_id`.

No active `chapters` domain.

## Forward Migration

Create a new migration after current head `018`:

```text
019_align_subject_knowledge_tree.py
```

## Data Preservation

Current local data:

- 1 Subject row
- 3 Knowledge Point rows
- 6 Knowledge Point Link rows
- 0 Chapter rows

Required preservation:

- Existing Subject remains.
- Existing Knowledge Points remain.
- Existing Knowledge Point Links remain.

## Migration Steps

1. Inspect `chapters`.
2. If `chapters` contains rows, stop with a clear error unless an explicit chapter-to-knowledge-point conversion plan is approved.
3. Add `subjects.status` with default `active`.
4. Backfill `subjects.status` from `subjects.is_active`.
5. Drop `subjects.is_active`.
6. Add `knowledge_points.parent_id` nullable.
7. Add self FK from `knowledge_points.parent_id` to `knowledge_points.id`.
8. Add `knowledge_points.status` with default `active`.
9. Backfill `knowledge_points.status` from `knowledge_points.is_active`.
10. Drop FK/index for `knowledge_points.chapter_id`.
11. Drop `knowledge_points.chapter_id`.
12. Drop `knowledge_points.is_active`.
13. Drop `chapters` indexes/table after confirming it is empty.
14. Add tree indexes:
    - `idx_knowledge_points_subject_parent_sort`
    - `idx_knowledge_points_parent`
15. Preserve `knowledge_point_links`.

## Runtime Rules After Migration

Service must enforce:

- parent belongs to same subject
- node cannot parent itself
- node cannot move under descendant
- archive recursively updates subtree
- nested tree API is default for subject tree

## Downgrade

Downgrade may reconstruct legacy columns:

- recreate empty `chapters`
- add `is_active` from `status`
- add nullable `chapter_id`
- drop `parent_id`
- drop `status`

Downgrade cannot reconstruct historical chapter membership if no chapter rows were present. This is acceptable for local rollback of the applied frozen model, but production migration would need backup confirmation before execution.

## Risks

- If another environment contains non-empty `chapters`, migration will block to prevent data loss.
- Existing later-batch tables may depend on `knowledge_point_links`; preserve this table.
- Existing UI components still using Chapter must be updated or left unreachable.
