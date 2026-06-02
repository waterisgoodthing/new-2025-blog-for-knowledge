# SYSTEM_AUDIT_REPORT.md

Audit time: 2026-06-01 15:12:03 CST

Scope: system-level review for a personal blog, mistake notebook, study notes, AI analysis, taxonomy, file storage, deployment, and data reliability system.

Deployment assumption updated by owner:

- This is a personal system, not a multi-user SaaS.
- Cloudflare already applies IP allowlisting/rate restriction in front of the exposed service.
- The review therefore does not require SaaS-grade verification or adversarial threat modeling.
- Risks are ranked by personal long-term use: data not lost, not confused, not accidentally leaked, and deployment remaining predictable.

Rules followed:

- No business code was modified.
- No `.env`, secrets, production config, database data, or generated content was modified.
- No `git add`, `git commit`, or `git push` was executed.
- No destructive database/file operation was executed.
- Only read-oriented inspection and lightweight validation commands were run.

## Executive Summary

The system already has the right main pieces for a personal knowledge/blog product: Next.js frontend, FastAPI backend, PostgreSQL model, Alembic migrations, notes/mistakes/review, AI analysis, and GitHub static sync.

Under the updated assumption that Cloudflare IP allowlisting protects the backend, the biggest practical risk is no longer "random internet user immediately takes over the backend." The bigger personal-system risks are:

1. Uploaded mistake images are stored on the backend local filesystem but referenced by the frontend as public asset URLs, so evidence images may disappear or fail to load after redeploys.
2. Hidden/draft/private notes can be exported into `public/notes/...` by the GitHub sync path, which can turn private study data into static public files if that export is used.
3. App-layer auth is currently bypassed. With Cloudflare IP restrictions this may be an acceptable short-term personal convenience, but it is still a fragile single-control setup if the origin is ever exposed, a tunnel is opened, CF rules are loosened, or another machine on the allowlist is compromised.
4. Database schema management mixes Alembic with `create_all` on startup, which makes long-term schema state harder to reason about.

## Findings

### AUDIT-001

- Severity: P1
- Impact scope: mistake image evidence, note image uploads, file storage, deployment reliability
- Evidence:
  - `backend/app/routers/notes.py:108-139` stores uploads under local `public/images/pictures` and returns `/images/pictures/{filename}`.
  - `wrangler.toml:1-8` indicates frontend assets are served from OpenNext/Cloudflare assets, not from the FastAPI backend local filesystem.
  - `backend/app/services/github_sync.py:95-182` exports note metadata and markdown but does not export `images` or upload binary evidence files.
- Trigger scenario: You upload mistake images through `/write-mistake`; later the frontend runs from Cloudflare assets while the backend runs elsewhere, or the backend is redeployed without preserving the local `public/images/pictures` directory.
- Risk: Wrong-question evidence can become unreachable even though the database still contains image URLs. For this personal system, this is a data-continuity risk more than a security risk.
- Fix recommendation: Pick one durable image strategy:
  - Cloudflare R2/S3/object storage for uploaded evidence, with URLs stored in the database.
  - Backend static serving from a persistent volume with backups.
  - GitHub export that copies uploaded images and includes `images` metadata.
- Acceptance method: Upload one test image, restart/redeploy backend, open the note detail from the deployed frontend, and confirm the image still loads.
- Needs manual confirmation: Yes. Confirm whether mistake images should be public assets, IP-restricted assets, or private authenticated files.

### AUDIT-002

- Severity: P1
- Impact scope: notes export, privacy, static generated content, GitHub sync
- Evidence:
  - `backend/app/services/github_sync.py:95-182` exports all notes ordered by update time.
  - `backend/app/services/github_sync.py:102-121` includes hidden notes in `public/notes/index.json` with `hidden` metadata.
  - `backend/app/services/github_sync.py:141-167` writes each note's config and markdown content regardless of `hidden` or `status`.
- Trigger scenario: You call `/api/sync/push`; generated `public/notes/...` is committed and then deployed or browsable.
- Risk: Hidden/draft/private notes and mistakes may become static files under `public/`. Even if UI hides them, raw markdown/config can still be addressable by path.
- Fix recommendation: Split export destinations:
  - Public export: only `status=published` and `hidden=false`, and probably only `type=blog` or explicitly public notes.
  - Private backup: encrypted archive, private repo, object storage, or database dump, not `public/`.
- Acceptance method: Create a hidden/draft test note and run the intended sync flow in a safe environment; confirm no file for it appears under public export paths.
- Needs manual confirmation: Yes. Confirm whether ordinary notes and mistakes should ever be exported to public static files.

### AUDIT-003

- Severity: P1
- Impact scope: auth, notes, mistakes, review, AI, upload, sync, music, recommendations, taxonomy management, manage page
- Evidence:
  - `backend/app/routers/auth.py:16-33` returns the first user, auto-creates `admin`, and promotes the first user to admin without checking credentials.
  - `backend/app/routers/auth.py:36-40` returns admin privileges without checking `is_admin`.
  - `backend/app/utils/auth.py:26-29` defines JWT decoding but it is not used by `get_current_user`.
- Trigger scenario: A request reaches the FastAPI backend from an allowed Cloudflare IP, a temporarily opened tunnel, local network access, or a mistakenly exposed origin.
- Risk: Cloudflare IP allowlisting is a meaningful outer control, so this is not automatically an internet-wide P0 in your current deployment model. But application auth is still effectively absent once a request reaches the app. Any allowed path can create/update/delete notes, upload images, trigger AI spending, submit review changes, alter taxonomy, and use GitHub sync endpoints.
- Fix recommendation: Either:
  - Restore real JWT verification for normal production use, or
  - Explicitly document this as a local/IP-restricted personal-admin mode and add a startup warning when `ENV=production` uses bypass auth.
- Acceptance method: Lightweight option: from a non-allowlisted IP, backend is unreachable due to CF. Stronger option: from an allowlisted IP without token, admin endpoints return `401/403`.
- Needs manual confirmation: Yes. Confirm whether auth bypass is intentional for trusted-IP personal use.

### AUDIT-004

- Severity: P1
- Impact scope: notes, mistakes, blog privacy, public read APIs, RSS/sitemap
- Evidence:
  - `backend/app/routers/auth.py:43-48` makes `get_optional_user` always return an admin user.
  - `backend/app/routers/notes.py:70-79` hides drafts/hidden notes only when the user is not admin.
  - `backend/app/routers/notes.py:157-159` blocks hidden/draft detail only when the user is not admin.
- Trigger scenario: Any request that reaches `GET /api/notes` or `GET /api/notes/{slug}` is treated as admin-visible.
- Risk: Hidden and draft notes/mistakes/blogs are returned by public-looking read APIs. With Cloudflare IP restrictions this is mostly a "trusted user sees everything" behavior, but it can still leak private content into RSS/sitemap/frontend caches or accidental screenshots if the API is used from public pages.
- Fix recommendation: Make optional auth genuinely optional. If no valid token exists, return `None` and keep public reads filtered to `hidden=false` and `status=published`. If you want trusted-IP admin reads, expose a separate explicit admin query path.
- Acceptance method: Without a token, a hidden/draft note does not appear in list/detail; with admin token or explicit trusted admin mode, it does.
- Needs manual confirmation: Yes. Confirm intended public/private policy for `note`, `blog`, and `mistake`.

### AUDIT-005

- Severity: P1
- Impact scope: GitHub sync/export, static blog workflow, site config, public assets, repository integrity
- Evidence:
  - `backend/app/routers/sync.py:20-109` exposes push, publish, delete, save-config, batch-edit, save-json-file, and commit endpoints with `get_current_admin`.
  - `backend/app/services/github_sync.py:659-692` can create/update/delete files in `src/` and `public/`; `content_base64 is None` means delete at `backend/app/schemas/sync.py:73-80`.
  - `backend/app/services/github_sync.py:16-21` sends requests with `GITHUB_TOKEN`.
- Trigger scenario: You or a script call sync endpoints from an allowlisted environment, or the backend becomes reachable outside the intended IP boundary.
- Risk: The sync endpoint is powerful enough to rewrite site source/static content. In a personal system, the main practical risks are accidental bulk deletion, bad path input, token over-permission, and making private content public.
- Fix recommendation: Keep the endpoint, but narrow the blast radius:
  - Use a GitHub token scoped only to this repo.
  - Add command-specific path allowlists.
  - Make delete flows explicit and separately confirmed in UI.
  - Log commit target paths before pushing.
- Acceptance method: A dry-run or preview mode lists files that would be written/deleted before actual commit; paths outside intended folders are rejected.
- Needs manual confirmation: Yes. Confirm whether backend GitHub sync is enabled in the deployed backend and what token permissions are granted.

### AUDIT-006

- Severity: P1
- Impact scope: database schema lifecycle, migrations, deployment stability
- Evidence:
  - `backend/main.py:37-38` runs `Base.metadata.create_all` on application startup.
  - Alembic migrations exist under `backend/alembic/versions/`.
- Trigger scenario: Backend starts against a fresh or partially migrated database.
- Risk: `create_all` can create tables without applying the full Alembic history, leaving schema state ambiguous. It also does not handle future schema changes as reliably as migrations. For a personal long-lived system, this can make backup/restore and upgrades harder.
- Fix recommendation: Use Alembic as the only production schema mechanism. If you want convenience for local first-run, gate `create_all` behind an explicit development-only setting.
- Acceptance method: Production startup does not mutate schema implicitly; setup docs say to run `alembic upgrade head` for fresh or restored databases.
- Needs manual confirmation: Yes. Confirm whether the current database already contains long-term personal data.

### AUDIT-007

- Severity: P2
- Impact scope: blog/static sync, path safety, GitHub repository writes
- Evidence:
  - `backend/app/schemas/sync.py:12-27` accepts raw `slug`.
  - `backend/app/services/github_sync.py:244` builds `base_path = f"public/blogs/{req.slug}"`.
  - `backend/app/services/github_sync.py:629-634` checks `save_json_file` prefix/extension but not canonical path traversal.
  - `backend/app/services/github_sync.py:659-662` checks `commit` paths start with `src/` or `public/`.
- Trigger scenario: A manual script, UI bug, or malformed request submits a slug/path containing `..`, double slashes, backslashes, or reserved paths.
- Risk: In a personal system, this is more likely to be accidental damage than attack. A bad slug/path can produce unexpected Git tree entries or delete unintended static files.
- Fix recommendation: Validate slugs with a strict pattern such as `^[a-z0-9][a-z0-9-]{0,254}$`; normalize paths and reject `..`, empty segments, backslashes, control characters, and unexpected prefixes.
- Acceptance method: A small set of path validation tests rejects malformed paths and accepts known valid content paths.
- Needs manual confirmation: Yes. Confirm intended editable path surface for each static management feature.

### AUDIT-008

- Severity: P2
- Impact scope: frontend production API connectivity, RSS, sitemap, notes/blog lists
- Evidence:
  - `src/lib/api/client.ts:1` falls back to `http://localhost:8000`.
  - `src/app/rss.xml/route.ts:12` falls back to `http://localhost:8000`.
  - `src/app/sitemap.ts:4` falls back to `http://localhost:8000`.
  - `tasks-process-keepalive.md:21` records intended `NEXT_PUBLIC_API_URL=https://api.limengyang.me`, but this is not enforced by config.
- Trigger scenario: Frontend is built/deployed without `NEXT_PUBLIC_API_URL`.
- Risk: Production pages or generated routes call localhost instead of the real API, leading to empty RSS/sitemap, failed notes/blog lists, or broken management/write flows.
- Fix recommendation: For production builds, fail fast or show a clear diagnostic when `NEXT_PUBLIC_API_URL` is missing or points to localhost.
- Acceptance method: Production build/deploy uses the intended API URL; RSS and sitemap fetch real backend data.
- Needs manual confirmation: Yes. Confirm whether `https://api.limengyang.me` is the permanent backend URL.

### AUDIT-009

- Severity: P2
- Impact scope: frontend type safety, build confidence
- Evidence:
  - `next.config.ts:9-11` sets `typescript.ignoreBuildErrors = true`.
  - `npx tsc --noEmit` failed with:
    - `src/hooks/use-markdown-render.tsx(93,24): error TS7006: Parameter 'item' implicitly has an 'any' type.`
    - `src/hooks/use-markdown-render.tsx(93,30): error TS7006: Parameter 'index' implicitly has an 'any' type.`
- Trigger scenario: OpenNext/Next build runs while type errors are ignored.
- Risk: For a personal system this is not an immediate blocker, but it weakens confidence that frontend API contracts match backend schemas over time.
- Fix recommendation: Fix current TypeScript errors, then remove `ignoreBuildErrors` or keep it documented as temporary debt.
- Acceptance method: `npx tsc --noEmit` passes locally.
- Needs manual confirmation: No.

### AUDIT-010

- Severity: P2
- Impact scope: backend deploy verification, dependency management
- Evidence:
  - `backend/requirements.txt:1-12` lists backend dependencies.
  - Import check command `PYTHONDONTWRITEBYTECODE=1 python3 -c "import sys; sys.path.insert(0, 'backend'); import main; print(main.app.title)"` failed with `ModuleNotFoundError: No module named 'fastapi'`.
- Trigger scenario: Attempting to verify or run backend from the current active shell environment.
- Risk: The backend cannot be verified from this environment without installing dependencies or activating the correct environment. This is mainly an operability/documentation risk.
- Fix recommendation: Document the backend virtualenv/deployment setup. A small non-secret setup note is enough for a personal system.
- Acceptance method: From the documented environment, importing `main.app` succeeds.
- Needs manual confirmation: Yes. Confirm where the real backend runtime environment lives.

### AUDIT-011

- Severity: P2
- Impact scope: AI cost control, accidental overuse, reliability
- Evidence:
  - `backend/app/routers/ai.py:12-22` uses an in-memory global rate limiter with key `"global"`.
  - `backend/app/routers/ai.py:251-299` protects expensive AI calls through the current admin dependency.
  - `backend/app/routers/ai_polish.py:12-21` rate limits by `user.id`, but current auth returns the same auto-admin user for all callers.
- Trigger scenario: You paste/upload many images quickly, refresh, use multiple tabs, or run multiple backend workers.
- Risk: For a personal IP-limited system, abuse risk is lower. The practical problem is uneven behavior: one global bucket may throttle your own flows, while multi-process/restart behavior may not cap spend consistently.
- Fix recommendation: Keep it simple: add clear UI throttling, request size limits, and optionally a daily cost/request counter in Postgres.
- Acceptance method: Repeated AI calls produce predictable feedback instead of mysterious failures; large image requests are bounded.
- Needs manual confirmation: Yes. Confirm acceptable daily AI usage/cost.

### AUDIT-012

- Severity: P2
- Impact scope: upload hygiene, storage health
- Evidence:
  - `backend/app/routers/notes.py:118-123` trusts `file.content_type` starts with `image/`.
  - `backend/app/routers/notes.py:126` preserves the original filename extension.
  - `backend/app/routers/notes.py:130-137` reads the whole file into memory before enforcing the 10MB limit.
- Trigger scenario: You upload a mislabeled file, a corrupt image, or several near-limit files.
- Risk: The system may store non-image files under image paths, use more memory than needed, or accumulate orphaned uploads.
- Fix recommendation: Verify image headers, canonicalize extensions, and define retention/cleanup behavior for images removed from notes.
- Acceptance method: A corrupt file with `image/png` content type is rejected; deleted/removed image references have a known retention policy.
- Needs manual confirmation: Yes. Confirm whether you prefer keeping orphan images as backups or cleaning them.

### AUDIT-013

- Severity: P2
- Impact scope: markdown rendering safety
- Evidence:
  - `src/lib/markdown-renderer.ts:134-135` drops raw HTML, which is good.
  - `src/lib/markdown-renderer.ts:138-144` injects `token.text` inside anchor HTML without escaping it.
  - `src/lib/markdown-renderer.ts:155-158` injects `token.text` inside heading HTML without escaping it.
  - `src/lib/markdown-renderer.ts:316-318` injects custom highlight text without escaping it.
  - `src/hooks/use-markdown-render.tsx:108-110` uses `dangerouslySetInnerHTML` for KaTeX-rendered math HTML.
- Trigger scenario: AI-generated or pasted markdown contains crafted content in links/headings/highlights/math.
- Risk: Raw HTML is already stripped, which lowers risk. Remaining custom renderers should still be escaped consistently to avoid future surprises.
- Fix recommendation: Escape custom renderer text output and add a small markdown safety test set.
- Acceptance method: Crafted markdown renders as inert text, not executable DOM.
- Needs manual confirmation: Yes before changing rendering behavior for existing posts.

### AUDIT-014

- Severity: P2
- Impact scope: review correctness, date/time behavior
- Evidence:
  - `backend/app/routers/notes.py:197-200` initializes mistake `next_review` with `date.today()`.
  - `backend/app/routers/review.py:19` and `backend/app/routers/review.py:65` use server-local `date.today()`.
  - `backend/app/routers/review.py:44-55` updates SM-2 state using server-side dates.
- Trigger scenario: Backend server timezone differs from your study timezone.
- Risk: Daily review queues can appear early/late, causing confusing stats or missed reviews.
- Fix recommendation: Add a single personal `APP_TIMEZONE`, likely `Asia/Shanghai`, and compute review dates against it.
- Acceptance method: Around midnight, queue and stats match your expected local day.
- Needs manual confirmation: Yes. Confirm intended study timezone.

### AUDIT-015

- Severity: P3
- Impact scope: migration performance, query performance
- Evidence:
  - `backend/alembic/versions/002_add_status_field.py:20-21` adds `idx_notes_status`.
  - `backend/alembic/versions/1119bee5a419_add_images_to_notes.py:20-24` adds `images` but drops `idx_notes_status`.
  - `backend/app/models/note.py:40` has `status` but no status index declaration.
- Trigger scenario: Note table grows and public/admin list filters frequently use `status`.
- Risk: Status filtering may become slower, and migration history contains an unexpected index drop.
- Fix recommendation: Decide whether the status index should exist. If yes, restore it in a migration; if not, document removal.
- Acceptance method: Alembic head and model metadata agree on intended indexes.
- Needs manual confirmation: No.

### AUDIT-016

- Severity: P3
- Impact scope: documentation, production observability
- Evidence:
  - `wrangler.toml:10-18` enables 100% head sampling, invocation logs, and local persist.
- Trigger scenario: Production Cloudflare deployment with verbose logging.
- Risk: Logs may be noisier than needed for a personal system. This is not blocking, especially if CF access is restricted.
- Fix recommendation: Keep logs if useful, but note expected sampling/retention in deployment docs.
- Acceptance method: You know where logs live, how long they retain, and whether request details are acceptable.
- Needs manual confirmation: Yes. Confirm preferred production log verbosity.

## Validation Evidence

- `git status --short`
  - Result at audit start: no output.
- `npx tsc --noEmit`
  - Impact: type-check only, no build output requested.
  - Result: failed.
  - First errors:
    - `src/hooks/use-markdown-render.tsx(93,24): error TS7006: Parameter 'item' implicitly has an 'any' type.`
    - `src/hooks/use-markdown-render.tsx(93,30): error TS7006: Parameter 'index' implicitly has an 'any' type.`
- `PYTHONDONTWRITEBYTECODE=1 python3 -c "import sys; sys.path.insert(0, 'backend'); import main; print(main.app.title)"`
  - Impact: import check only, no service start, no bytecode write requested.
  - Result: failed.
  - First error: `ModuleNotFoundError: No module named 'fastapi'`.

## Recommended Fix Order For This Personal System

1. Decide durable storage for mistake images and make uploads survive redeploys.
2. Decide what content is public, private, or backup-only; prevent private notes/mistakes from exporting to `public/`.
3. Keep Cloudflare IP allowlisting, but either restore app-layer JWT or explicitly mark bypass auth as trusted-IP personal mode.
4. Narrow GitHub sync paths and add a preview/dry-run view before repository writes/deletes.
5. Make Alembic the production schema path; keep `create_all` only for explicit local bootstrap if desired.
6. Fix `NEXT_PUBLIC_API_URL` production config and current TypeScript errors when convenient.
7. Add small guardrails for AI usage, upload validation, markdown escaping, and timezone behavior.

## Human Confirmation Questions

1. Should `note` and `mistake` records ever be visible outside your Cloudflare allowlisted IPs?
2. Should GitHub sync export private notes/mistakes as backup, or only public-facing content?
3. Do you want mistake images stored publicly, IP-restricted, or privately behind app auth?
4. Was auth bypass intentionally chosen because Cloudflare IP allowlisting is the primary gate?
5. Is `https://api.limengyang.me` the permanent backend URL?
6. What timezone should review scheduling use, likely `Asia/Shanghai`?
