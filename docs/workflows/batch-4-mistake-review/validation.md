# Batch 4 Validation

## Results

- Database revision: `020 (head)`.
- Mistake/Review targeted tests: `10 passed`.
- Full backend regression: `236 passed, 2 pre-existing AI AsyncMock warnings`.
- Frontend tests: `16 passed`.
- Frontend TypeScript check: passed.
- Frontend production build: passed.
- Built routes include `/manage/mistakes`, `/manage/mistakes/[id]`, and `/manage/review`.

## Row Preservation

Read-only counts after implementation:

| Table | Rows |
|---|---:|
| `mistake_drafts` | 3 |
| `mistakes` | 3 |
| `review_items` | 3 |
| `review_records` | 4 |
| `notes` | 13 |

No migration ran in Batch 4. No Mistake, Review, or Note rows were rewritten, deleted, or migrated.

## Known Gaps

`alembic check` still reports the previously recorded Batch 2 taxonomy index/model drift. It is outside Batch 4 and was not changed here.

The full backend suite retains two pre-existing AI gateway AsyncMock warnings; the suite passes.

## Boundary Verification

Unchanged:

- public Note-backed `/mistakes` reads;
- old `/api/review/*` Note compatibility API;
- Question canonical content;
- Practice, Attempt, AI, OCR, Capture, BKT, search, analytics, and Batch 5 attachment work.

## Acceptance

Batch 4 was accepted by the user. Batch 5 remains explicitly out of scope and has not started.
