# Validation

# Validation

## C1 Staging Validation

- Explicit staging completed for the approved A–H baseline scope.
- Cached paths: 256 total — 190 added, 65 modified, 1 deleted.
- Unstaged paths: 0.
- Untracked paths: 0.
- `git diff --cached --check`: FAIL due to whitespace already present in approved documentation files, plus one trailing-space line in `backend/alembic/versions/020_add_canonical_question_contract.py` and blank-line-at-EOF findings in several newly added docs.
- `npx tsc --noEmit --pretty false`: PASS.
- `PYTHONPATH=. .venv/bin/pytest -q`: PASS — 244 passed, 2 existing RuntimeWarnings.
- Targeted backend tests: PASS — 37 passed in 1.28s.
- `npm test -- --run`: PASS — 8 test files, 26 tests.
- `PYTHONPATH=. .venv/bin/alembic check`: FAIL — detected knowledge-point index removals and a unique-constraint addition as new upgrade operations. No migration was executed.
- No migration, database write, push, or deployment executed.
