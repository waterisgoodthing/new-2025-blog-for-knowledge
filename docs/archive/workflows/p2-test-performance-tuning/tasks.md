# Tasks

Approved by the user on 2026-07-31 for sequential execution.

- [x] **P2-TEST-PERF-01** Run the full frontend suite, capture the complete
  warning output, and identify the exact test cases and asynchronous updates.
  - Baseline: 23 files / 64 tests passed.
  - Warning sources: `static-placeholders.test.tsx` render calls at lines 47
    and 54, plus `page.test.tsx` at line 39.
  - Cause: each test ended before the mocked `getAiRuns()` promise completed;
    the resulting `setRuns`, `setTotal`, and `setLoading` updates escaped the
    Testing Library async boundary.
- [x] **P2-TEST-PERF-02** Apply minimal test-only synchronization fixes, then
  verify each focused test file passes without React `act(...)` warnings.
  - Added user-visible async completion assertions to the three affected tests.
  - Focused result: 2 files / 5 tests passed with zero React `act(...)`
    warnings.
- [x] **P2-TEST-PERF-03** Run the complete frontend suite and confirm all tests
  pass with no React `act(...)` warnings or count regression.
  - Full result: 23 files / 64 tests passed in 2.13s.
  - React `act(...)` warnings: zero.
  - Existing unrelated `DEP0205` and `TimeoutNaNWarning` output remains outside
    this approved scope.
- [x] **P2-TEST-PERF-04** Add eager/high-priority loading to the anonymous
  `/manage` avatar and validate the page at 1280x800, 1440x900, and 390x844.
  - Added `loading="eager"` and `fetchPriority="high"` to the existing login
    avatar, plus a focused DOM regression assertion.
  - At all three exact content viewports the image was complete, rendered at
    56x56, exposed both attributes, and produced no horizontal overflow.
  - No LCP/eager-loading guidance appeared in the three-second console
    observation window at any size; visual inspection showed no regression.
- [x] **P2-TEST-PERF-05** Run TypeScript and production-build gates, update
  validation evidence, and review the final scoped diff and worktree status.
  - Final suite: 23 files / 64 tests passed with zero React `act(...)`
    warnings.
  - `npx tsc --noEmit`, `npm run build` (40/40 static pages), and
    `git diff --check` passed.
  - The worktree contains only the four approved frontend files and this
    workflow directory. Changes remain intentionally uncommitted and ready for
    review; no stage, commit, push, deployment, backend, or database action
    occurred.
