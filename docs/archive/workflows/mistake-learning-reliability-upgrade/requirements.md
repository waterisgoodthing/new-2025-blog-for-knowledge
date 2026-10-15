# Requirements: Mistake Learning Reliability Upgrade

Version: v1.0
Date: 2026-06-12
Status: Draft, awaiting task approval

## User Roles

| Role | Scenario |
|------|----------|
| Personal admin | Logs in, records mistakes, edits notes, reviews due mistakes, and expects public deployment to work from the browser. |
| Mistake learner | Reads mistake details, compares personal answer with correct answer, reviews weak points, and wants actionable diagnosis. |
| Implementation agent | Executes the approved task list while preserving existing dirty worktree changes. |

## Core Problems

1. Browser API failures are too opaque and can break login/review/save flows.
2. Review submission and adjacent note update paths can hit backend timestamp consistency bugs.
3. Mistake creation can fail on duplicate slugs with no recovery path.
4. Tags and weak points are fragmented because raw tags, concepts, and quality labels are mixed.
5. Weak-point diagnosis is count-based and template-like, not personalized.
6. Weak-point diagnosis consumes page space and should become a drawer-style workflow.
7. Mistake detail layout separates tags from knowledge summary and wastes space.
8. AI formula output is not reliably LaTeX even though rendering support exists.
9. AI analysis does not receive structured personal-answer context.

## Functional Requirements

### REQ-P0-01: Public API And Login Reliability Diagnostics

- Input: Browser requests from `blog.limengyang.me` to backend APIs, including auth status, subjects, notes, review, and AI endpoints.
- Processing: Use the correct public API base URL; detect and classify network, CORS, Cloudflare/tunnel, auth, and backend JSON failures.
- Output: Stable authenticated API calls and clear user-facing error messages.
- Failure handling: If the API host is unreachable or auth expires, show actionable messages instead of generic `Failed to fetch`.
- Acceptance: Public-origin probes and browser checks confirm the correct API host, CORS headers, auth status, and meaningful errors.

### REQ-P0-02: Note Datetime Write Consistency

- Input: A review quality score submitted from `/mistakes/review`, plus adjacent `Note` update/type-conversion operations that write `updated_at`.
- Processing: Update `Note.updated_at` and `Note.last_reviewed` using one timestamp format compatible with the current `Note` datetime columns.
- Output: Review submission returns success, updates SM-2 fields, and navigates to the next item; adjacent note update paths do not reintroduce the same datetime error.
- Failure handling: Backend exceptions return JSON errors and are logged; frontend displays the backend reason.
- Acceptance: Review submission, note edit/update, and type conversion no longer raise timezone-aware/naive datetime errors in the covered paths.

### REQ-P0-03: Unique Slug Handling For Mistake Creation

- Input: A new mistake title, including Chinese titles containing the same ASCII token such as `IPv4`.
- Processing: Generate or resolve a unique slug server-side, or retry with suffixes safely.
- Output: New mistakes save successfully without forcing the user to manually invent a slug.
- Failure handling: If a conflict remains, frontend shows a clear duplicate-title/slug message.
- Acceptance: Creating two mistakes with similar Chinese titles succeeds with distinct slugs.

### REQ-P1-01: Tag And Concept Normalization

- Input: Existing note tags, AI generated tags, and `knowledge_points`.
- Processing: Separate broad retrieval tags from canonical knowledge concepts; normalize aliases; suppress low-value labels in primary displays; prevent obvious quality labels or one-off fragments from entering the primary tag pool on new AI-assisted saves.
- Output: `/mistakes` sidebar and summaries show grouped, meaningful concepts instead of raw duplicated pills.
- Failure handling: Unknown concepts fall back to raw display under a secondary/details area, not the primary summary.
- Acceptance: Example network concepts display as grouped weak points instead of scattered `直通交换`/`交换机`/`以太网` items, and new AI tag suggestions do not include quality labels such as `解析清晰`.

### REQ-P1-02: Personalized Weak-Point Diagnosis

- Input: Related mistake sources, `question`, `my_answer`, `correct_answer`, `analysis`, `knowledge_points`, tags, review metrics, and optional user self-analysis.
- Processing: Generate evidence-backed personalized diagnosis and next-action advice from the actual mistake pattern.
- Output: Weak-point drawer shows personalized cause, evidence, related mistakes, and a short action checklist.
- Failure handling: If there is not enough personal context, label the diagnosis as limited and ask for missing fields.
- Acceptance: Diagnosis for an IPv4 mistake references the learner's wrong answer pattern, not only the knowledge-point count.

### REQ-P1-03: Drawer-Style Weak-Point Interaction

- Input: `/mistakes` page weak-point summary data.
- Processing: Render a compact summary on the page and move detailed diagnosis into a drawer.
- Output: Desktop uses a side drawer; mobile uses a bottom drawer. The main page remains scan-friendly.
- Failure handling: Loading, empty, and error states remain available without blocking the mistake list.
- Acceptance: The full weak-point diagnosis can be opened and closed from a compact entry.

### REQ-P1-04: Mistake Detail Layout Reorganization

- Input: A mistake note detail with tags, knowledge points, question, personal answer, correct answer, and AI metadata.
- Processing: Move `知识点归总` below tags in the right rail and remove large empty metadata blocks.
- Output: Main column focuses on learning content; right rail groups review status, tags, knowledge summary, and next actions.
- Failure handling: Missing tags or knowledge points produce compact empty states or omit the block.
- Acceptance: `/notes/[id]` no longer shows a large empty `知识点归总` block below analysis.

### REQ-P1-05: Reliable LaTeX Output And Rendering

- Input: AI generated question, correct answer, analysis, knowledge points, variants, and knowledge cards.
- Processing: Require math expressions to use `$...$` or `$$...$$`; validate/repair formula-like output before persistence.
- Output: Formulas render through existing `RichText`/KaTeX path.
- Failure handling: Invalid LaTeX degrades to visible source text and is marked for manual correction.
- Acceptance: A sample formula field containing `$E=mc^2$` and a block formula renders as math on the detail page.

### REQ-P1-06: Structured Personal Error Inputs

- Input: User's wrong answer, user's own error analysis, correct answer, and question text.
- Processing: Capture `user_error_analysis` in the write-mistake UI, persist it without overwriting generic analysis, and pass it as a separate field to AI analysis instead of requiring the user to paste it into one text blob.
- Output: AI returns generic solution analysis plus separate personalized diagnosis fields; the detail page can show the user's self-analysis and AI's personalized diagnosis distinctly.
- Failure handling: If fields are blank, the UI states that personalization is limited.
- Acceptance: Browser/network inspection confirms AI receives `my_answer` and `user_error_analysis` when present, and reloading the saved mistake preserves the user's self-analysis.

## Non-Functional Requirements

| Type | Requirement |
|------|-------------|
| Scope discipline | Keep changes within `auth`, `mistakes`, `review`, `notes`, and shared API/AI helpers. |
| Data safety | Preserve existing mistake data and do not overwrite personal answers or manual analysis. |
| Security | Do not expose secrets, tokens, or Cloudflare tunnel credentials in repo docs or code. |
| Compatibility | Do not break note/blog rendering while changing mistake detail rendering. |
| Determinism | Keep weak-point aggregation deterministic; call AI only in explicit personalized summary/generation paths. |
| Maintainability | Prefer existing API clients, schemas, hooks, and renderer patterns. |
| Deployment safety | Treat external Cloudflare tunnel changes as operational steps, not source-code changes, unless explicitly requested. |

## Boundaries

Out of scope for this iteration:

- Adding a full `KnowledgePoint` database table unless a later approved design expands scope.
- Reworking the whole notes/blog taxonomy system.
- Replacing the existing markdown renderer.
- Building a public multi-user learning SaaS model.
- Modifying unrelated guestbook/public-site changes currently dirty in the worktree.

## Acceptance Criteria

| ID | Acceptance |
|----|------------|
| AC-P0-01 | Browser login/auth status and core API calls work through the correct public API host. |
| AC-P0-02 | API failures distinguish auth, CORS/network, Cloudflare/tunnel, and backend JSON errors. |
| AC-P0-03 | Review submission and covered note update/type-conversion paths complete without datetime exceptions. |
| AC-P0-04 | Creating duplicate-title Chinese/ASCII mistakes creates distinct slugs or shows a clear recoverable message. |
| AC-P1-01 | `/mistakes` primary tags/weak points are grouped and no longer raw duplicated fragments. |
| AC-P1-02 | Weak-point details open in a drawer and no longer occupy the main page by default. |
| AC-P1-03 | Personalized diagnosis uses and preserves `my_answer` plus `user_error_analysis` when present. |
| AC-P1-04 | `知识点归总` appears below tags in the detail right rail. |
| AC-P1-05 | AI math output persists and renders as LaTeX in mistake fields. |
| AC-P1-06 | Validation evidence is recorded in `validation.md` and per-task completion notes are added to `tasks.md`. |
