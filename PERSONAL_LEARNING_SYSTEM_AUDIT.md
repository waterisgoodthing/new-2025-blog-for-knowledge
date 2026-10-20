# PERSONAL LEARNING SYSTEM AUDIT

> 文档治理（2026-10-09）：历史审计/建议快照保留。测试、版本、缺陷与权限描述只对应报告原时点；本轮重新核验结果以当前审查和状态为准，不覆盖原裁定。 当前入口见 [文档索引](docs/DOCUMENTATION_INDEX.md)。

**Audit scope:** `2025-blog-public` @ `refactor/baseline` (HEAD `4a954ea`)
**Audit type:** Read-only, evidence-driven. No application code or existing data modified; only the two requested report files were created.
**Audit run:** 2026-09-02—2026-09-03
**Primary Owner:** Principal Software Architect. Product, learning-system, full-stack, security, and UI/UX checks are perspective passes by the same auditor, not independent reviews.
**Auditor inputs:** first-hand file reads, current-run in-app-browser screenshots, safe executions (`tsc`, Vitest, `pytest` on an isolated throwaway Postgres, `next build`, `npm audit`) and read-only SQL against the local development database.

---

## 1. Executive Summary

This repository is a single-user "personal learning space" that has grown far beyond a blog. It contains a genuinely engineered, second-generation **learning domain** — `Subject → KnowledgePoint (tree) → Question → Attempt → MistakeDraft → Mistake → ReviewItem → ReviewRecord` — with a clean FastAPI layering, typed session auth, versioned and validated AI prompts, and an admin workspace UI that is real, not decorative.

The dominant finding is **fragmentation**: the product lives on two parallel generations of the same concepts.

1. **Legacy generation (still live):** `notes` is one polymorphic table. `Note.type ∈ {note, blog, mistake}`. Mistakes are notes carrying SM-2 fields (`ef/interval/repetitions/next_review`), free-text `knowledge_points`, and `tags`. Public pages `/blog`, `/notes`, `/mistakes`, review queue `/mistakes/review`, AI context/weak-point retrieval (`knowledge_retrieval.py`, `review_planner.py`) all operate on this table.
2. **Canonical generation (the workspace):** formal `Question`/`Mistake`/`ReviewItem` with drafts, capture (OCR/AI), concurrency-safe review, `Subject`/`KnowledgePoint` taxonomy, `/manage/*`.

The canonical **draft→mistake→review** sub-chain is populated (3 mistakes, 3 review items, 4 review records), but the whole practice loop is not demonstrated: all 3 questions are archived, Attempts = 0, and Captures = 0. The **learning loop is not closed**:

- No **mastery / graduation** exists anywhere. `ReviewItem.state` is constrained to `active|paused`; rating 0–2 never resets repetitions; `Mistake` has no proficiency column; legacy "mastered" is unreachable by its own SM-2 route.
- No **objective re-answer** from a Mistake. Once a mistake exists the only follow-up is a 0–5 self-rating; `Attempt` only exists against `Question`.
- **Practice is vestigial**: attempts exist only as an in-editor self-check; the dev DB has 0 attempts.
- **Content (notes) never binds to the KnowledgePoint tree.** Notes use tags/folders/categories; only questions/mistakes/drafts are KP-linked.
- **Feedback/weak points are computed from legacy text** (parsing comma-delimited `knowledge_points` strings), not from canonical Mistake/ReviewRecord joins.
- Public mistakes page and public weak-point/plan cards read legacy Note data while the dashboard reads canonical data — the same user can see two disagreeing "due today" numbers.
- **A UI regression exists today**: every `/write*` editor is redirected to `/manage/dashboard` (`next.config.ts:46-53`), and note/blog edit menus route to `/manage/dashboard` (`src/lib/content-routes.ts:8-12`) — but no replacement editor exists in the workspace. The dashboard "快速开始" still advertises 写笔记/写博客 (`dashboard-overview.tsx:100-129`), producing a self-loop. **As shipped, the user cannot create or edit a note/blog from any reachable UI.**

Two additional current-state failures materially change the verdict:

- The pre-existing server on port 2025 returned `200` HTML while **8 of its 16 referenced static assets returned `404`** at the final 2026-09-03 re-check (7 JavaScript chunks and 1 CSS asset), producing a blank home page and indefinitely loading Notes/Auth states. A fresh production build and a fresh server process rendered the same source and real local API data correctly. This is an **artifact/process consistency failure**, not a source-build failure.
- A clean Alembic replay reaches revision `026`, but it does **not** create `guest_messages` or `guest_message_bans`; those active runtime models are deliberately excluded from Alembic metadata and no separate provisioning contract was found. The current development DB has the tables, so the gap is hidden on an existing installation.

Engineering quality is high (constraints, FKs, indexes, optimistic concurrency, validation, graceful degradation, 786 passing tests). The cost is real over-engineering for a single user: a DB-level legacy-migration ledger with security-definer functions and five DB roles (`alembic/versions/026`), dozens of orphan API functions/pages, two review schedulers (SM-2 *and* fixed interval), and hundreds of governance documents.

**Verdict:** `MVP`. Engineering maturity is higher than product maturity: the second-generation domain is well tested, but the primary loop cannot yet demonstrate practice→mistake→re-answer→mastery, authoring is unreachable, the current long-running frontend is broken, and a fresh schema cannot provision every active feature.

---

## 2. Final Score

**61 / 100**

| Dimension | Weight | Score | Key deductions |
|---|---|---|---|
| 产品定位与学习闭环 | 15 | 8.0 | Loop runs to self-rated review but never to mastery/graduation; practice stage absent as daily activity; fragmented data across two generations. |
| 知识系统 | 12 | 6.0 | Subject/KP tree + tree API real; but notes/blogs never KP-linked; QKP `role`/prereq is write-only; weak points derived from text not structure; no graph (correctly deferred). |
| 错题与复习系统 | 15 | 8.5 | Draft→convert→review-item chain is high quality & concurrency-safe; but no lapse reset, no graduated state, no type-aware re-answer, duplicate legacy SM-2 review still live. |
| 数据模型 | 10 | 6.5 | Constraints/FKs/indexes strong and the owned migration chain replays to 026. Deductions: dual KP modeling, polymorphic legacy `notes`, untyped JSON content, and active guest-message tables outside the verified schema lifecycle. |
| UI/UX | 10 | 5.5 | Fresh public pages render and the workspace shell is coherent; but authoring is unreachable, request failures collapse into blank/empty states, the current 2025 runtime is blank, and 1280px captures leave most of the canvas unused. |
| 前端工程 | 8 | 5.5 | Typed API layer, clean SWR patterns, low `any` in workspace; but no primitive layer (41× duplicated input class, 48 raw `<button>`), orphan code, dual-shaped `Question` DTO, dashboard test locks in a self-loop bug, vitest absent from CI. |
| 后端工程 | 8 | 6.0 | Router→service layering, error mapping and optimistic concurrency are strong; deductions for two schedulers, orphan endpoints, the guest-schema lifecycle gap, and the heavy `026` ledger contract. |
| AI Integration | 6 | 3.5 | Prompt registry v2 + Pydantic validation + AiRun governance real; but polish is ungoverned (no registry/run log), OCR flaky (31 failed `capture_recognition` runs), many outputs never persist, `question-draft/confirm` is a stub, citations are schema-only. |
| 测试 | 6 | 5.0 | 412 backend + 374 frontend tests pass; good domain coverage. Deductions: vitest & Playwright specs not in CI; no tests on mastery semantics (feature absent). |
| 安全 | 4 | 2.5 | Session auth and renderer defenses are sound, but current `npm audit --omit=dev` reports 7 advisories (5 high), password login has no rate limit, passkey challenges are process-local singleton values, proxy IP trust is weak, generic attachments trust declared MIME, and no application security headers were observed locally. |
| 性能 | 2 | 1.5 | Correct scale; trivial dashboard queries; FTS computed per request acceptable at 13 notes. |
| 可维护性 | 4 | 2.5 | Heavy process/doc overhead, legacy+canonical duplication, orphan endpoints/components; partially offset by disciplined structure. |

---

## 3. Maturity Level

**MVP** (engineering maturity approaches `MATURE MVP`, product/runtime maturity does not).

Evidence for mature engineering inside the MVP:
- Second-generation domain is fully typed, constrained at DB level, concurrency-safe, migration-consistent, and test-covered (412 backend tests pass on a fresh migration replay).
- Real AI governance (prompt registry with versions, validation, run ledger, human review).

Evidence against `MATURE MVP` / `BETA`:
- Mastery is not modeled; the loop cannot terminate a review item as learned.
- Practice surface is minimal; attempts = 0 in the working DB.
- The public/presentational layer still reads the legacy generation; two "review today" sources coexist.
- Note/blog authoring is currently unreachable from the UI.
- The user's genuine content has not migrated to the canonical domain (canonical rows in dev DB are predominantly `LT-*` migration-rehearsal fixtures).
- The current long-running frontend instance is unusable until restarted with a coherent build artifact; a fresh process works.
- A fresh owned-schema migration cannot provision the active guestbook tables.

---

## 4. Project Map

### 4.1 Project Map — Tech stack

| Layer | Choice | Evidence |
|---|---|---|
| Frontend | Next.js 16.2 App Router (React 19), `turbopack` dev, Tailwind v4, `motion`, lucide-react, swr, zustand (homepage/store only), sonner | `package.json` |
| Markdown render | `marked` + `html-react-parser` custom renderer (drops raw HTML, protocol allow-list); KaTeX math, Mermaid/markmap/chart blocks | `src/lib/markdown-renderer.ts`, `use-markdown-render.tsx` |
| Charts | echarts v6 (only inside `chart` fenced blocks of note/blog markdown) | `src/components/chart-block.tsx` |
| Backend | FastAPI, SQLAlchemy 2.0 async, Pydantic v2 | `backend/` |
| Database | PostgreSQL 16, asyncpg | `DATABASE_URL`, `ci.yml` |
| Migrations | Alembic linear chain `001→026` (two legacy files `0ec…`/`1119…` fold in early) | `backend/alembic/versions/`; `alembic current` = `026 (head)` |
| Auth | Stateful opaque HttpOnly cookie `admin_session` (hashed), password + optional WebAuthn passkey; optional session for reads | `models/session.py`, `routers/auth.py:119-130` |
| CSRF | None (SameSite=Lax + cookie `path=/api` only) | `routers/auth.py:40-58` |
| Search | Postgres FTS (`simple`) + `pg_trgm` similarity, computed at query time over `notes` only | `knowledge_markdown_service.search_notes:68-82` |
| Storage | Local disk (`backend/uploads` for attachments, `backend/public/images` for managed content) | `models/attachment.py`, `main.py:133-135` |
| AI | Multi-provider OpenAI-compatible gateway w/ fallback; DashScope vision (OCR), DeepSeek text; image gen for diagrams | `ai_gateway.py`, `ai_routing_policy.py`, `ai_prompt_registry.py` |
| Deployment | OpenNext/Cloudflare Workers (frontend) + backend; wrangler; static images in `public` | `wrangler.toml`, `open-next.config.ts`, `npm run deploy:*` |
| Testing | Backend: unittest+pytest (DB-backed). Frontend: Vitest + Testing Library (jsdom). 8 Playwright `.spec.ts` exist but are not in CI | `ci.yml`; `vitest.config.ts` |
| CI | GitHub Actions: frontend = `tsc --noEmit` + `next build`; backend = venv + `alembic upgrade head` + `pytest` on ephemeral Postgres 16. **vitest not run in CI** | `.github/workflows/ci.yml` |
| Lint | None configured (no ESLint config/script; prettier only) | `package.json` scripts |

### 4.2 Scale

Frontend `src`: ~40,800 LOC TS/TSX; Backend `app`: ~19,000 LOC Python; backend tests ~10,200 LOC; 34 routers; 47 services; 46 DB tables; 49 route `page.tsx` files.

### 4.3 Directory responsibilities

- `src/app/` — routes: public pages (`(home)`, `/blog`, `/notes`, `/mistakes`, `/discover`, `/music`, …), authoring pages (`/write*`, now redirecting), workspace (`/manage/(workspace)/*`) and legacy `/manage` console.
- `src/components/`, `src/hooks/`, `src/layout/`, `src/lib/` — shared UI, hooks, layout, API clients + markdown renderer.
- `src/lib/api/` — 31 typed API client modules over one `client.ts` fetch wrapper (`credentials:'include'`).
- `backend/app/{routers,schemas,services,models}/` — standard layering; `utils/` helpers; `config.py`; `cli.py`.
- `backend/alembic/versions/` — 29 files; head `026` installs a DB-level legacy-migration ledger (roles, security-definer functions) under `legacy_migration` schema.
- `docs/` — very large process/handoff record (phases C/D/I, audits); `docs/adr`, `docs/architecture`, `docs/iterations`.
- `scripts/` — setup/check/predeploy audits.
- `.github/workflows/ci.yml` — CI.

---

### 4.4 Page Map (public + workspace)

Status legend (restricted to the requested values): `PASS` current-run usable · `PARTIAL` real but incomplete/mixed · `BROKEN` current defect · `PLACEHOLDER` shell only · `UNVERIFIED` source/build evidence exists but the full route was not exercised in an authenticated browser. The fresh runtime browser pass covered `/`, `/blog`, `/notes`, `/mistakes`, and the unauthenticated `/manage` boundary; all other route judgments explicitly rely on source, build, tests, and/or API evidence.

| Route | Purpose | Status | Data source |
|---|---|---|---|
| `/` (home) | Draggable personal landing (greeting/clock/calendar/article/music cards) | PARTIAL — fresh process renders; the pre-existing 2025 process is blank; learning counts remain `—` | `GET /api/notes`, recommendations, daily song, site settings |
| `/blog` · `/blog/[id]` | Blog list + detail | PARTIAL — list browser-verified; errors are rendered as empty content; detail not exercised | `Note` type=blog via `GET /api/notes` |
| `/notes` · `/notes/[id]` | Note list + detail/backlinks | PARTIAL — list browser-verified with 13 rows; authoring/edit route is dead; explicit error state is not rendered | `Note` via `/api/notes`; backlinks API |
| `/mistakes` | Public mistake list + admin legacy stats/plan/weak points | PARTIAL — list browser-verified; it is still legacy Note data and ignores request errors | `Note type=mistake`; legacy review/knowledge APIs for admin cards |
| `/mistakes/review` | Legacy SM-2 queue source page | PARTIAL — runtime redirect to `/manage/review`; superseded page still compiles | legacy `/api/review/*` |
| `/discover` | Shares/bloggers/featured-note discovery | UNVERIFIED | `/api/content/*`, `/api/notes?featured` |
| `/about`,`/share`,`/pictures`,`/projects`,`/snippets`,`/bloggers`,`/music`,`/guestbook` | Personal content and interactivity | UNVERIFIED — source/build only; guestbook also depends on externally provisioned tables | content, guest-message, and music APIs |
| `/clock`,`/image-toolbox`,`/wuthering-waves`,`/svgs` | Utility/play pages | UNVERIFIED | client-side |
| `/live2d` | Character page | PLACEHOLDER — displays “未启用” | client-side shell |
| `/write`,`/write-note`,`/write-mistake` (+`/[slug]`) | Legacy markdown editors | BROKEN — all redirect to `/manage/dashboard`; no replacement editor is reachable | source pages exist but runtime redirect wins |
| `/manage` | Login plus legacy management console after authentication | PARTIAL — unauthenticated login boundary browser-verified; authenticated console unverified; legacy placeholders remain | auth plus old management APIs |
| `/manage/dashboard` | Workspace home: quick actions, feedback, today, counts, activity | PARTIAL — real DB service/tests; guest correctly lands on login; authenticated browser state unverified; two quick actions self-loop | `/api/admin/dashboard/summary` |
| `/manage/subjects` · `/manage/knowledge-points` | Taxonomy tree CRUD | UNVERIFIED — service/route tests pass; authenticated browser not exercised | admin subject/KP APIs |
| `/manage/questions` (+`/[id]`) | Question bank CRUD + in-editor answer check | UNVERIFIED — code/tests pass; authenticated browser not exercised | admin questions/attempts APIs |
| `/manage/mistakes` (+`/[id]`) | Mistake + mistake-draft workspace | UNVERIFIED — code/tests pass; authenticated browser not exercised | admin mistakes/drafts APIs |
| `/manage/drafts` | Unified question/mistake draft queue | UNVERIFIED — code/tests pass; authenticated browser not exercised | admin draft APIs |
| `/manage/review` | Due review queue, 0–5 rating and history | UNVERIFIED — service/tests pass; authenticated browser not exercised; algorithm is incomplete | admin review-item API |
| `/manage/capture` | Image/manual/question-bank capture | UNVERIFIED — code/tests pass; 31/31 recorded recognition runs failed | admin captures and AI APIs |
| `/manage/ai` · `/manage/ai/runs` | AI-run governance, retry/accept/reject | PARTIAL — duplicate routes render the same panel; authenticated browser unverified | admin AI-run API |
| `/manage/attachments` | Attachment files and links | UNVERIFIED — code/tests pass; authenticated browser not exercised | admin attachment API |
| `/manage/search` | Note-only search | PARTIAL — implementation exists, nav marks it deferred, canonical entities are omitted | `POST /api/admin/search` |
| `/manage/settings` | Admin profile and dashboard preferences | UNVERIFIED — code/tests pass; authenticated browser not exercised | admin profile API |
| `/manage/jobs` · `/manage/analytics` | Governance overview reused under two labels | PLACEHOLDER — both routes render `GovernanceOverview`, not jobs/learning analytics | governance summary API |
| `/rss.xml`,`/sitemap` | Feeds | UNVERIFIED — production build emitted the routes; no current-run response exercise | build-time |

---

### 4.5 Data Model Map

| Domain | Canonical owner | Parallel/legacy owner | Current evidence |
|---|---|---|---|
| Learning taxonomy | `subjects`, `knowledge_points`, `question_knowledge_points`, `knowledge_point_links` | `Note.subject`, `Note.knowledge_points`, tags/folders | 2 subjects, 3 KPs; links target questions/drafts only; notes have no canonical KP link |
| Questions/practice | `questions`, `question_sources`, `attempts` | none | 3 questions, all archived; 0 attempts |
| Mistakes | `mistake_drafts`, `mistakes`, `draft_items` | `notes(type='mistake')` | 3 canonical mistakes; 5 legacy mistake notes |
| Review | `review_items`, `review_records` | SM-2 columns on `notes` + `/api/review/*` | 3 active/due items, 4 records; both schedulers remain live |
| Content/publishing | `notes`, tags, folders, versions, links | same polymorphic table also owns legacy mistakes | 13 notes total; 0 note versions and 0 note links in the current DB |
| Capture/AI | `capture_items`, `ai_runs`, `ai_call_logs`, recommendations | several direct/model-specific paths outside the gateway | 0 captures; 41 runs (10 success, 31 failure); all run targets null |
| Auth/files/audit | admin/session, attachment/link and audit tables | local filesystem content stores | 43 sessions, 0 active; 1 attachment |
| Guestbook | `guest_messages`, `guest_message_bans` runtime models | no verified schema owner found | tables exist in the development DB but are absent after a clean 001→026 replay |

Detailed relationships and the ten required model questions are in §12.

### 4.6 Learning Workflow Map

| Step | Implemented path | Current break/limit |
|---|---|---|
| Learn/record | note/blog source editors; capture/manual question intake | `/write*` redirects make note/blog authoring unreachable; OCR history is 0/31 success |
| Organize | tags/folders for content; Subject→KP tree for formal learning | notes never bind to KPs, so organization is split |
| Practice | submit an `Attempt` from question editing | no daily practice surface; current DB has 0 attempts |
| Detect mistake | wrong Attempt or manual/capture flow → `MistakeDraft` | attempt-derived reason defaults to unknown; later wrong attempts can duplicate work |
| Curate mistake | draft triage → atomic `Mistake` + `ReviewItem` conversion | strong implementation, but legacy public mistake chain remains separate |
| Review | due queue → rating 0–5 → append `ReviewRecord` | no type-aware re-answer; failures still increment repetitions |
| Master | none | no mastered/graduated state; item stays active until archive |
| Feedback | dashboard counts/recent activity; legacy weak-point cards | no per-KP accuracy, repeated-error, stability, or long-overdue aggregation from canonical data |

This is the baseline used by the detailed loop audits in §§7–11.

### 4.7 Five-state capability matrix

This matrix prevents “code exists” from being reported as “complete.” `Runnable` means the implementation executed in tests/API/build or a current browser; `Verified` names the boundary of that evidence.

| Major capability | Design exists | Code exists | Runnable | Closed loop | Verified |
|---|---|---|---|---|---|
| Note/blog authoring | YES | YES | **NO from reachable UI** | NO | YES — redirects, links and browser path checked |
| Subject/KP taxonomy | YES | YES | YES (API/tests) | PARTIAL — content excluded | PARTIAL — authenticated UI not browser-run |
| Question→Attempt | YES | YES | YES (service/tests) | NO — no practice routine; 0 live attempts | PARTIAL — no authenticated browser run |
| Mistake draft→Mistake→ReviewItem | YES | YES | YES | YES for this sub-chain | YES — DB/service/API tests + current rows; UI source only |
| Review rating/history | YES | YES | YES | NO — no re-answer/mastery terminal state | YES for scheduler/history behavior; UI source only |
| Learning feedback | YES | YES | YES (dashboard service/tests) | NO — canonical KP accuracy absent | PARTIAL — authenticated UI not browser-run |
| Capture/OCR→draft | YES | YES | PARTIAL — manual path exists, recorded OCR is 0/31 success | NO in observed data | YES for failure evidence; no successful live capture verified |
| Public content output | YES | YES | YES on fresh runtime | PARTIAL — disconnected from canonical learning results | YES for home/blog/notes/mistakes list routes only |
| Search | YES | YES | YES | PARTIAL — Notes only | YES in implementation/tests; workspace UI not browser-run |
| AI citation binding | YES (schemas) | PARTIAL | PARTIAL (in-memory response) | NO — nothing persisted | YES at code/schema boundary only |

---

## 5. Current Product Positioning

**Answer: this is a "Personal Learning System (canonical core) that is still surfaced through blog/note chrome, split across two data generations."** It is not a blog+note CMS: blogs/notes/mistakes all live in one `notes` table and are edited through shared legacy tooling; meanwhile a fully separate, private, formal learning domain (subject/KP/question/mistake/review) has been built in the workspace and is the intended future. Public pages are the "publishing layer" of the same personal knowledge; the workspace is the learning layer. Neither yet feeds the other for mistakes (workspace mistakes are private and invisible to the public 错题集).

**Gaps versus "真正的个人学习系统"** (each mapped to code):
1. No state that says "this mistake/knowledge point is now learned" (mastery/graduation) — see §9.
2. No daily practice stage (answer fresh questions) — attempts only via the question editor's 作答验证; no queue/paper/session UI; dev DB attempts = 0.
3. Notes (the record stage) are not connected to the KP tree that the review/feedback stage depends on.
4. Feedback surfaces (weak points, review plan, public stats) are computed from legacy Note text, so the user's canonical mistakes do not influence the "what's weak" answer.
5. The authoring entry for notes/blogs is currently broken by route cutover (see R03).
6. AI-generated knowledge materials (variants, knowledge cards, summaries w/ citations) are not persisted or linked to a KP, so the AI output disappears after display.

### Blog module verdict

Blog and Note already share the `Note` model, list API, markdown renderer, tag/folder machinery, and authoring code; `type='blog'|'note'` is the main distinction. That reuse is appropriate. Blog has independent value as the public learning-output layer, but a new `Article` aggregate would duplicate the same content before the Note→Knowledge relationship even exists. The proportionate target is: private/draft Note → bind to one or more KPs → intentionally publish the same content as Blog output, with provenance retained. **KEEP CURRENT IMPLEMENTATION:** keep Blog and Note on the shared content model; do not add a separate Article table now. Restore the editor and add KP/publication workflow instead.

---

## 6. Architecture

**Frontend:** page/component → hook → `src/lib/api/*` → backend. Workspace under `src/app/manage/(workspace)` with one sidebar nav source (`manage-sidebar.tsx:38-171`). Server session auth via cookie; `AuthGate` is UX-only.

**Backend:** router → Pydantic schema → service → model. 34 routers all mounted in `main.py:97-131`; startup pins `alembic` revision `026` and runs fail-closed security checks (`main.py:17-61`). Auth boundary is `get_current_admin` (`routers/auth.py:119-130`).

**Two parallel data stacks (key architectural fact):**

| Aspect | Legacy (public-facing) | Canonical (workspace) |
|---|---|---|
| Mistake storage | `Note.type='mistake'` + SM-2 cols | `Mistake` + `MistakeDraft` + `DraftItem` |
| Scheduling | `sm2.py` writes `Note.ef/interval/...` in place | `ReviewItem`/`ReviewRecord`, `fixed_interval_v1` |
| Review API | `/api/review/queue|stats|plan|/{slug}` | `/api/admin/review/items` |
| KP | free-text `Note.knowledge_points` | `Subject/KnowledgePoint/KnowledgePointLink`, QKP |
| Weak points | `knowledge_retrieval.retrieve_weak_points` (text parse) | *(absent in dashboard)* |
| Practice | — | `Attempt` (auto-graded) |
| Capture/OCR | — | `CaptureItem` pipeline |
| Data in dev DB | 13 notes (1 blog/5 mistake/7 note), tags 34 | 3 questions(archived, `LT-*`), 3 mistakes, 3 review_items, 4 review_records, 0 attempts, 0 captures |

---

## 7. Learning Loop Audit

| Stage | Implementation | Data model | UI | Closed loop? | Status |
|---|---|---|---|---|---|
| 学习/记录 (input) | Manual note/blog editor (**currently unreachable**), capture(OCR) for mistakes | `Note`; `CaptureItem` | `/write*`(redirected); `/manage/capture` | ✗ notes can't attach to KP | BROKEN / PARTIAL |
| 整理 (curate) | Tags/folders/categories (notes); subjects+KP tree (formal) | `Tag/note_tags`, `Folder`, `Subject/KnowledgePoint` | `/notes` sidebar; `/manage/subjects` | ✗ note tags ≠ KP | PARTIAL |
| 知识点 | Tree CRUD w/ unique-under-parent, subtree archive | `knowledge_points` (self-FK) | `/manage/subjects/{id}`, `/manage/knowledge-points` | partial | PASS |
| 练习 | In-editor 作答验证 only | `Attempt` | `question-editor.tsx` | ✗ no practice session/queue; dev attempts=0 | WEAK |
| 错题 | Draft → human convert → Mistake (+ReviewItem) | `MistakeDraft/Mistake/DraftItem` | `/manage/drafts`, `/manage/mistakes` | ✔ chain exists | PASS |
| 错因 | enum + free text on draft; AI suggestions | `reason_category` (5 values), `mistake_reason` | draft edit UI | draft→mistake retains it | PASS |
| 复习 | Fixed-interval due queue, 0–5 rating, history | `ReviewItem/ReviewRecord` | `/manage/review` | ✗ no lapse reset/graduation; new item instantly due | PARTIAL |
| 掌握度变化 | **Absent** | none (`Mistake` no mastery col; `ReviewItem.state` = active/paused only) | none | ✗ | MISSING |
| 反馈 | Dashboard counts + deterministic "what to do"; legacy weak-points | `DashboardSummary` from canonical; weak-points from legacy text | `/manage/dashboard`, `/mistakes` | ✗ feedback ignores canonical mistakes/KP accuracy | PARTIAL |

---

## 8. Knowledge System Audit

- Tree: real CRUD, per-parent uniqueness, archive-subtree, cycle-safe reparenting (`taxonomy_service.py`); nested tree API (`/subjects/{id}/knowledge-tree`) used by editors.
- Relations/prereq: `QuestionKnowledgePoint.role ∈ primary|secondary|prerequisite` exists but is never surfaced or used in planning/retrieval.
- Notes-to-KP: **no binding** (the weakest knowledge link). No editor control; no API.
- Backlinks: implemented for notes via `[[wikilink]]` extraction (`knowledge_markdown_service.py:20-56`) + `/notes/{id}/backlinks`; dev DB `note_links` = 0 (feature dormant).
- Versioning: `NoteVersion` snapshot on create/update + `/notes/{slug}/versions` API exist; dev DB 0 rows; no version-history UI seen in authoring.
- Search for notes: FTS+trigram at query time over title/content/summary/category, `hidden=false AND published` (`search_notes:68-82`). The `search_vector` column and GIN index exist, but all 13 current notes have `search_vector IS NULL`; the query recomputes vectors instead of using that index.
- AI knowledge retrieval: `retrieve_context_pack` re-ranks legacy notes by subject/KP-text/tag/due — a pragmatic local retrieval path, but still legacy-only.
- Knowledge graph: not implemented. **Is it worth it?** Not as a graph database/visualization. The minimal worthwhile step is notes→KPs so one KP page can list its notes/questions/mistakes; no graph layout is needed now.

### Search verdict

Title/content/category search, Postgres FTS and trigram are sufficient for the current personal corpus. The functional gap is scope, not engine capacity: the search route returns visible published Notes only and omits canonical Questions, Mistakes and KPs. **KEEP CURRENT IMPLEMENTATION:** retain PostgreSQL FTS + `pg_trgm` + ordinary SQL; decide whether search is intentionally notes-only or add a small canonical multi-entity result union. Do not add Elasticsearch or vector infrastructure at this scale. Separately, either maintain/use `search_vector` or remove its unused GIN index so the schema tells the truth.

---

## 9. Mistake System Audit

**"错题存储器 or 错题学习系统?"** It is a well-built **mistake intake and storage system with a review queue**, not yet a full mistake-learning system: type-aware re-answer, mastery inference, and KP-level feedback are missing.

Present and verified in code/tests:
- Capture image → OCR (`CaptureItem` uploaded→recognizing→recognized→drafting→ready→converted) → editable AI draft → QuestionDraft+MistakeDraft.
- Manual question entry, mistake-from-question-bank, and wrong Attempt→MistakeDraft (idempotent per attempt).
- Draft triage with `pending/needs_fix/rejected/converted`, versioned edits, rejection reason, and atomic Mistake+ReviewItem+KP-link conversion.
- Reason category + free text, attachment links, list/detail/update/soft-archive.

Missing or weak:
- **No re-answer:** Review provides only 0–5 self-rating. Exact automatic equality is also inappropriate for `short_answer`/`essay`; those need a human-confirmed outcome.
- **No mastery:** archive is the only terminal action; rating history never graduates an item or updates the Mistake/KP state.
- **Retry duplication:** a later wrong attempt can create another draft without reconciling the active ReviewItem for the same question.
- **OCR reliability:** current DB has 31 failed `capture_recognition` runs, 0 successes, and 0 `capture_items`.
- Attempt-derived drafts default to `reason_category='unknown'` and no reason text.

---

## 10. Review System Audit (with data)

**What exists**
- `ReviewItem` (`models/review_item.py`): `target_type='mistake'` CHECK-constrained; `mistake_id` FK unique; `algorithm` column constrained to exactly `'fixed_interval_v1'`; `next_review_at` default `now()`; `idx_review_items_due (state, next_review_at)`.
- `ReviewRecord` stores rating 0–5 plus previous/next intervals & timestamps — a real, append-only history.
- `review_item_service.submit_review` (`:29-41`) uses row-lock + `expected_next_review_at` optimistic check → strong concurrency. `INTERVALS={0:1,1:1,2:1,3:3,4:7,5:14}`.
- UI queue `/manage/review` (`review-queue.tsx`): rating buttons 0–5, interval labels, per-item inline history.

**Broken loop details (evidence)**
1. `submit_review` increments `item.repetitions += 1` for **every** rating including 0–2 (`review_item_service.py:40`); there is no lapse reset, no EF, and no state where a failing review pushes the item back into "learning".
2. `ReviewItem.state` CHECK is `state IN ('active','paused')` (`models/review_item.py:33`); `paused` is only set when a Mistake is archived (`mistake_service.py:188`). Nothing can express `mastered`/`graduated`; a ReviewItem is due forever until manually archived.
3. `Mistake` has no mastery/interval column (`models/mistake.py`); review outcomes never write back to the mistake or to its knowledge points.
4. Because `next_review_at` defaults to `now()`, a newly converted mistake is immediately due, mixing "new" and "overdue" in one due queue.
5. Legacy duplication: the same repo contains a second scheduler `sm2.py` (`quality≥3 → 1, 6, round(interval*ef)`; `<3 → reset`), mutating `Note` in place via `/api/review/{slug}` with **no history**; legacy "mastered" = `next_review IS NULL` (`routers/review.py:70-73`) which the SM-2 route can never produce (it always sets `next_review`). Its public stats/plan cards still render for admins on `/mistakes`.

**FSRS decision (single user, ~tens–hundreds of items):** Not now. Expected benefit is small (better interval prediction) while the dominant defect is *semantics* (no graduation, no lapse handling, no re-answer), not interval precision. Recommended sequence: (1) add mastery/lapse semantics to the existing scheduler (≈1–3 days), (2) optionally upgrade canonical scheduler to SM-2-style EF later. **KEEP current fixed-interval as the algorithm until mastery semantics exist.** Revisit FSRS only if item count grows into the thousands and daily review accuracy visibly matters.

---

## 11. Dashboard Audit

**Answers to the "does the system answer…" questions**

| Question | Verdict | Evidence |
|---|---|---|
| 我最近学了什么？ | PARTIAL — "最近活动" (recent questions + recent reviews) | `dashboard_service.py:71-77`; `dashboard-overview.tsx:183-189` |
| 我哪里最薄弱？ | **NO (canonical)** — weak-point UI exists but reads legacy Note text | `knowledge_retrieval.py:247-311`; shown on `/mistakes` only |
| 哪些知识点错误最多？ | NO — no accuracy aggregation by KP anywhere | QKP role/link tables never aggregated |
| 哪些知识长期没复习？ | NO — dashboard shows only due count, no stale/overdue horizon | `DashboardCounts` = questions/mistakes/kps/attachments/due_reviews |
| 哪些题反复出错？ | NO — ReviewRecord is never aggregated per question/KP | `review_records` consumed only in detail drawer + recent list |
| 最近学习是否稳定？ | NO — no time-series | no chart/streak module (echarts is content-only) |
| 今天最值得复习什么？ | PARTIAL — deterministic rule only ("due>0→复习；否则整理错题…") | `dashboard-overview.tsx:55-91`; no KP/subject targeting |
| 学习历史 | NO — no daily history/streak/log | audit_logs exists but is action audit, not learning history |

**Placeholder audit:** No hardcoded stats or fake charts on the dashboard (tests assert no static shell, `dashboard-overview.test.tsx:72`). Real holes: home `LearningSpaceCard` shows `—` with aria "数量尚未接入" (`learning-space-card.tsx:12-33`); legacy `/manage` overview stat cards render `--` (`manage/page.tsx:286`); `manage-placeholder-page.tsx`, `future-capability-page.tsx`, `wip.tsx` are dead components.

**10-second question:** A user opening `/manage/dashboard` gets the 学习反馈 block pinned near the top, which does answer "due reviews → 复习; else 整理错题/复盘". That is good. But after clearing due reviews there is no "next learning task", no weakness signal, and two of four 快速开始 cards (写笔记/写博客) bounce back to the dashboard via redirect.

---

## 12. Data Model Audit (ER + 10 questions)

ER (canonical spine):
```
subjects 1─n knowledge_points (self-FK parent)
subjects 1─n questions 1─n question_knowledge_points m─1 knowledge_points
questions 1─n question_sources 1─n attempts
questions 1─n attempts; attempts 0..1 draft_items (mistake_draft_item_id)
draft_items 1─1 question_drafts | 1─1 mistake_drafts (CHECK-partitioned)
mistake_drafts n─1 questions; mistakes n─1 questions; mistakes 1─1 draft_items(source)
mistakes 1─1 review_items (mistake_id UNIQUE) 1─n review_records
knowledge_points n─m KnowledgePointLink (target_type|target_id polymorphic)
notes (legacy poly: type=note|blog|mistake; SM-2 cols; knowledge_points TEXT; search_vector TSVECTOR)
note_tags m─n tags; note_versions, note_links; attachments/attachment_links; capture_items; ai_runs/ai_call_logs; audit_logs …
guest_messages, guest_message_bans (active runtime tables, intentionally outside owned Alembic metadata)
```

| # | Question | Answer |
|---|---|---|
| 1 | Knowledge 能形成结构？ | Yes for canonical: KP self-parent tree, per-subject unique-name partial indexes, subtree archive (`taxonomy_service`). |
| 2 | Question 绑定 Knowledge？ | Yes — `question_knowledge_points` (role primary/secondary/prerequisite) **and** generic `KnowledgePointLink`; but `role` is write-only, never read (`question_service.py:105-120,192-219`). |
| 3 | Mistake 绑定 Question？ | Yes — `Mistake.question_id` FK; plus frozen `question_text/correct_answer/analysis` snapshot. |
| 4 | Mistake 记录错误原因？ | Yes — enum `concept/calculation/reading/careless/unknown` + free `mistake_reason`; auto drafts from attempts default to `unknown` + `None` (`attempt_service.py:47-70`). |
| 5 | ReviewItem 能追踪复习？ | Partially — append-only `ReviewRecord` tracks rating/intervals; but no mastery/graduation; `algorithm` hardwired to one value. |
| 6 | Subject 真正参与学习组织？ | Partially — KP tree scoped to Subject and question/mistake FK subject; but review queue and dashboard don't group by subject. |
| 7 | Note 与 Knowledge 关系？ | **None.** Notes use tags/folders; legacy `knowledge_points` is free text; `KnowledgePointLink` is never written for notes (dev DB targets = question/question_draft only). |
| 8 | Tag 承担了 Knowledge 职责？ | Yes partly — tags/folders do ad-hoc clustering on notes that the formal KP tree should own; public filters rely on tags/`Note.subject` string. |
| 9 | 重复建模？ | Yes — `QuestionKnowledgePoint` vs `KnowledgePointLink` dual-write for the same fact; legacy `Note` mistake columns (subject/difficulty/question/answers/ef/interval/…) vs canonical tables; two schedulers; SM-2 duplicate. |
| 10 | 未来扩展困难的结构？ | Polymorphic `KnowledgePointLink.target_id VARCHAR(64)` (no FK, orphan-prone); untyped managed-content JSON; `Note` god-table; migration 026's large governance contract; active guest tables without a verified provisioning owner. |

Data-quality notes from the development DB: `alembic current` = `026`; 13 notes (7 note/1 blog/5 legacy mistake), 2 subjects, 3 KPs, 3 archived questions, 0 attempts, 3 active/due review items, 4 review records, 0 capture items, 41 AI runs, 0 note versions and 0 note links. Core FKs/constraints sampled cleanly. A fresh replay 001→026 passes for the **owned metadata**, but `to_regclass('guest_messages')` and `to_regclass('guest_message_bans')` are null afterward. Therefore “no schema drift” is true only inside `SCHEMA_LIFECYCLE_METADATA`, not for the whole active application.

### Database engineering verdict

The owned migration chain, timestamps, foreign keys, uniqueness rules, CHECK constraints, partial indexes, soft archive paths and conversion transactions are stronger than typical for a single-user system. No repository abstraction or new datastore is justified. The concrete database defect is ownership: two mounted guestbook tables are outside the verified migration lifecycle. The structural debt is duplication (`QuestionKnowledgePoint` plus polymorphic `KnowledgePointLink`, and legacy mistake columns beside canonical models), not missing infrastructure.

---

## 13. Frontend Audit

- Layer discipline good: pages → hooks (SWR) → `src/lib/api/*`; robust error classification in `client.ts` (network/auth/backend, 204→undefined); streaming bypasses documented.
- Current operational split: the old port-2025 process is BROKEN by missing chunks; a new production build/process is PASS for exercised public pages. The deployment/start contract does not currently guarantee a coherent HTML/manifest/chunk set.
- Public request-state handling is inconsistent: Notes records `data-render-state='error'` but has no error branch; Blog and Mistakes omit the returned error entirely. These pages can misreport an outage as “还没有内容”.
- `any` count: 125 in `src` (9 in lib/api; only 1 in the modern workspace — the rest in the legacy `/manage` console).
- Type duplication: dual-shaped `Question` DTO (canonical structured + legacy flat), two review clients (`review.ts` legacy vs `review-items.ts`), reason label maps re-declared in 4 files.
- Dead/orphan frontend: `ai.analyzeMistakeStream/analyzeTextStream`, `folders.updateFolder/moveFolder`, `music.*`, most `music-manage.*`, `meta.createTag/mergeTag/*Category`, `notes.promoteNote`, `questions.updateQuestion` (PATCH orphan), `knowledge.getKnowledgeSummary`, components `manage-placeholder-page.tsx`, `future-capability-page.tsx`, `wip.tsx`, `src/app/music/list.ts`, unused `readFileAsText` import (`blog/page.tsx:19`).
- No component-primitive layer: 41 identical `w-full rounded-lg border border-slate-200 px-3 py-2.5` input literals across editors; 48 raw `<button>` across workspace pages; mixed `rounded-lg`/`rounded-2xl`/`rounded-3xl` shells; ad-hoc `window.confirm` vs inline alertdialogs.
- State: workspace uses local state + SWR (good). zustand only in home/write preview stores.
- Dashboard test pins the broken 写笔记/写博客 hrefs (`dashboard-overview.test.tsx:79`) rather than catching the redirect self-loop.

---

## 14. Backend Audit

- Router→service→model discipline is consistent; routers thin-ish; error mapping helpers per router; optimistic concurrency & row locks; `version` columns + 409s.
- Inconsistencies: DELETE semantics differ — questions/mistakes soft-archive (200 + entity), subjects/KPs/categories hard delete (204); `DELETE /api/admin/subjects/{id}` and `POST|PUT|DELETE /api/categories/*` are orphans (no UI caller).
- Duplication: two schedulers (SM-2 legacy + fixed interval canonical); `QuestionKnowledgePoint` + `KnowledgePointLink` dual write; `review_planner` (legacy) vs dashboard (canonical).
- Over-engineering for a single user: migration `026` installs 5 DB roles, `SECURITY DEFINER` plpgsql functions and a ledger state machine to govern a one-off legacy-note migration that is not even routed from HTTP (`legacy_note_migration_adapter.py` needs a dedicated runner DB user + 3–4 independent approvers). High quality, but its operating cost now exceeds its value until the cutover is actually executed.
- Orphan APIs: `PATCH /api/admin/questions/{id}`, subject DELETE, category write endpoints; `drafts.py` rejects non-question types by design.
- Schema ownership gap: guest-message models and mounted routes are live, but `models/registry.py` removes both guest tables from Alembic metadata. A clean 026 database therefore cannot run that feature unless an undocumented external provisioner creates the tables.

### API contract verdict

Major administrative mutations are Pydantic-validated and protected by `get_current_admin`; the draft→mistake conversion is transactional/idempotent, and review submission uses both a row lock and an expected timestamp. Status/error semantics are mostly deliberate, but resource deletion is inconsistent (hard delete/204 versus archive/200), canonical and legacy review APIs overlap, and several write endpoints have no repository caller. Keep the current router→service boundary; do not add a Repository layer. Normalize contracts only while touching the owning domain, and require usage evidence before deleting an apparent orphan endpoint.

---

## 15. AI Pipeline Audit

Verified architecture: `AiTaskType` enum → `PROMPT_REGISTRY` (frozen `PromptTemplate` with versions) → `ai_gateway` (run record + call log + provider fallback) → `ai_validator` → `AiRun` review ledger. Current DB evidence is weaker than the architecture suggests: 10/41 runs succeeded, 31/41 failed (all `capture_recognition`), and all 41 have `target_id IS NULL`.

**Input→Prompt→Context→Model→Output→Validation→Persistence check:** governed tasks start from typed request input, select a versioned registry prompt, combine task-specific context (image, recognized text, KP/question context, or recommendation context), route through configured providers/fallbacks, validate structured outputs, and store run/call evidence. Human-editable draft flows preserve the source and require confirmation before trusted entities are written. The exceptions are material: polish and diagram fallback bypass the registry/gateway; several successful structured outputs are display-only; citation context is caller-supplied and not persisted; every observed run lacks a target binding. Gateway retries/fallback and AiRun review/retry controls exist, but 31 consecutive capture failures show that retry machinery is not equivalent to a working feature.

Per-feature chain check:

| Feature | Input→Prompt→Model | Output validation | Persistence | Issues |
|---|---|---|---|---|
| `analyze`/OCR | vision (DashScope qwen), DeepSeek text | manual parse + repair | AiRun + AiCallLog only | not schema-validated; no entity link |
| `capture_recognition` | image → `RecognitionOutput` | schema ✔ | `capture_items.recognized_text` | OCR flaky (31 fails in dev DB) |
| `capture_draft` | text → `MistakeDraftSuggestionV1` | schema ✔ | capture draft fields | depends on OCR |
| staged mistake (`question-draft`, `error-interpretation`, `final-analysis`) | image/text → schemas | ✔ | AiRun only; **front-end then writes a legacy `Note` via `/api/notes`** | `question-draft/confirm` = non-persisting stub (`ai.py:487-497`); results not linked to returned run; AiRun target_type/id not set from these routes |
| `generate_variant` / `generate_knowledge_card` | KP → schema | ✔ | AiRun only; output discarded after display | no persist/link to KP |
| `knowledge_summary` w/ citations | context pack → schema-only blocks | blocks downgraded to `ai_inference` when unsupported | **nothing persisted** | citation model exists only in schemas (`schemas/knowledge.py`) |
| `recommendation` | learning context → `RecommendationOutput` | ✔ | `recommendations` row w/ `raw_context` | works; 8 succeeded runs, 29 rows |
| **polish** (note/blog assistant) | **hard-coded unversioned `SYSTEM_PROMPTS` dict**, direct httpx stream bypassing the gateway | none | no AiRun/AiCallLog; only `audit_action` | governance hole |
| diagram fallback image-gen | Qwen HTTP call outside gateway | none | unlogged | not in run ledger |

**Overall:** The AI foundation is thoughtfully designed, but adoption and observed reliability are partial. AI creates most value when it ends in a human-editable draft; it creates the least value where output is displayed and discarded. The currently recorded flagship capture path has no successful run, so its product value is not yet verified.

Repository-wide searches found no current task types or implementations named `mistake_social_export` or `knowledge_article`. They are therefore **not missing plumbing to finish**; they are unstarted product ideas and belong in D — Do Not Build Yet while the learning loop is incomplete.

---

## 16. Citation System Audit

- **No persisted citation model.** `CitationBlock/SourceRef/SourceType` exist only as request/response DTOs in `schemas/knowledge.py`; `knowledge_summary` returns blocks with `source_refs` bound against the caller-supplied context pack and downgraded to `ai_inference` when a source isn't supported — but nothing writes citations to the DB.
- `QuestionSource` (`models/question.py:180-202`) is genuine provenance for questions (source book/exam/note/url) — not AI output citations.
- A `[1]/[2]`-style rendering without a DB relation would be judged incomplete; currently the output doesn't even claim DB citations (in-memory binding only). **Decision needed**: either persist source bindings (see R18) or remove the citation presentation from the summary UI to avoid implying traceability the DB doesn't record.

---

## 17. UI/UX Audit

### Current-run visual evidence

| State | Observation | Screenshot |
|---|---|---|
| Existing port-2025 home | Blank white viewport because HTML references missing chunks | `/Users/limengyang/.codex/visualizations/2026/09/02/01a06187-cbbc-7102-8714-1059dd58e18c/runtime-existing-home-blank.png` |
| Fresh build + fresh server home | Renders real article/music data; confirms source is runnable | `/Users/limengyang/.codex/visualizations/2026/09/02/01a06187-cbbc-7102-8714-1059dd58e18c/runtime-fresh-connected-home.png` |
| Fresh Notes list | Renders all 13 public rows and filters; fixed/narrow content uses less than half of the 1280px canvas | `/Users/limengyang/.codex/visualizations/2026/09/02/01a06187-cbbc-7102-8714-1059dd58e18c/runtime-fresh-connected-notes.png` |
| Fresh unauthenticated Manage | Correctly resolves to the login surface; authenticated workspace visuals remain `UNVERIFIED` | `/Users/limengyang/.codex/visualizations/2026/09/02/01a06187-cbbc-7102-8714-1059dd58e18c/runtime-fresh-manage-auth.png` |

### Findings

- **Information architecture:** the public shell is coherent as a personal site, but the learning spine is discoverable only after entering Manage. The public mistake page then falls back to the legacy generation, so navigation crosses data models without explaining the boundary.
- **States:** `/notes` computes `renderState='error'` but renders neither an error panel nor retry; `/blog` receives `error` from its hook but discards it; `/mistakes` discards the note-index error. Network failure therefore becomes blank content or “还没有…”, which is factually wrong. No route-level `loading.tsx` or `error.tsx` exists.
- **Hierarchy and density:** at 1280px, public pages cluster very small text and controls in roughly the left half while leaving a large empty canvas. This is visually distinctive, but scanning/filtering learning content is harder than necessary and the key next action is visually weak.
- **Consistency:** global tokens and shared Manage panels exist, and the authenticated mobile navigation implementation has focus trapping, Escape handling, `inert`, and focus restoration. However, public and Manage surfaces use different visual languages; workspace forms still repeat raw Tailwind control styles and label maps.
- **Accessibility (source-based, mobile browser not captured):** public bottom-nav links use `text-[10px]` and `px-3 py-1`; the “更多” sheet has no dialog role, modal semantics, focus trap, Escape close, or focus restoration. Manage mobile navigation already contains the stronger pattern and should be reused.
- **Honest verification boundary:** public home/blog/notes/mistakes and guest→Manage login were browser-verified. Authenticated `/manage/*` pages were reviewed through source, tests, and database evidence only; they are not claimed as current browser PASS.

### Design system verdict

This is a partial design system, not a unified one. Global color/type/layout tokens and reusable Manage panels create a recognizable shell, and the Manage mobile drawer demonstrates a good interaction pattern. But buttons, inputs, cards, radii, labels and confirmation behavior are still largely page-local: 41 repeated input class literals and 48 raw workspace buttons are concrete duplication. The right-sized response is a thin primitive layer (`Button`, `Input`, `Field`, `Panel`, one modal/drawer pattern) extracted while repairing real workflows—not a standalone design-system rewrite.

---

## 18. Testing Audit

Ran safely (isolated Postgres for backend; no dev data touched):

### Build and test status

| Suite | Command | Result |
|---|---|---|
| Frontend typecheck | `npx tsc --noEmit` | PASS |
| Frontend test typecheck | `npm run test:typecheck` | PASS |
| Frontend unit (Vitest) | `npm test` | PASS — 39 files, **374 passed** |
| Backend unit/integration | `pytest tests/` on throwaway PG (fresh `alembic upgrade head`) | PASS — **412 passed, 6 skipped** |
| Frontend prod build | `NEXT_PUBLIC_API_URL=http://ci-check.invalid:8000 npm run build` | PASS |
| Migration replay | `alembic upgrade head` from empty isolated DB | PASS (001→026) |
| Browser smoke, existing server | current port 2025 | FAIL — HTML 200, multiple referenced chunks 404; blank/loading screenshots |
| Browser smoke, fresh build/server | public routes + guest auth boundary | PASS for exercised routes; authenticated workspace UNVERIFIED |
| Lint | none configured | NOT AVAILABLE |

**Executed totals:** 792 test cases observed: 786 passed, 0 failed, 6 skipped. The backend run emitted 2 `RuntimeWarning`s from an un-awaited `AsyncMock` in `test_ai_gateway.py`; Vitest emitted known `act(...)` warnings in hydration tests and a `TimeoutNaNWarning`. These do not fail the suites but should not be silently treated as clean output.

Coverage of the learning spine is good: taxonomy, attempt service, mistake service/routes, review (legacy + item) service, dashboard routes/UI, capture chain, question domain, search. **Gaps:** no tests exist for mastery/lapse (feature absent); Vitest and `test:typecheck` are not run in CI; the 8 Playwright `.spec.ts` files are not wired into CI; guest-message endpoints are not tested against a fresh migrated schema; there is no deploy/start smoke test that catches missing chunks.

---

## 19. Security Audit

- Auth: opaque session cookie (hashed token, expiry, revocation), passkey tier; `get_current_admin` on every mutation; cookie `HttpOnly`, `SameSite=Lax`, `path=/api`, Secure on https.
- **CSRF:** no token; mitigated by SameSite=Lax + cookie path scoping. Acceptable for single user behind admin auth but worth a SameSite decision note (legacy `cross-site` contexts would need tokens).
- Uploads: attachment MIME allow-list (png/jpeg/webp/pdf/txt), 10 MB cap, checksums, path/symlink protections and private visibility are good. **Generic attachments trust the declared MIME**; only the legacy managed-image routes inspect magic bytes.
- XSS: markdown renderer drops raw HTML (`renderer.html=()=>''`), protocol allow-list for links/images, HTML escaped before parse. Remaining surface: two `dangerouslySetInnerHTML` sites (KaTeX math, Mermaid SVG) fed by renderer-escaped text (`markdown-math.tsx:27`, `diagram-viewer.tsx:108-112`); no DOMPurify anywhere. Low residual risk.
- Fail-closed guards at startup (`main.py:41-61`); `AUTH_BYPASS` setting exists (fail-closed check present); AI error messages sanitized.
- Public note detail returns full legacy mistake content (question/correct_answer/analysis) to guests for published rows — intentional (public 错题集) but should be an explicit content decision; EF/interval rows are admin-only in the list UI.
- Password login has no request throttling/lockout. Registration and authentication passkey challenges are global process-local dictionaries keyed by the literal `"current"`, with no TTL; concurrent attempts or multiple workers can overwrite/lose challenges.
- Guest-message IP rate limiting trusts the first `X-Forwarded-For` value without a verified trusted-proxy boundary; direct clients can spoof it if the service is exposed outside the expected proxy.
- Current local responses expose `X-Powered-By: Next.js` and no CSP, HSTS, `X-Content-Type-Options`, `Referrer-Policy`, or `Permissions-Policy` was observed. Deployment-edge headers were not verified, so production status is `NOT_VERIFIED`.
- `npm audit --omit=dev` reports **7 production-tree advisories: 5 high, 2 moderate** (`brace-expansion`/`glob`/`minimatch` through OpenNext, plus `nanoid`, `dompurify`, `undici`). Reachability was not established; do not blindly accept the suggested OpenNext downgrade.

---

## 20. Performance Audit

At this scale (13 notes; 3 canonical questions) query cost is fine. FTS is computed per request (acceptable today), dashboard aggregates are small, and review-queue `session.get` calls are inconsequential at 3 items. No new infrastructure is justified. The real performance/reliability issue is artifact coherence: a cached 200 HTML document referenced missing chunks and produced a blank page. Also, the existing `search_vector` GIN index has no effect while all vectors are null and queries recompute `to_tsvector`; either maintain/use it or remove the misleading index.

---

## 21. Complexity Audit

**Introduced but unnecessary/over-heavy for a single-user system:**
1. Migration 026 DB governance (roles, security-definer state machine, ledger tables) as dormant tooling for a migration not yet executed.
2. Two full parallel stacks (legacy Note-based + canonical) each with its own review UI, schedulers, stats, and APIs.
3. `QuestionKnowledgePoint` + polymorphic `KnowledgePointLink` dual record of the same link.
4. Dozens of orphan endpoints/components/pages + legacy `/manage` console tabs kept alive beside the workspace.
5. Prompt-standardization + run-governance machinery that is first-class, but applied inconsistently (polish excluded).
6. Very large `docs/` process record (phases C/D/I, several hundred files) — historical overhead.
7. Active guest-message models/routes are intentionally outside Alembic, but the alternative schema owner/provisioning path is not present in the runnable contract.

**Looks simple today but will become debt:**
- Polymorphic `KnowledgePointLink.target_id` without FK (orphans as KPs/questions are deleted).
- `notes` god-table (3 types + review columns) that the canonical system must eventually drain.
- `managed_content_entries.data JSON` untyped content.
- Review scheduling semantics (interval map + forever-active items) hardcoded in code and CHECK constraints — changing algorithm requires a migration.
- The redirect-based route cutover removed authoring without providing a replacement entry (see R03).

---

## 22. Missing Capabilities (learner view, with necessity/ROI)

| Capability | Necessity | Cost | Do now? |
|---|---|---|---|
| Mastery/graduation on review items | High — loop cannot close | M | **Yes (P0)** |
| Re-answer mistakes objectively | High | M | **Yes (P0)** |
| Working note/blog authoring entry | High (regression) | M | **Yes (P0)** |
| Canonical-first weak points & per-KP accuracy | High — the "feedback" promise | M | **Yes (P0/P1)** |
| Notes↔KP binding | Medium-high | M | **Yes (P1)** |
| Daily practice queue (fresh questions) | Medium | M | P1/P2 |
| Attempts history/statistics API | Medium | S | P1 |
| Streak/consistency & long-overdue visibility | Low-Medium | M | C |
| Knowledge graph visualization | Low | XL | **No (D)** |
| FSRS | Low now | M+ | **No (D)** |
| Vector search | Very low | L | **No (D)** |
| OCR hardening | Medium (pipeline exists, flaky) | M | P1 (fix config/provider first) |

---

## 23. Features to Remove / Merge / Simplify

1. **Remove** source-only dead UI/components after a final reference/build check: `manage-placeholder-page.tsx`, `future-capability-page.tsx`, `wip.tsx`, unused client helpers and imports. Treat apparently orphan HTTP endpoints (`PATCH questions`, subject/category writes) as **deprecation candidates**, not proven deletions, until access logs/external-client ownership are checked.
2. **Merge/retire** legacy console `/manage` tabs into the workspace (keep auth/audit/settings), remove `--` stat cards and FoldersTags placeholder.
3. **Retire** the legacy review chain (`/api/review/*`, `sm2.py`, `review_planner.py`, legacy weak-point retrieval) *after* public pages are wired to canonical data — do not delete public mistake content until a migration decision is recorded.
4. **Delete or wire** the stale redirect set `/write*` + `getContentEditHref→/manage/dashboard` once real editors exist; never ship a self-looping "写笔记" button.
5. **Remove** the "搜索(后续)" deferred nav tag — the page is fully implemented (`/manage/search`).
6. **Rename or re-scope** `/manage/jobs` & `/manage/analytics` (both currently reuse GovernanceOverview); either build real pages or move them under a single 治理 menu.
7. **Consolidate** duplicated reason/status label maps into one module; extract the 41× input literal into primitives.
8. **Delete** the AI polish bypass by routing it through the gateway (or disable polish).
9. If the home `LearningSpaceCard` counts stay unwired, **remove the card** until wired (R12).

---

## 24. Improvement Recommendations

Full detailed list with evidence, acceptance criteria and effort lives in `IMPROVEMENT_BACKLOG.md`. 35 recommendations: R01–R35. Headlines by tier:

- **P0** — R31 artifact-atomic releases; R01 review mastery/lapse; R02 type-aware re-answer; R03 restore note/blog authoring; R04 canonical-first mistakes/weak-points; R05 per-KP accuracy.
- **P1** — R06–R14 loop/AI/debt work; R32 guest schema ownership; R33 passkey/login/proxy hardening; R34 dependency/header/upload hardening.
- **P2** — R15–R22 consolidation, search, provenance, API and CI work.
- **P3** — R23–R28 and R30 UX/documentation debt; R29 and R35 are explicit defer decisions.

---

## 25. Recommendation Ranking (qualitative)

Value ≈ User Impact × Frequency × Strategic Importance; ROI = Value/Cost.

| Tier | Items | Rationale |
|---|---|---|
| **A — Now** | R31, R03, R01, R02, R04, R05 | Restore current usability, authoring and the learning loop; high frequency and high strategic value |
| **B — Next** | R06–R14, R32–R34 | Deepen the loop and close verified reliability/security/schema gaps |
| **C — Later** | R15–R28, R30 | Consolidation, UX depth and provenance after the core path is trustworthy |
| **D — Do not build yet** | R29, R35 | Analytics/advanced infrastructure/AI outputs are unproven at current scale |

---

## 26. Target Learning Workflow (not over-engineered)

```
打开系统 (/manage/dashboard)
  └─ 学习反馈: “今天 N 项到期复习 + 可做 M 题练习”
学习知识点（笔记 + 绑定 KnowledgePoint）
  └─ 在 /manage/knowledge-points 可看到该点关联的笔记/题目/错题
记录/录入：手动 或 /manage/capture 图片 → 题目
  └─ 完成题目 (Attempt, 自动判分)
      ├─ 答对 → 记录 Attempt(history)
      └─ 答错 → 自动生成 MistakeDraft（AI 预填错因）→ 快速确认 → Mistake + ReviewItem
复习 (/manage/review)
  └─ 先看题干 → 主动作答(可选)或自评 0–5 → 写 ReviewRecord
      └─ rating<3 → 间隔缩短/重置(repetitions 归零) → 3 天内再来
      └─ 连续成功 → interval 逐级 3/7/14/30… → 达到阈值 → state=mastered
掌握度变化 → Mistake 记录 mastery + 每 KP 聚合准确率
Dashboard 更新：due 数 / 薄弱 KP / 复习趋势
```

---

## 27. Target Information Architecture

**Keep (public layer, refactored onto canonical where relevant):** `/blog`, `/notes`, `/discover`, `/about`, `/guestbook`, `/music`, `/pictures` (decorative but personal; content-managed). Public `/mistakes` stays as a **curated showcase** fed from canonical mistakes with `visibility` intent, not legacy notes.

**Move/merge:** all authoring into the workspace (notes/blog editors as `/manage/notes[/{id}]` + blog tab or a unified 写作 item); retire `/write*`, `/mistakes/review`, legacy `/manage` console (auth/audit/settings absorbed by `/manage/settings` + workspace).

**Simplify:** `/manage/jobs`, `/manage/analytics`, `/manage/search` → one 治理/分析 entry until real pages exist; capture and drafts already merged conceptually (keep).

**Add:** a KP detail page (`/manage/knowledge-points/{id}` currently is an edit-only page; extend to "linked notes/questions/mistakes + accuracy"); a lightweight 今日任务 card that surfaces weakness-derived review targets.

**Delete (when safe):** orphan components/APIs, dead fallback JSON, unversioned polish bypass, unused nav flags.

Proposed workspace nav: 概览 · 写作(笔记/博客) · 题目 · 错题 · 复习 · 知识(科目/知识点) · 采集 · 附件 · AI · 设置. Remove: drafts as top-level? No — keep drafts (it is the triage hub), keep capture separate.

---

## 28. Top 10 Priorities

1. R31 — Restore artifact-atomic startup/deploy and add the chunk smoke test.
2. R03 — Restore a reachable note/blog authoring path and remove quick-action self-loops.
3. R01 — Add review lapse and graduation semantics.
4. R02 — Add type-aware re-answer with human confirmation for free text.
5. R04 — Move mistake/weak-point surfaces to one canonical source before retiring legacy.
6. R05 — Produce per-KP accuracy/weakness evidence for the dashboard.
7. R06 — Bind notes to KnowledgePoints.
8. R09 — Add the smallest daily practice surface that generates real Attempts.
9. R10 — Diagnose the 31/31 capture-recognition failures and preserve a manual fallback.
10. R22 — Put Vitest/test-typecheck and core-loop/browser-start smoke into CI.

---

## 29. 30-Day Improvement Plan

- **Week 1 — Restore trustworthy access (R31, R03, R23, R22 subset).** Fix the immutable build/start contract and chunk smoke first; restore one reachable note/blog editor path; add truthful public error/retry states. Acceptance: old and new releases stay loadable, authoring click-through works, API-offline pages never masquerade as empty.
- **Week 2 — Close review semantics (R01, R02).** Implement lapse reset/graduation and type-aware re-answer; keep free-text judgment human-confirmed. Acceptance: one browser/API fixture proves wrong→draft→mistake→re-answer→review history→graduation/lapse.
- **Week 3 — Establish one learning truth (R04, R05, R06, R09 smallest slice).** Read mistake/weak-point feedback from canonical records, bind notes to KPs, and add a minimal practice entry that creates Attempts. Do not delete legacy content until parity evidence and separate migration approval exist.
- **Week 4 — Reliability gate (R10, R22, then R32–R34 only within remaining capacity).** Diagnose provider/config before adding retries; wire full suites and browser-start smoke into CI; baseline guest schema ownership; remediate reachable high dependency/security findings. Defer polish, charts, graph/vector/FSRS and broad refactors.

After 30 days the loop should demonstrably close: a wrong answer → draft → mistake → reviews with lapses/graduations → dashboard shows per-KP accuracy and a concrete "today" plan.

---

## 30. Final Verdict

The engineering is ahead of the product. The repository contains a substantial formal learning domain, but the product cannot yet demonstrate a trustworthy daily practice→mistake→re-answer→mastery cycle and currently pays for two generations of data and UI. Restore a coherent runtime and authoring first, then close review semantics and consolidate feedback on canonical data. New AI, scheduling, analytics, or graph features have lower ROI until those facts change.

### The 10 questions, answered

1. **博客/笔记 or 个人学习系统?** A Hybrid: public blog/notes plus a private personal-learning-system MVP. The learning intent is clear, but actual use and feedback remain split across generations.
2. **最有价值三模块:** (1) atomic MistakeDraft→Mistake→ReviewItem conversion plus ReviewRecord history; (2) structured Subject/KnowledgePoint/Question model; (3) the typed API/auth/test foundation that lets those flows be changed safely. Capture is promising but not yet verified valuable because recorded recognition is 0/31.
3. **最薄弱三模块:** (1) current runtime/authoring accessibility; (2) review and practice semantics (no type-aware re-answer or mastery); (3) feedback/data ownership split (legacy vs canonical, plus guest schema outside owned migrations).
4. **学习闭环在哪断裂?** At review→mastery (no state), at mistake→objective re-answer (none), at content note→KP (never bound), and at feedback (canonical activity ignored by weak-point UI).
5. **Knowledge/Question/Mistake/ReviewItem 关系?** Question→KP ✔; Mistake→Question ✔; Mistake→ReviewItem 1:1 ✔ with ReviewRecord history ✔. Missing: any mastery value on Mistake; KP role unused; notes outside the graph; accuracy never aggregated per KP.
6. **Dashboard 帮助学习决策?** Partially — honest real-data counts and a deterministic "do X first" rule, but no weakness/accuracy/long-overdue signal, and its 快速开始 includes two self-looping actions.
7. **AI 创造价值?** Partially and not yet reliably. Recommendation/analyze runs have 10 successes, but the flagship capture-recognition history is 0/31, all 41 runs lack a target binding, display-only outputs are discarded, and polish bypasses governance.
8. **最大技术债三件:** (1) non-atomic frontend artifact/start process that can serve broken 200 pages; (2) legacy+canonical models, schedulers and feedback; (3) incomplete ownership boundaries—guest schema outside migrations plus orphan/deferred routes and APIs.
9. **只能开发 30 天，最值得做 10 件事:** see §28 Top 10.
10. **明确不应继续开发:** FSRS, vector search, knowledge-graph visualization/database, autonomous `knowledge_article`, mistake social export, background job infrastructure, gamification/new decorative modules, or chart-heavy analytics before canonical outcome data exists (R29/R35).
