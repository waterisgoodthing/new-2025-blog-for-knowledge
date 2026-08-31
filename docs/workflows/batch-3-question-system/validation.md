# Batch 3 Validation

## Current Status

P0-01 through P0-07 completed for the approved Batch 3 scope.

The following implementation validation was executed:

- backend Question/Draft/route tests: `14 passed`;
- full backend regression: `234 passed, 2 warnings`;
- frontend tests: `5 files, 16 tests passed`;
- frontend typecheck: `npx tsc --noEmit --pretty false` passed;
- frontend production build: `npm run build` passed;
- Alembic current: `020 (head)`;
- migration upgrade from `019` to `020` completed;
- read-only row checks preserved `questions=3`, `question_drafts=3`, `draft_items=6`, `mistakes=3`;
- canonical relation contains `3` migrated Question links.

The full backend suite initially exposed a compatibility regression where legacy Draft conversion wrote `unspecified` into the MistakeDraft difficulty field. The compatibility path now preserves legacy `NULL`; the rerun passed.

## Evidence

- Active Alembic revision observed: `019 (head)`.
- Existing Question/Draft tables contain data.
- Existing downstream FKs/imports were recorded in [audit.md](./audit.md).
- P0-02 requirements and compatibility constraints are recorded in [requirements.md](./requirements.md), [design.md](./design.md), and [implementation-plan.md](./implementation-plan.md).

## Known Validation Gap

`alembic check` still reports four pre-existing Batch 2 taxonomy metadata differences:

- `idx_knowledge_points_subject_sort`;
- `uq_knowledge_points_child_name`;
- `uq_knowledge_points_root_name`;
- `uq_knowledge_points_sibling_name` model/index mismatch.

These differences are outside Batch 3 Question scope and were not changed here. The Question-specific source length drift was corrected.

The full backend suite also retains two pre-existing AsyncMock warnings in AI gateway tests; they do not fail the suite.

## Gate State

Migration Gate: `PASS` for the approved additive Question migration. Repository-wide Alembic metadata check remains `KNOWN GAP` because of the Batch 2 taxonomy drift above.

No automatic transition to Batch 4 is authorized.
