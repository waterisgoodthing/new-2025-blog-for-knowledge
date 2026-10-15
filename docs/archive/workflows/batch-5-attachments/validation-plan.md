# Validation Plan

## Before Implementation

- Confirm current revision remains `020 (head)`.
- Snapshot read-only counts and identifiers for `attachments` and `attachment_links`.
- Confirm no migration is needed before coding.

## Backend

- Upload: allowed MIME, text/plain compatibility, empty/oversize/unsafe input, checksum, atomic failure cleanup.
- Access: admin authorization, active-only content, missing/deleted behavior, no path/key leakage.
- Links: target existence, active attachment requirement, duplicate conflict, delete behavior.
- Regression: existing attachment/link rows remain unchanged.

## Frontend

- `npx tsc --noEmit`.
- Targeted attachment tests and full frontend tests if configured.
- `npm run build`.
- Verify `/manage/attachments` and `/manage/attachments/[id]` are present and protected.

## Database

- `PYTHONPATH=. .venv/bin/alembic current`.
- `alembic check` may retain known pre-existing taxonomy drift; report it separately.
- Re-read counts and key identifiers after tests. No production data mutation is allowed.
