# Validation

Environment: project-convention venv `backend/.venv` (Python 3.12, uv-created, `.gitignore:49` already covers it). Commands run from `backend/` mirroring CI (`python -m pytest tests/`).

## Executed checks

1. `py_compile` on edited files (`main.py`, `app/routers/auth.py`, `app/routers/ai.py`, `alembic/versions/026_legacy_system_retirement.py`) — **PASS**.
2. Targeted suites — **PASS**:
   - `test_security_settings_guards.py` + `test_026_downgrade_guard.py` — 18/18 passed (pre-review), 20/20 after review hardening.
   - `test_monitoring_routes.py` contract tests — 5/5 passed (AUTH_BYPASS / JWT_SECRET_KEY / CORS / ENABLE_REGISTRATION matchers + development bypass semantics preserved).
   - `test_manage_write_permissions.py` — 7/7 passed (route protection allowlist intact after endpoint removal).
   - Static migration contract tests — 31 passed / 4 skipped (026 body untouched, no contract violated).
3. Full backend suite (`.venv/bin/python -m pytest tests/ -q`) — **338 passed / 74 failed / 6 skipped**.
   - Failure attribution: all 74 produce the identical signature `OSError: [Errno 61] Connect call failed ('127.0.0.1', 5432)` — local PostgreSQL (user `blog_v2` database per local `.env`) is not running. Failures occur at DB connect, before any code path touched by this remediation. **BLOCKED (pre-existing local environment), not caused by these changes; CI is the authoritative green gate for these.**
   - 1 additional pre-review failure (`LSR03_PYTHON_RUNTIME_REQUIRED`) was the LSR03 harness refusing a non-project interpreter; resolved by running under `backend/.venv` as the harness requires.
   - 6 skips are the LSR03 tests that require `LSR03_DATABASE_URL` (by design).
4. Static greps — **PASS**:
   - `grep -rn "detail=str(e)" backend/app` → 0 hits (was 14).
   - `grep -rn "passkey/reg-options" backend/app src` → 0 hits (endpoint removed; CLI local server path unaffected).
   - `grep -c "logger.exception" backend/app/routers/ai.py` → 13 (5 Exception + 4 ValueError + 4 RuntimeError).
5. Independent review (separate agent, read-only) — **OVERALL: APPROVED**. Verified: contract matchers, repo-wide absence of consumers for the removed endpoint, ENV normalization edge cases (case/whitespace fail closed), compare_digest call correctness with preserved 403 semantics, downgrade() at module top level with single-head graph, no test relies on the removed error details. 3 MINOR findings were fixed inside this workflow (whitespace-only `ALLOWED_ORIGINS` now rejected; static source test pinning `secrets.compare_digest`; doc counts corrected). Accepted residuals recorded in `design.md` (`prompt-test` diagnostic field; ENV="prod" registration-guard semantics unchanged from pre-remediation behavior).
6. Frontend — untouched by this workflow. `npx tsc --noEmit` was green on this working tree earlier the same day (scan phase); no frontend file changed since.

## Final states

| Item | State |
|------|-------|
| S1 revision pin 025→026 | PASS |
| S2 guarded downgrade() | PASS |
| S3 fail-closed guards (non-dev ENV) | PASS |
| S4 constant-time key comparison | PASS |
| S5 orphaned endpoint removal | PASS |
| S6 error-text sanitization (14 sites) | PASS |
| Backend suite (full, local) | PARTIAL — 338 passed; 74 BLOCKED on missing local Postgres (pre-existing); CI green required before release |
| Migration execution / deploy | NOT_AUTHORIZED (separate approval required) |
| Commit / push | NOT_AUTHORIZED (working tree left uncommitted) |

## Release pairing reminder

Backend pinned to revision `026` refuses to boot against a database still at `025` (intended fail-closed). Deploying requires running `alembic upgrade head` first — execution is a G2/G5 gated action requiring separate approval.
