# Validation

Status: `F4 EXECUTION APPROVED (2026-08-17); PRA-01/02/03/04/05 COMPLETE; PRA-06 PASS; PRA-07 PASS_WITH_NOTES; PRA-08 PASS; overall PARTIAL; no production deployment/readiness claim`

The 2026-08-03 development/empty-data measurements and the 2026-08-17 PRA-04/PRA-08 run are historical evidence, not current-run acceptance evidence. The current user authorization permits PRA-04 through PRA-08 within the existing isolation and no-production-change boundaries. At current entry no frontend/backend service, temporary account, browser run or current-run performance sample is active.

Current interpretation: G3 is current PASS through FIX-01, but no fixed count in a historical F4 package is a current acceptance total. PRA-01/02/03 remain historical evidence unless current source review finds drift; PRA-04 onward requires current-run artifacts.

## FIX-05 F4-input delivery audit (2026-08-16)

- The parent records the current final commands: PSS browser `5 passed (13.3s)`, test typecheck PASS, source TypeScript PASS, Vitest `38 files / 372 passed`, and backend permission regression `14 passed`. Links, whitespace, diff and port cleanup checks also pass under the stated residual formatting warnings.
- Therefore the F4 input is ready for separate approval. This workflow remains unstarted: no instrumentation, source readiness mark, synthetic dataset/database, production build, login/performance sample, deployment or F4 action occurred.

## PRA-01 contract and entry validation (2026-08-17)

- Separate execution approval received for PRA-01 through PRA-08 only; it explicitly excludes deployment, production data/services/credentials, dependency/CORS/auth/permission/schema/route/renderer changes, Git publication and optimization work.
- Re-read: root `AGENTS.md`; parent `frontend-foundation-and-quality` README/design/requirements/tasks/audit/validation and `f4-input-package.md`; PRA README/design/requirements/tasks/audit/validation.
- Current workflow evidence: G2 isolated PASS, G3 limited PASS, G4 limited PASS; PRA-01 through PRA-08 were all unchecked before this update.
- Baseline command: `git status --short && git worktree list --porcelain`; baseline `HEAD=202ea14d3362a84a491a7a8e32d2afd5d2e0bc1f`, branch `refactor/baseline`, Node `v26.0.0`, npm `11.12.1`, PostgreSQL tools `16.14`. The main worktree already contains modified source and untracked workflow assets. In-scope modified source changes are optional-session/cache fixes, not readiness marks; they will be preserved by exact scoped patches and all runtime resources must be isolated from this tree.
- Frozen scenario, state, mark, sample and raw-schema contract: [`audit.md`](audit.md#pra-01-frozen-contract-2026-08-17). No build, service, database, synthetic data, login or browser sample has run in PRA-01.

## PRA-02 / PRA-03 failing-first readiness verification (2026-08-17)

| Command | Result | Evidence / limitation |
| --- | --- | --- |
| `npx vitest run src/lib/render-readiness.test.ts --reporter=dot` before implementation | FAIL | Vite could not resolve `./render-readiness`; this is the retained red-state proof. |
| same command after implementation | PASS, `2 passed` | fixed whitelist mark is emitted once and repeated commit does not duplicate it. |
| `npx tsc --noEmit` | PASS | source typecheck after state/mark additions. |

Changed files are `src/lib/render-readiness.ts`, its focused test, and the three existing route owners. The code records no content, slug, user, token or credential in any mark. jsdom only proves the small mark helper; PRA-05/06 must still provide the required real-browser DOM, Performance, network and side-effect evidence.

## PRA-04 isolation precondition and blocker (2026-08-17)

### Resumed isolated-snapshot evidence

The prior partial-copy blocker is superseded for build isolation only: a new detached worktree received a read-only full snapshot of the current main tree, with private copy-on-write `node_modules` and backend virtual environment. Its isolated PostgreSQL cluster replayed `001 -> 025`; `NEXT_PUBLIC_API_URL=http://api.localhost:8100 npm run build -- --webpack` completed successfully. No frontend/backend service, seed, temporary admin, browser sample, or production connection has started yet; PRA-04 remains in progress.

| Check | Result |
| --- | --- |
| ports `3000`, `3100`, `8100`, `55432` | free before PRA resource creation |
| `initdb --version` | PostgreSQL 16.14 available |
| `api.localhost` isolated HTTP check | `200`, remote `127.0.0.1` |
| isolated migration | PASS: empty cluster, `001 -> 025` |
| `NEXT_PUBLIC_API_URL=http://api.localhost:8100 npm run build` | FAIL: Turbopack rejects external `node_modules` symlink |
| `npm run build -- --webpack` retry | FAIL: partial copy of main dirty session/auth dependency graph cannot typecheck |

The exact build failures are retained here as text evidence: first `Symlink [project]/node_modules is invalid, it points out of the filesystem root`; then missing `invalidateAdminAuthState`, followed by missing `getSessionState` and the incompatible `AuthGate` `strict` option. These show why selectively copying target page changes is not a valid source baseline. No seed/admin/session/service/browser artifacts exist; the temporary root path is intentionally not recorded because it is being deleted in PRA-08.

## PRA-08 cleanup and final local integrity (2026-08-17)

- `pg_ctl -D <isolated>/postgres stop -m fast`: PASS, server stopped.
- `git worktree remove --force <isolated>/worktree`: PASS. Follow-up `git worktree list --porcelain` contains only the four pre-existing worktrees.
- `lsof -nP -iTCP:{3000,3100,8100,55432} -sTCP:LISTEN`: no output after cleanup.
- `git diff --check`: PASS.
- The temporary directory and its non-secret logs were moved to system Trash rather than irreversibly deleted. There was no generated admin/session/credential to retain or revoke.

### Main-worktree inventory after cleanup

- Related new files: `src/lib/render-readiness.ts`, `src/lib/render-readiness.test.ts`, and the untracked `docs/workflows/production-render-readiness-acceptance/` workflow directory.
- Related modified files: `src/app/notes/page.tsx`, `src/app/notes/[id]/note-detail-content.tsx`, `src/app/manage/page.tsx` (each also carried pre-existing optional-session work before PRA).
- Unrelated/pre-existing modified files include `AGENTS.md`, backend auth schema/router, package files, home/blog/about/public-page files, AuthGate/mobile navigation, and session/blog-index hooks/API files.
- Unrelated/pre-existing untracked sets include `.cluster/`, `agents/`, other `docs/workflows/*`, reports/scripts, PSS test/harness files, Markdown PoC files, and their supporting test files. No such file was staged, reverted, removed or copied back from the temporary worktree.

Historical status before the 2026-08-22 resumed isolated handoff: PRA-01/02/03/08 complete; PRA-04 BLOCKED; PRA-05/06/07 unexecuted because their required isolated production service was not established. The current PRA-04 PASS and PRA-05 evidence are recorded below; no p50/p90/max/failure-rate baseline or optimization recommendation is claimed here.

## Related regression closeout (2026-08-17)

| Command | Result |
| --- | --- |
| `npm run test:typecheck` | PASS |
| `npx tsc --noEmit` | PASS (PRA-03) |
| `npm test -- --reporter=dot` | PASS, `39 files / 374 tests`; pre-existing Markdown hydration `act(...)` warnings and `TimeoutNaNWarning` retained as warnings |
| `cd backend && PYTHONPATH=. .venv/bin/pytest tests/test_manage_write_permissions.py tests/test_optional_session_state.py -q` | PASS, `12 passed` |
| `npx playwright test src/app/public-session-state.browser.spec.ts` | FAIL before a test scenario: `page.goto('/blog/pss-public-blog')` reports invalid URL, so 1 failed and 4 did not run. This invocation has no configured base URL / isolated server because PRA-04 is blocked; it is not browser evidence and no retry is permitted without new isolated-service evidence. |
| `npx prettier --check` on all scoped source/workflow files | FAIL warnings in three pre-existing dirty route files and `audit.md`/`validation.md`; no auto-format was applied in order to preserve mixed user changes. |

The PSS Playwright failure artifact remains at the test runner's generated `test-results/` location; it is an environment/configuration failure, not an accepted PSS regression result. `git diff --check` still passes.

## PRA-04 current-run validation (2026-08-22)

| Check | Result | Evidence |
| --- | --- | --- |
| Main-tree preflight | PASS | HEAD `202ea14d…`; mixed status preserved; target ports free before resource creation; existing unrelated worktrees unchanged |
| Complete isolated snapshot | PASS | Detached `/tmp/pra04-20260822-auWgUg/worktree`; source dry-run has no content delta; private dependencies; no external `node_modules` symlink |
| Private frontend dependencies | PASS | `npm ci --no-audit --no-fund`; current snapshot lockfile; no dependency declaration change |
| Private backend dependencies | PASS after runtime selection | Python 3.14.6 failure retained; Python 3.12.13 `.pra04-venv` install from unchanged `backend/requirements.txt` passed |
| Isolated Alembic replay | PASS | `127.0.0.1:55432/pra_f4`; empty cluster; `001 -> 025`; current/head `025`; 40 tables; 46 foreign keys |
| Synthetic dataset | PASS | 30 total; 20 public visible; 10 hidden; note/blog/mistake `10/10/10`; D1 slug `pra04-d1` |
| Production build | PASS | `NEXT_PUBLIC_API_URL=http://api.localhost:8100 npm run build`; Next.js 16.2.12 Turbopack; Webpack fallback not needed |
| API/frontend services | PASS | API 8100, frontend 3100, PostgreSQL 55432 active; API health 200; frontend root/notes 200; `api.localhost` -> 127.0.0.1 |
| Normal auth/session proof | PASS | Login 200; HttpOnly `admin_session`; authenticated `/api/auth/me` 200; anonymous `/api/auth/me` 401; `AUTH_BYPASS=false` |
| Public visibility proof | PASS | Anonymous list 200/20; hidden fixture not leaked; D1 200 |
| Browser sampling/performance | NOT STARTED | Explicitly outside PRA-04; no raw samples or metrics created |
| Main-tree integrity after work | PASS | `git diff --check`; status inventory retained; no staging/revert/format/delete/product-source write |

Artifacts: `assets/pra04-isolation-manifest-20260822.json`, `assets/pra04-build.log`, `assets/pra04-migration.log`, `assets/pra04-runtime-checks.log`, and retained `assets/pra04-private-env-failure.log`.

Final PRA-04 state: `PASS`. This is isolated evidence only. It is not production readiness, deployment approval, or a performance baseline. Services/database/worktree remain active for PRA-05/PRA-06; PRA-08 cleanup is intentionally not executed in this task.

## PRA-05 current-run validation (2026-08-22)

| Check | Result | Evidence |
| --- | --- | --- |
| Minimal reproducible harness | PASS | `assets/pra05-browser-sampler.cjs`; no product-source/package/auth/schema/dependency changes |
| First bounded sample | PASS with retained failure evidence | E0 single sample persisted immediately and retained in `assets/pra05-e0-raw.ndjson` plus diagnostic copy `assets/pra05-e0-smoke.ndjson`; failure reason was the initial h3-count assertion |
| E0 anonymous empty | PASS | `assets/pra05-e0-raw.ndjson`: 11 rows, 10 valid and 1 failed; state `empty`, `notes:list-ready`, public synthetic link count 0 |
| L20 anonymous list | PASS | `assets/pra05-l20-raw.ndjson`: 10 rows, 10 valid; state `ready`, `notes:list-ready`, 20 synthetic links; one corrected health-check sample also persisted |
| D1 anonymous detail | PASS | `assets/pra05-d1-raw.ndjson`: 10 rows, 10 valid; state `ready`, `notes:detail-ready`, rendered prose/headings/code/table/link assertions |
| Browser/server temperature | PASS | All accepted full-run rows are `browser_temperature=cold`, `server_temperature=warm`; each uses a fresh browser context |
| Required raw schema | PASS | Every accepted and failed row includes navigation, LCP field, readiness, required API timing/status, DOM, console/page errors, failed requests, unexpected navigation, dialogs, downloads and explicit `failure_reason` |
| API/security boundary | PASS | Required public APIs status 200; no strict `/api/auth/me` or `/api/admin/*`; no cookies, tokens, passwords or secrets persisted |
| Fixture/handoff | PASS | Final isolated DB state `draft/hidden=true=5`, `published/hidden=false=20`, `published/hidden=true=5`, D1 public; services remain active |
| Main worktree integrity | PASS | `git diff --check` PASS; only scoped PRA-05 harness/raw/fixture/workflow artifacts added; no staging, revert, cleanup or deployment |

PRA-05 final status: `PASS` for the required E0/L20/D1 raw evidence. The initial failed sample remains in the same E0 raw artifact and is not silently removed. No server-cold samples were collected. No p50/p90/maximum/failure-rate calculation or performance-baseline claim is made; those belong to PRA-07.

## PRA-06 current-run validation (2026-08-22)

| Check | Result | Evidence / limitation |
| --- | --- | --- |
| Bounded M30 login probe | BLOCKED | `assets/pra06-login-raw.ndjson`, 1 attempted / 0 valid; login POST 200 followed by `/api/auth/me` 401 |
| HttpOnly admin session | NOT VERIFIED | browser context observed no usable HttpOnly session after login; no cookie/token persisted |
| Management ready state | NOT VERIFIED | no management API, no unique `[data-render-state]` main, no `manage:content-ready` |
| Negative logout/invalid-session boundary | BLOCKED | `assets/pra06-negative-probe.json`; authenticated-before-logout was never established |
| Bypass flags | PASS | manifest records `AUTH_BYPASS=false`, `AUTH_BYPASS_ALLOW=false` |
| Main-tree integrity | PASS | `git diff --check`; no product-source or unrelated-file changes |

PRA-06 final state: `BLOCKED`. This is an isolated auth/session evidence failure, not authorization to modify authentication, CORS, permissions, routes, or production configuration. PRA-07 cannot start because its M30 input is absent; PRA-08 cleanup is required.

## PRA-06 CORS runtime recheck validation (2026-08-22)

| Check | Result | Evidence / limitation |
| --- | --- | --- |
| Fresh detached snapshot/private dependencies | PASS | Manifest records a complete dirty-tree snapshot, private npm install, private Python 3.12 venv, and no copied credential-like env files |
| Isolated build/migration/M30 | PASS | Production frontend build PASS; PostgreSQL 55433; Alembic 025; synthetic fixture 30 total / 20 public-visible / 5 published-hidden / 5 drafts |
| Runtime single variable | PASS | `ALLOWED_ORIGINS=http://localhost:3101`; `AUTH_BYPASS=false`; `AUTH_BYPASS_ALLOW=false`; no source/config contract change |
| CORS header verification | PASS | API response included `Access-Control-Allow-Origin: http://localhost:3101` and `Access-Control-Allow-Credentials: true` |
| Normal browser login probe | FAIL | Exactly one form-reaching normal probe (M30-02): login POST 200, no `admin_session`, `/api/auth/me` 401, strict management 401 |
| Cookie attributes | NOT VERIFIED | No browser-visible `admin_session`; no cookie value was recorded |
| Management/render readiness | NOT VERIFIED | No management list success, no unique `main[data-render-state]`, no `manage:content-ready` |
| Negative no-cookie boundary | INVALID | `assets/pra06-cors-recheck-20260822.negative.json`; normal auth was not established |
| Failure preservation | PASS | Raw M30-02, startup preflight failure, exact failure_reason, manifest and logs are retained under the `pra06-cors-recheck-20260822.*` prefix |
| Ten-sample/performance work | NOT RUN | No 10 samples, p50/p90/max, failure-rate or performance/readiness claim |
| Main-tree integrity | PASS | `git diff --check` PASS; post-run status hash `6de303c46f48dfd069c96161d5b6e967a54ba056fa60879093ebd3ef21ea2476` matches the pre-run inventory; no product-source change |
| Exact-resource cleanup | PASS | 3101/8101/55433 have no listeners; new worktree is unregistered; recoverable copy is in `/Users/limengyang/.Trash/pra06-cors-recheck-20260822-wUJZDh` |

Recheck decision: `FAIL`. CORS runtime configuration took effect, but browser session propagation remained unestablished. This does not authorize auth/CORS source changes or imply production readiness.

## PRA-06 cookie propagation diagnostic validation (2026-08-22)

| Check | Result | Evidence / limitation |
| --- | --- | --- |
| Complete detached snapshot/private dependencies | PASS | New complete dirty-tree snapshot; private Node 24/npm 11 and Python 3.12 dependencies; no product-source or main-tree change |
| Isolated build/migration/runtime | PASS | Production build PASS; fresh PostgreSQL 55434; Alembic `001 -> 025`; API/frontend health 200; M30 `30/20/5/5` |
| Runtime-only contract | PASS | `NEXT_PUBLIC_API_URL=http://api.localhost:8102`; `ALLOWED_ORIGINS=http://localhost:3102`; both bypass flags false |
| Startup/preflight preservation | PASS | Duplicate startup bind failure and separate healthy preflight are retained in `assets/pra06-cookie-diagnostic-20260822-preflight.log`; no login occurred in the failed startup invocation |
| Single normal login | FAIL | Exactly one form POST: login `200`; no 10× sampler started |
| Server Set-Cookie evidence | PASS | Playwright/CDP saw `admin_session` Set-Cookie attribute presence: Path, Max-Age, HttpOnly, SameSite=Lax; no raw value persisted |
| Browser cookie blocking evidence | PARTIAL | CDP blocked-cookie reason count `0`; this means no detailed rejection reason was exposed, not that browser acceptance was proven |
| Browser cookie jar | FAIL | `admin_session` absent after login |
| Subsequent Cookie header | FAIL | `/api/auth/me` GET `401` twice and strict `/api/admin/dashboard/summary` `401`; Cookie header presence false on all captured requests |
| Readiness DOM/marks | FAIL | `manage:auth-submit` count 1; no unique `[data-render-state]` management main and no `manage:content-ready` |
| Complete failure reason | PASS | Raw NDJSON retains `strict-management-status:401; cookie-jar:admin_session-absent; readiness-dom:0:missing; readiness-mark:manage-content-ready-missing; console-errors; failed-requests` |
| Cleanup/main-tree integrity | PASS | Temporary admin disabled, isolated session revoked, exact resources stopped, ports free, worktree unregistered, recoverable snapshot retained, main status hash unchanged and `git diff --check` PASS |

Diagnostic decision: `FAIL / BLOCKED`. The server emitted Set-Cookie; the browser did not retain it, so subsequent requests did not send it. The exact browser rejection cause remains unverified. This diagnoses the boundary only and does not authorize an auth/CORS fix, route change, deployment, readiness claim, or performance baseline. No 10× samples were run.

## PRA-06 same-host topology diagnostic validation (2026-08-22)

| Check | Result | Evidence / limitation |
| --- | --- | --- |
| Complete detached snapshot/private dependencies | PASS | Fresh dirty-tree snapshot; private Node 24/npm 11 and Python 3.12 environments; no product-source change |
| Isolated PostgreSQL/migration | PASS | `127.0.0.1:55435/pra06_same_host`; empty cluster; Alembic `001 -> 025` |
| Requested runtime topology | PASS | Frontend `localhost:3103`; API bind/URL `127.0.0.1:8103`/`localhost:8103`; `NEXT_PUBLIC_API_URL=localhost:8103`; `ALLOWED_ORIGINS=localhost:3103`; both bypass flags false |
| Production frontend build | BLOCKED | Existing `src/lib/api/config.ts` production guard rejected the localhost API base; exact output in `assets/pra06-same-host-diagnostic-20260822-build.log` |
| API/frontend startup | NOT RUN | Build failed before either service started; startup failure kept separate |
| Synthetic M30/admin | NOT RUN | No seed or temporary admin was created; no password persisted |
| Real-browser normal login | NOT RUN | Login attempt count 0; no 10× run |
| Cookie/auth/readiness evidence | NOT VERIFIED | Raw NDJSON records `null/not_started`; no Set-Cookie, jar, Cookie header, `/api/auth/me`, strict management or DOM/mark evidence exists for this run |
| Cleanup | PASS | PostgreSQL stopped; ports 3103/8103/55435 free; worktree unregistered; recoverable copy retained |
| Main-tree integrity | PASS | Main status hash unchanged at `6de303c46f48dfd069c96161d5b6e967a54ba056fa60879093ebd3ef21ea2476`; `git diff --check` PASS |

Decision: `BLOCKED BEFORE BROWSER LOGIN`. This preserves the requested single-experiment boundary but does not establish same-host Cookie behavior and does not authorize changing the production guard, auth/CORS source, using a dev server, or making any readiness/performance claim.

## PRA-06 same-hostname execution diagnostic validation (2026-08-22)

| Check | Result | Evidence / limitation |
| --- | --- | --- |
| Complete detached dirty-tree snapshot/private deps | PASS | Snapshot at `/private/tmp/pra06-same-hostname-exec-20260822-qmNpfI/worktree` before cleanup; Node `v24.18.0`/npm `11.16.0`, Python `3.12.13`; `node_modules/.bin/next` asserted |
| Production build | PASS | `NEXT_PUBLIC_API_URL=http://api.localhost:8107 npm --prefix SNAPSHOT run build`; Next.js `16.2.12` Turbopack; first no-URL guard failure retained separately |
| PostgreSQL/migration/M30 | PASS | `127.0.0.1:55439/pra06_same_hostname_exec`; Alembic `001 -> 025`; synthetic M30 `30/20/5/5`; runtime admin password not persisted |
| Runtime CORS/bypass contract | PASS | `ALLOWED_ORIGINS=http://api.localhost:3107`; preflight 200 with matching allow-origin and credentials; both bypass flags false |
| Startup lifecycle | FAIL | `app.main:app` failure, `main:app` + default registration guard failure, then corrected API health 200 followed by process exit; logs retained under exact prefix |
| Persistent API verification | FAIL | `nohup main:app` returned one health 200, then 8107 listener absent at first interval; `api-persistent.log` and `persistent-preflight.log` |
| Real Playwright normal login | NOT AUTH EVIDENCE | Exactly one probe from snapshot cwd; browser navigation 200, all API calls `ERR_CONNECTION_REFUSED`; raw record does not establish login or auth |
| Set-Cookie/cookie jar/Cookie header | NOT VERIFIED | No API response reached the browser; no Set-Cookie, jar, or Cookie header evidence exists |
| `/api/auth/me` and strict management | NOT VERIFIED | Both were connection-refused/missing, not HTTP auth outcomes |
| Readiness DOM/marks | NOT VERIFIED | No API-backed management render; selector/marks absent because lifecycle failed |
| Exact failure reason | PASS | Raw `failure_reason`: `login-post-status:missing; me-status:missing; strict-management-status:missing; cookie-jar:admin_session-absent; readiness-dom:0:missing; readiness-mark:manage-content-ready-missing; console-errors; failed-requests` |
| Ten-sample/performance work | NOT RUN | No 10× samples, p50/p90/max, failure-rate or readiness/performance claim |
| Cleanup | PASS | 3107/8107/55439 free; PostgreSQL stopped; worktree unregistered; root recoverable at `/Users/limengyang/.Trash/pra06-same-hostname-exec-20260822-qmNpfI` |
| Main-tree integrity | PASS | Main pre-run status hash `6de303c46f48dfd069c96161d5b6e967a54ba056fa60879093ebd3ef21ea2476`; authorized artifacts only added; `git diff --check` verified |

Diagnostic decision: `BLOCKED / LIFECYCLE FAILURE`. This run does not provide auth/Cookie evidence and does not authorize changes to auth, CORS, permissions, routes, schema, renderer, dependencies, production configuration or deployment.

## PRA-06 corrected single-shell retry2 validation (2026-08-22)

| Check | Result | Evidence / limitation |
| --- | --- | --- |
| Exact runner execution | PASS_WITH_BLOCKER | Requested command completed with runner exit `0`; runner recorded `probe_exit=1` in `assets/pra06-single-shell-retry2-20260822.runner.log` |
| Corrected Alembic cwd | PASS | `assets/pra06-single-shell-retry2-20260822.migration.log`: isolated replay completed `001 -> 025` |
| Isolated production build | PASS | `assets/pra06-single-shell-retry2-20260822.build.log`; Next.js 16.2.12 Turbopack build completed |
| API/frontend runtime and preflight | PASS | `api-health.json`, `api-host-health.json`, `preflight.log`; API 8110, frontend 3110, CORS preflight 200 |
| Bypass/source boundary | PASS | Runner records `AUTH_BYPASS=false`, `AUTH_BYPASS_ALLOW=false`, `product_source_changed=false`; no source/auth/CORS/dependency/production change |
| Manifest/raw generation | BLOCKED | `pra06-single-shell-retry2-20260822.manifest.json` and `.raw.ndjson` are absent; probe stopped at `git rev-parse HEAD` before manifest initialization, exact error in `.log` |
| Browser/auth/readiness evidence | NOT VERIFIED | No browser login, temporary admin, session, raw sample, management API result or readiness mark was produced |
| Cleanup ports | PASS | Runner and read-only verification report zero listeners on 3110/8110/55441 |
| Worktree cleanup | PARTIAL | Exact root is recoverable at `/Users/limengyang/.Trash/pra06-single-shell-retry2-20260822-TADkxk`; Git still lists `/private/tmp/pra06-single-shell-retry2-20260822-TADkxk/worktree` as `prunable`; no prune/delete performed |
| Main-tree integrity | PASS | Pre/post status inventory hash `6de303c46f48dfd069c96161d5b6e967a54ba056fa60879093ebd3ef21ea2476`; `git diff --check` exit `0` |

Validation decision: `BLOCKED`. The corrected migration path and isolated runtime are verified, but the browser probe cannot begin until the runner/probe snapshot Git-metadata precondition is resolved under separate authorization. No auth/CORS conclusion, 10-sample run, performance metric, readiness claim or production-readiness claim follows.

## PRA-06 single-shell retry validation (2026-08-22)

| Check | Result | Evidence / limitation |
| --- | --- | --- |
| Exact reviewed runner execution | PASS | `PRA_RUN_ID=pra06-single-shell-retry-20260822 bash docs/workflows/production-render-readiness-acceptance/assets/pra06-single-shell-runner-20260822.sh`; exit code `30` |
| Isolated snapshot and setup | PARTIAL | Snapshot creation, private npm/Python setup, production build, PostgreSQL init/start reached; migration stopped before API/frontend startup |
| Migration | FAIL | `assets/pra06-single-shell-retry-20260822.migration.log`: `Path doesn't exist: '/Users/limengyang/2025-blog-public/alembic'` |
| Manifest/raw | NOT CREATED | No current-run manifest or raw NDJSON exists because the runner stopped before the browser harness |
| JSON/NDJSON parsing | PASS | At final verification, all 47 JSON/NDJSON files under `assets/` parsed; 117 documents/records; 0 errors; retry added no JSON/NDJSON |
| Browser/auth/readiness/performance | NOT RUN | No API/frontend listener, seed/admin/session, browser sample, Cookie, management-ready DOM or performance metric was created |
| Port cleanup | PASS | 3110/8110/55441 have no listeners after runner cleanup |
| Worktree cleanup | PARTIAL | Retry entry `/private/tmp/pra06-single-shell-retry-20260822-siiSYs/worktree` remains registered as `prunable`; no matching root was found in `/private/tmp` or `/Users/limengyang/.Trash`; no prune/delete was run |
| Main-tree integrity | PASS | Main status hash remains `6de303c46f48dfd069c96161d5b6e967a54ba056fa60879093ebd3ef21ea2476`; `git diff --check` PASS; no product source/auth/CORS/deployment/commit/push change |

Decision: `BLOCKED BEFORE BROWSER LOGIN`. This retry supplies migration failure and cleanup evidence only; it does not change the prior PRA-06 auth/session block or authorize a fix.

## PRA-08 current-run validation (2026-08-22)

| Check | Result | Evidence |
| --- | --- | --- |
| Temporary admin/session cleanup | PASS | Worker recorded admin disabled and 3 isolated sessions revoked/expired; no secret values persisted |
| Frontend/API/PostgreSQL cleanup | PASS | Exact current-run PIDs stopped; no run-scoped listener remains |
| Worktree/temp-root cleanup | PASS | Exact detached worktree removed; `/private/tmp/pra04-20260822-auWgUg` absent; recoverable copy at `/Users/limengyang/.Trash/pra04-20260822-auWgUg` |
| Port cleanup | PASS | `lsof` found no listeners on 3000, 3100, 8100 or 55432 |
| Pre-existing worktree preservation | PASS | Only the four pre-existing worktrees remain |
| Artifact preservation | PASS | PRA-04/05/06 JSON and NDJSON artifacts remain and parse successfully |
| Main-tree integrity | PASS | `git diff --check` PASS; no staging, revert, formatting, or unrelated deletion |

Post-cleanup targeted checks: `npx vitest run src/lib/render-readiness.test.ts --reporter=dot` = 1 file / 2 tests PASS; `npm run test:typecheck` = PASS; `npx tsc --noEmit` = PASS; JSON/NDJSON parse = PASS. The post-cleanup `git status --short` hash remains `6de303c46f48dfd069c96161d5b6e967a54ba056fa60879093ebd3ef21ea2476`, matching the pre-cleanup capture in `pra08-pre-cleanup-20260822.txt`.

## Final current-run decision

`PARTIAL`: PRA-04 is isolated-evidence PASS; PRA-05 is PASS_WITH_NOTES; PRA-06 is independently verified PASS with 10 valid M30 raw samples and negative-boundary evidence; PRA-07 is PASS_WITH_NOTES for raw-only aggregation; PRA-08 is PASS after final QA cleanup and integrity review. There is no F4 PASS, production-readiness, performance-baseline, optimization, deployment, commit, or push claim.

## PRA-07 raw-data aggregation validation (2026-08-22)

| Check | Result | Evidence / limitation |
| --- | --- | --- |
| Explicit raw input boundary | PASS | `pra07-raw-aggregation.py` reads only the three named PRA-05 raw files plus the ten raw paths in `pra06-m30-batch-final-20260822.manifest.json`; manifest is recorded as input metadata |
| Recomputable artifacts | PASS | `assets/pra07-raw-aggregation-20260822.json` and `.md`; JSON records paths, SHA-256, temperatures, filters, anomalies and algorithm |
| Scenario counts | PASS_WITH_NOTES | E0 `11/10/1/0.09090909090909091`; L20 `10/10/0/0`; D1 `10/10/0/0`; M30 `10/10/0/0`; all have at least 10 valid |
| Timing metrics | PASS_WITH_NOTES | TTFB, DOMContentLoaded, load, readiness and key API duration p50/p90/max computed from valid finite non-negative raw values using nearest-rank; E0 failed row remains listed |
| LCP handling | PASS_WITH_NOTES | All valid LCP values are `null`; report status is `not_available`, p50/p90/max remain null, and null is never treated as zero |
| M30 authentication boundaries | PASS | Login/me/strict-management status counts are reported separately from API duration; status codes are not used as latency values |
| Exclusion boundary | PASS | Smoke, health-check, server-cold and M30 negative-boundary artifacts are listed in `separate_or_excluded_artifacts` and excluded from primary aggregates |
| Independent recheck | PASS | Independent parser/reducer confirmed JSON/NDJSON parsing, input/output counts, failure rates, LCP null semantics and no password/token/raw-cookie values; `git diff --check` PASS |
| Scope claims | PASS | No service start, sample collection, source/auth/route/schema/renderer/dependency change, deploy, commit or push; no SLA, production baseline, optimization proof or F4 PASS claim |
| Gate | PASS_WITH_NOTES | PRA-07 aggregation is complete; PRA-08 final QA cleanup and integrity review is PASS |

## PRA-06 corrected single-probe harness confirmation (2026-08-22)

| Check | Result | Evidence |
| --- | --- | --- |
| Exact single-shell execution | PASS | `PRA_RUN_ID=pra06-noise-confirm-20260822 bash docs/workflows/production-render-readiness-acceptance/assets/pra06-single-shell-runner-20260822.sh`; runner exit `0`, probe exit `0`, one normal login attempt |
| Harness cookie-path correction | PASS | `pra06-cookie-diagnostic-20260822.mjs` queries `context.cookies(`${API_BASE}/api/auth/me`)`, matching cookie Path `/api`; raw jar evidence records `domain=api.localhost`, `path=/api`, `http_only=true` |
| Raw event preservation | PASS | New raw NDJSON retains `console_errors` and `failed_requests` arrays plus `expected_*`/`unexpected_*` partitions; counts reconcile exactly |
| Expected console noise | PASS | 1 exact `Failed to load resource: ... 401 (Unauthorized)` event classified expected; 0 unexpected console errors |
| Expected failed-request noise | PASS | 26 frontend `/notes|/blog` `net::ERR_ABORTED` link-prefetch events and 1 Google Analytics `/g/collect` `net::ERR_ABORTED` event classified expected; 0 unexpected failed requests |
| Login and Set-Cookie | PASS | Login POST `200`; `admin_session` Set-Cookie header present with Path/HttpOnly/Max-Age/SameSite attribute evidence; no raw cookie value persisted |
| Cookie jar and request header | PASS | Browser jar contains `admin_session`, `path=/api`, `http_only=true`; strict management request has Cookie header; authenticated `/api/auth/me` GET also has Cookie header |
| Strict management | PASS | `/api/admin/dashboard/summary` status `200`; same-context direct check `200` |
| Readiness | PASS | `[data-render-state]` selector count `1`, main count `1`, state `ready`; exactly one `manage:content-ready` mark |
| Scope boundary | PASS | Manifest says `ten_sample_run=false`, `performance_baseline=false`, `production_readiness_claim=false`; no product source/auth/CORS/dependency change |
| JSON/NDJSON parse | PASS | Independent parse: 38 JSON files and 21 NDJSON files, 0 errors |
| Diff/status/ports/worktree | PASS | `git diff --check` exit `0`; status hash unchanged at `6de303c46f48dfd069c96161d5b6e967a54ba056fa60879093ebd3ef21ea2476`; ports 3110/8110/55441 free; no noise-run worktree/temp root |

Independent validation decision: `PASS` for this corrected PRA-06 single-probe harness confirmation. The result is limited to one isolated normal-login probe and does not create a 10× performance matrix, p50/p90, production-readiness or deployment authorization. The prior failed raw evidence remains historical evidence and was not overwritten.

## PRA-06 M30 batch sampling validation (2026-08-22)

| Check | Result | Evidence / limitation |
| --- | --- | --- |
| Isolated production runtime | PASS | Runner and build artifacts under `pra06-m30-batch-20260822.*`; production build, Alembic replay, health, frontend/API startup, `AUTH_BYPASS=false`, private dependencies and detached snapshot; no product source change |
| M30 raw count | PASS | `pra06-m30-batch-final-20260822.manifest.json`: 10 attempts, 10 valid, 0 failed, failure rate 0; no p50/p90 computed |
| Raw field contract | PASS_WITH_NOTES | All ten raw NDJSON records contain navigation/TTFB/DCL/load/LCP fields, readiness marks, API timing/status evidence, DOM selector/main/state/30 rows, errors, expected/unexpected network partitions, side-effect arrays and failure reason; LCP is explicitly null in observations where no browser LCP entry was available |
| Normal auth/readiness | PASS | All samples login 200, authenticated me/strict management 200, one ready main, one auth-submit mark and one content-ready mark |
| Expected noise | PASS | Raw event arrays retained; expected 401 and ERR_ABORTED events separated from unexpected; all ten samples have zero unexpected console/page/network failures |
| No-cookie boundary | PASS | `pra06-m30-negative-final-20260822-negative.json`: no-cookie auth-me 401 and strict management 401 |
| Logout/invalid-session boundary | PASS | Normal authenticated-before-logout true; logout 200; after logout auth-me 401, strict management 401, no admin session cookie |
| Negative raw classification history | PASS_WITH_NOTES | Earlier preserved no-cookie raw records contain HTTP 401/401 but `valid=false` due a harness field-name mismatch; the intermediate recheck has `logout_boundary.valid=true`, and the final corrected raw has both no-cookie and logout boundaries `valid=true` |
| Failure preservation | PASS | Initial and corrected negative probe failures retained in `pra06-m30-batch-20260822-negative.json` and `pra06-m30-negative-recheck-20260822-negative.json`; no successful raw overwritten |
| Cleanup/integrity | PASS | Ports 3110/8110/55441 free; four pre-existing worktrees only; status hash unchanged; `node --check`, `bash -n`, `git diff --check` pass |
| Gate | PASS | Independent Verifier completed the raw/schema/auth/noise/negative-boundary/cleanup audit; PRA-07 is authorized only for serial raw-data aggregation. |

## PRA-08 final QA cleanup and integrity validation (2026-08-22)

| Check | Result | Evidence / limitation |
| --- | --- | --- |
| Target port cleanup | PASS | `lsof` checked `3000`, `3100-3108`, `3110`, `8100-8108`, `8110`, `55432-55441`; zero listeners. `ps` showed only unrelated pre-existing local processes; none were touched. |
| Worktree cleanup | PASS | `git worktree list --porcelain` shows exactly the four known pre-existing worktrees; `git worktree prune -n -v` is empty; no user worktree was deleted. |
| Temporary admin / credentials | PASS | Workflow records and final cleanup evidence confirm temporary admin disabled and three isolated sessions revoked/expired; final negative raw records `password_token_cookie_values_persisted=false`; no real service or credential was contacted. |
| Raw artifact preservation | PASS | 94 non-empty JSON/NDJSON files parsed into 164 records with zero parse failures; M30 final 10/10 valid, final negative raw valid, historical failed raw retained. |
| Aggregation integrity | PASS | PRA-07 JSON/MD exist; all 14 recorded input SHA-256 values match current files; aggregation contract test passes; sensitive findings are empty. |
| Main worktree protection | PASS | Status hash equals `6de303c46f48dfd069c96161d5b6e967a54ba056fa60879093ebd3ef21ea2476`; staged path list is empty; `git diff --check` passes. |
| Scope boundary | PASS | No service start, resampling, product/auth/route/schema/renderer/dependency change, real-service access, commit, push or deployment. |

Final PRA-08 decision: `PASS`. Evidence is persisted in `assets/pra08-final-cleanup-20260822.json`. The workflow overall remains `PARTIAL`: PRA-04 PASS, PRA-05 PASS_WITH_NOTES, PRA-06 PASS, PRA-07 PASS_WITH_NOTES, PRA-08 PASS. This does not establish F4 PASS, production readiness, a production performance baseline or deployment authorization.

## PRA-04 to PRA-08 current evidence recheck (2026-08-23)

| Check | Result | Current evidence / limitation |
| --- | --- | --- |
| PRA-04 isolation evidence | PASS | Manifest and retained logs agree on build, migration `025`, `40` tables, `46` foreign keys, synthetic `30/20/10`, bypass disabled and auth/public visibility. Former ports `3100/8100/55432` and the run worktree are absent after cleanup. |
| PRA-05 public matrix | PASS_WITH_NOTES | E0 `11/10/1`; L20 `10/10/0`; D1 `10/10/0`. Required raw fields and failed-row retention pass. LCP is null throughout, server-cold was not aggregated, and the original scenario manifests retain an earlier warm-probe `404` while corrected evidence is separate. |
| PRA-06 management matrix | PASS | Ten distinct manifest-listed raw rows are valid and satisfy normal session, strict management, ready DOM/30 rows, mark and unexpected-noise checks. Final no-cookie/logout boundary is valid and secret-value persistence flags are false. |
| PRA-07 aggregation | PASS_WITH_NOTES | Contract test passes; temporary recomputation matches the persisted JSON except `generated_at`; all 14 input hashes match. E0 failure and unavailable LCP remain explicit. |
| PRA-08 cleanup/integrity | PASS | 30 target ports have no listeners; four known worktrees remain; prune dry-run is empty; 94 JSON/NDJSON files parse into 164 records; no staged paths; `git diff --check` passes; status hash matches the recorded value. |
| Review independence | NOT_VERIFIED | This 2026-08-23 check is a Primary Owner perspective pass and does not claim new independent review. The separately recorded 2026-08-22 independent evidence remains historical evidence. |
| Gate | PARTIAL | Per-task evidence is accepted with the stated notes, but the missing LCP/server-cold evidence and non-representative local environment do not support a production performance baseline, budget/SLA commitment, F4 PASS, production readiness or deployment authorization. |
