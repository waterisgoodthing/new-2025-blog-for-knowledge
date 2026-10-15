# Batch 7 Validation

## Final Status

Batch 7 accepted. P0-02 through P0-06 completed within the approved compatibility and closure scope.

No Batch 8 work was started and no next batch should start automatically.

## Completed Changes

- Froze public/private route contracts and legacy entry classifications in `audit.md`.
- Added `src/app/batch7-compatibility.test.ts` for public/private route availability, AuthGate coverage, and legacy route preservation.
- Added `backend/tests/test_batch7_compatibility.py` for public Note read and admin mutation dependency contracts.
- Added an error recovery state to `src/app/mistakes/review/page.tsx`; review request failure now exits loading state and links back to `/manage/mistakes`.
- No route was deleted, no public route was gated, and no data contract was changed.

## Frontend Evidence

| Check | Result |
|---|---|
| `npm test` | PASS — 8 files, 25 tests |
| `npx tsc --noEmit --pretty false` | PASS — exit 0 |
| `npm run build` | PASS — Next.js production build completed |
| Route output | PASS — `/`, `/blog`, `/blog/[id]`, `/notes`, `/notes/[id]`, `/mistakes`, `/manage/**`, `/mistakes/review`, `/write-note*`, `/write-mistake*` present |
| Batch 7 focused frontend tests | PASS — 5 tests |

Build warnings were limited to the existing `baseline-browser-mapping` freshness warning and Node `module.register()` deprecation warning. They did not fail the build.

## Backend Evidence

- Import check passed: `from main import app`; app registered 177 routes.
- Focused route/permission tests passed: `12 passed`.
- Public Note GET routes do not depend on `get_current_admin`.
- Review, attachment, capture, AI, Note create/update/delete, and image upload routes retain `get_current_admin`.
- No AI provider, OCR, Capture processing, background job, or external service was invoked.

## Database Evidence

- `PYTHONPATH=. .venv/bin/alembic current` returned `020 (head)`.
- No Batch 7 migration was created or executed.
- No INSERT, UPDATE, DELETE, cleanup, re-keying, or data migration was executed.
- Read-only counts match the P0-01 baseline:

```text
notes=13
subjects=1
knowledge_points=3
question_drafts=3
questions=3
mistake_drafts=3
mistakes=3
review_items=3
review_records=4
attachments=1
attachment_links=1
```

Representative current IDs were read-only sampled and preserved in the validation run output. P0-01 recorded counts but not representative IDs, so a strict before/after ID comparison is unavailable; no database write command ran during this batch.

## Legacy Entry Decisions

- `/write-note`: preserve + active, protected legacy editor.
- `/write-note/[slug]`: preserve + active, protected historical edit route.
- `/write-mistake`: preserve + redirect/notice, protected compatibility form explicitly directing users to `/manage/mistakes`.
- `/write-mistake/[slug]`: preserve + active, protected historical edit route.
- Current content edit links use `/manage/**`; legacy routes remain available and were not deleted.

## Known Risks

- The repository contains unrelated dirty changes from earlier batches and adjacent workflows; they were preserved and not included in the Batch 7 change set.
- The database baseline did not include pre-batch representative IDs, limiting ID-level before/after proof to the current read-only snapshot.
- Build emits non-blocking dependency freshness/deprecation warnings described above.

## Local Trial Runbook

```bash
npm test
npx tsc --noEmit --pretty false
npm run build
cd backend
PYTHONPATH=. .venv/bin/python -c "from main import app; print(len(app.routes))"
PYTHONPATH=. .venv/bin/pytest -q tests/test_batch7_compatibility.py tests/test_anon_capture_access.py tests/test_mistake_routes.py tests/test_attachment_routes.py
PYTHONPATH=. .venv/bin/alembic current
```

Keep public routes anonymous-readable, keep admin mutations behind backend authorization, and do not invoke disabled AI/OCR/Capture capabilities during local trial.
