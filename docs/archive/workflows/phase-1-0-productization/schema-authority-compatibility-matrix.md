# Schema Authority Compatibility Matrix — SA-A

## Status

Decision: **SA-A approved on 2026-07-19**.  The current `knowledge_points` database contract is authoritative. This document records the decision and read-only preflight only; it does not authorize source changes, migration, DDL or data writes.

## Final contract

| Object | Current physical definition | SA-A meaning | Required metadata representation |
|---|---|---|---|
| `idx_knowledge_points_parent` | btree `(parent_id)` | Parent-to-children lookup remains supported | non-unique `Index` |
| `idx_knowledge_points_subject_parent_sort` | btree `(subject_id, parent_id, sort_order, id)` | Stable ordered tree listing remains supported | non-unique `Index` |
| `idx_knowledge_points_subject_sort` | btree `(subject_id, sort_order, id)` | Stable subject-wide listing remains supported | non-unique `Index` |
| `uq_knowledge_points_root_name` | unique `(subject_id, lower(name))` where `parent_id IS NULL` | Root names are case-insensitively unique per subject | unique expression `Index` with root partial predicate |
| `uq_knowledge_points_child_name` | unique `(subject_id, parent_id, lower(name))` where `parent_id IS NOT NULL` | Child names are case-insensitively unique per subject and parent | unique expression `Index` with child partial predicate |

The primary key, parent and subject foreign keys, `status` check and self-parent check are unchanged and are not the RISK-P10-008 drift set.

## Why the current ORM contract is incompatible

The current model has `UniqueConstraint(subject_id, parent_id, name, name="uq_knowledge_points_sibling_name")`. It differs from SA-A in two material ways:

1. It compares `name` case-sensitively rather than `lower(name)`.
2. It uses one nullable unique constraint. PostgreSQL considers `NULL` values distinct for ordinary unique constraints, so it cannot enforce root-name uniqueness when `parent_id` is `NULL`.

It also omits `idx_knowledge_points_subject_sort`. Aligning the ORM metadata must preserve all three query indexes and replace the incompatible constraint with the two partial expression indexes. This work is assigned to SA-P0-02 and is not authorized by this document.

## Data compatibility preflight

Read-only checks on 2026-07-19 reported:

| Check | Result |
|---|---:|
| Root duplicate groups under SA-A normalized key | 0 |
| Child duplicate groups under SA-A normalized key | 0 |
| Knowledge-point rows | 3 |

This proves only that current rows do not violate the selected uniqueness keys. It does not prove route behavior, write validation, migration safety or final Alembic closure.

## Approval boundary and acceptance

SA-P0-02 requires explicit approval before adding tests or changing model metadata. Its acceptance requires targeted tests, `alembic current`, `alembic heads`, `alembic check`, preserved permissions/API behavior, and documented counts. No migration/DDL is authorized unless a later task explicitly requests it.
