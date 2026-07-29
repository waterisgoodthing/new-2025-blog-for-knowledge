# Current-State Audit

## Architecture Facts

- `mvp-scope.md` defines Batch 6 as AI/OCR placeholders and reserved interfaces only.
- `capture-router.md` is a future design and describes classification/draft output, but does not authorize implementation in this batch.
- `attachment-system.md` defines attachments as private source material; Batch 5 explicitly excluded OCR and Capture.

## Current Repository Facts

- Manage routes exist for `/manage/ai`, `/manage/ai/runs`, and `/manage/capture`.
- The AI and Capture route pages are currently placeholder wrappers in the inspected tree.
- The worktree also contains AI/Capture components, API clients, backend routers, services, and models. These are existing worktree facts and are not automatically in Batch 6 scope.
- Manage workspace layout uses `AuthGate`.

## Database Facts (Read Only)

- Alembic revision: `020 (head)`.
- `capture_items`: 0 rows.
- `ai_call_logs`: 40 rows.
- `ai_runs`: 25 rows.
- `attachments`: 1 row.
- `attachment_links`: 1 row.
- No migration or data mutation was executed for this audit.

## Risks

1. Existing AI/Capture code can be mistaken for approved Batch 6 scope.
2. Reading historical AI rows from a new placeholder can imply an enabled audit feature.
3. Uploading from Capture would bypass Batch 5's boundary and start OCR intake prematurely.
4. Exposing provider/model/cost details without verified runtime state would create false governance signals.
