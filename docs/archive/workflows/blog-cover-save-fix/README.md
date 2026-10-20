# Blog Cover Save Fix

## Goal

Fix the blog editor path where a locally selected cover image cannot be saved as a persisted blog cover.

## Touched Domains

- `blog`: `/write` create/edit publishing flow.
- `shared infrastructure`: backend note image upload API and frontend API client, if needed.

## Current Status

Implemented and validated. `npx tsc --noEmit` passed.

## Workflow Files

- [design.md](./design.md)
- [requirements.md](./requirements.md)
- [tasks.md](./tasks.md)
- [validation.md](./validation.md)
- [handoff-prompt.md](./handoff-prompt.md)

## Initial Finding

The write editor stores dropped/selected cover files as local `ImageItem` objects with `previewUrl`. `pushBlog()` only persists `cover` when it is already a URL, so a local file cover is never uploaded and never sent to `createNote()` / `updateNote()`.
