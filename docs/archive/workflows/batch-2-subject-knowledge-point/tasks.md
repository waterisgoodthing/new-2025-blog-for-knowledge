# Tasks

> Status: approved for implementation by the user. Execute in order and update this file immediately after each completed item.

## Design Freeze Tasks

- [x] Read mandatory architecture and Batch 1 context.
- [x] Confirm Batch 1 completion and route-shell availability.
- [x] Record missing requested docs: `docs/README.md`, `docs/PROJECT_CURRENT_STATUS.md`.
- [x] Define Subject domain boundary, lifecycle, status, and rationale.
- [x] Define Knowledge Point tree model and invariants.
- [x] Design future `subjects` schema.
- [x] Design future `knowledge_points` schema with `parent_id` self-reference.
- [x] Design `/manage/subjects` and `/manage/knowledge-points` route responsibilities.
- [x] Define future API contracts without implementation.
- [x] Record decisions, open questions, risks, and implementation gate.
- [x] Apply approved decision update: no owner model, subtree archive, nested tree API by default.

## Implementation Tasks

These are approved for execution in order.

- [x] P0-01 Audit existing database and code state for `subjects`, `knowledge_points`, `chapters`, and related migrations.
- [x] P0-02 Compare old model/migration/API/UI against frozen design and write migration strategy.
- [x] P0-03 Implement schema migration to align `subjects` and `knowledge_points` with the frozen model.
- [x] P0-04 Implement backend schemas/services/routers with admin auth and tree invariants.
- [x] P0-05 Implement frontend API client types for Subject and Knowledge Point tree.
- [x] P0-06 Replace only `/manage/subjects` and `/manage/knowledge-points` placeholders with real UI.
- [x] P0-07 Validate backend tests, frontend tests/typecheck/build, route behavior, permissions, and no public-page regression.

## Hard Stops

- [ ] Do not modify Question/Mistake/Review/Attachment/OCR/AI/Search/Analytics behavior.
- [ ] Do not introduce `owner_id`.
- [ ] Do not create a separate `chapters` domain in the final Batch 2 model.
- [ ] Do not delete old system files casually.
- [ ] Do not touch unrelated dirty worktree changes.

## Approval Gate

Human approval received:

```text
Approve Batch 2 Subject / Knowledge Point tasks
```
