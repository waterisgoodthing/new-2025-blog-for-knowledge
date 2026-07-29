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

## Phase 6: Open-Source Structure Audit

Status: completed on 2026-06-16 after user requested a current open-source project structure review.

- [x] **P6-01** Inventory repository-facing open-source files and tracked project structure.
  - Scope: README, license, contribution/security docs, package metadata, environment templates, CI/templates, tests, backend migrations, and workflow records.
  - Completed: 2026-06-16.
  - Evidence: `git status --short`, `git ls-files`, targeted `find`, and direct reads of `README.md`, `package.json`, `CONTRIBUTING.md`, `SECURITY.md`, `backend/.env.example`, `.gitignore`, `backend/app/config.py`, and `LICENSE`.

- [x] **P6-02** Record what is still missing for open-source readiness.
  - Scope: classify required, recommended, and optional gaps without changing product code.
  - Completed: 2026-06-16.
  - Evidence: See `audit.md`.

## Phase 7: Full Open-Source Preparation

Status: completed on 2026-06-16. Materials are mixed Chinese/English.

- [x] **P7-01** Add and complete environment examples.
  - Scope: create root `.env.example`; expand `backend/.env.example` to cover settings in `backend/app/config.py`.
  - Completion standard: examples use placeholders only and do not copy real secrets or local-only production values.
  - Completed: 2026-06-16.
  - Evidence: Root `.env.example` created with `NEXT_PUBLIC_API_URL` and `NEXT_PUBLIC_IMAGE_BASE_URL`. `backend/.env.example` expanded to cover `ENV`, `DATABASE_URL`, `JWT_*`, `ALLOWED_ORIGINS`, `ENABLE_REGISTRATION`, `REGISTRATION_KEY`, `AI_*`, `DASHSCOPE_*`, `DEEPSEEK_*`, `DASHSCOPE_IMAGE_*`, `KEEP_ALIVE_*`, `AUTH_BYPASS*`, `WEBAUTHN_*`, `OPERATOR_REGISTRATION_KEY`, `IMAGE_BASE_URL`. All values are placeholders.

- [x] **P7-02** Add platform-neutral one-command setup/check entry.
  - Scope: add scripts and documented commands for local initialization and repository validation, such as `npm run init`, `npm run setup`, and `npm run check`.
  - Completed: 2026-06-16.
  - Evidence: `scripts/setup.mjs` created with `--check`, `--init`, and `--setup` modes. `package.json` updated with `check`, `init`, and `setup` scripts. Script supports prerequisite detection (Node.js, Python, PostgreSQL, Docker), env file creation, dependency installation, JWT secret generation, database migration, registration mode configuration, operator passkey setup, AI provider preset registry with 14 presets, capability-based assignment (general/text/OCR/image), and masked secret output. Check-only mode validated successfully.

- [x] **P7-03** Update README for full open-source setup.
  - Scope: add database bootstrap, Alembic migration, validation command matrix, contributor navigation, configuration notes, setup/check command usage, AI setup behavior, and admin credential guidance.
  - Completed: 2026-06-16.
  - Evidence: `README.md` rewritten with quick-start section (check/init/setup), manual setup guide, database bootstrap with Alembic, admin credential setup, validation command matrix table, configuration tables (env vars, AI providers, admin credentials), architecture navigation (backend/frontend layers), and contributor links.

- [x] **P7-04** Add GitHub Actions CI baseline.
  - Scope: create `.github/workflows/ci.yml` for frontend install/typecheck/build and backend install/test/import checks.
  - Completed: 2026-06-16.
  - Evidence: `.github/workflows/ci.yml` created with frontend job (Node.js 20, npm ci, tsc, build) and backend job (Python 3.12, PostgreSQL 16 service container, pip install, import check, pytest). Does not require production secrets.

- [x] **P7-05** Update package metadata for public repository identity.
  - Scope: add `license`, `repository`, `bugs`, and `homepage` metadata using verified repository evidence.
  - Completed: 2026-06-16.
  - Evidence: `package.json` updated with `license: "MIT"`, `repository` pointing to `https://github.com/waterisgoodthing/new-2025-blog-for-knowledge.git`, `bugs` and `homepage` URLs derived from repository. `"private": true` preserved.

- [x] **P7-06** Add GitHub issue and pull request templates.
  - Scope: create bug report and feature request issue templates plus PR template under `.github/`.
  - Completed: 2026-06-16.
  - Evidence: `.github/ISSUE_TEMPLATE/bug_report.yml` (description, steps, environment, screenshots, security impact), `.github/ISSUE_TEMPLATE/feature_request.yml` (motivation, proposal, alternatives, context), `.github/pull_request_template.md` (summary, changes, testing, screenshots, security/env checklist). All mixed Chinese/English.

- [x] **P7-07** Re-check tracked structure and ignored local artifacts.
  - Scope: verify `.github/`, env examples, scripts, and metadata are tracked candidates; confirm `.env`, virtualenvs, caches, generated outputs, and unrelated dirty files remain excluded.
  - Completed: 2026-06-16.
  - Evidence: `git check-ignore` confirmed all new files are NOT ignored; `.env`, `backend/.env`, `backend/.venv/`, `__pycache__/`, `*.pyc`, `.next/`, `.output/`, `node_modules/` are properly excluded.

- [x] **P7-08** Run final validation and record results.
  - Scope: run targeted frontend/backend checks feasible in the local environment, run setup/check dry-run or check-only paths, inspect new docs/templates, and verify secret-safety behavior.
  - Completed: 2026-06-16.
  - Evidence: See `validation.md` Phase 7 section. TypeScript check PASS, backend import PASS, setup check-only PASS (4 expected warnings), file tracking PASS, secret exclusion PASS.

- [x] **P7-09** Review Phase 7 closure.
  - Scope: compare implemented files against `requirements.md`, `design.md`, `tasks.md`, and `audit.md`.
  - Completed: 2026-06-16.
  - Evidence: See closure review below.

### Phase 7 Closure Review

**Requirements coverage:**

| Req | Description | Status |
|---|---|---|
| 11 | CI provides PR health baseline | ✅ P7-04 |
| 12 | Env examples cover frontend + backend settings | ✅ P7-01 |
| 13 | Database bootstrap with Alembic documented | ✅ P7-03 |
| 14 | package.json has repo metadata | ✅ P7-05 |
| 15 | `npm run init/setup/check` exist | ✅ P7-02 |
| 16 | Two setup modes (conservative + fuller) | ✅ P7-02 |
| 17 | Missing tool detection + explicit permission | ✅ P7-02 |
| 18 | AI config can be skipped | ✅ P7-02 |
| 19 | Multiple AI providers + custom | ✅ P7-02 |
| 20 | Provider presets mapped via OpenAI-compatible | ✅ P7-02 |
| 21 | Check-only/dry-run path | ✅ P7-02 |
| 22 | AI capability labels (general/text/OCR/image) | ✅ P7-02 |

**Audit gap coverage:**

| Gap | Status |
|---|---|
| No CI workflow | ✅ Closed |
| No issue/PR templates | ✅ Closed |
| No frontend env template | ✅ Closed |
| backend/.env.example incomplete | ✅ Closed |
| Database bootstrap under-documented | ✅ Closed |
| package.json sparse metadata | ✅ Closed |

**Deferred items (out of approved scope):**

1. **Docker Compose**: explicitly deferred per `design.md`. Setup script detects Docker and prints guidance but does not automate database creation.
2. **CODEOWNERS / support policy**: optional for personal project, not in approved scope.
3. **Upstream project URL**: requires external information not available in repository evidence.
4. **Setup script cross-platform testing**: validated on macOS; Linux/Windows testing needed before external contributors rely on it.

**Verdict**: Phase 7 is **closed**. All 9 tasks completed. All required gaps from `audit.md` are addressed. All acceptance criteria from `requirements.md` that are in scope are met. Residual risks are recorded in `validation.md`.
