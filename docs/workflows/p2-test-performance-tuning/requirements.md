# Requirements

## Functional Scope

- Locate every React `act(...)` warning in the current frontend suite.
- Fix warnings using correct asynchronous test synchronization.
- Preserve all existing assertions and application behavior.
- Eagerly load the anonymous `/manage` avatar with high fetch priority.

## Acceptance

- `npm test -- --run` passes with no React `act(...)` warning and no reduction
  from the current test file/test count baseline.
- `npx tsc --noEmit` passes.
- `npm run build` passes and reports the expected static page total.
- `/manage` shows no avatar LCP eager-loading suggestion at 1280x800,
  1440x900, or 390x844.
- The avatar remains visible without functional or visual regression.

## Constraints

- No test framework/toolchain refactor.
- No business logic, component behavior, Dashboard, AuthGate, or permission
  logic changes.
- No backend or database work.
- During implementation, no deployment, staging, commit, or push.
- The user separately authorized staging, commit, and push on 2026-07-31;
  deployment remains prohibited.
