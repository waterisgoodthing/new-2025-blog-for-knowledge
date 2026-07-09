# Design: Mistake Editor Simplification

## Baseline Findings

Current split:

- Create route: `src/app/write-mistake/page.tsx` renders `StagedMistakeForm`.
- Edit route: `src/app/write-mistake/[slug]/page.tsx` renders legacy `MistakeForm`.
- List route: `src/app/mistakes/page.tsx` renders sidebar, stats cards, review plan, weak-point diagnosis, filters, and item list in one long stack.

This explains the user's "two sets of logic" report: the create and edit routes are not only different modes, they are different components with different saving models.

## Visual Thesis

Operational study workspace: compact, calm, and scan-first, with one clear action row and AI details kept in progressive disclosure instead of a pile of panels.

## Content Plan

- Editor header: back action, title, save/publish action, small mode/status labels.
- Source and question area: images/text input, recognized question, options, metadata.
- Learner reasoning area: wrong thought/user error reason placed near the question.
- AI support area: interpretation, final analysis, diagram, and regeneration actions in collapsible sections.
- Save footer: primary save, cancel, and clear validation feedback.

## Interaction Thesis

- Use compact segmented stage/status navigation for AI workflow, but allow direct edit mode to jump into already completed sections.
- Use collapsible sections/drawers for AI diagnosis on both editor and list page.
- Keep list-page interactions focused: search/filter, start due review, open weak-point drawer, open item.

## Implementation Approach

### 1. Shared Editor Shell

Create or refactor toward a single mistake editor component that supports:

- `mode: 'create' | 'edit'`
- optional `initialData: NoteDetail`
- create save path: `createNote`
- edit save path: `updateNote(initialData.slug, payload)`
- shared field model for title, subject, difficulty, tags, images, question, wrong thought, correct answer, analysis, knowledge points, and AI metadata

The preferred path is to evolve `StagedMistakeForm` into a reusable editor shell because it is the current create flow. Keep the legacy `MistakeForm` only as a temporary source of known edit behaviors, then remove or stop routing to it once the unified editor covers edit mode.

### 2. Staged Metadata Rehydration

When `initialData` exists, derive editor state from:

- first-class note fields: `title`, `question`, `my_answer`, `correct_answer`, `analysis`, `knowledge_points`, `subject`, `difficulty`, `tags`, `images`
- `ai_metadata.question_ai_draft`
- `ai_metadata.user_error_reason` / `user_error_analysis`
- `ai_metadata.ai_error_interpretation`
- `ai_metadata.final_analysis`
- `ai_metadata.diagram` and `ai_metadata.diagrams`

For edit mode, do not require the user to replay every AI stage. Show completed AI sections as reviewable/editable state, with regenerate actions where existing API wrappers already support it.

### 3. Editor Visual Simplification

Reduce card stacking:

- Use one constrained editor surface with section dividers instead of many nested cards.
- Keep source upload and pasted text side by side on desktop and stacked on mobile.
- Move technical AI details behind disclosure.
- Preserve dense operational fields rather than a decorative landing-page feel.

### 4. `/mistakes` Page Simplification

Proposed layout:

- Top toolbar: title, due-review CTA, add mistake.
- Compact status strip: only essential counts, likely total/due/mastered.
- Main row: sidebar + list.
- Search and difficulty filter directly above list.
- Weak-point diagnosis becomes compact summary or drawer trigger. It should not occupy a large always-open block.
- Remove duplicated "start review" affordance if both plan and due count show the same action.

### 5. Mermaid Error Containment

Root cause needs implementation-time verification, but likely paths are:

- invalid Mermaid in saved mistake content rendered by shared markdown flow,
- invalid AI diagram metadata rendered by `MermaidBlock`,
- Mermaid library appending parser error SVG/DOM outside the component boundary.

Fix should be source-based, not CSS-only:

- inspect `src/components/mermaid-block.tsx`;
- ensure render attempts clear previous Mermaid output before rendering;
- catch parse/render errors and render a compact local fallback;
- avoid rendering invalid diagram metadata on list surfaces;
- verify `/mistakes` does not include a global Mermaid error artifact.

## Files Expected To Change

- `src/app/write-mistake/page.tsx`
- `src/app/write-mistake/[slug]/page.tsx`
- `src/app/write-mistake/components/staged-mistake-form.tsx`
- possibly `src/app/write-mistake/components/mistake-form.tsx` if retiring the old edit component
- `src/app/mistakes/page.tsx`
- possibly `src/app/mistakes/components/weak-point-diagnosis.tsx`
- possibly `src/components/mermaid-block.tsx`

## Validation Plan

- Run `npx tsc --noEmit`.
- Run browser inspection for:
  - `/mistakes`
  - `/write-mistake`
  - `/write-mistake/[slug]` using an existing mistake slug.
- Confirm screenshot symptom is gone: no large `Syntax error in text mermaid version...` marker visible on `/mistakes`.
