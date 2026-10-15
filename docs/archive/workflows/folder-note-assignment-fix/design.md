# Design

## Context

The notes workspace uses folders through:

- `backend/app/routers/folders.py`
- `backend/app/schemas/folder.py`
- `backend/app/models/folder.py`
- `backend/app/routers/notes.py`
- `backend/app/schemas/note.py`
- `src/lib/api/folders.ts`
- `src/lib/api/notes.ts`
- `src/app/notes/page.tsx`
- `src/app/notes/components/knowledge-sidebar.tsx`
- `src/components/move-to-folder-dialog.tsx`
- `src/app/write-note/page.tsx`

Current data flow:

```text
notes page / sidebar / move dialog -> src/lib/api/* -> backend API -> SQLAlchemy models
```

## Findings So Far

1. Moving an existing note to a folder uses `POST /api/folders/move-note/{slug}` and updates `Note.folder_id`.
2. After a move, `src/app/notes/page.tsx` refreshes only the note list through `mutate()`. The `KnowledgeSidebar` owns its folder tree state internally and is not forced to reload after a move.
3. Creating a new note does not support folder assignment:
   - `backend/app/schemas/note.py` `NoteCreate` has no `folder_id`.
   - `src/lib/api/notes.ts` `NoteCreateInput` has no `folder_id`.
   - `src/app/write-note/page.tsx` does not read or send any folder context.
4. `backend/app/routers/folders.py` computes `note_count` from `f.notes`, so validation should include `GET /api/folders` after a folder contains notes.

## T1 Diagnosis Result

The confirmed failing path is create-new-note-in-folder, with a secondary refresh gap after move:

- `src/app/notes/page.tsx` renders the create action as the static `href` returned by `getCreateAction()`, so selecting a folder does not pass folder context into `/write-note`.
- `src/app/write-note/page.tsx` saves through `createNote(...)` without `folder_id`.
- `src/lib/api/notes.ts` `NoteCreateInput` has no `folder_id`.
- `backend/app/schemas/note.py` `NoteCreate` has no `folder_id`; a public schema check returned `False` for `"folder_id" in NoteCreate.model_fields`.
- Existing move-to-folder uses the dedicated folder API, so moving a note is separate from creating content inside the currently selected folder.

## Proposed Approach

Keep the fix narrow and notes-domain scoped:

1. Add an explicit folder assignment contract to note creation if the intended workflow is "create inside selected folder".
2. Preserve the existing move endpoint for moving existing content.
3. Add a sidebar refresh trigger so folder tree/count state updates after move operations.
4. Verify `GET /api/folders` still works after a note exists in the folder.

No unrelated visual redesign or persistence refactor is in scope.
