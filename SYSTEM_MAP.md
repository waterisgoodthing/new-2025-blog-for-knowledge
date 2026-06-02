# SYSTEM_MAP.md

Audit time: 2026-06-01 15:12:03 CST

Scope: system-level review only. No business code, secrets, database data, or production config were modified.

## 1. Repository Status

- `git status --short`: no output observed at audit start, so the worktree appeared clean before report files were generated.
- Touched domain for this audit: shared infrastructure, auth, notes, mistakes, review, blog, sync, manage, AI, upload, deployment.

## 2. High-Level Architecture

This repository has two active architectural lines:

- Frontend and original static-blog system: Next.js App Router under `src/`.
- Personal knowledge backend: FastAPI, PostgreSQL, JWT auth, notes, mistakes, review, AI, and GitHub sync under `backend/`.

## 3. Frontend Framework

- Framework: Next.js App Router.
- Evidence: `package.json:6-13` defines `next dev`, `next build`, OpenNext Cloudflare build/preview/deploy scripts.
- Runtime versions: `next@16.0.10`, `react@19.2.1`, `react-dom@19.2.0`.
- Main route root: `src/app/`.
- Shared components: `src/components/`.
- Shared API clients: `src/lib/api/`.
- Shared hooks: `src/hooks/`.
- Static/generated public content: `public/`.

## 4. Backend Framework

- Framework: FastAPI.
- Evidence: `backend/main.py:51` creates `FastAPI(title="Blog + Notes + Mistakes API", version="1.0.0")`.
- Dependencies: `backend/requirements.txt:1-12` includes FastAPI, Uvicorn, SQLAlchemy asyncio, asyncpg, Alembic, python-jose, bcrypt, httpx, Pydantic settings.
- Router registration: `backend/main.py:64-72` includes auth, notes, review, tags, sync, music, recommendations, AI, and AI polish routers.

## 5. Database And ORM

- Database: PostgreSQL through `postgresql+asyncpg`.
- Evidence: `backend/app/config.py:7` default `DATABASE_URL` uses PostgreSQL asyncpg.
- ORM: SQLAlchemy async.
- Evidence: `backend/app/database.py:8-9` creates async engine and async sessionmaker.
- Migration tool: Alembic.
- Evidence: `backend/alembic.ini`, `backend/alembic/env.py`, and `backend/alembic/versions/`.
- Main domain model: `Note`.
- Evidence: `backend/app/models/note.py:32-70`.

## 6. Core Data Model

- `Note.type` supports `note`, `blog`, and `mistake`.
- Backend enum evidence: `backend/app/schemas/note.py:8-12`.
- Frontend API type evidence: `src/lib/api/notes.ts:3-24`.
- Mistake fields are first-class backend columns:
  - `subject`, `difficulty`, `question`, `my_answer`, `correct_answer`, `analysis`, `knowledge_points`, `ef`, `interval`, `repetitions`, `next_review`, `last_reviewed`.
  - Evidence: `backend/app/models/note.py:49-60`.
- Mistake images are stored in JSON column `images`.
- Evidence: `backend/app/models/note.py:61`, `backend/app/schemas/note.py:45`, `src/lib/api/notes.ts:23`.

## 7. AI Interface Locations

- Image/text mistake analysis router: `backend/app/routers/ai.py`.
- OCR model call: `backend/app/services/ai_service.py:8-17`, using DashScope-compatible endpoint by default.
- Text model call: `backend/app/services/ai_service.py:20-29`, using DeepSeek-compatible endpoint by default.
- AI polish stream router: `backend/app/routers/ai_polish.py`.
- AI polish service: `backend/app/services/ai_polish_service.py`.
- Frontend clients:
  - `src/lib/api/ai.ts`
  - `src/lib/api/ai-polish.ts`
- Frontend usage examples:
  - `src/app/write-mistake/page.tsx:61-87` uploads images and then sends base64 images to AI analysis.

## 8. File Upload And Storage

- Backend note image upload endpoint: `POST /api/notes/upload-image`.
- Evidence: `backend/app/routers/notes.py:112-139`.
- Storage path: local repository filesystem at `public/images/pictures`.
- Evidence: `backend/app/routers/notes.py:108-109`.
- Returned URL: `/images/pictures/{filename}`.
- Evidence: `backend/app/routers/notes.py:139`.
- Blog/static asset upload for original static workflow uses GitHub tree/blob APIs.
- Evidence: `backend/app/services/github_sync.py:237-359`, `408-563`, `659-692`.

## 9. Auth And Security Model

- Frontend backend JWT token storage: browser `localStorage`.
- Evidence: `src/lib/api/auth.ts:18-20`, `src/lib/api/client.ts:10-28`.
- Backend JWT utility exists.
- Evidence: `backend/app/utils/auth.py:19-29`.
- Backend auth dependency currently bypasses JWT verification and returns or creates an admin user.
- Evidence: `backend/app/routers/auth.py:16-40`.
- Optional user dependency also returns admin.
- Evidence: `backend/app/routers/auth.py:43-48`.
- Production startup checks exist for default JWT key and wildcard CORS.
- Evidence: `backend/main.py:17-35`.

## 10. GitHub Sync / Export

- Backend sync router: `backend/app/routers/sync.py`.
- Main GitHub sync service: `backend/app/services/github_sync.py`.
- GitHub API auth uses `GITHUB_TOKEN`.
- Evidence: `backend/app/services/github_sync.py:16-21`.
- Notes export writes:
  - `public/notes/index.json`
  - `public/notes/{slug}/config.json`
  - `public/notes/{slug}/index.md`
  - `public/notes/tags.json`
  - `public/notes/subjects.json`
  - `public/notes/categories.json`
- Evidence: `backend/app/services/github_sync.py:95-182`.
- Static blog publish/delete/config workflows modify `public/` and `src/config/`.
- Evidence: `backend/app/services/github_sync.py:237-692`.

## 11. Deployment Shape

- Frontend deployment target: OpenNext on Cloudflare Workers.
- Evidence: `package.json:10-13`, `wrangler.toml:1-8`, `open-next.config.ts`.
- Cloudflare observability enabled with invocation logs.
- Evidence: `wrangler.toml:10-18`.
- Backend deployment shape is not fully declared in a Dockerfile/compose file in the current file list. It appears intended to run as a separate FastAPI service with environment variables from `.env`.
- Evidence: `backend/main.py`, `backend/.env.example`, `backend/app/config.py`.

## 12. Environment Variable Loading

- Backend uses Pydantic Settings and `.env`.
- Evidence: `backend/app/config.py:5-35`.
- Important backend env vars:
  - `ENV`
  - `DATABASE_URL`
  - `JWT_SECRET_KEY`
  - `ALLOWED_ORIGINS`
  - `ENABLE_REGISTRATION`
  - `REGISTRATION_KEY`
  - `AI_API_KEY`
  - `DASHSCOPE_API_KEY`
  - `DEEPSEEK_API_KEY`
  - `GITHUB_TOKEN`
  - `GITHUB_OWNER`
  - `GITHUB_REPO`
  - `GITHUB_BRANCH`
- Frontend backend API base:
  - `NEXT_PUBLIC_API_URL`, fallback `http://localhost:8000`.
  - Evidence: `src/lib/api/client.ts:1`, `src/app/rss.xml/route.ts:12`, `src/app/sitemap.ts:4`.
- Frontend site URL:
  - `NEXT_PUBLIC_SITE_URL`, fallback `http://localhost:2025`.
  - Evidence: `src/app/rss.xml/route.ts:7`.

## 13. Main Frontend Routes

- Home: `src/app/(home)/page.tsx`
- Blog list/detail/write:
  - `src/app/blog/page.tsx`
  - `src/app/blog/[id]/page.tsx`
  - `src/app/write/page.tsx`
  - `src/app/write/[slug]/page.tsx`
- Notes:
  - `src/app/notes/page.tsx`
  - `src/app/notes/[id]/page.tsx`
  - `src/app/write-note/page.tsx`
  - `src/app/write-note/[slug]/page.tsx`
- Mistakes/review:
  - `src/app/mistakes/page.tsx`
  - `src/app/mistakes/review/page.tsx`
  - `src/app/write-mistake/page.tsx`
- Management:
  - `src/app/manage/page.tsx`
- Static content routes:
  - `src/app/about/page.tsx`
  - `src/app/projects/page.tsx`
  - `src/app/pictures/page.tsx`
  - `src/app/share/page.tsx`
  - `src/app/snippets/page.tsx`
  - `src/app/bloggers/page.tsx`
- Generated routes:
  - `src/app/rss.xml/route.ts`
  - `src/app/sitemap.ts`

## 14. Main Backend Routes

- Auth: `backend/app/routers/auth.py`
- Notes and image upload: `backend/app/routers/notes.py`
- Review: `backend/app/routers/review.py`
- Tags: `backend/app/routers/tags.py`
- Subjects: `backend/app/routers/subjects.py`
- Categories: `backend/app/routers/categories.py`
- GitHub sync/static file write: `backend/app/routers/sync.py`
- AI analysis: `backend/app/routers/ai.py`
- AI polish: `backend/app/routers/ai_polish.py`
- Music: `backend/app/routers/music.py`
- Recommendations: `backend/app/routers/recommendations.py`

## 15. Validation Commands Run

- `npx tsc --noEmit`
  - Impact: type-check only, no build output requested.
  - Result: failed.
  - First failures:
    - `src/hooks/use-markdown-render.tsx(93,24): error TS7006: Parameter 'item' implicitly has an 'any' type.`
    - `src/hooks/use-markdown-render.tsx(93,30): error TS7006: Parameter 'index' implicitly has an 'any' type.`
- `PYTHONDONTWRITEBYTECODE=1 python -c "..."`
  - Result: failed because `python` command was not found.
- `PYTHONDONTWRITEBYTECODE=1 python3 -c "import sys; sys.path.insert(0, 'backend'); import main; print(main.app.title)"`
  - Impact: import check only, no service start, no bytecode write requested.
  - Result: failed because `fastapi` is not installed in the active Python environment.
