# Tasks

> Status: P0-01 through P0-08 completed and accepted; Batch 3 closed.
>
> Implementation approval was granted in the conversation before P0-03; no automatic transition to Batch 4 is allowed.

## P0-01 Current-State Audit And Drift Report

- [x] Inspect active Alembic revision, real database schema, row counts, and existing Question-related tables.
- [x] Compare existing code contracts against Batch 2 taxonomy and the new Batch 3 frozen design.
- [x] Update [audit.md](./audit.md) with exact findings and implementation strategy.

Completion criteria:

- Existing Question/Draft tables are classified as absent, empty-compatible, data-bearing, or blocking.
- Old `knowledge_point_links` usage is classified as reusable compatibility, migration input, or rejected.
- No code/database changes except workflow documentation.

Result:

- Existing Question/Draft tables are data-bearing.
- Existing `knowledge_point_links` is migration input and compatibility data, not automatically accepted as final frozen relation.
- Current database is `019 (head)`.
- No code, database, migration, frontend route, or API change was made.

## P0-02 Finalize Requirements Gate

- [x] Reconfirm that Batch 3 implements direct Question CRUD first; existing Draft workflow remains compatibility-only.
- [x] Update [requirements.md](./requirements.md) with the unavoidable data-bearing and downstream compatibility constraints.
- [x] Confirm that no scope expansion into Draft, Mistake, Capture, Attachment, AI, or Review is authorized.

Completion criteria:

- Question System scope remains explicit.
- No hidden old-model assumption survives into implementation.

Result:

- Direct Question CRUD is the canonical Batch 3 contract.
- Legacy DraftItem / QuestionDraft remains readable compatibility infrastructure.
- Migration strategy is additive and non-destructive by default.
- P0-03 and later were subsequently approved and completed under the recorded implementation gate.

## P0-03 Backend Test Plan And RED Tests

- [x] Add targeted backend tests for direct Question creation, structured answer validation, source preservation, cross-subject Knowledge Point rejection, update, and archive behavior.
- [x] Record initial failing tests before implementation.

Completion criteria:

- Tests fail for missing or mismatched implementation behavior.
- Test scope does not enter Mistake/Review/AI/OCR.

Result:

- `tests/test_question_domain.py` now defines the first direct Question contract.
- Initial RED evidence: missing `QuestionCreate`, then missing `create_question` service entry point.
- Existing Draft tests remain unchanged and continue to define the compatibility boundary.

## P0-04 Migration Reconciliation

- [x] Create or adjust Alembic migration according to audit findings.
- [x] Preserve Batch 2 `subjects` and `knowledge_points`.
- [x] Avoid destructive changes unless separately approved.

Completion criteria:

- Migration can run from current DB state to target state.
- No old data is silently dropped.
- Migration path is documented.

Result:

- Added migration `020_add_canonical_question_contract` from `019` to `020`.
- Added canonical Question fields, source metadata, and dedicated Question-Knowledge Point relation.
- Backfilled existing Question rows and `knowledge_point_links(target_type='question')`.
- Preserved legacy fields, generic links, Draft tables, and downstream foreign keys.
- First run exposed and fixed a PostgreSQL JSON comparison issue; final upgrade completed at `020 (head)`.

## P0-05 Backend Question Domain Implementation

- [x] Implement or align `Question`, `QuestionSource`, and Question-KnowledgePoint relation models.
- [x] Implement schemas and service validation.
- [x] Implement thin admin routers under `/api/admin/questions`.
- [x] Require backend admin authentication for all endpoints.

Completion criteria:

- Question CRUD uses backend service rules.
- Cross-subject Knowledge Point links are rejected.
- Answer/analysis/source/difficulty contracts are stable.

Result:

- Added direct Question create and PATCH contracts while preserving legacy PUT/Draft conversion compatibility.
- Added structured answer/options validation, source validation, canonical analysis/difficulty fields, and dedicated relation handling.
- Updated backend readiness revision to `020`.
- Targeted backend Question/Draft/route tests pass: `14 passed`.

## P0-06 Frontend API And Manage Pages

- [x] Align `src/lib/api/questions.ts` with the frozen contract.
- [x] Implement or align `/manage/questions`.
- [x] Implement or align `/manage/questions/[id]`.
- [x] Preserve manage shell and public pages.

Completion criteria:

- Admin can view list/detail and create/update/archive Questions if approved in final UI scope.
- UI has loading, empty, validation error, and archived states.

Result:

- Added typed direct Question create/PATCH clients and retained a legacy PUT adapter.
- Replaced Batch 1 placeholders with Question list, detail/edit, and new-question entry surfaces.
- Reused existing AuthGate, manage shell, taxonomy selector, loading/error/empty/status components.
- Frontend TypeScript check passed: `npx tsc --noEmit --pretty false`.

## P0-07 Validation

- [x] Run backend targeted tests.
- [x] Run database migration checks.
- [x] Run `npx tsc --noEmit --pretty false`.
- [x] Run `npm test`.
- [x] Run `npm run build`.
- [x] Inspect manage Question route output from the production build.

Completion criteria:

- Results are recorded in validation documentation.
- Failures are either fixed in scope or explicitly classified as pre-existing/out-of-scope.

Result:

- Backend targeted tests: `14 passed`.
- Full backend regression: `234 passed, 2 warnings`.
- Frontend tests: `16 passed`.
- Typecheck and build: passed.
- Alembic current: `020 (head)`.
- `alembic check` retains known Batch 2 taxonomy metadata drift; recorded as out of scope.

## P0-08 Handoff

- [x] Record final implementation decisions, validation evidence, and remaining risks.
- [x] Identify Batch 4 dependencies for Mistake / Review without starting Batch 4.

Completion criteria:

- Batch 3 is accepted and closed.
- No automatic transition to Batch 4.

Result:

- Handoff recorded in [handoff-prompt.md](./handoff-prompt.md).
- Batch 4 remains a separate approval gate.

## Approval

P0-01 read-only audit was requested by the user and completed.

P0-02 requirements gate is completed as documentation-only reconciliation.

Acceptance state:

> Batch 3 implementation completed with the P0-02 additive compatibility strategy. Batch 4 requires a separate approval.
