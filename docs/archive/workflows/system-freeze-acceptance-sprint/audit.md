# Audit — Codex Quality Review

## Scope

Reviewed:

- `backend/app`
- `backend/tests`
- `src/app`
- `src/lib`
- `docs/workflows`
- Alembic migrations
- README / setup documentation

This is a read-only quality audit. No code fixes were applied.

## P0 Blockers

None found.

No evidence was found that anonymous users can access `/manage/*` workspace data, that AI Run acceptance writes formal entities, that formal generation still depends on old stream endpoints, or that sensitive AI fields are exposed in the checked AI management pages/API responses.

## P1 High-Priority Issues

### P1-01 Public pages still expose management entry points to anonymous users

Evidence:

- Browser validation showed public `/`, `/blog`, and `/notes` render a visible `管理` entry.
- `src/components/nav-card.tsx:211-220` renders a desktop `管理` link to `/manage/dashboard`.
- `src/components/mobile-nav.tsx:29-31` includes `管理` in the mobile more menu.
- `src/components/empty-state.tsx:17-23` defaults `no-content` to `新建笔记` -> `/manage/dashboard`; browser validation saw `/blog` empty state rendering `新建笔记`.
- `src/app/notes/page.tsx:168-172` returns create actions to `/manage/capture` or `/manage/dashboard`.

Impact:

- This does not expose management data because `/manage/*` is AuthGate-protected.
- It does blur the public-read/admin-write boundary and creates public UI affordances for admin actions.

Recommendation:

- Hide management entry/action links from anonymous public pages, or deliberately document the visible login entry as a product decision.
- Keep backend permissions unchanged.

### P1-02 Fresh local alternate-port acceptance needs manual CORS knowledge

Evidence:

- Isolated local frontend on `3025`/`3026` initially received CORS preflight `400` from the local backend.
- `backend/app/config.py:10` defines `ALLOWED_ORIGINS` as a comma-separated string.
- `backend/main.py:50-52` splits that string on commas.
- A JSON-style env value failed; comma-separated `ALLOWED_ORIGINS=http://127.0.0.1:3026,http://localhost:3026` worked.

Impact:

- Standard `2025` + `8000` local setup should work if env files are correct.
- Fresh or alternate-port setup is easy to misconfigure, making local acceptance look broken.

Recommendation:

- Improve setup docs / setup script messaging around comma-separated `ALLOWED_ORIGINS`.
- Treat as setup hardening, not a business-code blocker.

## P2 Deferred Issues

### P2-01 `/api/folders` anonymous boundary needs product/security decision

Evidence:

- Browser validation of anonymous `/notes` showed `GET /api/folders` returning 200.
- `backend/app/routers/folders.py:78-84` exposes `list_folders` without `get_current_admin`.
- Mutations are protected by `get_current_admin`, for example `backend/app/routers/folders.py:87-94`.

Impact:

- Public folder metadata and note counts are visible anonymously.
- This may be intended for public note navigation, but it is not explicitly frozen in the final boundary.

Recommendation:

- Decide whether folder tree metadata is public.
- If public, document allowed fields and ensure hidden/private counts are not leaked.
- If admin-only, update `/notes` to degrade without folder data.

### P2-02 Backend tests pass but retain two async mock warnings

Evidence:

- `pytest tests/ -ra` passed with `226 passed, 2 warnings`.
- Warnings point to `backend/app/services/ai_gateway.py:98` under `backend/tests/test_ai_gateway.py`.

Impact:

- Not blocking, but warnings can hide future async mistakes if they accumulate.

Recommendation:

- Clean the mock shape or run `test_ai_gateway.py` with warnings-as-errors in a test hygiene batch.

### P2-03 No project lint script exists

Evidence:

- `package.json` has scripts for `dev`, `build`, `check`, `check:project`, `init`, `setup`, but no `lint`.

Impact:

- TypeScript/build catch many issues, but there is no consistent lint gate.

Recommendation:

- Add or explicitly reject a lint policy in a tooling cleanup batch.

### P2-04 Complete provider token streaming remains intentionally deferred

Evidence:

- `backend/app/routers/ai.py:153-193` keeps deprecated stream endpoints.
- Narrow scan found no formal app-surface usage outside `src/lib/api/ai.ts`.
- `src/lib/api/ai.ts` still exports compatibility stream wrappers.

Impact:

- Current formal generation is non-streaming and auditable.
- Future callers could still use compatibility wrappers unless deprecated/removed later.

Recommendation:

- Keep as deferred cleanup unless a real streaming product need returns.

### P2-05 Fresh setup likely depends on external PostgreSQL and manual env choices

Evidence:

- `backend/.env.example` points to `postgresql+asyncpg://user:password@localhost:5432/blog_db`.
- README says PostgreSQL must be configured.
- No Redis requirement was found for the current app.

Impact:

- A clone cannot become fully usable without PostgreSQL credentials and DB creation.

Recommendation:

- Confirm in SFA-06 and improve setup docs if needed.

## P3 Cleanup Items

- Legacy write routes still exist as pages but are AuthGate-protected or redirected by route strategy; dead code cleanup can be deferred.
- `src/lib/api/ai.ts` stream wrappers can be marked more visibly deprecated in TypeScript comments later.
- Public text can better distinguish public content navigation from admin login affordances.
- Build warning: `baseline-browser-mapping` data is stale.
- Build warning: Node `DEP0205 module.register()` deprecation from tooling.

## False Positives / Non-Issues

- `/manage/ai` visible text includes `token usage`; direct API scan showed this is usage/cost observability (`input_tokens` / `output_tokens`), not credential leakage.
- Anonymous `/api/auth/me` 401 on public pages is a session check, not management data exposure.
- `ai_runs.output_data` exists by design as business audit output. Usage/cost/health aggregation code reviewed in `backend/app/services/ai_log_service.py` describes `ai_call_logs` as the source and does not rely on `ai_runs.output_data`.
- AI Run decision service records accept/reject state and audit metadata only; `backend/app/services/ai_run_service.py:177-223` does not call question/mistake/review write services.
- Workspace `/manage/*` layout is protected by `AuthGate` at `src/app/manage/(workspace)/layout.tsx:1-20`.
- `/write-note/[slug]`, `/write-mistake/[slug]`, and `/mistakes/review` are AuthGate-wrapped in current source.

## Suggested Repair Order

1. Decide public management entry policy and hide/relabel anonymous public admin affordances if not intentional.
2. Review `/api/folders` anonymous response contract.
3. Improve local setup/CORS documentation and setup script checks.
4. Clean AI Gateway AsyncMock warnings.
5. Add a lightweight browser smoke regression suite for public/admin route boundaries.
6. Defer stream wrapper removal until compatibility risk is acceptable.

## Daily-Use Recommendation From Audit Alone

Audit alone suggests **B. Can enter real daily use with conditions**:

- No P0 blockers were found.
- P1 items are boundary clarity/setup hardening, not data exposure.
- Keep real daily use admin-only until public admin affordances and `/api/folders` boundary are explicitly accepted or cleaned up.
