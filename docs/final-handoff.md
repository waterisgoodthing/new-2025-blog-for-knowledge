# Final Handoff

Status: `completed`

Last updated: 2026-07-09

## System Positioning

This repository is a personal knowledge and public blog system with two active architectural lines:

- `src/`: Next.js App Router frontend for public reading, management UI, notes, blog, mistakes, review, capture, attachments, and AI governance panels.
- `backend/`: FastAPI backend for PostgreSQL-backed content, admin auth, learning workflows, AI calls, audit logs, captures, questions, mistakes, review, and attachments.

The system is frozen for acceptance. The current sprint does not add product features, migrations, provider probes, AI Gateway refactors, prompt back office, A/B testing, auto-circuit-breaking, or recommendation changes.

## Current Feature Map

Completed and accepted mainlines:

- Public content reading: `/`, `/blog`, `/blog/[id]`, `/notes`, `/notes/[id]`, `/mistakes`.
- Admin login and management entry: `/manage`.
- Workspace management: dashboard, capture, AI, AI Runs, review, mistakes, questions, attachments, subjects, settings.
- Batch 8 image capture flow: image upload and capture-item staging surface.
- Batch 9 AI Gateway kernel: typed provider calls, technical call logging, fallback policy, and provider contract tests.
- Batch 10 / 10.1 / 10.2 prompt governance: prompt registry, runtime integration, validator, standard output discipline, and deterministic repair.
- Batch 11 AI Run audit and human review: independent `ai_runs` business audit table, accept/reject/retry decisions, and no automatic formal entity writes.
- Batch 12A-D provider/routing/cost/health/admin observability: typed routing policy, usage/cost snapshots from call logs, health snapshot API, and read-only AI admin panel.

## Route Map

Public routes:

- `/`
- `/blog`
- `/blog/[id]`
- `/notes`
- `/notes/[id]`
- `/mistakes`

Admin or owner-only routes:

- `/manage`
- `/manage/dashboard`
- `/manage/capture`
- `/manage/ai`
- `/manage/ai/runs`
- `/manage/review`
- `/manage/mistakes`
- `/manage/questions`
- `/manage/attachments`
- `/manage/subjects`
- `/manage/settings`
- `/write-note`
- `/write-note/[slug]`
- `/write-mistake`
- `/write-mistake/[slug]`
- `/mistakes/review`

Deprecated or compatibility-only AI route class:

- Old stream endpoints remain available only for compatibility. They are not the formal generation mainline.

## Database And Migration State

Current Alembic state:

```text
018 (head)
```

Accepted migration chain includes:

- content and note foundations
- folders/tags
- admin sessions and passkeys
- audit logs
- subject taxonomy
- question drafts and formal questions
- mistakes and review
- attachments
- capture items
- `ai_call_logs`
- prompt version field on call logs
- independent `ai_runs`

This handoff introduces no new migration and no new database table.

## AI Architecture

The accepted AI architecture uses two fact-source tracks:

- `ai_call_logs`: technical provider-call fact source.
- `ai_runs`: business audit fact source for formal AI generation attempts and human decisions.

Strict boundaries:

- AI output must not directly write formal `question`, `mistake`, or `review_item` records.
- Human accept/reject records a decision on the Run and does not automatically apply changes to formal entities.
- Formal auditable AI generation goes through the non-streaming Run lifecycle.
- Old stream endpoints are deprecated / compatibility-only.
- Usage, cost, and health snapshots are derived from technical call facts and routing/provider state, not from `ai_runs.output_data`.
- Unknown usage or cost means unknown, not zero and not estimated billing.
- Health snapshot is observational and does not claim to be a real provider probe.

## Permissions Boundary

The real security boundary is backend auth, not frontend route hiding.

Public read APIs:

- `GET /api/notes`
- `GET /api/notes/{slug}`

Public reads must filter to published and non-hidden content for anonymous users.

Admin-only surfaces:

- mutations
- uploads
- AI operations
- review queues and review submissions
- capture workflows
- formal question management
- attachment management
- AI Run audit

Frontend management routes use `AuthGate` or equivalent management layout protection. Browser validation confirmed anonymous users are redirected to `/manage` and management data is not rendered.

Known boundary follow-up:

- Public navigation still exposes management entry links and empty-state create actions to anonymous users. This does not leak data because backend and route auth hold, but it weakens public/admin product separation and is recorded as P1.
- `/api/folders` is publicly readable and should be reviewed as a P2 boundary cleanup.

## Running The System

Backend local dev:

```bash
cd backend
python3.12 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
PYTHONPATH=. alembic upgrade head
python -m uvicorn main:app --reload
```

Frontend local dev:

```bash
npm ci
cp .env.example .env
npm run dev
```

Important setup notes:

- Use Python 3.12 for the current dependency set.
- `ALLOWED_ORIGINS` is comma-separated.
- Local dev may use localhost API URLs.
- Production build requires a non-localhost `NEXT_PUBLIC_API_URL`.
- Redis is not required.
- Real provider keys are not required for booting the application or opening the read-only AI governance panel.

## Testing The System

Accepted local verification commands:

```bash
cd backend
.venv/bin/python -m pytest tests/ -ra
PYTHONPATH=. .venv/bin/alembic current
```

```bash
npx tsc --noEmit
npm run build
git diff --check
```

`npm run lint` is not currently available because `package.json` has no `lint` script.

Fresh setup smoke tests used:

```bash
cd backend
.venv/bin/python -m pytest tests/test_temp_admin_bootstrap.py tests/test_ai_routing_policy.py tests/test_ai_provider_health_snapshot.py -q
```

## Daily Use Flow

Recommended daily private workflow:

1. Start backend and frontend with normal auth enabled.
2. Log in through `/manage`.
3. Use `/manage/capture` for image capture staging.
4. Use `/manage/mistakes`, `/manage/questions`, and `/manage/review` for private learning data.
5. Use `/manage/ai` and `/manage/ai/runs` for read-only AI governance and Run decisions.
6. Publish only content intended for public reading.

Do not use:

- `AUTH_BYPASS` as a normal acceptance or production path.
- Deprecated stream endpoints as the formal generation path.
- Mock provider results as proof of real provider availability.
- Admin-only pages as public product surfaces.

## Known Risks

P0 blockers:

- None found in this sprint.

P1 high-priority issues:

- Public pages expose management entry points or create actions to anonymous users. Backend protection works, but public/admin UI separation should be tightened.
- Fresh setup is not self-service on this machine unless Python 3.12 and production-build API URL rules are followed.

P2 deferred issues:

- `/api/folders` public boundary review.
- pytest async mock warnings in AI Gateway tests.
- missing `npm run lint`.
- usage/cost persistence and true cost calculation.
- real provider health probe and health event persistence.
- budget/quota enforcement.
- provider/routing online editing.
- complete provider token streaming audit.
- broader long-run browser regression.
- local production CORS documentation cleanup.
- httpOnly cookie/session architecture cleanup.

## Backlog Link

Canonical remaining backlog:

- `docs/final-backlog.md`

## Next-Stage Recommendation

Use the system for private daily work under a conditional acceptance posture:

- keep management pages owner-only
- keep AI governance read-only
- do not expose admin operations publicly
- fix P1 public/admin affordance and setup documentation before claiming turnkey readiness
- schedule P2 observability and cleanup work in explicit future batches
