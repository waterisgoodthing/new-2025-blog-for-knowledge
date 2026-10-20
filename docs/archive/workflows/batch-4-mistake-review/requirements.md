# Requirements

## Scope

Batch 4 implements the private Mistake and simple Review loop on top of the canonical Batch 3 Question System.

## Functional Requirements

### REQ-B4-M-01 Mistake Draft

MistakeDraft is an unconfirmed candidate and must reference exactly one source:

- a formal `Question`; or
- a `QuestionDraft` that has not yet converted.

It must preserve source snapshots for question text, correct answer, and explanation so the draft remains reviewable if the source changes.

### REQ-B4-M-02 Human Confirmation

Only an administrator can edit, reject, or convert a MistakeDraft. Conversion must be version-checked and idempotent.

An unconfirmed draft must not create a formal Mistake or ReviewItem.

Repeated conversion of the same successfully converted DraftItem is idempotent: return the existing Mistake with `200`. If the DraftItem points to a missing or different result, return `409`.

### REQ-B4-M-03 Formal Mistake

Mistake is a private record of a learner's wrong outcome and reflection around a Question.

It must keep or reference:

- `question_id`
- subject
- question snapshot
- learner answer
- correct answer
- analysis
- reason category
- mistake reason
- difficulty
- Knowledge Point links
- active/archived status

Mistake must not own Question content as a second canonical question model.

### REQ-B4-M-04 Review Item

Only an active formal Mistake can create a ReviewItem in the MVP. ReviewItem must be unique per Mistake and support active/paused state. An archived Mistake cannot create a new ReviewItem.

ReviewItem stores scheduling state outside Mistake.

### REQ-B4-M-05 Review Submission

Review submission must atomically:

1. append an immutable ReviewRecord;
2. calculate the next fixed interval;
3. update `ReviewItem.next_review_at`.

The MVP rating mapping is `0/1/2 -> 1 day`, `3 -> 3 days`, `4 -> 7 days`, `5 -> 14 days`.

### REQ-B4-M-06 Compatibility

The new private Mistake/Review stack and the old public `Note(type="mistake")` stack coexist during migration. No automatic Note migration is part of Batch 4.

### REQ-B4-M-07 Security

All `/api/admin/mistake-drafts`, `/api/admin/mistakes`, and `/api/admin/review/items` endpoints require backend admin authentication. `/mistakes` remains a public Note-backed route and must not call private admin APIs anonymously.

## Explicit Non-Goals

- Practice Session, Attempt, scoring, or automatic wrong-answer detection.
- AI, OCR, Capture, attachments, uploads, or document import.
- BKT, mastery events, adaptive scheduling, or complex capacity control.
- Public exposure of private Mistake or Review records.
- Silent migration from Note-backed mistakes.
- Multi-user ownership or collaboration.

## Acceptance Baseline

- Draft confirmation is the only path from candidate to formal Mistake.
- Formal Mistake references Batch 3 Question IDs.
- Review cannot be created for an unconfirmed or archived Mistake.
- Stale versions and duplicate conversion are handled deterministically.
- Public Note mistakes remain unchanged.
