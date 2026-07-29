# Audit

## Status

P0-01 completed on 2026-07-15.

## Git Worktree

The worktree contains many existing modified and untracked files from prior work. This Batch 2 implementation must preserve unrelated changes and avoid broad rewrites.

## Alembic State

Command:

```text
cd backend
PYTHONPATH=. .venv/bin/alembic current
PYTHONPATH=. .venv/bin/alembic heads
```

Result:

```text
018 (head)
018 (head)
```

Implication:

- The previously documented 011 taxonomy migration is already part of the applied migration chain.
- The frozen Batch 2 schema update must be implemented as a new forward migration after 018.
- Do not rewrite historical migrations as the primary local database path.

## Current Database Shape

Read-only introspection via project async SQLAlchemy engine:

### `subjects`

- Exists: yes
- Rows: 1
- Columns: `id`, `name`, `description`, `is_active`, `sort_order`, `created_at`, `updated_at`
- Current row:
  - `id=135`
  - `name=LT-20260704 Algorithms`
  - `is_active=true`

### `chapters`

- Exists: yes
- Rows: 0
- Current role: obsolete under updated Batch 2 decision.

### `knowledge_points`

- Exists: yes
- Rows: 3
- Columns: `id`, `subject_id`, `chapter_id`, `name`, `description`, `is_active`, `sort_order`, `created_at`, `updated_at`
- All current `chapter_id` values: `null`
- Current rows:
  - `LT-20260704 Hash Table`
  - `LT-20260704 Stack`
  - `LT-20260704 Tree BFS`

### `knowledge_point_links`

- Exists: yes
- Rows: 6
- Links point to current knowledge points for `question_draft` and `question`.
- This table belongs to already-existing later-batch artifacts. It is not part of the frozen Batch 2 schema, but preserving it avoids breaking existing references.

## Current Code Shape

Current implementation artifacts exist:

- `backend/app/models/taxonomy.py`
  - contains `Chapter`
  - contains `KnowledgePoint.chapter_id`
  - contains `KnowledgePointLink`
- `backend/app/schemas/taxonomy.py`
  - contains Chapter DTOs
  - uses `is_active`
  - uses `chapter_id`
- `backend/app/services/taxonomy_service.py`
  - provides Chapter CRUD
  - validates `chapter_id` against Subject
  - does not validate `parent_id` tree cycles because parent tree does not exist yet
- `backend/app/routers/knowledge_points.py`
  - exposes `/api/knowledge-points` with `chapter_id` filters
- `src/lib/api/taxonomy.ts`
  - exposes Chapter types and CRUD
  - uses `is_active`
  - uses `chapter_id`
- `/manage/subjects` and `/manage/knowledge-points` page entries were frozen to static placeholders in Batch 1, but route-specific implementation components still exist in the worktree.

## Drift Against Updated Frozen Design

| Area | Current | Frozen Design |
| --- | --- | --- |
| owner model | none | none |
| Subject status | `is_active boolean` | `status active/archived` |
| Chapter | separate `chapters` table/domain | no Chapter domain |
| Knowledge Point parent | `chapter_id` optional FK | `parent_id` self FK |
| Archive | boolean active/inactive | status plus subtree archive |
| Tree API | flat list only | nested tree by default |

## P0-01 Conclusion

Implementation can proceed, but must:

1. Add a forward migration after 018.
2. Convert `is_active` to `status`.
3. Convert Knowledge Point hierarchy to `parent_id`.
4. Remove Chapter from active model/API/UI.
5. Preserve existing knowledge point rows and existing `knowledge_point_links`.
6. Block or explicitly handle non-empty `chapters` during migration; current local `chapters` is empty.
