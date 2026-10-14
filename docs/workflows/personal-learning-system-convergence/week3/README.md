# Week 3 — CANONICAL LEARNING execution plan

Status: **WEEK3_GATE_PASS** (2026-09-22, user-decided; INC-01/INC-02 recorded as closed process events)  
Prepared: 2026-09-22 · Implementation authorized: 2026-09-22  
Execution mode: **WORKER**; the main agent remains `primary_owner` and final code acceptor.  
Live progress and background: [TRACKING.md](TRACKING.md) · Task assignments: [tasks/](tasks/) · Final report: [week3-technical-report.md](week3-technical-report.md)

## 1. Outcome

Week 3 closes the canonical learning read path so that the private Dashboard can answer, from canonical entities only:

1. What should I review today?
2. What should I practise today?
3. Which knowledge points are weakest?

It also cuts the public mistake list over to explicitly published canonical `Mistake` rows and adds the canonical Note-to-KnowledgePoint relationship required by later learning features.

Planning this week does **not** authorize implementation, a real database migration, production data inspection or writes, commit, push, merge, deployment, or Week 4 work.

## 2. Verified starting point

- Week 2 records its Gate as `PASS` on 2026-09-21. The current dirty worktree contains the Week 2 implementation and migrations 028–030; it must be preserved as the Week 3 baseline, not treated as a clean or committed branch.
- Source migration head is 030. Migrations 031 and 032 do not exist yet.
- Public `/mistakes` still reads legacy `Note(type='mistake')` through `useNoteIndex`.
- Canonical `Mistake.visibility` still has a database/model contract of private-only, and the admin DTO/client also narrow it to `private`.
- The existing Dashboard summary uses canonical Question, Mistake, ReviewItem and ReviewRecord rows, but it does not yet expose daily practice, weak KnowledgePoints, or recently mastered items.
- `QuestionKnowledgePoint.knowledge_point_id` and `KnowledgePoint.id` are `INTEGER`. The older D8 sketch saying UUID is stale and must not drive migration 032.
- Existing `MistakeOut` contains private fields including `my_answer`; it must not be reused as the public DTO.
- The existing legacy migration adapter creates canonical mistakes with `visibility='private'`. PR-09 must reconcile this behavior instead of building a second, conflicting migrator.

## 3. Decisions locked by this plan

### W3-D01 — Serial delivery order

Execute and accept each item before starting the next:

```text
W3-00 preflight and contract lock
→ PR-09 canonical public mistakes
→ PR-10 KP analytics
→ PR-12 Note↔KP schema/API
→ PR-13 daily practice
→ PR-11 Dashboard integration
→ Week 3 Gate
```

PR-11 moves behind PR-13 because its “today practise” answer depends on the practice endpoint. PR numbers remain unchanged; only execution order changes.

### W3-D02 — PR-09 implementation and rollout order

The former R04 and D6 prose disagreed about cutover order. The parent requirements/design have now been aligned to this fail-closed order:

```text
prepare schema/API/UI and dry-run tooling
→ freeze all new legacy mistake writes
→ migrate legacy rows idempotently in scratch
→ reconcile counts, visibility and provenance
→ enable canonical public read
→ verify public/private negative cases and honest Empty
```

For a future production rollout, freeze, migration, verification and cutover require their own approved runbook and rollback decision. No production execution is part of Week 3 implementation authorization.

### W3-D03 — Public DTO is an allowlist

Create a separate public response contract. The initial allowlist is `id`, `title`, `question_text`, `correct_answer`, `analysis`, `reason_category`, `mistake_reason`, `difficulty`, `knowledge_point_ids`, `created_at` and `updated_at`. It excludes `my_answer`, source draft identifiers, internal version/audit fields, private review state, and unpublished rows. Only `active + public` rows are readable. The first cutover renders canonical cards inline and removes the legacy slug dependency; it does not invent a new public detail route. The admin DTO remains separate and continues to require `get_current_admin`.

### W3-D04 — Migration 032 key types

`note_knowledge_points.note_id` is UUID and `knowledge_point_id` is INTEGER, matching the current canonical tables. The pair is the primary key or has an equivalent unique constraint; both foreign keys use `ON DELETE CASCADE`.

### W3-D05 — Deterministic analytics and practice

- Attempt metrics use canonical `Attempt` rows with `context_type='practice'`, joined through `QuestionKnowledgePoint`; review re-answer attempts do not inflate practice accuracy.
- `accuracy` and `wrong_rate` use an explicit non-zero graded-attempt denominator; zero samples return 0 rather than NaN/error.
- `review_count` and `due_count` use canonical ReviewRecord/ReviewItem/Mistake-to-KP paths.
- `lapse_count` is the lifetime count of canonical ReviewRecords with `rating <= 2` for the KP. Multi-KP Questions contribute one full observation to each linked KP; this first version does not fractionally allocate attempts. Archived Questions, archived Mistakes and inactive KPs are excluded. “Current streak failures” is rejected because a lapse resets the streak and `active → active` does not distinguish lapse from progression.
- Every sort has a stable final tie-breaker (`knowledge_point_id`, then `question_id` where applicable).
- Daily practice uses weak-KP priority, active/unarchived Questions, a configurable rolling window defaulting to the previous 7×24 hours, and excludes a Question when any linked canonical Mistake has a mastered ReviewItem. It returns 0..10 actual items; 3 is a target only when at least three eligible candidates exist. Its DTO excludes `answer_data`, `correct_answer`, `analysis` and `explanation` until the existing authenticated submit/evaluation flow returns feedback.
- Week 3 includes deterministic fallback only. Daily AI recommendation, AI generation, UTC+8 idempotency, and PR-20–26 remain outside scope.

## 4. Work packages and acceptance

### W3-00 — Preflight and contract lock

Risk: HIGH  
Gates: G0 requirement/domain, G2 data/database, G3 security/auth, G4 recommendation

Tasks:

1. Snapshot the dirty-worktree scope and identify Week 2-owned files; do not reformat, stage, revert, or absorb unrelated changes.
2. Verify a single source migration head at 030 and pin the scratch runtime expectation before writing 031.
3. Inventory every legacy mistake writer and reader, including note create/update/promote, review/suggestion/knowledge services, public `/mistakes`, and compatibility tests.
4. Reconcile the existing migration-026 adapter with PR-09 using a new mapping version in the same ledger/idempotency mechanism, not a parallel five-row script. The Week 3 mapping must also create ReviewItems with the accepted v2 algorithm rather than the adapter's historical v1 default.
5. Encode the public DTO allowlist, analytics/practice/Dashboard response shapes and the decisions in W3-D03–D05 in tests or contract fixtures.
6. Create a guarded scratch-only runner that rejects `blog_db`, `blog_v2`, default `.env`, and any database name outside the task-specific `astra_week3_*` allowlist.

Stop if migration head is not exactly the accepted Week 2 head, the Week 2 dirty diff cannot be isolated, a legacy writer is unaccounted for, or any public field classification remains unresolved.

### PR-09 — Canonical public mistakes

Risk: HIGH  
Gates: G0, G2, G3

Implementation slice:

- migration 031 replaces only `ck_mistakes_visibility` with `IN ('private','public')`; model, admin schema and TypeScript DTO are updated together;
- admin-only visibility mutation is added with optimistic-version/conflict behavior consistent with current admin mutations;
- a separate unauthenticated read endpoint returns only `status='active' AND visibility='public'` via the public allowlist DTO;
- all paths that can make a Note `type='mistake'`—create, update-type, promote and the legacy writer UI—fail closed while legacy reads remain available for compatibility evidence;
- the existing migration-026 ledger/idempotency mechanism is reused with a new Week 3 mapping version supporting the approved visibility mapping, dry-run, idempotent replay and a machine-readable reconciliation report;
- the public page switches to canonical data only after scratch migration verification; no fallback to legacy data is permitted.

Acceptance evidence:

- migration 031 fresh upgrade, 030→031 upgrade, 031→030 downgrade, constraint rejection and single-head checks; downgrade must fail closed or first prove there are no `public` rows;
- fixture matrix for published/unpublished × hidden/visible mapping, rerun idempotency, changed-source conflict, count/provenance reconciliation and zero-public Empty;
- anonymous public list/cards cannot return private rows or `my_answer`; admin list/update remains 401/403 without an admin session;
- source searches and route tests prove legacy writes are frozen while approved compatibility reads remain;
- real Chromium verifies public populated/Empty/error states and admin publish/unpublish behavior without leaking private content.

### PR-10 — Canonical KP analytics

Risk: MEDIUM  
Gates: G0, G4

Implementation slice:

- add a service-owned analytics query and admin-only read endpoint for `attempt_count`, `wrong_count`, `review_count`, `due_count`, `accuracy`, `wrong_rate` and the locked lapse metric;
- rank weakness by `wrong_rate DESC`, `lapse_count DESC`, `due_count DESC`, then stable ID;
- keep SQL/query construction in the service layer and keep the router thin;
- do not add weights, ML, trend analytics or AI summaries.

Acceptance evidence:

- canonical fixture cases cover correct/wrong practice attempts, review-context exclusion, no-attempt/zero denominator, due/future/mastered reviews, ties and stable ordering;
- query-count or equivalent evidence prevents per-KP N+1 behavior;
- endpoint is admin-only and its frontend DTO matches the backend schema.

### PR-12 — Canonical Note↔KnowledgePoint relation

Risk: HIGH  
Gates: G0, G2, G3

Implementation slice:

- migration 032 adds the UUID/INTEGER association table and indexes needed by its actual query direction;
- model, schema, service/router and `src/lib/api/notes.ts` are updated together;
- link/unlink is explicit admin-only user intent; AI suggestions do not write automatically. Because the current Note stores subject as free text rather than a canonical `subject_id`, Week 3 does not silently enforce cross-subject matching; that normalization is deferred and recorded.
- existing polymorphic `knowledge_point_links` remains intact until a separately authorized compatibility retirement.

Acceptance evidence:

- fresh-to-032 and 031→032 upgrade/downgrade replay, one-head check, FK/cascade proof and duplicate-link rejection;
- missing Note/KP, repeated link/unlink, unauthorized mutation and concurrent duplicate cases have defined 404/409/401-403 behavior;
- no existing Note authoring or legacy knowledge-link regression.

### PR-13 — Daily practice

Risk: MEDIUM  
Gates: G0, G4

Implementation slice:

- add `GET /api/admin/practice/today` through router → schema → service;
- consume PR-10 weakness ordering, active Questions and the locked recent-attempt window;
- exclude mastered targets and return explicit selection reasons plus honest Empty metadata; stable ordering ends with `knowledge_point_id`, then `question_id`;
- add the typed API client, but do not create a new full practice platform.

Acceptance evidence:

- fixtures cover 0, 1, 2, 3 and more than 10 eligible candidates;
- weak-KP ordering, stable ties, archived exclusion, recent-attempt exclusion, mastered exclusion and no-KP fallback behavior are deterministic;
- endpoint is read-only/admin-only and does not create Attempts merely by listing questions.

### PR-11 — Dashboard integration

Risk: MEDIUM  
Gates: G0, G3, G4

Implementation slice:

- extend the existing Dashboard summary rather than creating a second dashboard authority;
- render today review count/action, today practice count/action, weak Top 3 and recently mastered 4 from canonical services. “Recently mastered” means distinct ReviewItems whose latest qualifying ReviewRecord changed `new_state` to `mastered`, whose current item state remains mastered, ordered by `reviewed_at DESC` then item ID, limited to four;
- `今日先做` uses only deterministic fallback derived from due review/practice data;
- preserve existing Dashboard profile, activity, storage and failure-degradation behavior.

Acceptance evidence:

- component/contract tests cover review-first, practice-first, all-empty, partial-service failure and retry/focus behavior;
- real Chromium covers desktop and narrow mobile widths, keyboard order, loading, Empty, error/retry and reduced motion;
- browser/API evidence traces each displayed value to canonical rows; no legacy Note query supplies the three Gate answers.

## 5. Week 3 Gate

Run the final Gate only after PR-09, PR-10, PR-12, PR-13 and PR-11 each has implementation, self-check, independent review, required gate decisions, verification and main-agent acceptance recorded as `PASS`.

Seed a fresh guarded scratch database with at least:

- two KnowledgePoints with deliberately different weakness histories;
- active, archived, recently attempted and eligible Questions;
- due, future and mastered ReviewItems with ReviewRecords;
- public and private canonical Mistakes plus legacy Note mistakes;
- a Note linked to a KnowledgePoint through migration 032.

The Gate must prove:

| Question / invariant | Required evidence |
| --- | --- |
| What should I review today? | Dashboard count/action equals canonical due active ReviewItems. |
| What should I practise today? | Dashboard count/action equals PR-13 eligible output and respects weak/recent/mastered filters. |
| Which KP is weakest? | Top result matches the locked PR-10 ordering and stable tie-breaker. |
| Is public mistake ownership canonical? | Anonymous API/browser sees only public canonical Mistakes; legacy-only/private rows are absent and Empty is honest. |
| Is Note↔KP canonical? | Link/unlink persists through migration-032 schema and duplicate/FK constraints reject invalid writes. |
| Is the boundary safe? | Anonymous admin calls are 401/403; public DTO contains no private-only fields; no auth contract is changed. |

Final verification set:

- targeted backend/frontend suites for all five PRs;
- backend full suite against the explicitly verified scratch database;
- frontend full test/typecheck suite and `npx tsc --noEmit`;
- migration 030→032 replay plus downgrade/re-upgrade and schema/integrity queries;
- fresh `npm run build:cf`, production workerd preview, runtime smoke and real Chromium Week 3 walkthrough;
- `git diff --check` and an independent final review with zero unresolved BLOCKER/HIGH findings.

## 6. Ownership and evidence rules

For every PR:

1. The main agent finalizes the exact contract and write scope.
2. A bounded implementer may change only that PR's assigned files.
3. A different read-only reviewer checks domain, compatibility, security and regression risks.
4. Database/security/recommendation gates are decided from current code and reproducible evidence, not implementation claims.
5. The main agent accepts or returns rework; later PRs do not start until the current PR is `PASS`.

Only processes and scratch resources created for Week 3 may be cleaned up. Resident services and unrelated dirty files are protected.

## 7. Explicit exclusions

- production data inspection/write, real migration execution, deployment and cutover;
- commit, stage, push, merge or release;
- deletion of legacy tables/endpoints or migration-026 governance records;
- Question visibility redesign, public practice, a full practice player, FSRS, weighted/ML weakness, trends or charts;
- AI daily recommendation, AI KP auto-linking, automatic persistence without human confirmation;
- PR-14 onward and PR-20–26.

## 8. Authorization boundary

This document is ready for review. Starting W3-00 or any PR requires explicit Week 3 implementation authorization. Production migration/cutover remains a separate later decision even if all local Week 3 gates pass.


### 2026-09-26 后续复核

历史 Gate PASS 保留；本次证据完整性复核 PARTIAL。事故防复发补强与独立评审见 [后续记录](incident-followup-2026-09-26/README.md)，不执行数据库恢复/清理。
