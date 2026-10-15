# Requirements

## Problem

When re-editing content created through the note writing flow, saving can fail in the browser with:

`Failed to load resource: the server responded with a status of 409`

Backend inspection shows `POST /api/notes` returns 409 for `Slug already exists`. Re-edit saves should update the existing record instead of trying to create a new record with the same slug.

## Acceptance Criteria

- Re-editing an existing ordinary note saves via `PUT /api/notes/{slug}`.
- Re-editing an existing blog entry saves via `PUT /api/notes/{slug}`.
- The save button cannot submit an edit as create while edit data is still loading.
- Existing slug immutability behavior is preserved unless the backend explicitly supports slug rename.
- Existing user edits and unrelated dirty files are preserved.
- Validation is recorded in `validation.md`.

## Out Of Scope

- Adding slug rename support.
- Refactoring the full write/editor architecture.
- Changing persistence from backend PostgreSQL to static files or GitHub sync.
- Modifying mistake review behavior unless the same 409 is reproduced there.

