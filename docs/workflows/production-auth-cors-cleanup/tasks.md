# Tasks

## Approval Required

Implementation was approved in conversation and completed on 2026-06-09.

The 2026-06-12 production login/API incident is a new operational phase. Do not execute the Phase 6 repair tasks until the user explicitly approves this updated task list.

## Phase 1: Reproduce And Classify

- [x] **P0-01** Record the pasted production console symptoms in validation notes.
  - Domain: shared infrastructure.
  - Completion standard: `validation.md` lists each symptom and expected classification.
  - Completed: Initial evidence and classification recorded in `validation.md`.

- [x] **P0-02** Confirm current route/component sources for anonymous admin calls.
  - Domain: notes/auth.
  - Completion standard: identify source files for weekly summary, folder/tag mutations, and GitHub sync.
  - Completed: Source mapping recorded in `validation.md`.

## Phase 2: Notes Public/Admin Gates

- [x] **P0-03** Gate `WeeklySummaryCard` behind `isAdmin`.
  - Domain: notes.
  - Completion standard: logged-out `/notes` no longer calls `/api/ai/weekly-summary`; admin `/notes` still shows the drawer in dashboard context.
  - Completed: `/notes` renders `WeeklySummaryCard` only when `isAdmin && showDashboard`; public empty states no longer expose create links.

- [x] **P0-04** Gate `KnowledgeSidebar` mutation controls by admin state.
  - Domain: notes.
  - Completion standard: logged-out users can filter by folder/tag but cannot create, reorder, rename, delete, or drag/drop mutate folders/tags.
  - Completed: `KnowledgeSidebar` now defaults to read-only and exposes mutation controls only when `canManage` is true. `/notes` passes `isAdmin`; `/manage` passes `canManage`.

- [x] **P0-05** Confirm notes content context menu remains read-only when logged out.
  - Domain: notes.
  - Completion standard: logged-out right-click only shows safe actions such as open/copy link.
  - Completed: verified current source keeps edit/move/delete inside the `isAdmin` branch.

## Phase 3: Sync And API Host

- [x] **P1-01** Trace and gate the `GitHub sync failed` source.
  - Domain: manage/sync or home/settings.
  - Completion standard: no GitHub sync call runs from a public page or logged-out route.
  - Completed: visible legacy settings entries and shortcut now route to `/manage`; GitHub sync remains only in the page-settings save flow hosted inside the management console.

- [x] **P1-02** Verify production public API host selection.
  - Domain: shared infrastructure.
  - Completion standard: docs record whether `NEXT_PUBLIC_API_URL` is `https://public-api.limengyang.me`; no public page call should require Cloudflare Access.
  - Completed: `.env.production` uses `https://public-api.limengyang.me`; evidence recorded in `validation.md`.

## Phase 4: Admin Entry Discoverability

- [x] **P0-06** Add a clear administrator console entry to desktop navigation.
  - Domain: shared navigation/manage.
  - Completion standard: desktop users can discover `/manage` from the normal navigation without knowing the URL.
  - Completed: desktop vertical navigation and home navigation card now expose `管理面板` linking to `/manage`.

- [x] **P0-07** Add a clear administrator console entry to mobile navigation.
  - Domain: shared navigation/manage.
  - Completion standard: mobile users can discover `/manage` from the normal navigation.
  - Completed: mobile "更多" navigation includes `管理面板`.

- [x] **P0-08** Reconcile the old "网站设置" entry with the new manage console.
  - Domain: home/manage.
  - Completion standard: old settings affordance either links to `/manage?tab=settings` or is clearly secondary to `管理面板`.
  - Completed: visible old settings affordances and the keyboard shortcut now route to the management console instead of opening the public legacy settings dialog, and the `/manage?tab=settings` destination remains available after authenticated admin login.

## Phase 5: Validation

- [x] **P0-09** Run TypeScript validation.
  - Command: `npx tsc --noEmit`.
  - Completed: pass on 2026-06-09.

- [x] **P0-10** Run browser validation for logged-out `/notes`.
  - Completion standard: no visible admin actions; no automatic admin AI calls; no folder mutation requests unless logged-in admin intentionally acts.
  - Completed: fresh dev server at `http://localhost:3026/notes` showed no weekly summary, AI suggestions, write-note action, create-folder action, or reorder controls; browser console had no errors.

- [x] **P0-11** Run browser validation for admin console discoverability.
  - Completion standard: desktop and mobile navigation both expose a clear path to `/manage`.
  - Completed: desktop collapsed navigation shows `管理` linking to `/manage`; mobile `更多` menu shows `管理面板`; clicking the desktop entry reaches the management login page.

- [x] **P0-12** Record results in `validation.md`.
  - Completed: static and browser validation evidence recorded in `validation.md`.

- [x] **P0-13** Make the desktop admin entry readable without hover.
  - Domain: shared navigation/manage.
  - Completion standard: the collapsed desktop side navigation shows a readable "管理" label for `/manage`, and the active state is visible on `/manage`.
  - Completed: collapsed desktop side navigation now shows a persistent "管理" label and applies active styling when the current route starts with `/manage`.

## Phase 6: 2026-06-12 Public API Login Incident

- [x] **P0-14** Record current public API and private API failure evidence.
  - Domain: shared infrastructure/auth/music.
  - Completion standard: `validation.md` contains fresh HTTP evidence for `public-api` health/CORS, passkey status, music playlist, and private `api` Access redirect.
  - Completed: 2026-06-12. `validation.md` records `public-api` `530 / 1033`, failed CORS-adjacent checks, and private `api` Cloudflare Access redirect evidence.

- [x] **P0-15** Check local backend and tunnel service state without changing code.
  - Domain: shared infrastructure.
  - Completion standard: record whether backend health is reachable locally, whether `cloudflared tunnel info blog-tunnel` shows active connectors, and whether launch agents for backend/tunnel are running.
  - Completed: 2026-06-12. Local backend returned `200 {"status":"ok","db":"ok"}` and launch agents were listed, but `cloudflared tunnel info blog-tunnel` reported no active connection; config also showed `protocol: http2`.

- [x] **P0-16** Repair production API reachability if service state confirms tunnel/backend drift.
  - Domain: shared infrastructure.
  - Completion standard: restart only the affected service(s), then `https://public-api.limengyang.me/api/health` returns `200` JSON and no longer returns Cloudflare `1033`.
  - Completed: 2026-06-12. Restored Clash Verge real DNS resolution for `argotunnel.com`, kept `cloudflared` on `quic`, restarted `com.blog.tunnel`, confirmed active connector and `public-api` health `200`.

- [x] **P0-17** Verify CORS and login-adjacent endpoints after repair.
  - Domain: auth/music/shared infrastructure.
  - Completion standard: `OPTIONS /api/music/playlist`, `GET /api/auth/passkey/status`, and a representative public read endpoint include expected CORS behavior from origin `https://blog.limengyang.me`.
  - Completed: 2026-06-12. Music preflight, passkey status, music playlist, and subjects all returned `HTTP 200` with expected CORS headers from `https://blog.limengyang.me`.

- [x] **P0-18** Verify the deployed frontend does not still call the private Access host for routine public/login data.
  - Domain: shared infrastructure/frontend deployment.
  - Completion standard: inspect deployed assets or browser network evidence and record whether `https://api.limengyang.me` remains only an intentional private host.
  - Completed: 2026-06-12. Downloaded deployed HTML/chunks for home, notes, and manage; chunks contain `https://public-api.limengyang.me` and no standalone `https://api.limengyang.me`.

- [x] **P0-19** Run a `/manage` login smoke check and record the result.
  - Domain: auth/manage.
  - Completion standard: fresh browser/login verification shows either successful login or a remaining auth-specific error after API reachability is restored.
  - Completed: 2026-06-12. Headless Chrome loaded live `/manage`; login UI and Passkey button rendered; `auth/me` returned expected anonymous `401`; `site-settings`, `music/playlist`, and `passkey/status` returned `200` from `public-api` with CORS. Full credential assertion was not executed because it requires user Passkey/password confirmation.
