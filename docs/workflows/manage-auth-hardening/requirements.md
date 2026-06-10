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

REQ-09: Public-deployment passkey registration and use must work from this machine.

- The live/public RP configuration must match the public hostname and origin used by the browser on this machine.
- The operator must be able to register a passkey credential from this machine against the production/public RP settings.
- After registration, the operator must be able to authenticate with that passkey from this machine.

REQ-10: Sensitive production administrator actions must be protected by passkey-level auth after registration.

- Password-admin sessions may still exist as fallback login where intended.
- Passkey-only actions must reject password-only sessions server-side and be visibly gated in the UI.

REQ-11: The temporary execution round must verify exact public URLs and exact machine-facing outcomes.

- Validation must record the public hostname used.
- Validation must record whether registration options, browser prompt, device prompt, verification, session creation, and passkey-only action checks succeeded or failed.

REQ-12: Operator-only passkey registration must be possible against the public RP.

- A tool must exist that allows the operator to register a passkey credential bound to `blog.limengyang.me` (RP ID) and `https://blog.limengyang.me` (origin).
- The tool must not expose passkey registration to anonymous public users.
- The tool must be protected by a separate operator key, not by session auth.
- The tool must replace any existing credential atomically (single transaction).
- The tool must work from a real browser on the public origin, not from a localhost simulation.

REQ-13: The operator registration key must fail closed.

- If `OPERATOR_REGISTRATION_KEY` is empty or unset, operator registration endpoints must reject all requests with 403.
- The key must be transmitted via HTTP header, not URL query parameter.

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

DEC-04: For this temporary execution round, should the task include live machine registration on the public production RP if the code path already exists?

- Current user direction: yes.
