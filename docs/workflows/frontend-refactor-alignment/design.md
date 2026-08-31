# Design

## 1. Documentation Precedence

For present-state assertions, use this order:

1. Current source, package manifest, migrations, and executable tests.
2. Current root README and a completed workflow validation record when it cites fresh evidence.
3. Current roadmap documents, but only after their individual assertions are checked against source.
4. Historical refactor plans, audits, and task lists as intent and provenance only.

No document may be called authoritative merely because its heading says so when its file-path or runtime assertion contradicts the source tree.

## 2. Target Task Decomposition

The broad proposal is split into six independently approved future task groups:

At the orchestration level, the first five groups are owned by [frontend-foundation-and-quality](../frontend-foundation-and-quality/README.md). Visual-system consolidation remains the second master category and is not absorbed into the foundation workflow.

| Group | Scope | Explicit exclusion |
| --- | --- | --- |
| Route ownership alignment | Decide whether the long-term owner is /manage/(workspace), legacy routes, or a new route family; inventory links and compatibility needs. | No redirect or deletion before its own approval. |
| Editor convergence | Define a shared editor capability boundary and compare note, blog, and mistake workflows. | No UnifiedEditor implementation or route switch. |
| Visual-system consolidation | Inventory theme tokens and repeated surface patterns; design a minimal shared token/component strategy. | No broad CSS rewrite or cosmetic sweep. |
| Markdown rendering security | Execute the isolated markdown-rendering-security-poc only after its own task-list approval. | No production consumer migration or legacy renderer deletion. |
| Public session state optimization | Replace anonymous public-page `/api/auth/me` 401 probing with a minimal optional-session contract and shared frontend state. | No mutation permission change, AuthGate weakening, or auth bypass. |
| Production render readiness acceptance | Add stable page-readiness evidence and measure representative production builds with synthetic data. | No production deployment, real credentials, or SLA claim based only on the local empty-data probe. |

## 3. Required Output Per Follow-up

Every follow-up must contain a task workspace with README, design, requirements, tasks, and validation. Its task list must:

- identify exact owner routes and public/admin access implications;
- list source files, tests, browser checks, and rollback boundary;
- keep unrelated refactor-plan proposals out of scope;
- state whether it changes a public route, a private route, or shared infrastructure;
- require separate user approval before implementation.

## 4. Guardrails

- Preserve public note, blog, and mistake reads.
- Do not use the presence of src/app/manage/(workspace) as proof that a /workspace route exists.
- Do not delete legacy write routes merely because historical documents proposed it.
- Treat Markdown written by administrators and AI as untrusted when planning the rendering work.
- Do not change package dependencies in this documentation-alignment workflow.
- Preserve `GET /api/auth/me` as a strict protected identity contract; any public optional-session contract must be separate and minimal.
- Treat the 2026-08-03 timing sample as a local empty-data development baseline, not as a production performance guarantee.

## 5. Runtime Probe Amendment (2026-08-03)

The completed `page-render-timing-validation` workflow adds runtime evidence that was absent from the original broad proposal:

| Scenario | Browser samples | Local content-ready proxy | Boundary |
| --- | ---: | ---: | --- |
| Anonymous `/notes` | 5 | median 284.9 ms; max 362.8 ms | Empty isolated database, development server already running |
| Password login to `/manage` | 5 | median 201.0 ms; max 334.5 ms | Empty isolated database, normal cookie login, no auth bypass |

The anonymous route rendered correctly but unconditionally called `GET /api/auth/me` and received 401 before degrading to non-admin state. Source inventory shows that `useAdminAuth` is also consumed by several other public routes and shared navigation components. The technical response is therefore a shared session-state task, not a `/notes`-only patch.

The timing values are evidence for measurement feasibility only. They do not validate real content volume, production builds, public CDN behavior, mobile networks, or server cold starts. Those gaps belong to a separate acceptance task group.

## 6. Cross-Reference Repair Queue

The following locations remain historical until a later documentation-maintenance task updates them. They are not changed by this workflow because their scope is broader than the new reconciliation record.

| Location | Required future correction |
| --- | --- |
| docs/refactor-plan/00-CORRECTED-PHASED-PLAN.md | Label the /workspace route, route deletion, and old phase gates as historical proposals; link to the route-ownership task group. |
| docs/refactor-plan/03-IMPLEMENTATION-PLAN-KEEP-VISUAL.md | Separate completed sync removal from unimplemented route and UnifiedEditor proposals. |
| docs/refactor-plan/04-DESIGN-REFACTOR-PROPOSAL.md | Replace statements that describe /workspace as already created with current route evidence or a product decision. |
| docs/note-editor-tasks.md | Reconcile source-present editor components with unchecked task boxes and retain unverified browser evidence as unverified. |
| docs/roadmap-tasks.md | Identify and label old GitHub-sync references that conflict with the supported persistence declaration in root README. |

The six follow-up task workspaces created or linked by this workflow are the current planning entry points. They do not supersede source code or grant implementation authority.
