# Decisions

## D1. Subject Means Learning Namespace

Decision:

Subject represents a top-level private learning namespace / learning track.

It can model a discipline, course, exam subject, or self-study track, but the system does not split these into separate domain entities in Batch 2.

Rationale:

- It keeps the MVP simple.
- It avoids premature curriculum/exam modeling.
- It provides a stable partition for Knowledge Point trees.
- It lets future Question, Mistake, and Review link to a consistent root.

Alternatives rejected:

- Separate Discipline/Course/ExamSubject tables.
- Treat Subject as a public content category.
- Treat Subject as a Review or Analytics entity.

## D2. Knowledge Point Uses Self-Referential Tree

Decision:

Knowledge Point uses `parent_id` self-reference.

Rationale:

- Supports unlimited hierarchy.
- Directly models the requested tree example.
- Avoids adding Chapter as a third Batch 2 domain.
- Works for future mind-map rendering.

Alternatives rejected:

- Separate `chapters` table.
- Materialized path as primary schema.
- Nested set model.

## D3. Chapter Is A Knowledge Point, Not A Separate Batch 2 Domain

Decision:

Chapter-like nodes such as `高等数学` or `线性代数` are represented as Knowledge Points with children.

Rationale:

- User scope explicitly says Batch 2 only covers Subject and Knowledge Point.
- A separate Chapter table would complicate routing, API, migration, and later linking.
- Knowledge Point tree can represent sections, chapters, topics, formulas, and concepts uniformly.

## D4. Status Is Active / Archived

Decision:

Subject and Knowledge Point use:

```text
active
archived
```

Rationale:

- Draft is unnecessary for manually created taxonomy.
- Archived preserves history and references.
- Hard delete can be a guarded operation later, but should not be the default lifecycle.

## D5. Future APIs Are Admin-Only

Decision:

All Subject and Knowledge Point management APIs require backend admin authentication.

Rationale:

- These are private learning management entities.
- Public pages must not request admin APIs and degrade from 401/403.
- Batch 1 `AuthGate` only controls page experience, not security.

## D6. Batch 2 Does Not Design Cross-Domain Links

Decision:

Batch 2 documents that future domains may reference Knowledge Points, but does not design Question, Mistake, Review, Attachment, AI, Search, or Analytics contracts.

Rationale:

- Prevents batch drift.
- Keeps Subject/Knowledge Point clean.
- Leaves each future domain to define its own relation semantics.

## D7. Existing Historical Artifacts Are Context, Not Current Approval

Decision:

Existing files or older workflow notes related to Subject/Taxonomy are treated as current-state evidence and risk context, not as approval to implement in this round.

Rationale:

- The current user instruction says this stage is architecture design only.
- We must not modify database, backend, frontend page logic, or migrations.
- Dirty worktree changes are preserved and not reverted.

## D8. First Version Has No Owner Model

Decision:

Do not add `owner_id` to `subjects` or `knowledge_points` in the first version.

Rationale:

- The system is currently a single-user Personal Learning System.
- Introducing User, Owner, permission scope, or multi-tenant workspace modeling now would increase complexity without improving the MVP learning loop.
- If SaaS or collaboration appears later, ownership and workspace boundaries must be designed as their own phase.

## D9. Knowledge Point Archive Archives The Subtree

Decision:

Archiving a Knowledge Point recursively archives all descendants.

Rationale:

- Knowledge tree parent-child semantics are strong.
- Active children below archived parents create broken default queries and mind-map gaps.
- Service logic must preserve tree consistency.

## D10. Tree API Defaults To Nested Tree

Decision:

`GET /api/admin/subjects/{id}/knowledge-tree` returns nested tree by default.

Flat node queries remain available for editing, large-tree loading, movement validation, recursive computation, and future search indexing.

Rationale:

- Page rendering and future mind-map surfaces naturally consume nested trees.
- Flat operations are still useful internally and for efficient manipulation.

## Open Decisions Before Implementation

- Whether hard delete exists at all or only archive is exposed.
- Whether normalized-name uniqueness should be case-insensitive in the initial database migration.
