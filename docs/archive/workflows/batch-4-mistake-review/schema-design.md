# Schema Design

This document is a target and reconciliation design. It does not authorize a migration by itself.

## `mistake_drafts`

Existing target shape is retained with these constraints:

- UUID `id` and unique `draft_item_id`;
- exactly one of `question_id` and `question_draft_id`;
- required `subject_id` and `question_text` snapshot;
- optional `my_answer`, `correct_answer_snapshot`, `explanation_snapshot`;
- controlled `reason_category`;
- nullable legacy difficulty;
- source and version state supplied by `draft_items`.

Required indexes: subject and draft-item lookup. FKs must remain restrictive for Question sources and cascading only for the unified DraftItem ownership boundary.

## `mistakes`

Existing target shape is retained:

- UUID `id`;
- unique `source_draft_item_id`;
- restrictive FK `question_id -> questions.id`;
- restrictive FK `subject_id -> subjects.id`;
- question/answer/analysis snapshots as first-class fields;
- `reason_category`, optional `mistake_reason`, optional difficulty;
- `status` active/archived;
- `visibility` private;
- positive optimistic `version`.

Formal Mistake must not add a second structured Question content model. Batch 4 may add only fields required by the frozen requirements after audit proves they are missing.

## `review_items`

Existing MVP target shape:

- UUID `id`;
- `target_type = mistake`;
- string `target_id` with unique `(target_type, target_id)`;
- `state` active/paused;
- `algorithm = fixed_interval_v1`;
- non-negative interval/repetition counters;
- `next_review_at` and optional `last_reviewed_at`.

## `review_records`

ReviewRecord is append-only and stores rating, reviewed time, previous/next interval, and previous/next due timestamps. Deleting a ReviewItem is restricted by its records.

## Knowledge Point Relations

Current architecture uses generic `knowledge_point_links` for Mistake and MistakeDraft. Batch 4 must audit this usage and preserve it. It must not duplicate the Batch 3 Question-specific relation or change cross-domain target semantics without a separate decision.

## Compatibility Constraint

No table is dropped or automatically merged with `notes`. Any migration from public Note mistakes requires a separate, explicit data mapping and rollback plan.
