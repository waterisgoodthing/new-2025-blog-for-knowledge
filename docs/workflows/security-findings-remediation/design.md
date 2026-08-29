# Design

## S1 — Revision pin bump (`backend/main.py`)

`EXPECTED_ALEMBIC_REVISION = "025"` → `"026"`, paired with the untracked migration `026_legacy_system_retirement.py` (declares `revision="026"`, `down_revision="025"`). The startup check `validate_database_readiness()` keeps its fail-closed RuntimeError; CI (`alembic upgrade head` before tests) stays consistent because CI will have 026 once committed.

Deployment note: a backend pinned to `026` refuses to boot against a database still at `025` — that is the intended fail-closed pairing; run the migration first (execution is separately authorized).

## S2 — Guarded downgrade (migration 026)

Add an explicit `downgrade()` that raises `RuntimeError` with remediation text pointing at the DBA procedure. Rationale: today `alembic downgrade 025` fails with an opaque missing-function error; an explicit guard makes irreversibility a documented decision and gives the failure a searchable message. The migration body is untouched (protected by static contract tests `test_legacy_note_migration_static_contract.py`, which assert SQL content but do not forbid `downgrade`).

## S3 — Fail-closed guards (`backend/main.py`)

Extract the inline production checks from `lifespan()` into a pure function:

```python
_DEV_ENVIRONMENTS = {"development", "dev", "local", "test"}

def validate_security_settings(settings) -> None
```

- Returns immediately for dev environments (preserves tested development bypass semantics).
- For non-dev `ENV`: default `JWT_SECRET_KEY` → RuntimeError; active auth bypass (both flags true, matching `_is_auth_bypass_active()` semantics in `auth.py`) → RuntimeError; missing/wildcard `ALLOWED_ORIGINS` → RuntimeError.
- `ENABLE_REGISTRATION` check remains production-only.
- `lifespan()` calls `validate_security_settings(settings)` before `validate_database_readiness()` (bypass rejection still precedes DB access, per existing test).
- Error texts keep the substrings asserted by `test_monitoring_routes.py`.

Test settings objects are built with `SimpleNamespace` in the style of the existing tests; `getattr(..., default)` is used for optional fields so minimal namespaces work.

## S4 — Constant-time comparison (`backend/app/routers/auth.py`)

`secrets.compare_digest(a.encode("utf-8"), b.encode("utf-8"))` for both `_require_operator_key` and `register`. Missing provided key short-circuits to 403 exactly as before.

## S5 — Endpoint removal (`backend/app/routers/auth.py`)

Delete `passkey_reg_options` (GET `/api/auth/passkey/reg-options`). Verified non-consumers:

- Frontend: only `/api/auth/passkey/status` (`src/lib/api/auth.ts:151`) and the `/passkey/operator/*` family.
- CLI: `app/cli.py` serves its own `/api/passkey/register/options` from a local HTTP server and calls `generate_registration_options` directly — the service stays.
- Tests: `test_manage_write_permissions.py` references only the operator variant.

Regression test asserts the path is absent from `main.app.routes`.

## S6 — Sanitized errors (`backend/app/routers/ai.py`, `backend/app/routers/auth.py`)

Pattern (precedent: `diagnostics` no-leak test, observability middleware "log only safe context"):

```python
except Exception:
    logger.exception("<endpoint-specific message>")
    raise HTTPException(status_code=502, detail="AI 服务暂时不可用，请稍后重试")
```

- 5 sites `except Exception → 502 str(e)` (gateway/vision/text calls) → opaque 502 + `logger.exception`.
- 4 sites `except ValueError → 500 str(e)` (staged-response parsing; `ValueError` is never raised intentionally by `mistake_staged_service`, so it is always internal) → opaque 500 + `logger.exception`.
- 4 sites `except RuntimeError → 502 str(e)` (gateway error text, which itself embeds `str(exc)[:500]` from `ai_gateway.py:201`) → opaque 502 + `logger.exception`.
- `auth.py` operator register: `message=f"Registration failed: {str(e)}"` → fixed message + `logger.exception`.
- `prompt_test` (`ai.py`) intentionally returns provider error text (admin-gated diagnostic surface) — accepted residual risk, unchanged.

## Test additions

- `backend/tests/test_security_settings_guards.py`: non-dev fail-closed matrix, dev passthrough, removed-endpoint regression, revision-pin parity.
- `backend/tests/test_026_downgrade_guard.py`: static contract that 026 declares an explicit guarded `downgrade()`; file compiles.
- Operator-key comparison tests (correct/wrong/unconfigured) via direct `_require_operator_key` calls with monkeypatched settings.

## Out of scope / residual risks (for the release decision)

- Cluster-level statements in 026 (`CREATE ROLE ... LOGIN`, `CREATE EXTENSION`, `REVOKE ... FROM PUBLIC` re-granted to dedicated roles) — flagged; production execution requires G5 approval and a shared-cluster impact check.
- `GET /api/auth/passkey/status` stays public: it discloses only whether a passkey exists, which `POST /api/auth/login-passkey` error messages already disclose; protecting it would break the login page.
- AI provider error detail no longer reaches the admin UI; follow-up option is mapping gateway error kinds to safe user-facing categories.
