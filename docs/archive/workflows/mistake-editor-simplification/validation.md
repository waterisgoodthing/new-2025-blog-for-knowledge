# Validation: Mistake Editor Simplification

## Baseline

Not yet recorded for implementation. Initial planning observation was made with a dirty worktree containing unrelated changes; implementation must record a fresh baseline before source edits.

## Planned Checks

| Check | Purpose | Status |
| --- | --- | --- |
| `git status --short` | Preserve unrelated user changes | Pending |
| Mermaid root-cause inspection | Explain screenshot symptom before fixing | Pending |
| `npx tsc --noEmit` | TypeScript validation for frontend changes | Pending |
| Browser `/mistakes` | Verify simplified list and no Mermaid overlay | Pending |
| Browser `/write-mistake` | Verify create editor UI | Pending |
| Browser `/write-mistake/[slug]` | Verify edit editor UI and update behavior | Pending |

## Initial Evidence

- `src/app/write-mistake/page.tsx` currently renders `StagedMistakeForm`.
- `src/app/write-mistake/[slug]/page.tsx` currently renders `MistakeForm`.
- `src/app/mistakes/page.tsx` currently includes stats, review plan, weak-point diagnosis, filters, and list in one main stack.
- User screenshot from 2026-06-23 shows large `Syntax error in text mermaid version 11.15.0` text visible beside `/mistakes`.
