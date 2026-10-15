# Blog Cover Save Fix Tasks

Approved in conversation and completed.

- [x] **P0-01** Update blog publish service to upload a local file cover through `uploadImage(file, { noteType: "blog", slug })` before `createNote()` or `updateNote()`.
- [x] **P0-02** Ensure the save payload uses the resolved cover URL for both create and edit modes while preserving existing URL covers.
- [x] **P0-03** Check whether body markdown local image placeholders are part of the reported failure; document the result and defer or fix only if directly required.
- [x] **P0-04** Run frontend TypeScript validation with `npx tsc --noEmit`.
- [x] **P0-05** Record validation evidence and any remaining limits in `validation.md`.

## P1 Body Image Persistence

Approved in conversation after the body-image risk was explained.

- [x] **P1-01** Update `pushBlog()` to replace markdown `local-image:<id>` placeholders with persisted upload URLs before save.
- [x] **P1-02** Reuse the same uploaded URL when a local file is used as both cover and body image.
- [x] **P1-03** Preserve URL images and unreferenced local image list items without unnecessary uploads.
- [x] **P1-04** Run frontend TypeScript validation with `npx tsc --noEmit`.
- [x] **P1-05** Record body-image validation evidence and remaining limits in `validation.md`.

## P2 Public Deployment

Approved in conversation by request to push this round to the public site.

- [x] **P2-01** Prepare a deployment workspace containing only this round's source change.
- [x] **P2-02** Run `npx tsc --noEmit` in the deployment workspace.
- [x] **P2-03** Run Cloudflare build and deploy to `blog.limengyang.me`.
- [x] **P2-04** Smoke-check the public site and API health.
- [x] **P2-05** Record deployment evidence and remaining limits in `validation.md`.
