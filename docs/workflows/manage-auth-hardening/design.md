# Design

## Scope Boundary

This task affects the `manage` and `auth` domains plus deployment/auth boundary documentation. It should not refactor unrelated content-management behavior.

## Current Evidence Summary

### Frontend

- `/manage` is a client-side page that calls `getMe()` on mount and conditionally renders either:
  - a login form, or
  - the management console.
- The current `LoginForm` renders username/password fields only.
- Frontend auth APIs already include:
  - password login,
  - passkey auth-options fetch,
  - passkey login submit.

### Backend

- `_resolve_session_user()` contains an `AUTH_BYPASS` branch that:
  - loads the first user,
  - creates `admin` if missing,
  - promotes the first user to admin if needed,
  - returns a successful session resolution without a real authenticated session.
- Passkey login and passkey-only action guards already exist.

### Production/Deployment

- `blog.limengyang.me/manage` is a public page route.
- `api.limengyang.me` is Cloudflare-Access-protected.
- prior workflow evidence points production public bundles toward `public-api.limengyang.me`, but the currently observed auth/runtime path still needs explicit validation within this task.

## Proposed Workstreams

### 1. Auth Contract Hardening

- Review every `AUTH_BYPASS` branch in auth resolution and optional-admin helpers.
- Define which code paths are valid for:
  - local/private trusted development,
  - authenticated production management,
  - public anonymous browsing.
- Remove or narrow any path that can auto-promote or auto-authenticate admins outside the intended mode.

### 2. `/manage` Gate Clarification

- Keep or revise the current “single route acting as login gate” pattern.
- Ensure the unauthenticated state is obvious and consistent:
  - management title,
  - why login is required,
  - available login methods,
  - passkey availability or absence messaging.

### 3. Passkey Entry Completion

- Wire existing passkey login API support into the management login UI.
- Preserve password login as a fallback where intended.
- Represent passkey availability and failure states cleanly.

### 4. Validation Strategy

- Static validation:
  - `npx tsc --noEmit`
  - backend import/compile check
- Runtime validation:
  - anonymous `/manage`
  - password login
  - passkey login entry visibility
  - passkey-only action rejection under password session
  - production-host observations documented with exact URLs and outcomes

## Risks

- Tightening `AUTH_BYPASS` may break existing local operator flows if the dev/private mode contract is not made explicit first.
- Adding passkey UI without clear “not registered” handling can create a worse operator experience than the current password-only form.
- Route-level redirect changes may conflict with current navigation assumptions and prior workflow links into `/manage?tab=settings`.

## Recommended Direction

Prefer this shape unless the user wants a different product contract:

1. `/manage` remains the public login-gate route.
2. Unauthenticated users can reach `/manage`, but only see the login gate.
3. Real management content requires a valid session from the backend.
4. Passkey login is shown alongside password login in the UI.
5. `AUTH_BYPASS` is explicitly restricted to local/private development and cannot silently grant admin access in production.
