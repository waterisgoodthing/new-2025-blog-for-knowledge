# Design

## Diagnosis Summary

The backend notes router currently raises 409 only in `create_note` when a slug already exists:

`POST /api/notes -> createNote -> Slug already exists`

The ordinary note edit page, `/write-note/[slug]`, calls:

`updateNote(slug, payload) -> PUT /api/notes/{slug}`

The blog edit page, `/write/[slug]`, relies on Zustand state:

`loadBlogForEdit(slug) -> set mode=edit/originalSlug=slug -> usePublish -> pushBlog(mode=edit) -> updateNote(originalSlug, payload)`

If a save is possible before the edit store has loaded, `mode` can still be `create`; `pushBlog` then calls `createNote` with the existing slug, causing 409.

## Proposed Approach

1. Reproduce or confirm the failing request path from code and, if practical, by running the app.
2. Make edit pages resilient:
   - Ensure edit pages initialize or guard edit mode before save.
   - Disable save while edit data is loading or edit identity is missing.
   - Prefer using the route slug as the source of truth for edit saves.
3. Improve user-facing error clarity only if needed, without hiding contract failures.
4. Validate with TypeScript and targeted manual/browser checks.

## Constraints

- Keep routers thin and avoid backend changes unless the frontend path cannot be made correct.
- Preserve current slug immutability.
- Do not touch unrelated dirty files.

