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

## Incident Evidence 2026-06-12

Reason:

- User reports that every fresh login shows failure. The pasted browser console includes CORS failures for `public-api.limengyang.me/api/music/playlist`, `public-api.limengyang.me/api/auth/passkey/status`, and repeated redirects from `api.limengyang.me/api/subjects` to Cloudflare Access login.

Current HTTP checks:

- `GET https://public-api.limengyang.me/api/health`: `HTTP 530`, body `error code: 1033`.
- `OPTIONS https://public-api.limengyang.me/api/music/playlist` with `Origin: https://blog.limengyang.me`: `HTTP 530`, body `error code: 1033`.
- `GET https://public-api.limengyang.me/api/auth/passkey/status` with `Origin: https://blog.limengyang.me`: `HTTP 530`, body `error code: 1033`.
- `GET https://api.limengyang.me/api/subjects` redirects to `small-term-e3a5.cloudflareaccess.com/...` and returns Cloudflare Access login HTML after following redirects.

Classification:

- `public-api.limengyang.me` is currently not reaching its backend origin/tunnel, so login-adjacent API calls fail before application auth can be evaluated.
- `api.limengyang.me` remains Access-protected; using it from public browser XHR still produces Access-login HTML/CORS failure and should not be considered a successful public API path.

Next approved task gate:

- Execute Phase 6 in `tasks.md` after explicit user approval.

### P0-15 Local Service State

- `GET http://127.0.0.1:8000/api/health`: `HTTP 200`, body `{"status":"ok","db":"ok"}`.
- `launchctl list | rg 'com\.blog\.(backend|tunnel)'`: both `com.blog.backend` and `com.blog.tunnel` are listed.
- `cloudflared tunnel info blog-tunnel`: `does not have any active connection`.
- `~/.cloudflared/config.yml`: ingress includes both `api.limengyang.me` and `public-api.limengyang.me` to `http://localhost:8000`, but `protocol` is currently `http2`.

P0-15 conclusion:

- Backend is healthy locally.
- Public API outage is at the Cloudflare tunnel connector layer, not the FastAPI app or database.

### P0-16 Repair Evidence

Actions:

- Restored `~/.cloudflared/config.yml` to `protocol: quic`.
- Added Clash Verge DNS/rule overrides so `*.argotunnel.com` resolves to real Cloudflare Edge IPs instead of fake `198.18.0.x` addresses.
- Restarted Clash Verge and confirmed `dig region1.v2.argotunnel.com` returns `198.41.*` addresses.
- Restarted `com.blog.tunnel`.

Post-repair evidence:

- `cloudflared tunnel info blog-tunnel`: active connector `9ee077b9-ad4b-45b6-9165-1c522be11699`, version `2026.6.0`, edge locations `lax01`, `lax05`, `sjc06`, `sjc07`.
- `cloudflared` log: four `Registered tunnel connection` entries and connectivity prechecks all `PASS`.
- `GET https://public-api.limengyang.me/api/health`: `HTTP 200`, body `{"status":"ok","db":"ok"}`.

P0-16 conclusion:

- The public API tunnel is restored. The immediate `530 / 1033` outage is resolved.

### P0-17 CORS And Login-Adjacent Endpoint Verification

- `OPTIONS https://public-api.limengyang.me/api/music/playlist` from `Origin: https://blog.limengyang.me`: `HTTP 200`, `access-control-allow-origin: https://blog.limengyang.me`, `access-control-allow-credentials: true`.
- `GET https://public-api.limengyang.me/api/auth/passkey/status` from `Origin: https://blog.limengyang.me`: `HTTP 200`, body `{"registered":true}`, expected CORS headers present.
- `GET https://public-api.limengyang.me/api/music/playlist` from `Origin: https://blog.limengyang.me`: `HTTP 200`, body `[]`, expected CORS headers present.
- `GET https://public-api.limengyang.me/api/subjects` from `Origin: https://blog.limengyang.me`: `HTTP 200`, body `[]`, expected CORS headers present.

P0-17 conclusion:

- The browser-visible CORS failure path for music/passkey status/public reads is repaired.

### P0-18 Deployed Frontend API Host Verification

- Downloaded live HTML/chunks for:
  - `https://blog.limengyang.me/`
  - `https://blog.limengyang.me/notes`
  - `https://blog.limengyang.me/manage`
- Search result: deployed client chunk contains `https://public-api.limengyang.me`.
- Search result: no deployed HTML/chunk contains standalone `https://api.limengyang.me`.

P0-18 conclusion:

- The deployed frontend is built against the public API host for routine browser API calls.

### P0-19 Manage Login Smoke Check

Tool:

- Headless Google Chrome via Playwright.

Observed page/API behavior:

- `https://blog.limengyang.me/manage` loaded successfully.
- Passkey login text/button was visible.
- `GET https://public-api.limengyang.me/api/auth/me`: `HTTP 401` with CORS header. This is expected for an anonymous session.
- `GET https://public-api.limengyang.me/api/content/site-settings`: `HTTP 200` with CORS header.
- `GET https://public-api.limengyang.me/api/music/playlist`: `HTTP 200` with CORS header.
- `GET https://public-api.limengyang.me/api/auth/passkey/status`: `HTTP 200` with CORS header.
- No request to standalone `https://api.limengyang.me` was observed.
- No browser request failure was observed for app APIs. Only Google Analytics beacon requests reported `net::ERR_ABORTED`.

Validation boundary:

- A full credential assertion was not executed because password entry or Passkey approval requires user presence. The original CORS/API-transport failure path is repaired; any remaining failure after a real credential attempt would be auth-specific, not the `public-api` tunnel outage recorded in this incident.
