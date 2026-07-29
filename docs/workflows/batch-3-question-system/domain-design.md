# Domain Design

## Domain Definition

Question is the canonical problem object used by the private learning system.

It stores:

- what the learner should solve
- the expected answer
- the explanation / analysis
- difficulty
- type
- source
- Subject
- related Knowledge Points

It does not store:

- a user's submitted answer
- whether the user got it wrong
- review interval
- AI generation state
- OCR result
- attachment metadata

## Question Boundary

Question belongs to Question System.

Question may be referenced by future domains:

- Mistake System
- Review System
- Practice System
- Search
- Analytics

Those future domains must not backfill their state into Question itself.

## Question Lifecycle

Recommended first lifecycle:

```text
active -> archived
```

Create and edit are admin-only operations.

Hard delete is deferred. Once Mistake or Review references exist, hard delete should be blocked or replaced with archive.

## Question Content

Question content has three layers:

| Layer | Purpose |
| --- | --- |
| `title` | optional short display title |
| `stem_md` | required prompt / question body |
| `options` | structured option list for objective types |

`stem_md` uses Markdown-compatible text. Batch 3 does not add attachment embedding, OCR fragments, or file uploads.

## Question Type

First supported types:

| Type | Meaning | Answer shape |
| --- | --- | --- |
| `single_choice` | exactly one option is correct | one option key |
| `multiple_choice` | one or more options are correct | option key array |
| `true_false` | boolean statement | true / false |
| `short_answer` | compact text answer | text or accepted variants |
| `essay` | long-form answer | rubric / sample answer |

Deferred:

- multi-part question sets
- fill-in-the-blank with positional blanks
- coding questions
- generated variants
- scoring rubrics with points

## Difficulty

Question difficulty is a controlled domain value:

```text
unspecified
easy
medium
hard
```

`unspecified` is allowed because a personal learning system often captures useful questions before difficulty is known.

## Answer

Answer is separate from analysis.

Recommended answer contract:

```json
{
  "kind": "single_choice",
  "value": ["A"]
}
```

For short answer:

```json
{
  "kind": "short_answer",
  "value": "极限不存在",
  "accepted": ["不存在", "无极限"]
}
```

For essay:

```json
{
  "kind": "essay",
  "sample": "参考答案 Markdown",
  "rubric": ["关键点 1", "关键点 2"]
}
```

Batch 3 validates the shape but does not grade attempts.

## Analysis

Analysis stores explanation and solution thinking:

- reasoning
- method
- key formula
- common trap
- why the answer is correct

Field name preference:

```text
analysis_md
```

This avoids overloading `answer` with explanation text.

## Question-KnowledgePoint Relation

Questions can link to multiple Knowledge Points.

Recommended relation roles:

```text
primary
secondary
prerequisite
```

MVP may default all manually selected links to `primary` if role UI is not implemented yet, but the schema should allow role so later analytics can distinguish the main tested concept from supporting concepts.

Validation rules:

- `question.subject_id` must exist.
- every linked `knowledge_point.subject_id` must equal `question.subject_id`.
- duplicate question / knowledge point links are rejected.
- archived Knowledge Points should not be selectable by default.

## Question Source

Question Source records provenance. It is not an import job.

First source types:

```text
manual
book
exam
note
url
other
```

Examples:

- manual: created by the learner.
- book: textbook or workbook reference.
- exam: source exam or paper name.
- note: derived from a private note.
- url: external page reference.
- other: freeform fallback.

AI/OCR/capture generated source types are intentionally deferred.

## Relationship To Old Draft Model

The older model placed Question behind `DraftItem + QuestionDraft -> convert -> Question`.

This Batch 3 design does not reject draft workflows forever. It only says the first frozen Question System should be understandable without making draft review the center of the model.

If future capture or AI creates untrusted material, a Draft domain can feed Question later.
