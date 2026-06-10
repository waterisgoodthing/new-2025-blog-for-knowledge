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

1. **Production API host not fully validated in this task.** Prior workflow noted `public-api.limengyang.me` returned HTTP 530 during audit. The frontend `NEXT_PUBLIC_API_URL` must point to a reachable host. This is a deployment configuration concern, not a code issue.
   - Live verification on 2026-06-09 reproduced `HTTP 530` for both `/api/auth/me` and `/api/auth/passkey/status` on `public-api.limengyang.me`.

2. **WebAuthn RP settings are localhost defaults.** `WEBAUTHN_RP_ID` defaults to `"localhost"` and `WEBAUTHN_ORIGIN` defaults to `"http://localhost:2025"`. Production passkey login requires these to be set to the production domain. This must be configured in the production `.env`.
   - Because the new passkey-preflight login gate is not yet deployed live, this task could not verify the end-to-end production RP/origin browser behavior from the actual manage login UI.

3. **In-memory challenge store.** `passkey_service.py` uses `_reg_challenge_store` and `_auth_challenge_store` as module-level dicts. This works for single-process deployments but will fail with multiple workers. Not introduced by this task.

4. **AUTH_BYPASS requires double opt-in.** Bypass now requires both `AUTH_BYPASS=true` and `AUTH_BYPASS_ALLOW=true`. This is fail-closed — setting only `AUTH_BYPASS=true` has no effect. Operators who want bypass in trusted environments must explicitly set both flags.

5. **Single-passkey limitation.** The system only supports one passkey credential at a time. Not introduced by this task.

6. **Passkey status endpoint is unauthenticated.** `GET /api/auth/passkey/status` reveals whether a passkey is registered. For a single-admin system this is low risk, but it is information disclosure.

7. **Production deployment drift.** The repository code and the live production manage bundle are not in sync as of 2026-06-09. This is the primary blocker for true live acceptance of the task.
