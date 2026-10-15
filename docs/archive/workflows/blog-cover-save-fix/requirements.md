# Blog Cover Save Fix Requirements

## Functional Requirements

- A blog cover selected from a local image file must be uploaded before publishing.
- The saved blog `cover` field must contain the uploaded image URL.
- Existing URL-based covers must continue to save without upload.
- Body markdown image placeholders in the form `local-image:<id>` must be replaced with uploaded image URLs before publishing.
- Only local body images actually referenced by markdown should be uploaded.
- If the cover local file is also referenced in markdown, the publish flow should reuse the same uploaded URL.
- Edit mode must continue to update the original slug and must not silently create a duplicate blog.
- The user-facing success/failure behavior should remain through the existing publish toast flow.

## Architectural Requirements

- Frontend flow must stay within:

```text
page/component -> hook/local action -> src/lib/api/* -> backend API
```

- Backend flow must remain:

```text
router -> schema validation -> service/model -> response schema
```

- No new API endpoint should be introduced unless the existing `/api/notes/upload-image` contract is proven insufficient.
- Keep changes scoped to `blog` and shared note-image API usage.
- Do not introduce a second upload API for blog body images.

## Validation Requirements

- Run `npx tsc --noEmit` because frontend TypeScript is touched.
- If feasible, run or inspect the relevant `/write` route in a browser and verify local cover/body image save behavior.
- Record validation results in `validation.md`.
