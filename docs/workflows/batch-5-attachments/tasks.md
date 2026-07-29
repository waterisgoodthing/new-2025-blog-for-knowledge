# Tasks

> Status: P0-02 through P0-08 implemented, validated, and accepted; Batch 5 closed.

## P0-01 Read-Only Audit

- [x] Check worktree and identify attachment-domain files.
- [x] Inspect current models, schemas, service, routers, clients, pages, and tests.
- [x] Inspect migration lineage, live schema, constraints, indexes, and data counts.
- [x] Record compatibility risks and confirm no database changes were executed.

## P0-02 Contract And Scope Freeze

- [x] Freeze upload, preview/download, soft-delete, link, MIME, and error contracts.
- [x] Confirm no OCR, Capture, AI, derivatives, object storage, or public delivery.

Completion result:

- Approved contracts require bounded streaming, temporary-file SHA-256, atomic finalization, compensating cleanup, explicit content disposition, symlink rejection, idempotent missing transition, and `204` soft delete.
- New link creation is limited to `source`, `question`, `answer`, and `inline`; legacy AI-purpose rows remain readable only.
- No schema change is authorized without a separate approval.

## P0-03 RED Tests

- [x] Add failing/targeted tests for upload validation, path containment, content access, delete state, and link conflicts.
- [x] Add row-preservation assertions for existing attachment/link data.

Completion result:

- RED run initially failed because the approved streaming service contract did not exist.
- Added coverage for bounded reads, control characters, symlink rejection, legacy AI-purpose creation rejection, path containment, missing transition, soft delete, and duplicate links.
- The test module passes after the backend implementation; final row-preservation assertions remain in P0-07 against the live database.

## P0-04 Schema Reconciliation Gate

- [x] Reconcile model/migration/live schema after contract freeze.
- [x] If drift requires migration, stop and request separate migration approval; otherwise record no migration required.

Completion result:

- Live schema matches migration `014` and the attachment ORM shape; current revision remains `020 (head)`.
- `alembic check` reports only the previously known Batch 2 `knowledge_points` index/constraint metadata drift.
- No Batch 5 migration is required or authorized.

## P0-05 Backend Implementation

- [x] Align admin attachment endpoints with the approved contract.
- [x] Preserve backend admin authorization and thin-router/service boundaries.
- [x] Verify atomic writes, missing-file handling, soft delete, and link validation.

Completion result:

- Upload now streams bounded chunks into a temporary file, computes SHA-256, fsyncs, and atomically renames the opaque storage key with cleanup on failure.
- Content access supports `inline`/`attachment`, rejects symlinked or escaping paths, and only serves active files.
- Delete is soft and idempotent; the router returns `204` and preserves links.
- New link creation excludes AI purposes while legacy AI-purpose rows remain readable.

## P0-06 Manage UI Implementation

- [x] Align list/detail/upload/link surfaces with the approved private attachment contract.
- [x] Preserve AuthGate and avoid public attachment controls or admin API calls from public pages.

Completion result:

- Replaced the two Batch 1 attachment placeholders with the existing private list/detail components.
- Upload, preview, download, soft-delete, status filtering, and link management remain under the manage workspace `AuthGate`.
- The frontend client now models `204` deletion and explicit `inline`/`attachment` content URLs.

## P0-07 Validation

- [x] Run targeted and full backend tests.
- [x] Run frontend typecheck, tests, build, and route checks.
- [x] Recheck Alembic revision and attachment/link row preservation.

Completion result:

- Targeted backend: `13 passed`; full backend: `239 passed`, with 2 pre-existing AI gateway AsyncMock warnings.
- Frontend tests: `16 passed`; `npx tsc --noEmit --pretty false` passed.
- Build route output includes `/manage/attachments` and `/manage/attachments/[id]`; final build rerun is recorded in `validation.md`.
- Database remains `020 (head)`; `attachments=1` and `attachment_links=1`; existing IDs are unchanged.

## P0-08 Handoff And Closure

- [x] Record validation evidence and residual risks.
- [x] Mark Batch 5 closed only after explicit acceptance; do not enter Batch 6 automatically.

Completion result:

- Validation and handoff evidence were accepted by the user.
- Batch 5 is closed. Batch 6 is tracked in a separate approved-start workflow.

## Acceptance Gate

Implementation approval was granted:

> Approve Batch 5 tasks P0-02 through P0-08.

Final human acceptance recorded:

> 批准 batch5 通过，开始 batch6
