# Diff Report — P1 Acceptance Cleanup Patch

Status: `completed`

## Summary

Closed the two approved SFA P1 issues:

1. Public pages no longer expose anonymous management navigation or default admin creation actions.
2. Fresh setup now documents and checks the Python/API URL/CORS constraints that blocked the SFA fresh setup experiment.

## Files Changed

Frontend public/admin affordance cleanup:

- `src/components/nav-card.tsx`
- `src/components/mobile-nav.tsx`
- `src/components/vertical-nav.tsx`
- `src/components/empty-state.tsx`
- `src/app/notes/page.tsx`

Setup hardening:

- `README.md`
- `.env.example`
- `backend/.env.example`
- `scripts/setup.mjs`

Workflow evidence:

- `docs/workflows/p1-acceptance-cleanup-patch/README.md`
- `docs/workflows/p1-acceptance-cleanup-patch/tasks.md`
- `docs/workflows/p1-acceptance-cleanup-patch/validation.md`
- `docs/workflows/p1-acceptance-cleanup-patch/diff-report.md`

## Behavior Changes

Public pages:

- Removed the desktop public nav `管理` shortcut.
- Removed the mobile public nav `管理` shortcut.
- Removed the vertical public nav `管理` shortcut.
- Removed `EmptyState`'s default admin creation action.
- Kept `/notes` admin create actions visible only when `useAdminAuth()` reports an admin session.
- Changed anonymous `/notes` empty text from login/admin-oriented copy to public-reading copy.

Setup:

- `scripts/setup.mjs` warns on unsupported Python versions and selects `python3.12` / `python3.13` when available.
- README now recommends Python 3.12 / 3.13 and warns against Python 3.14 for the current backend dependency set.
- README and `.env.example` now distinguish local-dev localhost API URLs from production-build non-localhost API URLs.
- `backend/.env.example` now explicitly states that `ALLOWED_ORIGINS` is comma-separated and not a JSON array.

## Explicit Non-Changes

- No backend permission model change.
- No migration.
- No database table.
- No AI Gateway, Prompt Registry, `ai_runs`, or `ai_call_logs` main-logic change.
- No use of `AUTH_BYPASS` in validation.
- No P2 backlog item was converted into a blocker.

## Remaining Deferred Items

The following remain deferred P2/P3 items:

- `/api/folders` public boundary review.
- AI Gateway async mock warning cleanup.
- lint policy.
- broader long-running browser regression.
- production CORS architecture cleanup beyond documentation.
- httpOnly cookie/session architecture cleanup.
