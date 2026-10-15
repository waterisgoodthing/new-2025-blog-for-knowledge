# Design

## Commit Flow

1. Read-only inventory of branch, worktree, staged state, and changed paths.
2. Classify every candidate path as included, excluded, or needs user confirmation.
3. Obtain explicit approval for the exact `tasks.md` scope.
4. Stage only approved explicit paths.
5. Inspect cached names, diff, whitespace, and relevant validation results.
6. Create one or more commits only when the approved boundary is satisfied.
7. Record commit evidence and residual dirty paths without touching excluded work.

## Boundary Rules

- A file is not included merely because it is modified or adjacent to an included feature.
- Existing commits and remote divergence are preserved.
- Deletions and new migrations require explicit inclusion in the approved scope.
- Documentation-only changes stay separate from runtime changes unless the approval explicitly groups them.
- Push is a separate operation and is not implied by commit approval.
