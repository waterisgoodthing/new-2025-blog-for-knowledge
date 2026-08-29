# F4 Input Audit

Current status: `CURRENT RUN PARTIAL; PRA-04 PASS; PRA-05 PASS_WITH_NOTES; PRA-06 PASS; PRA-07 PASS_WITH_NOTES; PRA-08 PASS; G2/G3/G4 PASS only in limited scopes`.

## Current evidence recheck (2026-08-23)

The Primary Owner performed a read-only perspective pass over the existing PRA-04 through PRA-08 artifacts. PRA-04 manifest/log facts, PRA-05 primary raw counts and retained E0 failure, PRA-06 ten M30 rows and final negative boundary, PRA-07 normalized recomputation and all 14 input hashes, and PRA-08 port/worktree/status integrity all remain consistent. The check started no service and collected no new sample. Because it is the same-agent perspective pass, it does not replace the separately recorded 2026-08-22 independent review.

The closure audit also found that this workflow lacked its own residual-risk and next-requirement files even though PRA-07 named them as outputs. `risks.md` and `next-requirements.md` now record the missing LCP evidence, absent server-cold matrix, warm-probe provenance inconsistency and the blocked production-budget decision. The overall gate therefore remains `PARTIAL`, not F4 PASS or production readiness.

The parent F4 input package and the 2026-08-17 PRA-04/PRA-08 run are historical evidence. The current run has explicit user authorization and must re-establish isolation, current artifacts and cleanup from the present dirty worktree. No current-run production service, temporary account, browser measurement or deployment exists at entry.

Key constraints carried into a future execution:

- G2's Mermaid/Markmap/Chart result is isolated-PoC evidence only; F4 cannot turn it into a production consumer migration.
- G3 protects public/management session boundaries; anonymous runs must remain free of strict/admin API noise.
- G4 selects Option A coexistence and preserves first-class mistake/review data, existing preview owners, and all authorization boundaries. The legacy `/write/[slug]` page-level gate gap is a separate residual security task, not F4 scope.
- Any inability to create an isolated production-build/API/database environment without real services, credentials, DNS/CORS changes or `AUTH_BYPASS` is a `BLOCKED` outcome.

## PRA-07 raw-only aggregation (2026-08-22)

The authorized read-only aggregation completed with `PASS_WITH_NOTES`. The only implementation artifact is `assets/pra07-raw-aggregation.py`; the CLI reads exactly `assets/pra05-e0-raw.ndjson`, `assets/pra05-l20-raw.ndjson`, `assets/pra05-d1-raw.ndjson`, and the ten raw paths listed by `assets/pra06-m30-batch-final-20260822.manifest.json`. It does not start services or discover additional primary samples. Recomputable outputs are `assets/pra07-raw-aggregation-20260822.json` and `assets/pra07-raw-aggregation-20260822.md`.

The script records input paths and hashes, browser/server temperature, valid/failed filtering, anomalies, nearest-rank percentile definition (`ceil(q*n)`, no interpolation), and sensitive-value findings. Failed rows are not silently discarded: E0 is 11 attempts / 10 valid / 1 failed / failure rate `0.09090909090909091`; L20 is 10 / 10 / 0 / `0`; D1 is 10 / 10 / 0 / `0`; M30 is 10 / 10 / 0 / `0`. All four scenarios have at least 10 valid rows. Smoke, health-check, server-cold and M30 negative-boundary artifacts are listed separately and are not mixed into primary timing counts.

The JSON/Markdown report contains readiness, TTFB, DOMContentLoaded, load, LCP and key API timing summaries. LCP is null for every valid sample in all four scenarios and is recorded as `not_available`, never zero. M30 login, `/api/auth/me` and strict-management status counts are a separate authentication-boundary overview; status codes are not latency values. Independent raw reparse/count comparison, no-sensitive-value check and `git diff --check` passed. No SLA, production performance baseline, optimization verification, production-readiness or F4 PASS claim follows. PRA-08 final QA cleanup and integrity review is PASS.

## PRA-08 final QA cleanup and integrity review (2026-08-22)

PRA-08 is `PASS`. The complete read-only evidence is `assets/pra08-final-cleanup-20260822.json`. `lsof` found zero listeners on `3000`, `3100-3108`, `3110`, `8100-8108`, `8110` and `55432-55441`; `ps` showed only unrelated pre-existing local processes, which were not touched. `git worktree list --porcelain` contains only the four known pre-existing worktrees and `git worktree prune -n -v` produced no output.

Workflow records and the final negative-run evidence confirm the temporary administrator was disabled, three isolated sessions were revoked or expired, and no password, token or raw cookie value was persisted. All 94 JSON/NDJSON artifacts were non-empty and parsed (164 records, zero failures); the two final aggregation outputs exist, all 14 recorded input hashes match current files, and sensitive findings are empty. Historical invalid samples and failed negative probes remain present. The main-tree status hash is unchanged at `6de303c46f48dfd069c96161d5b6e967a54ba056fa60879093ebd3ef21ea2476`, no paths are staged, and `git diff --check` passes. No service was started, no sample was collected, and no commit, push or deployment occurred. Overall F4 remains `PARTIAL`, not production-ready and not deployment-authorized.

## PRA-01 frozen contract (2026-08-17)

The separate user approval authorizes PRA-01 through PRA-08 only. The acceptance remains local and isolated: no deployment, real account/content/credential/API/database, dependency, CORS, authentication, authorization, route, Markdown-renderer, schema, visual, Git-publication or optimization change.

| Scenario | Dataset | Successful UI state and mark | Start / end | Failure conditions | Raw evidence |
| --- | --- | --- | --- | --- | --- |
| E0 anonymous list | no published notes | `main[data-render-state=empty]`; `notes:list-ready` | navigation start / mark | missing mark/state, protected/admin request, visible draft, page/console/network failure | `assets/pra-raw-samples.json` |
| L20 anonymous list | 20 deterministic published notes | `main[data-render-state=ready]`; 20 visible records; `notes:list-ready` | navigation start / mark | missing state/mark/count, public visibility failure, page/console/network failure | same |
| D1 anonymous detail | one deterministic Markdown-heavy published note | `main[data-render-state=ready]`; rendered article; `notes:detail-ready` | navigation start / mark | missing state/mark/article, unsafe/public visibility failure, page/console/network failure | same |
| M30 administrator | 30 deterministic mixed records; unpublished records excluded from anonymous reads | login form submit mark / `main[data-render-state=ready]`; `manage:content-ready` | `manage:auth-submit` / content-ready mark | failed normal Cookie login, missing mark/state, incorrect strict authorization, page/console/network failure | same |

Each server-warm scenario requires 10 fresh browser contexts. Server-cold samples, if feasible, use the identical record schema but are never merged into the browser-cold/server-warm aggregate. Metrics are TTFB, DOMContentLoaded, load, LCP if present, readiness duration, all required API start/responseEnd/duration/status, DOM result, errors and side effects. p50, p90, maximum and failure rate are calculated only from retained raw values; failed samples remain counted and stored. Marks are exact fixed strings without slug, title, username, content, token or other personal data.

### Entry review

- Current source/workflow records show G2, G3 and G4 as PASS only in their stated scopes; PRA-01/02/03 evidence is retained from 2026-08-17 and PRA-04 onward is being resumed.
- `git status --short` shows a pre-existing mixed worktree, and the current checkout contains the previously added readiness helper/test. No user change has been overwritten; production build, database, service and browser resources will be created only in a new isolated worktree after PRA-04's preconditions pass.

## PRA-02 / PRA-03 readiness evidence (2026-08-17)

- Red: `src/lib/render-readiness.test.ts` was introduced before implementation and failed because `./render-readiness` was absent.
- Green: `src/lib/render-readiness.ts` admits only four fixed non-sensitive names and uses existing Performance entries to avoid ambiguity on re-render. Focused Vitest result: `2 passed`.
- Page-local UI ownership: notes list has `loading|empty|ready|error` and `notes:list-ready`; note detail has `loading|ready|error` and `notes:detail-ready` after Markdown rendering; the legacy management content list has `loading|ready|error`, `manage:content-ready`, and the login handler starts the `manage:auth-submit` interval. The browser matrix remains required to prove real emitted marks and DOM results.
- `npx tsc --noEmit` passed. No production Markdown consumer, data owner, API call, auth semantics, CORS, route or visual design was changed.

## PRA-04 isolation result (2026-08-17): BLOCKED

- A new detached worktree, a new PostgreSQL cluster on `127.0.0.1:55432`, and database `pra_f4` were created outside the main tree. Alembic replay completed `001 -> 025`.
- The requested non-local production API string can use `http://api.localhost:8100`; an isolated server check resolved it to `127.0.0.1`, while the frontend origin `http://localhost:3000` is already in the existing strict allowlist. No DNS, host-file or CORS change was made.
- Turbopack refuses an external `node_modules` symlink in an isolated worktree. A Webpack retry reached application typecheck but failed because the current main worktree's uncommitted session-state change has dependencies outside the permitted copied files: first `invalidateAdminAuthState`, then `getSessionState` and the legacy `AuthGate` option contract.
- This is a source-isolation failure, not permission to copy all dirty auth work. No isolated backend service, seed, temporary account, real browser run, production API call or performance datum was created. PRA-05 through PRA-07 are blocked by dependency; PRA-08 cleanup is mandatory.

## PRA-08 cleanup result (2026-08-17): PASS

- Isolated PostgreSQL was stopped cleanly before the worktree was removed. The detached worktree no longer appears in `git worktree list --porcelain`.
- Port checks for `3000`, `3100`, `8100`, and `55432` found no listener after cleanup. No temporary administrator, session, password, seed, browser context or production-mode service was ever created.
- The temporary root and non-secret diagnostic logs were moved to the system Trash as recoverable cleanup; no active build output, database cluster, credential or process remains. Main-worktree status retained its prior mixed changes; the only new source additions are the two scoped readiness files.

## PRA-04 current-run result (2026-08-22): PASS

- `git status --short`, HEAD, branch, existing worktrees and ports were recorded before isolation. Main-tree changes remained intact; no file was staged, reverted, formatted, deleted or copied back.
- Complete source snapshot: `/tmp/pra04-20260822-auWgUg/worktree` is a new detached worktree at the current HEAD with the main tree's dirty and untracked source state copied as a whole. Dependencies and generated/runtime directories were isolated; no external dependency symlink was used. Main secret-like environment files were not copied into the isolated runtime.
- Backend private environment: Python 3.14.6 installation failure was retained as a compatibility observation, then Python 3.12.13 with unchanged requirements completed successfully. This did not require a dependency upgrade or source change.
- Database evidence: isolated PostgreSQL `127.0.0.1:55432/pra_f4`, empty cluster, Alembic `001 -> 025` PASS, current/head `025`, 40 tables, 46 foreign keys. Synthetic data is 30 total records, 20 public-visible records, 10 hidden records, and 10 of each note/blog/mistake type.
- Build/runtime evidence: Turbopack production build PASS; API at `127.0.0.1:8100`; frontend at `localhost:3100`; `api.localhost` resolves locally to `127.0.0.1`; health and frontend HTTP checks return 200.
- Security/visibility evidence: normal password login succeeds with an HttpOnly `admin_session`; authenticated admin `/api/auth/me` is 200; no-cookie `/api/auth/me` is 401; public list is 20; hidden fixture is absent; D1 is 200; both bypass flags are false. No password, cookie, token or secret was persisted.
- PRA-05/PRA-06 may use the active isolated handoff. At the PRA-04 handoff boundary browser sampling had not started; PRA-08 remains pending because resources are intentionally retained.

## PRA-05 current-run result (2026-08-22): PASS

- Primary Owner takeover: `senior-qa-sdet` after two Senior Frontend Worker no-op TASK_BLOCKs; scope was limited to anonymous E0/L20/D1 browser sampling. No PRA-06 work was started.
- Harness: `assets/pra05-browser-sampler.cjs`. It records exact base URLs, git HEAD `202ea14d3362a84a491a7a8e32d2afd5d2e0bc1f`, Chromium `151.0.7922.34`, production-build-local-isolated mode, browser/server temperature, fixture state and per-sample evidence. It uses `[data-render-state]` and asserts exactly one node whose tag is `main`; no `locator('main')` is used.
- Raw evidence: E0 `assets/pra05-e0-raw.ndjson` = 10 valid + 1 failed; L20 `assets/pra05-l20-raw.ndjson` = 10 valid; D1 `assets/pra05-d1-raw.ndjson` = 10 valid. Each full-run sample is fresh-browser/server-warm. The first failed E0 sample is retained in the same E0 raw artifact and in the diagnostic copy `assets/pra05-e0-smoke.ndjson`; it was not counted as valid.
- Required evidence passed for all full-run samples: readiness state/mark, navigation timing, required public API timing and status, DOM assertions, console/page errors, failed requests, unexpected navigations, dialogs and downloads. LCP was recorded as null where Chromium exposed no entry.
- Negative/public boundary evidence: no strict `/api/auth/me`, no `/api/admin/*`, no failed requests, no console/page errors and no unexpected side effects in the valid full-run samples.
- Fixture evidence: `assets/pra05-fixture-events.ndjson` and `assets/pra05-fixture-baseline-v3.json` show reversible E0/L20/D1 switching and final M30 restoration: 30 total, 20 public visible, 5 published hidden, 5 draft hidden, D1 public. Only isolated PostgreSQL `127.0.0.1:55432/pra_f4` was used.
- An initial probe used `/health` and retained a 404 in its manifests; the harness was corrected to `/api/health`, and the subsequent L20 health-check manifest records 200. Browser-required APIs were 200 throughout the accepted samples. No credentials, cookies, tokens, passwords or private content were persisted.
- This PASS is limited to PRA-05 evidence collection. It is not a performance baseline, release readiness, deployment approval, or PRA-07 budget result. Services, database and detached worktree remain active; PRA-08 is intentionally pending.

## PRA-06 current-run result (2026-08-22): BLOCKED

- Primary Owner: `senior-qa-sdet` takeover after the initial Security Worker no-op block; one bounded M30 probe was executed without persisting any credential.
- `assets/pra06-login-raw.ndjson` retains M30-01 as failed: login POST 200, both `/api/auth/me` requests 401, no HttpOnly session observed, no management API, no unique ready DOM or content-ready mark, and the negative probe could not establish an authenticated-before-logout state.
- Block Type: `TASK_BLOCK`; Severity: `High`; Problem: normal password login did not establish the isolated browser session; Impact: no valid M30 readiness sample or auth-boundary proof; Required Action: separately investigate host/CORS/cookie propagation without changing the auth contract; Recheck Condition: 10 valid M30 samples plus independent invalid-session/logout evidence are retained.
- PRA-07 is not authorized because its required M30 evidence is missing. PRA-08 must clean the currently active isolated resources.

## PRA-06 isolated CORS runtime recheck (2026-08-22): FAIL

- The recheck changed runtime configuration only: `ALLOWED_ORIGINS=http://localhost:3101`; `AUTH_BYPASS=false` and `AUTH_BYPASS_ALLOW=false`. No product source, auth/CORS code, route, schema, permission, renderer, dependency, production service, credential or main-tree file was changed.
- A fresh complete dirty-tree detached snapshot used private frontend/backend dependencies, a new PostgreSQL cluster at `127.0.0.1:55433/pra06_cors_recheck`, API `http://api.localhost:8101`, frontend `http://localhost:3101`, and synthetic-only M30 counts `30/20/5/5`. Build, migration to 025, health checks and CORS header check passed.
- A startup lifecycle failure occurred before browser navigation and is preserved separately; no login was submitted in that preflight attempt. The only normal-login form probe is raw row M30-02 in `assets/pra06-cors-recheck-20260822.raw.ndjson`.
- M30-02: login POST 200; no `admin_session` cookie observed (therefore no cookie attributes could be verified); `/api/auth/me` 401; strict `/api/admin/dashboard/summary` 401; no management list success, unique `main[data-render-state]`, or `manage:content-ready`. Exact failure_reason is retained in the raw NDJSON.
- The runtime CORS response independently contained the requested origin and credentials allowance, so the single-variable CORS setting was effective but did not produce a browser session. The no-cookie negative probe is invalid by design because normal authentication was not established.
- This is a recheck failure, not proof that auth/CORS source is defective and not authorization to modify it. The complete manifest/raw/log set is `assets/pra06-cors-recheck-20260822.manifest.json` and its sibling artifacts.
- Cleanup PASS: only the new API/frontend processes and PostgreSQL 55433 were stopped; ports 3101/8101/55433 are free; the new detached worktree is unregistered; the exact root is preserved at `/Users/limengyang/.Trash/pra06-cors-recheck-20260822-wUJZDh`. Main status inventory hash and `git diff --check` remain unchanged/PASS.

## PRA-06 cookie propagation diagnostic (2026-08-22): FAIL / BLOCKED

- Scope was one bounded normal browser login only. A fresh complete dirty-tree detached snapshot, private dependencies, PostgreSQL 55434, API `http://api.localhost:8102`, frontend `http://localhost:3102`, and synthetic M30 fixture were used. Build, migration `001 -> 025`, health and CORS preflight passed; no product source or runtime auth/CORS contract was changed.
- A duplicate startup invocation caused one separate API/frontend bind failure before the probe; it submitted no login and is preserved in `assets/pra06-cookie-diagnostic-20260822-preflight.log`. The surviving isolated listeners were healthy before the single browser probe.
- The single form-reaching normal login was `M30-cookie-diagnostic-01`: login POST `200`. CDP response evidence shows `Set-Cookie` present for `admin_session` with Path, Max-Age, HttpOnly and SameSite=Lax attribute presence; no raw value was retained. CDP exposed zero blocked-cookie reasons.
- The same browser context had no `admin_session` in its cookie jar. Both subsequent `/api/auth/me` GET requests were `401`; strict `/api/admin/dashboard/summary` was `401`; request Cookie-header presence was false for all of them. `manage:auth-submit` was present once, while management ready DOM/`manage:content-ready` were absent. The exact raw failure reason is retained in `assets/pra06-cookie-diagnostic-20260822.raw.ndjson`.
- Diagnosis: the server emitted a session cookie; the browser did not retain it, and consequently no later request sent it. The exact browser rejection reason was not exposed by the available CDP events. This is diagnosis evidence only, not proof of a source defect and not authorization to modify authentication, CORS, permissions, routes or production configuration.
- Cleanup PASS is recorded in `assets/pra06-cookie-diagnostic-20260822-cleanup.log`: temporary admin disabled, isolated session revoked, exact services stopped, ports 3102/8102/55434 free, detached worktree unregistered, recoverable snapshot at `/Users/limengyang/.Trash/pra06-cookie-diagnostic-20260822-6YOPhy`, main/production resources untouched.

## PRA-06 same-host topology diagnostic (2026-08-22): BLOCKED BEFORE BROWSER LOGIN

- This was a fresh complete dirty-tree detached snapshot with private dependencies. The only requested runtime topology change was applied: frontend `http://localhost:3103`, API bind `127.0.0.1:8103` and URL `http://localhost:8103`, PostgreSQL `55435`, `NEXT_PUBLIC_API_URL=http://localhost:8103`, `ALLOWED_ORIGINS=http://localhost:3103`, and both bypass flags false.
- Private dependencies and isolated Alembic replay to `025` passed. The production frontend build then failed before service startup because the existing production guard in `src/lib/api/config.ts` rejects a localhost API base. Exact startup evidence is `assets/pra06-same-host-diagnostic-20260822-build.log` and the separate preflight record.
- No API/frontend listener, M30 fixture, temporary admin, browser context or normal login was created after the build failure. The raw row intentionally records all login/Cookie/auth/readiness fields as `not_started/null`; it is not browser evidence and is not converted into an auth/CORS conclusion.
- No source, dependency, auth/CORS contract, production resource, deployment, commit or push was changed. We did not bypass the guard or substitute a development server because that would change an additional runtime variable.
- Cleanup PASS: PostgreSQL stopped, ports 3103/8103/55435 free, detached worktree unregistered, recoverable snapshot at `/Users/limengyang/.Trash/pra06-same-host-diagnostic-20260822-sBC76G`, main status hash unchanged, and `git diff --check` passed. PRA-06 remains blocked; no readiness or performance claim follows.

## PRA-06 same-hostname execution diagnostic (2026-08-22): BLOCKED / LIFECYCLE FAILURE

- The requested isolated topology was executed with frontend `http://api.localhost:3107`, API `http://api.localhost:8107` bound to `127.0.0.1:8107`, PostgreSQL `127.0.0.1:55439`, `NEXT_PUBLIC_API_URL=http://api.localhost:8107`, `ALLOWED_ORIGINS=http://api.localhost:3107`, `AUTH_BYPASS=false`, `AUTH_BYPASS_ALLOW=false`, and runtime `ENABLE_REGISTRATION=false` on the final start.
- A complete dirty-tree detached snapshot used private Node `v24.18.0`/npm `11.16.0` and Python `3.12.13` dependencies. `node_modules/.bin/next` existed, Alembic replay reached `025`, M30 was seeded as `30/20/5/5`, and the production build passed after the required API URL was supplied.
- Startup failures are kept separate: `app.main:app` failed in `pra06-same-hostname-exec-20260822.api.log`; `main:app` then loaded but default `ENABLE_REGISTRATION=true` failed the production lifespan in `pra06-same-hostname-exec-20260822.api-restart.log`. The corrected `ENABLE_REGISTRATION=false` process returned health 200, then exited before browser navigation without an application traceback.
- Exactly one Playwright normal-login probe was launched with process cwd equal to the snapshot. Its raw row shows navigation 200 but every API request, including login, `/api/auth/me` and strict management, failed with `ERR_CONNECTION_REFUSED`; no Set-Cookie, cookie jar, Cookie header, auth or readiness evidence exists. This is lifecycle evidence and is not counted as an auth failure.
- A persistent `nohup main:app` restart was attempted with the same runtime contract. It returned one health 200, but the first interval of the 10-second listener check found 8107 absent. No second browser probe was run; no 10× run or performance claim exists.
- Artifacts are under `assets/pra06-same-hostname-exec-20260822.*`, including manifest, raw NDJSON, startup/restart logs, browser log, exact failure reason, preflight and cleanup logs. Password, token and raw cookie values were not persisted.
- Cleanup PASS: exact services and PostgreSQL were stopped, ports 3107/8107/55439 are free, worktree registration is absent, and the recoverable root is `/Users/limengyang/.Trash/pra06-same-hostname-exec-20260822-qmNpfI`. No product source, auth/CORS contract, dependency, deployment, commit or push was changed.

## PRA-06 single-shell retry (2026-08-22): BLOCKED BEFORE BROWSER LOGIN

- The already-reviewed runner was executed exactly as requested with run id `pra06-single-shell-retry-20260822`. It exited `30` at the Alembic migration step after creating the detached snapshot and reaching the isolated database setup; API/frontend startup and the browser probe were not reached.
- The run recorded HEAD `202ea14d3362a84a491a7a8e32d2afd5d2e0bc1f`, frontend port `3110`, API port `8110`, PostgreSQL `127.0.0.1:55441/pra06_single_shell`, and both bypass flags false. The retained migration evidence is `assets/pra06-single-shell-retry-20260822.migration.log`, whose error is `Path doesn't exist: '/Users/limengyang/2025-blog-public/alembic'`.
- No current-run manifest/raw, temporary admin, session, service, or browser artifact was produced. The current-run artifacts are the retained `assets/pra06-single-shell-retry-20260822.*` logs. At final verification, all 47 JSON/NDJSON files under `assets/` parsed successfully (117 documents/records; 0 parse errors); the retry added no JSON/NDJSON.
- Post-run verification: ports 3110/8110/55441 have no listeners; main status hash remains `6de303c46f48dfd069c96161d5b6e967a54ba056fa60879093ebd3ef21ea2476`; `git diff --check` passes. Cleanup is partial rather than PASS: the retry worktree registration remains as `/private/tmp/pra06-single-shell-retry-20260822-siiSYs/worktree` with `prunable` status, and no matching root was found in `/private/tmp` or `/Users/limengyang/.Trash`. No prune or deletion was performed.
- This is migration/lifecycle evidence only. It does not establish auth, CORS, Cookie, management readiness, performance, or production readiness, and it authorizes no source, deployment, commit, or push change.

## PRA-06 corrected single-shell retry2 (2026-08-22): BLOCKED BEFORE BROWSER LOGIN / HARNESS LIFECYCLE FAILURE

- The corrected runner was executed exactly as requested with run id `pra06-single-shell-retry2-20260822`. It exited `0` after cleanup and recorded `probe_exit=1`; unlike the prior retry, the Alembic command ran from `SNAPSHOT/backend` and completed `001 -> 025`.
- Isolated build/runtime evidence passed: production build, API/frontend startup, `/api/health`, host health and CORS preflight. The run used frontend `http://api.localhost:3110`, API `http://api.localhost:8110`, PostgreSQL `127.0.0.1:55441/pra06_single_shell`, `AUTH_BYPASS=false`, `AUTH_BYPASS_ALLOW=false`, and `product_source_changed=false`.
- The probe failed before its first manifest write at `git rev-parse HEAD` because the rsync-created snapshot has no usable `.git` metadata. Exact evidence is `assets/pra06-single-shell-retry2-20260822.log`; only the runner/log/build/runtime artifacts exist under the run prefix. The run therefore produced no manifest/raw/parsed browser evidence, temporary admin, session or login attempt, and cannot be classified as an auth/CORS failure.
- Cleanup is partial: the runner reported zero listeners on 3110/8110/55441 and the main status inventory hash remained `6de303c46f48dfd069c96161d5b6e967a54ba056fa60879093ebd3ef21ea2476`. The exact root is recoverable at `/Users/limengyang/.Trash/pra06-single-shell-retry2-20260822-TADkxk`, while `git worktree list --porcelain` still shows its detached worktree as `prunable`; no prune/delete was performed.
- Audit decision: this is a runner/probe asset-generation lifecycle blocker. It does not authorize source, auth/CORS, dependency, production, deployment, commit or push changes; PRA-06 remains blocked and PRA-07 remains unauthorized.

## PRA-08 current-run result (2026-08-22): PASS

- Pre-cleanup evidence is retained in `assets/pra08-pre-cleanup-20260822.txt` without password, cookie, token or credential values.
- The temporary admin was disabled and 3 isolated sessions were revoked/expired. Frontend PID 84751, API PID 84872 and PostgreSQL PID 84161 were stopped; no run-scoped browser process remained.
- The exact detached worktree was removed from Git registration and the exact isolated root was moved to `/Users/limengyang/.Trash/pra04-20260822-auWgUg`. No production or main-tree process was touched.
- Final read-only checks passed: ports 3000/3100/8100/55432 have no listeners; only the four pre-existing worktrees remain; the temp root is absent; PRA JSON/NDJSON artifacts parse; and `git diff --check` passes.
- Overall current-run decision remains `BLOCKED` because PRA-06 is blocked and PRA-07 was not authorized. Cleanup PASS does not change that gate.

## Independent PRA-06 corrected harness confirmation (2026-08-22): PASS

### Scope and boundary

The verifier read the repository `AGENTS.md`, current PRA-06 workflow documents, the cookie diagnostic harness, the single-shell runner and prior raw evidence. It executed exactly one fresh isolated run with `PRA_RUN_ID=pra06-noise-confirm-20260822`; no 10× sampler, product source, auth/CORS, dependency, deployment, commit or push action was performed.

### Harness assertions

- The Playwright query is `context.cookies(`${API_BASE}/api/auth/me`)`, matching the session cookie's `/api` Path rather than querying the API origin root.
- Raw `console_errors` and `failed_requests` remain in the NDJSON record. The harness additionally persists `expected_*` and `unexpected_*` partitions; it does not replace the raw event arrays.
- The accepted console shape is the exact pre-login-style `401 (Unauthorized)` console message. The accepted failed-request shapes are frontend `/notes|/blog` `net::ERR_ABORTED` link-prefetch targets and Google Analytics `/g/collect` `net::ERR_ABORTED`. The fresh run had no unexpected event in either partition.

### Fresh evidence

The manifest is `status=pass`, `valid=true`, `normal_login_attempts=1`, and records `auth_bypass=false`, `auth_bypass_allow=false`, `ten_sample_run=false`, `performance_baseline=false`, and `production_readiness_claim=false`. The raw record shows login `200`, Set-Cookie attribute presence for `admin_session`, cookie jar `admin_session` with `path=/api` and `http_only=true`, strict management `200`, authenticated Cookie header presence, one ready main, and one `manage:content-ready` mark. Raw noise counts are preserved as console `1` expected / `0` unexpected and failed requests `27` expected / `0` unexpected (`26` frontend plus `1` Google Analytics).

### Independent cleanup and integrity

The runner recorded probe exit `0`, ports 3110/8110/55441 at zero listeners after cleanup, and unchanged main status hash `6de303c46f48dfd069c96161d5b6e967a54ba056fa60879093ebd3ef21ea2476`. Independent checks parsed all 38 JSON and 21 NDJSON assets, passed `git diff --check`, found no noise-run worktree registration or temp root, and found no new-run status entry because the workflow assets are ignored/untracked in this dirty checkout. No product source/auth/CORS/dependency file was changed by this verification.

Decision: `PASS` for the corrected PRA-06 single-probe harness and its one fresh isolated confirmation. This does not make the broader F4 gate PASS, authorize PRA-07, establish a performance baseline, or authorize production readiness/deployment.

## PRA-06 M30 batch collection (2026-08-22): PASS

- The Primary Owner executed the reviewed single-shell runner with `PRA_M30_COUNT=10` and `PRA_M30_MAX_ATTEMPTS=12`. The isolated runtime used frontend `http://api.localhost:3110`, API `http://api.localhost:8110`, PostgreSQL `127.0.0.1:55441/pra06_single_shell`, private dependencies, a detached dirty-tree snapshot, `ENV=production`, `ENABLE_REGISTRATION=false`, `AUTH_BYPASS=false`, and `AUTH_BYPASS_ALLOW=false`. No product source/auth/CORS/dependency/route/schema/renderer/production change was made.
- `assets/pra06-m30-batch-final-20260822.manifest.json` is the authoritative batch manifest. It lists `M30-01` through `M30-10`, exact raw/manifest paths, `attempts=10`, `valid_count=10`, `failed_count=0`, `failure_rate=0`, and no p50/p90 fields populated. All ten raw files are `valid=true`, browser-cold/server-warm, and persisted before the next child attempt.
- The raw contract is present per sample: navigation timing fields, `lcp`, API ResourceTiming plus status-bearing login/me/strict-management events, exact readiness marks, DOM selector count/main count/state/row count, console/page errors, complete failed requests with expected/unexpected classification, unexpected navigation/dialog/download arrays, and explicit `failure_reason`. No password, token, raw cookie value or content body was persisted.
- `assets/pra06-m30-negative-final-20260822-negative.json` independently proves the two required negative boundaries: no-cookie strict management and `/api/auth/me` both `401`; after authenticated login, logout `200`, subsequent `/api/auth/me` and strict management `401`, and no remaining session cookie. The first two harness failures are preserved, with their corrected causes, in the batch recheck history and were not silently deleted.
- Raw-status/classification distinction: the first two preserved no-cookie probe records show the expected HTTP `401/401` statuses while reporting `valid=false` because the harness checked nonexistent `*_status` fields; this is an evidence-classification bug, not a server authorization failure. The intermediate recheck already records `logout_boundary.valid=true`; the final corrected raw records `no_cookie_boundary.valid=true` and `logout_boundary.valid=true`.
- Cleanup evidence: `pra06-m30-batch-20260822.runner.log`, `pra06-m30-negative-final-20260822.runner.log`, and `pra06-m30-negative-final-20260822.cleanup.log` report zero listeners on `3110/8110/55441`; final worktree listing has only four pre-existing worktrees; main status hash is unchanged; `git diff --check` and static asset checks pass.
- Independent Verifier Hegel performed a read-only audit of all ten raw records, the final negative boundary, preserved historical failures, cleanup provenance, current ports/worktrees/status hash and `git diff --check`: PASS. The negative-only runner's `probe_exit=2` is retained as bookkeeping because its M30 sample counter was zero; the final negative raw is `valid=true` and the cleanup log is derived line-for-line from that runner log.
- Gate decision: `PASS` for PRA-06. PRA-07 is authorized only for its next serial raw-data aggregation phase; no performance baseline, F4 PASS, production readiness or deployment claim follows until that phase and its independent review complete.
