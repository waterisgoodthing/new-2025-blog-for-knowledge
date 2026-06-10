# Tasks

## Approval Required

Implementation was approved in conversation and completed on 2026-06-09.

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
