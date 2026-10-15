# Tasks

> Status: P0-01 through P0-08 completed and accepted; Batch 4 closed.

## P0-01 Current-State Audit

- [x] Inspect active Alembic revision and row counts for Mistake/Review/Note tables.
- [x] Read current models, schemas, services, routers, clients, and tests.
- [x] Record public Note compatibility and private Mistake/Review dependencies.

Completion criteria:

- Existing tables are classified as data-bearing or empty.
- Old Note-backed public mistake/review behavior is explicitly separated.
- No code, database, or migration changes are made by the audit.

## P0-02 Requirements And Domain Freeze

- [x] Confirm MistakeDraft -> Mistake -> ReviewItem -> ReviewRecord as the only Batch 4 core flow.
- [x] Confirm public `Note(type="mistake")` remains compatible and is not silently migrated.
- [x] Confirm fixed-interval Review MVP and exclusion of Practice/AI/OCR/BKT.
- [x] Resolve whether any existing API/model contract requires an additive migration.

Completion result:

- Duplicate conversion is frozen as `200` for a valid existing target and `409` for an inconsistent binding.
- QuestionDraft conversion must resolve a converted formal Question ID.
- No Batch 4 migration is currently required by the audit; P0-04 must still verify the full `013 -> 020` lineage before implementation changes.

## P0-03 Implementation Plan And RED Tests

- [x] Add or align tests for draft source rules, confirmation, idempotency, archive behavior, and review conflicts.
- [x] Record initial failing tests for approved changes only.

Completion result:

- Added RED coverage for inconsistent converted-target handling and QuestionDraft-to-formal-Question resolution.
- Initial failure confirmed `MistakeNotFound` was returned for an invalid converted target instead of the frozen `MistakeConflict`/`409` contract.
- Existing tests continue to cover idempotent conversion, archive-to-paused synchronization, fixed intervals, stale review submission, and unconfirmed queue exclusion.

## P0-04 Migration Reconciliation

- [x] Compare current 013-020 schema with the frozen Batch 4 target.
- [x] Confirm whether additive/reversible migration changes are required.
- [x] Preserve all existing Mistake/Review/Note rows and downstream FKs.

Completion result:

- Actual lineage is `013 -> ... -> 018 -> 019 -> 020`; current database is `020 (head)`.
- No Batch 4 migration is required for the approved contract.
- Read-only counts remain `mistake_drafts=3`, `mistakes=3`, `review_items=3`, `review_records=4`, `notes=13`.
- `alembic check` remains blocked only by the known Batch 2 taxonomy metadata drift; no Batch 4 table drift was detected.

## P0-05 Backend Mistake And Review Implementation

- [x] Align schemas/services/routes with the approved contract.
- [x] Keep routers thin and admin-protected.
- [x] Preserve generic Mistake Knowledge Point links.
- [x] Verify transaction and idempotency behavior.

Completion result:

- Normal duplicate conversion returns the existing Mistake; invalid or incomplete target bindings now raise `MistakeConflict` for HTTP `409`.
- QuestionDraft conversion validates converted status, `target_type='question'`, valid UUID, and existing formal Question.
- Existing admin routers and backend `get_current_admin` dependencies remain unchanged and protected.
- No new tables, migration, Practice, AI, OCR, Capture, or Note migration were introduced.

## P0-06 Frontend Private Learning Pages

- [x] Align typed clients for private MistakeDraft/Mistake/ReviewItem APIs.
- [x] Implement or align `/manage/mistakes`, `/manage/mistakes/[id]`, and `/manage/review`.
- [x] Preserve public `/mistakes` and Note-backed public detail behavior.

Completion result:

- Replaced Batch 1 placeholders with private Mistake list/detail and Review queue surfaces.
- Existing AuthGate protects the complete `/manage/**` workspace; typed clients use `/api/admin/**` paths.
- Draft detail supports both `pending` and `needs_fix` editing states.
- Public Mistake routes were not changed and no public page calls admin APIs.
- Frontend TypeScript check passed: `npx tsc --noEmit --pretty false`.

## P0-07 Validation

- [x] Run targeted and full backend tests.
- [x] Run migration checks and read-only row preservation checks.
- [x] Run frontend typecheck, tests, build, and route checks if UI changes are made.

Completion result:

- Mistake/Review targeted tests: `10 passed`.
- Full backend regression: `236 passed, 2 pre-existing AI AsyncMock warnings`.
- Frontend tests: `16 passed`; TypeScript and production build passed.
- Build route output includes `/manage/mistakes`, `/manage/mistakes/[id]`, and `/manage/review`.
- Database remains `020 (head)` with `mistake_drafts=3`, `mistakes=3`, `review_items=3`, `review_records=4`, `notes=13`.
- `alembic check` remains a known Batch 2 taxonomy metadata gap; no Batch 4 migration was added.

## P0-08 Handoff

- [x] Record final evidence and known risks.
- [x] State whether Batch 4 is accepted without entering Batch 5.

Completion result:

- Final evidence and risks are recorded in [validation.md](./validation.md) and [handoff-prompt.md](./handoff-prompt.md).
- Batch 4 was accepted by the user.
- Batch 5 is not started and no automatic transition is authorized.

## Approval

P0-02 through P0-08 were explicitly approved and executed.

Acceptance recorded:

> Accept Batch 4 Mistake and Review implementation; do not enter Batch 5.
