# PR-11 backend self-evidence (dashboard summary delta)

agent_id: PR-11-impl-backend (implementer, senior-backend-engineer)
date: 2026-09-25
status: self-check PASS (implementation), independent review/verification pending

## Contract delivered (extends existing Dashboard summary, no second authority)

`GET /api/admin/dashboard/summary` (`DashboardSummary`) gains exactly the locked
delta fields plus the W3R-05 per-section action shape:

| Field | Meaning | Authority |
| --- | --- | --- |
| `review_today_count` | active ReviewItems with `next_review_at <= now` | canonical `review_items` |
| `practice_today_count` | number of PR-13 practice items returned | `practice_service.get_daily_practice` (reused) |
| `weak_top3` | first 3 of the PR-10 ordering | `kp_analytics_service.get_knowledge_point_analytics` (reused) |
| `recently_mastered_4` | latest record `new_state=mastered` AND current state `mastered`, `reviewed_at DESC` then item ID, limit 4 | canonical `review_records` + `review_items` |
| `today_first_action` | deterministic review-first → practice → none | derived from the two counts above; no AI |
| `section_actions.{review,practice}` | `{section,count,available,target_route,reason}` | W3R-05 per-section action |

Existing `counts`, `recent_*`, `sections`, `system` and the independent
learning/activity/storage degradation behavior are preserved (router fallback
also extended).

## Evidence

- `tests/pr-11-service-pytest.txt` — 9 PR-11 service tests PASS.
  Covers review-first, practice-first, all-empty, partial-service degradation,
  weak_top3 == PR-10 authority, recently_mastered boundaries (latest record not
  mastered → excluded; item no longer mastered → excluded; ordering/limit/tie),
  and no legacy `Note` dependency in `dashboard_service`.
- `tests/pr-11-http-pytest.txt` — 2 HTTP tests PASS (anonymous 401/403; complete
  delta + action shape for an authenticated admin).
- `tests/pr-11-regression-pytest.txt` — 90 PASS (dashboard routes + dependency
  lifecycle + week3 contracts + PR-13 + PR-10 service regressions).
- `tests/pr-11-targeted-suite.txt` — 101 PASS combined.
- `api/pr-11-source-provenance.txt` — source search: `dashboard_service.py` has
  no `Note`/`notes` reference; imports only canonical models; reuses
  `kp_analytics_service` + `practice_service`.

## Notes / open items for review

- `target_route` for practice is `/manage/practice`; the frontend PR-11 owner
  decides the concrete route. Review action points to `/manage/review`.
- `weak_top3` follows PR-10 literally (top 3 of the ordering); with no attempt/
  review signal it can list zero-metric active KPs ordered by ID, matching the
  locked authority rather than inventing a weakness threshold.
- `today_first_action` is only the ui-design §6.1 deterministic fallback; no AI
  recommendation path is introduced (G4).
