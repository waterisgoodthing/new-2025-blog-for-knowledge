# IMPROVEMENT BACKLOG — Personal Learning System

> 文档治理（2026-10-09）：历史审计/建议快照保留。测试、版本、缺陷与权限描述只对应报告原时点；本轮重新核验结果以当前审查和状态为准，不覆盖原裁定。 当前入口见 [文档索引](docs/DOCUMENTATION_INDEX.md)。

Companion to `PERSONAL_LEARNING_SYSTEM_AUDIT.md`. 35 recommendations, each with: Current Problem → Evidence → Why It Matters → Recommended Change → Expected Benefit → Implementation Complexity (S/M/L/XL) → Priority (P0–P3) → Affected Files → Verification Method.

**Sizing legend:** S ≤ 1 day · M 1–3 days · L ~1 week · XL >1 week (single developer).
**Tier:** A — Now · B — Next · C — Later · D — Do Not Build Yet.

---

## P0 — Close the loop (Tier A)

### R01 — Review items must model lapse and mastery (graduated state)
- **Category:** Review System
- **Current Problem:** `submit_review` always increments `repetitions` (even ratings 0–2) and maps failures to a 1-day interval with no lapse reset; `ReviewItem.state` CHECK only allows `active|paused`; nothing can mark an item "learned". A mistake is therefore due forever unless archived.
- **Evidence:** `backend/app/services/review_item_service.py:11,36-40` (`INTERVALS={0:1,1:1,2:1,3:3,4:7,5:14}`, `item.repetitions+=1` unconditional); `backend/app/models/review_item.py:32-34` (`CheckConstraint("state IN ('active','paused')")`); `models/mistake.py:83-91` (no mastery column). Legacy "mastered" (`routers/review.py:70-73`) is unreachable via its own SM-2 route which always sets `next_review`.
- **Why It Matters:** Without a terminal state the loop cannot produce "I have learned this" — the core promise of the whole module.
- **Recommended Change:** Extend the scheduler contract: rating < 3 ⇒ reset `repetitions=0`, force next review ≤ 3 days; rating ≥ 3 ⇒ advance intervals (3/7/14/30…). Add `ReviewItem.state ∈ {active, mastered}` plus a migration; when an item reaches the graduation threshold (e.g. 3 consecutive ≥4 reviews after interval ≥30) set `state='mastered'` and stop surfacing it in the due queue (keep in history). Record the transition in `ReviewRecord`.
- **Expected Benefit:** Review queue becomes a real learning pipeline; dashboard "due" count shrinks as items graduate; foundation for R05 accuracy stats.
- **Implementation Complexity:** M
- **Priority:** P0
- **Affected Files:** `backend/app/models/review_item.py`, `backend/alembic/versions/027_*.py`, `backend/app/services/review_item_service.py`, `backend/app/schemas/review_item.py`, `src/lib/api/review-items.ts`, `src/app/manage/(workspace)/review/review-queue.tsx`
- **Verification Method:** New unit tests: rating 0/1/2 resets repetitions and shortens interval; 3 successful reviews graduate an item; graduated items absent from `due=true` but present in `records`; migration replay clean.

### R02 — Type-aware re-answer of mistakes (objective where possible, human-confirmed otherwise)
- **Category:** Mistake System / Learning Workflow
- **Current Problem:** After a Mistake exists, the only follow-up is a subjective 0–5 rating; there is no re-answer interaction. The existing `_is_correct` uses exact string equality for short answers and essays, so blindly reusing it would create false failures.
- **Evidence:** `Attempt.question_id` is question-only; the review UI is rating buttons only; `_is_correct` handles boolean/list specially but otherwise compares trimmed strings exactly (`attempt_service.py:16-25`); current DB Attempts = 0.
- **Why It Matters:** Subjective self-rating is the weakest signal in the loop; objective re-answer makes review data honest and enables per-KP accuracy (R05).
- **Recommended Change:** Add “重新作答” in `/manage/review`. Auto-grade single/multiple choice and true/false; for short answer/essay, show the reference answer after submission and require the learner to confirm correct/incorrect (AI may suggest, never decide). Write the outcome as an Attempt/review event and derive a suggested rating that the user can override.
- **Expected Benefit:** Honest re-mastery evidence without pretending free text can be graded by exact equality.
- **Implementation Complexity:** M
- **Priority:** P0
- **Affected Files:** `backend/app/schemas/attempt.py`, `backend/app/routers/attempts.py` (or review_items), `backend/app/services/attempt_service.py`, `src/lib/api/review-items.ts`, `review-queue.tsx`
- **Verification Method:** E2E: wrong multiple-choice re-answer shortens the interval; correct advances it; essay requires explicit human confirmation; case/format variants do not create false objective grades.

### R03 — Restore a working note/blog authoring entry (un-break the redirect self-loop)
- **Category:** Product / IA
- **Current Problem:** All `/write*` routes redirect to `/manage/dashboard` (`next.config.ts:46-52`); the notes context-menu "编辑" returns `/manage/dashboard` (`src/lib/content-routes.ts:8-12`); the workspace sidebar has no notes/blog authoring entry; yet the dashboard "快速开始" advertises 写笔记→`/write-note` and 写博客→`/write` (`dashboard-overview.tsx:100-129`). Result: **no reachable UI can create/edit a note or blog**, and two of the four quick actions bounce to the dashboard. A unit test pins the wrong href (`dashboard-overview.test.tsx:79`).
- **Evidence:** Current route/config reads show `/write`, `/write-note`, `/write-mistake`, and `/write-article` redirected to `/manage/dashboard`; `getContentEditHref` returns the same dashboard target; the current-run browser check confirms `/manage` reaches the auth boundary, while no sidebar or dashboard path reaches an editor.
- **Why It Matters:** Notes are the "record" stage of the learning loop; a system you cannot write into is not usable.
- **Recommended Change:** Choose one: (a) move the two editors under `/manage/write-note` and `/manage/write` (or a `/manage/notes` route) and point `getContentEditHref` and quick actions there; or (b) as an interim, remove the `/write*` redirects and fix quick-action targets. Remove the redirects only together with a reachable entry (never redirect to a dead target). Update the dashboard test to assert reachable, non-redirecting destinations.
- **Expected Benefit:** Unblocks daily content capture; quick actions actually work.
- **Implementation Complexity:** M
- **Priority:** P0
- **Affected Files:** `next.config.ts`, `src/lib/content-routes.ts`, `src/app/manage/(workspace)/dashboard/dashboard-overview.tsx` (+`.test.tsx`), `src/app/manage/components/manage-sidebar.tsx`
- **Verification Method:** Browser/robot: navigate dashboard → 写笔记 → type & save → note appears in `/notes`; edit from `/notes` opens an editor. Unit tests assert quick-action links resolve to non-redirected pages.

### R04 — Make the mistakes/weak-point public surfaces read canonical data, then retire legacy chain
- **Category:** Mistake System / IA / Database
- **Current Problem:** Public `/mistakes` list reads `Note.type='mistake'`; admin weak-point/plan cards call legacy `/api/review/*` and `/api/knowledge/weak-points` which parse free-text `knowledge_points` off legacy Notes. Canonical `Mistake`/`ReviewItem` data never reaches these surfaces, so dashboard and public stats can disagree and new canonical mistakes are invisible to the public page.
- **Evidence:** `src/app/mistakes/page.tsx:27-41` (list + legacy stats/plan), `src/hooks/use-note-index.ts` (→ `/api/notes`), `routers/review.py` (Note-based), `knowledge_retrieval.retrieve_weak_points` (`Note.type=="mistake"`, text split), `knowledge.py:118-141`; canonical domain only served under `/api/admin/*`.
- **Why It Matters:** One user, one truth. Fragmentation makes every future feature cost double.
- **Recommended Change:** Add a canonical "mistake showcase" query (published + `visibility` intent) and switch the public page + weak-point/plan UI to it; add a curated export concept (which canonical mistakes to publish) so the public 错题集 stays meaningful; record a migration decision for the 5 existing published legacy notes; then remove `/api/review/*`, `sm2.py`, `review_planner.py`, legacy `knowledge_retrieval` and the `/mistakes/review` page + redirect.
- **Expected Benefit:** Removes the two-source contradiction, retires ~4 services/router pair, halves future mistake work.
- **Implementation Complexity:** L
- **Priority:** P0
- **Affected Files:** `routers/{review,knowledge}.py`, `services/{sm2,review_planner,knowledge_retrieval,legacy_note_migration_adapter}.py` (final), new canonical public mistakes router, `src/app/mistakes/**`, `src/lib/api/{review.ts,review-items.ts}`, `next.config.ts`
- **Verification Method:** After cutover the public page, dashboard, and `/manage/review` all derive from `mistakes/review_items`; zero references to `/api/review`; 5 legacy notes preserved as curated public items.

### R05 — Per-knowledge-point accuracy analytics to power dashboard weak points
- **Category:** Feedback / Data / Backend
- **Current Problem:** The dashboard shows counts but no weakness signal; the only weak-point UI parses legacy note text instead of actual mistake/review records.
- **Evidence:** `dashboard_service.py:43-77` (counts/recent only; no aggregation), `dashboard.py` schema has no weak-point field; `knowledge_retrieval.py:247-311` text-parsing path is legacy-only and unused by dashboard.
- **Why It Matters:** "我哪里最薄弱" is the highest-value learning question, and the data to answer it now exists (QKP links + attempts + review records + reason_category).
- **Recommended Change:** Add a service that joins `review_records/attempts → review_items → mistakes → question_knowledge_points → knowledge_points` and returns per-KP: mistake count, review count, mean rating, wrong-again rate, due count. Expose as an extension of `GET /api/admin/dashboard/summary` (or `/api/admin/dashboard/weak-points`) and render a weak-point list in the 学习反馈 area; order by severity = recent wrong-again × due.
- **Expected Benefit:** The dashboard finally answers the learner's core question using trusted structured data.
- **Implementation Complexity:** M
- **Priority:** P0
- **Affected Files:** new `services/analytics_service.py` (or extend dashboard_service), `schemas/dashboard.py`, `routers/dashboard.py`, `src/lib/api/dashboard.ts`, `dashboard-overview.tsx`
- **Verification Method:** Insert fixtures (mistake on KP A with low ratings, KP B clean) → dashboard weak-point list ranks A first; SQL single-statement counts match unit expectations.

---

### R31 — Make frontend releases artifact-atomic and add a post-start chunk smoke test
- **Category:** Engineering / Frontend / Reliability
- **Current Problem:** The current long-running server on port 2025 returns HTML 200 while 8 of 16 referenced static assets return 404 at the final 2026-09-03 re-check (7 JavaScript chunks and 1 CSS asset); Home is blank and Notes/Auth remain loading. A fresh build and fresh server from the same source render correctly.
- **Evidence:** Current-run curl of the HTML's chunk URLs plus `runtime-existing-home-blank.png`; fresh build PASS plus `runtime-fresh-connected-home.png` and real Notes data.
- **Why It Matters:** This is the highest-severity present usability failure: a healthy process and 200 response still deliver no application.
- **Recommended Change:** Never replace the `.next` directory underneath a running server. Build into an immutable release directory, start the new process against that release, verify HTML plus every referenced first-load chunk, then switch traffic and retire the old process. Add the same chunk check to local start/deploy runbooks and CI smoke.
- **Expected Benefit:** Eliminates split HTML/manifest/chunk deployments and detects blank-page releases before use.
- **Implementation Complexity:** M
- **Priority:** P0
- **Affected Files:** deployment/start scripts, `.github/workflows/ci.yml`, OpenNext/predeploy checks, operational runbook
- **Verification Method:** On a fresh release, fetch `/`, parse all first-load chunk URLs, assert every one is 200, then load `/`, `/notes`, and `/manage` in a browser. Rebuilding another release must not break the still-running old release.

---

## P1 — Complete the loop and close verified operational gaps (Tier A/B)

### R06 — Bind notes (and blogs) to KnowledgePoints
- **Category:** Knowledge System
- **Current Problem:** The KP tree is the formal knowledge structure, but notes are linked only via tags/folders; `KnowledgePointLink` is never written for notes (dev DB targets: `question`, `question_draft` only).
- **Evidence:** `write-note` editor has no KP control (verified no `KnowledgePointSelect` outside `/manage`); `models/taxonomy.py:75-77` target_type free string; DB group-by of `knowledge_point_links` = question/question_draft only.
- **Why It Matters:** The "record" and "knowledge" stages never connect, so a KP cannot show its notes and review feedback cannot point back to the source note.
- **Recommended Change:** Add KP multi-select to the note/blog editor and save via `KnowledgePointLink(target_type='note')` (or a proper `note_knowledge_points` table); show a note's KPs on `/notes/[id]`; later feed R05/R26.
- **Expected Benefit:** Notes become part of the knowledge structure; weakest link of the chain repaired.
- **Implementation Complexity:** M
- **Priority:** P1
- **Affected Files:** `schemas/note.py`, `routers/notes.py` (or `knowledge.py`), `services/knowledge_markdown_service.py`, `write-note` editor, `src/app/notes/[id]`
- **Verification Method:** Saving a note with 2 KPs writes links (FK-checked); KP detail lists that note; deleting the note cascades cleanly.

### R07 — Attempt-derived drafts: prefill reason, dedupe existing review items, quick-triage UX
- **Category:** Mistake System / AI
- **Current Problem:** A wrong attempt auto-creates a MistakeDraft with `reason_category='unknown'` and no `mistake_reason`, forcing full manual re-entry; and re-answering an already-converted question wrong creates another draft instead of linking to the existing active ReviewItem.
- **Evidence:** `attempt_service.create_mistake_draft_for_attempt` builds `MistakeDraftCreate(question_id, my_answer, difficulty)` without reason (`services/attempt_service.py:47-70`); `models/mistake.py:50-52` default `'unknown'`.
- **Why It Matters:** The draft is the friction point between "I got it wrong" and "it enters review"; low friction here makes the whole system actually used.
- **Recommended Change:** If an active ReviewItem exists for this question, mark the new attempt against it (record wrong-again) instead of a new draft; when creating a draft, run the lightweight AI error-interpretation to prefill category+reason (fallback: user quick-pick), and surface the draft with a "确认并入库" one-click.
- **Expected Benefit:** Wrong answers flow to review in one click with a real reason; duplicate review items disappear.
- **Implementation Complexity:** M
- **Priority:** P1
- **Affected Files:** `services/attempt_service.py`, `services/mistake_service.py`, `ai_prompt_registry.py` (+ existing staged endpoints), `draft-workspace.tsx`
- **Verification Method:** Unit: second wrong attempt on a mastered-reviewed question increments the same ReviewItem rather than creating a draft. Browser: wrong answer ⇒ draft arrives with prefilled reason ⇒ one-click convert.

### R08 — Attempts history & per-question statistics API
- **Category:** Backend / Learning Workflow
- **Current Problem:** Attempts are write-only (single POST router, no read endpoint), so past answers can't feed analytics or a question-level "我上次错在哪".
- **Evidence:** `routers/attempts.py` contains only `POST /api/admin/attempts`.
- **Why It Matters:** Attempt history is the ground truth for R05 and for the practice stage (R09).
- **Recommended Change:** Add `GET /api/admin/attempts?question_id=&page=&size=` returning graded history incl. `is_correct`, `submitted_answer`, and the linked mistake draft id when present.
- **Expected Benefit:** Enables question detail "作答记录", R05 accuracy, and honest practice feedback.
- **Implementation Complexity:** S
- **Priority:** P1
- **Affected Files:** `routers/attempts.py`, `schemas/attempt.py`, `src/lib/api/attempts.ts`, `question-editor.tsx`
- **Verification Method:** Unit/route test on filtered pagination; UI shows prior attempts on the question editor.

### R09 — Minimal daily practice surface ("今日练习")
- **Category:** Product / Learning Workflow
- **Current Problem:** The loop's "practice" stage has no daily surface; attempts only exist as an in-editor self-check, so a learner can review but never practices new/unmastered questions.
- **Evidence:** only `question-editor.tsx:125-154` "作答验证"; dev DB attempts = 0.
- **Why It Matters:** Practice is where new mistakes are generated; without it the mistake/review modules starve.
- **Recommended Change:** In `/manage/review` (or a new `/manage/practice`), add a "练几题" mode: pick N questions (exclude those with an active ReviewItem or mastered state; optionally filter by weak KP from R05), reuse the attempt submission + instant grade, wrong ⇒ auto-draft (R07).
- **Expected Benefit:** Completes input→practice→mistake→review loop as a daily routine.
- **Implementation Complexity:** M
- **Priority:** P1
- **Affected Files:** new page or `review-queue.tsx`, `src/lib/api/questions.ts` (batch query), reuse attempts
- **Verification Method:** Daily session of N questions produces Attempt rows and, on wrong answers, drafts; session summary shown.

### R10 — Capture/OCR reliability and failure visibility
- **Category:** AI / Operations
- **Current Problem:** OCR is the flagship intake path but flaky: dev DB `ai_runs` shows 31 failed `capture_recognition` and `capture_items` has 0 rows; failures surface only as inline error codes.
- **Evidence:** DB query results; `capture_service.trigger_recognition` (`:172-230`) retries `attempt_count`, stores sanitized error; `ai_gateway` fallback exists.
- **Why It Matters:** A capture path that usually fails silently is worse than a manual form; intake is the first stage of the whole loop.
- **Recommended Change:** First verify current model/provider config (vision model reachable, image size/format limits); then (a) add automatic provider retry with a second vision model, (b) make failed captures visible in the drafts/capture list with the stored error + "重试", (c) add a small health metric (recent OCR success rate) to `/manage/capture`.
- **Expected Benefit:** Converts a 31/31 failure history into reliable intake.
- **Implementation Complexity:** M
- **Priority:** P1
- **Affected Files:** `config.py`, `services/capture_recognition.py`, `routers/captures.py`, `capture-workspace.tsx`
- **Verification Method:** Manual capture of the same sample image succeeds twice in a row; failure retry path exercised by test; dashboard shows success rate.

### R11 — Govern the AI polish path (gateway + registry + validation)
- **Category:** AI
- **Current Problem:** The note/blog "polish" assistant uses an unversioned hard-coded `SYSTEM_PROMPTS` dict and streams directly via httpx, bypassing the run ledger and validators — the single AI feature that can rewrite user prose is the least governed.
- **Evidence:** `services/ai_polish_service.py:13-29` (14 hard-coded prompts), `routers/ai_polish.py:17-31` (direct stream, only `audit_action`), contrast with `ai_prompt_registry.py` v2 + `ai_gateway` used elsewhere.
- **Why It Matters:** It's the only AI path that touches user content with no audit, prompt version, or rollback record.
- **Recommended Change:** Route polish through `ai_gateway` with registry-registered, versioned prompts; record an AiRun (input summary + sanitized output); add lightweight validation (output non-empty, length bounds) — or, if too costly now, disable polish UI until governed.
- **Expected Benefit:** Consistent auditability; align with AGENTS.md "AI-generated content is not verified fact".
- **Implementation Complexity:** M
- **Priority:** P1
- **Affected Files:** `services/ai_polish_service.py`, `routers/ai_polish.py`, `ai_prompt_registry.py`, `ai_runs.py`
- **Verification Method:** Polish call creates an AiRun with prompt_version; unit asserts registry validation passes.

### R12 — Wire or remove dashboard/home count widgets; define "due today" consistently
- **Category:** Dashboard / UI
- **Current Problem:** Home `LearningSpaceCard` shows `—` "数量尚未接入"; dashboard "待复习" counts canonical due items while `/mistakes` admin cards count legacy notes — same user, two numbers.
- **Evidence:** `learning-space-card.tsx:12-33` (`meta:'—'`, aria "数量尚未接入"); `dashboard_service.py:49` canonical due vs `routers/review.py:79-85` legacy due.
- **Why It Matters:** A dashboard that shows unwired or contradictory numbers erodes trust in the learning feedback.
- **Recommended Change:** Wire LearningSpaceCard counts to `/api/admin/dashboard/summary` (due reviews + pending drafts) or remove the card; keep a single definition of "due today" (local-timezone end-of-day boundary) used by dashboard, review queue, and (post-R04) public stats; fix the `next_review_at` "new item is instantly due" default by scheduling new items for tomorrow or tagging them `new`.
- **Expected Benefit:** Consistent, honest numbers; "today" behaves like a day not a second.
- **Implementation Complexity:** M
- **Priority:** P1
- **Affected Files:** `learning-space-card.tsx`, `schemas/dashboard.py`, `services/review_item_service.py`, `review-queue.tsx`, `dashboard-overview.tsx`
- **Verification Method:** Home card and dashboard show same due count; a review submitted at 23:59 doesn't reappear immediately as due for the same day.

### R13 — Legacy console & dead-code removal (round 1)
- **Category:** Engineering
- **Current Problem:** Legacy `/manage` console (with `--` stats, FoldersTags placeholder, duplicate quick links to dashboard), orphan components, orphan API functions and a stale nav tag ("搜索 · 后续") inflate maintenance and confuse navigation.
- **Evidence:** `manage/page.tsx:286,293-294,306,685-691`; orphan list in §23 of the audit; `capability-state.ts:3-11` marks `search:'deferred'` while `/manage/search` is fully implemented.
- **Why It Matters:** Every orphan is a place where bugs and "which is the truth?" confusion live.
- **Recommended Change:** Remove source-only dead components/helpers after a final reference/build check; mark search capability active; retire legacy console tabs whose function exists in the workspace (keep auth/passkey/audit/guest moderation accessible). For apparently orphan HTTP endpoints (question PATCH, subject/category writes), first inspect access logs and document external ownership; deprecate before deletion rather than inferring safety from zero frontend callers.
- **Expected Benefit:** Smaller mental model; clearer nav.
- **Implementation Complexity:** M
- **Priority:** P1
- **Affected Files:** as listed + `src/lib/api/*.ts` cleanups + `capability-state.ts`
- **Verification Method:** repository references are zero for removed source symbols; endpoint candidates have a logged deprecation/consumer check; nav shows search as active; build+tests pass.

### R14 — Staged-mistake AI chain: wire end-to-end or remove
- **Category:** AI / Product
- **Current Problem:** The staged `/write-mistake` flow (AI question-draft → error-interpretation → final-analysis → diagram) saves through legacy `createNote(type:'mistake')` and its entry is now redirected to `/manage/capture`; several AI steps are stubs or produce unpersisted results, and AiRuns aren't linked to the final objects.
- **Evidence:** `staged-mistake-form.tsx:409-424` → `POST /api/notes`; `ai.py:487-497` confirm stub; staged endpoints don't set `target_type/target_id` on AiRun.
- **Why It Matters:** A full AI-assist pipeline is valuable only if its outcome lands in the canonical draft/review system; currently it writes to the legacy table being retired and half its steps don't persist.
- **Recommended Change:** Decision gate: either port the staged wizard's final save to `/api/admin/mistake-drafts` (via capture-style convert) and remove the legacy `/api/notes` write + redirect, or cut `/write-mistake` and its unused AI steps entirely. Prefer: keep the capture pipeline as the single staged-AI intake and remove the parallel staged flow.
- **Expected Benefit:** Removes the legacy write path & stub steps; all AI intake funnels through the governed canonical pipeline.
- **Implementation Complexity:** L
- **Priority:** P1
- **Affected Files:** `src/app/write-mistake/**`, `ai.py` staged endpoints, `notes.py` mistake-type writes, `next.config.ts`
- **Verification Method:** No UI/API writes `type:'mistake'` notes; staged endpoints removed or fully canonical; audit shows zero `/write-mistake` traffic.

---

### R32 — Put guest-message tables under a verified schema owner
- **Category:** Database / Backend
- **Current Problem:** `GuestMessage` and `GuestMessageBan` power mounted public/admin routes, but `models/registry.py` deliberately removes both tables from Alembic metadata. A clean 001→026 migration leaves both `to_regclass(...)` values null, while the current DB happens to contain 8 messages.
- **Evidence:** `backend/app/models/registry.py:1-90`; no migration creates either table; current-run isolated replay + read-only `to_regclass`; live DB row count.
- **Why It Matters:** A fresh or recovered environment can pass migration checks and still return database errors on the guestbook.
- **Recommended Change:** Make ownership explicit: preferably add an approved Alembic baseline migration for both tables; if policy requires an external owner, check in the provisioner and make startup/readiness fail with a precise missing-schema message. Add route tests against a freshly migrated DB.
- **Expected Benefit:** Reproducible install/restore and an honest readiness contract.
- **Implementation Complexity:** M
- **Priority:** P1
- **Affected Files:** `backend/app/models/registry.py`, new migration or explicit provisioning script, `backend/main.py` readiness, guest-message tests
- **Verification Method:** Empty Postgres → documented provision/migration → guest POST/GET/moderation tests pass; omitting the owner step produces a deliberate readiness failure, not a runtime 500.

### R33 — Make passkey challenges and login throttling multi-request safe
- **Category:** Security / Backend
- **Current Problem:** Registration/authentication challenges use process-local dicts keyed by the singleton `"current"` with no TTL; concurrent requests overwrite each other and multi-worker restarts lose state. Password login has no throttle. Guest rate limiting trusts the first `X-Forwarded-For` value without a verified proxy boundary.
- **Evidence:** `passkey_service.py:14-16,53-55,87-99,174-211`; auth password route has no limiter; `guest_messages.py` derives rate-limit identity from the untrusted forwarded header.
- **Why It Matters:** These are real authentication/abuse-control boundaries, even for a single-user system exposed on the public internet.
- **Recommended Change:** Key challenges by a random flow/session ID, store expiry and one-time use in the existing DB (or another already-operated shared store), add bounded password-login throttling, and accept forwarded client IP only from a configured trusted proxy; otherwise use the socket peer.
- **Expected Benefit:** Reliable passkey login across concurrency/restarts and harder brute-force/rate-limit bypass.
- **Implementation Complexity:** M
- **Priority:** P1
- **Affected Files:** `passkey_service.py`, auth schemas/routes, guest-message router, session/migration model, security tests
- **Verification Method:** Two simultaneous passkey flows cannot invalidate each other; expired/replayed challenges fail; repeated password failures are throttled; spoofed `X-Forwarded-For` from an untrusted peer does not change the rate-limit key.

### R34 — Resolve reachable dependency advisories and complete basic response/upload hardening
- **Category:** Security / Engineering
- **Current Problem:** `npm audit --omit=dev` reports 7 advisories (5 high, 2 moderate). Local frontend/backend responses expose framework/server headers and no common browser security headers were observed. Generic attachments validate declared MIME but not file signatures.
- **Evidence:** Current-run npm audit: `brace-expansion`, `glob`, `minimatch`, `nanoid`, `dompurify`, `undici`; local response headers; `attachment_service._validate_mime` checks metadata only, unlike managed-image routers' magic-byte checks.
- **Why It Matters:** Advisories and mislabeled files are not automatically exploitable, but leaving reachability unassessed makes security status unknowable; missing headers reduce defense in depth for rich Markdown/SVG rendering.
- **Recommended Change:** Trace each advisory to runtime/build-only usage, upgrade/override to a fixed compatible version after OpenNext regression tests, and document any accepted residual risk. Add CSP/referrer/content-type/permissions headers at the real deployment edge, disable `X-Powered-By`, and inspect magic bytes for uploaded types used by capture. Do **not** blindly apply npm's suggested OpenNext downgrade.
- **Expected Benefit:** Evidence-based dependency posture and stronger browser/upload boundaries without new infrastructure.
- **Implementation Complexity:** M
- **Priority:** P1
- **Affected Files:** `package.json`, lockfile, Next/deployment header config, attachment validation/tests
- **Verification Method:** `npm audit --omit=dev` has no unaccepted high finding; build/OpenNext smoke passes; production-like headers are asserted; a fake PNG declared as `image/png` is rejected.

---

## P2 — Consolidate & deepen (Tier B/C)

### R15 — Consolidate QuestionKnowledgePoint and KnowledgePointLink
- **Category:** Database
- **Current Problem:** The same fact (question ↔ KP) is written to two tables (`question_knowledge_points` + polymorphic `knowledge_point_links`), reads fall back from one to the other, and `role` is stored but never returned.
- **Evidence:** `question_service.py:105-120` dual inserts; `:192-219` QKP read with fallback; `QuestionOut` exposes only `knowledge_point_ids` (`schemas/question.py:319`); QKP role never read.
- **Why It Matters:** Dual-write invites drift and makes every future relation feature ambiguous.
- **Recommended Change:** Keep the typed `question_knowledge_points` for questions/mistakes and restrict generic `KnowledgePointLink` to non-question targets (or vice-versa); start returning `role` in question detail; add a migration guard removing stale duplicate links.
- **Expected Benefit:** Single source of truth for KP relations.
- **Implementation Complexity:** M
- **Priority:** P2
- **Affected Files:** `question_service.py`, `mistake_service.py`, `models/taxonomy.py`, migration `027`, `schemas/question.py`
- **Verification Method:** After backfill, both tables have identical question↔KP sets; writes keep them consistent; tests assert no divergence after 100 random ops.

### R16 — Search scope decision: keep notes-only, or add canonical entities
- **Category:** Search
- **Current Problem:** `/api/admin/search` only indexes `notes` (published, non-hidden) — questions, mistakes, and knowledge points are unsearchable; nav marks it deferred.
- **Evidence:** `knowledge_markdown_service.search_notes:68-82`; `search.py` router; only-note searchable set confirmed.
- **Why It Matters:** At single-user scale, plain SQL is right (keep FTS+trigram — no Elasticsearch/vector). But a search box that can't find your questions/KPs is half-useful.
- **Recommended Change:** Add lightweight `ILIKE`/FTS over `questions.question_text`, `mistakes.question_text`, and `knowledge_points.name` in the same admin endpoint with a `scope` param; keep implementation simple.
- **Expected Benefit:** Search becomes a true admin finder across the learning domain.
- **Implementation Complexity:** M
- **Priority:** P2
- **Affected Files:** `routers/search.py`, `schemas/search.py`, `search` page + `src/lib/api/search.ts`
- **Verification Method:** Queries return matching questions/mistakes/KPs with sensible ranking; index stays fast at <10k rows.

### R17 — Citation persistence decision (knowledge summaries)
- **Category:** AI / Database
- **Current Problem:** `knowledge_summary` returns citation blocks bound only in memory against the caller-supplied context pack; nothing is persisted, so a re-render or later review cannot trace "where did this claim come from".
- **Evidence:** citations exist only in `schemas/knowledge.py:8-41,118-143`; no DB table; `ai_analyze_service.parse_summary_blocks:274-331` downgrades unsupported to `ai_inference`.
- **Why It Matters:** The audit's own standard: `[1][2]` without a real relation is an incomplete citation system. Decide persistence or presentation honesty.
- **Recommended Change:** Either (a) persist summary blocks with source bindings (add `ai_summary_blocks` referencing source note/attachment + text anchor) when summaries are saved to a KP or note, or (b) drop the citation framing and label outputs "AI 推断，未附来源". Do (b) immediately if not persisting.
- **Expected Benefit:** No misleading provenance; groundwork for trustworthy AI note drafting.
- **Implementation Complexity:** M
- **Priority:** P2
- **Affected Files:** `schemas/knowledge.py`, `services/ai_analyze_service.py`, frontend summary panel
- **Verification Method:** If (a): a saved summary block links to a DB source row. If (b): UI shows inference disclaimer and no citation glyphs.

### R18 — Show source provenance on mistake & question detail
- **Category:** Product / Mistake System
- **Current Problem:** `QuestionSource` (book/exam/note/url + refs) and capture attachment links exist but are not surfaced on the mistake/question detail pages, so the origin ("from textbook p.88 / from this photo") is invisible where it would help re-study.
- **Evidence:** `models/question.py:180-202`; `models/attachment.py:68-103` link purposes `source/ai_input/ai_output`; mistake detail UI (`mistake-detail.tsx`) shows no source block.
- **Why It Matters:** Source context improves re-study and is the honest grounding for review.
- **Recommended Change:** Render a small 来源 card on `/manage/mistakes/{id}` and `/manage/questions/{id}` showing QuestionSource fields + linked original image attachment.
- **Expected Benefit:** Mistakes carry their context; images stay reachable from review.
- **Implementation Complexity:** S
- **Priority:** P2
- **Affected Files:** `schemas/mistake.py`/`mistake_service.py` (include sources), `mistake-detail.tsx`, `question-editor.tsx`
- **Verification Method:** A captured-from-image mistake shows its photo link on detail.

### R19 — First-run & empty-state guidance through the loop
- **Category:** UX / Product
- **Current Problem:** Empty states tell you to add items but not how the stages connect (科目→知识点→题目→错题→复习), so a new user doesn't know what "record a mistake" should start from.
- **Evidence:** `EmptyState` variants (`empty-state.tsx`); dashboard deterministic start hint "从新建题目开始" (`dashboard-overview.tsx:85-90`).
- **Why It Matters:** The loop's value appears only when a user internalizes the intended path.
- **Recommended Change:** Add a compact first-run checklist card on empty dashboard (建科目 → 加知识点 → 录题目 → 练几题) that hides as data arrives; link each empty state to the correct next action.
- **Expected Benefit:** New users reach the working loop in one session.
- **Implementation Complexity:** S
- **Priority:** P2
- **Affected Files:** `dashboard-overview.tsx`, `empty-state.tsx`
- **Verification Method:** Fresh DB shows checklist; adding one question removes the top item; manual click-through.

### R20 — Canonical review plan card (7-day forecast)
- **Category:** Product / Review System
- **Current Problem:** The `/mistakes` page (admin) still shows a plan card computed from legacy notes by `review_planner.build_review_plan`; no canonical equivalent exists, so post-R04 this card has nothing to read.
- **Evidence:** `review_planner.py` (legacy Note inputs), `/api/review/plan`; no `/api/admin/review/plan`.
- **Why It Matters:** "What's coming this week" supports planning; it should come from the canonical queue.
- **Recommended Change:** Implement a small forecast endpoint over `review_items` (due today/this week/next, per subject) and render it in `/manage/review`.
- **Expected Benefit:** Replaces the legacy card with canonical truth (ties into R04).
- **Implementation Complexity:** M
- **Priority:** P2
- **Affected Files:** `services/review_item_service.py`, new endpoint, `review` page
- **Verification Method:** Forecast numbers equal a manual SQL of due items per bucket.

### R21 — API/REST consistency cleanup
- **Category:** Backend
- **Current Problem:** Delete semantics differ across routers (soft-archive returns entity with 200; hard-delete returns 204), question PATCH is orphaned while PUT holds the "legacy" shape, and drafts router rejects non-question types by 400.
- **Evidence:** `admin_mistakes.py` DELETE → archive 200; `knowledge_points.py` DELETE → 204; `categories.py` writes orphaned; `questions.py` PUT (legacy) vs PATCH (canonical) with only PUT used.
- **Why It Matters:** Consistent contracts reduce client bugs; orphan endpoints mislead future work.
- **Recommended Change:** Standardize: archive operations return the updated entity with explicit 200 (already the pattern), destructive deletes return 204; delete orphaned endpoints or document them; converge question PUT/PATCH to one canonical shape used by the editor.
- **Expected Benefit:** Predictable API; fewer duplicate client paths.
- **Implementation Complexity:** M
- **Priority:** P2
- **Affected Files:** `questions.py`, `admin_mistakes.py`, `subjects.py`, `categories.py`, clients
- **Verification Method:** Route-contract tests (like `test_mistake_routes.py`) enumerate method→status expectations.

### R22 — Complete CI & test coverage of the mastery loop
- **Category:** Testing
- **Current Problem:** CI runs frontend `tsc`+`build` and backend `pytest` only; Vitest (374 tests) and `test:typecheck` never run in CI, and there are no tests for review mastery semantics (R01).
- **Evidence:** `.github/workflows/ci.yml`; `package.json` scripts `test`/`test:typecheck`; `review_item_service` tests absent for lapse/mastery.
- **Why It Matters:** The review semantics are the core product behavior; regressions there are silent today.
- **Recommended Change:** Add `npm test` and `npm run test:typecheck` steps to the frontend CI job; add backend unit tests for the R01/R02 contracts.
- **Expected Benefit:** The most important behavior gets enforced on every PR.
- **Implementation Complexity:** S
- **Priority:** P2
- **Affected Files:** `.github/workflows/ci.yml`, `review_item_service` tests
- **Verification Method:** CI turns red when a mastery test fails.

---

## P3 — Polish & debt reduction (Tier C)

### R23 — Add honest request-state primitives, then consolidate form primitives
- **Category:** Frontend / Design System
- **Current Problem:** Public pages do not represent request failure honestly: Notes computes an error state but renders no branch; Blog and Mistakes discard the hook error and can show “还没有内容”. Separately, workspace control markup and reason/status labels are duplicated.
- **Evidence:** `notes/page.tsx:180,288-300`; `blog/page.tsx:27,442`; `mistakes/page.tsx:27,205-215`; no route `error.tsx`/`loading.tsx`; 41 repeated input-class literals, 48 raw workspace buttons, and label maps in 4+ files.
- **Why It Matters:** Empty content and an outage require different user decisions. A shared state contract prevents this factual UX error and also reduces visual drift.
- **Recommended Change:** First add one shared `AsyncStatePanel` (loading/empty/error/retry) and use it on Notes/Blog/Mistakes plus route-level boundaries. Then add only the small form primitives and centralized label maps demonstrated by repeated usage; do not build a large design-system package.
- **Expected Benefit:** Failures become diagnosable and retryable; common controls and labels become consistent.
- **Implementation Complexity:** L
- **Priority:** P3
- **Affected Files:** `src/components/`, public list pages, `src/app/**/error.tsx`, `src/app/manage/components/`, workspace pages
- **Verification Method:** Force the API offline: all three public lists show “加载失败” + Retry and never “还没有…”. Existing empty fixtures still show empty states. Targeted visual and accessibility tests pass.

### R24 — Mobile pass for review & capture
- **Category:** UI/UX
- **Current Problem:** Review queue and capture workspace are dense desktop grids; no mobile-specific evidence of optimization.
- **Evidence:** `review-queue.tsx`, `capture-workspace.tsx` desktop-first classes.
- **Why It Matters:** Real learners photograph mistakes from a phone; a weak mobile capture flow undercuts the flagship intake.
- **Recommended Change:** Audit capture upload + draft editing and review submission on ≤390px viewports; fix tap targets, sheet vs grid layout.
- **Expected Benefit:** Intake from the phone becomes dependable.
- **Implementation Complexity:** M
- **Priority:** P3
- **Affected Files:** capture/review workspace styles
- **Verification Method:** Browser resize smoke test at 390px; capture-and-review from mobile emulation.

### R25 — Note version history & wikilink UX
- **Category:** Product / Notes
- **Current Problem:** `NoteVersion` snapshots + `/notes/{slug}/versions` exist but dev DB shows 0 versions and there is no version-picker UI in the (currently broken) editor; backlink support (wikilinks) has no authoring affordance.
- **Evidence:** DB counts (note_versions=0, note_links=0); `knowledge_markdown_service.py:24-40`; no editor version UI found.
- **Why It Matters:** Once authoring returns (R03), version history and wikilinks are the note module's differentiation; without UI they're dead weight.
- **Recommended Change:** Add a version drawer ("历史版本 / 恢复") and a wikilink helper in the note editor once R03 lands.
- **Expected Benefit:** Note system becomes genuinely versioned and cross-linked.
- **Implementation Complexity:** M
- **Priority:** P3
- **Affected Files:** editor components, `src/lib/api/notes.ts`
- **Verification Method:** Edit a note twice → 3 versions; restore works; `[[slug]]` link auto-registers backlink.

### R26 — KP hub page (linked notes/questions/mistakes + accuracy)
- **Category:** Knowledge System
- **Current Problem:** `/manage/knowledge-points/[id]` is edit-focused; nothing shows "this point's notes, questions, mistakes, accuracy".
- **Evidence:** `knowledge-point-editor.tsx` scope; QKP + links data unaggregated.
- **Why It Matters:** After R05/R06 the KP page becomes the natural "go study this point" destination.
- **Recommended Change:** Extend the KP page with tabs: 关联笔记 / 相关题目 / 相关错题 / 掌握情况(from R05) — depends on R05/R06 data.
- **Expected Benefit:** Turns the taxonomy into a study organ per topic.
- **Implementation Complexity:** M
- **Priority:** P3
- **Affected Files:** `knowledge-points/[id]/page.tsx`, schema additions
- **Verification Method:** KP with linked content shows all tabs populated.

### R27 — Public mistake exposure policy & redaction
- **Category:** Security / Product
- **Current Problem:** Public published legacy mistake notes return full `NoteOut` (question, correct_answer, analysis) to guests via `/api/notes/{slug}`; there is no per-row decision about exposing answers.
- **Evidence:** `routers/notes.py:216-235` (public detail returns full NoteOut).
- **Why It Matters:** "Publishing mistakes" may intentionally show answers, but the system should make that a deliberate, reviewable choice rather than an implicit one.
- **Recommended Change:** Decide a policy (answers public vs hidden) and encode it: e.g., a `mistakes` public showcase (R04) exposes question + analysis but hides "my wrong answer" unless admin.
- **Expected Benefit:** Clear privacy boundary for a personal system.
- **Implementation Complexity:** S
- **Priority:** P3
- **Affected Files:** `schemas/note.py`/public notes router, `src/app/mistakes/**`
- **Verification Method:** Guest sees policy-respecting fields only; admin unchanged.

### R28 — Re-scope analytics/jobs menu or build thin real pages
- **Category:** Product / IA
- **Current Problem:** `/manage/analytics` and `/manage/jobs` render the same `GovernanceOverview` as the governance page, while the sidebar implies future dedicated tools.
- **Evidence:** `analytics/page.tsx:4` and `jobs/page.tsx:4` → `<GovernanceOverview/>`.
- **Why It Matters:** Mislabeled menu items create false expectations.
- **Recommended Change:** Either remove jobs/analytics from nav until real pages exist (keep 治理), or rename to 系统治理 and show R05-derived learning trends when available.
- **Expected Benefit:** Honest IA.
- **Implementation Complexity:** S
- **Priority:** P3
- **Affected Files:** `manage-sidebar.tsx`, `capability-state.ts`
- **Verification Method:** Nav matches implemented pages.

### R29 — Defer weekly trend charts until outcome events are trustworthy
- **Category:** Dashboard / Product
- **Current Problem:** A trend chart is tempting, but current Attempts = 0, review semantics cannot graduate items, and activity is split between canonical and legacy sources; a chart now would be decorative rather than decision-grade.
- **Evidence:** Current DB counts and dashboard service; ECharts is currently only a Markdown content renderer, not a learning analytics dependency.
- **Why It Matters:** Building analytics before trustworthy events wastes time and creates false confidence.
- **Recommended Change:** **Do not build this in the current 30-day scope.** Revisit only after R01–R05 have produced at least four weeks of canonical Attempt/Review events. If justified, start with a plain 14-day bar/list rather than a new chart framework.
- **Expected Benefit:** Avoids premature dashboard work while preserving a low-cost future path.
- **Implementation Complexity:** M
- **Priority:** P3
- **Affected Files:** `dashboard_service.py`, `dashboard-overview.tsx`
- **Verification Method:** Current roadmap contains no trend implementation; later go/no-go requires four weeks of canonical event data and a concrete learner decision the view will change.

### R30 — Update project truth documents
- **Category:** Engineering
- **Current Problem:** Root README/audit docs describe flows (write editors, JWT naming, note-as-mistake review) that the redirect cutover and canonical system have superseded; `README.md` still calls the auth secret `JWT_SECRET_KEY` for session signing and describes `/write*` as normal usage.
- **Evidence:** `README.md:116-127,154-166`; legacy flow docs in root (`SYSTEM_AUDIT_REPORT.md`, etc.); `content-routes.ts` comment contradicts reachable routes.
- **Why It Matters:** Documentation is the map newcomers and future agents use; today it points at dead paths.
- **Recommended Change:** After R03/R04 settle the intended flows, update README (authoring entry, canonical mistake pipeline, review semantics) and archive superseded root audit docs.
- **Expected Benefit:** Repository documents reality.
- **Implementation Complexity:** S
- **Priority:** P3
- **Affected Files:** `README.md`, root audit `.md` files
- **Verification Method:** Link/file existence checks; README commands reproduce flows.

### R35 — Do not build autonomous publishing, social export, graph/vector infrastructure, or FSRS yet
- **Category:** Product / AI / Engineering
- **Current Problem:** The core loop and operational contract have verified gaps, while advanced ideas would add new data contracts and maintenance. No implemented `mistake_social_export` or `knowledge_article` task type was found in the current repository.
- **Evidence:** Attempts/Captures = 0; review has no mastery; canonical and legacy data disagree; current runtime/guest-schema gaps; repository searches for those two task names returned no implementation.
- **Why It Matters:** These features have low present frequency and cannot improve the broken practice→mastery path.
- **Recommended Change:** Freeze FSRS, vector search, knowledge-graph visualization/database, autonomous `knowledge_article` publishing, mistake social export, background jobs/queues, gamification, and new decorative public modules. Reconsider one item only after the A-tier loop is used for at least four weeks and a measured bottleneck names it.
- **Expected Benefit:** Protects the 30-day budget for high-frequency learning value and reduces maintenance risk.
- **Implementation Complexity:** XL
- **Priority:** P3
- **Affected Files:** none now; record the defer decision in the approved roadmap/backlog only
- **Verification Method:** No new route/model/task/dependency for these capabilities enters the 30-day implementation scope; any later proposal includes usage evidence and a smaller experiment first.

---

## Backlog by tier

| Tier | Items |
|---|---|
| **A — Now** | R31, R03, R01, R02, R04, R05 |
| **B — Next** | R06–R14, R32, R33, R34 |
| **C — Later** | R15–R28, R30 |
| **D — Do Not Build Yet** | R29, R35 |

## P0–P3 summary

| Priority | Items |
|---|---|
| P0 | R01 · R02 · R03 · R04 · R05 · R31 |
| P1 | R06–R14 · R32 · R33 · R34 |
| P2 | R15–R22 |
| P3 | R23–R30 · R35 |
