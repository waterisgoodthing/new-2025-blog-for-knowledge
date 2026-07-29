# Tasks — P1 Acceptance Cleanup Patch

> Status: `completed`
>
> Rule: Do not modify business/source code until this task list is explicitly approved by the user.

## Approval Gate

- [x] User approves this `tasks.md` for execution.

## P1-01 — Public Admin Affordance Cleanup

- [x] Remove or auth-gate the desktop public navigation `管理` affordance in `src/components/nav-card.tsx`.
- [x] Remove or auth-gate the mobile public `管理` affordance in `src/components/mobile-nav.tsx`.
- [x] Remove the shared `EmptyState` default admin creation action from anonymous/public contexts.
- [x] Adjust `/notes` public empty-state create actions so anonymous visitors do not see admin workspace/capture links.
- [x] Confirm backend permissions and `/manage` route protection remain unchanged.

## P1-02 — Fresh Setup Hardening

- [x] Update README setup instructions for supported Python version expectations.
- [x] Update README or env comments for local-dev versus production-build `NEXT_PUBLIC_API_URL`.
- [x] Update README or env comments to make comma-separated `ALLOWED_ORIGINS` explicit.
- [x] Update `scripts/setup.mjs` Python check so unsupported Python versions are reported clearly.
- [x] Ensure setup docs do not suggest `AUTH_BYPASS` for acceptance or production.

## Validation

- [x] Run `npx tsc --noEmit`.
- [x] Run `npm run build`.
- [x] Run `git diff --check`.
- [x] Run `npm run check` if `scripts/setup.mjs` changes are implemented.
- [x] Browser-check anonymous `/`, `/blog`, `/notes`, and `/manage`.
- [x] Record validation in `validation.md`.

## Closure

- [x] Write `diff-report.md`.
- [x] Update final status in this workflow.
- [x] Summarize remaining deferred P2 items without treating them as current blockers.

## Stop Rule

- [x] If a new P0/P1 appears outside this approved patch scope, record evidence and stop for user approval before fixing.
