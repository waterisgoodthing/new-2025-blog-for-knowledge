# Validation — System Freeze & Acceptance Sprint

## SFA-03 Complete Local Acceptance

Validation date: 2026-07-09.

Repository state note: the worktree already contained many unrelated modified and untracked files before this sprint. This sprint did not revert or repair those changes.

## Command Results

| Check | Command | Result |
| --- | --- | --- |
| Backend tests | `cd backend && .venv/bin/python -m pytest tests/ -ra` | Passed: `226 passed, 2 warnings in 3.86s`. |
| Alembic current | `cd backend && PYTHONPATH=. .venv/bin/alembic current` | Passed: `018 (head)`. |
| Frontend typecheck | `npx tsc --noEmit` | Passed, no output. |
| Frontend build | `npm run build` | Passed. Next.js generated 37 app routes. Warnings: stale `baseline-browser-mapping` data and Node `module.register()` deprecation. |
| Diff whitespace | `git diff --check` | Passed, no output. |
| Lint | `npm run lint` | Not available. `package.json` has no `lint` script. |

Backend pytest warnings:

- `backend/tests/test_ai_gateway.py::LogWriteFailureTest::test_log_write_failure_does_not_block`
- `backend/tests/test_ai_gateway.py::LogWriteFailureTest::test_write_call_log_catches_exception`

Both warnings are `RuntimeWarning: coroutine 'AsyncMockMixin._execute_mock_call' was never awaited` at `backend/app/services/ai_gateway.py:98` in mock-based tests. They do not fail the suite but should remain a P2 test hygiene item.

## Local Browser Setup

Existing local services were already listening on:

- `127.0.0.1:8000`
- `*:2025`

The existing `2025` frontend used `https://public-api.limengyang.me`, so it was not accepted as complete local proof.

An isolated local acceptance pair was started:

```text
backend:  http://127.0.0.1:18000
frontend: http://127.0.0.1:3026
```

The first isolated backend attempt used JSON-style `ALLOWED_ORIGINS` and returned CORS preflight `400`. The backend expects comma-separated origins, so it was restarted with:

```text
ALLOWED_ORIGINS=http://127.0.0.1:3026,http://localhost:3026
```

After that restart, browser API requests to the local backend succeeded.

No `AUTH_BYPASS` proof was used.

## Anonymous Public Pages

Tested with browser against `http://127.0.0.1:3026` and local backend `http://127.0.0.1:18000`.

| Route | Result | API observations |
| --- | --- | --- |
| `/` | Loaded public home content. | Public APIs returned 200; `/api/auth/me` returned 401 for anonymous session; no admin/capture/review/attachment/AI data API request observed. |
| `/blog` | Loaded public blog list with one published article. | Public APIs returned 200; `/api/auth/me` returned 401; no admin/capture/review/attachment/AI data API request observed. |
| `/notes` | Loaded public notes list. | Public notes API returned 200; `/api/auth/me` returned 401; no admin/capture/review/attachment/AI data API request observed. `/api/folders` returned 200 and is recorded as a deferred boundary review item. |

## Anonymous Management Access

Routes checked:

- `/manage`
- `/manage/capture`
- `/manage/ai`
- `/manage/ai/runs`
- `/manage/review`
- `/manage/mistakes`
- `/manage/questions`
- `/manage/attachments`

Result:

- All routes showed the `/manage` login page or redirected back to `/manage`.
- Anonymous API calls observed were limited to public site settings/music, `/api/auth/me` returning 401, and passkey status.
- No management data was rendered to anonymous users.
- No admin Run/capture/review/mistake/question/attachment data API returned to anonymous users in browser validation.

## Authenticated Management Pages

A temporary admin account was created via:

```text
cd backend && .venv/bin/python -m app.cli create-temp-admin --username sfa-temp-admin
```

The browser logged in through the password form. `AUTH_BYPASS` was not used.

Routes checked after login:

| Route | Result |
| --- | --- |
| `/manage` | Loaded legacy management panel with workspace handoff banner and admin identity. |
| `/manage/capture` | Loaded Batch 8 image capture page. `/api/admin/captures` and subjects returned 200. |
| `/manage/ai` | Loaded AI console, Run audit entry, provider status, health snapshot, usage/cost snapshot, call stats, and call log sections. |
| `/manage/ai/runs` | Loaded AI Run audit table with pagination and 17 local Runs. `/api/admin/ai/runs` returned 200. |
| `/manage/review` | Loaded review queue. `/api/admin/review/items?due=true` returned 200. |
| `/manage/mistakes` | Loaded private mistakes page, draft form, pending drafts, and formal mistakes. Admin APIs returned 200. |
| `/manage/questions` | Loaded formal question bank. `/api/admin/questions?status=active` returned 200. |
| `/manage/attachments` | Loaded private attachments page. `/api/admin/attachments?status=active` returned 200. |

## Sensitive Field Checks

Browser visible text checks:

- `/manage/ai`: did not show `api_key`, `authorization`, `storage_key`, `input_summary`, `replay_input`, `cookie`, `secret`, or `bearer`. It did show explanatory text `token usage`, which is expected for the usage/cost panel.
- `/manage/ai/runs`: did not show `api_key`, `authorization`, `storage_key`, `input_summary`, `replay_input`, `cookie`, `secret`, `bearer`, or `token`.
- `/manage/attachments`: did not show `storage_key`; it describes opaque storage key conceptually but does not render actual keys.

Direct authenticated API response scan:

| Endpoint | Status | Sensitive-field scan |
| --- | --- | --- |
| `/api/ai/provider-status` | 200 | No hits for `api_key`, `authorization`, `storage_key`, `input_summary`, `replay_input`, `cookie`, `secret`, `bearer`, `token`. |
| `/api/ai/call-logs?limit=20&offset=0` | 200 | No hits for banned sensitive fields. |
| `/api/ai/call-logs/usage-cost` | 200 | Hit `token` only in expected `input_tokens` / `output_tokens` usage fields; no credential token value. |
| `/api/ai/provider-health-snapshot` | 200 | No hits for banned sensitive fields. |
| `/api/admin/ai/runs?limit=20&offset=0` | 200 | No hits for banned sensitive fields, including `replay_input`. |
| `/api/admin/attachments?status=active` | 200 | No hits for `storage_key` or other banned sensitive fields. |

## Stream Endpoint Mainline Check

Static search:

```text
rg -n "analyzeMistakeStream|analyzeTextStream|/api/ai/analyze-stream|/api/ai/analyze-text-stream|EventSource|text/event-stream" src/app src/components src/hooks src/lib -g '!src/lib/api/ai.ts'
```

Result: no matches.

Interpretation:

- Formal app surfaces do not call the old stream wrappers.
- Old wrappers remain in `src/lib/api/ai.ts`.
- Old backend endpoints remain in `backend/app/routers/ai.py` with `deprecated=True`.
- This confirms old stream endpoints are compatibility-only and not the formal generation mainline.

## SFA-03 Conclusion

Complete local acceptance passed with notes:

- Commands passed except lint, which is unavailable.
- Browser acceptance passed using isolated local frontend/backend ports.
- Public pages do not request management data APIs; `/api/folders` on `/notes` remains a deferred boundary review item.
- Management pages are protected from anonymous access and work after normal password login.
- AI and Run surfaces did not expose prohibited sensitive fields in visible UI or scanned API responses.
- Deprecated stream endpoints are not the formal generation mainline.

No P0 blocker was found in SFA-03.

## SFA-06 Fresh Setup Experiment

Validation date: 2026-07-09.

Isolation path:

```text
/tmp/2025-blog-public-fresh-setup
```

Isolation method:

- Copied the current working tree into the isolated path with runtime/build artifacts excluded.
- Excluded `.git`, `node_modules`, `.next`, `.open-next`, `.output`, `backend/.venv`, caches, `.env`, `.env.local`, `.env.production`, and `backend/.env`.
- This was not a reuse of the current running services or current virtual environment.

Tool versions recorded in the fresh setup:

| Tool | Version |
| --- | --- |
| Node.js | `v26.0.0` |
| npm | `11.12.1` |
| Python used for passing backend install | `Python 3.12.13` |
| PostgreSQL client | `psql (PostgreSQL) 16.14 (Homebrew)` |

Dependency installation:

| Check | Result |
| --- | --- |
| `npm ci` | Passed. npm reported `5 vulnerabilities (3 moderate, 2 high)` and one deprecated transitive package warning for `whatwg-encoding@3.1.1`. |
| Backend install with default `python3` | Failed because local `python3` is `Python 3.14.5`; `pydantic-core` / PyO3 does not support Python 3.14 in this dependency set. |
| Backend install with `/opt/homebrew/bin/python3.12` | Passed after recreating `backend/.venv`. |

Environment and setup findings:

- Root `.env.example` is sufficient for local dev server startup, but production `npm run build` rejects `NEXT_PUBLIC_API_URL=http://localhost:8000`.
- `backend/.env.example` documents `DATABASE_URL`, `JWT_SECRET_KEY`, comma-separated `ALLOWED_ORIGINS`, AI keys, `AUTH_BYPASS=false`, WebAuthn, and `IMAGE_BASE_URL`.
- Manual values were required for the fresh experiment: real local `DATABASE_URL`, non-template `JWT_SECRET_KEY`, port-specific `ALLOWED_ORIGINS`, frontend `NEXT_PUBLIC_API_URL`, frontend `NEXT_PUBLIC_IMAGE_BASE_URL`, and local WebAuthn origin.
- `ALLOWED_ORIGINS` must be comma-separated. JSON-style arrays are not accepted by the current settings parser.
- README recommends Python 3.12 but the setup script currently accepts any Python 3 command; on this machine that selects Python 3.14 and causes backend dependency install failure.
- Redis was not required.
- Real provider keys were not required for application startup, login, `/manage`, `/manage/ai`, or `/manage/capture`. No real provider probe was run.

Database initialization:

```text
dropdb --if-exists sfa_fresh_acceptance
createdb sfa_fresh_acceptance
cd /tmp/2025-blog-public-fresh-setup/backend
PYTHONPATH=. .venv/bin/alembic upgrade head
```

Result: passed from an empty PostgreSQL database through migration `018`.

Fresh backend/frontend startup:

| Service | Command shape | Result |
| --- | --- | --- |
| Backend | `.venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 18030` | Started successfully. |
| Frontend | `npx next dev --turbopack -p 3030` with local API env overrides | Started successfully. |

Admin creation/login:

- Created a temporary admin in the fresh database via `cd backend && .venv/bin/python -m app.cli create-temp-admin --username sfa-fresh-admin`.
- Browser-context login against `http://127.0.0.1:18030/api/auth/login` returned 200.
- Browser-context `/api/auth/me` returned 200 for the fresh admin session.
- `AUTH_BYPASS` was not used.

Fresh browser page checks:

| Route | Result |
| --- | --- |
| `/manage` | Loaded authenticated management page with `sfa-fresh-admin`, empty content state, and workspace handoff banner. |
| `/manage/ai` | Loaded AI console, provider/routing/usage/health read-only sections, empty call logs, and Run audit entry. |
| `/manage/capture` | Loaded image capture page and empty capture state. |

Fresh smoke tests:

```text
cd /tmp/2025-blog-public-fresh-setup/backend
.venv/bin/python -m pytest tests/test_temp_admin_bootstrap.py tests/test_ai_routing_policy.py tests/test_ai_provider_health_snapshot.py -q
```

Result: passed, `10 passed in 1.50s`.

Fresh frontend build:

| Command | Result |
| --- | --- |
| `npm run build` with local `NEXT_PUBLIC_API_URL=http://127.0.0.1:18030` | Failed. Error: `NEXT_PUBLIC_API_URL must be set to a non-localhost URL in production` while collecting `/sitemap.xml` and `/rss.xml`. |
| `NEXT_PUBLIC_API_URL=https://public-api.limengyang.me NEXT_PUBLIC_IMAGE_BASE_URL=https://public-api.limengyang.me npm run build` | Passed. Next.js generated 37 app routes. Warnings matched SFA-03 build warnings: stale `baseline-browser-mapping` data and Node `module.register()` deprecation. |

## Fresh Setup Report

Blockers:

- P1 setup blocker: default `python3` can be Python 3.14 on this machine, but the backend dependency set requires Python 3.12 or another supported Python version.
- P1 setup/documentation blocker: production `npm run build` cannot use the localhost default from `.env.example`; a non-localhost production API URL must be documented as required for production build.

Manual steps required:

- Choose Python 3.12 explicitly when creating `backend/.venv`.
- Create a PostgreSQL database and set `DATABASE_URL`.
- Replace the template `JWT_SECRET_KEY`.
- Set `ALLOWED_ORIGINS` as a comma-separated list matching the chosen frontend port.
- Set `NEXT_PUBLIC_API_URL` and `NEXT_PUBLIC_IMAGE_BASE_URL` differently for local dev versus production build.
- Create an admin with the CLI before management login.

Documentation gaps:

- README/setup should fail or warn on unsupported Python versions instead of accepting any `python3`.
- README should call out that localhost API URLs are valid for dev server startup but not for production `npm run build`.
- README should give an explicit local-build versus production-build environment example.
- `.env.example` already says production must use non-localhost API URL, but the quick-start path does not make this operationally obvious.

Fresh setup conclusion:

- From-zero local dev startup is possible with manual environment setup and Python 3.12.
- From-zero production build is possible only after replacing localhost API URLs with production-shaped non-localhost URLs.
- No Redis or real provider key is required to boot and access the audited management pages.
- Because the default Python command and production-build environment behavior can block a new operator, the fresh setup is **not frictionless** and should be treated as conditionally passable, not fully self-service.
