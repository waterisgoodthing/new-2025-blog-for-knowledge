# W4-00 Evidence — Legacy Cleanup Candidate Classification (PR-18 preflight)

Status: **PARTIAL** (read-only inventory; no deletion authorized or performed)
Date: 2026-09-26
Repo: `/Users/limengyang/2025-blog-public`
Branch/HEAD: `refactor/baseline` @ `4a954ea` (dirty worktree preserved as-is)
Scope: read-only classification for `w4-00.md` task 5 and `pr-18.md` task 1.
Baseline for run counts: `w4-00-baseline-status.txt`, `w4-00-baseline.diff`.

Classification legend: `SAFE_TO_DELETE` | `IN_USE` | `UNCLEAR`.

Conservative rule applied: any live non-test import/call, any registered
backend route, any dedicated backend test, or any documented staged/ops intent
⇒ not `SAFE_TO_DELETE`. Where runtime/access-log proof is required and absent,
the item is `UNCLEAR`, not `SAFE_TO_DELETE`.

No source file was modified, moved, renamed, staged, or deleted. The only file
written by this task is this document.

---

## 1. Classification table

| Candidate | Location | Classification | Static grep evidence | Tests | Notes / risk |
|-----------|----------|----------------|----------------------|-------|--------------|
| 1. Legacy SM-2 service (F11) | `backend/app/services/sm2.py` | **UNCLEAR** | import `routers/review.py:15`; call `routers/review.py:60`; router registered `main.py` (`include_router(review.router)`). Zero `src/` refs. | no dedicated `test_sm2.py`; behavior indirectly covered by PR-09 freeze tests (expect 410) | Call sits **after** `assert_not_legacy_mistake_write` (`review.py:53`), so the POST is 410-frozen before `sm2()` runs, but the module is imported by a **registered** router. Deleting `sm2.py` alone breaks app import. No leaf. |
| 2. Legacy review API client (pre-v2) | `src/lib/api/review.ts` | **IN_USE** | importers: `src/hooks/use-note-index.ts:3`, `src/app/mistakes/review/page.tsx:6`, type-only `src/adapters/ui-v2/from-backend.ts:25`, test `src/features/ui-v2/today/today.test.tsx:6` | `src/hooks/use-note-index.test.ts`; `/mistakes/review` guarded by `src/app/batch7-compatibility.test.ts` | Backs `useReviewStats`/`useReviewPlan` on public `/mistakes` + manage, and the protected `/mistakes/review` route. Not safe. |
| 3. Canonical review client (v2) | `src/lib/api/review-items.ts` | **IN_USE** (baseline) | importers: `src/app/manage/(workspace)/review/review-queue.tsx:13`, `src/features/ui-v2/review/useReviewQueueModel.ts:6`, `src/adapters/ui-v2/from-backend.ts:24` | `src/app/manage/(workspace)/review/review-queue.test.tsx` | Not a cleanup target; listed only to distinguish from #2. |
| 4. "Broken" Dashboard quick-action tests | `src/app/manage/(workspace)/dashboard/*.test.tsx` (4 files) | **IN_USE** (candidate stale) | no `it.skip/describe.skip/xit/xdescribe/test.todo/.only/skip:` anywhere in dir (exit 1 = no match) | `npx vitest run` → 4 files / **22 tests passed**, 0 skipped | No skipped/failing/todo test exists. Quick-action test `dashboard-overview.test.tsx:120` passes. Do not delete. |
| 5. WIP placeholder component | `src/components/wip.tsx` | **SAFE_TO_DELETE** | repo grep `components/wip`, `from './wip'`, `<WIP` → only the file's own `export default function WIP()`; no route renders it | none | Corroborated `PERSONAL_LEARNING_SYSTEM_AUDIT.md:327,378,546`. **Strongest candidate.** |
| 6. Placeholder page component | `src/app/manage/components/manage-placeholder-page.tsx` | **SAFE_TO_DELETE** | `ManagePlaceholderPage` appears only in its own file (definition + props interface); zero import sites | none | Corroborated audit doc. Zero call sites, not routed. |
| 7. Future-capability page component | `src/app/manage/(workspace)/components/future-capability-page.tsx` | **SAFE_TO_DELETE** | `FutureCapabilityPage` appears only in its own file; zero import sites | none | Corroborated audit doc. Zero call sites, not routed. |
| 8. UI-v2 foundation tree (staged/WIP) | `src/features/ui-v2/**`, `src/adapters/ui-v2/**`, `src/contracts/ui-v2/**`, `src/mocks/ui-v2/**`, `src/components/ui-v2/**` | **UNCLEAR** | no importer outside the ui-v2 tree (`features/ui-v2` external → none; `adapters/ui-v2` external → none) | self-tests only (`analytics.test.tsx`, `dashboard.test.tsx`, …) | `src/features/ui-v2/README.md` declares it **reserved** pending separate approval. Intentional staged work, not proven dead. |
| 9. Unused endpoint | `backend/app/routers/diagnostics.py` → `/api/admin/diagnostics` | **UNCLEAR** | 0 non-test `src/` callers (the `diagnostics` hits in `src` are `/api/music/manage/diagnostics`) | `backend/tests/test_monitoring_routes.py` | Registered, admin-guarded ops surface. No frontend caller ≠ dead (manual/ops use). Access-log proof required, absent. |
| 10. Unused endpoint | `backend/app/routers/file_workspace.py` → `/api/admin/workspace/files` | **UNCLEAR** | 0 `src/` callers; no `src/lib/api` client | `test_i7_file_workspace_routes.py`, `test_i7_file_workspace.py` | Backend service + tests exist, no UI wired. Possible planned attachments-management surface. Access-log proof absent. |
| 11. Legacy weak-point analytics | `backend/app/routers/knowledge.py:` `/weak-points` + `services/knowledge_retrieval.py:retrieve_weak_points` | **IN_USE** | frontend `src/hooks/use-knowledge.ts:24` `useWeakPoints` → `weak-point-diagnosis.tsx:43` / `weak-points-panel.tsx:7`, consumed by `src/app/mistakes/page.tsx` | backend knowledge/i6 tests; `src/app/mistakes/page.test.tsx` | Canonical KP analytics did **not** replace this surface. Live. |
| 12. Legacy weakness aggregation | `backend/app/services/knowledge_assistant.py:aggregate_weaknesses` | **IN_USE** | imported `routers/suggestions.py`; frontend `src/lib/api/knowledge-assistant.ts` | backend suggestion tests | Reachable via `/api/ai/suggestions`, `/api/ai/weekly-summary`. Live. |
| 13. Legacy review planner | `backend/app/services/review_planner.py:build_review_plan` | **IN_USE** | import/call `routers/review.py:14,104`; frontend `getReviewPlan` in `use-note-index.ts` | PR-09 freeze tests | Lives on registered `/api/review/plan` GET (read-compat, not frozen). Live. |
| 14. Canonical KP analytics (PR-10) | `backend/app/services/kp_analytics_service.py` + `routers/knowledge_points.py:` `/analytics` | **IN_USE** (canonical) | used by `services/dashboard_service.py:27,125` and `services/practice_service.py:36,94` | `test_pr10_kp_analytics_{contract,http,service}.py`, `test_pr10_verify_{contract,matrix}.py` | New authority; not a cleanup target. |
| 15. Canonical KP analytics client | `src/lib/api/knowledge-points.ts` | **UNCLEAR** | 0 importers (`lib/api/knowledge-points` external → none); only self-test | `src/lib/api/knowledge-points.test.ts` | New W3 canonical client not yet wired to a page. Unused ≠ legacy-dead; keep pending wiring decision. |
| 16. Orphan static data module | `src/app/music/list.ts` | **SAFE_TO_DELETE** | repo grep `music/list`, `from './list'` → none; `src/app/music/page.tsx` does not import it; file is a 1-item iframe data array | none | Corroborated audit doc. Zero call sites. |
| 17. Dead import | `src/app/blog/page.tsx:19` `import { readFileAsText }` | **SAFE_TO_DELETE** (one-line edit) | `readFileAsText` occurs exactly once — the import line; no usage | none | `noUnusedLocals` not enabled so `tsc` does not flag it. Corroborated audit doc. |
| 18. Orphan frontend client helpers | `src/lib/api/{ai,folders,meta,notes,questions,knowledge}.ts` | **UNCLEAR** | zero non-test callers for `analyzeMistakeStream`, `analyzeTextStream`, `updateFolder`, `moveFolder`, `createTag`, `mergeTag`, `createCategory`, `updateCategory`, `deleteCategory`, `promoteNote`, `updateQuestion`, `getKnowledgeSummary` | none | These are typed **API library surfaces** (back real endpoints); audit doc calls them orphan. Deleting them is a client-contract decision, not proven dead. Separate from endpoint removal. |

### Tally

- **SAFE_TO_DELETE: 5** — #5 `src/components/wip.tsx`, #6 `manage-placeholder-page.tsx`, #7 `future-capability-page.tsx`, #16 `src/app/music/list.ts`, #17 `readAsText` dead import.
- **IN_USE: 7** — #2 legacy review client, #3 canonical review client (baseline), #4 dashboard tests, #11 legacy weak-point analytics, #12 knowledge_assistant, #13 review_planner, #14 canonical KP analytics.
- **UNCLEAR: 6** — #1 `sm2.py`, #8 ui-v2 tree, #9 `/api/admin/diagnostics`, #10 `/api/admin/workspace/files`, #15 `knowledge-points.ts`, #18 orphan client helpers.

---

## 2. Candidate detail + raw command output (trimmed)

### Candidate 1 — `backend/app/services/sm2.py`

```bash
$ grep -rn "sm2" backend/ --include="*.py" | grep -iv __pycache__
backend/app/routers/review.py:15:from app.services.sm2 import sm2
backend/app/routers/review.py:53:        assert_not_legacy_mistake_write(note.type, operation="review.sm2_submit")
backend/app/routers/review.py:60:    ef, interval, repetitions, next_review = sm2(
backend/app/services/sm2.py:4:def sm2(quality: int, ef: float, interval: int, repetitions: int) -> ...
backend/tests/test_pr09_verify_api_contract.py:350:def test_F7_review_sm2_submit_frozen(client):
backend/tests/test_pr09_verify_http.py:285:def test_F7_sm2_submit_frozen(admin_client):
backend/tests/test_week3_contracts.py:517: "review.sm2_submit",
backend/tests/week3_contracts_support.py:314: "review.sm2_submit",  # F-7
backend/tests/test_pr09_legacy_mistake_freeze.py:64: "F-7": ("backend/app/routers/review.py", "review.sm2_submit"),
backend/tests/test_review_schema_v2.py:184: ReviewItemOut(**self._valid_item_kwargs(algorithm="sm2"))

$ grep -rn "sm2" src/
(no matches)

$ ls backend/tests/test_sm2.py
ls: cannot access 'backend/tests/test_sm2.py': No such file or directory

$ grep -n "app.include_router(review.router)" backend/main.py
app.include_router(review.router)
```

Route ordering proves the call is runtime-unreachable while the guard is in place
(`assert_not_legacy_mistake_write` raises 410 at `review.py:53`, before `sm2()` at `:60`):

```bash
$ sed -n '38,66p' backend/app/routers/review.py
@router.post("/{slug}", response_model=NoteOut)
async def submit_review(slug, req, db=..., _admin=Depends(get_current_admin)):
    ... note = <Note(type="mistake") only>
    assert_not_legacy_mistake_write(note.type, operation="review.sm2_submit")   # -> 410
    ...
    ef, interval, repetitions, next_review = sm2(...)                            # unreachable
```

**Verdict: UNCLEAR.** Static reference check **fails** (a registered router
imports and calls it). Only runtime path is the 410-frozen POST. A correct
retirement must remove the whole `/api/review` chain plus `review_planner.py`
and legacy `src/lib/api/review.ts`, and must **not** remove the public
`/mistakes/review` route in PR-18. `sm2.py` alone is not a leaf.

### Candidate 2 — Legacy review API client under `src/lib/api/`

```bash
$ ls src/lib/api/ | grep review
review-items.ts   # canonical v2 (ReviewItem/ReviewRecord -> /api/admin/review/items)
review.ts         # legacy pre-v2 (Note/SM-2 -> /api/review/{queue,slug,stats,plan})

$ grep -rn "lib/api/review'" src/ --include="*.ts" --include="*.tsx"
src/app/mistakes/review/page.tsx:6:import { getReviewQueue, submitReview, getReviewStats, getReviewPlan, ... } from '@/lib/api/review'
src/features/ui-v2/today/today.test.tsx:6:import type { ReviewPlan } from '../../../lib/api/review'
src/adapters/ui-v2/from-backend.ts:25:import type { ReviewPlan } from '../../lib/api/review'
src/hooks/use-note-index.test.ts:7:vi.mock('@/lib/api/review', () => ({

$ grep -rn "lib/api/review-items" src/ --include="*.ts" --include="*.tsx"
src/app/manage/(workspace)/review/review-queue.tsx:13:} from '@/lib/api/review-items'
src/app/manage/(workspace)/review/review-queue.test.tsx:6,71
src/features/ui-v2/review/useReviewQueueModel.ts:6:import { listDueReviewItems } from '../../../lib/api/review-items'
src/adapters/ui-v2/from-backend.ts:24:import type { ReviewItem } from '../../lib/api/review-items'
```

Downstream consumers of the legacy client (non-test):

```bash
$ grep -rn "useReviewStats\|useReviewPlan" src/ --include="*.tsx" --include="*.ts" | grep -v "src/hooks/use-note-index"
src/app/mistakes/page.tsx:14:import { useReviewPlan, useReviewStats } from '@/hooks/use-note-index'
src/app/mistakes/page.tsx:39: const { data: stats } = useReviewStats(isAdmin)
src/app/mistakes/page.tsx:40: const { data: plan } = useReviewPlan(isAdmin)
```

Compatibility contract keeps `/mistakes/review`:

```bash
$ grep -n "mistakes/review" src/app/batch7-compatibility.test.ts
24: 'mistakes/review/page.tsx',
57: expect(nextConfig).toContain("{ source: '/mistakes/review', destination: '/manage/review', permanent: false }")
```

**Verdict: IN_USE.** Still powers `use-note-index` stats/plan on public
`/mistakes` + manage and the `/mistakes/review` route. Not safe.

### Candidate 3 — Dashboard tests

```bash
$ grep -rnE "it\.skip|describe\.skip|xit\(|xdescribe|test\.todo|\.only\(|skip:|todo\(" \
    "src/app/manage/(workspace)/dashboard/"
exit=1   # no matches

$ npx vitest run "src/app/manage/(workspace)/dashboard"
 ✓ dashboard-content.test.tsx (2 tests)
 ✓ dashboard-content-verify.test.tsx (1 test)
 ✓ dashboard-verify.test.tsx (7 tests)
 ✓ dashboard-overview.test.tsx (12 tests)
 Test Files  4 passed (4)
      Tests  22 passed (22)
```

**Verdict: IN_USE / candidate stale.** The "broken Dashboard quick-action
tests" do not exist in the current tree — no skipped, todo, or failing tests.
`dashboard-overview.test.tsx:120` ("offers real daily actions without creating a
parallel workspace route") passes.

### Candidate 4 — WIP/TODO components

Marker scan (excluding benign `placeholder=` JSX attributes):

```bash
$ grep -rn "WIP\b\|TODO\|FIXME\|NOT IMPLEMENTED\|NotImplemented" src/components src/features src/app \
    --include="*.ts" --include="*.tsx" | grep -v placeholder
src/components/wip.tsx:6:export default function WIP() {
```

Import/call-site checks:

```bash
$ grep -rn "components/wip\|from './wip'\|from \"../wip\"\|<Wip\|<WIP" src/ --include="*.ts" --include="*.tsx"
(no matches)

$ grep -rn "ManagePlaceholderPage\|manage-placeholder-page" src/ --include="*.ts" --include="*.tsx"
src/app/manage/components/manage-placeholder-page.tsx:4,11,16   # self only
$ grep -rn "FutureCapabilityPage\|future-capability-page" src/ --include="*.ts" --include="*.tsx"
src/app/manage/(workspace)/components/future-capability-page.tsx:12,20,26   # self only

$ grep -rn "features/ui-v2" src/ --include="*.ts" --include="*.tsx" | grep -v "^src/features/"
(no matches)
$ grep -rn "adapters/ui-v2" src/ --include="*.ts" --include="*.tsx" | grep -v "^src/adapters/"
(none outside ui-v2 consumers)
$ sed -n '1,5p' src/features/ui-v2/README.md
# src/features/ui-v2 — reserved
# 本轮（F0–F5）仅保留本占位文件，不建业务页面。进入业务页面实施需下一次单独批准。
```

**Verdict:** `wip.tsx`, `manage-placeholder-page.tsx`,
`future-capability-page.tsx` = **SAFE_TO_DELETE** (zero call sites, zero tests,
not routed). `src/features/ui-v2` and its `adapters/contracts/mocks/components`
dependencies = **UNCLEAR** (explicitly reserved pending separate approval).

### Candidate 5 — Router prefixes vs frontend callers

All routers registered in `backend/main.py` (37 `include_router` calls;
`attachments.router` + `attachments.links_router`). Non-test `src/` caller files
per prefix:

```bash
$ bash -c 'for p in $prefixes; do
    n=$(grep -rlF "$p" src/ | grep -vE "\.(test|spec)\." | wc -l); echo "$n  $p"; done'
```

```text
1  /api/admin/dashboard          1  /api/admin/knowledge-points   3  /api/recommendations
0  /api/admin/diagnostics        1  /api/admin/mistake-drafts      6  /api/review
0  /api/admin/workspace/files    1  /api/admin/ai/runs            1  /api/tags
1  /api/admin/attachment-links   11 /api/ai                       28 /api/notes
1  /api/admin/attachments        1  /api/audit                    1  /api/public/mistakes
1  /api/admin/attempts           4  /api/auth                     2  /api/categories
1  /api/admin/search             17 /api/content                 5  /api/folders
1  /api/admin/profile            5  /api/guest-messages          5  /api/knowledge
1  /api/admin/governance         1  /api/music/manage            6  /api/music
2  /api/admin/mistakes           1  /api/admin/review/items       1  /api/admin/practice
1  /api/admin/notes              1  /api/admin/drafts             1  /api/admin/questions
1  /api/admin/captures           1  /api/admin/subjects
```

Items with **no** non-test frontend caller:

```bash
$ grep -rn "admin/diagnostics" src/
(no matches)
$ grep -rn "workspace/files" src/
(no matches)
```

Both are registered, admin-guarded, and have dedicated backend tests
(`test_monitoring_routes.py`; `test_i7_file_workspace_routes.py` /
`test_i7_file_workspace.py`). `/api/audit` is not in `src/lib/api` but is real:
direct `fetch('/api/audit?page=...')` in `src/app/manage/audit-tab.tsx:53`.

**Verdict:** the other prefixes are IN_USE. `/api/admin/diagnostics` and
`/api/admin/workspace/files` = **UNCLEAR** (no frontend caller, but live
router/service/tests; runtime/access-log proof absent and required).

### Candidate 6 — Duplicate / legacy analytics surfaces

Canonical PR-10 analytics:

```bash
$ grep -rln "kp_analytics\|knowledge_point" backend/app/services backend/app/routers --include="*.py" | grep -v __pycache__
backend/app/services/kp_analytics_service.py
backend/app/routers/knowledge_points.py        # GET /analytics
backend/app/services/dashboard_service.py      # uses kp_analytics_service
backend/app/services/practice_service.py       # uses get_knowledge_point_analytics
```

Pre-existing weakness surfaces and their frontend callers:

```bash
$ grep -rn "weak-point\|getWeakPoints\|useWeakPoints" src/ --include="*.ts" --include="*.tsx" | grep -v "\.test\."
src/hooks/use-knowledge.ts:22,24
src/app/mistakes/components/weak-points-panel.tsx:4,7
src/app/mistakes/components/weak-point-diagnosis.tsx:6,43
src/app/mistakes/page.tsx
```

```bash
$ grep -rn "aggregate_weaknesses" backend/app --include="*.py" | grep -v __pycache__
backend/app/services/knowledge_assistant.py:46
backend/app/routers/suggestions.py        # via /api/ai/suggestions, /api/ai/weekly-summary
$ grep -rn "build_review_plan" backend/app --include="*.py" | grep -v __pycache__
backend/app/services/review_planner.py:...
backend/app/routers/review.py:14,104
```

**Verdict:** legacy weak-point analytics (#11), `knowledge_assistant` (#12),
`review_planner` (#13) = **IN_USE**; canonical `kp_analytics_service` (#14) =
**IN_USE**. The only analytics surface with no app importer is the reserved
`src/features/ui-v2/analytics/AnalyticsSection.tsx` = **UNCLEAR** (part of #8).
No duplicate *backend* analytics route was found that canonical PR-10 replaced.

### Candidate 7 — Other dead application code

```bash
$ grep -rn "music/list\|from './list'" src/ --include="*.ts" --include="*.tsx"
(no matches)                      # src/app/music/page.tsx imports from @/lib/api/music-manage only
$ grep -n "readFileAsText" src/app/blog/page.tsx
19:import { readFileAsText } from '@/lib/file-utils'   # single occurrence (import only)

$ grep -rn "analyzeMistakeStream\|analyzeTextStream" src/ --include="*.ts" --include="*.tsx"
src/lib/api/ai.ts:106,181 (definitions only)
$ grep -rn "updateFolder\|moveFolder" src/ --include="*.tsx" | grep -v "lib/api/folders"
(no component callers)
$ grep -rn "createTag\|mergeTag\|createCategory\|updateCategory\|deleteCategory" src/ | grep -v "lib/api/meta"
(no callers)
$ grep -rn "promoteNote" src/ | grep -v "lib/api/notes"
(no callers)
$ grep -rn "updateQuestion" src/ | grep -v "lib/api/questions"
(no callers; updateQuestionDraft is different and used in draft-editor.tsx)
$ grep -rn "getKnowledgeSummary" src/ | grep -v "lib/api/knowledge"
(no callers)
```

**Verdict:** `src/app/music/list.ts` and the unused `readFileAsText` import are
**SAFE_TO_DELETE**. The orphan client-helper functions (#18) are **UNCLEAR**:
they are typed API-library surfaces with zero callers, but removing them is a
client-contract decision and does not remove the backing endpoints.

---

## 3. Strongest deletion candidate

**`src/components/wip.tsx`** — strongest single candidate.

- Static: repo grep for `components/wip`, `from './wip'`, `<WIP` returns only
  the file's own `export default function WIP()`; no route renders it.
- Tests: none reference it; removing it cannot regress a test.
- Runtime: no page imports it, so no rendered surface can reach it.
- Corroboration: named dead in `PERSONAL_LEARNING_SYSTEM_AUDIT.md:327,378,546`.

Same three-part evidence also supports (batch-deletable together):
`src/app/manage/components/manage-placeholder-page.tsx`,
`src/app/manage/(workspace)/components/future-capability-page.tsx`,
`src/app/music/list.ts`, and the unused `readFileAsText` import.

---

## 4. Runtime evidence status (PR-18 three-part requirement)

- Candidates #9 `/api/admin/diagnostics` and #10 `/api/admin/workspace/files`
  have static + test evidence but **no runtime/access-log evidence** yet
  (access logs were not available to this read-only inventory). Therefore
  **NOT_VERIFIED** on part 3 and classified `UNCLEAR`.
- Candidate #1 `sm2.py`: runtime proof exists that the only reachable path is
  the 410-frozen POST (code ordering + PR-09 tests), but static proof of
  no-imports **fails**; hence `UNCLEAR`.
- All `SAFE_TO_DELETE` items (#5–#7, #16, #17) have complete static + test
  (none) + "no rendered surface" evidence.

---

## 5. Explicit non-actions

- No file was deleted, moved, renamed, reformatted, staged, or committed.
- `sm2.py`, `src/lib/api/review.ts`, the ui-v2 tree, `knowledge-points.ts`,
  `/api/admin/diagnostics`, `/api/admin/workspace/files`, and the orphan client
  helpers were **left untouched** and are **NOT_AUTHORIZED** for deletion.
- Database columns/tables/migrations and public-facing routes were out of scope
  and were not evaluated for removal.
- Remaining work before any PR-18 deletion: (a) capture ≥2-week access-log
  runtime proof for `/api/admin/diagnostics` and `/api/admin/workspace/files`;
  (b) obtain separate approval for the coordinated `/api/review` retirement
  (which would unlock `sm2.py` + `review_planner.py` + legacy `review.ts`);
  (c) decide the client-contract question for #18.
