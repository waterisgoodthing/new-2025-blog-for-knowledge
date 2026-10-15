# PR-17 (W4-D06) — CI four jobs: independent review

Reviewer role: INDEPENDENT (did not implement PR-17)
Mode: READ-ONLY (no source modified; this file is the only artifact created; no git write)
Date: 2026-09-26
Branch: `refactor/baseline`
Scope reviewed: `.github/workflows/ci.yml`, `tsconfig.test.json`, `playwright.config.ts`,
`tests/e2e/*.spec.ts`, `package.json` (`test:e2e`), `docs/ci-local-reproduction.md`,
and the PR-17 evidence under `.../week4/evidence/` and `.../evidence/gate/ci/`.

## Verdict

**FAIL**

The workflow/config plumbing is largely present and Jobs 1 and 3 are credible, but the PR's
central deliverable — four CI jobs that can pass — is not met:

- **Job 2 (`backend`) cannot pass as written.** Its own fresh-DB evidence log ends with
  `4 failed` and pytest exit code `1`, and the step has no tolerance mechanism. On a real CI
  run the `psycopg2` failure disappears (fresh venv), leaving the 3 state-pollution failures,
  so the step still exits non-zero and the job fails.
- **Job 4 (`e2e`) contains two broken locators** that fail with Playwright strict-mode
  violations even after the same-site cookie issue is solved: `03-capture.spec.ts:21` and
  `04-review-flow.spec.ts:19`. Both were reproduced (count = 2 matches each).

Remote GitHub Actions was not run (push not authorized), so this verdict is based on source
inspection, the PR's own evidence logs, and local runs/reproductions.

## Findings

| ID | Severity | Problem | Evidence (file:line) | Required action |
|---|---|---|---|---|
| PR17-R01 | HIGH | E2E-03 uses ambiguous accessible name `上传图片`; Playwright default name matching is a case-insensitive **substring**, so it resolves to **2** buttons (mode `上传图片` + workspace `点击上传图片`) → `toHaveAttribute` fails with a strict-mode violation once login works. | `tests/e2e/03-capture.spec.ts:21`; `src/app/manage/(workspace)/capture/components/capture-content.tsx:15`; `.../capture-workspace.tsx:331`; reproduction below (`count = 2`) | Use `getByRole('button', { name: '上传图片', exact: true })`, or scope to the `采集方式` group / add `data-testid`. |
| PR17-R02 | HIGH | E2E-04 `getByRole('heading', { name: '复习' })` substring-matches both the page `<h1>复习</h1>` and the empty-state `<h2>今日复习已完成</h2>`. On a fresh CI DB the review queue is empty, so the empty state renders → **2** matches → strict-mode violation. | `tests/e2e/04-review-flow.spec.ts:19`; `src/app/manage/(workspace)/review/page.tsx:9`; `.../review-queue.tsx:321`; `src/components/async-state-panel.tsx:75`; reproduction below (`count = 2`) | Use `{ name: '复习', exact: true }` or `{ level: 1 }`. |
| PR17-R03 | HIGH | CI Job 2 (`Run tests` = `pytest tests/ -q`) has no tolerance/deselection/`continue-on-error`. Its own fresh-DB evidence run exited `1` with `4 failed`. The `psycopg2` failure is local-only (absent from `requirements.txt`), leaving 3 deterministic state-pollution failures in CI → Job 2 always fails. | `.github/workflows/ci.yml:96-98`; `docs/workflows/.../week4/evidence/pr-17-ci-run-local.txt:43-60`; `.../evidence/gate/ci/job2-backend.txt:245-250`; `backend/requirements.txt:4` (asyncpg only) | Fix/exclude the polluting tests or isolate DB state per test; or explicitly mark Job 2 non-blocking and stop claiming PASS. Re-baseline the suite. |
| PR17-R04 | MEDIUM | The local E2E-01..04 failure aborts in the shared `login()` helper at `管理面板` (cross-site cookie), so R01/R02 are never reached and remain undetected locally; the local "1 passed / 4 failed" is an environment limitation, not a spec defect by itself. | `.../evidence/gate/ci/job4-e2e.txt:11-33`; `docs/ci-local-reproduction.md:172-184`; `src/app/manage/page.tsx:694` (heading exists) | After the CI same-site topology is verified, fix R01/R02; consider an auth fixture that does not depend on cross-origin cookies. |
| PR17-R05 | MEDIUM | The backend suite is non-hermetic. A rerun on the already-populated scratch DB produced `23 failed, 842 passed, 9 skipped, 21 errors` vs `4 failed, 882 passed` on the evidence's fresh DB. A CI job whose result depends heavily on residual DB state is fragile. | raw rerun below; `.../evidence/gate/ci/job2-backend.txt:53-95` (fresh); rerun failures reproduced locally on `astra_week4_pr17` | Add per-test isolation (transaction rollback / truncate / unique fixtures) and record a stable baseline. |
| PR17-R06 | LOW | The five `**/ui-v2/**` trees are excluded from `npm run test:typecheck`, yet their tests still execute under vitest; their type errors are covered by no step (main `tsc` excludes `**/*.test.*`). Documented W4-E10 tradeoff; only acceptable while ui-v2 stays unshipped. | `tsconfig.test.json:14-21`; `tsconfig.json:26`; `docs/ci-local-reproduction.md:207-212` | Keep the reservation recorded; require type-check re-enable before any ui-v2 import becomes shipped. |
| PR17-R07 | LOW | The `package.json` PR-17 diff also adds `"smoke": "node scripts/runtime-smoke.mjs"`, which is outside the declared PR-17 scope (only `test:e2e` was listed); likely from PR-16. | `git diff -- package.json` | Confirm attribution and commit scoping; keep PR boundaries clean. |
| PR17-R08 | INFO | The working tree is broadly dirty with many shipped-source modifications outside PR-17's declared file set. PR-17's own files touch no shipped runtime, but a blanket commit would contradict the "CI/config/tests/docs only" claim. | `git status --short` (128 entries) | Commit only PR-17 files; never `git add -A` these unrelated changes. |

Severity counts: **BLOCKER 0 · HIGH 3 · MEDIUM 2 · LOW 2 · INFO 1**.
No BLOCKER/data-loss/secret-exposure finding.

## Verification against source

### 1. CI YAML (`ci.yml`)
- Four jobs present: `frontend`, `backend`, `runtime-smoke`, `e2e` (`ci.yml:13,45,102,200`).
- PG 16 service + healthcheck wired on exactly the DB-using jobs: `backend` (`:54-67`),
  `runtime-smoke` (`:113-126`), `e2e` (`:214-227`). Frontend has none. Correct.
- No real secrets: `user/password`, `ci-test-secret-key`, `ci-test-admin-password` are test-only.
- Job 2 keeps the verified contract: `.venv` (`:80-82`), `pip install -r requirements.txt pytest`
  (`:84-86`), `from main import app` (`:88-90`), `alembic upgrade head` (`:92-94`),
  `pytest tests/ -v --tb=short` (`:96-98`). `python -m` from `working-directory: backend` puts
  `backend/` on `sys.path`, so no `PYTHONPATH=.` is required.
- Job 3 builds with non-localhost `NEXT_PUBLIC_API_URL=http://ci-check.invalid:8001` (`:159-162`);
  Job 4 with `http://api.ci.test:8001` (`:292-295`). Both satisfy the guard in
  `src/lib/api/config.ts:16`. Browser-reachable API stays `127.0.0.1:8001`.
- Job 4 host mapping via `sudo` (`:290`), preview (`:307-314`), then Playwright (`:316-317`)
  — ordering is correct.
- Seed heredoc (`:263-287`) is valid YAML block-scalar Python; `bootstrap_temp_admin(username,
  password)` exists (`backend/app/cli.py:41`). Session cookie is `SameSite=Lax`, `Path=/api`,
  and `secure` only for https (`backend/app/routers/auth.py:42-59`), so the http CI topology is
  not blocked by `Secure`.
- **Deterministic failure found: Job 2 only** (R03). No wrong working-directory, missing env var,
  bad port/health ordering, or nonexistent script was found in the other jobs.

### 2. `tsconfig.test.json` exclusion (W4-E10)
- Exclusion is scoped to the reserved tree only: `src/features/ui-v2/**`, `src/adapters/ui-v2/**`,
  `src/contracts/ui-v2/**`, `src/mocks/ui-v2/**`, `src/components/ui-v2/**`
  (`tsconfig.test.json:14-21`). No shipped `src/**` path and no non-ui-v2 test is excluded.
- No shipped code imports the ui-v2 tree (grep for `ui-v2` outside those five subtrees → 0 hits).
- Pre-fix errors were all under `src/features/ui-v2/**` (10 errors, `job1-test-typecheck-before.txt`).
- `npx tsc --noEmit` → exit 0; `npm run test:typecheck` → exit 0 (raw results below).

### 3. E2E routes/selectors (E2E-01..05)
Every referenced route and selector exists in current `src/app/**`:

| Spec | Route | Selectors | Exists? |
|---|---|---|---|
| E2E-01 | `/manage`, `/manage/dashboard` | `#username`/`#password` (`manage/page.tsx:425,436`), button `密码登录` (`:450`), heading `管理面板` (`:694`), `学习管理首页` (`dashboard-overview.tsx:510`), `快速开始` (`:109`), AuthGate redirect (`(workspace)/layout.tsx` → `auth-gate.tsx:13`) | Yes |
| E2E-02 | `/manage/notes/new` | `#content-title` (`content-editor.tsx:279`), placeholder `从这里开始写作...` (`:318`), button `保存草稿` (`:342`), text `已保存` (`:298`), URL rewrite `window.history.replaceState(.../manage/notes/${slug})` (`:182`) | Yes |
| E2E-03 | `/manage/capture` | group `采集方式` + `aria-pressed` mode buttons (`capture-content.tsx:49-66`), `点击上传图片` (`capture-workspace.tsx:331`), label `题干` (`manual-question-entry.tsx:95`) | Yes, but locator ambiguous (**R01**) |
| E2E-04 | `/manage/review` | h1 `复习` (`review/page.tsx:9` via `manage-page-header.tsx:17`), `今日到期` (`review-queue.tsx:300`), group `六档评分` (`:271`), empty `今日复习已完成` (`:321`) | Yes, but heading locator ambiguous in empty state (**R02**) |
| E2E-05 | `/notes` | `main[data-render-state]` (`notes/page.tsx:199`), default error heading `加载失败` + button `重试` (`async-state-panel.tsx:75,83`), route `**/api/notes*` matches `useNoteIndex` key (`use-index.ts:6`) | Yes |

**E2E-01..04 local failure root cause = environment, not a spec defect.** The failure is at
`expect(getByRole('heading', { name: '管理面板' }))` inside `login()` after `POST /api/auth/login`
→ 200 but `GET /api/auth/me` → 401 (`job4-backend.log`), consistent with the documented
`SameSite=Lax` cross-site topology (`localhost:8787` vs `api.localhost:8001`). The spec defect in
E2E-03/04 is separate and only hides behind this environment failure.

### 4. Shipped runtime source
- PR-17's tracked diffs are `ci.yml`, `tsconfig.test.json`, `package.json`; plus new
  `playwright.config.ts`, `tests/e2e/*.spec.ts`, docs and evidence. None are shipped runtime.
- **Caveat:** the working tree contains ~128 changed entries including many shipped files
  (`src/app/**`, `backend/app/**`). These are outside PR-17's declared set and are **not**
  attributable to PR-17 by this review. A commit that includes them would violate the
  "no shipped runtime modified" claim. Unexpected within the PR-17 diff: the `smoke` script
  (R07).

## Raw results (reviewer rerun)

Host: macOS/darwin · Node v26.0.0 · npm 11.12.1 · `backend/.venv` Python 3.12.13

```
$ npx tsc --noEmit
(no output)                      TSC_EXIT=0

$ npm run test:typecheck
> node node_modules/typescript/bin/tsc --noEmit --project tsconfig.test.json
(no output)                      TYPECHECK_EXIT=0

$ npx vitest run
 Test Files  70 passed (70)
      Tests  522 passed (522)
   Duration  5.35s
VITEST_EXIT=0
```

Backend (command exactly as requested; DB **not** recreated/dropped, and `astra_week4_pr17`
was already populated by the earlier evidence/E2E run):

```
$ python3 scripts/week4-scratch-guard.py run \
    --url "postgresql+asyncpg://limengyang@localhost:5432/astra_week4_pr17" -- \
    bash -c "cd backend && PYTHONPATH=. .venv/bin/python -m pytest tests/ -q"
PASS: db_name='astra_week4_pr17' source=explicit:--url
...
23 failed, 842 passed, 9 skipped, 2 warnings, 21 errors, 47 subtests passed in 37.79s
```

Failure families in the rerun: `test_pr09_verify_api_contract` (14 F), `test_pr09_verify_http`
(1 F + 21 E), `test_pr11_dashboard_service` (2 F), `test_lsr03_guarded_runner` (1 F). The 21
errors are `sqlalchemy.exc.*` (re-insert against residual rows), i.e. **cross-test/DB-state
pollution on a reused scratch DB** — the same class the evidence documents, but worse because
the DB was not fresh. This does not supersede the evidence's fresh-DB result; it demonstrates
the suite is not hermetic (**R05**).

Playwright locator reproduction (standalone, browsers already installed; no repo files written):

```
E2E-03 getByRole(button,{name:"上传图片"}) count = 2
E2E-03 buttons: [ '上传图片', '手工录入题目', '从题库记录错题', '点击上传图片' ]
E2E-04 getByRole(heading,{name:"复习"}) count = 2
E2E-04 headings: [ '复习', '今日到期', '今日复习已完成' ]
```

Evidence cross-checks:
- `job2-backend.txt:53-95` — fresh-DB failures: `psycopg2` present locally, `public` empty
  envelope false, `weak_top3` shows leftover `pr09-rework-kp` (kp id 15), MissingGreenlet on
  expired attribute. None touch PR-17 (no backend source changed) → pre-existing/environmental.
- `job4-e2e.txt:8` — E2E-05 PASS; `:11-33` — E2E-01..04 fail at the `管理面板` heading.
- `job3-smoke.txt` — `SMOKE referenced=20 ok=20 failed=0 checks=23 failed=0` (evidence only).
- `job1-test-typecheck-before/after.txt` — 10 errors all `src/features/ui-v2/**` before, none after.

## Job 2 failure classification (item 5)

| # | Failure | Classification | PR-17 cause? |
|---|---|---|---|
| 1 | `test_lsr03_guarded_runner::test_asyncpg_is_available_and_psycopg2_is_not_a_runtime_fallback` | Environmental: local `.venv` has `psycopg2`; `backend/requirements.txt:4` has only `asyncpg`, so a fresh CI venv passes | No |
| 2 | `test_pr09_verify_http::test_public_empty_envelope_explicit` | DB-state pollution (residual public mistake rows) | No |
| 3 | `test_pr11_dashboard_service::test_all_empty_answers_are_honest` | DB-state pollution (leftover kp id 15) | No |
| 4 | `test_pr11_dashboard_service::test_partial_service_failure_degrades_without_raising` | Pre-existing test/ORM-expiry interaction (MissingGreenlet), aggravated by shared DB | No |

Spot-check confirms the root causes above from `job2-backend.txt:53-188`. Because PR-17 changed
no backend source, none are regressions. However, they are **not** harmless: CI has no tolerance,
so they make Job 2 red (R03).

## NOT_VERIFIED

- **Remote GitHub Actions execution** of any job: NOT_VERIFIED (push not authorized; workflow was
  not run on GitHub).
- **CI same-site E2E topology actually restoring login** (`app.ci.test:8787` ↔ `api.ci.test:8001`
  via `/etc/hosts`): NOT_VERIFIED locally (no passwordless sudo; `*.ci.test` resolves to
  `198.18.1.16`, not loopback). Consequently E2E-01..05 against the real CI stack are unverified.
- **Whether Job 2's 3 state failures reproduce identically on `ubuntu-latest` + Postgres 16
  service**: inferred from the equivalent local PG 16 fresh-DB log; not executed in Actions.
- **`npm ci` lockfile/`package.json` sync** in CI: not executed by this review.
- **Job 3 runtime-smoke on ubuntu + workerd**: reviewer did not rerun it; evidence-only PASS.
- **Commit intent**: whether the new untracked files (`tests/`, `playwright.config.ts`,
  `scripts/runtime-smoke.mjs`) will be added in the PR; remote CI cannot succeed without them.

## Unresolved questions

1. Is Job 2 intended to be allowed-red (baseline failures) or must it be made green before the
   four-job CI claim holds? The workflow has no tolerance encoded.
2. Are E2E-03's `上传图片` / E2E-04's `复习` meant to be matched exactly, or should these specs
   rely on scoped/`data-testid` locators?
3. Should the backend suite be made hermetic (per-test isolation), given R05, before it is used
   as a CI gate?
4. Will the untracked new files be committed as part of PR-17 so remote CI can run them?

---

# §recheck — 2026-09-26 (post-fix re-verification)

Role: same INDEPENDENT reviewer. Mode: READ-ONLY (this appended section is the only write; no
source modified; no git write). Fresh scratch DB `astra_week4_pr17r` was dropped/created because
the recheck task explicitly authorized it.

## Recheck verdict: **PASS_WITH_NOTES**

R01, R02, R03 are independently reproduced as fixed. All reviewer reruns pass. Remaining items
are non-blocking open debt (R05–R08) and the unchanged NOT_VERIFIED remote-CI boundary.

## Per-finding status

| ID | Prior severity | Status | Recheck basis |
|---|---|---|---|
| PR17-R01 | HIGH | **CLOSED** | `03-capture.spec.ts` now uses `exact: true` on `上传图片`, `点击上传图片`, `手工录入题目`, `从题库记录错题`, and the `采集方式` group. Standalone reproduction: each exact locator resolves to **1**. |
| PR17-R02 | HIGH | **CLOSED** | `04-review-flow.spec.ts:27` uses `getByRole('heading', { name: '复习', exact: true })`; empty-state heading pinned exact (`:31`). Reproduction: exact `复习` = **1**. |
| PR17-R03 | HIGH | **CLOSED** | Job 2 deselects **exactly** the 3 isolation failures (`ci.yml:103-109`); `lsr03` psycopg2 test kept. Fresh-DB rerun of the exact command → **exit 0**, `883 passed, 9 skipped, 3 deselected`. |
| PR17-R04 | MEDIUM | **CLOSED (environment remains)** | The local cross-site cookie limitation still blocks E2E-01..04 locally, but it no longer masks a spec defect (R01/R02 closed). Topology still NOT_VERIFIED. |
| PR17-R05 | MEDIUM | **OPEN (tracked debt)** | Deselect is a workaround; suite is still non-hermetic. Documented in `docs/ci-local-reproduction.md` §"Deselected backend debt (R03)" with a follow-up to remove the flags. |
| PR17-R06 | LOW | **OPEN (accepted)** | `tsconfig.test.json` still excludes the 5 reserved ui-v2 trees; ui-v2 tests run under vitest but are not type-checked. Documented W4-E10. |
| PR17-R07 | LOW | **OPEN (non-blocking)** | `package.json` still adds `smoke` alongside `test:e2e`; attribution unchanged. |
| PR17-R08 | INFO | **OPEN (informational)** | Working tree still has unrelated dirty shipped files; PR-17 file set itself touches no shipped runtime. |

## Item 1 — deselect targets (exactly 3, lsr03 kept)

`ci.yml:103-109` contains exactly three `--deselect` flags and no `-k`/other selection:

- `tests/test_pr09_verify_http.py::test_public_empty_envelope_explicit`
- `tests/test_pr11_dashboard_service.py::DashboardPr11ServiceTest::test_all_empty_answers_are_honest`
- `tests/test_pr11_dashboard_service.py::DashboardPr11ServiceTest::test_partial_service_failure_degrades_without_raising`

These are exactly the three non-`psycopg2` failures recorded in `job2-backend.txt:246-249`.
`test_lsr03_guarded_runner::test_asyncpg_is_available_and_psycopg2_is_not_a_runtime_fallback`
appears in `ci.yml` **only in a comment** (line 99), not in any deselect. Arithmetic confirms the
account: old fresh run `882 passed + 4 failed + 9 skipped = 895`; recheck
`883 passed + 3 deselected + 9 skipped = 895` (the recovered pass is the lsr03/psycopg2 test,
now green because the local `.venv` no longer contains `psycopg2`).

## Item 2 — full E2E locator strict-mode audit (all 5 specs)

Every locator inspected against current source; none can resolve to >1 element in its reachable
state. Exact/scoped fixes verified by standalone Chromium reproduction (counts below all `1`).

| Spec | Locator | Source | Unique? |
|---|---|---|---|
| 01 | `#username`/`#password` | `manage/page.tsx:425,436` | yes (only form inputs) |
| 01 | `button 密码登录` exact | `manage/page.tsx:450` | yes (hint is a `<p>`) |
| 01 | `heading 管理面板` exact | `manage/page.tsx:694` | yes (body copy is a span, excluded by exact) |
| 01 | `heading 学习管理首页` exact | `dashboard-overview.tsx:510` | yes (excludes `…加载失败` error title) |
| 01 | `heading 快速开始` exact | `dashboard-overview.tsx:109` | yes |
| 02 | `#content-title`, placeholder `从这里开始写作...` | `content-editor.tsx:279,318` | yes |
| 02 | `button 保存草稿` exact | `content-editor.tsx:342` | yes |
| 02 | `[data-content-editor] >> text 已保存` exact | `content-editor.tsx:271,298` | yes (scoped to editor) |
| 03 | `group 采集方式` exact | `capture-content.tsx:49` | yes (count 1) |
| 03 | `button 上传图片` exact | `capture-content.tsx:15` | yes (excludes `点击上传图片`; count 1) |
| 03 | `button 点击上传图片` exact | `capture-workspace.tsx:331` | yes (count 1) |
| 03 | `button 手工录入题目` / `从题库记录错题` exact | `capture-content.tsx:16,17` | yes (panel titles are h2, not buttons; count 1 each) |
| 03 | `getByLabel 题干` exact | `manual-question-entry.tsx:95` | yes (single textarea; mistake panel not mounted) |
| 04 | `heading 复习` exact | `review/page.tsx:9` | yes (excludes `今日复习已完成`; count 1) |
| 04 | `heading 今日到期` exact | `review-queue.tsx:300` | yes (count 1) |
| 04 | `heading 今日复习已完成` exact | `review-queue.tsx:321` | yes (count 1) |
| 04 | `group /六档评分/` + `.first()` | `review-queue.tsx:271` | intentional multi-match handled by `.first()` on the either/or assertion |
| 05 | `main[data-render-state]` | `notes/page.tsx:199` | yes (single `<main>`) |
| 05 | `heading 加载失败` exact, `button 重试` exact | `async-state-panel.tsx:75,83` | yes (notes error branch renders only AsyncStatePanel) |

Standalone reproduction (`exact: true`): E2E-03 buttons/groups all `1`; E2E-04 headings all `1`;
E2E-01 headings/button all `1`. No remaining strict-mode collision found.

## Item 3 — shipped runtime source

No shipped runtime source modified by the fix. Files touched by the rework:
`.github/workflows/ci.yml`, `docs/ci-local-reproduction.md`, `package.json`, `playwright.config.ts`,
`tests/e2e/*.spec.ts`, `tsconfig.test.json`, and evidence/tsbuildinfo artifacts. A scan for any
`src/**` or `backend/app/**` file newer than this review found **none**. `git diff` for
`package.json` (only `smoke` + `test:e2e`) and `tsconfig.test.json` (only the 5 ui-v2 excludes) is
unchanged in shape from the first review. R07/R08 remain the only scope notes.

## Item 4 — raw recheck results

```
$ dropdb --if-exists astra_week4_pr17r; createdb astra_week4_pr17r
CREATED_EXIT=0

$ python3 scripts/week4-scratch-guard.py run \
    --url "postgresql+asyncpg://limengyang@localhost:5432/astra_week4_pr17r" -- \
    bash -c "cd backend && PYTHONPATH=. .venv/bin/alembic upgrade head"
PASS: db_name='astra_week4_pr17r' source=explicit:--url
... 001 -> ... -> 033 (head)
ALEMBIC_EXIT=0

$ python3 scripts/week4-scratch-guard.py run \
    --url "postgresql+asyncpg://limengyang@localhost:5432/astra_week4_pr17r" -- \
    bash -c "cd backend && PYTHONPATH=. .venv/bin/python -m pytest tests/ -q \
      --deselect tests/test_pr09_verify_http.py::test_public_empty_envelope_explicit \
      --deselect \"tests/test_pr11_dashboard_service.py::DashboardPr11ServiceTest::test_all_empty_answers_are_honest\" \
      --deselect \"tests/test_pr11_dashboard_service.py::DashboardPr11ServiceTest::test_partial_service_failure_degrades_without_raising\""
883 passed, 9 skipped, 3 deselected, 2 warnings, 47 subtests passed in 26.37s
PYTEST_EXIT=0

$ npx tsc --noEmit
(no output)                      TSC_EXIT=0

$ npm run test:typecheck
> node node_modules/typescript/bin/tsc --noEmit --project tsconfig.test.json
(no output)                      TYPECHECK_EXIT=0

$ npx playwright test --list
[chromium] › 01-login-dashboard.spec.ts:24:5 › E2E-01 ...
[chromium] › 02-note-creation.spec.ts:20:5 › E2E-02 ...
[chromium] › 03-capture.spec.ts:22:5 › E2E-03 ...
[chromium] › 04-review-flow.spec.ts:23:5 › E2E-04 ...
[chromium] › 05-error-retry.spec.ts:8:5 › E2E-05 ...
Total: 5 tests in 5 files
PLAYWRIGHT_LIST_EXIT=0
```

## Item 5 — NOT_VERIFIED (unchanged after recheck)

- **Remote GitHub Actions execution** of any of the four jobs: NOT_VERIFIED (push not authorized;
  workflow not run on GitHub). Job 2's deselect command is verified locally only.
- **Job 4 E2E-01..05 under the CI same-site topology** (`app.ci.test:8787` ↔ `api.ci.test:8001`
  via `/etc/hosts`): NOT_VERIFIED locally (no sudo; `*.ci.test` resolves to `198.18.1.16`). The
  Playwright run was not executed end-to-end; only static locator uniqueness and `--list` were
  verified.
- **Liveness of Job 2's 3 deselected tests in CI**: expected to remain failing until the isolation
  debt (R05) is paid; not separately re-proven on `ubuntu-latest`.
- **`npm ci` lockfile sync**, **Job 3 runtime-smoke on ubuntu/workerd**, and the **commit intent
  for untracked files** remain NOT_VERIFIED.
