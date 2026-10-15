# Requirements: Mistake Editor Simplification

## Scope

This task affects the `mistakes` domain and possibly shared Mermaid rendering. It must not refactor unrelated blog, music, manage, auth, or backend AI provider code.

## Users

| User | Need |
| --- | --- |
| Personal learner/admin | Add a mistake quickly, edit it later without switching mental models, and review the mistake list without noisy duplicate panels. |
| Public reader | View `/mistakes` without leaked Mermaid parser artifacts or confusing internal UI noise. |

## Functional Requirements

- **REQ-01** New mistake creation and existing mistake editing must share one product model and one visual language.
- **REQ-02** Editing an existing staged mistake must preserve important metadata: question draft, user error reason, AI interpretation, final analysis, diagram metadata, images, tags, subject, difficulty, and review fields.
- **REQ-03** Re-editing should not force the user back through AI stages unless they choose to regenerate or revise those sections.
- **REQ-04** The new mistake editor must be visually calmer and more useful: fewer stacked cards, clearer primary action, better field grouping, and denser operational layout.
- **REQ-05** `/mistakes` must be less verbose by default. It should prioritize due review, search/filter, and the mistake list; secondary diagnosis and summary details should be collapsible or drawer-based.
- **REQ-06** The Mermaid syntax-error marker shown in the screenshot must not leak into the `/mistakes` page as a large visual artifact.
- **REQ-07** Any icon-only action added or changed must have an accessible name.
- **REQ-08** Existing public read access for mistakes must remain intact.

## Non-Goals

- Do not replace the backend AI analysis architecture.
- Do not introduce a new domain type.
- Do not change the `Note` model or create a database migration unless implementation discovers a true contract gap.
- Do not redesign unrelated `/notes`, `/blog`, `/manage`, or music pages.

## Acceptance Criteria

- **AC-01** `/write-mistake` and `/write-mistake/[slug]` use the same editor shell/components, with mode-specific behavior only where necessary.
- **AC-02** Editing a saved mistake loads the same fields shown by create flow and saves via `updateNote` without creating a duplicate note.
- **AC-03** Staged AI metadata remains visible and editable/regenerable in an understandable way.
- **AC-04** `/mistakes` first viewport is quieter: no duplicate review CTA stack, no large always-open diagnosis block, and no unrelated Mermaid error text visible.
- **AC-05** Invalid Mermaid content renders as a compact local fallback or is hidden from list surfaces.
- **AC-06** `npx tsc --noEmit` passes or any failure is clearly identified as pre-existing.
- **AC-07** Browser inspection covers `/mistakes`, `/write-mistake`, and `/write-mistake/[slug]`.
