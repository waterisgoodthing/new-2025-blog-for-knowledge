# Validation Plan

## Status

P0-01 through P0-08 implementation and validation completed. Executed evidence is recorded in [validation.md](./validation.md).

## Required Validation After Implementation

### Database

Run from `backend/`:

```text
PYTHONPATH=. .venv/bin/alembic current
PYTHONPATH=. .venv/bin/alembic upgrade head
PYTHONPATH=. .venv/bin/alembic check
```

Validate:

- active revision is expected.
- frozen Question columns exist.
- no unintended drop of Batch 2 `subjects` or `knowledge_points`.
- Question-KnowledgePoint relation enforces uniqueness.
- no migration touches unrelated public content tables.

### Backend

Run targeted tests first:

```text
cd backend
.venv/bin/python -m pytest tests/test_question_service.py -q
```

Expected behavior coverage:

- create Question with same-subject Knowledge Points.
- reject cross-subject Knowledge Point links.
- validate answer shape by Question Type.
- archive Question.
- optimistic version conflict.
- admin auth required.

### Frontend

Run:

```text
npx tsc --noEmit --pretty false
npm test
npm run build
```

If UI changes are implemented, inspect:

- `/manage/questions`
- `/manage/questions/[id]`

Required states:

- loading
- empty
- error
- validation error
- archived state
- keyboard focus visible

### Route Check

Confirm:

- `/manage/questions` exists.
- `/manage/questions/[id]` exists.
- no public `/questions` route is introduced.
- existing public `/`, `/blog`, `/notes`, and `/mistakes` remain outside Batch 3 changes.

### Boundary Check

Confirm unchanged:

- no AI/OCR integration.
- no file upload.
- no Mistake implementation.
- no Review implementation.
- no Search or Analytics implementation.
- no multi-user owner model.

### P0-02 Documentation Check

Validated in the current workflow:

- direct Question CRUD is the canonical Batch 3 contract;
- legacy Draft compatibility is explicitly bounded and not expanded;
- data-bearing old Question/Draft rows are preserved as a migration constraint;
- no code, database, migration, API, or frontend route was changed in P0-01/P0-02.

Migration Gate: BLOCKED pending explicit approval of the updated task list and the P0-04 reconciliation plan.

## Validation Recording

Actual command results are recorded in [validation.md](./validation.md).
