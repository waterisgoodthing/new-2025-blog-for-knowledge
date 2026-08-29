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
| T10 | Authorized ops: grouped commits, push, local migration replay 025→026, local schema drift repair | S1, S2 | DONE |

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
- T10 (user authorization 2026-08-29 「我给你所有权限」):
  - Commit `549cb2f` — security remediation + migration 026 + LSR03 rehearsal assets (29 files, kept coherent: auth.py carries in-flight session-state endpoint, schemas included for import coherence).
  - Commit `2dc495b` — preserved in-flight frontend refactor, session-state client, agents/ governance docs, workflow folders; `.gitignore` extended for tooling state dirs (326 files).
  - Pushed `refactor/baseline` → `mine/refactor/baseline` (`202ea14..2dc495b`).
  - Local migration replay: started local PostgreSQL 16 (pg_ctl; `brew services` broken on this machine — `stop_timeout` error; stale `postmaster.pid` from unclean shutdown removed after confirming no live postmaster). `alembic upgrade head` as `blog_user` failed with `InsufficientPrivilegeError: permission denied to create role` and **rolled back cleanly** (transactional DDL; version stayed 025) — confirms migration 026 requires CREATEROLE/superuser, i.e. role provisioning is a DBA step outside the app runtime user. Replayed successfully as local superuser: version `['026']`, roles `app_role`/`legacy_migration_owner`/`legacy_note_adapter_runner` created.
  - Local schema drift repair: `review_items.mistake_id uuid NOT NULL` existed locally that no migration produces (013 `op.create_table` shape + ORM + green CI all lack it) and it **broke all review-item inserts for the runtime user** (`NotNullViolationError`, 6 test failures + real app breakage). Rows backed up to `/tmp/review_items_backup_20260829.json`; all 3 rows had `mistake_id == target_id` (pure legacy duplication), column dropped as superuser. Post-repair suite: **412 passed / 6 skipped / 0 failed** (skips are LSR03 tests gated on `LSR03_DATABASE_URL` by design); `validate_database_readiness()` PASS as `blog_user`.
