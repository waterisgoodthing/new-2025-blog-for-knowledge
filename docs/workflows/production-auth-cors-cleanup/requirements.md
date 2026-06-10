# Requirements

## Reported Symptoms

The production browser console shows:

- `GET .../api/auth/me -> 401`
- `GET .../api/ai/weekly-summary -> 401`
- `DELETE .../api/folders/<id> -> 401`
- `GitHub sync failed: {"detail":"Not authenticated"}`
- Requests to `https://api.limengyang.me/api/subjects` are redirected to Cloudflare Access login, then blocked by CORS because the Access login response does not include `Access-Control-Allow-Origin`.

## Functional Requirements

REQ-1: Public notes pages must remain readable without an admin session.

REQ-2: Public notes pages must not automatically call admin-only AI endpoints such as weekly summary or AI suggestions.

REQ-3: Public users must not see or trigger folder/tag mutation controls: create, rename, delete, reorder, drag/drop move.

REQ-4: Admin users must retain the same folder/tag controls after authentication.

REQ-5: GitHub sync calls must only run from explicit authenticated management/editing flows, never as a background effect on public pages.

REQ-6: Public frontend API calls must use the public API host (`public-api.limengyang.me`) or another host not protected by Cloudflare Access.

REQ-7: Private/admin API calls may fail with `401` when logged out, but the UI should handle that quietly unless the user is on an admin-only page.

REQ-8: Validation must include browser or HTTP checks for logged-out `/notes` and API host selection.

REQ-9: The administrator console must be discoverable from the normal site navigation. Users should not need to know `/manage` manually.

REQ-10: The old "网站设置" entry should not remain the only visible settings/admin entry after the management console exists. It should either navigate to `/manage?tab=settings` or be clearly distinguished from the full admin console.

REQ-11: The administrator console entry must be understandable without hover-only text. On desktop, the collapsed navigation state must still show a readable management label, because users may not discover hidden hover labels.

## Non-Goals

- Do not change Cloudflare Access policy in code.
- Do not expose admin mutation endpoints publicly.
- Do not reintroduce bearer-token localStorage auth.
