# Tasks — System Freeze & Acceptance Sprint

> Status: `completed`
>
> Rule: Implementation, validation, status cleanup, fresh setup, and final audit execution start only after the user explicitly approves this task list.

## Approval Gate

- [x] User approves this `tasks.md` for execution.

## SFA-01 — Clean Workflow Task Status

- [x] Inspect required workflow folders for status language and conflicting states.
- [x] Update completed tasks to `closed` / `completed` where status wording is stale.
- [x] Move or summarize unfinished enhancements into deferred backlog wording.
- [x] Write `diff-report.md` with conflicts found, files fixed, and backlog items left deferred.

## SFA-02 — Freeze Current System Boundary

- [x] Create or update `docs/final-system-boundary.md`.
- [x] Explicitly document AI formal-write boundaries and stream compatibility-only status.
- [x] Explicitly document `ai_call_logs`, `ai_runs`, usage/cost, and health fact-source boundaries.

## SFA-03 — Complete Local Acceptance

- [x] Run backend pytest: `cd backend && .venv/bin/python -m pytest tests/ -ra`.
- [x] Run Alembic current: `cd backend && PYTHONPATH=. .venv/bin/alembic current`.
- [x] Run frontend typecheck: `npx tsc --noEmit`.
- [x] Run frontend build: `npm run build`.
- [x] Run diff whitespace check: `git diff --check`.
- [x] Run `npm run lint` if supported, or record why it is unavailable.
- [x] Validate anonymous pages: `/`, `/blog`, `/notes`.
- [x] Validate management pages: `/manage`, `/manage/capture`, `/manage/ai`, `/manage/ai/runs`, `/manage/review`, `/manage/mistakes`, `/manage/questions`, `/manage/attachments`.
- [x] Record all command and browser results in `validation.md`.

## SFA-04 — Consolidate Remaining Backlog

- [x] Create or update `docs/final-backlog.md`.
- [x] Include every required backlog item with priority, current-use blocking status, suggested batch, risk, and validation method.
- [x] Ensure deferred items are not described as current blockers unless evidence shows they block acceptance.

## SFA-05 — Codex Quality Audit

- [x] Audit backend permissions, public/admin API boundaries, AI output cleaning, `ai_call_logs`/`ai_runs`, review, attachments, migrations, services, and exceptions.
- [x] Audit frontend AuthGate coverage, public route behavior, AI panel sensitive fields, UI states, deprecated routes, and legacy write paths.
- [x] Audit AI governance boundaries, fallback explainability, usage/cost truthfulness, health snapshot truthfulness, and stream deprecation language.
- [x] Audit tests for skip/xfail, shared DB fragility, contract drift, and warnings.
- [x] Write `audit.md` with P0, P1, P2, P3, false positives, repair order, and daily-use recommendation.

## SFA-06 — Fresh Setup Experiment

- [x] Create or reuse isolated path `/tmp/2025-blog-public-fresh-setup`.
- [x] Install dependencies and record Node/Python/tooling versions.
- [x] Evaluate `.env.example`, setup docs, database initialization, and manual env gaps.
- [x] Run `alembic upgrade head` in the fresh setup.
- [x] Start backend and frontend in the fresh setup.
- [x] Verify admin creation/login and access to `/manage`, `/manage/ai`, and `/manage/capture`.
- [x] Run minimal pytest smoke tests and `npm build`.
- [x] Record Fresh Setup Report in `validation.md` or a dedicated fresh setup section.

## SFA-07 — Final Handoff

- [x] Create or update `docs/final-handoff.md`.
- [x] Include system positioning, feature map, routes, database/migrations, AI architecture, permissions, run/test commands, daily-use flow, risks, backlog, and next-stage recommendations.

## SFA-08 — Final Daily-Use Decision

- [x] Return conclusion A, B, or C.
- [x] If conclusion is B, list required P0/P1 fixes, deferrable P2 items, admin-only capabilities, and capabilities that must not be public.

## Stop Rule

- [x] If any P0/P1 issue is found, record it and wait for explicit user approval before applying fixes.
