# Requirements

## Functional Requirements

- A folder that already contains a moved note must still be selectable as a destination for more content.
- Moving a second note into the same folder must succeed and the visible list/folder state must refresh.
- If a user creates a note while a folder is selected, the intended behavior must be explicit:
  - either create the note in that selected folder, or
  - clearly keep creation independent of folder selection.
- Folder counts and folder tree rendering must not break after notes are assigned to folders.

## Contract Requirements

- Frontend TypeScript API types must match backend Pydantic schemas.
- Backend note creation must validate any supplied `folder_id` before storing it.
- Existing move-to-folder behavior must remain compatible.

## Non-Goals

- Do not redesign the notes workspace.
- Do not change the folder hierarchy model.
- Do not change mistake review behavior unless the same folder contract is directly affected.
- Do not introduce a new state library.

## Validation Requirements

- Frontend TypeScript validation: `npx tsc --noEmit`.
- Backend validation: targeted import/start check or a small route-level check for folder listing after note assignment.
- UI validation if implementation proceeds: run the dev server and inspect `/notes` in a browser, including moving content into an already populated folder.
