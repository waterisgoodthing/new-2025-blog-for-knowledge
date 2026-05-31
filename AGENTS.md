# Agent Architecture Rules

This file is mandatory for all AI agents working in this repository. Read it before inspecting or editing code. If a user request conflicts with this file, ask for explicit confirmation before breaking these rules.

## Project Shape

This project has two active architectural lines:

1. Frontend and original static-blog system: Next.js App Router under `src/`.
2. Personal knowledge backend: FastAPI, PostgreSQL, JWT auth, notes, mistakes, review, AI, and GitHub sync under `backend/`.

Do not blur these lines accidentally. Every change must state which line it affects.

## Required First Steps

Before making code changes:

1. Check `git status --short`.
2. Identify the touched domain: `blog`, `notes`, `mistakes`, `review`, `auth`, `sync`, `home`, `share`, `manage`, or shared infrastructure.
3. Read the existing files in that domain before editing.
4. Prefer existing patterns over new abstractions.
5. Preserve user changes and generated content. Never revert unrelated dirty files.

## Frontend Boundaries

Use these ownership rules:

- `src/app/<route>/page.tsx`: route-level UI and page composition only.
- `src/app/<route>/components/`: route-specific UI components.
- `src/app/<route>/services/`: client-side services tied to that route only.
- `src/app/<route>/hooks/`: route-specific hooks only.
- `src/components/`: shared UI used by more than one route.
- `src/hooks/`: shared hooks used by more than one route.
- `src/lib/api/`: typed API clients and request DTOs only. No React.
- `src/lib/`: shared pure utilities, markdown rendering, auth helpers, and client helpers.
- `src/config/`: static JSON configuration. Do not rely on JSON inference for public types.
- `public/`: static assets and static generated content only.

Do not put API calls directly in components when an API wrapper already exists or should exist in `src/lib/api/`.

Do not create a new top-level route for a domain if an existing domain route should own it.

## Backend Boundaries

Use these ownership rules:

- `backend/app/models/`: SQLAlchemy database models only.
- `backend/app/schemas/`: Pydantic request and response contracts only.
- `backend/app/routers/`: HTTP routing, dependency wiring, status codes, and thin orchestration.
- `backend/app/services/`: business logic such as SM-2 review, AI analysis, GitHub sync, import/export, and domain operations.
- `backend/app/utils/`: small framework-independent helpers.
- `backend/app/config.py`: settings only.
- `backend/alembic/versions/`: database migrations.

Routers must stay thin. If a route grows complex, move logic into `services/`.

Model changes require matching schema, API client, and migration changes unless there is a documented reason.

## Domain Model Rules

The current knowledge model is centered on `Note` with these content types:

- `note`: ordinary notes.
- `blog`: blog-like long-form entries.
- `mistake`: wrong-question records with review metadata.

If adding podcast records, do not overload `music` or `blog` silently. Add an explicit `podcast` content type and update all of these together:

- Backend enum/schema/model.
- Frontend API types in `src/lib/api/`.
- List filters and labels.
- Create/edit UI.
- Detail UI.
- Management UI.
- GitHub sync/export.
- Tests or verification notes.

Mistake records must preserve these fields as first-class data, not only markdown text:

- `subject`
- `difficulty`
- `question`
- `my_answer`
- `correct_answer`
- `analysis`
- `knowledge_points`
- `ef`
- `interval`
- `repetitions`
- `next_review`
- `last_reviewed`

## Data Flow Rules

Frontend pages must use this flow:

`page/component -> hook or local action -> src/lib/api/* -> backend API`

Backend APIs must use this flow:

`router -> schema validation -> service/model -> response schema`

Do not introduce a second data source for the same domain unless the architecture decision is documented in this file or in a dedicated architecture note.

The original GitHub-file workflow and the new backend workflow are both present. When changing persistence, be explicit about whether data lives in:

- static files under `public/`
- PostgreSQL through the backend
- GitHub export/sync generated from backend data

## Type And Contract Rules

Do not trust inferred JSON types for mutable configuration. Define explicit TypeScript types when arrays may start empty, especially:

- `siteContent.artImages`
- `siteContent.socialButtons`
- background images
- route config arrays

Keep frontend TypeScript types in sync with backend Pydantic schemas.

Do not hide contract failures by adding `any` unless the code is integrating an untyped external boundary and the unsafe part is isolated.

Do not add new fields in only one layer.

## Auth And Security Rules

There are two auth concepts:

1. Original GitHub App private-key auth for static content updates.
2. Backend JWT auth for notes, mistakes, review, and management APIs.

Do not mix these casually. A feature must clearly use one path.

For backend-protected mutations, use JWT auth through `Authorization: Bearer <token>`.

Do not expose broad registration, wildcard CORS, or persistent secrets in production without calling it out as a security risk.

Never commit real `.env`, private keys, tokens, database dumps, or personal content not intentionally public.

## UI And Product Rules

The project is a personal knowledge/blog system, not a generic demo. Core user workflows are:

- write and read notes
- record and review mistakes
- write blog posts
- optionally add podcast records if the domain type is introduced
- manage content safely

Do not add landing-page marketing screens for these workflows.

For operational pages such as notes, mistakes, review, and manage, prefer dense but readable interfaces over decorative hero sections.

Every public icon-only button must have an accessible name.

Every image that conveys meaning must have `alt`.

Do not disable user zoom.

## Static Assets And Content Rules

Static content references must point to files that exist under `public/`.

If removing imported public content, update all indexes and references in the same change.

If a UI uses `/music/*`, `/images/share/*`, `/images/art/*`, `/images/blogger/*`, or `/blogs/*`, verify the referenced files exist.

Do not commit generated caches:

- `.next/`
- `.open-next/`
- `.output/`
- `node_modules/`
- `backend/.venv/`
- `__pycache__/`
- `.pytest_cache/`
- `*.pyc`

## Validation Rules

Choose validation based on touched files:

- Frontend TypeScript changes: run `npx tsc --noEmit`.
- Frontend build-sensitive changes: run `npm run build`.
- Frontend UI changes: run the dev server and inspect the relevant route in a browser.
- Backend Python changes: run targeted tests if present, or at least import/start checks for FastAPI.
- API contract changes: verify both frontend client types and backend schemas.
- Database model changes: add or update Alembic migrations.

If validation fails because of pre-existing issues, report that clearly and include the first relevant failure.

Do not rely on `next.config.ts` `ignoreBuildErrors` as proof that the project is healthy.

## Package And Tooling Rules

Prefer the package manager already chosen by the repository. If both `pnpm-lock.yaml` and `package-lock.json` exist, do not update both casually. Ask or document which one is authoritative before changing dependencies.

Do not add large dependencies for small utilities.

Do not introduce a new state library; the project already uses Zustand and SWR.

## Change Discipline

Keep changes small and domain-scoped.

Do not refactor unrelated old blog features while implementing notes, mistakes, or podcast records.

Do not move files only for tidiness unless the user asked for architecture cleanup.

When creating a new domain feature, include:

- route
- API client
- backend schema/router/service/model updates
- navigation entry if user-facing
- empty state
- create/edit/read flow
- validation notes

## Current Known Architecture Debt

Agents must be aware of these known issues and avoid deepening them:

- TypeScript checking currently fails because JSON empty arrays infer as `never[]`.
- `next.config.ts` ignores build type errors.
- Static assets referenced by the UI may be missing after upstream content removal.
- Backend and original GitHub App persistence models are not fully unified.
- Backend registration and CORS are suitable for local prototype use, not production.
- Podcast records are not a first-class domain yet.

When working near these areas, either fix the debt in scope or explicitly avoid making it worse.

