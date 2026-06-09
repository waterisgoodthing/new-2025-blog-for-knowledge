# Admin Contract Organization Music Upgrade

## Goal

Build the next large task group for the personal knowledge/blog system:

- Add an internal administrator contract after removing site-level protection.
- Support passkey and password-based administrator sessions with different authority levels.
- Upgrade content organization with folder deletion, folder nesting, drag-and-drop, tags, and context menus across the system.
- Consolidate administration into `/manage`, including AI management, page settings, content management, music management, security, and audit logs.
- Restore and upgrade the music page with NetEase Cloud Music API candidate-pool daily song support.
- Redesign structured weak-point diagnosis for mistakes.

## Touched Domains

- `auth`: administrator token, passkey, password login, logout, token revocation.
- `notes`: public read-only access, admin write/edit/delete, folders, tags, context menus.
- `mistakes`: public read-only access, mistake creation/editing, weak-point diagnosis.
- `blog`: public read-only access plus admin context actions.
- `music`: deployable NetEase Cloud Music API, synchronized candidate pool, AI daily song, listening playback, admin-managed configuration.
- `manage`: unified administrator console.
- `review`: admin-protected review operations.
- `shared infrastructure`: API client auth, context menus, drag/drop, audit logs.
- `backend`: FastAPI auth, folders, tags, notes, audit, NetEase music integration, AI management.

## Current Status

Task list approved in conversation on 2026-06-08.

No business-code implementation has started in this workflow by Codex. Ownership is being handed to another intelligent agent.

## Workflow Files

- [requirements.md](./requirements.md)
- [design.md](./design.md)
- [tasks.md](./tasks.md)

## Required Approval Gate

Implementation may start from `tasks.md` because the user approved this round in conversation on 2026-06-08.
