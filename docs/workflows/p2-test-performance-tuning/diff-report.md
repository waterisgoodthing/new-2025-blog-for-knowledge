# Diff Report

## Source Changes

- `src/app/manage/(workspace)/ai/page.test.tsx`: await the async empty state.
- `src/app/manage/(workspace)/ai/static-placeholders.test.tsx`: await the
  async empty state in both AI route smoke tests.
- `src/app/manage/manage-auth.test.tsx`: assert eager/high-priority avatar
  loading in the anonymous login state.
- `src/app/manage/page.tsx`: add `loading="eager"` and
  `fetchPriority="high"` to the existing login avatar.

Source diff: 4 files, 11 insertions, 3 deletions.

## Scope Review

- No production component behavior changed except the two image loading hints.
- No Dashboard, AuthGate, permission, backend, database, dependency, snapshot,
  deployment, or generated-content changes.
- The workflow directory contains planning and acceptance evidence required by
  repository policy.
- `git diff --check` passed.
