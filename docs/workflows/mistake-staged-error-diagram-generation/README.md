# Mistake Staged Error Diagram Generation

## Goal

Redesign the mistake recording workflow so image-heavy mistake creation becomes a staged, user-approved process:

1. AI extracts and structures the question from image/text.
2. The learner writes their real error reason.
3. AI proposes an interpretation of that error reason.
4. The learner accepts or rejects that interpretation.
5. Only after acceptance, AI generates final analysis and a teaching diagram.

The diagram path must prefer deterministic chart rendering such as SVG, Mermaid, or canvas. Qwen image generation is only a fallback for cases that cannot be represented accurately as structured diagrams.

## Touched Domains

- `mistakes`: `/write-mistake` staged creation workflow and saved mistake content.
- `notes`: mistake detail rendering for accepted error interpretation, analysis, and generated diagrams.
- `manage`: AI configuration/prompt visibility if model settings need surfacing.
- `backend`: staged AI endpoints, prompt contracts, diagram strategy, Qwen image fallback.
- `shared infrastructure`: typed API clients, diagram rendering, generated asset handling.

## Current Status

Planning only. Implementation must not start until `tasks.md` is explicitly approved in conversation.

## Workflow Files

- [requirements.md](./requirements.md)
- [design.md](./design.md)
- [tasks.md](./tasks.md)
- [audit.md](./audit.md)
- [validation.md](./validation.md)
- [handoff-prompt.md](./handoff-prompt.md)

## Approval Gate

Source implementation is blocked until the user approves `tasks.md`.
