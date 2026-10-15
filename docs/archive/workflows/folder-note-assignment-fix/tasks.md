# Tasks

Implementation approved by user on 2026-06-13.

- [x] T1 Diagnose the exact failing path: distinguish move-second-note failure from create-new-note-in-folder failure, and capture the observed code/API evidence.
  - Evidence: `design.md` and `validation.md` now record that create-new-note-in-folder lacks a `folder_id` route/query/client/backend contract; the red schema check returned `False`.
- [x] T2 Add or update the minimal backend contract needed for note folder assignment on creation, including schema validation for `folder_id` if creation-in-folder is the intended behavior.
  - Evidence: `NoteCreate`, `NoteOut`, and `NoteListItem` now include `folder_id`; `create_note` validates the folder exists before assigning `Note.folder_id`.
- [x] T3 Update frontend API types and write-note entry flow so selected-folder creation behavior is explicit and contract-safe.
  - Evidence: `NoteListItem` and `NoteCreateInput` include `folder_id`; `/notes` adds `folder_id` to the write-note URL when a folder is active; `/write-note` sends `folder_id` on create.
- [x] T4 Refresh folder tree/count state after move operations from the notes page and move dialog.
  - Evidence: `KnowledgeSidebar` accepts `refreshKey`; `/notes` increments it after drag/drop move and move-dialog completion so the folder tree/counts reload.
- [x] T5 Run targeted validation and record results in `validation.md`.
  - Evidence: backend schema/router checks, folder listing count regression check, Python compile check, `npx tsc --noEmit`, `npm run build`, diff hygiene, and local HTTP checks are recorded in `validation.md`.
- [x] T6 Update this task list immediately as each approved implementation task completes.
  - Evidence: T1 through T5 were marked complete immediately after their corresponding diagnosis, implementation, or validation step.
