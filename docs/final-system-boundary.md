# Final System Boundary

## Current System Positioning

This repository now contains a personal knowledge and blog system with two active lines:

1. Public read experience: static/blog/notes routes under `src/`.
2. Private management and learning system: FastAPI + PostgreSQL backend, admin-authenticated management routes, notes, questions, mistakes, review, attachments, capture, AI Gateway, AI Runs, usage/cost/health snapshots, and GitHub/static compatibility layers.

The current goal is stable personal daily use by the site owner, not a multi-tenant SaaS product and not a public AI platform.

## Completed Mainlines

- Batch 0-7 MVP rebuild baseline.
- Batch 8 image mistake capture MVP.
- Route Cutover Sprint: public read surface and private `/manage/*` mainline separated.
- Batch 9 AI Gateway minimal kernel and `ai_call_logs`.
- Batch 10 Task / Prompt / Validator management.
- Batch 10.1 Prompt Registry runtime integration.
- Batch 10.2 Prompt engineering standardization.
- Batch 11 AI Run audit and human review flow.
- RISK-B11-001, RISK-B11-003, and RISK-B11-004 closed.
- Batch 12A typed provider/routing policy.
- Batch 12B usage/cost observability snapshot.
- Batch 12C provider health snapshot API.
- Batch 12D management read-only AI governance panel.

## Closed Risks

- RISK-B11-001: Run management browser and sensitive-field verification closed.
- RISK-B11-003: closed by moving formal auditable generation away from pseudo-stream endpoints. Legacy stream endpoints are deprecated / compatibility-only.
- RISK-B11-004: controlled true provider synchronous Run audit proof closed, with matching `ai_runs` and `ai_call_logs` evidence.

## Current Non-Goals

The current system does not implement:

- ProviderProfile / ModelProfile / RoutingRule database persistence.
- Real provider health probe.
- Health event table.
- Automatic circuit breaker, cooldown, or temporary provider disablement.
- Budget or quota enforcement.
- Prompt admin, Prompt A/B, hot update, or Prompt effect evaluation.
- Complete provider token streaming lifecycle audit.
- Public AI operations.
- AI auto-apply into formal question, mistake, or review entities.
- Multi-user registration or production-grade open SaaS access.

## Deferred Capabilities

Deferred capabilities live in `docs/final-backlog.md`. They are not current blockers unless a later acceptance run proves otherwise.

Key deferred areas:

- Persist actual token usage and cost estimates.
- Persist daily AI usage aggregates.
- Add real provider probe and health event history.
- Add provider/routing online editing.
- Add complete stream token lifecycle support only if a real product need appears.
- Clean legacy dead code and route compatibility surfaces.
- Review `/api/folders`, production CORS, and httpOnly cookie architecture.

## Security Boundary

The project uses a public-read plus admin-write model.

Public surfaces may read published, non-hidden content. Admin surfaces and mutations require backend authorization. Frontend gates improve UX but are not the security boundary.

Admin-only capabilities include:

- Content creation, edit, delete, import/export, and sync actions.
- Capture, attachment upload, AI analysis, AI Runs, AI decisions, review queue, and management dashboards.
- Provider/routing/usage/health snapshots.

The system must not rely on `AUTH_BYPASS` as acceptance proof. `AUTH_BYPASS=true` plus `AUTH_BYPASS_ALLOW=true` must not be treated as production-safe.

## AI Boundary

AI output is assistive, not authoritative.

Hard rules:

- AI output must not directly write formal `question`, `mistake`, or `review_item` records.
- Human accept/reject records a decision about an AI Run only; it does not automatically apply output to formal entities.
- Formal entity creation still requires the existing human-controlled draft/confirm path.
- Formal auditable AI generation uses the non-streaming Run lifecycle.
- Old stream endpoints are deprecated / compatibility-only and must not be used as the formal generation mainline.
- Mock validation must not be described as true provider validation.
- A health snapshot from historical logs must not be described as a real provider probe.

## AI Fact Sources

`ai_call_logs` is the technical call fact source.

It records provider-level call facts such as task type, provider, model, success/failure, latency, fallback, attempts, input summary, and Prompt version.

`ai_runs` is the business audit fact source.

It records business Run lifecycle, validation status, human review status, safe output snapshot, retry chain, provider/model snapshot, latency, and safe errors.

Usage, cost, and health must not be inferred from `ai_runs.output_data`.

Current usage/cost/health snapshots are based on `ai_call_logs` and configuration/log history. Token usage and cost remain unknown/null unless real provider usage data is persisted.

## Public And Admin Boundaries

Public routes are for read-only content and must not show admin operations to anonymous users.

Admin routes live under `/manage/*` and must be protected by the existing admin authentication path.

Key public routes:

- `/`
- `/blog`
- `/blog/[id]`
- `/notes`
- `/notes/[id]`

Key management routes:

- `/manage`
- `/manage/dashboard`
- `/manage/capture`
- `/manage/ai`
- `/manage/ai/runs`
- `/manage/review`
- `/manage/mistakes`
- `/manage/questions`
- `/manage/attachments`

Legacy or compatibility routes may exist, but they are not the current product mainline.
