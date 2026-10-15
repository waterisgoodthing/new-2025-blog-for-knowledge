# Requirements

## Background

The notes workspace is becoming the daily operating surface for writing notes, reviewing mistakes, organizing folders/tags, and using AI. Several current behaviors are confusing or too rigid:

- Tag filters are always exposed and cannot be toggled off by clicking the active tag again.
- Weekly summary and AI organization suggestions appear outside the intended "全部" context.
- Folder creation exists in API/data concepts but is not discoverable from the notes workspace.
- The top-right create button is hardcoded as "写笔记" even when the active context changes.
- The editor toolbar has icons, but long-hover explanations and richer insert/template choices are not enough.
- The AI assistant is a fixed action panel rather than a conversational "tell it what I want changed" tool.
- Saved notes should get AI tag suggestions/completion automatically.
- Mistake AI analysis progress uses static phase text instead of truthful backend progress.
- There is a reported whole-system scroll/rendering issue where content continues rendering while scrolling down.

## Functional Requirements

### REQ-01 Collapsible Navigation And Tags

- Input: user opens `/notes` or related knowledge pages.
- Processing: sidebar sections such as tags should support collapse/expand. On mobile, drawer behavior should remain available.
- Output: tags are discoverable but do not occupy excessive vertical space.
- Failure handling: if tags fail to load, show an empty/error state without blocking notes.
- Acceptance: tag section can collapse and expand; active tag state remains visible.

### REQ-02 Toggle Active Tag

- Input: user clicks an active tag.
- Processing: if the clicked tag is already selected, clear `activeTag` and reset pagination.
- Output: list returns to the non-tag-filtered view for the current content context.
- Failure handling: no API mutation should be triggered.
- Acceptance: clicking the same tag twice selects then clears it.

### REQ-03 Contextual Summary And Suggestions

- Input: user switches between all/note/blog/mistake/inbox/folder/tag contexts.
- Processing: weekly summary appears only in "全部" context. AI suggestions become a collapsible drawer/panel instead of a full always-open card.
- Output: other tabs such as mistake-only view do not show weekly summary by default.
- Failure handling: suggestion API failure does not blank the page.
- Acceptance: weekly summary renders only when `activeFilter === "all"` and no folder/tag/search override is active; AI suggestions can open/close.

### REQ-04 Scroll/Rendering Stability

- Input: user scrolls down long lists or switches routes.
- Processing: avoid repeated mount animations, blank screens, or runaway rendering while scrolling.
- Output: page remains stable and responsive.
- Failure handling: if a pre-existing issue is found outside this workflow, document it in validation/risk.
- Acceptance: manual browser check shows no continuous re-render loop or blank content after scrolling.

### REQ-05 Folder Creation Entry

- Input: user wants to create a folder from the notes workspace.
- Processing: provide a visible create-folder action near the folder section and reuse existing folder API patterns.
- Output: newly created folder appears in the sidebar and can receive dragged/moved notes.
- Failure handling: API errors show a toast and preserve form input.
- Acceptance: user can create a folder without leaving `/notes`.

### REQ-06 Right-Click Context Menu

- Input: user right-clicks a note card, folder, or tag.
- Processing: show a context menu with scoped actions.
- Output: actions are available without requiring tiny hover buttons.
- Failure handling: menu closes on Escape/outside click; destructive actions require confirmation.
- Acceptance: at least note-card right-click is implemented after action set approval.

### REQ-07 Dynamic Create Button

- Input: active workspace context changes.
- Processing: top-right action label and href should reflect context.
- Output:
  - all/note context: "写笔记" -> `/write-note`
  - blog context: "写博客" -> existing `/write` blog editor
  - mistake context: "写错题" -> `/write-mistake`
- Failure handling: unknown context falls back to "写笔记".
- Acceptance: button is not hardcoded in contexts where a more specific create action is known.

### REQ-08 Editor Long-Hover Help

- Input: user rests cursor on toolbar buttons such as H1, template, insert.
- Processing: after a short delay, show a tooltip with name, purpose, and optional example.
- Output: icon-only and compact controls become self-explanatory.
- Failure handling: tooltip must not trap focus or cover active text.
- Acceptance: toolbar controls have accessible labels and delayed explanatory tooltips.

### REQ-09 Richer Templates And Inserts

- Input: user opens templates or insert menu.
- Processing: provide richer domain-neutral templates and blocks based on reusable thinking structures such as capture, understand, analyze, review, plan, organize, and express.
- Output: inserted content is useful and editable Markdown.
- Failure handling: insertion respects cursor position and does not corrupt selected text.
- Acceptance: template and insert menus include expanded categorized options.

### REQ-10 Conversational AI Editor

- Input: user types a natural-language request such as "把选中的内容整理成表格" or "根据全文补一个复习计划".
- Processing: AI assistant accepts free-form instructions with context/selection, streams result, then lets user insert/replace/apply metadata.
- Output: fixed action chips become shortcuts, not the only available mode.
- Failure handling: stop generation works; errors show without losing draft content.
- Acceptance: AI panel includes a request box and can apply generated output to editor content.

### REQ-11 AI Tag Completion On Save

- Input: user clicks save/publish with missing or incomplete tags.
- Processing: if no tags are listed, the save flow is intercepted with an explanation. The system generates tag suggestions automatically and lets the user continue with the generated tags. The reminder includes a lower-left "next time do not remind me" option.
- Output: saved content has better tags without forcing manual entry.
- Failure handling: AI failure should not block saving; the user can continue saving without generated tags.
- Acceptance: saving with empty tags triggers the reminder/tag generation flow unless the user has disabled future reminders.

### REQ-12 Truthful Mistake AI Progress

- Input: user uploads image or submits text for mistake AI analysis.
- Processing: backend reports real progress events if possible, preferably with streaming/SSE rather than client-side fake phase rotation or polling.
- Output: UI says what is actually happening: uploading, OCR request sent, model analyzing, parsing result, saving/applying.
- Failure handling: partial progress ends with a concrete error state.
- Acceptance: static fake phase text is replaced by real event-driven progress or a documented server-limited fallback.

## Non-Functional Requirements

- Preserve existing user changes and dirty files.
- Keep operational UI dense and readable; no marketing-style hero pages.
- Every icon-only action must have an accessible name.
- Avoid introducing a new state library.
- Avoid large dependencies unless justified.
- Frontend changes must pass `npx tsc --noEmit` or document pre-existing failures.
- UI changes require browser inspection of relevant routes.

## Decisions Needed Before Implementation

- D1 Right-click actions: decided for first version.
  - Note card actions: open, edit, move to folder, copy link, delete.
  - Folder/tag right-click actions are deferred unless explicitly approved later.
- D2 Blog create route: decided.
  - Use current `/write` blog editor.
- D3 AI tag completion policy: decided.
  - Empty-tag save is intercepted with an explanation, AI auto-suggests tags, and the reminder has a lower-left "next time do not remind me" option.
- D4 Template categories and default template list: decided.
  - Use domain-neutral workflow shapes: 记录型, 理解型, 分析型, 复盘型, 计划型, 整理型, 表达型.
- D5 Conversational AI scope: decided.
  - Aggressive scope: AI may update title, summary, tags, category, and body content, with explicit user apply/confirm controls.

## Template Discussion Candidates

Template design is decided at the category level. Templates should stay domain-neutral and avoid overly specific subjects such as a single course, protocol, or algorithm category.

Candidate template families:

- 记录型: capture facts, source, context, and raw observations.
- 理解型: explain concepts, relationships, examples, and open questions.
- 分析型: break down a problem, cause, evidence, alternatives, and conclusion.
- 复盘型: compare goal/process/result, extract lessons, and define next action.
- 计划型: define objective, constraints, tasks, priority, and review checkpoint.
- 整理型: convert messy notes into outline, table, checklist, or knowledge map.
- 表达型: shape content into article, explanation, summary, or presentation draft.

## Out Of Scope For First Implementation Pass

- Full folder rename/delete/merge unless approved in right-click scope.
- Backend data model changes for folders/tags unless existing APIs are insufficient.
- Replacing the entire editor with a rich-text editor.
- Production-grade multi-user collaborative editing.

## 2026-06-15 Follow-Up Requirements

### REQ-13 OS-Like Folder Navigation

- Input: user expects folder placement and folder navigation to behave like an operating-system file browser.
- Processing: folder selection, child folder creation, and active folder context must be visually and behaviorally obvious.
- Output: the user can tell where they are and where new content will be created.
- Failure handling: ambiguous folder state should fall back to inbox/all-content without silently losing context.
- Acceptance: folder context is visible, selectable, and preserved through the supported create/edit/back flows.

### REQ-14 Create Note Inside Current Folder

- Input: user is currently inside a folder and clicks the create-note action.
- Processing: `/write-note` receives and preserves `folder_id`, saves the note with that folder, and returns to the same folder-aware notes context.
- Output: the newly created note is already classified into the current folder.
- Failure handling: invalid or deleted `folder_id` is rejected by the backend and shown clearly in the UI.
- Acceptance: creating from a selected folder produces a note whose `folder_id` matches the selected folder, without manual move.

### REQ-15 Restore AI Tag Generation

- Input: user saves a note with missing tags or requests tag generation in the AI assistant.
- Processing: tag generation streams or resolves reliably, parses the JSON/tag list, and offers explicit apply/merge controls.
- Output: suggested tags are visible and can be applied to the note.
- Failure handling: AI/tag parse failures show a usable error and do not block saving.
- Acceptance: empty-tag save and AI assistant tag generation both expose tag suggestions again.

### REQ-16 Preserve Folder Context After Edit Back

- Input: user enters edit/detail from a folder-scoped overview and then returns.
- Processing: route links or navigation state preserve the previous folder context.
- Output: overview returns to the same main folder instead of all content.
- Failure handling: if context is missing, default to all content.
- Acceptance: folder-scoped navigation round trip keeps the active folder.

### REQ-17 Scheduled Weekly Summary Folder

- Input: every Monday at 08:00 local time, the user wants a weekly summary generated, displayed, and saved under a dedicated folder.
- Processing: determine whether scheduling belongs in backend service, deployment cron, or on-demand idempotent generation, then implement the smallest reliable path.
- Output: weekly summaries are persisted as notes/files in a weekly-summary folder and displayed in the notes workspace.
- Failure handling: duplicate runs for the same week must not create duplicate summaries.
- Acceptance: the system can prove where the summary is stored and how Monday 08:00 generation is triggered.

### REQ-18 Evidence-Based AI Suggestions

- Input: the system produces organization or weak-point suggestions.
- Processing: suggestions must be based on stable evidence such as mistakes, review outcomes, knowledge points, missing metadata, or repeated failed reviews, not merely frequent recent uploads.
- Output: suggestion text explains the evidence and avoids overclaiming user weakness.
- Failure handling: insufficient evidence yields neutral organization suggestions instead of diagnosis.
- Acceptance: uploading many computer-network notes alone does not produce "you are bad at computer networking" style weak-point claims.

### REQ-19 Streaming UI Render Hardening

- Input: long AI/tag streaming responses arrive rapidly while the user switches desktops or the component unmounts.
- Processing: render updates are throttled with `requestAnimationFrame`, pending animation frames are canceled on completion/error/unmount, and stale request ids are ignored.
- Output: no runaway React re-render loop from per-chunk updates.
- Failure handling: abort/stop and unmount clean up pending work.
- Acceptance: code has shared or clearly duplicated cleanup paths and TypeScript validation passes.
