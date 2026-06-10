# Manage Auth Hardening

## Goal

Investigate, constrain, and repair the administrator access path for `/manage` so production behavior matches the intended security model:

- anonymous visitors should not gain management capabilities;
- password and passkey login entry points should be explicit and understandable;
- production/private deployment auth modes should be separated deliberately instead of being mixed implicitly.

## Touched Domains

- `manage`: management console route, login gate, passkey/password UX, tab access behavior.
- `auth`: backend session resolution, bypass behavior, password/passkey login, auth-level enforcement.
- `shared infrastructure`: production API host expectations, deployment-mode auth boundaries, validation evidence.

## Current Status

Code changes completed and reviewed on 2026-06-09.

Live production verification on 2026-06-09 found deployment drift.

Deployment drift investigation on 2026-06-10 confirmed drift causes.

Production execution on 2026-06-10 closed all blockers:

- `cloudflared` tunnel restarted; `public-api.limengyang.me` ingress rule added; tunnel reconnected to Cloudflare edge.
- Frontend deployed from `notes-workspace-ux-upgrade` branch (commit `4e4b69d`) to Cloudflare Workers (Version `4149ddd3`).
- Live bundle now contains passkey preflight login gate (`checkPasskeyRegistered`, `passkey/status`, `使用 Passkey 登录`, `无法检查 Passkey 状态`, `服务器未注册 Passkey`).
- WebAuthn RP config updated: `WEBAUTHN_RP_ID=blog.limengyang.me`, `WEBAUTHN_ORIGIN=https://blog.limengyang.me`.
- Smoke test passed: all 7 acceptance checks verified via API and bundle analysis.
- Deployment-level acceptance: **PASS** (2026-06-10).

Remaining non-blocker items:

- Existing passkey credential (registered under `localhost` RP ID) must be re-register after RP ID change.
- In-memory challenge store, single-passkey limitation, and unauthenticated passkey status endpoint are pre-existing design constraints.

Temporary follow-up task requested on 2026-06-10:

- complete the public-deployment administrator flow using this machine's identity and register/add a local passkey credential against the live public RP configuration;
- treat this as a temporary auth/deployment execution task that does not change the scope of `open-source-closure`.

Phase 7 operator-only registration tool implemented on 2026-06-10:

- Added `OPERATOR_REGISTRATION_KEY` config (fail-closed when empty).
- Added operator-only endpoints: `POST /api/auth/passkey/operator/reg-options`, `POST /api/auth/passkey/operator/register`.
- Added `replace_credential()` for atomic credential swap in `passkey_service.py`.
- Added static operator registration page at `public/operator-passkey-register.html`.
- Remaining: set operator key in production `.env`, restart backend, deploy frontend, execute registration, verify login.

Changes made:
- Backend `AUTH_BYPASS` hardened with double opt-in (`AUTH_BYPASS` + `AUTH_BYPASS_ALLOW`); auto-create/auto-promote removed.
- All auth helpers (`get_current_admin`, `get_optional_user`, `get_optional_admin`) simplified and aligned.
- `/manage` login gate exposes passkey login with preflight check + friendly error mapping; password login as fallback.
- Passkey status distinguishes "not registered" from "cannot check".
- Settings tab passkey gate (`passkeyOnly: true` + `auth_level` render guard) preserved.
- Code review passed with no remaining code-level findings.

See [validation.md](./validation.md) for live evidence and residual deployment risks.

## Workflow Files

- [requirements.md](./requirements.md)
- [design.md](./design.md)
- [tasks.md](./tasks.md)
- [audit.md](./audit.md)
- [validation.md](./validation.md)
- [handoff-prompt.md](./handoff-prompt.md)
