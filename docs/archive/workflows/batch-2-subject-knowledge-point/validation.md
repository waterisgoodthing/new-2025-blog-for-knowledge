# Validation

## Status

Completed on 2026-07-15.

## Migration

Commands:

```text
cd backend
PYTHONPATH=. .venv/bin/alembic current
PYTHONPATH=. .venv/bin/alembic upgrade head
```

Result:

```text
019 (head)
```

Migration `019_align_subject_knowledge_tree.py` was applied successfully.

Post-migration schema inspection:

- `subjects` exists with columns:
  - `id`
  - `name`
  - `description`
  - `sort_order`
  - `created_at`
  - `updated_at`
  - `status`
- `chapters` does not exist.
- `knowledge_points` exists with columns:
  - `id`
  - `subject_id`
  - `name`
  - `description`
  - `sort_order`
  - `created_at`
  - `updated_at`
  - `parent_id`
  - `status`
- `knowledge_point_links` still exists and was preserved.

Data counts after migration:

```text
subjects: 1
knowledge_points: 3
knowledge_point_links: 6
```

## Backend

Command:

```text
cd backend
.venv/bin/python -m pytest tests/test_taxonomy_service.py -q
```

Result:

```text
7 passed
```

Covered behaviors:

- Subject name normalization and blank rejection.
- Status enum validation.
- Subject duplicate update conflict.
- Knowledge Point parent must belong to same Subject.
- Knowledge Point cannot move under a descendant.
- Archiving a Knowledge Point archives the subtree.
- Subject knowledge tree returns nested nodes.

Import check:

```text
cd backend
.venv/bin/python -m compileall -q app main.py
```

Result:

```text
PASS
```

Registered route check:

```text
/api/admin/subjects
/api/admin/subjects/{subject_id}
/api/admin/subjects/{subject_id}/knowledge-tree
/api/admin/knowledge-points
/api/admin/knowledge-points/{knowledge_point_id}
/api/admin/knowledge-points/{knowledge_point_id}/archive
```

No `/api/chapters` route is registered.

## Frontend

TypeScript:

```text
npx tsc --noEmit --pretty false
```

Result:

```text
PASS
```

Vitest:

```text
npm test
```

Result:

```text
5 files passed
16 tests passed
```

Production build:

```text
npm run build
```

Result:

```text
PASS
```

Build route table includes:

- `/manage/subjects`
- `/manage/subjects/[id]`
- `/manage/knowledge-points`
- `/manage/knowledge-points/[id]`

## Static Checks

```text
git diff --check
```

Result:

```text
PASS
```

## Boundary Check

Preserved:

- No `owner_id` added.
- No active `chapters` model/API/table after migration.
- Question/Mistake/Review/Attachment/OCR/AI/Search/Analytics behavior not modified as part of the domain implementation.
- Public routes remain outside this implementation scope.

Known current-state note:

- The wider worktree contains unrelated dirty and untracked files from previous work. They were not reverted.
- `src/lib/api/taxonomy.ts` keeps compatibility filter input `is_active` and maps it to `status`; this is a frontend compatibility shim only, not a database field.
