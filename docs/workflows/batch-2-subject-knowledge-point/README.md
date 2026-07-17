# Batch 2 - Subject / Knowledge Point Domain Design

## Goal

Freeze the domain design for the two Batch 2 learning organization domains:

- Subject
- Knowledge Point

This workflow is design-only. It does not implement schema, migration, backend routes, frontend pages, CRUD, or visualization.

## Current Status

Status: **Design ready for human review. Implementation not approved.**

Batch 1 is confirmed complete from:

- `docs/batch1-route-current-state.md`
- `docs/batch1-ui-shell-design.md`
- `docs/batch1-ui-shell-validation.md`
- `docs/batch1-handoff.md`
- `docs/workflows/mvp-rebuild-batch-1-ui-shell/validation.md`

Batch 1 provides `/manage` workspace shell, `AuthGate`, sidebar/topbar, and static route containers for:

- `/manage/subjects`
- `/manage/subjects/[id]`
- `/manage/knowledge-points`
- `/manage/knowledge-points/[id]`

Those routes remain containers only in this design round.

## Mandatory Context Read

Read and used:

- `docs/architecture/personal-learning-system-v2.md`
- `docs/architecture/domains.md`
- `docs/architecture/routes.md`
- `docs/architecture/ui-redesign.md`
- `docs/architecture/mvp-scope.md`
- `docs/architecture/implementation-phases.md`
- `docs/batch1-route-current-state.md`
- `docs/batch1-ui-shell-design.md`
- `docs/batch1-ui-shell-validation.md`
- `docs/batch1-handoff.md`
- `docs/workflows/mvp-rebuild-batch-1-ui-shell/`

Requested but not found in the current worktree:

- `docs/README.md`
- `docs/PROJECT_CURRENT_STATUS.md`

This absence is recorded as an evidence gap, not silently ignored.

## Scope

In scope:

- Subject definition, boundary, lifecycle, status, and relation to Knowledge Point.
- Knowledge Point tree model with unlimited hierarchy, parent-child relation, sorting, detail route support, and future mind-map readiness.
- Future schema design for `subjects` and `knowledge_points`.
- Future route design for `/manage/subjects`, `/manage/subjects/[id]`, `/manage/knowledge-points`, `/manage/knowledge-points/[id]`.
- Future API contract only.
- Implementation task list for later approval.

Out of scope:

- Question
- Mistake
- Review
- Attachment
- OCR
- AI
- Upload
- Search
- Analytics
- Real CRUD
- Backend implementation
- Frontend implementation
- Database migration
- Mind-map component
- Third-party libraries

## Documents

- [Requirements](./requirements.md)
- [Domain Design](./domain-design.md)
- [Schema Design](./schema-design.md)
- [Route Design](./route-design.md)
- [API Contract](./api-contract.md)
- [Decisions](./decisions.md)
- [Tasks](./tasks.md)

## Batch 2 Design Report

### 1. Current Design Conclusion

Subject is the top-level private learning namespace. It can represent a school discipline, course, exam subject, or self-study track, but the system treats all of these as one domain object: a stable learning container used to organize Knowledge Point trees.

Knowledge Point is the unit of conceptual organization inside one Subject. It uses a self-referential `parent_id` tree, not a separate Chapter table in this Batch 2 design. This supports examples such as:

```text
数学
├── 高等数学
│   ├── 函数
│   │   └── 三角函数
│   └── 极限
└── 线性代数
```

Future Question, Mistake, and Review domains may reference Subject and Knowledge Point by stable IDs, but they are not designed or implemented in this batch.

### 2. Updated Decisions

- Owner model: first version does not introduce multi-user ownership. `subjects.owner_id` and `knowledge_points.owner_id` are cancelled.
- Knowledge Point archive: archive a subtree recursively to preserve tree consistency.
- Tree API: default response is nested tree from `GET /api/admin/subjects/{id}/knowledge-tree`; flat node queries remain available for editing, validation, and future indexing.

### 3. Remaining Open Questions

- Whether slug fields are needed in the first implementation. Current design keeps admin routes ID-based and treats slug as optional/deferred.
- Whether hard delete exists at all in first implementation or only archive is exposed. Current design prefers archive for user-created taxonomy data.

### 4. Risk Analysis

- The repository already contains later-batch and historical Subject/Taxonomy implementation artifacts. This design does not assume they are approved for the current round.
- A self-referential tree needs cycle prevention in service logic and database-safe parent validation.
- Unlimited hierarchy is product-supported, but UI must use progressive disclosure to avoid rendering a huge tree at once.
- Moving or renaming old taxonomy files without approval would blur history and is forbidden.

### 5. Follow-Up Implementation Advice

- Implement by vertical slices after human approval: Subject list/detail first, then Knowledge Point root list, then parent-child operations, then tree reorder.
- Add migration only after `tasks.md` is approved.
- Use backend service validation for parent-child integrity and cycle prevention.
- Keep Question/Mistake/Review linkage out until their batches explicitly approve it.

## Gate

Batch 2 design has been reviewed and the implementation task list is approved by the user.

Implementation must still proceed in the approved order and update `tasks.md` after each completed item.
