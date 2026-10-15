# Validation Plan

## UI

- Run frontend tests and `npx tsc --noEmit --pretty false`.
- Run `npm run build` and verify the three manage routes are present.
- Inspect source to confirm no placeholder imports an AI, OCR, Capture, Job, or run API.

## Backend

- Import/start checks only; do not invoke provider, OCR, capture recognition, or draft-generation services.
- Confirm existing admin routes still require `get_current_admin`.

## Database

- Run `PYTHONPATH=. .venv/bin/alembic current`.
- Re-read counts for `capture_items`, `ai_call_logs`, `ai_runs`, `attachments`, and `attachment_links`.
- No migration, insert, update, delete, or file upload is allowed in validation.

## Closure

Record known pre-existing warnings separately. Batch 6 remains open until human acceptance and must not roll into Batch 7 automatically.
