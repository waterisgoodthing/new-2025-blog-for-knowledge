# Batch 4 Mistake And Review

## Goal

Design and implement the smallest private learning loop after Batch 3:

```text
Question / QuestionDraft
  -> MistakeDraft
  -> human confirmation
  -> Mistake
  -> ReviewItem
  -> ReviewRecord
```

## Current Status

Status: P0-01 through P0-08 completed and accepted. Batch 4 is closed; Batch 5 has not started.

## Touched Domains

- private Mistake System
- private Review System
- Question compatibility boundary
- Manage Mistakes and Review routes
- backend admin APIs and existing persistence

## Hard Boundaries

- Public `Note(type="mistake")` remains readable through the existing public Note contract.
- The new private `mistakes` stack must not silently migrate or delete old Note mistakes.
- No Practice Session or Attempt implementation.
- No AI, OCR, Capture, upload, search, analytics, BKT, or complex capacity control.
- Review is limited to active Mistake targets and the frozen fixed-interval behavior.
- All writes remain backend-admin protected; AuthGate is only page-level access experience.

## Workflow Files

- [requirements.md](./requirements.md)
- [design.md](./design.md)
- [schema-design.md](./schema-design.md)
- [api-contract.md](./api-contract.md)
- [audit.md](./audit.md)
- [tasks.md](./tasks.md)
- [validation-plan.md](./validation-plan.md)
- [validation.md](./validation.md)
- [handoff-prompt.md](./handoff-prompt.md)

## Closure

The implementation and validation were accepted by the user. No Batch 5 work is authorized from this workflow.
