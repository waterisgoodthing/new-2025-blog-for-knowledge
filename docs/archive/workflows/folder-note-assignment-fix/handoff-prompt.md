# Handoff Prompt

Continue or review the completed folder note assignment fix in `/Users/limengyang/2025-blog-public`.

Respect `AGENTS.md`. The original `tasks.md` was approved by the user and all listed tasks are complete.

Key evidence:

- Existing note moves use `POST /api/folders/move-note/{slug}`.
- Notes page refreshes the note list and bumps a sidebar `refreshKey` after move operations.
- `NoteCreate`, `NoteCreateInput`, and `write-note/page.tsx` now support `folder_id` creation.
- `Folder.notes` is explicitly a collection relationship, and `list_folders` explicitly preloads folder notes.
- Folder listing count was validated through `list_folders` with a rollback-only temporary folder and two temporary notes; the observed `note_count` was `2`.
