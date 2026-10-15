# PR-18 Evidence — SAFE_TO_DELETE Legacy Cleanup (3 components + music/list + dead import)

Status: **PASS** (deletions executed; static + test + no-surface evidence complete; before/after validation green)
Date: 2026-09-26
Repo: `/Users/limengyang/2025-blog-public`
Branch/HEAD: `refactor/baseline` @ `4a954eaa92952fcc5a6b18a2e15d2e824b094e41`
Source classification: `w4-00-cleanup-candidates.md` (§1 items #5, #6, #7, #16, #17)
Write scope honored: 4 file deletions + 1 import-line removal only. No other file edited, staged, or committed. **No git write, no DB command.**

Deleted (4 files):

| # | File | Lines removed |
|---|------|---------------|
| 1 | `src/components/wip.tsx` | 27 |
| 2 | `src/app/manage/components/manage-placeholder-page.tsx` | 26 |
| 3 | `src/app/manage/(workspace)/components/future-capability-page.tsx` | 64 |
| 4 | `src/app/music/list.ts` | 6 |

Edited (1 line): `src/app/blog/page.tsx` — removed `import { readFileAsText } from '@/lib/file-utils'` (old line 19). Rest of file unchanged.

---

## Three-part evidence (W4-D07)

Each item below records: **Static** (no remaining reference in `src/` and `backend/`, tests included), **Tests** (no dedicated test references it), **Runtime / no-surface** (no page/route imports it, so no rendered surface can reach it). Commands were run after deletion; exit `1` from `grep` = no matches (expected).

### Item 1 — `src/components/wip.tsx`

Static (no remaining reference):

```bash
$ grep -rn "components/wip\|from './wip'\|from \"../wip\"\|from \"@/components/wip\"\|<WIP\|<Wip\|export default function WIP" src/ backend/ --include="*.ts" --include="*.tsx" --include="*.py"
(no output)
exit=1
```

Tests (no dedicated test):

```bash
$ grep -rn "components/wip\|<WIP\|<Wip" src/ --include="*.test.ts" --include="*.test.tsx"
(no output)
exit=1
```

Runtime / no-surface (no page or route imports it):

```bash
$ grep -rn "components/wip" src/app --include="*.ts" --include="*.tsx"
(no output)
exit=1
```

Pre-deletion reference scan showed only the file's own definition (`src/components/wip.tsx:6:export default function WIP()`); no import sites existed. Deleting it cannot remove a rendered surface.

### Item 2 — `src/app/manage/components/manage-placeholder-page.tsx`

Static:

```bash
$ grep -rn "ManagePlaceholderPage\|manage-placeholder-page" src/ backend/ --include="*.ts" --include="*.tsx" --include="*.py"
(no output)
exit=1
```

Tests:

```bash
$ grep -rn "ManagePlaceholderPage" src/ --include="*.test.ts" --include="*.test.tsx"
(no output)
exit=1
```

Runtime / no-surface:

```bash
$ grep -rn "manage-placeholder-page" src/app --include="*.ts" --include="*.tsx"
(no output)
exit=1
```

Pre-deletion reference scan showed only the file's own definition + props interface (`:4`, `:11`, `:16`); zero import sites.

### Item 3 — `src/app/manage/(workspace)/components/future-capability-page.tsx`

Static:

```bash
$ grep -rn "FutureCapabilityPage\|future-capability-page" src/ backend/ --include="*.ts" --include="*.tsx" --include="*.py"
(no output)
exit=1
```

Tests:

```bash
$ grep -rn "FutureCapabilityPage" src/ --include="*.test.ts" --include="*.test.tsx"
(no output)
exit=1
```

Runtime / no-surface:

```bash
$ grep -rn "future-capability-page" src/app --include="*.ts" --include="*.tsx"
(no output)
exit=1
```

Pre-deletion reference scan showed only the file's own definition + props interface (`:12`, `:20`, `:26`); zero import sites.

### Item 4 — `src/app/music/list.ts`

Static:

```bash
$ grep -rn "music/list\|from './list'\|from \"../list\"" src/ backend/ --include="*.ts" --include="*.tsx" --include="*.py"
(no output)
exit=1
```

Tests:

```bash
$ grep -rn "music/list\|from './list'" src/ --include="*.test.ts" --include="*.test.tsx"
(no output)
exit=1
```

Runtime / no-surface:

```bash
$ grep -rn "music/list" src/app --include="*.ts" --include="*.tsx"
(no output)
exit=1
```

`src/app/music/page.tsx` imports from `@/lib/api/music-manage` only and never referenced `./list`; the module was a 1-item iframe data array with zero call sites.

### Item 5 — dead `readFileAsText` import in `src/app/blog/page.tsx`

Static (import removed; only the out-of-scope definition in `src/lib/file-utils.ts` remains):

```bash
$ grep -rn "readFileAsText" src/ --include="*.ts" --include="*.tsx"
src/lib/file-utils.ts:3:export function readFileAsText(file: File): Promise<string> {
exit=0
```

The `src/app/blog/page.tsx` occurrence is gone. `src/lib/file-utils.ts` is **not in WRITE SCOPE** and was left untouched; its exported `readFileAsText` is now an unused (but still exported) utility — see DECISION NEEDED in `pr-18-summary.md`.

Tests:

```bash
$ grep -rn "readFileAsText" src/ --include="*.test.ts" --include="*.test.tsx"
(no output)
exit=1
```

Runtime / no-surface: the symbol had exactly one occurrence repo-wide — the removed import line; no JSX/route consumed it, so no rendered surface depended on it.

---

## Before / After validation (raw)

`npm run test:typecheck` must stay exit 0 (satisfied). Same three commands on both sides.

### BEFORE

```bash
$ npx vitest run
 Test Files  70 passed (70)
      Tests  522 passed (522)
   Duration  5.54s
EXIT=0

$ npx tsc --noEmit
EXIT=0

$ npm run test:typecheck
> node node_modules/typescript/bin/tsc --noEmit --project tsconfig.test.json
EXIT=0
```

### AFTER

```bash
$ npx vitest run
 Test Files  70 passed (70)
      Tests  522 passed (522)
   Duration  5.47s
EXIT=0

$ npx tsc --noEmit
EXIT=0

$ npm run test:typecheck
> node node_modules/typescript/bin/tsc --noEmit --project tsconfig.test.json
EXIT=0
```

No new failures; identical file/test counts (70 / 522) and exit 0 on all three.

### Dangling-import + worktree proof (after)

```bash
$ grep -rn "manage-placeholder-page\|future-capability-page\|music/list\|components/wip" src/app --include="*.ts" --include="*.tsx"
(no output)   # exit=1
```

```bash
$ git diff --check
check exit=0
```

Status delta before → after shows exactly the 5 intended paths and nothing else:

```text
>   M src/app/blog/page.tsx
>   D src/app/manage/(workspace)/components/future-capability-page.tsx
>   D src/app/manage/components/manage-placeholder-page.tsx
>   D src/app/music/list.ts
>   D src/components/wip.tsx
```

---

## Net lines removed

```bash
$ git diff --numstat -- 'src/components/wip.tsx' 'src/app/manage/components/manage-placeholder-page.tsx' 'src/app/manage/(workspace)/components/future-capability-page.tsx' 'src/app/music/list.ts' 'src/app/blog/page.tsx'
0	1	src/app/blog/page.tsx
0	64	src/app/manage/(workspace)/components/future-capability-page.tsx
0	26	src/app/manage/components/manage-placeholder-page.tsx
0	6	src/app/music/list.ts
0	27	src/components/wip.tsx
```

**Net: 124 lines removed, 0 lines added** across 5 files (deletion-only change; no reformatting).

## Explicit non-actions

- `backend/app/services/sm2.py`, `src/lib/api/review.ts`, dashboard tests, `src/lib/api/knowledge-points.ts`, the ui-v2 tree, `/api/admin/diagnostics`, `/api/admin/workspace/files`, and all endpoint/analytics code were **not touched** (`w4-00-cleanup-candidates.md` classifies them `IN_USE`/`UNCLEAR`).
- No file outside WRITE SCOPE was reformatted, moved, staged, or committed.
- No git write and no DB command was performed.
