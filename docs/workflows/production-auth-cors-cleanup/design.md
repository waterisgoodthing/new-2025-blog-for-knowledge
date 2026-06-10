# Design

## Diagnosis

The reported console log contains three categories:

1. Expected auth probes: `/api/auth/me` returns `401` when logged out. This is acceptable if it is quiet and does not break the page.
2. Frontend gate leaks: public `/notes` mounts admin-only widgets or controls, causing calls to protected endpoints such as `/api/ai/weekly-summary` and `/api/folders/<id>`.
3. Deployment host mismatch: some requests still use `api.limengyang.me`, which remains Cloudflare Access-protected. Browser fetch receives an Access login page from another host and fails CORS.

## Planned Changes

### Notes Dashboard Admin Widgets

`SuggestionCard` is already gated by `isAdmin`; `WeeklySummaryCard` is not. Render weekly summary only when:

- dashboard context is active, and
- `isAdmin` is true.

This preserves the admin experience while preventing anonymous calls to `/api/ai/weekly-summary`.

### Knowledge Sidebar Admin Actions

Add an admin capability flag to `KnowledgeSidebar`, or use the existing auth hook inside it. Prefer prop injection from route pages so public/admin behavior remains explicit at the composition boundary.

When not admin:

- hide create-folder inline control;
- hide reorder controls;
- disable drag/drop mutation handlers;
- do not open folder/tag mutation context menus;
- keep read-only folder/tag filtering available.

When admin:

- preserve current create, rename, delete, reorder, drag/drop behavior.

### GitHub Sync Noise

Audit the source of `GitHub sync failed` and ensure protected sync calls are only triggered from admin-managed save flows. If the failure comes from a save action while logged out, the route should be behind `AuthGate`; if it is from a public settings component, gate the component.

### API Host Verification

Document and verify production build-time `NEXT_PUBLIC_API_URL`. Public pages should be built against `https://public-api.limengyang.me` unless the backend protection strategy changes.

Because `NEXT_PUBLIC_API_URL` is baked into client bundles, validation must inspect built/runtime chunks or run a browser check rather than only reading local source.

### Admin Console Discoverability

The repository now has a full `/manage` route, but the global navigation still exposes an older "网站设置" control that opens the home settings dialog. This makes the new administrator console hard to find.

Add an explicit "管理面板" entry in desktop and mobile navigation. Prefer linking to `/manage`, with the existing page-settings experience available inside `/manage?tab=settings`. The old home settings dialog may remain as a specialized homepage edit affordance, but it should not be the primary admin entry.

After user feedback, the desktop side navigation needs a stronger collapsed state. A settings icon alone is not discoverable enough, so the `/manage` entry should show a visible short label such as "管理" even before hover expansion. When `/manage` is active, the entry should use the same active visual language as other navigation items.

Likely files:

- `src/components/vertical-nav.tsx`
- `src/components/nav-card.tsx`
- `src/components/mobile-nav.tsx`
- `src/layout/index.tsx`

## Risks

- `useAdminAuth()` intentionally calls `/api/auth/me`; this may leave a harmless `401` network entry. If console noise is unacceptable, introduce a silent optional-auth endpoint or avoid checking auth on purely public pages until admin actions are needed.
- Cloudflare Access configuration cannot be fixed from repository code; if public read endpoints still go to `api.limengyang.me`, deployment environment variables must be corrected.
- Changing the settings entry can affect the old homepage customization workflow, so validate that `/manage?tab=settings` still provides page settings.
- A visible collapsed management label slightly increases the height of the side navigation, so keep the label compact and avoid changing the main content layout.
