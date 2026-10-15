# Validation Plan

## Database

- confirm current revision before and after any migration;
- preserve existing `mistake_drafts`, `mistakes`, `review_items`, `review_records`, and `notes` rows;
- verify no migration drops or rewrites public Note mistakes;
- verify unique DraftItem/Mistake and ReviewItem/Mistake relations.

Executed evidence is recorded in `validation.md`.

## Backend

- run targeted Mistake/Review tests;
- verify exactly-one Question/QuestionDraft source;
- verify draft version conflicts and idempotent conversion;
- verify unconfirmed/archived Mistakes do not enter active review queue;
- verify fixed interval mapping and stale review conflict;
- verify all admin route authentication.

## Frontend

- verify `/manage/mistakes`, `/manage/mistakes/[id]`, and `/manage/review` under AuthGate;
- verify loading, empty, error, pending, active, archived, paused, and stale-conflict states;
- verify public `/mistakes` does not request admin ReviewItem APIs when anonymous;
- run TypeScript, frontend tests, and production build if UI changes are approved.

## Boundary Checks

Confirm unchanged:

- public Note mistake reads;
- Question canonical content;
- no Practice, AI, OCR, Capture, upload, BKT, search, analytics, or multi-user work.
