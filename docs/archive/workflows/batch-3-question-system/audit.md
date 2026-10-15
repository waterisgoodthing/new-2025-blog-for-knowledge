# Audit

## Status

P0-01 read-only audit completed.

This audit did not modify code, database, migrations, or frontend routes.

## Batch 2 Baseline

Batch 2 validation recorded:

- `subjects` exists.
- `knowledge_points` exists.
- `knowledge_points.parent_id` provides the frozen tree model.
- `knowledge_point_links` still exists and was preserved.
- no active `chapters` model/API/table after Batch 2 migration.

Question System must align to `Subject -> Knowledge Point Tree`.

## Read-Only Commands

Executed read-only checks:

```text
git status --short
sed -n '1,260p' backend/alembic/versions/012_add_question_drafts_and_questions.py
sed -n '1,260p' backend/app/models/question.py
sed -n '1,260p' backend/app/schemas/question.py
sed -n '1,260p' backend/app/services/question_service.py
sed -n '1,380p' backend/app/services/draft_service.py
rg -n "Question|QuestionDraft|DraftItem|question_draft|questions|question_sources|knowledge_point_links" ...
cd backend && PYTHONPATH=. .venv/bin/alembic current
cd backend && PYTHONPATH=. .venv/bin/python - <<'PY'
SQLAlchemy inspector for table columns, constraints, indexes, FKs, and row counts.
PY
```

No migration command was run.

No write SQL was executed.

## Existing Question Artifacts Found

Source search found existing Question/Draft artifacts:

- `backend/alembic/versions/012_add_question_drafts_and_questions.py`
- `backend/app/models/question.py`
- `backend/app/schemas/question.py`
- `backend/app/services/question_service.py`
- `backend/app/services/draft_service.py`
- `backend/app/routers/questions.py`
- `backend/app/routers/drafts.py`
- `src/lib/api/questions.ts`
- `src/lib/api/drafts.ts`
- `/manage/questions` UI files
- `/manage/drafts` UI files

Related downstream imports exist in:

- Capture services
- Mistake services
- Attachment services
- AI schemas/services

## Active Database State

Alembic current:

```text
019 (head)
```

Real table state:

| Table | Exists | Rows | Classification |
| --- | ---: | ---: | --- |
| `draft_items` | yes | 6 | data-bearing old Draft system |
| `question_drafts` | yes | 3 | data-bearing old QuestionDraft system |
| `questions` | yes | 3 | data-bearing old Question system |
| `question_sources` | yes | 3 | data-bearing old source system |
| `knowledge_point_links` | yes | 6 | data-bearing generic relation table |
| `mistake_drafts` | yes | 3 | downstream dependency |
| `mistakes` | yes | 3 | downstream dependency |
| `capture_items` | yes | 0 | code dependency, no current rows |
| `attachments` | yes | 1 | attachment system present |
| `attachment_links` | yes | 1 | downstream target-type dependency |

Distribution:

```text
draft_items:
  mistake / question / converted / mistake = 3
  question / manual / converted / question = 3

questions:
  short_answer / archived / medium = 3

question_sources:
  manual = 3

knowledge_point_links:
  question = 3
  question_draft = 3

mistake_drafts:
  source question = 3

mistakes:
  active = 3

attachment_links:
  mistake / answer = 1

capture_items:
  rows = 0
```

Conclusion:

```text
Existing Question/Draft tables are data-bearing.
```

They are not absent and not empty-compatible.

## Migration 012 Findings

`backend/alembic/versions/012_add_question_drafts_and_questions.py` creates the old draft-first design:

```text
draft_items
question_drafts
questions
question_sources
```

Important 012 characteristics:

- `draft_items.draft_type = 'question'`
- `draft_items.source_type = 'manual'`
- `question_drafts` and `questions` use `question_text`
- answer is `correct_answer`
- analysis is `explanation`
- `difficulty` is nullable and limited to `easy | medium | hard`
- `question_sources.source_type = 'manual'`
- source ref is mandatory and unique by `(source_type, source_ref)`
- no `question_knowledge_points` table exists
- Knowledge Point links use generic `knowledge_point_links(target_type, target_id)`

This does not match the new Batch 3 design preference:

```text
stem_md
answer_data
analysis_md
difficulty = unspecified | easy | medium | hard
question_knowledge_points
source_type = manual | book | exam | note | url | other
```

## Current Model Findings

`backend/app/models/question.py` no longer matches the original 012 exactly.

Current model has already been expanded by later migrations:

- `DraftItem.draft_type IN ('question', 'mistake')`
- `DraftItem.source_type` allows `question` and `question_draft` for mistake drafts
- converted targets support both `question` and `mistake`

This expansion comes from migration 013 and means `draft_items` is now shared infrastructure between Question and Mistake.

Current Question model still uses old field names:

```text
question_text
correct_answer
explanation
difficulty nullable
```

Current model does not include:

```text
stem_md
answer_data
analysis_md
question_knowledge_points
```

## Current Schema Findings

`backend/app/schemas/question.py` mirrors the old QuestionDraft-first contract:

- create payload is `QuestionDraftCreate`, not direct `QuestionCreate`
- update payload reuses draft validation by merging into `QuestionDraftCreate`
- `Difficulty = Literal["easy", "medium", "hard"]`
- no `unspecified`
- no structured `answer_data`
- no source create/update contract beyond output

Implication:

```text
Direct Question CRUD is not currently a first-class contract.
```

## Current Service Findings

`backend/app/services/draft_service.py` owns creation and conversion:

```text
create_question_draft
update_question_draft
convert_question_draft
reject_question_draft
```

`convert_question_draft` creates:

- `Question`
- `QuestionSource(source_type='manual')`
- `KnowledgePointLink(target_type='question')`

`backend/app/services/question_service.py` supports:

- list Question
- get Question
- update Question
- archive Question

But it validates Question updates by reusing `QuestionDraftCreate`, so the runtime contract remains tied to the old draft schema.

## Mistake Dependency Findings

Mistake is a strong downstream dependency.

`backend/app/models/mistake.py` has FKs:

- `mistake_drafts.question_id -> questions.id`
- `mistake_drafts.question_draft_id -> question_drafts.id`
- `mistakes.question_id -> questions.id`
- `mistakes.source_draft_item_id -> draft_items.id`

`backend/app/services/mistake_service.py` imports and uses:

- `DraftItem`
- `Question`
- `QuestionDraft`

It can create a MistakeDraft from either a formal Question or a QuestionDraft, and conversion may require a QuestionDraft to have already converted to Question.

Implication:

```text
Question schema alignment cannot ignore Mistake dependencies.
```

## Capture Dependency Findings

Capture has code dependency but no current rows.

`capture_items` exists with zero rows.

`backend/app/services/capture_service.py` imports:

- `QuestionDraftCreate`
- `create_question_draft`

The capture conversion path creates a QuestionDraft and then a MistakeDraft from that QuestionDraft.

Implication:

```text
Capture compatibility can likely be changed with lower data risk, but it is still a code dependency.
```

## Attachment Dependency Findings

Attachment target types include:

```text
question_draft
question
mistake
```

Current `attachment_links` row distribution:

```text
mistake / answer = 1
```

No current attachment rows point to Question or QuestionDraft, but the model and schema allow those target types.

## AI Dependency Findings

AI code depends on QuestionDraft-shaped schemas:

- `QuestionDraftRequest`
- `QuestionDraftResponse`
- `QuestionDraftConfirmRequest`
- `QuestionDraftConfirmResponse`
- `/api/ai/mistake/question-draft`
- `/api/ai/mistake/question-draft/confirm`

Diagram and validator services also refer to question draft structures.

Implication:

```text
AI must remain out of Batch 3 implementation unless a compatibility shim is kept.
```

## Question-KnowledgePoint Relation Findings

Current implementation uses:

```text
knowledge_point_links(target_type, target_id)
```

Current row distribution:

```text
question = 3
question_draft = 3
```

Classification:

```text
Existing generic links are migration input and compatibility data.
```

They should not be treated as the final frozen Question relation without an explicit decision.

Batch 3 design preference remains a dedicated relation:

```text
question_knowledge_points
```

But moving from generic links to the dedicated table would require a data-preserving migration or a compatibility layer.

## Drift Risks

### RISK-B3-001 Old taxonomy coupling

The old implementation used historical taxonomy assumptions and generic `knowledge_point_links`.

Batch 3 must re-check every relation against the Batch 2 frozen model:

```text
subjects
knowledge_points(parent_id)
```

### RISK-B3-002 Draft-first old workflow

Historical Batch 3 centered on:

```text
DraftItem -> QuestionDraft -> convert -> Question
```

The current Batch 3 request centers on Question System design fields, not draft review.

Draft workflow should not become a hidden dependency unless approved again.

### RISK-B3-003 Existing DB may already contain old tables

If old tables exist and contain data, implementation cannot safely replace them without a migration decision.

The first implementation task must inspect real DB schema and row counts.

### RISK-B3-004 Downstream imports may break if schema is renamed

Mistake/Capture/Attachment/AI modules currently import Question or QuestionDraft types.

Any schema alignment may need compatibility shims, or it may need a separate approval if it touches other domains.

### RISK-B3-005 Data-bearing old system blocks simple replacement

The active database contains existing Question, QuestionDraft, Source, Mistake, and KnowledgePointLink rows.

Replacing the old model without data migration would lose or orphan private learning data.

### RISK-B3-006 012 no longer describes current runtime alone

Migration 012 is not the whole current truth because 013 expanded `draft_items` for Mistake.

Any migration strategy must consider the 012 -> 013 -> 019 chain, not only 012.

### RISK-B3-007 Direct Question CRUD conflicts with old draft-first API

Current API has update/archive for formal Questions, but creation is routed through QuestionDraft conversion.

The new Batch 3 design must explicitly choose between:

- direct Question creation as the primary MVP path
- preserving draft-first creation for compatibility
- supporting both with clear domain boundaries

## Compatibility Needs

Batch 3 must preserve:

- Batch 2 Subject and Knowledge Point APIs.
- public content routes.
- existing Mistake/Review/AI behavior outside the approved scope.
- worktree changes not made by this batch.

Batch 3 implementation must not:

- drop `questions`, `question_drafts`, `draft_items`, or `question_sources`
- drop `knowledge_point_links`
- remove `QuestionDraft` while Mistake/Capture/AI still import it
- migrate existing rows without a reviewed data mapping
- treat `question_text/correct_answer/explanation` as equivalent to `stem_md/answer_data/analysis_md` without explicit mapping rules

## Implementation Strategy Recommendation

Recommended classification:

```text
data-bearing old Question/Draft system with downstream FK dependencies
```

Completed next gate:

```text
P0-02 Finalize Requirements Gate
```

P0-02 decision is:

1. Use direct Question CRUD as the canonical Batch 3 contract.
2. Use additive fields/relations or compatibility adapters while preserving old fields during transition.
3. Keep the old Draft workflow temporarily for compatibility and normalize only the new Question relation/source/answer contracts.
4. Do not expand Batch 3 into Draft, Mistake, Capture, Attachment, or AI work.

Safe default for implementation planning:

- prefer additive migration over destructive rewrite
- keep old rows readable
- preserve existing FKs
- create a data mapping plan for `question_text -> stem_md`, `correct_answer -> answer_data`, and `explanation -> analysis_md`
- migrate `knowledge_point_links(target_type='question')` into `question_knowledge_points` only with a reversible, audited migration
- leave QuestionDraft compatibility in place unless a separate Draft deprecation task is approved

## P0-01 Conclusion

P0-01 is complete.

The current system is not blank and not safe for direct replacement.

P0-02 was completed as a documentation-only requirements gate, then explicitly approved before implementation. P0-04 produced the reviewed additive migration reconciliation.
