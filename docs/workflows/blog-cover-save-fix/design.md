# Blog Cover Save Fix Design

## Problem

When building a blog cover in the write editor, selecting a local file creates a browser-only preview. The publish service currently writes:

```ts
cover: cover?.type === 'url' ? cover.url : undefined
```

That means `cover.type === 'file'` is dropped from the save payload. The backend contract already supports persisted cover URLs through `NoteCreate.cover` and `NoteUpdate.cover`, and the notes API already exposes `uploadImage(file, { noteType, slug })`.

## Data Flow

Expected flow:

```text
/write cover file -> pushBlog -> uploadImage -> persisted URL -> createNote/updateNote cover
```

Current broken flow:

```text
/write cover file -> local previewUrl -> pushBlog -> cover undefined -> createNote/updateNote
```

## Proposed Scope

1. Update `src/app/write/services/push-blog.ts` so local cover files are uploaded before save.
2. Use the existing `uploadImage()` API wrapper with `noteType: "blog"` and the target slug.
3. Preserve URL covers unchanged.
4. Keep edit mode slug protection intact.
5. Upload local body images referenced as `local-image:<id>` before save and replace markdown placeholders with persisted URLs.
6. Reuse uploaded URLs when the same local image is both the cover and a body image.
7. Avoid changing backend schema/model unless runtime evidence shows the existing upload API is insufficient.

## Out Of Scope

- Redesigning the write editor UI.
- Moving blog persistence to another data source.
- Refactoring note/mistake image upload flows.
- Changing public deployment or Cloudflare configuration.

## Risks

- Image upload requires admin auth through the existing backend JWT/session path.
- Local images that are present in the side image list but not referenced in markdown should not be uploaded during publish.
