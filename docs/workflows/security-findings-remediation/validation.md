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
| Migration 026 local replay (025→026) | PASS — as superuser; `blog_user` lacks CREATEROLE and failed cleanly (rolled back); role provisioning is a DBA step |
| Runtime user post-migration | PASS — `validate_database_readiness()` PASS as `blog_user`; full suite 412 passed / 6 skipped / 0 failed |
| Local schema drift repair | PASS — stray `review_items.mistake_id NOT NULL` (produced by no migration; broke all runtime inserts) dropped; rows backed up to `/tmp/review_items_backup_20260829.json`; values were exact duplicates of `target_id` |
| Commits + push | PASS — `549cb2f` (security), `2dc495b` (in-flight work preservation) pushed to `mine/refactor/baseline` |
| Production migration execution / deploy | NOT_AUTHORIZED — migration 026 needs CREATEROLE/superuser on the target and shared-cluster role/REVOKE review; release is a separate G2/G5 decision |
| Frontend | untouched; `tsc --noEmit` green earlier same day on identical tree |

## Release pairing reminder

Backend pinned to revision `026` refuses to boot against a database still at `025` (intended fail-closed). Deploying requires running `alembic upgrade head` first — execution is a G2/G5 gated action requiring separate approval.

## Addendum — authorized execution (2026-08-29, 「我给你所有权限」)

- Local migration replay evidence: see `tasks.md` T10. Summary: 025→026 executed on local `blog_v2`; version and roles verified; readiness PASS as runtime user; full suite green (412/6s/0f).
- Local drift repair evidence: stray column drop preceded by full-row backup (`/tmp/review_items_backup_20260829.json`) and redundancy proof (`mistake_id == target_id` on all rows); root cause predates this workflow (legacy SM2-era column added out-of-band; no migration produces it).
- Push: `202ea14..2dc495b refactor/baseline -> refactor/baseline` on remote `mine`.

## Addendum 2 — CI-exposed migration 026 defect and fix (2026-08-29)

- CI (PR #2, runs `33247219448` on `202ea14` and `33247588284` on `0b05bb5`) failed identically: 5×`test_mistake_review_service` + 1×`test_dashboard_routes` on `NotNullViolationError: null value in column "mistake_id" of relation "review_items"`, plus 2×LSR03 runtime-guard failures.
- Root cause: migration 026 (lines 1058–1072) adds `review_items.mistake_id UUID NOT NULL` with FK `fk_review_items_mistake` (`mistakes.id ON DELETE RESTRICT`) and unique index `uq_review_items_mistake_id`, backfilled from `target_id`; the ORM model had no such column, so **any database at revision ≥ 026 rejects every ORM review-items insert** — a production-breaking defect in the migration contract that only manifests post-026 (masked locally by pre-existing column state, invisible to fresh-025 CI runs before the migration landed).
- Fix (honors the migration; no new revision needed): `ReviewItem.mistake_id` added to the model mirroring the exact 026 DDL (FK name, `ON DELETE RESTRICT`, unique index name), `mistake_service.convert_mistake_draft` sets `mistake_id=m.id` after the mistake flush. Local DB restored to the 026 state per the same DDL (superseding the Addendum 1 column drop; row backup retained).
- CI venv alignment: backend job now creates `backend/.venv` and runs import/alembic/pytest through it, per the LSR03 runtime contract.
- Verification: local full suite against a true post-026 database — **412 passed / 6 skipped / 0 failed**; `validate_database_readiness()` PASS as runtime user. CI re-run pending on push.
