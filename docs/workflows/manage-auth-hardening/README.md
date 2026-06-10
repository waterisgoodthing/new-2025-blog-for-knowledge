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

Live production verification on 2026-06-09 found deployment drift:

- the production `/manage` route is reachable, but the served client bundle still reflects the older password-only login gate;
- the new passkey preflight UX is not present in the live bundle yet;
- public/private API host behavior still needs deployment-side correction or confirmation.

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
