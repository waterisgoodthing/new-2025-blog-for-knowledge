# Current-State Audit

## Scope And Lines

This audit covers the private learning backend attachment line and the existing manage attachment UI. Public blog/content routes were not changed.

## Repository Facts

- Existing model: `backend/app/models/attachment.py`.
- Existing schema: `backend/app/schemas/attachment.py`.
- Existing service/router/tests cover local bytes upload, metadata, content path resolution, soft delete, links, and admin routes.
- Existing manage routes: `src/app/manage/(workspace)/attachments/page.tsx` and `[id]/page.tsx`.
- Existing typed client: `src/lib/api/attachments.ts`.
- Migration source: `backend/alembic/versions/014_add_attachments.py`.

## Database Facts (Read Only)

- Alembic revision: `020 (head)`.
- `attachments`: 1 row; status `active`; MIME `text/plain`; visibility `private`.
- `attachment_links`: 1 row; target `mistake`; purpose `answer`.
- `attachments.created_by` is nullable FK to `users.id` with `ON DELETE SET NULL`.
- Current checks enforce local provider, private visibility, valid status, nonnegative size, and checksum length.
- No schema write, migration, or data mutation was executed.

## Compatibility Findings

1. Existing data proves `text/plain` is a live compatibility requirement for Batch 5.
2. Existing link storage uses a string `target_id`, while the current request schema accepts UUIDs; implementation must preserve the stored string-compatible contract.
3. Existing soft-delete behavior preserves the row and does not delete physical content; this remains the Batch 5 baseline.
4. `created_by` is audit metadata, not a future ownership model. Do not add owner/tenant fields in this batch.

## Risks To Resolve During Implementation

- Ensure upload failure cannot leave a database row or partial file.
- Ensure missing/deleted files never get served through content endpoints.
- Ensure public routes never call admin attachment endpoints.
- Keep existing attachment/link row identifiers stable.
