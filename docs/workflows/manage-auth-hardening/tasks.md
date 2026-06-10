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
