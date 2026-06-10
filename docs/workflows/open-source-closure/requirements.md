# Requirements

## Objective

Ship an open-source-safe version of the repository that no longer depends on GitHub sync as a write path and that has a clear single-source-of-truth story for active content domains.

## Scope

In scope:

- Remove GitHub sync write capabilities from the active application flow.
- Identify and replace UI flows that still depend on GitHub sync.
- Close the highest-risk public/private data exposure gaps that are directly affected by sync removal.
- Clarify runtime and contributor setup for open-source use.
- Record validation evidence for the new architecture.
- Migrate currently editable legacy static-content domains onto backend APIs so editing remains available after sync removal.

Out of scope unless explicitly approved later:

- Broad redesign of unrelated frontend routes.
- Production secret rotation or live deployment operations.
- Data migration of user-owned production content outside the repository.

## Functional Requirements

1. Active admin write flows must no longer require GitHub repository write access.
2. Public readers must not receive hidden, draft, or admin-only note content through the post-change public API.
3. Editable legacy static-content domains must retain edit capability through backend-owned APIs after GitHub sync removal.
4. README setup instructions must match the actual package manager and runtime expectations in the repo.
5. Open-source collaboration basics must be documented with at least contribution and security guidance.
6. The repository must have a clear documented source-of-truth model for each active content domain after migration.

## Non-Functional Requirements

1. Changes should preserve existing admin workflows by migrating them to backend architecture rather than dropping edit support.
2. The new design should reduce accidental public exposure of private learning content.
3. The implementation should keep the codebase easier to understand, not replace GitHub sync with another hidden dual-write path.
4. Validation must distinguish verified runtime behavior from environment-blocked checks.

## Decisions Needed During Implementation

1. Whether startup `create_all` remains temporarily tolerated during this task or is included in scope for final release cleanup.
2. How much cross-domain normalization is acceptable in one round versus route-by-route API migration with shared primitives underneath.
3. Whether the home/site settings domain should land in a generic config API or a more explicit site-settings contract.

## Acceptance Criteria

1. No active UI action in the supported management flow calls the GitHub sync API path.
2. Backend GitHub sync endpoints and service code are removed or explicitly retired from the app surface.
3. Public note APIs enforce a safe anonymous-read policy.
4. Legacy editable static domains continue to support save/edit through backend APIs rather than GitHub sync.
5. Documentation explains how to run the project locally without GitHub sync secrets.
6. Validation notes record TypeScript, targeted backend checks, and route-level behavior relevant to the removed sync flow.
