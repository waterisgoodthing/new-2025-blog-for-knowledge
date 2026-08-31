# P1 Acceptance Cleanup Patch

## Task Goal

Close the P1 issues discovered by the System Freeze & Acceptance Sprint without expanding product scope.

This patch is limited to:

- public-page admin affordance cleanup
- fresh setup documentation and setup-check hardening

It must not add business features, migrations, database tables, AI Gateway refactors, Prompt admin, A/B testing, provider probes, circuit breakers, recommendation changes, or backend permission rewrites.

## Touched Domains

- `home`: public navigation entry behavior.
- `notes`: public empty-state and create-action affordances.
- `manage`: only as destination semantics; no management feature changes.
- shared frontend infrastructure: `src/components/nav-card.tsx`, `src/components/mobile-nav.tsx`, `src/components/empty-state.tsx`.
- setup/shared infrastructure: `README.md`, `.env.example`, `backend/.env.example`, `scripts/setup.mjs`.

## Current Status

Status: `completed`.

The repository has a large pre-existing dirty worktree. This workflow preserved unrelated user and generated changes. Implementation started only after the user explicitly approved `tasks.md`.

## Source Evidence

This workflow follows the SFA P1 findings recorded in:

- `docs/workflows/system-freeze-acceptance-sprint/audit.md`
- `docs/workflows/system-freeze-acceptance-sprint/final-decision.md`
- `docs/workflows/system-freeze-acceptance-sprint/validation.md`

## Workflow Files

- [Requirements](requirements.md)
- [Design](design.md)
- [Tasks](tasks.md)
- [Validation](validation.md)
- [Diff Report](diff-report.md)
- [Handoff Prompt](handoff-prompt.md)

## Planned Output

- A small, auditable patch for P1 acceptance cleanup.
- Validation evidence proving public pages no longer expose anonymous admin affordances.
- Fresh setup checks/docs that make Python version, CORS format, and production API URL rules hard to miss.
