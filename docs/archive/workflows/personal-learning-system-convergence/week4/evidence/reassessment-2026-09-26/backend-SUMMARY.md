# Week 4 independent backend verification — 2026-09-26

Status: FAIL for release acceptance due to confirmed CLI regression and CI configuration defect. Targeted Week 4 tests and isolated migration lifecycle PASS.

No repository files changed. Four exclusively created local scratch databases were used and retained: astra_week4_reassess_20260926_verify, astra_week4_reassess_20260926_full, astra_week4_reassess_20260926_isolation, astra_week4_reassess_20260926_e2e. No existing application database was queried or changed. Creation used createdb's PostgreSQL maintenance connection only; every migration/test target was explicitly validated by week4-scratch-guard.py. AI provider credentials were blanked for test commands; no real provider requests were made. E2E backend used AUTH_BYPASS=false and AUTH_BYPASS_ALLOW=false.

## Verified results

- Fresh migration 001→033: PASS. `alembic heads`: single 033.
- Empty challenge table downgrade 033→032→033: PASS.
- Live challenge downgrade: correctly rejected; alembic_version remained 033. After expiring scratch challenge rows, downgrade/reupgrade both PASS.
- True concurrent consume with separate sessions: results [True, False], exactly one successful consume. This supplements the checked-in lifecycle test that only stores two rows sequentially in one session.
- Seven Week 4 test files: **61 passed, 41 subtests passed** in 12.20s.
- Fresh full backend suite, no deselection: **883 passed, 3 failed, 9 skipped, 2 warnings, 47 subtests passed** in 27.03s.
- The three failures are exactly the CI exclusions. Re-running only these three in another fresh database: **3 passed** in 0.52s. This confirms order/data isolation dependence, although polluted-state dashboard failure triggers a MissingGreenlet exception.
- 9 skips: 6 LSR03 tests require separately configured isolated LSR03 target; 3 review-schema migration tests recognize only astra_week2_/opencode_week2_ names and therefore skip Week 4 scratch. A passing suite does not cover those scenarios.
- E2E scratch database migrated and ci-admin test user seeded; backend on 18001 was supplied to parent. Parent owns browser E2E and smoke results. PID35822 terminated after parent completed validation; databases retained.

## Confirmed defects

1. HIGH — `backend/app/cli.py:158-173` reuses a pooled AsyncEngine while creating/closing an event loop per request. Actual registration HTTP server reproduction: first GET /api/passkey/register/options returns 200; second GET disconnects without response. Trace points to cli.py:165 with `Future ... attached to a different loop`. New PR-15 options persistence exercises the pool before verification. Checked-in ceremony tests use one event loop and miss this runtime failure. Evidence: probes-sanitized.log and probes.py. Raw probes.log contains generated scratch challenge SQL parameters and should not be copied into published evidence.
2. HIGH — CI backend, runtime-smoke and E2E jobs configure blog_db, while migration env calls require_migration_target and no exact approved target is set. Pure guard invocation confirms deterministic rejection before any DB connection. Tests also install a scratch-only connection guard. Thus these jobs are not merely remotely unverified; current configuration cannot pass their schema initialization step. Configure ephemeral CI scratch database names instead of bypassing the guard. Evidence: probes-sanitized.log plus .github/workflows/ci.yml and backend/app/utils/scratch_db_safety.py.

## Exact reproduction commands

Run from repository root. Harnesses under this evidence directory are inspection-only external scripts. They never print credentials/challenges intentionally.

```sh
python3 scripts/week4-scratch-guard.py run --db-name astra_week4_reassess_20260926_verify -- createdb -h localhost -p 5432 astra_week4_reassess_20260926_verify
python3 /tmp/week4-reassessment-backend/run.py verify
python3 /tmp/week4-reassessment-backend/run.py full
python3 /tmp/week4-reassessment-backend/run.py isolation
python3 /tmp/week4-reassessment-backend/run.py e2e
python3 scripts/week4-scratch-guard.py run --db-name astra_week4_reassess_20260926_verify -- env PYTHONPATH=backend backend/.venv/bin/python /tmp/week4-reassessment-backend/probes.py
python3 scripts/week4-scratch-guard.py run --db-name astra_week4_reassess_20260926_verify -- env PYTHONPATH=backend backend/.venv/bin/python /tmp/week4-reassessment-backend/lifecycle_probes.py
```

`run.py` records actual guarded child commands in each log and uses backend/.venv/bin/python with PYTHONPATH=backend. Full-suite arguments: `-m pytest -p no:cacheprovider tests/ -q --tb=short -rs`. These create-once harness commands should use new unique database names if repeated; no automatic reuse/drop occurs.

Evidence files: targeted.log; full-suite.log; excluded-isolated.log; verify-upgrade.log; verify-head.log; verify-downgrade.log; verify-reupgrade.log; lifecycle_probes.log; downgrade-live.log; expired-downgrade.log; expired-upgrade.log; probes-sanitized.log; e2e-upgrade.log; e2e-seed.log. No commit, push, merge, deployment, production migration or actual-provider test was executed.
