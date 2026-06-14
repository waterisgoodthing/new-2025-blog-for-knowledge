# Tasks

## Phase 0: Inventory And Boundary Mapping

- [x] **P0-01** Inventory every frontend GitHub sync call site and UI entry point.
  - Completed: 2026-06-10.

- [x] **P0-02** Inventory every backend GitHub sync route and service dependency.
  - Completed: 2026-06-10.

- [x] **P0-03** Classify active content domains into backend-managed vs intentionally static.
  - Completed: 2026-06-10.

## Phase 1: Remove GitHub Sync From Supported Product Flows

- [x] **P1-01** Introduce backend contracts for legacy static editable domains.
  - Completed: 2026-06-10.
  - Evidence: Backend model `ManagedContentEntry` (`backend/app/models/content.py`), schemas (`backend/app/schemas/content.py`), router (`backend/app/routers/content.py`), service (`backend/app/services/content_store.py`), and Alembic migration (`backend/alembic/versions/010_add_managed_content_entries.py`) were already in place from prior work. All 7 domains covered: about, shares, projects, pictures, snippets, bloggers, site-settings. Image upload/delete endpoints also included.

- [x] **P1-02** Switch frontend editing flows from GitHub sync helpers to backend APIs.
  - Completed: 2026-06-10.
  - Evidence:
    - Created `src/lib/api/content.ts` with typed API client for all content domains.
    - Rewrote all 7 push services to use backend content API instead of GitHub sync:
      - `src/app/about/services/push-about.ts` -> `updateAbout()`
      - `src/app/share/services/push-shares.ts` -> `updateShares()` + `uploadContentImage()`
      - `src/app/projects/services/push-projects.ts` -> `updateProjects()` + `uploadContentImage()`
      - `src/app/pictures/services/push-pictures.ts` -> `updatePictures()` + `uploadContentImage()` + `deleteContentImage()`
      - `src/app/snippets/services/push-snippets.ts` -> `updateSnippets()`
      - `src/app/bloggers/services/push-bloggers.ts` -> `updateBloggers()` + `uploadContentImage()`
      - `src/app/(home)/services/push-site-content.ts` -> `updateSiteSettings()` + `uploadContentImage()` + `deleteContentImage()`
    - Rewrote all 7 page components to load data from backend API via `useEffect` + `get*()` calls instead of static JSON imports:
      - `src/app/about/about-content.tsx`
      - `src/app/share/page.tsx`
      - `src/app/projects/page.tsx`
      - `src/app/pictures/page.tsx`
      - `src/app/snippets/page.tsx`
      - `src/app/bloggers/page.tsx`
      - `src/app/(home)/config-dialog/site-settings-panel.tsx`

- [x] **P1-03** Remove backend sync routes from the application surface.
  - Completed: 2026-06-10.
  - Evidence: `backend/app/routers/sync.py` deleted. `backend/main.py` no longer imports or mounts `sync.router`.

- [x] **P1-04** Remove backend GitHub write service code from the active architecture.
  - Completed: 2026-06-10.
  - Evidence: `backend/app/services/github_sync.py` and `backend/app/schemas/sync.py` deleted. `GITHUB_TOKEN`, `GITHUB_OWNER`, `GITHUB_REPO`, `GITHUB_BRANCH` removed from `backend/app/config.py` and `backend/.env`.

- [x] **P1-05** Remove frontend GitHub auth/client helpers and config that are no longer needed.
  - Completed: 2026-06-10.
  - Evidence:
    - Deleted: `src/lib/api/sync.ts`, `src/lib/github-client.ts`, `src/lib/auth.ts`, `src/lib/blog-index.ts`, `src/hooks/use-auth.ts`, `src/lib/aes256-util.ts`.
    - `src/consts.ts` no longer exports `GITHUB_CONFIG`.
    - `src/lib/api/meta.ts` no longer exports `syncPush()` or `SyncResult`.
    - `use-blog-index.ts` updated to use backend `/api/auth/me` for admin check instead of old GitHub auth store.
    - All page components no longer import `useAuthStore`.
    - Manage page "sync" tab removed.

## Phase 2: Public/Private Content Safety

- [x] **P2-01** Enforce safe anonymous filtering in note list/detail APIs.
  - Completed: 2026-06-10.
  - Evidence: `backend/app/routers/notes.py` updated:
    - `list_notes`: non-admin queries now enforce `Note.hidden == False` and `Note.status == "published"`.
    - `get_note`: non-admin access to hidden or non-published notes now returns 404.

- [x] **P2-02** Re-check admin-only UI affordances after sync removal.
  - Completed: 2026-06-10.
  - Evidence: The "sync" tab in the manage page (`src/app/manage/page.tsx`) has been removed. No stale sync controls remain in public pages.

## Phase 3: Open-Source Readiness Cleanup

- [x] **P3-01** Align README with the actual package manager and local run path.
  - Completed: 2026-06-10.
  - Evidence: `README.md` updated to use `npm install` / `npm run dev` matching `package-lock.json`. Backend setup instructions updated. Source-of-truth table added.

- [x] **P3-02** Add baseline open-source collaboration docs.
  - Completed: 2026-06-10.
  - Evidence: `CONTRIBUTING.md` and `SECURITY.md` created.

- [x] **P3-03** Document post-sync source-of-truth rules.
  - Completed: 2026-06-10.
  - Evidence: `README.md` includes a content source-of-truth table showing all domains are backend-managed via PostgreSQL.

## Phase 4: Validation And Handoff

- [x] **P4-01** Run frontend validation and record results.
  - Completed: 2026-06-10.
  - Evidence: `npx tsc --noEmit` passes with zero errors.

- [x] **P4-02** Run targeted backend checks and record environment blockers if any.
  - Completed: 2026-06-10.
  - Evidence: `python -c "from main import app"` passes. Backend starts cleanly.

- [x] **P4-03** Record final residual risks and follow-up items.
  - Completed: 2026-06-10.
  - Evidence: See `validation.md`.

## Phase 5: GitHub-Facing Chinese Content And Attribution

Status: completed on 2026-06-14 after user approval.

- [x] **P5-01** Inspect repository-facing docs and license evidence for upstream-origin details.
  - Scope: `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `LICENSE`, package metadata if relevant.
  - Completion standard: known upstream details are identified from repository evidence, or missing details are explicitly recorded.
  - Completed: 2026-06-14.
  - Evidence: `LICENSE` is MIT with copyright `YYsuni`; `package.json` has no repository/homepage/author metadata; `git remote -v` shows only the current `mine` remote; no `NOTICE`/`AUTHORS`/`CREDITS` file was found; early git history identifies `Suni <YYsuni1001@gmail.com>` commits but no upstream URL.

- [x] **P5-02** Rewrite `README.md` in Chinese as the primary GitHub landing document.
  - Scope: project overview, architecture lines, local setup, content source-of-truth, configuration, no-GitHub-write-access note.
  - Required attribution: include a visible Chinese source/thanks section stating that the project is adapted from an original open-source project.
  - Completed: 2026-06-14.
  - Evidence: `README.md` is now Chinese-first and includes `来源与致谢`, architecture lines, local development commands, content source-of-truth table, configuration notes, and the no-GitHub-write-access statement.

- [x] **P5-03** Rewrite `CONTRIBUTING.md` in Chinese.
  - Scope: setup workflow, code style, architecture boundaries, validation requirements, PR guidance.
  - Completed: 2026-06-14.
  - Evidence: `CONTRIBUTING.md` is now Chinese-first and covers setup, tech stack, architecture boundaries, validation, PR expectations, and issue reporting.

- [x] **P5-04** Rewrite `SECURITY.md` in Chinese.
  - Scope: vulnerability reporting, security scope, environment and secret handling guidance.
  - Completed: 2026-06-14.
  - Evidence: `SECURITY.md` is now Chinese-first and covers private vulnerability reporting, security scope, environment secret handling, production JWT/CORS guidance, and source/license note.

- [x] **P5-05** Validate documentation changes and update workflow records.
  - Scope: inspect changed files for Chinese primary language, attribution wording, command/path correctness, and license preservation.
  - Output: update `validation.md` with changed files, validation evidence, and any attribution limits.
  - Completed: 2026-06-14.
  - Evidence: `validation.md` records changed files, source/license inspection, Chinese documentation inspection, link/command inspection, and the upstream URL attribution limit.
