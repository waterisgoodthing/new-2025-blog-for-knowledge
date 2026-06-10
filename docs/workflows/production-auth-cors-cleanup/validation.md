# Validation

Implementation completed on 2026-06-09. Final validation evidence is recorded below.

## Initial Evidence From User Paste

- `GET /api/auth/me` returns `401`.
- `GET /api/ai/weekly-summary` returns `401`.
- `DELETE /api/folders/<id>` returns `401`.
- GitHub sync reports `{"detail":"Not authenticated"}`.
- `https://api.limengyang.me/api/subjects` redirects to Cloudflare Access login and then fails browser CORS from `https://blog.limengyang.me`.

## Current Classification

- `/api/auth/me -> 401`: expected for logged-out optional admin detection, but should be quiet.
- `/api/ai/weekly-summary -> 401`: frontend gate leak; weekly summary is admin-only but rendered on public `/notes`.
- `/api/folders/<id> -> 401`: frontend gate leak if folder mutation controls are visible or clickable while logged out.
- GitHub sync `401`: likely frontend gate leak unless triggered from an intentional logged-out write/save page.
- Cloudflare Access CORS: deployment/API host mismatch for public reads; public pages should not call Access-protected `api.limengyang.me`.
- Admin console discoverability: `/manage` exists, but current normal navigation primarily exposes old "网站设置" controls, so users can miss the actual management console.

## Source Mapping Before Fix

- `src/app/notes/page.tsx`: `WeeklySummaryCard` is rendered when `showDashboard` is true, without checking `isAdmin`.
- `src/app/notes/components/weekly-summary-card.tsx`: mounts `getWeeklySummary()` and calls protected `/api/ai/weekly-summary`.
- `src/app/notes/components/knowledge-sidebar.tsx`: exposes folder create/reorder/context-menu mutation controls without an admin capability prop.
- `src/app/notes/page.tsx`: content context menu already limits edit/move/delete actions to `isAdmin`.
- `src/app/(home)/config-dialog/site-settings-panel.tsx`: GitHub sync can fail with `Not authenticated` when the old settings dialog is used without an admin session.
- `src/components/vertical-nav.tsx`, `src/components/nav-card.tsx`, `src/components/mobile-nav.tsx`: no clear normal-navigation entry to `/manage`.

## Source Mapping After Notes Gate Fix

- `src/app/notes/page.tsx`: content card context menu remains read-only for logged-out users because edit, move, and delete actions are appended only inside the `isAdmin` branch.
- `src/app/(home)/config-dialog/site-settings-panel.tsx`: GitHub sync still exists inside the page-settings save flow, but visible public navigation no longer opens the legacy settings dialog after the entry cleanup. The page-settings flow is reachable through `/manage?tab=settings`.
- `src/app/manage/page.tsx`: `settings` remains available to authenticated admins after the navigation migration; only the `security` tab keeps the passkey-only requirement.

## API Host Evidence

- `.env.production` sets `NEXT_PUBLIC_API_URL=https://public-api.limengyang.me`.
- Previous workflow validation records public API CORS checks passing for `https://public-api.limengyang.me` from `https://blog.limengyang.me`.
- `api.limengyang.me` remains Cloudflare Access-protected by design; production public bundles must continue using `public-api.limengyang.me`.

## Admin Entry Source Evidence

- `src/components/vertical-nav.tsx`: desktop inner-page navigation links the management row to `/manage`, shows a readable collapsed `管理` label, and expands to `管理面板` on hover.
- `src/components/nav-card.tsx`: home navigation card links the old settings row to `/manage` with label `管理面板`.
- `src/components/mobile-nav.tsx`: mobile "更多" menu includes `管理面板` -> `/manage`.
- `src/layout/index.tsx`: the old settings shortcut now navigates to `/manage?tab=settings`.
- `src/app/live2d/page.tsx` and `src/app/(home)/write-buttons.tsx`: former settings entry points navigate to the management console.

## Static Validation 2026-06-09

- `npx tsc --noEmit`: pass.
- `python3 -m compileall backend/app`: pass.
- `npm run build`: pass.

## Browser Validation 2026-06-09

Environment:

- Existing `http://localhost:2025` server appeared stale and still served the old `网站设置` sidebar control, so a fresh dev server was started at `http://localhost:3026` for validation.
- Backend health was available on `http://localhost:8000`.

Logged-out `/notes` check on `http://localhost:3026/notes`:

- Visible text checks: no `周度总结`, no `AI 整理建议`, no `写笔记`.
- Folder/tag management checks: no `创建文件夹`, no `上移`, no `下移` controls.
- Admin entry check: desktop collapsed navigation shows a visible `管理` link with `aria-label="管理面板"` and `href="/manage"`.
- Browser console errors: none recorded.

Admin console discoverability:

- Clicking the explicit `a[href="/manage"]` entry navigated to `http://localhost:3026/manage`.
- The management login page displayed `管理面板登录`, confirming the entry is visible and reaches the admin console.

Mobile navigation check:

- Temporary viewport: `390x844`, reset after validation.
- Mobile bottom navigation shows `更多`; expanding it shows `管理面板` with `href="/manage"`.
- Browser console errors: none recorded.

Residual note:

- The stale server on port `2025` should be refreshed or rebuilt before local manual retesting; the validated fresh server on port `3026` reflects the current source changes.

## Follow-up Validation 2026-06-09

Reason for recheck:

- Initial implementation left `/manage?tab=settings` behind a passkey-only gate, which broke the migrated settings entry points despite the discoverability work completing.

Fix applied:

- `src/app/manage/page.tsx` now keeps `页面设置` available to authenticated admins and reserves passkey-only enforcement for `安全设置`.

Environment:

- A second fresh dev server was started at `http://localhost:3027` because port `2025` continued to serve stale assets during earlier checks.
- Backend health remained available on `http://localhost:8000`.

Browser checks:

- Logged-out `http://localhost:3027/notes` still showed no `周度总结`, no `AI 整理建议`, no `写笔记`, and no `创建文件夹`.
- Logged-out `http://localhost:3027/notes` still exposed a visible `/manage` entry, confirming the discoverability changes survived the follow-up fix.
- Visiting `http://localhost:3027/manage?tab=settings` while logged out showed `管理面板登录`, not a passkey-only warning, confirming the migrated settings entry now lands on the normal management login flow instead of a dead-end empty state.

Validation boundary:

- This round did not exercise a real authenticated browser login because local admin credentials were not used in the validation artifact. The code path and tab gating now align with the intended behavior, but an interactive post-login smoke check can still be added later if needed.
