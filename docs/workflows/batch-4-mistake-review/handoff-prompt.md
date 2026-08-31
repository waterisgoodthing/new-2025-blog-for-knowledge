# Batch 4 Handoff

Batch 4 must begin from the current-state audit in [audit.md](./audit.md). The current private Mistake/Review stack is data-bearing and already has service/API behavior; implementation should harden and reconcile it rather than introduce a parallel stack.

The most important review question is the coexistence boundary:

```text
public Note(type=mistake) -> existing public Note/review compatibility
private Question -> MistakeDraft -> Mistake -> ReviewItem -> ReviewRecord
```

No public Note migration is included. No Practice or AI behavior may be added as a convenience.

## Implementation Handoff

Completed in this batch:

- inconsistent converted MistakeDraft targets now return the conflict contract;
- QuestionDraft conversion verifies the converted formal Question target;
- private Mistake and Review management pages are wired through typed admin clients;
- public Note mistake/review compatibility remains unchanged.

Validation: `236` backend tests passed with two pre-existing AI AsyncMock warnings; frontend tests, typecheck, and build passed. Database remains `020 (head)` with all audited Mistake/Review/Note row counts preserved.

Batch 4 acceptance is recorded. Do not begin Batch 5 attachments; the user explicitly requested that the work stop here.
