# Design

## Existing Behavior

`useReviewStats(isAdmin)` and `useReviewPlan(isAdmin)` use `null` SWR keys when `isAdmin` is false. This is the correct conditional-fetch pattern and must not be replaced with conditional Hook invocation.

## Change Strategy

Prefer regression tests over production-code changes. If the test exposes a real request path, make the smallest change inside the shared hook or public page while preserving Hook call order and existing admin rendering.

## Permission Contract

- Anonymous `/mistakes`: public Note list only; no admin review requests.
- Admin `/mistakes`: may request review stats/plan and render the private summary.
- Backend `/api/review/*` remains the real permission boundary.
