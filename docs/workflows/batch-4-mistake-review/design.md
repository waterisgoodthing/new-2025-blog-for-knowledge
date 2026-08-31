# Design

## Domain Flow

```text
Question / QuestionDraft
        |
        v
MistakeDraft -- edit/reject/convert --> Mistake -- create --> ReviewItem
                                           |                       |
                                           +-- archive --> paused  |
                                                                   v
                                                              ReviewRecord
```

## Domain Boundaries

Question remains the canonical problem body. Mistake stores the learner-specific wrong outcome and reflection. Review stores scheduling and immutable review history. The public Note domain remains a compatibility read model for existing published mistakes.

## Lifecycles

MistakeDraft:

```text
pending -> needs_fix -> pending -> converted
pending -> rejected
```

Mistake:

```text
active <-> archived
```

ReviewItem:

```text
active <-> paused
```

Archiving a Mistake pauses its ReviewItem. Repeated archive is idempotent.

## Conversion Conflict Contract

```text
converted + valid existing target   -> 200 existing Mistake
converted + missing/different target -> 409
stale version                       -> 409
```

The normal duplicate request is not treated as an error. Only an inconsistent conversion binding is a conflict.

## Source Rules

- A MistakeDraft from a formal Question can convert directly.
- A MistakeDraft from a QuestionDraft can convert only after the QuestionDraft itself is converted.
- That conversion must resolve the converted Question's `question_id`; `question_draft_id` is never the formal Mistake's question reference.
- The source draft and snapshots remain retained after conversion for auditability.

## Review Algorithm

Batch 4 keeps the existing `fixed_interval_v1` algorithm explicit and replayable. The rating-to-interval mapping is part of the API/domain contract, not an AI decision. BKT and adaptive scheduling remain deferred.

## Public/Private Separation

```text
Public Note(type=mistake) -> public Note API -> /mistakes and /notes/[slug]

Private Question -> MistakeDraft -> Mistake -> ReviewItem -> admin APIs -> /manage/**
```

No route or migration may infer that these are already the same persistence object.
