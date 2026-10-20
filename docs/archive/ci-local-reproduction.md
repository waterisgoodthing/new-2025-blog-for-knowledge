# CI Local Reproduction (PR-17 / W4-D06)

> 文档复核（2026-10-09）：本文件保留PR17/F04当期实测数字，不作为当前重跑结果；当前test:typecheck FAIL见 [状态](PROJECT_STATUS.md)。当前CI Job2已有B04双schema门禁，下方复现命令已补齐；本次仅核代码/修文档，未运行命令。数据库/provider/Git/生产操作须有对应授权。

How to reproduce the four GitHub Actions jobs from `.github/workflows/ci.yml` on a local machine
before pushing. Remote CI is **NOT_VERIFIED** here because pushing is not authorized for this
task; this document lets a human or a later authorized run validate the same commands.

The workflow has four independent jobs:

| Job | Purpose | Service |
|---|---|---|
| `frontend` | type-check + unit tests + production build | — |
| `backend` | migrations + full pytest suite | PostgreSQL 16 |
| `runtime-smoke` | OpenNext/Workers build + backend + workerd preview + smoke | PostgreSQL 16 |
| `e2e` | full stack + Chromium Playwright, `workers=1` | PostgreSQL 16 |

All local database work must target a Week 4 scratch database only. Use
`scripts/week4-scratch-guard.py`, which fails closed unless the target name matches
`^astra_week4_[a-z0-9_]+$` and rejects `blog_db` / `blog_v2`.

The three PostgreSQL CI jobs (`backend`, `runtime-smoke`, `e2e`) use the scratch database
name **`astra_week4_ci`** in `DATABASE_URL`, `POSTGRES_DB`, and the `pg_isready` health command.
This name is required for **guard compatibility, not a relaxation of the guards**: the repository
refuses `blog_db` migrations in `backend/alembic/env.py` (`require_migration_target`) and refuses
`blog_db` test connections in `backend/tests/conftest.py` (the `astra_week3_*`/`astra_week4_*`
connection guard). A scratch name needs no `BLOG_APPROVED_MIGRATION_TARGET` opt-in. The host stays
`localhost`, which the guards allow. Verify with:

```bash
python3 scripts/week4-scratch-guard.py check --url "postgresql+asyncpg://user:password@localhost:5432/astra_week4_ci"   # PASS
python3 scripts/week4-scratch-guard.py check --url "postgresql+asyncpg://user:password@localhost:5432/blog_db"          # FAIL
```

```bash
createdb astra_week4_pr17 2>/dev/null || true
```

---

## Job 1 — frontend

CI runs (Node 24): `npm ci` → `npx tsc --noEmit` → `npm run test:typecheck` → `npm test` → `npm run build`.

```bash
npm ci

# Shipped sources (tsconfig.json excludes **/*.test.*)
npx tsc --noEmit

# Test tree (tsconfig.test.json). Excludes the reserved ui-v2 tree — see W4-E10 below.
npm run test:typecheck

# Vitest unit tests
npm test

# Production build needs a NON-localhost API URL (src/lib/api/config.ts production guard).
# .invalid is RFC 6761 and resolves instantly to NXDOMAIN.
NEXT_PUBLIC_API_URL=http://ci-check.invalid:8000 npm run build
```

Expected: all exit 0. Local result for this PR: tsc PASS, test:typecheck PASS, vitest
`522 passed (70 files)`, build PASS.

## Job 2 — backend

CI creates `backend/.venv`, installs `requirements.txt` + `pytest`, checks `from main import app`,
runs `alembic upgrade head`, ORM `alembic check`, governed-catalog definition gate, then `pytest tests/ -q` with **no deselects** (the prior
cross-test isolation debt is fixed — see "Deselected backend debt" below).

```bash
python3 scripts/week4-scratch-guard.py run \
  --url "postgresql+asyncpg://$(whoami)@localhost:5432/astra_week4_pr17r" -- \
  bash -c 'cd backend && PYTHONPATH=. .venv/bin/alembic upgrade head && PYTHONPATH=. .venv/bin/python -m alembic check && PYTHONPATH=. .venv/bin/python -m app.models.schema_catalog_gate && PYTHONPATH=. .venv/bin/python -m pytest tests/ -q'
```

The guard validates the target first, then injects `DATABASE_URL` into the child process; the
child is never run if validation fails.

CI equivalent (fresh venv, so no stray packages):

```bash
cd backend
python -m venv .venv
.venv/bin/pip install -r requirements.txt pytest
.venv/bin/python -c "from main import app"
.venv/bin/python -m alembic upgrade head
.venv/bin/python -m alembic check
.venv/bin/python -m app.models.schema_catalog_gate
.venv/bin/python -m pytest tests/ -v --tb=short
```

Reference env for local runs:

```bash
export DATABASE_URL="postgresql+asyncpg://$(whoami)@localhost:5432/astra_week4_pr17r"
export JWT_SECRET_KEY=ci-test-secret-key
export AUTH_BYPASS=false
```

Local result (fresh `astra_week4_pr17r`, guard run): exit 0 —
`922 passed, 9 skipped, 0 deselected`. The `lsr03` asyncpg/psycopg2 test is
active; it passes once the local venv matches CI (no stray `psycopg2`). Note: a shared developer
venv may contain `psycopg2-binary`, which makes that one test fail locally even though CI installs
`requirements.txt` only. If you hit it, run the CI-equivalent fresh venv above instead of
touching the shared one.

### Deselected backend debt (R03) — RESOLVED

The three tests that used to fail on a shared/reused database are now fixed and run in-suite with
**no `--deselect`**. The root cause was cross-test data pollution: earlier modules commit canonical
rows into the shared pytest scratch DB, and both suites queried global (unscoped) state.

| Test | Old symptom | Fix |
|---|---|---|
| `tests/test_pr09_verify_http.py::test_public_empty_envelope_explicit` | `data["empty"]` was `False` — public rows committed by earlier tests | The request now runs against a transaction-scoped `get_db` override that hides all active public mistakes (uncommitted), then rolls back; the empty-envelope contract is still genuinely computed for a zero-row view |
| `tests/test_pr11_dashboard_service.py::DashboardPr11ServiceTest::test_all_empty_answers_are_honest` | `weak_top3` non-empty (e.g. `pr09-rework-kp` left by earlier tests) | The class deactivates prior canonical rows (`review_records` deleted, review items paused, questions/mistakes/knowledge points archived) inside each per-test transaction, which is always rolled back |
| `tests/test_pr11_dashboard_service.py::DashboardPr11ServiceTest::test_partial_service_failure_degrades_without_raising` | `MissingGreenlet` when leaked persistent `Question` rows were expired by the service's internal `rollback()` | Same per-test isolation: the summary query only sees the test's own (rolled-back) rows, so no expired persistent object is refreshed synchronously |

Deactivation is used instead of `TRUNCATE` because `TRUNCATE ... CASCADE` reaches the protected
append-only legacy migration tables (`trg_lnm_*_no_truncate`), which raise
`LEGACY_MIGRATION_EVENT_APPEND_ONLY`. The isolation only mutates state inside a transaction that is
rolled back on teardown, so no committed data changes.

The `test_lsr03_guarded_runner.py::test_asyncpg_is_available_and_psycopg2_is_not_a_runtime_fallback`
test remains active so CI still catches a psycopg2/asyncpg environment regression.

## Job 3 — runtime-smoke

```bash
# 1. Build the workerd artifact. The frontend is not called by the smoke script, so a
#    non-localhost (guard-safe) build URL is used; smoke probes the backend directly.
NEXT_PUBLIC_API_URL=http://ci-check.invalid:8001 npm run build:cf

# 2. Start the backend against the scratch DB.
cd backend
DATABASE_URL="postgresql+asyncpg://$(whoami)@localhost:5432/astra_week4_pr17" \
  ENV=development JWT_SECRET_KEY=ci-test-secret-key AUTH_BYPASS=false \
  ALLOWED_ORIGINS=http://localhost:8787 \
  .venv/bin/uvicorn main:app --host 127.0.0.1 --port 8001 &
cd ..

# 3. Start the workerd preview on :8787.
npm run preview -- --port 8787 &

# 4. Wait for both, then smoke.
curl -fsS http://127.0.0.1:8001/api/health
curl -fsS -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8787/
node scripts/runtime-smoke.mjs
```

Expected: `SMOKE referenced=20 ok=20 failed=0 checks=23 failed=0`, exit 0. Local result for this
PR: PASS.

## Job 4 — e2e

CI seeds a deterministic admin, maps `app.ci.test` / `api.ci.test` to `127.0.0.1` via
`/etc/hosts`, builds with a non-localhost but same-site API URL, starts backend + preview, then
runs Playwright.

```bash
# 1. Migrate the scratch DB (Job 2 already did this).
python3 scripts/week4-scratch-guard.py run \
  --url "postgresql+asyncpg://$(whoami)@localhost:5432/astra_week4_pr17" -- \
  bash -c "cd backend && PYTHONPATH=. .venv/bin/alembic upgrade head"

# 2. Seed an admin with known credentials (test-only values).
cd backend
DATABASE_URL="postgresql+asyncpg://$(whoami)@localhost:5432/astra_week4_pr17" ENV=development \
  PYTHONPATH=. .venv/bin/python - <<'PY'
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.cli import bootstrap_temp_admin
from app.config import get_settings

async def main():
    engine = create_async_engine(get_settings().DATABASE_URL)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        await bootstrap_temp_admin(session, username="ci-admin", password="ci-test-admin-password")
        await session.commit()
    await engine.dispose()

asyncio.run(main())
PY
cd ..

# 3. Install the browser.
npx playwright install --with-deps chromium

# 4. Same-site host aliases (needs sudo; this is why local full-stack e2e is often skipped).
sudo sh -c 'echo "127.0.0.1 app.ci.test api.ci.test" >> /etc/hosts'

# 5. Build with a non-localhost API URL that shares the preview's registrable domain (ci.test).
NEXT_PUBLIC_API_URL=http://api.ci.test:8001 npm run build:cf

# 6. Start backend (ALLOWED_ORIGINS must equal the preview origin) and preview.
cd backend
DATABASE_URL="postgresql+asyncpg://$(whoami)@localhost:5432/astra_week4_pr17" \
  ENV=development JWT_SECRET_KEY=ci-test-secret-key AUTH_BYPASS=false \
  ALLOWED_ORIGINS=http://app.ci.test:8787 \
  .venv/bin/uvicorn main:app --host 127.0.0.1 --port 8001 &
cd ..
npm run preview -- --port 8787 &

# 7. Run the suite.
E2E_BASE_URL=http://app.ci.test:8787 \
  E2E_ADMIN_USERNAME=ci-admin E2E_ADMIN_PASSWORD=ci-test-admin-password \
  npm run test:e2e
```

### Why the same-site hostnames matter

`admin_session` is set `SameSite=Lax` with `Path=/api` (backend `app/routers/auth.py`). The API is
a different origin from the preview, so the browser only sends the session cookie on a **same-site**
request. `app.ci.test` and `api.ci.test` share the registrable domain `ci.test`, making
`app.ci.test:8787 → api.ci.test:8001` same-site. A preview on `localhost:8787` talking to a
different host (e.g. `api.localhost:8001`) is cross-site, and the cookie is dropped — that is the
exact local blocker recorded in `evidence/pr-17-ci-run-local.txt` for E2E-01..04. E2E-05 (public
`/notes`, route-intercept based) has no auth dependency and passes standalone:

```bash
E2E_BASE_URL=http://localhost:8787 npx playwright test tests/e2e/05-error-retry.spec.ts --workers=1
```

Environment variables used by the e2e job (all test-only, no real secrets):

```bash
ENV=development
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/astra_week4_ci   # CI service DB (scratch name required by the guards)
JWT_SECRET_KEY=ci-test-secret-key
AUTH_BYPASS=false
ALLOWED_ORIGINS=http://app.ci.test:8787
E2E_BASE_URL=http://app.ci.test:8787
E2E_ADMIN_USERNAME=ci-admin
E2E_ADMIN_PASSWORD=ci-test-admin-password
```

### Local same-site run without editing `/etc/hosts` (F04)

The CI job needs sudo to append `app.ci.test`/`api.ci.test` to `/etc/hosts`. For a local run,
`playwright.config.ts` can instead inject a Chromium-only resolver mapping when
`E2E_RESOLVE_HOSTS=1`:

```text
--host-resolver-rules=MAP api.ci.test 127.0.0.1, MAP app.ci.test 127.0.0.1
--no-proxy-server
```

`E2E_BASE_URL` selects the preview origin and `E2E_API_URL` (read by `tests/e2e/helpers.ts`)
selects the API origin for the in-page readback fetches. Nothing in `/etc/hosts` changes.

The shared `globalSetup` (`tests/e2e/global-setup.ts`) runs the deterministic idempotent seed
`tests/e2e/seed/seed_week4_business.py` before the tests: it creates/rotates `ci-admin`, one
Subject/KnowledgePoint, one active `short_answer` Question (correct answer `3`), one converted
Mistake and its ReviewItem, and **resets that ReviewItem to due** on every run. It fails closed on
any target that is not a local `astra_week4_*` database. Set `E2E_SKIP_SEED=1` to skip it for runs
that need no backend (e.g. E2E-05 alone).

Exact local stack (scratch DB `astra_week4_f04_e2e`; adjust the DB name to any `astra_week4_*`):

```bash
# 1. Provision + migrate the scratch DB (guard-validated).
createdb astra_week4_f04_e2e 2>/dev/null || true
python3 scripts/week4-scratch-guard.py run \
  --url "postgresql+asyncpg://$(whoami)@localhost:5432/astra_week4_f04_e2e" -- \
  bash -c 'cd backend && PYTHONPATH=. .venv/bin/alembic upgrade head'

# 2. Build the workerd artifact against the same-site API origin (non-localhost -> production guard OK).
NEXT_PUBLIC_API_URL=http://api.ci.test:18001 npm run build:cf

# 3. Scratch backend on :18001 (ALLOWED_ORIGINS must equal the preview origin).
DATABASE_URL="postgresql+asyncpg://$(whoami)@localhost:5432/astra_week4_f04_e2e" \
  ENV=development JWT_SECRET_KEY=ci-test-secret-key AUTH_BYPASS=false \
  ALLOWED_ORIGINS=http://app.ci.test:18787 \
  backend/.venv/bin/uvicorn main:app --host 127.0.0.1 --port 18001 --app-dir backend &

# 4. workerd preview on :18787.
npm run preview -- --port 18787 &

# 5. Full business suite (globalSetup seeds; the browser resolver maps ci.test -> loopback).
E2E_RESOLVE_HOSTS=1 \
  E2E_BASE_URL=http://app.ci.test:18787 \
  E2E_API_URL=http://api.ci.test:18001 \
  E2E_ADMIN_USERNAME=ci-admin E2E_ADMIN_PASSWORD=ci-test-admin-password \
  DATABASE_URL="postgresql+asyncpg://$(whoami)@localhost:5432/astra_week4_f04_e2e" \
  npx playwright test --workers=1
```

Result for the F04 run (scratch stack above): `5 passed (12.0s)`, repeated green on a second run;
E2E-03/04 assert the business outcome by reading the created Attempt/MistakeDraft/ReviewRecord
back through the API. Raw logs:
`docs/workflows/personal-learning-system-convergence/week4/evidence/gate/ci/job4-e2e-business*.txt`.

---

## Known deviations — PR17/F04历史记录与当前校正

- **W4-E09 — no ruff/mypy.** `backend/requirements.txt` does not include `ruff` or `mypy` and the
  repository has no `pyproject.toml` lint/type config, so those steps from the PR-17 plan are
  intentionally omitted from Job 2; adding them would fail CI. Job 2 keeps the verified contract:
  venv, `pip install -r requirements.txt pytest`, import check, `alembic upgrade head`,
  ORM `alembic check`, governed-catalog `app.models.schema_catalog_gate`, `pytest`（双schema门禁为后续B04加入，本次未运行）。
- **W4-E10 — reserved ui-v2 tree excluded from the test type-check.** `tsconfig.test.json`
  excludes `src/features/ui-v2/**`, `src/adapters/ui-v2/**`, `src/contracts/ui-v2/**`,
  `src/mocks/ui-v2/**`, and `src/components/ui-v2/**`. 原W4-E10记载该候选树10项类型错误；
  本次未重新核验数量。组件范围后来已获Final Gate GRANTED，主路由仍未挂载，不再称待组件批准。
  排除候选树不能证明当前门禁通过：2026-10-09首次审查中应用TS PASS、测试TS仍因ReviewQueue两处
  TS2322 FAIL；本次只审文档、未重跑或改测试。候选树独立类型验收仍列工程债。
- **Job 2 deterministic-green (R03) — resolved.** Job 2 no longer deselects anything. The three
  previously deselected cross-test isolation failures are fixed in-suite (see "Deselected backend
  debt" above); the lsr03 psycopg2 environment test stays active.
- **Remote CI is NOT_VERIFIED.** The workflow is YAML-validated and all four jobs were reproduced
  locally to the extent the environment allowed, but GitHub Actions itself was not run (push is
  not authorized). Job 3 passed locally. Job 4 is now locally green end-to-end on a same-site
  scratch stack **without** `/etc/hosts` (F04 fix): all five R22b specs pass, including the
  E2E-03 question→wrong-attempt→draft and E2E-04 mistake→re-review→record business flows, with
  deterministic seed and backend readback. See "Local same-site run without editing `/etc/hosts`"
  above and `docs/workflows/personal-learning-system-convergence/week4/evidence/pr-17-e2e-business.md`.
  The earlier cross-site-cookie blocker recorded in `evidence/pr-17-ci-run-local.txt` is superseded
  by the resolver-based local topology; remote GitHub Actions remained unexecuted at that F04 evidence point; current B-candidate DB/browser/build/CI readiness is separately NOT_VERIFIED in [PROJECT_STATUS](PROJECT_STATUS.md).
