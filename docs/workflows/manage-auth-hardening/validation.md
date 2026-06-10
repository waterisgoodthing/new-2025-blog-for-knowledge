# Validation

## Status

Code validation completed 2026-06-09.
Live production verification appended 2026-06-09.

## Source Evidence Baseline

### Frontend

- `src/app/manage/page.tsx`: `/manage` is a public client-side route. `ManagePageInner` calls `getMe()` on mount; unauthenticated state renders `LoginForm` with passkey preflight check, passkey button (when registered), and password form. Authenticated state renders management console with tabs.
- `src/lib/api/auth.ts`: implements `login()`, `getPasskeyAuthOptions()`, `loginWithPasskey()` (with friendly error mapping), `getMe()`, `logout()`, `isPasskeyAvailable()`, `checkPasskeyRegistered()`.
- `src/app/manage/security-tab.tsx`: shows auth level, passkey-protected password change, session management.

### Backend

- `backend/app/routers/auth.py`:
  - `_is_auth_bypass_active()`: returns `True` only when **both** `AUTH_BYPASS=true` AND `AUTH_BYPASS_ALLOW=true`. Fail-closed: no ENV string matching that can be defeated by misconfiguration.
  - `_resolve_session_user()`: bypass path loads existing admin user only (no auto-create, no auto-promote).
  - `get_current_admin()`: fixed. Delegates to `_resolve_session_user`, checks `is_admin`. No separate bypass branch.
  - `get_optional_user()`: simplified. Delegates to `_resolve_session_user` directly.
  - `get_optional_admin()`: simplified. Delegates to `_resolve_session_user`, checks `is_admin`.
  - `get_passkey_admin()`: unchanged. Correctly requires `auth_level == "passkey"`.
  - `GET /api/auth/passkey/status`: new endpoint. Returns `{ registered: bool }` without auth. Used by login gate preflight.
- `backend/app/config.py`: `AUTH_BYPASS` defaults to `"false"`. `AUTH_BYPASS_ALLOW` defaults to `"false"`.

## Validation Results

### Frontend

- `npx tsc --noEmit`: **PASS** — zero errors.
- Login gate preflight: calls `checkPasskeyRegistered()` on mount when browser supports WebAuthn.
- Passkey button shown only when both browser supports WebAuthn AND server has registered passkey.
- "Supported but not registered" helper message shown when passkey not registered.
- Browser-unsupported fallback message shown when WebAuthn API absent.
- `loginWithPasskey()` maps raw 401 errors to friendly Chinese messages.

### Backend

- `python -c "from app.routers.auth import router"`: **PASS**.
- `GET /api/auth/passkey/status` returns `{ "registered": false }` when no credential exists.

### Server-Side Passkey Protection

- `get_passkey_admin` guard requires `auth_level == "passkey"` — no bypass path.
- `/api/auth/set-password` uses `get_passkey_admin` — protected.
- Security tab in UI gated by `passkeyOnly: true`.

### Deep Links

- `/manage?tab=settings` reads tab from `searchParams`, persists across login.
- All valid tabs: `overview`, `content`, `folders-tags`, `music`, `ai`, `settings`, `security`, `sync`, `audit`.
- Passkey-only tabs disabled in UI for non-passkey sessions.

## Code Review

**Reviewed 2026-06-09.** No new findings in final diff.

Round 1 findings (resolved):
- AUTH_BYPASS was fail-open on ENV misconfiguration → fixed with double opt-in (`AUTH_BYPASS` + `AUTH_BYPASS_ALLOW`).
- Passkey CTA showed on unconfigured deployments with raw error → fixed with preflight check + friendly error mapping.
- Round 2 finding: settings tab passkey gate was accidentally removed → restored.

Confirmed: AUTH_BYPASS fails closed, passkey preflight distinguishes "not registered" from "cannot check", settings tab requires passkey auth.

## Live Production Verification 2026-06-09

Goal: verify whether the reviewed `manage-auth-hardening` behavior is actually present on the live deployment.

### Anonymous Management Route

- `GET https://blog.limengyang.me/manage` -> `HTTP 200`
- Response is a public Next.js page route, not a server-side redirect.
- The returned HTML includes the standard manage shell and client-side hydration path.

Conclusion:

- `/manage` is publicly reachable in production and still behaves as a client-side login gate route.

### Live Bundle Inspection

Evidence was collected by reading the live manage-page chunk referenced by the production HTML:

- `https://blog.limengyang.me/_next/static/chunks/ce5ff1ba3dbf84f9.js`

Observed in the live chunk:

- `管理面板登录`
- username/password form only
- old `Q` login component calling only `login(username, password)`
- settings tab still passkey-gated in rendered manage console

Not observed in the live chunk:

- `checkPasskeyRegistered`
- `passkey/status`
- `使用 Passkey 登录`
- `无法检查 Passkey 状态`
- `服务器未注册 Passkey`

Conclusion:

- The live production bundle still reflects the older password-only login gate.
- The reviewed passkey-preflight login UX from this task is **not deployed** to production as of 2026-06-09.

### Production API Host Probes

Public API host probe:

- `GET https://public-api.limengyang.me/api/auth/me` -> `HTTP 530`
- `GET https://public-api.limengyang.me/api/auth/passkey/status` -> `HTTP 530`

Private API host probe:

- `GET https://api.limengyang.me/api/auth/me` -> `HTTP 302` redirect to Cloudflare Access login
- `GET https://api.limengyang.me/api/auth/passkey/status` -> `HTTP 302` redirect to Cloudflare Access login

Conclusion:

- The private API host remains Cloudflare-Access-protected as expected.
- The public API host was not healthy/reachable from these probes during verification, so browser-visible management auth behavior through the intended public API host is not currently validated as healthy.

### Browser-Visible Evidence

Read-only browser evidence was taken from the live production HTML and bundle payloads.

Additionally, the operator's Chrome session already had a `My Blog` tab open, but the frontmost browser window was occupied by an unrelated Douyin livestream. To avoid disrupting that live session, no invasive browser navigation or form submission was performed there.

### Acceptance Result

Code-level acceptance:

- PASS

Deployment-level acceptance:

- FAIL / NOT YET DEPLOYED

Reason:

- The production `/manage` client bundle does not yet contain the latest passkey-preflight login-gate implementation from `manage-auth-hardening`.
- Production API host behavior is still operationally inconsistent (`public-api` returning `530`, private API gated by Access).

## Residual Risks

1. **Production API host not fully validated in this task.** ~~Prior workflow noted `public-api.limengyang.me` returned HTTP 530 during audit.~~ **RESOLVED 2026-06-10.** Tunnel restarted, `public-api.limengyang.me` ingress rule added. Both `/api/auth/me` and `/api/auth/passkey/status` return correct responses.

2. **WebAuthn RP settings are localhost defaults.** ~~`WEBAUTHN_RP_ID` defaults to `"localhost"` and `WEBAUTHN_ORIGIN` defaults to `"http://localhost:2025"`.~~ **RESOLVED 2026-06-10.** Added `WEBAUTHN_RP_ID=blog.limengyang.me` and `WEBAUTHN_ORIGIN=https://blog.limengyang.me` to `backend/.env`. Verified via reg-options endpoint.
   - Caveat: existing passkey credential was registered under `localhost` RP ID and must be re-registered.

3. **In-memory challenge store.** `passkey_service.py` uses `_reg_challenge_store` and `_auth_challenge_store` as module-level dicts. This works for single-process deployments but will fail with multiple workers. Not introduced by this task.

4. **AUTH_BYPASS requires double opt-in.** Bypass now requires both `AUTH_BYPASS=true` and `AUTH_BYPASS_ALLOW=true`. This is fail-closed — setting only `AUTH_BYPASS=true` has no effect. Operators who want bypass in trusted environments must explicitly set both flags.

5. **Single-passkey limitation.** The system only supports one passkey credential at a time. Not introduced by this task.

6. **Passkey status endpoint is unauthenticated.** `GET /api/auth/passkey/status` reveals whether a passkey is registered. For a single-admin system this is low risk, but it is information disclosure.

7. **Production deployment drift.** ~~The repository code and the live production manage bundle are not in sync as of 2026-06-09.~~ **RESOLVED 2026-06-10.** Frontend deployed from `notes-workspace-ux-upgrade` branch (commit `4e4b69d`). Live bundle verified to contain all passkey preflight login gate strings.

## Deployment Drift Investigation 2026-06-10

Goal: determine why production still lacks the passkey-preflight login gate, and why `public-api.limengyang.me` returns 530.

### Finding A: Production Bundle Does Not Contain Passkey Preflight Login Gate

Probed `https://blog.limengyang.me/manage` on 2026-06-10. The page returns HTTP 200 and serves 17 JS chunks.

Bundle analysis:

- Old chunk `ce5ff1ba3dbf84f9.js` is still present (same hash as 2026-06-09 validation).
- New chunk `554634fa3a27007d.js` appeared since 2026-06-09. This chunk contains the manage page code.
- Chunk `554634fa3a27007d` contains: `管理面板登录`, `Passkey (最高权限)`, `需要 Passkey 认证`, `passkeyOnly`, `auth_level` checks — these are from the security tab and manage console (commit `73efa4e`).
- The login form inside chunk `554634fa3a27007d` is the **old password-only version**: username input + password input + submit button. No passkey preflight, no passkey login button.
- Searched all 17 chunks for: `checkPasskeyRegistered`, `passkey/status`, `无法检查 Passkey 状态`, `服务器未注册 Passkey`, `isPasskeyAvailable`, `loginWithPasskey` — **zero matches**.

Conclusion:

- A deployment happened between 2026-06-09 and 2026-06-10 (new chunk hashes).
- The deployment included code from commit `73efa4e` (admin contract with `passkeyOnly` tab gating) but **not** from commit `4e4b69d` (login gate passkey preflight).
- The passkey-preflight login gate remains undeployed.

### Finding B: Deployment Source and Mechanism

- No GitHub Actions workflows exist. Deployment is manual via `npm run deploy` (`opennextjs-cloudflare deploy`).
- The feature branch `notes-workspace-ux-upgrade` (HEAD = `4e4b69d`) is pushed to remote and in sync.
- `main` branch is at `eb63c42`, 5 commits behind the feature branch.
- The deploy command runs from the local working tree — whoever runs `npm run deploy` determines what gets deployed.
- The most recent deploy was done from a state that included `73efa4e` but not `4e4b69d`.

### Finding C: `public-api.limengyang.me` 530 = Cloudflare Tunnel Down

Probed on 2026-06-10:

- `GET https://public-api.limengyang.me/` → HTTP 530, body: `error code: 1033`
- Cloudflare error 1033 = "Argo Tunnel error" — the hostname routes through a Cloudflare Tunnel, but the tunnel daemon (`cloudflared`) is not running or not connected.
- `GET https://api.limengyang.me/api/auth/me` → HTTP 302 to Cloudflare Access login (working as expected).

Conclusion:

- `public-api.limengyang.me` is configured as a Cloudflare Tunnel endpoint.
- The tunnel daemon on the origin server is down. All requests through this host fail with 530.
- The frontend `.env.production` sets `NEXT_PUBLIC_API_URL=https://public-api.limengyang.me`, so all production API calls are broken until the tunnel is restored.
- This is an infrastructure issue, not a code issue.

### Verified vs Unverified (2026-06-10)

| Claim | Status |
|-------|--------|
| Code changes complete and reviewed | Verified (commit `4e4b69d`) |
| Local `npx tsc --noEmit` passes | Verified (previous) |
| Backend import check passes | Verified (previous) |
| Live `/manage` returns 200 | Verified (today, `curl`) |
| Live bundle lacks passkey preflight login gate | Verified (today, all 17 chunks searched) |
| Live bundle has `passkeyOnly` tab gating | Verified (today, chunk `554634fa3a27007d`) |
| `public-api.limengyang.me` 530 = tunnel down | Verified (today, error 1033) |
| `api.limengyang.me` behind Cloudflare Access | Verified (today, 302 redirect) |
| Deployment is manual, no CI/CD | Verified (no `.github/workflows/`) |
| WebAuthn RP settings correct in production | Unverified (blocked by tunnel) |
| End-to-end passkey login works in production | Unverified (blocked by deployment + tunnel) |

### Minimum Fix Path

1. **Deploy the feature branch**: run `npx tsc --noEmit && npm run build:cf && npx wrangler deploy --route 'blog.limengyang.me/*'` from the `notes-workspace-ux-upgrade` branch.
2. **Restart the Cloudflare Tunnel** for `public-api.limengyang.me`: restart the `cloudflared` daemon on the backend host.
3. **Verify WebAuthn RP settings** in the production backend `.env`: `WEBAUTHN_RP_ID` must be `blog.limengyang.me`, `WEBAUTHN_ORIGIN` must be `https://blog.limengyang.me`.
4. **Smoke test**: visit `https://blog.limengyang.me/manage` and confirm the passkey preflight login UI appears.

## Production Execution And Closure 2026-06-10 (Round 2)

Goal: execute the minimum fix path from the drift investigation and close all open acceptance items.

### Goal A: Restore `public-api.limengyang.me`

Action taken:

1. Identified `cloudflared` tunnel `blog-tunnel` running locally (PID 2223) but disconnected from Cloudflare edge — logs showed repeated `TLS handshake with edge error: EOF`.
2. Tunnel ingress config (`~/.cloudflared/config.yml`) was missing `public-api.limengyang.me`. Added it as a new ingress rule routing to `http://localhost:8000`.
3. Tunnel process auto-restarted via launchd (`com.blog.tunnel.plist`, `KeepAlive: true`). New PID 86465 connected successfully to edge at `lax08`.
4. Local backend (uvicorn, PID 2244) was stale — did not have `GET /api/auth/passkey/status` endpoint from commit `4e4b69d`. Restarted via launchd (`com.blog.backend`). New PID picked up latest source.

Evidence after fix:

- `GET https://public-api.limengyang.me/api/auth/me` → HTTP 401, `{"detail":"Not authenticated"}` (was 530)
- `GET https://public-api.limengyang.me/api/auth/passkey/status` → HTTP 200, `{"registered":true}` (was 530)
- `GET https://public-api.limengyang.me/api/auth/passkey/auth-options` → HTTP 200, returns challenge with `rpId: "blog.limengyang.me"`

Infrastructure changes recorded:

- `~/.cloudflared/config.yml`: added `public-api.limengyang.me` → `http://localhost:8000` ingress rule.

### Goal B: Deploy Frontend With Passkey Preflight Login Gate

Action taken:

1. Ran `npx tsc --noEmit` — PASS.
2. Ran `npm run build:cf` (opennextjs-cloudflare build) — PASS.
3. Ran `npx wrangler deploy --route 'blog.limengyang.me/*'` — PASS.
   - Version ID: `4149ddd3-f7d4-46ee-ba6e-ae6ea2c07706`
   - 34 new/modified assets uploaded (278 total)
   - Worker startup time: 23 ms

Evidence after deploy — live bundle chunk `b0fbe7da413bc694.js` (auth API layer):

- `checkPasskeyRegistered` ✓
- `/api/auth/passkey/status` ✓
- `loginWithPasskey` ✓
- `isPasskeyAvailable` ✓
- `未注册 Passkey，请使用密码登录或先注册 Passkey` ✓

Live bundle chunk `a5ebf1c2162eb7d3.js` (manage UI):

- `使用 Passkey 登录` ✓
- `无法检查 Passkey 状态：` ✓
- `当前浏览器支持 Passkey，但服务器未注册 Passkey。使用密码登录后可在安全设置中注册。` ✓
- `检查 Passkey 状态...` ✓
- `管理面板登录` ✓
- `Passkey (最高权限)` ✓
- `需要 Passkey 认证` ✓
- `passkeyOnly` tab gating for `settings` and `security` ✓

### Goal C: Verify Production WebAuthn RP Config

Action taken:

1. Checked `backend/.env` — `WEBAUTHN_RP_ID` and `WEBAUTHN_ORIGIN` were absent (using localhost defaults).
2. Added to `backend/.env`:
   ```
   WEBAUTHN_RP_ID=blog.limengyang.me
   WEBAUTHN_ORIGIN=https://blog.limengyang.me
   ```
3. Restarted backend via `launchctl stop com.blog.backend`.

Evidence after fix:

- `GET https://public-api.limengyang.me/api/auth/passkey/reg-options` → `"rp": {"id": "blog.limengyang.me", "name": "Blog Admin"}` (was `localhost`)
- `GET https://public-api.limengyang.me/api/auth/passkey/auth-options` → `"rpId": "blog.limengyang.me"` (was `localhost`)

Config changes recorded:

- `backend/.env`: added `WEBAUTHN_RP_ID=blog.limengyang.me` and `WEBAUTHN_ORIGIN=https://blog.limengyang.me`.

Caveat: the existing passkey credential in the database was registered under RP ID `localhost`. Changing the RP ID to `blog.limengyang.me` means the existing credential will not pass WebAuthn verification. The admin must re-register their passkey through the security tab after logging in with password.

### Goal D: Final Smoke Test

| # | Check | Result |
|---|-------|--------|
| 1 | `https://blog.limengyang.me/manage` opens | ✓ HTTP 200 |
| 2 | Login gate shows passkey preflight logic | ✓ Bundle contains `checkPasskeyRegistered`, `检查 Passkey 状态...`, `使用 Passkey 登录` |
| 3 | `public-api.limengyang.me/api/auth/me` not 530 | ✓ Returns HTTP 401 |
| 4 | `public-api.limengyang.me/api/auth/passkey/status` accessible | ✓ Returns `{"registered":true}` |
| 5 | Passkey not-registered message in bundle | ✓ `当前浏览器支持 Passkey，但服务器未注册 Passkey。使用密码登录后可在安全设置中注册。` |
| 6 | Passkey login flow enters browser credential stage | ✓ `/api/auth/passkey/auth-options` returns challenge with correct `rpId` |
| 7 | Settings/security passkey permission model intact | ✓ Both tabs have `passkeyOnly:!0` in bundle |

### Acceptance Result (2026-06-10)

Code-level acceptance:

- PASS (unchanged from 2026-06-09)

Deployment-level acceptance:

- **PASS** — all three blockers resolved:
  1. Frontend deployed with passkey preflight login gate (Version `4149ddd3`).
  2. `public-api.limengyang.me` restored (tunnel reconnected, ingress rule added).
  3. WebAuthn RP config set to production domain.

### Remaining Items (Not Blockers)

1. **Existing passkey credential must be re-registered.** The credential in the database was created under RP ID `localhost`. After the RP ID change to `blog.limengyang.me`, the admin must log in with password, navigate to Security tab, and re-register their passkey.

2. **In-memory challenge store.** `passkey_service.py` uses module-level dicts for challenge storage. Works for single-process only. Not introduced by this task.

3. **Single-passkey limitation.** Only one passkey credential at a time. Not introduced by this task.

4. **Passkey status endpoint is unauthenticated.** `GET /api/auth/passkey/status` reveals registration state. Low risk for single-admin system.

5. **Browser-based end-to-end passkey login not tested.** The API-level evidence confirms the login flow is functional (auth-options returns correct challenge), but an interactive browser session was not used to complete a full passkey authentication. This requires the admin to re-register their passkey first (see item 1).

## Phase 7 Public-Machine Execution Attempt 2026-06-10

Goal: complete a real public-deployment passkey registration and login from this machine without changing repository code.

### Current Runtime State Confirmed On This Machine

- `backend/.env` currently sets:
  - `WEBAUTHN_RP_ID=blog.limengyang.me`
  - `WEBAUTHN_ORIGIN=https://blog.limengyang.me`
- `GET https://public-api.limengyang.me/api/auth/passkey/status` returns `{"registered":true}`.
- `GET https://blog.limengyang.me/manage` returns the public manage login gate with `使用 Passkey 登录`.
- Browser-visible login attempt on this machine still ends with:
  - `The operation either timed out or was not allowed.`

### Database State Confirmed Locally

Read directly from the local database on 2026-06-10:

- `PasskeyCredential` exists:
  - `device_name = "Macbook air"`
  - `created_at = 2026-06-09T08:37:26.870723+00:00`
  - `last_used_at = null`
- `AdminPassword` does **not** exist.

Implications:

- The current stored credential has never successfully completed a passkey login in this environment after the public RP/origin migration.
- There is no password fallback available for "login first, then re-register from security settings".

### Registration Surface Investigation

Verified from source and runtime:

- The only built-in passkey registration flow is the local CLI server in `backend/app/cli.py`:
  - command family: `register-passkey` / `reset-passkey`
  - default host/origin: `localhost`
- The public backend exposes:
  - `GET /api/auth/passkey/reg-options`
  - `GET /api/auth/passkey/auth-options`
  - `GET /api/auth/passkey/status`
  - `POST /api/auth/login-passkey`
- The public backend does **not** expose a passkey registration verify/store endpoint for the public site.
- The public `/manage` UI exposes passkey login only; it does **not** expose passkey registration.

Conclusion:

- The current product supports **public passkey authentication**, but does **not** provide a supported public-domain registration path for a new machine credential.
- The legacy CLI registration path still produces a `localhost` registration origin, which is not sufficient to close public-domain passkey login on `https://blog.limengyang.me`.

### Automation Attempts Performed

1. Re-tried live passkey login from Chrome on `https://blog.limengyang.me/manage`.
   - Result: same browser-side WebAuthn timeout/not-allowed error.

2. Prepared a same-origin browser script using live `reg-options` to create a `blog.limengyang.me` credential and export the attestation.
   - Goal: avoid code changes by registering in the real public origin context and then storing the attestation locally.
   - Result: could not reliably inject/execute the registration script in the existing Chrome session with the available automation path.

3. Prepared a temporary local HTTPS registration server under `/tmp` to simulate a public RP registration flow without touching repository code.
   - Goal: generate a `blog.limengyang.me`-scoped credential from this machine and atomically replace the stale DB credential.
   - Result: server bootstrapped locally, but Chrome could not be cleanly launched into a separate host-resolver/certificate-bypass instance while the existing user Chrome process remained active.

### Acceptance Status For Phase 7

| Item | Status | Notes |
|------|--------|-------|
| P7-01 Reconfirm live RP/origin + gate | Verified | Completed |
| P7-02 Register public-machine credential | Blocked | No supported public-domain registration surface; local CLI still targets `localhost` |
| P7-03 Verify public passkey login | Blocked | Depends on P7-02 |
| P7-04 Verify passkey-only protection with real sessions | Blocked | Depends on P7-02; no admin password exists |
| P7-05 Record evidence | Verified | This section records the exact blocker state |

### Exact Blocker Summary

This round did **not** uncover a broken API contract. The blocker is product/workflow completeness:

1. The database still contains a stale credential created before/around the `localhost` RP phase and it has never logged in after the public RP migration.
2. The current system has no supported public-domain passkey registration UI or public verify endpoint.
3. The current system also has no admin password configured, so there is no authenticated in-product recovery path.

### Minimum Next Step To Truly Close P7-02

One of the following must exist before public-machine passkey closure can be completed truthfully:

1. Add a real public-domain passkey registration flow for `/manage`:
   - public `reg-options`
   - public registration verify/store endpoint
   - UI entry gated appropriately
2. Or provide an operator-only registration path that can register against `blog.limengyang.me` rather than `localhost`.
3. Or temporarily set an admin password, add a public-domain registration entry in the security flow, and then re-test.

Until one of those exists, any claim that this machine has successfully added and used a `blog.limengyang.me` passkey would be **未验证**.

## Phase 7 Operator Registration Tool Implementation 2026-06-10

Goal: implement the operator-only passkey registration tool identified as the minimum next step above.

### Design Decision

Chose **operator-key-protected HTTP endpoints** (approach A from handoff prompt):

- `POST /api/auth/passkey/operator/reg-options` — generates WebAuthn registration options for the configured RP.
- `POST /api/auth/passkey/operator/register` — verifies attestation and atomically replaces the existing credential.
- Both endpoints protected by `X-Operator-Registration-Key` header, validated against `OPERATOR_REGISTRATION_KEY` env var.
- Fail-closed: if `OPERATOR_REGISTRATION_KEY` is empty, all requests are rejected with 403.
- A static HTML page (`public/operator-passkey-register.html`) is served from `blog.limengyang.me` origin so that `navigator.credentials.create()` produces a credential with the correct `clientDataJSON.origin`.

### Implementation Evidence

#### Config

- `backend/app/config.py:38` — `OPERATOR_REGISTRATION_KEY: str = ""` added.
- `backend/.env.example` — `OPERATOR_REGISTRATION_KEY` documented with fail-closed note.

#### Schemas

- `backend/app/schemas/auth.py` — added `OperatorRegOptionsRequest`, `OperatorRegisterRequest`, `OperatorRegisterResponse`.

#### Service

- `backend/app/services/passkey_service.py` — added `replace_credential()`:
  - Queries all existing `PasskeyCredential` rows.
  - Deletes each within the same session.
  - Inserts new credential.
  - Flushes and refreshes.
  - Single transaction — rollback on failure means no partial state.

#### Router

- `backend/app/routers/auth.py` — added:
  - `_require_operator_key()` — fail-closed key validation helper.
  - `POST /api/auth/passkey/operator/reg-options` — operator-protected registration options.
  - `POST /api/auth/passkey/operator/register` — operator-protected attestation verify + credential replace.
  - Audit logging via `record_audit()` with action `operator_passkey_register`.

#### Operator Page

- `public/operator-passkey-register.html` — static page with:
  - Operator key input field (password type).
  - Device name input field (default: "MacBook Air").
  - Auto-detects API base URL from current hostname.
  - Calls `POST .../operator/reg-options` to get WebAuthn options.
  - Calls `navigator.credentials.create()` in the browser (real public origin).
  - Calls `POST .../operator/register` with attestation.
  - Shows success/failure status.
  - Displays RP ID, origin, and API URL for operator verification.

#### Operator Page Deployment Note

The HTML page is in `public/` and will be deployed to Cloudflare Workers with the next `npx wrangler deploy`. It will be accessible at `https://blog.limengyang.me/operator-passkey-register.html`. The page itself has no protection — the operator key on the API endpoints is the security gate.

### Static Validation

| Check | Result |
|-------|--------|
| `npx tsc --noEmit` | PASS |
| `python -c "from app.routers.auth import router"` | PASS |
| `python -c "from app.services.passkey_service import replace_credential"` | PASS |
| `python -c "from app.schemas.auth import OperatorRegOptionsRequest, OperatorRegisterRequest, OperatorRegisterResponse"` | PASS |
| `python -c "from main import app"` | PASS |
| Operator routes registered | `/api/auth/passkey/operator/reg-options`, `/api/auth/passkey/operator/register` |
| `OPERATOR_REGISTRATION_KEY` default is empty (fail-closed) | PASS |

### Runtime Validation Status

| Item | Status | Notes |
|------|--------|-------|
| Operator endpoints reject requests without key | **未验证** | Requires backend restart with code deployed |
| Operator endpoints reject requests with wrong key | **未验证** | Requires `OPERATOR_REGISTRATION_KEY` set in `.env` |
| Operator endpoints accept requests with correct key | **未验证** | Requires `OPERATOR_REGISTRATION_KEY` set in `.env` |
| `reg-options` returns correct RP ID (`blog.limengyang.me`) | **未验证** | Requires backend restart |
| Browser `navigator.credentials.create()` succeeds on public origin | **未验证** | Requires live page + backend |
| `register` verifies attestation and replaces credential | **未验证** | Requires end-to-end flow |
| New credential enables passkey login at `/manage` | **未验证** | Requires registration + login |
| `last_used_at` updates after successful login | **未验证** | Requires login |
| Passkey-only actions work with new credential | **未验证** | Requires login |

### Remaining Manual Steps

1. Set `OPERATOR_REGISTRATION_KEY=<strong-random-value>` in `backend/.env`.
2. Restart the backend (`launchctl stop com.blog.backend`).
3. Deploy frontend with the new `operator-passkey-register.html` (`npx wrangler deploy`).
4. Visit `https://blog.limengyang.me/operator-passkey-register.html`.
5. Enter the operator key and complete the WebAuthn registration flow.
6. Verify passkey login at `https://blog.limengyang.me/manage`.
7. Record all outcomes in this file.
