# Requirements

Source: full-repository scan report delivered 2026-08-29 (security subset S1–S6).

## S1 — Alembic readiness gate parity

- `backend/main.py` must pin `EXPECTED_ALEMBIC_REVISION` to the same head as `backend/alembic/versions/` (currently `026`).
- Deploy pairing rule documented: the database must be at the pinned revision before the backend that pins it starts. Fail-closed behavior (RuntimeError at startup) is intentional and must remain.

## S2 — Explicit irreversible migration

- Migration `026_legacy_system_retirement.py` must declare an explicit `downgrade()` that refuses automated rollback with a clear explanation, instead of failing with a missing-function error.
- The migration body (roles, extensions, grants, revokes) must not be restructured in this workflow — it is the user's in-flight LSR03 work covered by separate rehearsal suites.

## S3 — Fail-closed configuration guards

- The startup security checks (default JWT secret, active AUTH_BYPASS, wildcard CORS) must apply to **every non-development environment** (`ENV` outside `{development, dev, local, test}`), not only `ENV == "production"`.
- `ENABLE_REGISTRATION` blocking stays production-only (staging may intentionally allow registration).
- The development bypass semantics must be preserved: `ENV="development"` with `AUTH_BYPASS=true` + `AUTH_BYPASS_ALLOW=true` still boots (protected by `test_monitoring_routes.py::test_nonproduction_startup_keeps_the_existing_auth_bypass_configuration_semantics`).
- Existing error-message contracts in `test_monitoring_routes.py` (`AUTH_BYPASS`, `JWT_SECRET_KEY`, `CORS`, `ENABLE_REGISTRATION` matchers) must keep passing.
- Guards must be testable without a database (pure settings function).

## S4 — Constant-time shared-key comparison

- `OPERATOR_REGISTRATION_KEY` and `REGISTRATION_KEY` comparisons must use `secrets.compare_digest` (bytes, UTF-8) in `backend/app/routers/auth.py`.
- Behavior preserved: unset configured key → 403 "not configured"; wrong/missing provided key → 403.

## S5 — Remove orphaned endpoint

- `GET /api/auth/passkey/reg-options` must be removed. Verified consumers: none (frontend uses `/passkey/status`, `/passkey/operator/*`; CLI local server uses its own `/api/passkey/register/options` path on a private origin; no test references it).
- `/api/auth/passkey/status` must remain public (used by `src/lib/api/auth.ts:151` for the login page).
- A regression test must assert the route is gone.

## S6 — Error-text sanitization

- No `HTTPException(..., detail=str(e))` may remain in `backend/app/`.
- `auth.py` operator registration failure must not return `str(e)` to the client.
- Every replaced site must log the full exception server-side (`logger.exception`) so admin diagnosability is preserved via logs.
- Status codes preserved per site (502 upstream, 500 parse).
- Accepted residual: `POST /api/ai/prompt-test` intentionally returns gateway/provider error text in its `error` field — it is an admin-gated diagnostic endpoint whose purpose is surfacing those errors. Documented, not changed.

## General

- No API contract change other than the S5 removal (which has zero consumers).
- No frontend changes required.
- All changes stay within `backend/` and `docs/workflows/security-findings-remediation/` plus new test files.
- Working tree must not be committed, and pre-existing dirty files must be preserved untouched.
