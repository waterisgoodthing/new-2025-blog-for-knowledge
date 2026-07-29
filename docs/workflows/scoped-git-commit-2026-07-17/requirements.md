# Requirements

## Must Have

- Capture the exact pre-operation branch and worktree state.
- Produce a path-level inclusion/exclusion report before staging.
- Preserve all pre-existing user changes outside the approved scope.
- Stage explicit paths only and verify the staged file list.
- Run proportional validation for the staged domains.
- Record commit hash, message, staged paths, validation, and remaining dirty paths.

## Approval Gate

Implementation of the commit task begins only after the user explicitly approves the task list or an identified phase in `tasks.md`.

## Safety Constraints

- No destructive Git commands.
- No migration execution.
- No production data modification.
- No push or deployment unless separately requested and approved.
