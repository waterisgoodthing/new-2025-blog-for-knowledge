# Requirements

## Problem Statement

The production management entry currently creates confusion in two areas:

1. Clicking `管理` reaches `/manage` without a route-level intercept, which can look like a broken login barrier.
2. The management login UI exposes password login only, even though passkey login support exists in the backend and frontend API layer.

The task must clarify and then enforce the intended administrator contract.

## Functional Requirements

REQ-01: The system must define an explicit deployment/auth mode model for management access.

- Private/local trusted mode and public/production strict mode must be distinguishable in code and documentation.
- `AUTH_BYPASS` must not silently behave like a production-safe auth path.

REQ-02: `/manage` access behavior must be intentionally defined.

- If `/manage` remains a public route, the page must clearly behave as a login gate when unauthenticated.
- If additional route-level interception is introduced, it must not conflict with the current App Router structure or break deep links such as `/manage?tab=settings`.

REQ-03: Anonymous visitors must never gain management capabilities through session auto-resolution or implicit admin promotion.

REQ-04: Password login and passkey login must both be represented consistently across:

- backend endpoints,
- frontend API clients,
- management login UI,
- auth-level state reporting.

REQ-05: Sensitive management actions must keep server-side passkey enforcement.

- Existing passkey-only actions must remain protected even if UI gating changes.

REQ-06: The task must define the intended user-facing language for:

- unauthenticated state,
- password-admin state,
- passkey-admin state,
- passkey unavailable / not registered state.

REQ-07: Production API-host expectations must be documented alongside auth expectations.

- Public pages and management pages must not accidentally rely on Cloudflare-Access-protected private hosts unless that is an explicit intended deployment mode.

REQ-08: Validation must cover both source evidence and runtime behavior.

- Anonymous `/manage` behavior.
- Authenticated password-admin behavior.
- Passkey login entry visibility and behavior.
- Passkey-only action protection.
- Production-mode vs bypass-mode behavior where feasible.

## Non-Goals

- Do not redesign unrelated notes/blog/music management UX.
- Do not replace the current session-cookie auth architecture with a new auth stack.
- Do not change Cloudflare Access policy directly from repository code.

## Open Product Decisions

DEC-01: Should `/manage` remain directly reachable as a public login-gate page, or should unauthenticated users be redirected to a separate dedicated login route?

DEC-02: In production, should `AUTH_BYPASS` be:

- fully disabled,
- allowed only for localhost/private dev origins,
- or kept behind a stronger explicit environment contract?

DEC-03: How should the UI present passkey login when no passkey has been registered yet?

- show the button and return a meaningful backend error,
- hide the button when passkey is unavailable,
- or show both the button and explanatory helper text?
