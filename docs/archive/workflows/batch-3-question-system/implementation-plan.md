# Implementation Plan

## Status

Not approved for implementation yet.

This plan was executed after [tasks.md](./tasks.md) was explicitly approved. Final evidence is recorded in [validation.md](./validation.md).

## Sequence

```text
Audit
  -> Requirements confirmation
  -> Backend tests
  -> Migration reconciliation
  -> Backend models/schemas/services/routes
  -> Frontend API client
  -> Manage pages
  -> Validation
```

## P0 Audit First

Before any migration or code change, implementation must inspect:

- active Alembic revision
- real database table columns
- old `012_add_question_drafts_and_questions.py`
- current `backend/app/models/question.py`
- current `backend/app/schemas/question.py`
- current `backend/app/services/question_service.py`
- current `backend/app/services/draft_service.py`
- imports from Mistake, Capture, Attachment, and AI services
- current `/manage/questions` UI and API client

Output should update [audit.md](./audit.md).

## Migration Strategy

Implementation must not assume the old `questions` table can be dropped or reused unchanged.

P0-02 decision: use an additive transition with compatibility preservation.

Allowed execution shape:

1. Reconcile the frozen contract against the existing data-bearing Question tables.
2. Add canonical fields/relations through forward migration or a documented compatibility adapter.
3. Preserve old rows, columns, generic links, and downstream FKs during the transition.
4. Stop for approval before any destructive or lossy operation.
5. Keep Draft compatibility reads/conversion intact while direct Question CRUD becomes canonical.

## Backend Design

Expected layering:

```text
router -> schema validation -> question service -> models -> response schema
```

Routers stay thin.

Service responsibilities:

- normalize text
- validate type-specific answer shape
- validate options by type
- validate same-subject Knowledge Point links
- handle optimistic version conflict
- archive instead of hard delete

## Frontend Design

Expected routes:

```text
/manage/questions
/manage/questions/[id]
```

Expected frontend client:

```text
src/lib/api/questions.ts
```

UI should use existing manage shell components and Batch 2 taxonomy client/selectors where possible.

No public page should be modified as part of Batch 3 unless validation proves a regression caused by this batch.

## Implementation Stop Conditions

Stop and request approval if:

- old Question tables contain data that need migration decisions.
- old Mistake/Capture/AI services require schema compatibility beyond Question scope.
- migration requires dropping columns or tables.
- implementation would introduce Draft, AI, OCR, Practice, Mistake, or Review work.

The current audit satisfied the first two stop-condition inputs. P0-02 was accepted, and P0-04 produced the additive migration reconciliation while preserving old data and downstream compatibility.
