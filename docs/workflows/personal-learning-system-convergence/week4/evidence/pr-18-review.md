# PR-18 Independent Review — Week 4 Legacy Cleanup

Reviewer role: independent reviewer (not the implementer).
Mode: read-only. No source modified, no git write, no DB command. Only this file created.
Date: 2026-09-26
Repo: `/Users/limengyang/2025-blog-public`
Branch/HEAD at review: `refactor/baseline` @ `4a954ea`
Reviewed artifacts: `evidence/pr-18-cleanup-components.md`, `evidence/pr-18-summary.md`
Authority: `evidence/w4-00-decisions.md` (W4-E07), `evidence/w4-00-cleanup-candidates.md` §1,
`tasks/week4-gate.md` (Net reduction ≥500 secondary metric).

## Verdict

**PASS_WITH_NOTES**

The 5 authorized SAFE_TO_DELETE items are executed exactly as claimed; no out-of-scope file was
touched by PR-18; all static greps reproduce; deleted-file line counts are exact; the touched
paths total 124 deletions / 0 insertions; and the three required validations plus `git diff --check`
are green. Notes are governance/documentation only (stale tracking status, omitted explicit ≥500
disclosure in the PR-18 docs themselves); none affects correctness or data safety.

Severity counts: **BLOCKER 0 · HIGH 0 · MEDIUM 1 · LOW/NOTE 3**.

## Scope-isolation method

`w4-00-baseline-status.txt` is a Week-start snapshot (pre-PR-14…PR-19), so a raw baseline diff cannot
attribute changes to PR-18. PR-18 was isolated by three independent signals that agree:

1. `git status --short` shows **exactly 4 `D` entries** (baseline had zero deletions).
2. `git diff --numstat` for the whitelisted paths totals **124 deletions, 0 insertions**.
3. Filesystem mtime: among `src/` and `backend/`, **only `src/app/blog/page.tsx`** has mtime after
   `2026-09-26 15:44:59` (15:48:02), matching the single edited line and PR-18 execution window.

## Findings

| id | severity | problem | evidence | required action |
|----|----------|---------|----------|-----------------|
| R-01 | MEDIUM | `TRACKING.md` and `tasks/pr-18.md` still declare PR-18 `NOT_STARTED` with all checkboxes `[ ]`, inconsistent with the evidence docs' `PASS`. A downstream gate reading tracking would see PR-18 as unstarted. | `TRACKING.md:140-147` "### PR-18 — Legacy cleanup — `NOT_STARTED`" and "Summary + net lines removed \| NOT_STARTED"; `tasks/pr-18.md` `- [ ]` throughout | Reconcile TRACKING.md + tasks/pr-18.md to the evidence state (evidence-completion bookkeeping; no source change). |
| R-02 | LOW/NOTE | PR-18's own docs report the raw net reduction (124) but never state that the plan's ≥500 secondary metric is **not met**. The shortfall is disclosed only in `w4-00-decisions.md:87` (W4-E07). The number is not misreported, but PR-18 (the artifact the gate cites for net lines) lacks the explicit pass/fail statement. | `grep 500\|secondary\|metric pr-18-*.md` → exit 1 (no match); `w4-00-decisions.md:87` "Net line reduction will be far below the plan's ≥500 secondary metric" | Add an explicit "≥500 secondary metric: NOT MET (124/500)" line to `pr-18-summary.md` §2 or to the gate matrix attribution. |
| R-03 | LOW/NOTE | `readFileAsText` remains exported and unused in `src/lib/file-utils.ts` after the import removal. Correctly disclosed by PR-18 as outside WRITE SCOPE / follow-up #3. | `grep -rn readFileAsText src/ --include=*.ts` → `src/lib/file-utils.ts:3:export function readFileAsText...` only | None for PR-18; carry as follow-up (already item #3 in `pr-18-summary.md`). |
| R-04 | LOW/NOTE | Stale textual references to the deleted modules remain in historical docs (and a stray worktree), e.g. `docs/workflows/mvp-rebuild-batch-1-ui-shell/design.md`, `docs/workflows/mvp-rebuild-batch-6-.../{tasks,audit,validation}.md`, `docs/workflows/manage-ui-consolidation/tasks.md:51`, `docs/workflows/personal-learning-system-v2-unification/i5-preparation-findings.md:15` (claims `/manage/settings` is a `FutureCapabilityPage`), plus `.kilo/worktrees/*` (separate branches). `PERSONAL_LEARNING_SYSTEM_AUDIT.md:327,378,546` references are consistent (it recommended the deletion). No live `src/`/`backend/` reference exists. | repo-wide grep output (below) | Optional doc hygiene only; historical records are evidence of prior decisions, not current authority. Do not edit historical docs as part of PR-18. |

No BLOCKER or HIGH finding. Per instructions no BLOCKER/HIGH reproduction is required.

## Verification 1 — exactly 5 items gone/edited, nothing else deleted

All 4 deleted paths were tracked at HEAD, absent on disk, and present as `D` in status; the 5th is a
one-line edit.

```bash
$ git status --short | grep -E '^ ?D'
 D src/app/manage/(workspace)/components/future-capability-page.tsx
 D src/app/manage/components/manage-placeholder-page.tsx
 D src/app/music/list.ts
 D src/components/wip.tsx
$ git status --short | grep -cE '^ ?D'
4
```

```bash
$ git diff -- src/app/blog/page.tsx
@@ -16,7 +16,6 @@ import { useAdminAuth } from '@/hooks/use-admin-auth'
 import { useReadArticles } from '@/hooks/use-read-articles'
 import JuejinSVG from '@/svgs/juejin.svg'
 import { useConfigStore } from '@/app/(home)/stores/config-store'
-import { readFileAsText } from '@/lib/file-utils'
 import { cn } from '@/lib/utils'
 import { EmptyState } from '@/components/empty-state'
 import { saveBlogEdits } from './services/save-blog-edits'
```

```bash
$ git diff --numstat -- 'src/components/wip.tsx' 'src/app/manage/components/manage-placeholder-page.tsx' \
    'src/app/manage/(workspace)/components/future-capability-page.tsx' 'src/app/music/list.ts' 'src/app/blog/page.tsx'
0	1	src/app/blog/page.tsx
0	64	src/app/manage/(workspace)/components/future-capability-page.tsx
0	26	src/app/manage/components/manage-placeholder-page.tsx
0	6	src/app/music/list.ts
0	27	src/components/wip.tsx
```

mtime isolation (only the edited file moved after PR-18's window):

```text
2026-09-26 15:48:02 src/app/blog/page.tsx   <-- only src/backend file with mtime >= 15:45
2026-05-31 17:17:02 backend/app/services/sm2.py
2026-06-02 14:38:05 src/lib/api/review.ts
2026-09-25 17:48:56 src/lib/api/knowledge-points.ts
```

Deleted-file line counts and definitions verified against `git show HEAD:<path>`:
`wip.tsx` 27, `music/list.ts` 6, `manage-placeholder-page.tsx` 26, `future-capability-page.tsx` 64
(`export default function WIP()` at wip.tsx:6 exactly as the evidence states).

## Verification 2 — static greps reproduce (no remaining source reference)

```bash
$ grep -rn "components/wip\|from './wip'\|from \"../wip\"\|from \"@/components/wip\"\|<WIP\|<Wip\|export default function WIP" src/ backend/ --include="*.ts" --include="*.tsx" --include="*.py"
(no output) exit=1
$ grep -rn "ManagePlaceholderPage\|manage-placeholder-page" src/ backend/ --include="*.ts" --include="*.tsx" --include="*.py"
(no output) exit=1
$ grep -rn "FutureCapabilityPage\|future-capability-page" src/ backend/ --include="*.ts" --include="*.tsx" --include="*.py"
(no output) exit=1
$ grep -rn "music/list\|from './list'\|from \"../list\"" src/ backend/ --include="*.ts" --include="*.tsx" --include="*.py"
(no output) exit=1
$ grep -rn "readFileAsText" src/ --include="*.ts" --include="*.tsx"
src/lib/file-utils.ts:3:export function readFileAsText(file: File): Promise<string> {
exit=0
```

Repo-wide grep confirms **zero** live `src/`/`backend/` references; only docs/evidence text and
separate `.kilo/worktrees/*` branches mention the identifiers (see R-04). `music/page.tsx` has no
`./list` import. No dangling import remains.

## Verification 3 — evidence authenticity

- Reproduced greps match the outputs quoted in `pr-18-cleanup-components.md` (same exit codes, same
  single `readFileAsText` line).
- `git diff --stat` current total `81 files changed, 3349 insertions(+), 1529 deletions(-)` matches the
  evidence's stated "After"; the stated Before `76/3349/1405` and delta `5/0/124` are arithmetically
  consistent with the verified After. (`w4-00-baseline-diffstat.txt` is `61/2601/1328` — a Week-start
  snapshot, not PR-18's before, as expected once PR-14…19 are included.)
- Deleted-file line counts (27/26/64/6) independently confirmed from git HEAD.
- SAFE_TO_DELETE authority mapping matches: candidates §1 items #5, #6, #7, #16, #17.

No fabricated output detected.

## Verification 4 — IN_USE / UNCLEAR items still present and untouched

```text
PRESENT: backend/app/services/sm2.py                 (mtime 2026-05-31)
PRESENT: src/lib/api/review.ts                       (mtime 2026-06-02)
PRESENT: src/lib/api/knowledge-points.ts             (mtime 2026-09-25)
dashboard tests: dashboard-content.test.tsx, dashboard-overview.test.tsx,
                 dashboard-content-verify.test.tsx, dashboard-verify.test.tsx  (all present)
PRESENT: src/features/ui-v2, src/components/ui-v2, docs/ui-v2
```

None appears in `git status --short` as modified and none has a PR-18-window mtime. The 4 dashboard
test files are unchanged by PR-18 (2 pre-existing untracked verify tests; 2 tracked baseline files
untouched by this PR). ui-v2 tree intact. Confirmed **untouched**.

## Verification 5 — after-state validation (raw)

```bash
$ npx vitest run
 Test Files  70 passed (70)
      Tests  522 passed (522)
   Duration  6.77s
VITEST_EXIT=0

$ npx tsc --noEmit
TSC_EXIT=0

$ npm run test:typecheck
> node node_modules/typescript/bin/tsc --noEmit --project tsconfig.test.json
TYPECHECK_EXIT=0

$ git diff --check
check_exit=0
```

Matches the evidence's claimed 70 files / 522 tests and exit 0 on all checks. No new failures.

## Verification 6 — net-line reporting vs ≥500 secondary metric

- Reported net: **124 lines removed / 0 added** — independently reproduced exactly
  (`1+64+26+6+27 = 124`, all in deletions). Honest and accurate.
- Plan metric (`tasks/week4-gate.md:42`): "Net reduction ≥500 lines removed (secondary metric)".
- PR-18's own two docs do **not** mention the metric (grep exit 1). The shortfall is disclosed only in
  `w4-00-decisions.md:87` (W4-E07: "far below the plan's ≥500 secondary metric").
- Assessment: the number is truthfully reported; the explicit "metric NOT met" statement is missing
  from the PR-18 artifact the gate cites → R-02 (LOW/NOTE).

## Unresolved questions

1. Should `TRACKING.md` and `tasks/pr-18.md` be reconciled to `PASS` now (R-01), or is tracking
   updated in a later gate step by convention? If the latter, the convention should be stated so the
   `NOT_STARTED` state is not mistaken for a real blocker.
2. Confirm the planned gate will record `Net reduction: 124 (<500) — secondary metric NOT MET` rather
   than silently omitting it (R-02), since the gate matrix is the ultimate authority for this metric.
3. Is `readFileAsText` retention in `src/lib/file-utils.ts` accepted as follow-up #3, or does the gate
   require it resolved before Week 4 closure? (No correctness impact either way.)
