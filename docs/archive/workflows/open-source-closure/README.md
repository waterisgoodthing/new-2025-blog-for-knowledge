# Open Source Closure

## Goal

Remove the GitHub sync write path and finish the remaining architecture and release cleanup needed to turn this repository into a clearer open-source project.

Current extension: update the GitHub-facing repository content into Chinese and clearly state that this project is adapted from an original open-source project.

Current audit extension: review the repository as an open-source project structure and identify remaining missing materials without changing product code.

Current preparation extension: prepare the repository for a fuller open-source release with mixed Chinese/English contributor-facing materials.

## Touched Domains

- `sync`: backend sync router/service and frontend sync API client. **Removed.**
- `notes`: public/private read boundary. **Fixed.**
- `blog`: publishing flow. Already backend-native, no changes needed.
- `manage`: admin actions and settings. **Sync tab removed.**
- `about`, `share`, `projects`, `pictures`, `snippets`, `bloggers`, site settings: **Migrated from static JSON + GitHub sync to backend API.**
- `shared infrastructure`: README, CONTRIBUTING, SECURITY. **Updated.**

## Current Status

Core open-source architecture cleanup completed on 2026-06-10.

GitHub-facing Chinese content and upstream-origin disclosure extension completed on 2026-06-14.

- All legacy static editable domains migrated to backend content API.
- GitHub sync code fully removed from both frontend and backend.
- Notes public boundary fixed for anonymous users.
- README aligned with actual package manager (npm).
- CONTRIBUTING.md and SECURITY.md added.
- TypeScript check passes. Backend import check passes.
- Chinese repository-facing docs and original open-source project attribution completed.
- Open-source structure audit completed on 2026-06-16; remaining gaps are recorded in `audit.md`.
- Full open-source preparation (Phase 7) completed on 2026-06-16. All 9 tasks closed.
  - Environment examples, setup/check scripts, CI, issue/PR templates, package metadata, README rewrite all done.
  - Validation recorded in `validation.md`.
  - Deferred: Docker Compose, CODEOWNERS, upstream URL, cross-platform setup script testing.

## Workflow Files

- [requirements.md](./requirements.md)
- [design.md](./design.md)
- [tasks.md](./tasks.md)
- [audit.md](./audit.md)
- [validation.md](./validation.md)
