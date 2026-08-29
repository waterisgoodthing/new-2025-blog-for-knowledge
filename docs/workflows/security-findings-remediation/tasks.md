# Tasks

Serial execution. Status updated immediately after each item. Approval: user instruction 2026-08-29 (autonomous completion of the security findings); commit/push/migration-execution/deploy remain unauthorized.

| # | Task | Finding | Status |
|---|------|---------|--------|
| T1 | Create workflow documents | — | DONE |
| T2 | Bump `EXPECTED_ALEMBIC_REVISION` to `026`; extract `validate_security_settings`; extend guards to non-dev ENV | S1, S3 | DONE |
| T3 | Constant-time key comparison in `auth.py` | S4 | DONE |
| T4 | Remove orphaned `GET /api/auth/passkey/reg-options` | S5 | DONE |
| T5 | Sanitize error-text leaks in `ai.py` (13) and `auth.py` (1) with server-side logging | S6 | DONE |
| T6 | Add guarded `downgrade()` to migration 026 | S2 | DONE |
| T7 | Add regression tests (settings guards, endpoint removal, revision parity, downgrade guard, operator key) | S1–S5 | DONE |
| T8 | Run backend test suite; record evidence | all | DONE |
| T9 | Independent review pass; update validation.md | all | DONE |

## Evidence Log

- T1: this folder created (README/requirements/design/tasks/validation).
- T2: `backend/main.py` — pin `026`; `_DEV_ENVIRONMENTS`; `validate_security_settings()`; `lifespan()` rewired. Existing `test_monitoring_routes.py` contracts preserved (dev bypass semantics test and AUTH_BYPASS/JWT_SECRET_KEY/CORS/ENABLE_REGISTRATION matchers all green).
- T3: `backend/app/routers/auth.py` — `secrets.compare_digest` (UTF-8 bytes) in `_require_operator_key` and `register`.
- T4: `backend/app/routers/auth.py` — `passkey_reg_options` endpoint removed; `generate_registration_options` service retained for `app/cli.py` local server; `/passkey/status` retained for the login page.
- T5: `backend/app/routers/ai.py` — module logger; 5×`except Exception`→opaque 502, 4×`ValueError`→opaque 500, 4×`RuntimeError`→opaque 502, all with `logger.exception`; `auth.py` operator register failure message fixed. `POST /api/ai/prompt-test` intentionally unchanged (admin-gated diagnostic surface).
- T6: `backend/alembic/versions/026_legacy_system_retirement.py` — explicit `downgrade()` raising RuntimeError with remediation text; migration body untouched.
- T7: `backend/tests/test_security_settings_guards.py` (18 collected incl. 1 parametrized ×4), `backend/tests/test_026_downgrade_guard.py` (2 tests) — 20 new tests total. Review hardening added: whitespace-only CORS rejection test and constant-time comparison static-source test.
- T8: see `validation.md`.
- T9: independent reviewer verdict `OVERALL: APPROVED`; 3 MINOR findings fixed in-workflow (whitespace CORS guard `.strip()`, constant-time source test, doc counts); 2 INFO accepted (ENV="prod" registration-guard semantics unchanged from pre-remediation; `prompt-test` diagnostic error field intentionally retained).
