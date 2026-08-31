# Planning Audit

## Current State

- Task workspace created on 2026-06-09.
- This audit is a pre-implementation front-to-back closure check for the `manage-auth-hardening` task.
- No business-code changes have been made for this task yet.
- The repository has unrelated dirty files and an existing in-progress workflow under `docs/workflows/production-auth-cors-cleanup/`; those changes must be preserved.

## Approval Status

- `tasks.md` is drafted.
- Implementation has not been approved yet.

## Closure Check 2026-06-09

Checked requirements, design, and the current code path for front-to-back closure across:

- `src/app/manage`
- `src/lib/api/auth.ts`
- `backend/app/routers/auth.py`
- `backend/app/models/session.py`
- `backend/app/schemas/auth.py`
- `backend/app/config.py`
- `src/app/manage/security-tab.tsx`

## Current Closure Summary

### Closed Areas

1. Session entity and auth-level model are mostly closed.
   - `AdminSession`, `PasskeyCredential`, and `AdminPassword` exist.
   - Backend session issuance exists for both password and passkey login.
   - Frontend auth types include `auth_level: "password" | "passkey"`.
   - Sensitive server-side enforcement exists through `get_passkey_admin`.

2. `/manage` as a unified admin console is structurally closed.
   - The route exists.
   - Unauthenticated state and authenticated state are already split in one page.
   - Passkey-only tabs are represented in the UI and on the server for at least security actions.

3. Password-session vs passkey-session authority is conceptually closed.
   - Security UI distinguishes `密码 (普通权限)` vs `Passkey (最高权限)`.
   - Backend password-change route requires passkey admin.

### Open Or Broken Closure Points

1. **P0 Gap: auth mode boundary is not closed**
   - `AUTH_BYPASS` exists in config, but its intended environment contract is not enforced.
   - `_resolve_session_user()` can auto-create or auto-promote an admin when `AUTH_BYPASS=true`.
   - `get_current_admin`, `get_optional_user`, and `get_optional_admin` each contain separate bypass branches, increasing drift risk.
   - Result: deployment mode, trust boundary, and runtime behavior are not cleanly closed.

2. **P0 Gap: manage login UX is not closed against available auth methods**
   - Frontend API client already implements passkey login.
   - Backend router already implements passkey auth endpoints.
   - Current `/manage` login UI renders username/password only.
   - Result: the user-facing entry point does not represent the full supported auth contract.

3. **P1 Gap: unauthenticated `/manage` behavior is only partially closed**
   - The route intentionally renders publicly.
   - The page itself acts as the login gate by calling `getMe()`.
   - This is structurally valid, but the product contract is not documented clearly enough yet to distinguish:
     - "public route that contains a login gate"
     - from
     - "private route that should redirect before rendering".
   - Result: the current behavior can look like a broken intercept even when it is technically following current code.

4. **P1 Gap: passkey state messaging is not closed**
   - There is no login-gate copy that explains:
     - whether passkey is available on the current device,
     - whether no passkey has been registered,
     - or why password and passkey have different authority levels.
   - Result: even after wiring passkey login into the UI, user understanding would still be incomplete unless messaging is added.

5. **P1 Gap: production host/auth evidence is not yet fully closed inside this task**
   - Prior workflows document `public-api.limengyang.me` as the public production API host.
   - Live read-only checks in this task confirmed:
     - `https://blog.limengyang.me/manage` returns `200`,
     - `https://api.limengyang.me/api/auth/me` redirects to Cloudflare Access,
     - `https://blog.limengyang.me/api/auth/me` returns `404`.
   - But this task has not yet fully validated the anonymous/runtime behavior of the production public auth endpoint used by the current bundle.
   - Result: the production auth-host chain is only partially closed and must be revalidated during implementation.

## Front-To-Back Closure Matrix

| Capability | Frontend Entry | API Client | Backend Route / Guard | Data / Config | Current Closure |
| --- | --- | --- | --- | --- | --- |
| Password login | `/manage` login form | `login()` in `src/lib/api/auth.ts` | `POST /api/auth/login` | `AdminSession`, `AdminPassword`, `User` | Closed |
| Passkey login | No UI entry in `/manage` | `getPasskeyAuthOptions()`, `loginWithPasskey()` | `GET /api/auth/passkey/auth-options`, `POST /api/auth/login-passkey` | `PasskeyCredential`, WebAuthn config | Broken at UI boundary |
| Session check | `getMe()` on `/manage` mount | `getMe()` | `GET /api/auth/me` | `AdminSession` or bypass path | Partially closed; bypass boundary unclear |
| Logout | manage top bar | `logout()` | `POST /api/auth/logout` | `AdminSession.revoked` | Closed |
| Passkey-only password change | `/manage/security` | direct `fetch('/api/auth/set-password')` | `POST /api/auth/set-password` guarded by `get_passkey_admin` | `AdminPassword` | Closed server-side; UX messaging partial |
| Anonymous `/manage` gate | `/manage` route itself | `getMe()` failure path | `GET /api/auth/me` | deployment/auth mode contract | Partially closed |
| Trusted local bypass | none explicit in UI | none explicit | `_resolve_session_user()` / helper bypass branches | `AUTH_BYPASS` | Not closed |

## Evidence Notes

### Source Evidence

- `src/app/manage/page.tsx`
  - login gate exists inside the page.
  - unauthenticated state renders `LoginForm`.
  - `LoginForm` currently supports password only.

- `src/lib/api/auth.ts`
  - password login, passkey auth-options fetch, passkey login, `getMe()`, and logout all exist.

- `backend/app/routers/auth.py`
  - `AUTH_BYPASS` can auto-resolve an admin user.
  - passkey-only guard exists.
  - password and passkey login routes both issue real sessions.

- `backend/app/config.py`
  - `AUTH_BYPASS` defaults to `"false"`.
  - WebAuthn RP/origin settings currently default to localhost development values.

### Read-Only Production Evidence

- `GET https://blog.limengyang.me/manage` -> `HTTP 200`
- `GET https://blog.limengyang.me/api/auth/me` -> `HTTP 404`
- `GET https://api.limengyang.me/api/auth/me` -> `HTTP 302` to Cloudflare Access login
- Direct probe to `https://public-api.limengyang.me/api/auth/me` returned `HTTP 530` during this audit and is not sufficient to classify anonymous auth behavior there.

## Pre-Implementation Recommendations

1. Keep this task scoped to `manage` + `auth` + deployment/auth boundary docs.
2. Resolve the auth-mode contract before touching UI details.
3. Treat `AUTH_BYPASS` hardening as the first implementation block.
4. Treat passkey login UI completion as the second implementation block.
5. Revalidate production-host behavior after implementation and mark anything still unverified explicitly.
