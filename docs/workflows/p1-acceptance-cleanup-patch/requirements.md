# Requirements — P1 Acceptance Cleanup Patch

## Scope

This workflow addresses only SFA P1 items:

1. Anonymous public pages expose management entry points or create actions.
2. Fresh setup can be blocked by unsupported Python versions or unclear production-build API URL / CORS requirements.

## Functional Requirements

### P1-01 Public Admin Affordance Cleanup

- Anonymous public navigation should not show a general `管理` entry as a public content action.
- Public empty states should not default to admin creation links.
- `/notes` public empty-state create action should not show admin workspace/capture links to anonymous users.
- Existing protected management routes must stay protected.
- Logged-in/admin workflows must remain reachable through intended management entry points.
- Backend permissions must not be weakened or removed.

### P1-02 Fresh Setup Hardening

- Setup checks should identify unsupported Python versions before dependency installation fails.
- README should clearly state the supported Python range for this dependency set.
- README should state that local dev may use localhost API URLs, but production `npm run build` requires a non-localhost `NEXT_PUBLIC_API_URL`.
- README or env comments should state that `ALLOWED_ORIGINS` is comma-separated, not a JSON array.
- Setup docs must not suggest `AUTH_BYPASS` for acceptance or production.

## Non-Requirements

- No new authentication system.
- No backend authorization rewrite.
- No new migration or database table.
- No redesign of the public navigation.
- No new Prompt admin, A/B, provider probe, auto-circuit-breaker, or recommendation change.
- No implementation of P2 backlog items such as `/api/folders` boundary review or lint policy.

## Validation Requirements

Run after implementation approval:

```bash
npx tsc --noEmit
npm run build
git diff --check
```

If setup script changes:

```bash
npm run check
```

Browser validation should cover:

- `/`
- `/blog`
- `/notes`
- `/manage`

Acceptance checks:

- Anonymous `/`, `/blog`, and `/notes` do not visibly expose `管理` or admin creation actions.
- Anonymous `/manage` remains the login entry and does not render management data.
- Management routes remain reachable after login through direct URL.
- Setup output/docs clearly communicate Python and production API URL constraints.
