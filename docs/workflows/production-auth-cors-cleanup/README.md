# Production Auth/CORS Cleanup

## Goal

Fix the production console errors reported from `https://blog.limengyang.me/notes`: anonymous `401` noise, admin-only UI actions leaking onto public pages, and Cloudflare Access redirects from `api.limengyang.me` causing browser CORS failures.

## Touched Domains

- `notes`: public notes workspace and sidebar behavior.
- `auth`: admin-gated rendering and anonymous auth checks.
- `manage/sync`: prevent GitHub sync calls outside authenticated management flows.
- shared infrastructure: public/private API base URL expectations.

## Current Status

Completed on 2026-06-09. Public `/notes` is now read-only when logged out, the admin console is discoverable from normal navigation, and migrated settings entry points resolve to `/manage?tab=settings` without the earlier passkey-only dead end.

## Workflow Files

- [requirements.md](./requirements.md)
- [design.md](./design.md)
- [tasks.md](./tasks.md)
- [validation.md](./validation.md)
- [handoff-prompt.md](./handoff-prompt.md)
