# Validation

## Date: 2026-06-10

## Frontend Validation

### TypeScript Check

```
npx tsc --noEmit
```

Result: **PASS** - zero errors.

### Source Inspection

**Sync removal:**
- No remaining imports of `src/lib/api/sync.ts`, `src/lib/github-client.ts`, `src/lib/auth.ts`, `src/hooks/use-auth.ts`, `src/lib/blog-index.ts`, or `src/lib/aes256-util.ts`.
- No remaining references to `GITHUB_CONFIG` or `NEXT_PUBLIC_GITHUB_*` env vars in frontend code.
- No remaining calls to `syncPush()` in `src/lib/api/meta.ts`.
- All 7 legacy static-content pages now load from backend API via `get*()` calls.
- All 7 push services now use `update*()` and `uploadContentImage()` from `src/lib/api/content.ts`.
- Manage page "sync" tab removed.

**Site settings backend闭环:**
- `src/components/site-settings-loader.tsx` fetches from `GET /api/content/site-settings` on mount and hydrates the Zustand store, applies theme CSS variables, updates favicon, and sets document title.
- `src/layout/index.tsx` renders `<SiteSettingsLoader />` so every page gets backend values on client load.
- `src/app/(home)/stores/config-store.ts` `SiteContent` type now includes `faviconUrl` and `avatarUrl`.

**Edit mode permission gating:**
- All editable pages (about, share, projects, pictures, snippets, bloggers, blog) now use `useAdminAuth()` hook to gate edit button visibility: `isAdmin && !hideEditButton && (...)`.
- `src/hooks/use-admin-auth.ts` calls `GET /api/auth/me` via SWR to check admin session.
- Anonymous users no longer see edit buttons.

**favicon/avatar consumption:**
- `src/components/nav-card.tsx` uses `siteContent.avatarUrl || '/images/avatar.png'` for avatar images.
- `src/components/vertical-nav.tsx` uses `siteContent.avatarUrl || '/images/avatar.png'`.
- `src/app/(home)/hi-card.tsx` uses `siteContent.avatarUrl || '/images/avatar.png'`.
- `src/app/(home)/config-dialog/site-settings/favicon-avatar-upload.tsx` uses `siteContent.avatarUrl` for preview.
- `SiteSettingsLoader` applies `faviconUrl` to `<link rel="icon">` dynamically.

## Backend Validation

### Import Check

```
python -c "from main import app"
```

Result: **PASS** - backend imports cleanly.

### Source Inspection

- `backend/app/routers/sync.py` deleted.
- `backend/app/services/github_sync.py` deleted.
- `backend/app/schemas/sync.py` deleted.
- `backend/main.py` no longer imports or mounts `sync.router`.
- `backend/app/config.py` no longer defines `GITHUB_TOKEN`, `GITHUB_OWNER`, `GITHUB_REPO`, `GITHUB_BRANCH`.
- `backend/.env` and `backend/.env.example` cleaned of GitHub config.

### Notes Public Boundary

- `GET /api/notes` for anonymous users now filters: `Note.hidden == False AND Note.status == "published"`.
- `GET /api/notes/{slug}` for anonymous users now returns 404 for hidden or non-published notes.

## Behavior Verification (Manual)

| Check | Status | Notes |
|---|---|---|
| Site settings load from backend on page visit | Requires runtime | `SiteSettingsLoader` calls `GET /api/content/site-settings` |
| Theme CSS variables applied from backend | Requires runtime | `SiteSettingsLoader.applyThemeVariables()` |
| Favicon updated from backend `faviconUrl` | Requires runtime | `SiteSettingsLoader.applyFavicon()` |
| Avatar uses backend `avatarUrl` | Verified | nav-card, vertical-nav, hi-card all use store value |
| Edit buttons hidden for anonymous users | Verified | All pages use `useAdminAuth()` gate |
| Edit buttons shown for admin users | Requires runtime | `isAdmin && !hideEditButton` |
| about page load/save via backend API | Requires runtime | `GET/PUT /api/content/about` |
| share/projects/pictures/bloggers/snippets | Requires runtime | `GET/PUT /api/content/*` + image upload |
| site settings save via backend API | Requires runtime | `PUT /api/content/site-settings` + image upload |
| Anonymous cannot see hidden notes | Requires runtime | Backend filters applied |
| Anonymous cannot see draft notes | Requires runtime | Backend filters applied |
| Frontend has no sync API calls | Verified | Source inspection confirmed |
| Manage page has no sync tab | Verified | Source inspection confirmed |

## Environment Blockers

- Full runtime behavior verification requires a running PostgreSQL instance and backend server. The validation above covers static analysis (TypeScript + Python import check) and source inspection. Runtime verification should be done in a staging environment.

## Residual Risks

1. **`Base.metadata.create_all` in `backend/main.py`**: The startup `create_all` call remains. This is acceptable for this round but should be retired in favor of Alembic-only migrations in a future cleanup.

2. **`jsrsasign` npm dependency**: No longer used by any frontend code after `src/lib/github-client.ts` removal. Can be removed from `package.json` in a follow-up cleanup.

3. **Static JSON seed files**: Files like `src/app/about/list.json`, `src/app/share/list.json`, etc. still exist in the repo. They are now only used as default seed data by `backend/app/services/content_store.py` for first-time database initialization. They are no longer imported by frontend pages.

4. **`src/lib/api/content.ts` schema types**: The frontend content API types duplicate the backend Pydantic schemas. A future improvement could generate frontend types from backend schemas.

5. **`create_all` vs Alembic**: The `ManagedContentEntry` table is created both by Alembic migration `010` and by `Base.metadata.create_all` at startup. This dual-track should be resolved in a future cleanup.

6. **Server-side metadata**: `src/app/layout.tsx` still reads static `site-content.json` for Next.js `Metadata` export (SEO). The client-side `SiteSettingsLoader` overrides visual state but SSR `<meta>` tags will show static defaults until a server-side data fetching strategy is added.

## Date: 2026-06-14

## Phase 5 Documentation Validation

### Scope

GitHub-facing documentation only. No runtime source code was changed.

Changed files:

- `README.md`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `docs/workflows/open-source-closure/README.md`
- `docs/workflows/open-source-closure/requirements.md`
- `docs/workflows/open-source-closure/design.md`
- `docs/workflows/open-source-closure/tasks.md`
- `docs/workflows/open-source-closure/validation.md`

### Source And License Inspection

Result: **PASS with attribution limit recorded**.

- `LICENSE` was inspected and left unchanged.
- License evidence: MIT License, copyright `YYsuni`.
- `package.json` was inspected and does not contain repository, homepage, author, or upstream metadata.
- `git remote -v` shows only the current `mine` remote.
- No top-level `NOTICE`, `AUTHORS`, `CREDITS`, or acknowledgement file was found.
- Early git history shows commits by `Suni <YYsuni1001@gmail.com>`, but no upstream URL.

Attribution limit: the repository currently supports stating that this project is adapted from an original open-source project and that the preserved license copyright is `YYsuni`. It does not provide enough evidence to name or link an upstream repository.

### Chinese Documentation Inspection

Result: **PASS**.

- `README.md` is Chinese-first and includes `来源与致谢`, project structure, local development, content source-of-truth, configuration, no-GitHub-write-access note, and contribution/security links.
- `CONTRIBUTING.md` is Chinese-first and includes setup, tech stack, architecture boundaries, validation expectations, PR guidance, and issue reporting.
- `SECURITY.md` is Chinese-first and includes private vulnerability reporting, security scope, environment security, JWT/CORS guidance, and source/license note.

### Link And Command Inspection

Result: **PASS**.

- `README.md` links point to existing `CONTRIBUTING.md` and `SECURITY.md`.
- Commands preserved from verified setup docs: `npm install`, `npm run dev`, `python -m venv .venv`, `source .venv/bin/activate`, `pip install -r requirements.txt`, `cp .env.example .env`, `uvicorn main:app --reload`.
- No code validation was run because this phase changed documentation only.

### Residual Follow-Up

If the original upstream repository URL is later confirmed, update `README.md` `来源与致谢` with the exact project name, link, and any additional attribution required by the upstream project.
## 2026-06-16 Open-Source Structure Audit

Touched domain: shared infrastructure.

Commands and evidence:

- `git status --short`: confirmed unrelated dirty work exists in notes/AI files and the notes workspace workflow; this audit did not touch those files.
- `git ls-files`: confirmed `.github/` is absent and local `backend/.env`, `backend/.venv/`, `__pycache__/`, and `*.pyc` are not tracked.
- Direct reads: `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `LICENSE`, `package.json`, `.gitignore`, `backend/.env.example`, and `backend/app/config.py`.
- File inventory: confirmed backend Alembic migrations and targeted backend tests exist.

Result:

- Open-source baseline exists.
- Remaining missing structure is documented in `audit.md`.
- No product code was changed.

## 2026-06-16 Phase 7 Full Open-Source Preparation

Touched domain: shared infrastructure.

### Changed Files

| File | Action | Task |
|---|---|---|
| `.env.example` | Created | P7-01 |
| `backend/.env.example` | Expanded | P7-01 |
| `scripts/setup.mjs` | Created | P7-02 |
| `package.json` | Updated (metadata + scripts) | P7-02, P7-05 |
| `README.md` | Rewritten | P7-03 |
| `.github/workflows/ci.yml` | Created | P7-04 |
| `.github/ISSUE_TEMPLATE/bug_report.yml` | Created | P7-06 |
| `.github/ISSUE_TEMPLATE/feature_request.yml` | Created | P7-06 |
| `.github/pull_request_template.md` | Created | P7-06 |

### Frontend TypeScript Check

```
npx tsc --noEmit
```

Result: **PASS** — zero errors.

### Backend Import Check

```
cd backend && python -c "from main import app"
```

Result: **PASS** — backend imports cleanly.

### Setup Script Check-Only

```
node scripts/setup.mjs --check
```

Result: **PASS** — 4 warnings (all expected for current environment):
- Docker not found (not required; PostgreSQL is running locally).
- Root `.env` missing (will be created by `npm run init` or `npm run setup`).
- Port 2025 in use (frontend dev server is running).
- Port 8000 in use (backend server is running).

### New File Tracking Check

```
git check-ignore .env.example .github/workflows/ci.yml scripts/setup.mjs .github/ISSUE_TEMPLATE/bug_report.yml .github/pull_request_template.md
```

Result: **PASS** — none of the new files are ignored by `.gitignore`.

### Secret/Cache Exclusion Check

```
git check-ignore .env backend/.env backend/.venv/ __pycache__/ *.pyc .next/ .output/ node_modules/
```

Result: **PASS** — all secrets, caches, and generated outputs are properly excluded.

### Environment Example Inspection

- Root `.env.example`: documents `NEXT_PUBLIC_API_URL` and `NEXT_PUBLIC_IMAGE_BASE_URL` with placeholders.
- `backend/.env.example`: covers all settings in `backend/app/config.py` including `ENV`, `DATABASE_URL`, `JWT_*`, `ALLOWED_ORIGINS`, `ENABLE_REGISTRATION`, `REGISTRATION_KEY`, `AI_*`, `DASHSCOPE_*`, `DEEPSEEK_*`, `DASHSCOPE_IMAGE_*`, `KEEP_ALIVE_*`, `AUTH_BYPASS*`, `WEBAUTHN_*`, `OPERATOR_REGISTRATION_KEY`, `IMAGE_BASE_URL`.
- All examples use placeholder values only; no real secrets or local-only production values.

### Package Metadata Inspection

- `license`: MIT ✓
- `repository`: points to `https://github.com/waterisgoodthing/new-2025-blog-for-knowledge.git` ✓
- `bugs`: points to issues URL ✓
- `homepage`: points to repository readme ✓
- `"private": true` preserved ✓

### CI Workflow Inspection

- `.github/workflows/ci.yml`: runs frontend install/typecheck/build and backend install/import/test.
- Uses PostgreSQL service container for backend tests.
- Does not require production secrets.

### Template Inspection

- Bug report: Chinese/English mixed, collects description, steps, environment, screenshots, security impact.
- Feature request: Chinese/English mixed, collects motivation, proposal, alternatives, context.
- PR template: Chinese/English mixed, collects summary, changes, testing, screenshots, security/env checklist.

### Residual Risks

1. **Setup script is new and untested in diverse environments**: `scripts/setup.mjs` has been validated in check-only mode on the current macOS environment. It should be tested on Linux and Windows before relying on it for external contributors.
2. **CI workflow uses ubuntu-latest**: should be verified on first PR push.
3. **Docker Compose is deferred**: the setup script detects Docker and prints guidance, but does not provide automated Docker-backed PostgreSQL. This is acceptable per design.md decision.
4. **Upstream attribution limit remains**: the upstream project URL is still unknown from repository evidence.
