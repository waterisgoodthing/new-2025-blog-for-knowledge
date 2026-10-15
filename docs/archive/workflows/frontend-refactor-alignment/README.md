# Frontend Refactor Alignment

## Goal

Turn the supplied broad frontend-refactor documentation into a current, implementable sequence without treating historical plans as present-state facts. This workflow is documentation-only: it reconciles routing, editor, visual-system, Markdown-rendering, public-session-state, and render-readiness plans with the current source tree.

## Touched Domains

- Shared frontend architecture and documentation.
- Public and administrator route inventory.
- Note, blog, and mistake editor boundaries.
- Shared Markdown rendering boundary.
- Public-route session probing and render-readiness measurement boundaries.

No source code, package manifest, lockfile, API contract, database schema, deployment setting, or authentication behavior is changed by this workflow.

## Current Status

Complete. The task list was approved in the conversation and the documentation-only work is complete. The initial source comparison found that the supplied worktree and this repository share baseline commit 202ea14d3362a84a491a7a8e32d2afd5d2e0bc1f, while several historical planning documents no longer describe the source tree.

## Documents

- [Audit](./audit.md)
- [Design](./design.md)
- [Requirements](./requirements.md)
- [Tasks](./tasks.md)
- [Validation](./validation.md)

## Decision Boundary

Approval of this task list authorizes documentation reconciliation and the creation of separately gated follow-up task groups only. It does not authorize route deletion, redirects, editor consolidation, dependency changes, Markdown renderer replacement, production deployment, or database work.

## Master Categories

1. [Frontend foundation and quality](../frontend-foundation-and-quality/README.md): route ownership, Markdown security, editor convergence, public session state, and production render readiness.
2. [Visual system consolidation](../visual-system-consolidation/README.md): shared visual, overlay, context action, and navigation migration after foundation gates.

## Recommended Next Approval Order

1. Approve the F0 baseline of `frontend-foundation-and-quality`.
2. Complete its gated route, Markdown/editor, session-state, and render-readiness phases.
3. Continue `visual-system-consolidation` implementation phases only after the relevant foundation gates are stable.

The foundation master task list is AWAITING USER APPROVAL. In the visual workflow, only its separately recorded VSC-01 read-only baseline approval is in force; no later phase starts automatically.
