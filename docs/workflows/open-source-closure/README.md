# Open Source Closure

## Goal

Remove the GitHub sync write path and finish the remaining architecture and release cleanup needed to turn this repository into a clearer open-source project.

## Touched Domains

- `sync`: backend sync router/service and frontend sync API client. **Removed.**
- `notes`: public/private read boundary. **Fixed.**
- `blog`: publishing flow. Already backend-native, no changes needed.
- `manage`: admin actions and settings. **Sync tab removed.**
- `about`, `share`, `projects`, `pictures`, `snippets`, `bloggers`, site settings: **Migrated from static JSON + GitHub sync to backend API.**
- `shared infrastructure`: README, CONTRIBUTING, SECURITY. **Updated.**

## Current Status

Implementation completed on 2026-06-10.

- All legacy static editable domains migrated to backend content API.
- GitHub sync code fully removed from both frontend and backend.
- Notes public boundary fixed for anonymous users.
- README aligned with actual package manager (npm).
- CONTRIBUTING.md and SECURITY.md added.
- TypeScript check passes. Backend import check passes.

## Workflow Files

- [requirements.md](./requirements.md)
- [design.md](./design.md)
- [tasks.md](./tasks.md)
- [validation.md](./validation.md)
