# Requirements

## Scope

Batch 3 builds the Question System foundation on top of Batch 2:

```text
Subject
  -> Knowledge Point Tree
  -> Question
  -> Future Mistake / Review
```

This batch covers formal Question design and implementation planning. It does not accept the earlier DraftItem / QuestionDraft model as the canonical Question model.

The P0-01 audit found that the old Question/Draft tables contain data and are referenced by Mistake, Capture, Attachment, and AI code. Therefore Batch 3 uses an additive transition boundary:

- Direct Question CRUD is the canonical Batch 3 path.
- Existing DraftItem / QuestionDraft records and conversion APIs remain readable compatibility infrastructure.
- Compatibility infrastructure is not expanded into a new Draft feature in Batch 3.
- No old table, column, relation, or downstream FK may be dropped or rewritten silently.

## Functional Requirements

### REQ-B3-Q-01 Question Entity

Question must represent a reusable private learning item.

It must be independent from:

- Note
- Mistake
- Review item
- Practice attempt
- AI draft
- OCR result

Question can later be referenced by Mistake and Review, but it must not store user attempt results or review scheduling state.

### REQ-B3-Q-02 Question Content

Question content must support:

- required stem / prompt
- optional title
- optional structured options for objective questions
- Markdown-friendly long text
- future display in manage detail pages

Question content must not depend on attachments, OCR, AI, or upload in this batch.

### REQ-B3-Q-03 Question Type

The first version must support a small controlled type set:

```text
single_choice
multiple_choice
true_false
short_answer
essay
```

More complex types such as fill-in-the-blank with multiple blanks, grouped reading-comprehension questions, programming tasks, and multi-part questions are deferred.

### REQ-B3-Q-04 Question-KnowledgePoint Relation

Questions must support many-to-many Knowledge Point relations.

Rules:

- A Question belongs to exactly one Subject.
- Linked Knowledge Points must belong to the same Subject.
- At least zero Knowledge Points are allowed during initial manual entry.
- Future validation may require at least one Knowledge Point before use in review or analytics.

### REQ-B3-Q-05 Question Source

Question Source records provenance.

MVP source types:

```text
manual
book
exam
note
url
other
```

AI, OCR, file import, and capture-router generated sources are deferred. They may later create source records, but they must not be part of the Batch 3 dependency path.

### REQ-B3-Q-06 Difficulty

Difficulty must be explicit and controlled:

```text
unspecified
easy
medium
hard
```

`unspecified` is preferred over null in API responses so filters and forms have a stable default.

### REQ-B3-Q-07 Answer

Answer must support type-specific structure without making the schema brittle.

Required design:

- objective questions store structured answer data.
- short answer and essay questions store text/rubric style answer data.
- answer validation belongs to service/schema logic, not UI-only checks.

Batch 3 does not grade user answers.

### REQ-B3-Q-08 Analysis

Analysis is human-readable explanation and solution notes.

Batch 3 must store analysis separately from answer so future Mistake and Review domains can use:

- correct answer
- why it is correct
- common traps
- solution method

AI-generated analysis is deferred.

### REQ-B3-Q-09 Admin Boundary

All Question APIs are private admin APIs.

Frontend AuthGate expresses access experience only. Backend admin authentication remains the real security boundary.

### REQ-B3-Q-10 Compatibility Boundary

Current old artifacts must be audited before implementation:

- `questions`
- `question_sources`
- `question_drafts`
- `draft_items`
- `knowledge_point_links`
- existing `/manage/questions` routes
- existing `/api/admin/questions` routes

No existing table, migration, route, or UI can be silently treated as correct without comparing it to this Batch 3 design.

### REQ-B3-Q-11 Transition Strategy

The first implementation must use an additive migration strategy because the current database is data-bearing and downstream services depend on the old contract.

Required transition behavior:

- Preserve existing Question, QuestionSource, QuestionDraft, DraftItem, and generic Knowledge Point link rows.
- Add or align canonical Question fields through forward migrations only after field-level reconciliation.
- Keep legacy fields readable until an explicit deprecation decision is approved.
- Introduce a dedicated Question-KnowledgePoint relation only with an audited mapping from existing `knowledge_point_links` rows.
- Preserve old Draft conversion behavior while the new direct Question API is introduced.
- Do not claim old rows are fully migrated until every field mapping and downstream read path is verified.

## Explicit Non-Goals

- New QuestionDraft workflow or redesign of the existing Draft workflow
- AI / OCR / upload integration
- Practice attempts
- Mistake system
- Review system
- Search and analytics
- public question bank
- multi-user ownership
- automatic migration from old Note or old Mistake data
- third-party mind map or question editor libraries

## Acceptance Baseline

Before implementation can be considered ready:

- Question schema is aligned with Batch 2 Subject / Knowledge Point tree.
- Question-KnowledgePoint relation prevents cross-subject links.
- Source, difficulty, answer, and analysis are first-class fields or contracts.
- API contract uses admin boundary only.
- Existing old implementation drift is documented and handled by migration strategy.
- The implementation plan explicitly separates canonical direct Question CRUD from legacy Draft compatibility.
