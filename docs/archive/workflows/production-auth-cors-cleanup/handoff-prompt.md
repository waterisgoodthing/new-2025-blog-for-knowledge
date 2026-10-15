# Handoff Prompt

You are working in `/Users/limengyang/2025-blog-public`.

Task folder: `docs/workflows/production-auth-cors-cleanup/`.

Goal: completed task. Keep this folder for maintenance follow-up only: production `/notes` console errors were reduced by removing anonymous admin-only calls from public pages, making `/manage` discoverable, and keeping migrated settings entry points usable through `/manage?tab=settings`.

Start by reading `README.md`, `requirements.md`, `design.md`, `tasks.md`, and `validation.md`. If new work extends scope, update the workflow docs before implementing.

Key suspected files:

- `src/app/notes/page.tsx`
- `src/app/notes/components/knowledge-sidebar.tsx`
- `src/app/notes/components/weekly-summary-card.tsx`
- `src/app/(home)/config-dialog/site-settings-panel.tsx`
- `src/components/vertical-nav.tsx`
- `src/components/nav-card.tsx`
- `src/components/mobile-nav.tsx`
- `src/lib/api/config.ts`
- `src/app/manage/page.tsx`

Important constraints:

- Public users can read notes/blogs/mistakes and music.
- Admin-only actions must be hidden or disabled when logged out.
- Do not loosen backend mutation auth.
- Do not change Cloudflare Access policy from code.
- Validate with `npx tsc --noEmit` and browser checks.
- Make `/manage` discoverable from desktop and mobile navigation.
- Keep `页面设置` usable for authenticated admins after any future navigation or auth changes; only explicitly sensitive tabs should require passkey-only access.
