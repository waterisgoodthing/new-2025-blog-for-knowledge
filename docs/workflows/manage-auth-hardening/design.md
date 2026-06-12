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

## Temporary Public-Passkey Execution Round

This follow-up round is narrower than the original hardening work:

1. confirm the current public RP/origin configuration used by the live/public backend,
2. verify the public `/manage` login gate from this machine,
3. register/add a passkey credential from this machine against the public RP,
4. verify passkey login from this machine,
5. verify a passkey-only action still rejects a password-only session and succeeds under a passkey session if the UI path is available.

This round should prefer the already-established architecture:

- session-cookie auth remains in place,
- passkey registration/login uses the existing backend/WebAuthn services,
- no new auth stack should be introduced,
- only code or config changes strictly needed to make the public-machine passkey flow succeed should be made.

### Public-Execution Risks

- The live backend may still carry stale RP/origin values or stale passkey credentials registered under a different RP.
- Browser/WebAuthn registration can fail because of hostname/origin mismatch even if the UI code is correct.
- Existing single-credential assumptions may require reset/replace handling before this machine can add a new credential.

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

## Phase 7: Operator-Only Passkey Registration Tool

### Problem

After the RP ID migration from `localhost` to `blog.limengyang.me`, the existing passkey credential became stale. No public-domain registration path exists:

- The CLI `register-passkey` command serves a localhost origin page — credentials it produces are bound to `localhost`, not `blog.limengyang.me`.
- The public backend exposes `reg-options` (read) but has no `register` (verify/store) endpoint.
- The `/manage` UI has passkey login but no passkey registration UI.
- No admin password exists, so "login then re-register from security tab" is not available.

### Chosen Approach: Operator-Key-Protected HTTP Registration Endpoints

**Why not CLI-only?** The browser's `navigator.credentials.create()` must execute in the context of `https://blog.limengyang.me` so that `clientDataJSON.origin` matches the backend's expected origin. A localhost CLI page cannot produce this.

**Why not public anonymous endpoints?** Passkey registration is a sensitive operation that replaces the sole admin credential. Exposing it anonymously would be a backdoor.

**Solution**: Three new backend endpoints protected by `X-Operator-Registration-Key` header, plus a key-gated static HTML page served from the public frontend origin.

### Architecture

```
Operator browser on https://blog.limengyang.me/operator-passkey-register.html
  |
  |-- [P2] Page hidden behind key gate: no valid key → page shows rejection message
  |
  |-- POST /api/auth/passkey/operator/validate-key  (with X-Operator-Registration-Key)
  |     validates key before showing registration form
  |
  |-- POST /api/auth/passkey/operator/reg-options    (with X-Operator-Registration-Key)
  |     returns { options, session_id } — challenge stored under operator:<session_id>
  |
  |-- navigator.credentials.create({ publicKey })    (browser authenticator prompt)
  |
  |-- POST /api/auth/passkey/operator/register       (with X-Operator-Registration-Key + session_id)
  |     verifies attestation against session-keyed challenge, replaces old credential
```

### Security Model

- `OPERATOR_REGISTRATION_KEY` env var: if empty, all operator endpoints return 403 (fail-closed).
- Key transmitted via `X-Operator-Registration-Key` HTTP header.
- **P2 fix**: HTML page is gated — it validates the key server-side via `validate-key` before rendering the registration form. Without a valid key, the page shows a rejection message.
- No session/cookie auth required — operator key is the sole gate.
- Old credential is deleted and new credential is written in a single DB transaction (atomic replace).
- Audit log records `operator_passkey_register` action with device name.

### Challenge Isolation (P1 Fix)

The global `_reg_challenge_store["current"]` used by the public `GET /reg-options` endpoint is a single-slot dict — any concurrent reg-options request overwrites the previous challenge. This is acceptable for the login-gate flow but unacceptable for the operator recovery path.

**Fix**: Operator challenges use a separate `_operator_reg_challenge_store` dict, keyed by a random `session_id` (hex, 32 chars). The flow:

1. `POST /operator/reg-options` generates a `session_id`, stores the challenge under `_operator_reg_challenge_store[session_id]`, returns both `options` and `session_id`.
2. `POST /operator/register` receives the `session_id`, pops the challenge from the store, and verifies.
3. The public `GET /reg-options` continues to use `_reg_challenge_store["current"]` — completely isolated.

This means:
- A concurrent public `GET /reg-options` cannot invalidate an operator challenge.
- Two concurrent operator flows each get their own `session_id`-scoped challenge.
- The `session_id` is single-use (popped on verify, not deleted on failure for security — failed attempts don't leak the challenge).

### Credential Replacement Strategy

`replace_credential()` in `passkey_service.py`:
1. Query all existing `PasskeyCredential` rows.
2. Delete each in the same session.
3. Insert new credential.
4. Flush and refresh.
5. If any step fails, the transaction rolls back — no partial state.

### Files Changed

| File | Change |
|------|--------|
| `backend/app/config.py` | Added `OPERATOR_REGISTRATION_KEY: str = ""` |
| `backend/.env.example` | Added `OPERATOR_REGISTRATION_KEY` documentation |
| `backend/app/schemas/auth.py` | Added `OperatorRegOptionsRequest`, `OperatorRegisterRequest` (with `session_id`), `OperatorRegisterResponse` |
| `backend/app/services/passkey_service.py` | Added `replace_credential()`, `generate_operator_registration_options()`, `verify_operator_registration()`, `_operator_reg_challenge_store` |
| `backend/app/routers/auth.py` | Added `_require_operator_key()`, `POST .../operator/validate-key`, `POST .../operator/reg-options`, `POST .../operator/register` |
| `public/operator-passkey-register.html` | Key-gated static operator registration page with session-keyed challenge flow |
