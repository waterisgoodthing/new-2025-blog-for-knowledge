# Diff Report

Date: 2026-06-13

## Backend

- `backend/app/models/folder.py`
  - Declared `Folder.notes` as a collection relationship so folders with multiple notes can be counted safely.
- `backend/app/routers/folders.py`
  - Explicitly preloads `Folder.notes` when listing folders.
- `backend/app/schemas/note.py`
  - Added `folder_id` to `NoteCreate`, `NoteOut`, and `NoteListItem`.
- `backend/app/routers/notes.py`
  - Imports `Folder`.
  - Validates `folder_id` during note creation.
  - Assigns `Note.folder_id` on create.
  - Records created note `folder_id` in audit metadata.

## Frontend

- `src/lib/api/notes.ts`
  - Added `folder_id` to note list and create API types.
- `src/app/notes/page.tsx`
  - Adds `folder_id` query param to the write-note URL when a folder is active.
  - Refreshes folder sidebar state after drag/drop move and move-dialog completion.
- `src/app/write-note/page.tsx`
  - Reads `folder_id` from search params.
  - Sends `folder_id` in the note creation payload.
- `src/app/notes/components/knowledge-sidebar.tsx`
  - Adds `refreshKey` prop and reloads folders when it changes.

## Workflow

- Updated task, validation, audit, risk, and next-iteration documents for closure evidence.
