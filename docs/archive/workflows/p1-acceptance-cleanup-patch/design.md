# Design — P1 Acceptance Cleanup Patch

## Approach

Keep this patch small and acceptance-focused. The patch should clean public/admin affordances and setup clarity without changing core data flow or security boundaries.

## Public Admin Affordance Cleanup

Current evidence:

- `src/components/nav-card.tsx` renders a desktop `管理` link to `/manage/dashboard`.
- `src/components/mobile-nav.tsx` includes a `管理` item in the mobile more menu.
- `src/components/empty-state.tsx` defaults `no-content` to `新建笔记` -> `/manage/dashboard`.
- `src/app/notes/page.tsx` returns create actions to `/manage/capture` or `/manage/dashboard`.

Planned design:

- Remove the public desktop `管理` link from the general public navigation card, or make it non-public by auth-aware rendering only if the existing auth pattern is simple and local.
- Remove `管理` from the mobile public more menu.
- Change the shared `EmptyState` `no-content` default so it does not point anonymous public surfaces to `/manage/dashboard`.
- Make `/notes` empty-state admin actions auth-aware or suppress them for public anonymous rendering.

Preferred implementation is conservative:

- Avoid introducing a new global auth state system.
- Prefer suppressing public admin actions over broad auth plumbing.
- Keep direct `/manage` access as the explicit login page.
- Keep backend permissions unchanged.

## Fresh Setup Hardening

Current evidence:

- `README.md` recommends `python3 -m venv .venv`, while this machine's default `python3` is `Python 3.14.5`, which fails `pydantic-core` build.
- `scripts/setup.mjs` accepts any Python 3 command.
- `src/lib/api/config.ts` rejects localhost `NEXT_PUBLIC_API_URL` in production.
- `backend/app/config.py` and `backend/main.py` parse `ALLOWED_ORIGINS` as a comma-separated string.

Planned design:

- Update README setup instructions to prefer Python 3.12 explicitly for this dependency set.
- Update setup script Python check to warn or fail on unsupported Python versions, with clear remediation.
- Clarify that localhost `NEXT_PUBLIC_API_URL` is for dev only and production build needs a non-localhost API URL.
- Clarify comma-separated `ALLOWED_ORIGINS`.

## Risk Controls

- No database or migration work.
- No AI Gateway changes.
- No hidden backend permission change.
- No use of `AUTH_BYPASS` in validation.
- If a P0/P1 blocker beyond the approved scope appears, record it and stop for approval.
