# Independent Review — Week 4 fixes F06 (bounded throttle state) + F01 (CI DB config vs guards)

- Reviewer: independent (did not implement these changes)
- Date: 2026-09-27
- Repo: /Users/limengyang/2025-blog-public
- Branch: `refactor/baseline` (dirty working tree; no commit, no push)
- Scope files claimed under review:
  - `backend/app/services/login_throttle.py` (untracked)
  - `backend/app/config.py`
  - `backend/app/schemas/auth.py`
  - `backend/tests/test_login_throttling.py` (untracked)
  - `.github/workflows/ci.yml`
  - `docs/ci-local-reproduction.md` (untracked)
- Read-only: no source modified, no git write. One file created: this evidence file.
- Not touched: `blog_db`, `blog_v2`, any production target.

## Verdict

**PASS** for both F06 and F01 at the reviewed scope.

- F06: account keys are length-bounded (long username collapses to a 71-char `sha256:` key), the account map has a hard capacity with least-recently-updated eviction, cross-IP protection still fires, and `LoginRequest.username` rejects over-long input (HTTP 422) before any throttle state is created. Reproduced independently at service and endpoint level.
- F01: all three DB jobs (`backend`, `runtime-smoke`, `e2e`) use `astra_week4_ci` consistently in `DATABASE_URL`, `POSTGRES_DB`, and `pg_isready`; no `blog_db` target remains anywhere under `.github/`; the DB guards are intact and strictly stronger than before (the migration guard is an addition, not a relaxation). The guard accepts `astra_week4_ci` and rejects `blog_db`/`blog_v2`.
- Side effects: none found that break existing tests/clients or change the accepted delay semantics.

Remote GitHub Actions execution is **NOT_VERIFIED** (push unauthorized); YAML is parse-valid and the guarded local run passed.

## Severity counts

| Severity | Count |
|---|---|
| BLOCKER | 0 |
| HIGH | 0 |
| MEDIUM | 0 |
| LOW | 3 (informational; no fix requested) |
| INFO | 3 |

No BLOCKER or HIGH finding, so no additional reproduction is required.

## Findings

| # | Sev | Area | Finding | Evidence |
|---|---|---|---|---|
| 1 | LOW | F01 adjacent | `Settings.DATABASE_URL` default is still `.../blog_db` (pre-existing, unchanged). It is not a CI target: every DB job sets `DATABASE_URL=...astra_week4_ci`, and the frontend job runs no DB work. If a future job omits the env var, the migration/connection guards fail closed rather than hitting `blog_db`. | `backend/app/config.py` default line; `ci.yml` env blocks |
| 2 | LOW | F06 | The 256-char hashing branch is unreachable through the HTTP endpoint because `LoginRequest.username` caps at 100. It is defense-in-depth for direct service callers (tests exercise it). Not a defect. | `_MAX_ACCOUNT_KEY_LENGTH=256`; `max_length=100`; service-level repro |
| 3 | LOW | F06 | Account counters do not decay with time; eviction is least-recently-*updated* (reads do not refresh recency). Under a flood within one process an actively-throttled account could be evicted. Documented trade-off; the independently TTL-evicted IP dimension still applies. | `login_throttle.py` docstring L26-41; `_evict_overflow_accounts` L138-148 |
| 4 | INFO | CI coverage | `backend` job deselects exactly 3 pre-existing isolation-debt tests (documented in `docs/ci-local-reproduction.md`). Unrelated to F06/F01, but "green" backend CI has reduced coverage until the follow-up isolation task lands. | `ci.yml` `--deselect` lines; doc L110-127 |
| 5 | INFO | F06 | `LoginRequest` still has no `min_length` on username and no `max_length` on password; out of scope, pre-existing. | `backend/app/schemas/auth.py` L7-9 |
| 6 | INFO | F01 | The `alembic/env.py` migration guard is an **addition** relative to `HEAD` (`git show HEAD:backend/alembic/env.py` has no guard). The CI rename to a scratch name is what makes it compatible; the guard itself was not weakened. | `git diff HEAD -- backend/alembic/env.py`; `git show HEAD:...` |

## Reproduction — raw results

### 1. Guard checks (F01)

```
$ python3 scripts/week4-scratch-guard.py check --db-name astra_week4_ci
PASS: db_name='astra_week4_ci' source=explicit:--db-name
exit=0

$ python3 scripts/week4-scratch-guard.py check --url "postgresql+asyncpg://limengyang@localhost:5432/blog_db"
FAIL: URL contains forbidden substring 'blog_db' (source=explicit:--url)
exit=1

$ python3 scripts/week4-scratch-guard.py check --db-name blog_v2
FAIL: database name contains forbidden substring 'blog_v2' (source=explicit:--db-name)
exit=1
```

Direct guard-layer proof (`backend/app/utils/scratch_db_safety.py`):

```
require_scratch_database(astra_week4_ci)   -> ACCEPT
require_scratch_database(astra_week4_pr16) -> ACCEPT
require_scratch_database(blog_db)          -> REJECT (Database safety: verification requires a loca...)
require_scratch_database(blog_v2)          -> REJECT (Database safety: verification requires a loca...)
require_scratch_database(production)       -> REJECT (Database safety: verification requires a loca...)
remote host (db.example.com)               -> REJECT (good)
require_migration_target(astra_week4_ci)   -> ACCEPT
require_migration_target(blog_db)          -> REJECT (good)
```

### 2. YAML parse + consistency (F01)

```
$ backend/.venv/bin/python -c "<yaml.safe_load + print jobs>"
jobs: ['frontend', 'backend', 'runtime-smoke', 'e2e']
frontend      | DATABASE_URL= None | POSTGRES_DB= None
backend       | DATABASE_URL= postgresql+asyncpg://user:password@localhost:5432/astra_week4_ci | POSTGRES_DB= astra_week4_ci
   health: --health-cmd="pg_isready -U user -d astra_week4_ci" --health-interval=10s --health-timeout=5s --health-retries=5
runtime-smoke | DATABASE_URL= postgresql+asyncpg://user:password@localhost:5432/astra_week4_ci | POSTGRES_DB= astra_week4_ci
   health: --health-cmd="pg_isready -U user -d astra_week4_ci" --health-interval=10s --health-timeout=5s --health-retries=5
e2e           | DATABASE_URL= postgresql+asyncpg://user:password@localhost:5432/astra_week4_ci | POSTGRES_DB= astra_week4_ci
   health: --health-cmd="pg_isready -U user -d astra_week4_ci" --health-interval=10s --health-timeout=5s --health-retries=5
YAML OK
```

```
$ rg -n "blog_db" .github/
(no matches)
```

`AUTH_BYPASS: "false"` in all three DB jobs (L57/126/224); no `BLOG_APPROVED_MIGRATION_TARGET`, no `--allow-remote-host`, no host override in the workflow.

### 3. Required guarded test run (exact command from task)

```
$ python3 scripts/week4-scratch-guard.py run \
    --url "postgresql+asyncpg://limengyang@localhost:5432/astra_week4_pr16" -- \
    bash -c "cd backend && .venv/bin/python -m pytest tests/test_login_throttling.py tests/test_login_throttling_integration.py tests/test_auth_error_handling.py -q"

.............................                                            [100%]
29 passed in 6.33s
PASS: db_name='astra_week4_pr16' source=explicit:--url; executing ['bash', '-c', 'cd backend && ...']
```

(`astra_week4_pr16` exists on local PostgreSQL 16; guard accepted the local host. These three suites are DB-independent unit/endpoint tests using a fake `get_db` override; the conftest connection guard was installed and did not trip.)

### 4. F06 service-level reproduction (independent script, temp dir, not in repo)

```
=== SERVICE LEVEL ===
accounts after 1 huge failure: 1
key len: 71 prefix: sha256:e6631 key==input: False
count for huge: 4
delay new IP for huge (expect 2.0): 5.0          # 4th recorded failure -> delays[1]=5; correct per schedule
distinct long keys: 2                            # 5000-char shared prefix + distinct suffix -> 2 entries
accounts after long-name flood (expect 25): 25   # capacity=25, 400 distinct 300-char usernames
max stored key len (expect <= 71): 71
256 kept verbatim: True | 257 hashed: True
```

Interpretation: a 100,000-char username is stored as a 71-char fixed digest (not the input); the same long username accumulates on a single entry and still produces a non-zero delay from a fresh IP; distinct long usernames do not collide; a flood of distinct long usernames is hard-capped by capacity with a bounded max key length.

### 5. F06 endpoint-level reproduction

```
=== ENDPOINT LEVEL ===
101-char status: 422 | accounts: 0
100-char status: 401 | accounts: 1
100000-char status: 422 | accounts: 0
```

Interpretation: over-long usernames (`>100`) are rejected by request validation with 422 and create **zero** throttle entries; a username at the boundary (100) is accepted and creates state. This is the required "rejected before throttle state is created" property.

### 6. Eviction / delay-semantics side effect

The in-repo test `test_delay_schedule_graduated_and_capped` asserts the schedule `[0.0, 0.0, 0.0, 2.0, 5.0, 15.0, 15.0, 15.0]`; it passes. `record_success` and `record_failure` both key through `_account_key`, so the hash path is consistent. Eviction only triggers above `LOGIN_THROTTLE_MAX_ACCOUNTS` (default 10 000); below that the accepted delay semantics are unchanged. No regression found.

### 7. max_length side-effect sweep

- Backend tests that POST `/api/auth/login` use short usernames (longest: `pr09-verify-api-admin`, `pr09-http-admin`); no test literal exceeds 100 chars (`rg` for 101+ char literals in `backend/tests`: none).
- `RegisterRequest` already had `max_length=100`, so login is now consistent with registration rather than newly restrictive.
- Frontend `src/lib/api/auth.ts` sends `{ username, password }` with no client-side cap; a >100-char login now yields a raw HTTP 422 instead of 401. No shipped test or client posts such input, so nothing breaks; noted only as a UI-polish consideration (finding #5 class).

## Unresolved questions

1. **Remote CI is NOT_VERIFIED.** GitHub Actions was not run (push unauthorized). YAML validity and a guarded local pytest run passed; the four jobs' full remote matrix remains unproven here.
2. **Product decision:** should the login form cap username client-side (e.g. `maxLength=100`) so an over-long input shows a friendly message instead of a bare 422? Currently backend-only enforcement.
3. **Coverage debt (out of scope):** the 3 CI `--deselect`s reduce backend job coverage until the isolation follow-up lands. Not introduced by F06/F01; flagging so it is not mistaken for full green coverage.

## Scope / safety statement

- Files read: the six listed scope files plus `backend/app/routers/auth.py`, `backend/app/utils/scratch_db_safety.py`, `backend/tests/conftest.py`, `backend/alembic/env.py`, `scripts/week4-scratch-guard.py`.
- Files written: this evidence file only. No source file was edited. No `git add`/`commit`/`push`.
- Databases touched: `astra_week4_pr16` (guarded; the three suites do not open a connection) and read-only inspection of pg_database names. `blog_db`/`blog_v2` untouched.
