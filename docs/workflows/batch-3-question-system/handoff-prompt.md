# Batch 3 Handoff

## Completed Boundary

Batch 3 now provides a private admin Question System with:

- direct Question create, list, detail, PATCH, legacy PUT compatibility, and archive;
- structured question options and answer data;
- separate analysis and difficulty fields;
- source provenance metadata;
- dedicated Question-Knowledge Point relations with same-Subject validation;
- preserved DraftItem / QuestionDraft conversion compatibility;
- `/manage/questions` and `/manage/questions/[id]` management surfaces.

## Batch 4 Entry Requirements

Future Mistake or Review work must consume Question IDs and must not recreate question content fields as a second canonical model.

Before entering Batch 4, review:

- whether `knowledge_point_links` can be deprecated after all downstream consumers are migrated;
- whether legacy `question_text`, `correct_answer`, and `explanation` can be retired;
- how Mistake records reference Question without changing the current Note-based public mistake boundary;
- how Review adds attempts and scheduling outside the Question entity.

## Known Risk

`alembic check` still reports Batch 2 taxonomy index/model drift. This is recorded in [validation.md](./validation.md) and is not silently folded into Batch 3.

## Stop Rule

Do not add AI, OCR, upload, capture, practice, or Review behavior to the Batch 3 implementation after this handoff.
