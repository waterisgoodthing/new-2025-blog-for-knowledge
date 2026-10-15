# Requirements

## Background

The Personal Learning System needs a stable knowledge organization base before Question, Mistake, and Review workflows can attach to it. Batch 1 created only the management shell and static route containers. Batch 2 freezes the domain design for Subject and Knowledge Point only.

## Users

- Personal administrator: creates and maintains private learning organization.
- Future Question/Mistake/Review workflows: reference stable Subject and Knowledge Point IDs after their own batches are approved.
- Public visitors: unaffected; they do not access private taxonomy management.

## Functional Requirements

### REQ-B2-01 Subject Domain Definition

Subject must be defined as the top-level private learning namespace.

It must support these real-world uses without splitting the model:

- school discipline, such as Mathematics
- course, such as Advanced Mathematics
- exam subject, such as GRE Quant
- self-study track, such as Algorithms

Acceptance:

- The decision and rationale are recorded.
- Subject is not overloaded with Question, Mistake, Review, or Analytics state.

### REQ-B2-02 Subject Lifecycle And Status

Subject must support a lifecycle suitable for personal learning management:

```text
active -> archived
```

Draft Subject is not required in Batch 2 because a Subject has no high-risk generated content. Delete, if later implemented, must be guarded by dependency checks.

Acceptance:

- Status meaning is documented.
- Hard delete is not assumed as the default lifecycle.

### REQ-B2-03 Knowledge Point Tree

Knowledge Point must support:

- unlimited hierarchy
- parent-child relation
- root nodes per Subject
- sibling ordering
- detail pages
- future mind-map rendering

Acceptance:

- Tree model uses `knowledge_points.parent_id`.
- Cycle prevention is required in future service logic.
- Ordering is deterministic.

### REQ-B2-04 Subject To Knowledge Point Relation

Every Knowledge Point belongs to exactly one Subject.

Each Knowledge Point may have zero or one parent Knowledge Point. If `parent_id` is set, the parent must belong to the same Subject.

Acceptance:

- Cross-subject parent-child relations are forbidden.
- Moving a subtree to another Subject requires explicit validation.

### REQ-B2-05 Schema Design Only

Design future tables:

- `subjects`
- `knowledge_points`

Acceptance:

- Fields, types, constraints, indexes, uniqueness, and FK relationships are documented.
- No migration file is created.
- No database command is executed.

### REQ-B2-06 Route Design Only

Design future route responsibilities:

- `/manage/subjects`
- `/manage/subjects/[id]`
- `/manage/knowledge-points`
- `/manage/knowledge-points/[id]`

Acceptance:

- Page responsibilities and data sources are documented.
- Batch 1 shell compatibility is preserved.
- No frontend page logic is changed.

### REQ-B2-07 API Contract Only

Define future admin API contracts for:

- Subject list/detail
- Knowledge tree
- Knowledge point detail

Acceptance:

- Request, response, errors, and permission boundaries are documented.
- No backend router, schema, service, or client is implemented.

## Non-Functional Requirements

- Security: all future management APIs require backend admin authentication.
- Compatibility: public routes remain unchanged.
- Traceability: decisions must state rationale and alternatives.
- Maintainability: future implementation must preserve thin router and service-owned domain logic.
- Accessibility: future pages must retain Batch 1 shell accessibility expectations.
- Performance: tree queries must avoid unbounded heavy payloads by default.

## Explicit Non-Goals

- No Question design beyond future references.
- No Mistake design.
- No Review design.
- No Attachment, Upload, OCR, AI, Search, or Analytics design.
- No CRUD implementation.
- No migration.
- No third-party tree or mind-map library.
