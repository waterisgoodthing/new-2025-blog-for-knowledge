# Tasks

> Status: P0-01 through P0-06 implemented, validated, and accepted; Batch 6 closed.

## P0-01 Read-Only Audit

- [x] Read Batch 5 acceptance and Batch 6 architecture boundaries.
- [x] Inspect current AI, OCR/Capture, Attachment, manage routes, clients, and backend entry points.
- [x] Record live Alembic revision and read-only row counts.
- [x] Separate existing dirty-worktree code from approved Batch 6 scope.

## P0-02 Scope And Placeholder Contract Freeze

- [x] Freeze the three placeholder page responsibilities and static unavailable states.
- [x] Confirm no live AI/OCR/Capture/Job API call and no database schema/data changes.

Completion result:

- `/manage/ai`, `/manage/ai/runs`, and `/manage/capture` are static unavailable/empty experiences only.
- Existing AI/Capture rows, clients, components, routers, services, and models remain outside implementation scope.
- Reserved status contracts remain documentation-only.

## P0-03 RED Tests And Route Guards

- [x] Add tests proving placeholder routes render without AI/OCR API calls.
- [x] Add route checks proving `/manage/ai`, `/manage/ai/runs`, and `/manage/capture` remain behind the manage `AuthGate`.

Completion result:

- Added static page tests for unavailable states, absence of historical run data, and absence of upload/processing controls.
- The shared manage layout remains the route-level AuthGate boundary.

## P0-04 UI Placeholder Implementation

- [x] Replace only approved placeholder page composition as needed.
- [x] Preserve public pages, Batch 5 attachment behavior, and existing backend modules.

Completion result:

- Updated only the three placeholder route texts from stale Batch 1 wording to Batch 6 static boundaries.
- No AI/Capture client import, API call, backend edit, migration, or database write was added.

## P0-05 Validation

- [x] Run frontend tests, typecheck, build, and route checks.
- [x] Run backend import/route checks without invoking providers or mutating data.
- [x] Recheck Alembic revision and row counts for `capture_items`, `ai_call_logs`, `ai_runs`, `attachments`, and `attachment_links`.

Completion result:

- Frontend tests: `20 passed`; TypeScript passed; production build passed.
- Build routes include `/manage/ai`, `/manage/ai/runs`, and `/manage/capture`.
- Backend import and reserved-route checks passed; existing Capture admin routes remain protected.
- Reserved `/api/admin/ai/status` and attachment OCR status routes are absent.
- Alembic remains `020 (head)`; audited row counts remain unchanged.

## P0-06 Handoff And Closure

- [x] Record validation evidence and residual risks.
- [x] Mark Batch 6 closed only after explicit human acceptance; do not begin Batch 7.

Current result:

- Evidence is recorded in `validation.md` and `handoff-prompt.md`.
- Human acceptance recorded. Batch 6 is closed and Batch 7 remains blocked.

Acceptance recorded:

> Accept Batch 6 AI/OCR placeholder implementation; do not enter Batch 7.

Batch 7 requires a separate design package, audit, task list, and explicit approval.

## Closure Gate

Implementation approval and final acceptance were recorded:

> Approve Batch 6 tasks P0-02 through P0-06.

> Accept Batch 6 AI/OCR placeholder implementation; do not enter Batch 7.
