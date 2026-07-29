# Schema Design

## Scope

This document designs schema only. It does not create migrations.

Designed:

- `questions`
- `question_knowledge_points`
- `question_sources`

Referenced:

- `subjects`
- `knowledge_points`

Audited later:

- existing `draft_items`
- existing `question_drafts`
- existing old `questions`
- existing old `question_sources`
- existing `knowledge_point_links`

## `questions`

### Purpose

Canonical private question entity.

### Proposed Fields

| Field | Type | Null | Default | Notes |
| --- | --- | ---: | --- | --- |
| `id` | uuid | no | generated | Primary key |
| `subject_id` | integer | no | none | FK to `subjects.id` |
| `title` | varchar(300) | yes | null | Optional display title |
| `stem_md` | text | no | none | Required question body |
| `question_type` | varchar(30) | no | none | Controlled enum |
| `options` | jsonb | no | `[]` | Option objects or strings |
| `answer_data` | jsonb | no | `{}` | Type-specific answer |
| `analysis_md` | text | yes | null | Explanation / solution |
| `difficulty` | varchar(20) | no | `unspecified` | Controlled enum |
| `status` | varchar(20) | no | `active` | `active` / `archived` |
| `visibility` | varchar(20) | no | `private` | Batch 3 fixed private |
| `version` | integer | no | `1` | Optimistic concurrency |
| `created_at` | timestamptz | no | now | Creation timestamp |
| `updated_at` | timestamptz | no | now | Update timestamp |

### Constraints

- `stem_md` must not be blank.
- `question_type in ('single_choice','multiple_choice','true_false','short_answer','essay')`.
- `difficulty in ('unspecified','easy','medium','hard')`.
- `status in ('active','archived')`.
- `visibility = 'private'`.
- `version > 0`.
- `options` must be an array.
- `answer_data` must be an object.

Some JSON shape checks should live in service/schema validation because SQL-only checks become brittle across question types.

### Indexes

- `(subject_id, status, updated_at)`
- `(question_type, status)`
- `(difficulty, status)`
- `(updated_at)`

### Deletion

Preferred lifecycle is archive, not hard delete.

Hard delete should remain blocked or admin-only after dependent domains exist.

## `question_knowledge_points`

### Purpose

Dedicated many-to-many relation between Question and Knowledge Point.

This design prefers a dedicated typed join table over the historical generic `knowledge_point_links` for the frozen Question contract.

### Proposed Fields

| Field | Type | Null | Default | Notes |
| --- | --- | ---: | --- | --- |
| `question_id` | uuid | no | none | FK to `questions.id` |
| `knowledge_point_id` | integer | no | none | FK to `knowledge_points.id` |
| `role` | varchar(20) | no | `primary` | `primary` / `secondary` / `prerequisite` |
| `sort_order` | integer | no | `0` | UI ordering |
| `created_at` | timestamptz | no | now | Creation timestamp |

### Constraints

- Primary key or unique: `(question_id, knowledge_point_id)`.
- `role in ('primary','secondary','prerequisite')`.
- Service must enforce same Subject:

```text
questions.subject_id == knowledge_points.subject_id
```

This cross-table constraint cannot be expressed cleanly by a simple FK without extra composite constraints.

### Indexes

- `(question_id, sort_order)`
- `(knowledge_point_id)`
- `(role)`

## `question_sources`

### Purpose

Record provenance for a Question.

### Proposed Fields

| Field | Type | Null | Default | Notes |
| --- | --- | ---: | --- | --- |
| `id` | uuid | no | generated | Primary key |
| `question_id` | uuid | no | none | FK to `questions.id` |
| `source_type` | varchar(30) | no | `manual` | Controlled enum |
| `source_title` | varchar(300) | yes | null | Human source name |
| `source_ref` | varchar(500) | yes | null | Book page, exam year, note id, etc. |
| `source_url` | text | yes | null | Optional URL |
| `source_note` | text | yes | null | Extra provenance note |
| `created_at` | timestamptz | no | now | Creation timestamp |

### Constraints

- `source_type in ('manual','book','exam','note','url','other')`.
- If `source_type = 'url'`, `source_url` should be present and validated by application logic.
- `question_id` FK uses cascade delete only if hard delete is later allowed; archive is preferred.

### Indexes

- `(question_id)`
- `(source_type)`

## Compatibility With Existing Tables

Current source may already include:

- `questions.question_text`
- `questions.correct_answer`
- `questions.explanation`
- `question_sources.source_name`
- `question_sources.source_ref`
- generic `knowledge_point_links(target_type, target_id)`

These are not automatically accepted as final.

Implementation must choose one of the following after audit:

1. Align existing tables in-place with a migration.
2. Add new fields while maintaining backward-compatible adapters temporarily.
3. Stop and request approval if migration would require destructive rewrite.

No silent drop, stamp, or history rewrite is allowed.

## P0-02 Transition Constraints

The active database contains three Question rows and related Draft, Source, and generic Knowledge Point link rows. The proposed schema is therefore a target contract, not permission to create a replacement table blindly.

Before migration implementation:

- confirm the physical primary-key types and existing foreign keys;
- define a reversible mapping for `question_text -> stem_md`, `correct_answer -> answer_data`, and `explanation -> analysis_md`;
- define how nullable legacy difficulty maps to `unspecified`;
- preserve the original legacy values when a structured conversion cannot be proven lossless;
- map only `knowledge_point_links.target_type = 'question'` into the dedicated relation after validating Subject ownership;
- keep `question_draft` links and Draft FKs untouched until their consumers are separately migrated;
- document whether the canonical relation is additive beside, or eventually replaces, the generic relation.

The P0-01 audit does not establish that the proposed UUID identifiers match the existing database. Identifier type must be reconciled before a migration is written.
