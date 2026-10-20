# Final Daily-Use Decision

Status: `completed`

Decision date: 2026-07-09

## Decision

B. 有条件进入真实日常使用。

## Reason

No P0 blocker was found in command validation, browser acceptance, quality audit, or fresh setup. The core private owner workflow is usable with normal auth and without `AUTH_BYPASS`.

The system should not be labeled turnkey or public-admin-ready yet because two P1 issues remain:

- Public pages expose management entry points or create actions to anonymous users. Auth boundaries hold, but public/admin product separation is not clean enough.
- Fresh setup requires manual Python 3.12 selection and production-build API URL handling. The default `python3` on this machine is Python 3.14 and fails backend dependency install; production `npm run build` rejects localhost `NEXT_PUBLIC_API_URL`.

## Required Before Claiming Full Readiness

P0:

- None found.

P1:

- Hide or conditionally render anonymous public-page management entry points and create actions.
- Update setup checks/docs so unsupported Python versions and production-build API URL requirements are explicit and hard to miss.

## Deferrable P2 Items

- `/api/folders` public boundary review.
- AI Gateway pytest async mock warning cleanup.
- Add or intentionally document missing frontend lint script.
- `ai_usage_daily` persistence.
- actual token usage persistence.
- estimated cost calculation.
- budget/quota enforcement.
- real provider probe.
- health event table.
- automatic circuit breaker / cooldown / provider temporary disablement.
- provider/routing online editing.
- Prompt admin / A-B / hot update / effect evaluation.
- complete provider token streaming audit.
- broader long-running browser regression.
- old source dead code cleanup.
- local production CORS configuration review.
- httpOnly cookie session architecture cleanup.

## Admin-Only Capabilities

- `/manage`
- `/manage/capture`
- `/manage/ai`
- `/manage/ai/runs`
- `/manage/review`
- `/manage/mistakes`
- `/manage/questions`
- `/manage/attachments`
- all AI operation APIs
- upload APIs
- review queue and review submission APIs
- formal question and attachment management APIs

## Capabilities That Must Not Be Public

- AI generation, repair, retry, accept, or reject operations.
- AI Run payloads, replay input, prompt text, input summaries, API keys, tokens, storage keys, and provider secrets.
- attachment storage internals.
- private review schedules and review submissions.
- capture queues and private draft workflows.
- provider/routing configuration editing.
- deprecated stream endpoints as a formal generation path.

## Operational Conditions

- Use normal admin login only; do not use `AUTH_BYPASS` as an acceptance or production path.
- Treat `/manage/ai` as read-only governance, not an online provider-control plane.
- Treat unknown usage/cost as unknown, not zero.
- Treat health snapshot as observational, not a real provider probe.
- Keep deferred backlog out of current-use blocker language unless future evidence shows actual blocking behavior.
