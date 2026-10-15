# PR-18 Summary — Week 4 Legacy Cleanup (SAFE_TO_DELETE only)

Status: **PASS**
Date: 2026-09-26
Repo: `/Users/limengyang/2025-blog-public`
Branch/HEAD: `refactor/baseline` @ `4a954eaa92952fcc5a6b18a2e15d2e824b094e41`
Preflight authority: `w4-00-cleanup-candidates.md` (§1 SAFE_TO_DELETE tally)
Per-item 3-part evidence: `pr-18-cleanup-components.md`
Constraint honored: WRITE SCOPE only; no git write; no DB command.

---

## 1. Items deleted (5 of 5 authorized SAFE_TO_DELETE)

| # | Item | Type | Result |
|---|------|------|--------|
| 1 | `src/components/wip.tsx` | file delete | done (27 lines) |
| 2 | `src/app/manage/components/manage-placeholder-page.tsx` | file delete | done (26 lines) |
| 3 | `src/app/manage/(workspace)/components/future-capability-page.tsx` | file delete | done (64 lines) |
| 4 | `src/app/music/list.ts` | file delete | done (6 lines) |
| 5 | `src/app/blog/page.tsx` unused `readFileAsText` import | 1-line edit | done (1 line) |

All 5 had complete static + test(none) + no-rendered-surface evidence both before and after deletion (see `pr-18-cleanup-components.md`). No item outside this list was modified.

## 2. Net lines removed

```text
Before (pre-existing dirty worktree baseline):
 76 files changed, 3349 insertions(+), 1405 deletions(-)

After:
 81 files changed, 3349 insertions(+), 1529 deletions(-)

Delta (this PR):
 5 files changed, 0 insertions(+), 124 deletions(-)
```

`git diff --stat` for the touched paths:

```text
 src/app/blog/page.tsx                              |  1 -
 .../components/future-capability-page.tsx          | 64 ----------------------
 .../manage/components/manage-placeholder-page.tsx  | 26 ---------
 src/app/music/list.ts                              |  6 --
 src/components/wip.tsx                             | 27 ---------
 5 files changed, 124 deletions(-)
```

## 3. Validation (before → after, raw)

| Command | Before | After |
|---------|--------|-------|
| `npx vitest run` | 70 files / 522 tests passed, exit 0 | 70 files / 522 tests passed, exit 0 |
| `npx tsc --noEmit` | exit 0 | exit 0 |
| `npm run test:typecheck` | exit 0 | exit 0 |
| `git diff --check` | n/a | exit 0 (no whitespace errors) |

No new failures; identical counts before and after. Post-deletion `grep` for every deleted path/identifier returns no matches (exit 1), and no page/route imports any deleted module — no dangling import remains.

## 4. Items deliberately NOT deleted (documented IN_USE / UNCLEAR from W4-00)

These are **not** cleanup targets in PR-18; they must remain untouched pending separate evidence/approval.

### IN_USE (live; deleting breaks the app)

| W4-00 # | Item | Reason it stays |
|---------|------|-----------------|
| 2 | `src/lib/api/review.ts` (legacy pre-v2 client) | Imported by `src/hooks/use-note-index.ts`, `src/app/mistakes/review/page.tsx`, `src/adapters/ui-v2/from-backend.ts` (type-only); backs public `/mistakes` stats/plan and protected `/mistakes/review`. |
| 3 | `src/lib/api/review-items.ts` (canonical v2) | Used by manage review-queue + ui-v2 review model; baseline authority, not a cleanup target. |
| 4 | `src/app/manage/(workspace)/dashboard/*.test.tsx` | No skipped/todo/failing tests exist (4 files / 22 pass). "Broken quick-action tests" is a stale description; deleting would remove live coverage. |
| 11 | `/weak-points` + `retrieve_weak_points` | Live via `useWeakPoints` → `weak-points-panel.tsx` / `weak-point-diagnosis.tsx` on `/mistakes`. |
| 12 | `knowledge_assistant.aggregate_weaknesses` | Reachable via `/api/ai/suggestions`, `/api/ai/weekly-summary`. |
| 13 | `review_planner.build_review_plan` | Live on registered `/api/review/plan` GET (read-compat, not frozen). |
| 14 | Canonical PR-10 KP analytics service/router | New authority used by dashboard + practice services. |

### UNCLEAR (no access-log or coordinated-retirement proof yet)

| W4-00 # | Item | Why it stays / what is missing |
|---------|------|--------------------------------|
| 1 | `backend/app/services/sm2.py` | Imported + called by **registered** `routers/review.py`; only runtime path is the 410-frozen POST. Static no-import proof fails. Not a leaf. |
| 8 | ui-v2 tree (`src/features/ui-v2/**`, adapters/contracts/mocks/components) | `README.md` declares it reserved pending separate approval; self-tests only. Intentional staged work. |
| 9 | `/api/admin/diagnostics` | Registered admin-guarded ops surface; 0 `src/` callers but no non-test frontend caller ≠ dead. **Access-log proof absent.** |
| 10 | `/api/admin/workspace/files` | Registered + service + dedicated tests; no UI wired. **Access-log proof absent.** |
| 15 | `src/lib/api/knowledge-points.ts` | New W3 canonical client with 0 importers + self-test. Unused ≠ legacy-dead; wiring decision pending. |
| 18 | Orphan client helpers in `src/lib/api/{ai,folders,meta,notes,questions,knowledge}.ts` | Typed API-library surfaces backing real endpoints; removal is a client-contract decision. |

## 5. Required follow-ups (carry out of PR-18)

1. **`sm2.py` coordinated retirement** — retire the whole `/api/review` chain together (`sm2.py` + `review_planner.py` + legacy `src/lib/api/review.ts`) under separate approval, **without** removing the public `/mistakes/review` route in this PR. Requires confirming the 410 freeze stays in force and re-homing `useReviewStats`/`useReviewPlan`.
2. **Access-log proof for the 2 endpoints** — capture ≥2-week runtime/access-log evidence for `/api/admin/diagnostics` and `/api/admin/workspace/files`; only then can they be reconsidered for deletion (currently `UNCLEAR`).
3. **Client-contract decision on orphan helpers** — decide whether `src/lib/api/{ai,folders,meta,notes,questions,knowledge}.ts` helper functions and the unused exported `readFileAsText` in `src/lib/file-utils.ts` should be retired, kept as public API surface, or wired up. This is a contract decision, not proven dead code.

## 6. Residual issues

- `readFileAsText` remains **exported and unused** in `src/lib/file-utils.ts` after the import removal. `src/lib/file-utils.ts` was outside WRITE SCOPE, so it was not touched; deleting the now-unused export is follow-up #3.
- No `sm2`/endpoint/analytics code was verified beyond static grep; this PR intentionally performed no runtime/DB validation of those boundaries.

## 7. Explicit non-actions

- No git commit, stage, or push; no DB command.
- The disconnect set named in the task (`sm2.py`, `src/lib/api/review.ts`, dashboard tests, `knowledge-points.ts`, ui-v2 tree, `/api/admin/diagnostics`, `/api/admin/workspace/files`, endpoint/analytics code) was left untouched.
- Only the 4 deletions, the 1 import removal, and the two evidence documents in this directory were written.
