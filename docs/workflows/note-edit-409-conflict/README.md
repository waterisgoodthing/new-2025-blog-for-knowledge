# Note Edit 409 Conflict

## Goal

Fix the bug where saving after re-editing a note-like entry can fail with HTTP 409.

## Touched Domains

- `notes`
- `write-note`
- `blog` edit flow, if the observed 409 comes from `/write/[slug]`
- shared API client only if clearer conflict messaging is needed

## Current Status

- Status: awaiting approval for implementation tasks.
- Initial diagnosis: backend `POST /api/notes` returns 409 only when a slug already exists. The normal `/write-note/[slug]` editor uses `PUT /api/notes/{slug}`, so a 409 during re-edit likely means the UI is reaching a create path instead of an update path, or the edit mode is not ready when save is clicked.

## Workflow Files

- [requirements.md](requirements.md)
- [design.md](design.md)
- [tasks.md](tasks.md)
- [validation.md](validation.md)
- [handoff-prompt.md](handoff-prompt.md)

