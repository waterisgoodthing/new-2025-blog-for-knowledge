# Editor Convergence Source Inventory

Current status: `COMPLETE — D2 OPTION A; E1～E5 PASS; G4 PASS FOR F4 INPUT ONLY`.

## Page and component owners

| Content path | Create owner                     | Edit owner                              | Current composition                                                                                                                                     | Preview owner                                                                                     |
| ------------ | -------------------------------- | --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| Blog         | `src/app/write/page.tsx`         | `src/app/write/[slug]/page.tsx`         | Legacy `useWriteStore`, `WriteEditor`, sidebar/actions, file/url image handling, `usePublish`                                                           | `WritePreview` → `BlogPreview` → existing `useMarkdownRender`                                     |
| Note         | `src/app/write-note/page.tsx`    | `src/app/write-note/[slug]/page.tsx`    | Local form plus `useNoteEditor`, `NoteToolbar`, templates, slash menu, image paste/upload, AI assistant, tag suggestion; edit also exposes version list | `NotePreviewContent` → existing `useMarkdownRender`                                               |
| Mistake      | `src/app/write-mistake/page.tsx` | `src/app/write-mistake/[slug]/page.tsx` | Create route keeps `StagedMistakeForm` only as a compatibility flow; edit route uses `MistakeForm`, including typed fields, uploads and AI assistance   | Structured staged previews; standard edit displays typed field form rather than a Markdown editor |

## Save-path inventory

- Legacy blog `usePublish` → `pushBlog` / `deleteBlog`. `pushBlog` uploads local images with `uploadImage`, resolves Markdown placeholders, then calls typed `createNote` or `updateNote` with `type: 'blog'`; delete calls `deleteNote`.
- Note create calls `createNote`; note edit calls `updateNote` with `expected_revision`, metadata and, when editing a mistake through this compatibility editor, the typed mistake fields. Both can upload pasted images with `uploadImage`.
- Standard mistake form calls `createNote`/`updateNote`, uploads evidence images via `uploadImage`, and retains AI metadata. Staged mistake create also calls the typed Note API after its separate AI/confirmation stages.
- The shared typed client is `src/lib/api/notes.ts`. Backend `NoteCreate`, `NoteUpdate` and `NoteOut` retain `note`, `blog`, `mistake`, metadata, revision and review fields. `POST`, `PUT`, `DELETE`, batch delete and promotion in `backend/app/routers/notes.py` depend on `get_current_admin`.

## Access and preview facts observed

- `/write`, `/write-note`, `/write-note/[slug]`, `/write-mistake`, and `/write-mistake/[slug]` render through strict `AuthGate`; its source uses `useAdminAuth({ mode: 'strict' })` and redirects an anonymous visitor to `/manage` before rendering children.
- The current legacy `/write/[slug]` source does **not** wrap its composition in `AuthGate`. Its mutation paths still use the protected Note API, so this is a page-level access evidence gap, not authority to weaken or change the backend. E3 must include it in the private-route matrix; E1 performs no route or permission change.
- Blog and note Markdown previews remain on existing production `useMarkdownRender` owners. They are not a fallback to the isolated Markdown PoC, and E1 makes no renderer migration or security claim.
- Mistake records are first-class Note fields: `subject`, `difficulty`, `question`, `my_answer`, `correct_answer`, `analysis`, `knowledge_points`, image/AI metadata, plus `ef`, `interval`, `repetitions`, `next_review`, and `last_reviewed` on responses. Both standard forms build a human-readable Markdown `content` projection, but persist the typed fields separately; future work must preserve this contract.

## E1 boundary conclusion

Only the common typed Note client and protected backend mutation boundary are shared facts. This inventory is not yet a common-primitive decision, a save-contract comparison, a field matrix, or an implementation design; those are E2, E3 and E4 respectively. No source, schema, route, renderer, visual UI, data migration, Git, deployment, real data, credential, production API, or `AUTH_BYPASS` action occurred.

## E2 capability matrix

| Capability                         | Blog legacy                                                   | Note                                                               | Mistake                                                                        | Evidence-backed result                                                                             |
| ---------------------------------- | ------------------------------------------------------------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------- |
| Title/slug and typed Note mutation | `PublishForm`, `pushBlog` → Note API                          | local form → Note API                                              | `MistakeForm`/staged form → Note API                                           | Common data-boundary candidate; no shared UI decision                                              |
| Tags and save feedback             | sidebar metadata, toast/loading                               | tag input/suggestion, toast/saving                                 | tag input/suggestion, toast/saving                                             | Candidate for a small metadata/tag and save-state primitive only after a later approved extraction |
| Markdown composition               | textarea with bold/italic/link/indent/paste-image logic       | textarea with `useNoteEditor`, toolbar, slash commands/templates   | no primary Markdown authoring surface                                          | Blog/note-only candidate: selection/insert/wrap core, not a universal editor                       |
| Markdown preview                   | `WritePreview` → `BlogPreview`                                | edit/preview tab → `NotePreviewContent`                            | structured/staged previews; no equivalent live Markdown preview                | Not common; preserve current owners and renderer boundary                                          |
| Images                             | file/url asset state and placeholder substitution             | pasted image upload inserts Markdown URLs                          | evidence images, AI image input and removal state                              | Not common beyond protected upload client; semantic contracts differ                               |
| AI                                 | no equivalent owner                                           | prose assistant that inserts/replaces text and metadata            | analysis/interpretation/final-analysis/diagram workflow and metadata staleness | Not common; mistake AI must remain domain-specific and protected                                   |
| Version/conflict handling          | no `expected_revision` in legacy blog save                    | edit supplies `expected_revision`, reads versions                  | standard form currently updates without revision argument                      | Not common; requires a separate save-contract decision, never silent normalization                 |
| Review model                       | no review fields                                              | may edit a mistake in compatibility form but persists typed fields | owns mistake type and review-related record fields                             | Not common; first-class mistake data cannot become Markdown                                        |
| Page access                        | create is `AuthGate`; current `/write/[slug]` source lacks it | create/edit `AuthGate`                                             | create/edit `AuthGate`                                                         | Not an extraction candidate; E3 must freeze the private-route matrix                               |

### E2 supported candidates and exclusions

- Supported candidates: typed `NoteCreate`/`NoteUpdate` DTO boundary; tag list normalization and empty-tag suggestion behavior; save pending/error/success state; a **blog/note-only** selection/insert/wrap utility if later code evidence and tests preserve each route's behavior.
- Explicit exclusions: `UnifiedEditor`; a common Markdown preview; common AI panel; common image workflow; common versioning; treating a mistake as generic Markdown; route ownership or AuthGate changes; any production Markdown renderer change.
- Reason: repeated UI labels alone are insufficient. The matrix requires common input/output semantics, and current preview, upload, AI, revision, review and access behavior diverge materially.

## E3 frozen field, save, preview and permission matrices

### Fields and save semantics

| Contract area              | Blog                                           | Note                                                                           | Mistake                                                                                                                 | Frozen constraint                                                                                                                |
| -------------------------- | ---------------------------------------------- | ------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| Core identity/content      | `slug`, `title`, Markdown `content`, tags      | same core fields; create can choose `note` or `blog`                           | `type: 'mistake'`, title/slug and a readable Markdown projection                                                        | Do not erase or infer domain type during a future extraction                                                                     |
| Publication metadata       | summary, cover, category, hidden, image assets | summary/category/cover/folder/sort order; edit type is displayed as immutable  | tags, subject/difficulty and images; no equivalent blog publication panel                                               | Metadata is not a uniform form; only common DTO transport is established                                                         |
| First-class mistake fields | none                                           | compatibility edit can load/save a mistake's typed fields                      | `subject`, `difficulty`, `question`, `my_answer`, `correct_answer`, `analysis`, `knowledge_points`, images, AI metadata | These fields must remain separate DTO/schema values; Markdown content is only a projection                                       |
| Review attributes          | none                                           | surfaced on `NoteOut` when type is mistake                                     | `ef`, `interval`, `repetitions`, `next_review`, `last_reviewed` are server-owned response state                         | No editor primitive may overwrite/reset review state or reduce it to text                                                        |
| Create/update concurrency  | legacy blog saves no `expected_revision`       | note edit passes `expected_revision: note.revision` and reads versions         | standard mistake form updates without `expected_revision`; note compatibility editor does pass it                       | Preserve current difference until a separately approved save-contract decision; never silently add/remove optimistic concurrency |
| AI state                   | no equivalent owner                            | text-assist operations may modify selected content/title/summary/tags/category | AI analysis/interpretation/final-analysis/diagram plus stale metadata handling                                          | Do not share or flatten AI state; all AI calls remain optional admin tools, not a save prerequisite                              |

### Preview and permission boundary

| Surface           | Current behavior                                                                                                                   | Required future boundary                                                                                                                 |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Blog preview      | `WritePreview` delegates to `BlogPreview` and existing production `useMarkdownRender`                                              | Preserve owner and current renderer until separately authorized Markdown migration; never select the old renderer as a security fallback |
| Note preview      | local edit/preview tab delegates to `NotePreviewContent` and existing `useMarkdownRender`                                          | Preserve per-route preview contracts; no common preview claim yet                                                                        |
| Mistake preview   | staged workflow has structured analysis/diagram previews; standard form is structured field editing                                | Do not force a Markdown preview or hide first-class fields behind a renderer                                                             |
| Public reads      | `GET /api/notes` and `GET /api/notes/{slug}` use optional current-user filtering; non-admin sees only published/non-hidden records | Keep public read access and hide administrative actions; no page-level AuthGate on public content                                        |
| Writes/uploads    | Note create/update/delete/batch/promote and `/api/notes/upload-image` use `get_current_admin`                                      | Backend remains the security boundary regardless of UI composition                                                                       |
| AI/review         | AI analysis/staged mistake endpoints and review queue/submit/stats/plan use `get_current_admin`                                    | Never expose these to public pages or make AI mandatory for saving a mistake                                                             |
| Editor page gates | `/write`, `/write-note*`, `/write-mistake*` use strict `AuthGate`; legacy `/write/[slug]` does not in current source               | Record this as a private-route remediation requirement for later approved work; do not change it during F3 evidence                      |

### E3 non-negotiables

- `get_current_admin`, strict session behavior, public-read filters, AuthGate-covered private pages, AI/upload/review protection and Cookie transport remain unchanged.
- A future common primitive may accept explicit domain data; it may not coerce a mistake record into `content` alone, mutate review fields, make AI or upload required, or alter preview/route ownership.
- The current legacy blog-edit page gate gap is a residual risk, not a reason to loosen backend protection or to perform a route change without separate approval.

## E4 recommendation and rollback boundary

The current evidence supports only **Option A: minimal shared primitives plus domain-editor coexistence**. Its allowed future extraction candidates and rollback are documented in `design.md`; each remains behind explicit domain adapters and can be removed without a schema/data/route/renderer migration. Option B (a larger unified owner) is not evidence-ready because it would have to normalize divergent state, preview, asset, AI, revision and access contracts. D2 is required before E5 can create an implementation task list.

## D2 decision

The user selected **Option A — minimal shared primitives plus domain-editor coexistence** on 2026-08-16. This selects the evidence-backed direction; it does not authorize source extraction. E5 may now create only a separate, explicitly approval-gated implementation task list. Its mandatory boundaries remain the typed first-class mistake/review contract, current route owners, existing preview owners, strict session/backend authorization, and the recorded legacy `/write/[slug]` access risk.

## E5 implementation-list output

`implementation-tasks.md` is now the separate Option A execution gate. It is intentionally `NOT APPROVED FOR IMPLEMENTATION`: it requires a new explicit approval and a fresh worktree/source inventory before any future action. The sequence starts with characterization/negative contract tests, limits extraction to blog/note-only helpers, preserves divergent save behavior, and moves the legacy blog edit AuthGate gap into a separate security task rather than hiding it in an editor refactor.

## G4 decision

`PASS — F4 input only`. The fields, save behavior, preview ownership, permission boundaries, supported reuse candidates, D2 direction, rollback boundary and separate implementation gate are source-backed and complete. The gate does not say the current editor architecture is migrated or free of risk: the legacy `/write/[slug]` page-level AuthGate gap, divergent concurrency modes and production Markdown renderer boundary remain explicit residuals. They are carried into the F4 input package and future implementation/security approval, while current backend mutation/AI/upload/review protection remains intact.
