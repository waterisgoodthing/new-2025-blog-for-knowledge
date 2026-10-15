# Mistake Editor Simplification

## Goal

Unify the mistake creation and re-editing experience, simplify the current `/mistakes` page, and contain any Mermaid syntax-error marker so it does not appear as a large unrelated overlay beside the mistake list.

## Touched Domains

- `mistakes`: `/mistakes`, `/write-mistake`, `/write-mistake/[slug]`, mistake form components, weak-point diagnosis placement.
- `notes`: only if mistake detail routing or edit links require a small alignment.
- `shared infrastructure`: only if Mermaid fallback rendering needs a shared containment fix.

## Current Status

Planning drafted. Per `AGENTS.md`, implementation is blocked until the user explicitly approves `tasks.md`.

## Current Evidence

- `/write-mistake` uses `StagedMistakeForm`.
- `/write-mistake/[slug]` uses the older `MistakeForm`.
- `/mistakes` currently stacks stats, review planning, weak-point diagnosis, filters, sidebar, and cards, making the page feel noisy.
- The supplied screenshot shows a large `Syntax error in text mermaid version 11.15.0` marker leaking into the visible `/mistakes` page area.

## Workflow Files

| File | Purpose | Status |
| --- | --- | --- |
| `requirements.md` | User-facing requirements and acceptance criteria | Drafted |
| `design.md` | UX and implementation approach | Drafted |
| `tasks.md` | Implementation task list requiring approval | Drafted, awaiting approval |
| `validation.md` | Validation plan and evidence log | Drafted |
| `diff-report.md` | Expected implementation scope | Not started |
| `audit.md` | Root-cause notes if implementation finds deeper drift | Not started |
| `handoff-prompt.md` | External-agent prompt if needed | Not started |
| `assets/` | Screenshots and browser evidence | Optional |

## Approval Gate

Source implementation must not start until `tasks.md` is approved in the conversation.
