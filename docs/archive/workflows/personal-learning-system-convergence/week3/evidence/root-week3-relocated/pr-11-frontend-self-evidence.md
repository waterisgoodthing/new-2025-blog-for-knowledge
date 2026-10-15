# PR-11 frontend self-evidence (Dashboard three-question integration)

agent_id: PR-11-impl-frontend (implementer, senior-frontend-engineer)
date: 2026-09-25
status: self-check PASS (implementation), independent review/verification pending

## Changes

- `src/lib/api/dashboard.ts` — added `DashboardWeakKnowledgePoint`,
  `DashboardRecentlyMasteredItem`, `DashboardSectionAction(s)`,
  `DashboardTodayFirstAction`; `DashboardSummary` gains
  `review_today_count`, `practice_today_count`, `weak_top3`,
  `recently_mastered_4`, `today_first_action`, `section_actions`.
- `src/app/manage/(workspace)/dashboard/dashboard-overview.tsx` — renders the
  three canonical questions inside the existing Dashboard (no second authority):
  `今日先做` (deterministic fallback from `today_first_action`),
  今日复习/今日练习 counts + `section_actions.*.target_route` entries,
  weak Top 3, recently mastered 4. The old hardcoded `getLearningFeedback`
  band was replaced by `今日先做` so there is a single deterministic next action.
- `src/app/manage/(workspace)/dashboard/dashboard-content.tsx` — threads
  `onSummaryRetry` so per-section unavailable panels retry the canonical summary
  and refocus the result region.
- `src/app/manage/(workspace)/practice/{page,practice-today}.tsx` — new target
  route for the backend practice action (`/manage/practice`) consuming the
  existing PR-13 `getTodayPractice` client. Four states via `AsyncStatePanel`.
- Tests: `src/lib/api/dashboard.test.ts`, dashboard component tests,
  practice page tests (review-first, practice-first, all-empty, partial service
  failure, retry/focus).

## Evidence

- `tests/pr-11-frontend-tsc.txt` — `npx tsc --noEmit` PASS (0 errors).
- `tests/pr-11-frontend-vitest.txt` — `npx vitest run src/app/manage src/lib/api`
  27 files / 97 tests PASS.
- `api/pr-11-frontend-source-provenance.txt` — dashboard/practice trees have no
  legacy Note query; only `@/lib/api/dashboard` and `@/lib/api/practice`.
- `api/pr-11-frontend-write-scope.txt` — all touched files inside declared scope.

## Unresolved / notes for verifier

- Real-Chromium desktop/mobile, keyboard order, reduced-motion and SQL
  provenance are PR-11-verify's scope; not executed here.
- `weak_top3` renders PR-10's literal ordering (can be zero-metric active KPs).
- Practice route is additive; PR-13 delivered only the API client, no UI.
