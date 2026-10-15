# Production Auth/CORS Cleanup

## Goal

Fix the production console errors reported from `https://blog.limengyang.me/notes`: anonymous `401` noise, admin-only UI actions leaking onto public pages, and Cloudflare Access redirects from `api.limengyang.me` causing browser CORS failures.

## Touched Domains

- `notes`: public notes workspace and sidebar behavior.
- `auth`: admin-gated rendering and anonymous auth checks.
- `manage/sync`: prevent GitHub sync calls outside authenticated management flows.
- shared infrastructure: public/private API base URL expectations.

## Current Status

Reopened on 2026-06-12 for a production login/API reachability incident. The earlier 2026-06-09 source-code cleanup remains complete, but current live checks show `public-api.limengyang.me` returning Cloudflare `530 / 1033`, while `api.limengyang.me` still redirects to Cloudflare Access by design. This affects `auth`, `music`, and shared API infrastructure; implementation/operations must follow the new Phase 6 task list.

## Workflow Files

- [requirements.md](./requirements.md)
- [design.md](./design.md)
- [tasks.md](./tasks.md)
- [validation.md](./validation.md)
- [handoff-prompt.md](./handoff-prompt.md)
