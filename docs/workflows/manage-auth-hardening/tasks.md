# Tasks

All tasks completed on 2026-06-09. Review fixes applied same day.

## Phase 0: Scope And Contract Closure

- [x] **P0-01** Confirm the target management access contract.
  - Contract: `/manage` remains public login-gate route; `AUTH_BYPASS` requires explicit double opt-in.

- [x] **P0-02** Capture the current-source and current-production evidence baseline.
  - Recorded in `validation.md`.

## Phase 1: Backend Auth Hardening

- [x] **P1-01** Refactor session-resolution logic so bypass behavior cannot silently auto-authenticate production admin access.
  - Added `_is_auth_bypass_active()` helper. Fail-closed: requires both `AUTH_BYPASS=true` AND `AUTH_BYPASS_ALLOW=true`.
  - Removed auto-create and auto-promote behavior from `_resolve_session_user()`.
  - Bypass only loads existing admin user when both flags are explicitly set.

- [x] **P1-02** Review all admin/optional-admin auth helpers for consistency with the new mode contract.
  - Fixed `get_current_admin` bug (default was `"true"`, now properly delegates to `_resolve_session_user`).
  - Removed redundant bypass branches from `get_optional_user` and `get_optional_admin`.
  - All helpers now consistently delegate to `_resolve_session_user()`.

## Phase 2: Manage Login UX Completion

- [x] **P2-01** Add passkey login entry to the `/manage` login gate.
  - `LoginForm` preflight-checks `GET /api/auth/passkey/status` on mount.
  - Passkey button shown only when browser supports WebAuthn AND server has registered passkey.
  - "Supported but not registered" helper message when passkey not registered.
  - `loginWithPasskey()` maps raw backend errors to friendly Chinese messages.

- [x] **P2-02** Add clear unauthenticated and passkey-state messaging.
  - Login gate title + subtitle explaining auth requirement.
  - Passkey button with description of its elevated privileges.
  - Divider separating passkey and password login methods.
  - Fallback message when browser doesn't support passkey.
  - Loading state while preflight check runs.

## Phase 3: Sensitive Access Verification

- [x] **P3-01** Re-verify server-side passkey-only protection after UI/auth changes.
  - `get_passkey_admin` guard unchanged, correctly requires `auth_level == "passkey"`.
  - `/api/auth/set-password` still uses `get_passkey_admin` dependency.
  - Security tab still gated by `passkeyOnly: true`.

- [x] **P3-02** Re-verify `/manage?tab=settings` and other deep links under the approved gate behavior.
  - URL tab param read correctly from `searchParams`.
  - Tab state preserved across login flow.
  - Passkey-only tabs disabled in UI for non-passkey sessions.

## Phase 4: Validation And Handoff

- [x] **P4-01** Run frontend validation.
  - `npx tsc --noEmit` passes with zero errors.

- [x] **P4-02** Run backend validation.
  - `python -c "from app.routers.auth import ..."` passes.
  - Syntax check passes.

- [x] **P4-03** Record final runtime evidence and residual risks.
  - Recorded in `validation.md`.

## Phase 5: Deployment Drift Investigation (2026-06-10)

- [x] **P5-01** Investigate why production bundle lacks passkey preflight login gate.
  - Root cause: manual deploy (`npm run deploy`) was run from a state after `73efa4e` but before `4e4b69d`. No CI/CD exists.
  - Evidence: all 17 live JS chunks searched; zero contain `checkPasskeyRegistered`, `passkey/status`, or preflight error strings.

- [x] **P5-02** Investigate why `public-api.limengyang.me` returns HTTP 530.
  - Root cause: Cloudflare Tunnel daemon is down. Error 1033 = "Argo Tunnel error".
  - `api.limengyang.me` (private) correctly returns 302 to Cloudflare Access.

- [x] **P5-03** Document minimum fix path.
  - 1. Deploy feature branch to Cloudflare Workers.
  - 2. Restart `cloudflared` tunnel daemon for `public-api.limengyang.me`.
  - 3. Verify WebAuthn RP settings in production backend `.env`.
  - 4. Smoke test the live login UI.

## Phase 6: Production Execution And Closure (2026-06-10 Round 2)

- [x] **P6-01** Restore `public-api.limengyang.me`.
  - Added `public-api.limengyang.me` → `http://localhost:8000` ingress rule to `~/.cloudflared/config.yml`.
  - Tunnel reconnected to Cloudflare edge at `lax08`.
  - Restarted stale backend (uvicorn) to pick up `GET /api/auth/passkey/status` endpoint.
  - Verified: `/api/auth/me` → 401, `/api/auth/passkey/status` → `{"registered":true}`.

- [x] **P6-02** Deploy frontend with passkey preflight login gate.
  - `npx tsc --noEmit` → PASS.
  - `npm run build:cf` → PASS.
  - `npx wrangler deploy --route 'blog.limengyang.me/*'` → PASS. Version `4149ddd3`.
  - Verified: all 5 required strings present in live bundle chunks.

- [x] **P6-03** Set production WebAuthn RP config.
  - Added `WEBAUTHN_RP_ID=blog.limengyang.me` and `WEBAUTHN_ORIGIN=https://blog.limengyang.me` to `backend/.env`.
  - Restarted backend. Verified: reg-options returns `rp.id=blog.limengyang.me`.

- [x] **P6-04** Final smoke test.
  - All 7 acceptance checks passed (API + bundle evidence).
  - Deployment-level acceptance: PASS.

- [x] **P6-05** Update validation.md and README.md with execution results.

## Phase 7: Temporary Public Passkey Execution Round (Approval Required)

Implementation for this phase must not start until explicitly approved in conversation.

- [x] **P7-01** Reconfirm the live public RP/origin and passkey preflight state from this machine.
  - Completion standard: record the exact public URL, RP ID, origin, passkey status response, and current `/manage` gate behavior in `validation.md`.
  - Completed: 2026-06-10. Source and live preflight evidence confirm this machine is targeting the public RP/origin pair and that the public passkey status endpoint is reachable.
  - Evidence:
    - Local backend env currently sets `WEBAUTHN_RP_ID=blog.limengyang.me` and `WEBAUTHN_ORIGIN=https://blog.limengyang.me`.
    - `https://public-api.limengyang.me/api/auth/passkey/status` returned `{"registered":true}` from this machine.
    - `https://public-api.limengyang.me/api/auth/me` remains unauthenticated without a session.
    - `https://blog.limengyang.me/manage` is publicly reachable from this machine and returns the management app shell.

- [x] **P7-02** Implement operator-only passkey registration tool.
  - Added `OPERATOR_REGISTRATION_KEY` to config (fail-closed when empty).
  - Added operator registration schemas (`OperatorRegOptionsRequest`, `OperatorRegisterRequest`, `OperatorRegisterResponse`).
  - Added `replace_credential()` to `passkey_service.py` for atomic credential replacement.
  - Added `POST /api/auth/passkey/operator/reg-options` and `POST /api/auth/passkey/operator/register` endpoints, protected by `X-Operator-Registration-Key` header.
  - Created `public/operator-passkey-register.html` — static page served from `blog.limengyang.me` origin that drives the browser WebAuthn flow against the backend operator endpoints.
  - Backend import check: PASS.
  - Frontend `npx tsc --noEmit`: PASS.
  - Operator routes registered: `/api/auth/passkey/operator/reg-options`, `/api/auth/passkey/operator/register`.

- [ ] **P7-03** Set `OPERATOR_REGISTRATION_KEY` in production backend `.env` and restart backend.
  - Completion standard: operator endpoints return 403 when key is missing/wrong, and return valid registration options when key is correct.

- [ ] **P7-04** Register a passkey credential from this machine against the public deployment.
  - Completion standard: visit `https://blog.limengyang.me/operator-passkey-register.html` from this machine, complete the WebAuthn registration flow, and the backend persists the new credential (replacing the old one).
  - Requires: P7-03 completed (operator key configured).

- [ ] **P7-05** Verify passkey login from this machine on the public deployment.
  - Completion standard: public `/manage` can establish a passkey-authenticated admin session from this machine using the newly registered credential.
  - Requires: P7-04 completed.

- [ ] **P7-06** Verify passkey-only protection after live registration.
  - Completion standard: a passkey session satisfies passkey-only action gates.
  - Requires: P7-05 completed.

- [ ] **P7-07** Record final public-machine execution evidence and residual risks.
  - Completion standard: `validation.md` captures exact URLs, outcomes, blockers, and any remaining manual follow-up.
