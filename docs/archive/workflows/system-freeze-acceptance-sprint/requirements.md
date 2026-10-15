# Requirements — System Freeze & Acceptance Sprint

## REQ-SFA-01 Workflow Status Cleanup

Inspect these workflow folders and reconcile status language:

- `batch-8*`
- `route-cutover*`
- `batch-9*`
- `batch-10*`
- `batch-10-1*`
- `batch-10-2*`
- `batch-11*`
- `stream-run-lifecycle-design-review`
- `batch-12-ai-provider-routing-cost-stability`

Completed work must be marked `closed` or `completed`. Deferred work must be moved or summarized into a deferred backlog and must not be described as a current blocking item. Conflicting statuses such as `closed` plus `pending approval` must be recorded and corrected where in scope.

## REQ-SFA-02 Final System Boundary

Create or update `docs/final-system-boundary.md` with:

- Current system positioning.
- Completed mainlines.
- Closed risks.
- Current non-goals.
- Deferred capabilities.
- Security boundary.
- AI boundary.
- Public/admin boundary.

The document must explicitly state:

- AI output must not directly write formal `question`, `mistake`, or `review_item` records.
- Human accept/reject records decisions only and does not automatically apply output to formal entities.
- Formal auditable AI generation uses the non-streaming Run lifecycle.
- Legacy stream endpoints are deprecated / compatibility-only.
- `ai_call_logs` is the technical call fact source.
- `ai_runs` is the business audit fact source.
- Usage, cost, and health must not be inferred from `ai_runs.output_data`.

## REQ-SFA-03 Complete Local Acceptance

Run and record:

- `cd backend && .venv/bin/python -m pytest tests/ -ra`
- `cd backend && PYTHONPATH=. .venv/bin/alembic current`
- `npx tsc --noEmit`
- `npm run build`
- `git diff --check`
- `npm run lint`, if supported.

Validate these pages:

- Anonymous: `/`, `/blog`, `/notes`.
- Admin: `/manage`, `/manage/capture`, `/manage/ai`, `/manage/ai/runs`, `/manage/review`, `/manage/mistakes`, `/manage/questions`, `/manage/attachments`.

Acceptance must check:

- Anonymous users cannot access management data.
- Public pages do not request admin APIs.
- `/manage/ai` does not leak API keys, tokens, `storage_key`, prompt text, or `input_summary`.
- `/manage/ai/runs` does not leak `replay_input`.
- Legacy stream endpoints are not the formal generation mainline.
- `AUTH_BYPASS` is not used as formal acceptance proof.

## REQ-SFA-04 Final Backlog

Create or update `docs/final-backlog.md`. Each item must include priority, whether it blocks current use, suggested batch, risk, and validation method.

The backlog must include at least:

- ProviderProfile / ModelProfile / RoutingRule database persistence.
- `ai_usage_daily` persistence.
- Actual token usage persistence.
- Estimated cost calculation.
- Budget / quota enforcement.
- Real provider probe.
- Health event table.
- Automatic circuit breaking / cooldown / temporary provider disablement.
- Provider/routing online editing.
- Prompt admin / A-B / hot update / Prompt effectiveness evaluation.
- Complete provider token streaming audit.
- Longer browser regression coverage.
- Legacy dead code cleanup.
- `/api/folders` admin boundary review.
- Local production CORS review.
- httpOnly cookie session check architecture cleanup.

## REQ-SFA-05 Codex Quality Audit

Perform a read-only quality audit over:

- `backend/app`
- `backend/tests`
- `src/app`
- `src/lib`
- `docs/workflows`
- Alembic migrations
- README / setup documentation

The audit report must categorize findings as P0 blockers, P1 high-priority issues, P2 deferred issues, P3 cleanup items, false positives, suggested repair order, and daily-use recommendation.

No code fixes may be applied in this sprint without later explicit repair approval.

## REQ-SFA-06 Fresh Setup Experiment

Use an isolated path such as `/tmp/2025-blog-public-fresh-setup`. Do not use the existing running state as proof.

Verify:

- Dependency installation.
- Whether `.env.example` is sufficient.
- Database initialization.
- `alembic upgrade head`.
- Backend startup.
- Frontend startup.
- Admin creation/login.
- `/manage`, `/manage/ai`, and `/manage/capture` access.
- Minimal pytest smoke tests.
- `npm build`.

Record manual environment variables, `.env.example` gaps, README/setup accuracy, DB blockers, Node/Python version requirements, Redis requirements, real provider key requirements, and whether mock/disabled AI mode can boot without real provider keys.

## REQ-SFA-07 Final Handoff

Create or update `docs/final-handoff.md` with:

- System positioning.
- Current feature map.
- Route map.
- Database/migration state.
- AI architecture.
- Permission boundary.
- Run commands.
- Test commands.
- Daily-use flow.
- Known risks.
- Deferred backlog.
- Next-stage recommendations.

## REQ-SFA-08 Daily-Use Decision

Return exactly one of:

- A. Can enter real daily use.
- B. Can enter real daily use with conditions.
- C. Not recommended for real daily use yet.

If the conclusion is B, list required P0/P1 fixes, P2 items that can be deferred, admin-only capabilities, and capabilities that must not be publicly exposed.
