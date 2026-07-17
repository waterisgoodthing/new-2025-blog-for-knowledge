# Design

## Design Summary

Batch 3 creates a clean Question System foundation after Batch 2 replaced the old chapter-style taxonomy with a Subject -> Knowledge Point tree.

The design preference is:

```text
subjects
  -> knowledge_points
  -> questions
  -> question_knowledge_points
  -> question_sources
```

This deliberately separates the new frozen design from the older historical model that routed Question creation through `draft_items` and `question_drafts`.

## Route Shape

Admin routes:

```text
/manage/questions
/manage/questions/[id]
```

No public Question route is introduced in Batch 3.

## API Shape

Admin API prefix:

```text
/api/admin/questions
```

Question Source can be embedded in Question create/update contracts for MVP, while still being stored as a separate persistence concern.

## Data Shape

Core tables to design:

- `questions`
- `question_knowledge_points`
- `question_sources`

Existing Batch 2 tables:

- `subjects`
- `knowledge_points`

Historical tables to audit, not blindly reuse:

- `draft_items`
- `question_drafts`
- old `questions`
- old `question_sources`
- generic `knowledge_point_links`

## Primary Design Decision

Question is a formal reusable learning object, not a draft, not an attempt, and not a mistake.

This decision keeps Batch 3 narrow and makes later Batch 4 clearer:

```text
Question = reusable problem body and canonical answer/analysis
Mistake = user's wrong outcome and reflection around a Question or imported prompt
Review = scheduling and review history for learning targets
```

## P0-02 Compatibility Decision

Batch 3 will implement direct Question CRUD as the primary contract. The existing DraftItem / QuestionDraft pipeline remains a compatibility path for existing data and downstream callers, but it is not the center of the new domain design and receives no new feature scope in this batch.

The transition is additive:

```text
legacy Draft -> existing Question rows
                          \
                           compatibility adapter / audited mapping
                            \
                             canonical Question contract
```

The exact physical migration remains a P0-04 task. It must preserve data and downstream foreign keys, and it must stop for approval if field mapping becomes lossy or requires destructive changes.

## Drift Handling

The existing repository may already contain Question-related code from an earlier MVP path. Batch 3 implementation must begin with a real schema/code audit and a migration reconciliation plan.

The implementation should not rename, drop, or rewrite existing tables until that audit determines:

- which tables exist in the active database
- which migrations have been applied
- which frontend routes depend on old contracts
- which downstream services import old types

## Implementation Posture

Implementation must follow:

```text
Requirements
  -> Domain Design
  -> Schema
  -> API Contract
  -> Implementation
  -> Validation
```

The current document package stops before implementation. See [tasks.md](./tasks.md) for the approval gate.
