# Blog Cover Save Fix Validation

Implementation and validation are complete for the scoped cover and body-image persistence fix.

## Pre-Implementation Evidence

- `src/app/write/components/sections/cover-section.tsx` sets selected local files as `cover` items with `type: "file"` and a `previewUrl`.
- `src/app/write/services/push-blog.ts` only sends a cover when `cover.type === "url"`.
- `src/lib/api/notes.ts` already exposes `uploadImage(file, { noteType, slug })`.
- `backend/app/schemas/note.py` and `backend/app/routers/notes.py` already accept and persist `cover`.

## Scope Check

- Body markdown images can still contain `local-image:<id>` placeholders from `src/app/write/components/editor.tsx` and are preview-resolved by `src/app/write/hooks/use-write-data.ts`.
- That is a separate body-image persistence risk. It is not the direct cause of the cover field being dropped, so this task keeps the implementation scoped to blog cover saving.

## 2026-06-14 Validation

- `npx tsc --noEmit`: passed.
- Source inspection: `src/app/write/services/push-blog.ts` now resolves a local file cover through `uploadImage(file, { noteType: "blog", slug })` before calling `createNote()` or `updateNote()`.
- Source inspection: URL covers still pass through unchanged.

## 2026-06-14 Body Image Persistence Validation

- `npx tsc --noEmit`: passed.
- Source inspection: `src/app/write/services/push-blog.ts` now replaces markdown `local-image:<id>` placeholders with uploaded image URLs before `createNote()` or `updateNote()`.
- Source inspection: a shared upload cache reuses the same uploaded URL when a local image is both the cover and a body image.
- Source inspection: body URL images are left unchanged, and local images in the side image list are uploaded only when their `local-image:<id>` placeholder appears in markdown.

## Remaining Limits

- Browser runtime validation was not run in this turn.
- Upload still depends on the existing authenticated backend `/api/notes/upload-image` path and its configured image base URL.

## 2026-06-14 Public Deployment

Deployment scope:

- Deployed from a temporary git worktree based on `HEAD` plus only `src/app/write/services/push-blog.ts` from this task.
- Unrelated dirty files in the main working tree were not included in the deployment workspace.

Build and deploy evidence:

- `npx tsc --noEmit`: passed in the deployment workspace after copying the generated `next-env.d.ts` used by this Next.js project.
- First `npm run build:cf`: failed because Turbopack rejected a symlinked `node_modules` in the temporary workspace.
- Second `npm run build:cf`: failed because the temporary workspace did not include `.env.production`, so `NEXT_PUBLIC_API_URL` fell back to localhost and production validation rejected it.
- Final `npm run build:cf`: passed after using a real `node_modules` copy and `.env.production`.
- `npx wrangler deploy --route 'blog.limengyang.me/*'`: passed.
- Cloudflare Worker: `2025-blog-public`.
- Worker URL: `https://2025-blog-public.17527677392.workers.dev`.
- Route: `blog.limengyang.me/*`.
- Version ID: `0381548f-2a53-41e9-b26b-653daf66ac48`.
- Assets uploaded: 3 new or modified static assets.

Public smoke checks:

- `curl -I https://blog.limengyang.me/`: `HTTP/2 200`, `x-opennext: 1`.
- `curl -I https://blog.limengyang.me/write`: `HTTP/2 200`, `x-opennext: 1`.
- `curl https://public-api.limengyang.me/api/health`: `{"status":"ok","db":"ok"}`.
- `curl -I https://2025-blog-public.17527677392.workers.dev`: `HTTP/2 200`, `x-opennext: 1`.
- Deployed JS chunk inspection found the expected `upload-image` API call and `local-image:<id>` replacement logic.

Deployment limits:

- Full authenticated browser publishing was not executed because it requires a live admin session and file selection in the browser.
