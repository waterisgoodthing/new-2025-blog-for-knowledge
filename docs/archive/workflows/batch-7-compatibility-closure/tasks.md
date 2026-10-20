# Tasks

> Status: design/audit complete; implementation is blocked pending explicit approval of this task list.

## P0-01 Current-State Audit

- [x] Read Batch 5/6 closure and public mistake gate acceptance.
- [x] Read MVP Batch 7 scope and current route/permission architecture.
- [x] Check current Alembic revision and data-bearing row counts.
- [x] Record dirty-worktree and compatibility risks.

## P0-02 Compatibility Contract Freeze

- [x] Classify old write/mistake/detail routes as preserve, redirect/notice, or active.
- [x] Freeze public/private route permission behavior and no-data-loss rules.

## P0-03 Route And Permission Audit Tests

- [x] Add focused checks for public route availability and absence of admin-only requests.
- [x] Add focused checks for AuthGate coverage on private pages and backend admin boundaries where applicable.

## P0-04 Minimal Compatibility Fixes

- [x] Apply only approved route, access-state, confirmation, or dead-link fixes.
- [x] Preserve public reads and existing data contracts.

## P0-05 Local Trial And Validation

- [x] Run frontend tests, typecheck, build, and route checks.
- [x] Run targeted backend permission/import checks.
- [x] Recheck Alembic revision, row counts, representative IDs, and public/private behavior.
- [x] Record local trial instructions and known warnings.

## P0-06 Handoff And Closure

- [x] Record evidence, residual risks, and compatibility decisions.
- [x] Mark Batch 7 closed only after explicit human acceptance; do not begin another batch.

## Closure Gate

Batch 7 tasks P0-02 through P0-06 are complete. Batch 8 is not started automatically.
