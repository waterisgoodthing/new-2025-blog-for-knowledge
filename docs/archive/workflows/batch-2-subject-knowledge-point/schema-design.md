# Schema Design

## Scope

This document designs schema only. It does not create or edit migrations.

Tables designed:

- `subjects`
- `knowledge_points`

Not designed in Batch 2:

- `questions`
- `mistakes`
- `review_items`
- `attachments`
- `ai_runs`
- search indexes
- analytics tables
- mind-map or graph tables

## Ownership Decision

First version does not introduce a multi-user owner model.

Do not add:

```sql
subjects.owner_id
knowledge_points.owner_id
```

Rationale:

- Current product is a Personal Learning System for a single learner.
- Multi-user ownership, workspace, tenant, and permission scope would add database, API, and migration complexity without improving the current learning loop.
- If SaaS or collaboration is introduced later, design `users`, `ownership`, `permissions`, and `workspace` as a separate architecture phase.

## `subjects`

### Purpose

Top-level private learning namespace.

### Proposed Fields

| Field | Type | Null | Default | Notes |
| --- | --- | ---: | --- | --- |
| `id` | integer / bigint | no | auto | Primary key |
| `name` | varchar(120) | no | none | Display name |
| `description` | text | yes | null | Optional human description |
| `status` | varchar(20) | no | `active` | `active` or `archived` |
| `sort_order` | integer | no | `0` | Manual ordering |
| `created_at` | timestamptz | no | now | Creation timestamp |
| `updated_at` | timestamptz | no | now | Update timestamp |

### Constraints

- Primary key: `id`.
- `name` must not be empty after trimming, enforced by application validation and preferably database check if supported.
- `status in ('active', 'archived')`.
No owner FK in the first version.

### Uniqueness

Recommended:

```text
unique(lower(name))
```

Do not rely only on case-sensitive uniqueness if the product treats `Math` and `math` as the same Subject.

### Indexes

- `(status, sort_order, id)` for single-admin MVP.
- Unique normalized-name index as above.

### Delete Behavior

Hard delete must be blocked while Knowledge Points exist.

Preferred lifecycle is:

```text
active -> archived
```

Archiving preserves references and avoids silent data loss.

## `knowledge_points`

### Purpose

Self-referential tree of concepts/topics inside a Subject.

### Proposed Fields

| Field | Type | Null | Default | Notes |
| --- | --- | ---: | --- | --- |
| `id` | integer / bigint | no | auto | Primary key |
| `subject_id` | integer / bigint | no | none | FK to `subjects.id` |
| `parent_id` | integer / bigint | yes | null | FK to `knowledge_points.id` |
| `name` | varchar(160) | no | none | Node display name |
| `description` | text | yes | null | Detail page content |
| `status` | varchar(20) | no | `active` | `active` or `archived` |
| `sort_order` | integer | no | `0` | Sibling order |
| `created_at` | timestamptz | no | now | Creation timestamp |
| `updated_at` | timestamptz | no | now | Update timestamp |

### Foreign Keys

- `subject_id -> subjects.id`
- `parent_id -> knowledge_points.id`

Recommended FK behavior:

- `subject_id`: restrict hard delete if children exist, or use application-level delete guard.
- `parent_id`: `ON DELETE RESTRICT` for strict safety, or `ON DELETE SET NULL` only if product accepts promoting children to root.

Batch 2 design preference:

```text
parent_id ON DELETE RESTRICT
```

Rationale: silent reparenting changes the user's knowledge tree. If future implementation wants "delete parent and promote children", it should be explicit UI behavior, not automatic FK behavior.

### Constraints

- `name` must not be empty after trimming.
- `status in ('active', 'archived')`.
- `parent_id != id`.
- Parent must belong to same Subject. This cannot be fully enforced by a simple FK unless a composite FK strategy is used; service validation is required.
- No cycles. Enforce in service logic before updating `parent_id`.

### Uniqueness

Recommended:

```text
unique(subject_id, parent_id, lower(name))
```

Because SQL unique constraints treat `null` specially in some databases, root-level uniqueness may need a functional/partial unique index:

```text
unique(subject_id, lower(name)) where parent_id is null
unique(subject_id, parent_id, lower(name)) where parent_id is not null
```

This allows:

- `数学 / 高等数学 / 函数`
- `数学 / 线性代数 / 函数`

But prevents duplicate sibling names under the same parent.

### Indexes

- `(subject_id, parent_id, sort_order, id)` for tree listing.
- `(subject_id, status, sort_order, id)` for active lists.
- `(parent_id)` for child lookup.
- normalized sibling-name unique index as above.

### Tree Query Pattern

MVP options:

1. Fetch all nodes for a Subject ordered by `(parent_id, sort_order, id)` and assemble tree in service/client.
2. Fetch a subtree by `parent_id`.

Future PostgreSQL recursive CTE may be used for ancestry path, subtree move validation, and breadcrumb generation. No third-party tree library is needed for schema.

## Rejected Schema Alternatives

### Separate `chapters` Table

Rejected for this design round.

Reason:

- User scope explicitly names only Subject and Knowledge Point.
- `parent_id` tree can represent chapter-like nodes such as `高等数学`.
- A separate Chapter model would add a third domain and blur Batch 2 scope.

### Materialized Path Only

Rejected as primary model.

Reason:

- It complicates moves and renames.
- It duplicates hierarchy state.
- Adjacency list is easier to validate and sufficient for MVP.

Materialized path may be added later as a cache/projection if tree queries become expensive.

### Nested Set

Rejected.

Reason:

- Reordering and moving nodes is more complex.
- Personal learning tree mutation should be simple and safe.

## Migration Gate For Future Implementation

Before implementation:

- Inspect current database and existing migration history.
- Confirm whether prior `subjects` / `knowledge_points` artifacts are canonical, stale, or need migration reconciliation.
- This design and `tasks.md` are now approved, but migration must still follow the audit findings and approved scope.
- Do not drop existing tables or rewrite history without a separate migration recovery plan.
