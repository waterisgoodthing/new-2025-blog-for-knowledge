# Requirements

1. Anonymous rendering of `/mistakes` must not invoke `getReviewStats`.
2. Anonymous rendering of `/mistakes` must not invoke `getReviewPlan`.
3. Admin rendering may enable both review hooks.
4. All Hooks must be called unconditionally and in stable order.
5. Public mistake list behavior and admin-only UI visibility must remain unchanged.
6. No backend, database, migration, Batch 7, or unrelated public-page changes.
