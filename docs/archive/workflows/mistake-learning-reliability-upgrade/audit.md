# Audit: Mistake Learning Reliability Upgrade

Date: 2026-06-12

## Scope

This audit combines runtime errors observed during live usage with product-quality issues in the mistake-learning flow. It is read-only evidence for the workflow docs; it is not an implementation report.

## Finding A1: Public API/Login Fetch Failures

Severity: P0

Observed symptoms:

- Browser toast showed `Failed to fetch` on mistake/review interactions.
- The user reported login repeatedly becoming broken.
- Public API behavior depended on whether the frontend called the public API host or an Access-protected host.

Likely root causes:

- Public API routing and Cloudflare tunnel availability are part of the user-visible auth/API flow.
- A generic `Failed to fetch` toast hides whether the real failure is CORS, Cloudflare Access redirect, tunnel `530/1033`, expired auth, or backend `500`.

Required direction:

- Frontend must consistently use the public API base for browser requests.
- Auth/session failure, CORS/network failure, Cloudflare/tunnel failure, and backend JSON errors must produce different user-facing diagnostics.
- Validation must include public-origin CORS probes and browser checks after login.

## Finding A2: Note Datetime Writes Can Fail From Timezone Mismatch

Severity: P0

Observed symptoms:

- Review submission on `/mistakes/review` showed `提交失败: Failed to fetch`.
- Backend stack trace showed timezone-aware datetime values being written into timestamp columns that are timezone-naive.
- Source inspection also found adjacent note update/type-conversion paths that write the same timezone-aware value shape into `Note.updated_at`.

Code evidence:

- Review writes `datetime.now(timezone.utc)` into `Note.last_reviewed` and `Note.updated_at`.
- Note update and type-conversion paths also write `datetime.now(timezone.utc)` into `Note.updated_at`.
- `Note.updated_at` and `Note.last_reviewed` are SQLAlchemy `DateTime` columns without timezone.

Required direction:

- Choose one consistent timestamp policy for all `Note` datetime writes.
- For a minimal low-risk patch, write naive UTC datetimes to current naive `DateTime` columns.
- Add regression validation for review submission, note edit/update, and type conversion if the implementation touches those paths.

## Finding A3: Mistake Save Fails With Slug Conflict

Severity: P0

Observed symptoms:

- Creating a new mistake showed `保存失败: {"detail":"Slug already exists"}`.
- Titles containing Chinese plus `IPv4` can collapse to the same generated slug, for example `ipv4`.

Code evidence:

- The write-mistake form generates slugs by lowercasing the title and stripping non-word characters.
- Backend rejects duplicate slugs with HTTP 409.
- The UI does not expose a slug field in the create mistake flow.

Required direction:

- Backend should be authoritative for unique slug generation or collision suffixing.
- Frontend should show a clear save conflict message if a conflict still occurs.
- Regression validation must cover repeated Chinese titles containing the same ASCII token.

## Finding A4: Tags And Weak Points Are Fragmented

Severity: P1

Observed symptoms:

- Sidebar and summary surfaces show many small items such as `直通交换`, `交换机`, `以太网`, and generic labels.
- The UI treats raw tags and knowledge points as flat, equally important pills.

Code evidence:

- `/mistakes` accumulates tags from current list items and passes them directly to `KnowledgeSidebar`.
- `KnowledgeSidebar` renders all tags as raw pills.
- Weak points are grouped by splitting the raw `knowledge_points` string.

Required direction:

- Separate retrieval tags, canonical knowledge concepts, and weak-point clusters.
- Do not show every raw point as a primary navigation/filter.
- Add alias/normalization for display and weak-point aggregation.
- Add tag-write hygiene so quality labels such as `解析清晰`, one-off adjectives, and overly small fragments are not repeatedly saved into the primary tag pool.

## Finding A5: Weak-Point Diagnosis Is Template-Like

Severity: P1

Observed symptoms:

- Diagnosis repeats generic advice such as doing special practice.
- Generated rescue plans are static templates.

Code evidence:

- Backend weak-point endpoint is deterministic and only returns counts, top error reasons, and evidence sources.
- Frontend turns those counts into fixed diagnosis text.

Required direction:

- Keep deterministic weak-point aggregation provider-free.
- Add a separate personalized analysis layer that uses source refs and learner-specific fields.
- Display evidence-backed advice with related mistake links and next action checklists.

## Finding A6: Weak-Point UI Takes Too Much Page Space

Severity: P1

Observed symptoms:

- The full weak-point diagnosis occupies a large section on `/mistakes`.
- The user wants a drawer-style interaction.

Required direction:

- Replace the full inline panel with a compact summary entry and an openable drawer.
- Drawer should work as a right-side drawer on desktop and bottom drawer on mobile.
- The page should remain scan-friendly when the drawer is closed.

## Finding A7: Knowledge Summary Placement Is Wrong

Severity: P1

Observed symptoms:

- `知识点归总` appears as a large lower block, leaving a large empty area.
- Tags and knowledge points are visually separated even though they are related metadata.

Code evidence:

- The mistake detail page renders tags in the right rail.
- It renders `知识点归总` later as a large `StudyBlock`.
- Large study blocks have a fixed minimum height.

Required direction:

- Move knowledge summary below tags in the right rail.
- Keep the main column focused on question, my answer, correct answer, and analysis.
- Avoid large empty study blocks for short metadata.

## Finding A8: AI Formula Output Is Not Reliably LaTeX

Severity: P1

Observed symptoms:

- AI generated formulas can appear as plain text.

Code evidence:

- The project already has KaTeX support in the markdown renderer.
- AI prompts ask for LaTeX, but the output is not validated or repaired.

Required direction:

- Strengthen AI output requirements and add validation/repair for formula-like text.
- Preserve `$...$` and `$$...$$` through JSON, persistence, and `RichText`.
- Add a small rendering regression case for math in mistake fields.

## Finding A9: Personalized Error-Cause Analysis Lacks Inputs

Severity: P1

Observed symptoms:

- AI analysis does not reflect why the learner personally got the question wrong.
- The user noted that AI does not receive the wrong answer and self-analysis.

Code evidence:

- AI analyze request schemas accept only `images` or `text`.
- The write-mistake form has `my_answer`, but standard AI calls do not pass it as a structured field.
- The current `analysis` field mixes AI analysis and manual reflection.

Required direction:

- Extend AI request contracts to include `my_answer`, `correct_answer`, and `user_error_analysis`.
- Add UI fields that make it natural to capture the learner's own reasoning before or during AI analysis.
- Store personalized outputs separately from generic solution analysis.
