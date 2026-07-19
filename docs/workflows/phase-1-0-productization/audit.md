# Current-State Audit

## Phase 0 Execution

Phase 0 was explicitly approved in conversation on 2026-07-17. Its scope is limited to P0-01 through P0-05.

## P0-01 Git And Architecture Baseline

- Branch: `notes-workspace-ux-upgrade`.
- HEAD: `939ad1fa68afb73ca20c266993c1f51c62b3ad98`.
- Upstream relation reported by Git: `notes-workspace-ux-upgrade...mine/notes-workspace-ux-upgrade [ahead 3]`.
- Worktree baseline: all visible changes are untracked documentation/artifact files under `docs/project-assessment/`, `docs/workflows/mvp-goal-gap-analysis/`, and `docs/workflows/phase-1-0-productization/`; no tracked source diff was present at capture time.
- Pre-existing untracked scope: `docs/project-assessment/mvp-gap-analysis.md` and `docs/workflows/mvp-goal-gap-analysis/` existed before Phase 0 execution and are preserved as separate artifacts.
- Current Phase 0 scope: `docs/workflows/phase-1-0-productization/` plus the canonical baseline that P0-05 will publish under `docs/releases/`.

Architecture remains split into two active lines:

1. Next.js App Router frontend and original public/static-blog line under `src/`.
2. FastAPI/PostgreSQL personal-learning backend under `backend/`.

Route inventory confirms both legacy/public and newer manage-workspace surfaces coexist:

- Public/legacy examples: `/`, `/blog`, `/notes`, `/notes/[id]`, `/mistakes`, `/mistakes/review`, `/write-note`, `/write-mistake`.
- Manage workspace: `/manage/dashboard`, `/manage/drafts`, `/manage/questions`, `/manage/mistakes`, `/manage/review`, `/manage/attachments`, `/manage/capture`, `/manage/ai`, `/manage/settings`, plus search/analytics/jobs and taxonomy pages.
- Backend routers include auth, notes, subjects, knowledge points, drafts, questions, mistake drafts, admin mistakes, review items, attachments/links, captures, AI/runs, audit and legacy content domains.

P0-01 conclusion: `PASS`. The current repository shape and dirty-tree boundary are recorded without changing or reclassifying user artifacts.

## P0-02 Database And Storage Baseline

Alembic read-only evidence:

- Current: `020 (head)`.
- Heads: `020 (head)`.
- History confirms `019 -> 020` is the current migration and revision 018 is historical.
- `alembic check`: `FAIL` because ORM metadata proposes removing three current knowledge-point indexes and adding `uq_knowledge_points_sibling_name`. This is recorded as schema drift; Phase 0 did not create or run a migration.

Core database counts:

| Table | Count | Representative ID fingerprint |
|---|---:|---|
| subjects | 1 | `13671077b66a` |
| knowledge_points | 3 | `6f4b6612125f` |
| question_drafts | 3 | `e3c573c9d88b` |
| questions | 3 | `f79186dc68a1` |
| mistake_drafts | 3 | `c5dad2aedc52` |
| mistakes | 3 | `e7a5433848bb` |
| review_items | 3 | `819025612a6e` |
| review_records | 4 | `7df9974ab15c` |
| attachments | 1 | `f9cdb6f6706c` |
| attachment_links | 1 | — |
| capture_items | 0 | — |
| ai_runs | 29 | — |

The fingerprints are truncated SHA-256 values derived from representative IDs; raw private identifiers are intentionally not copied into the release report.

Attachment storage evidence:

- Database: 1 active, local, private attachment; 264 bytes.
- Storage: 1 payload file; 264 bytes; repository placeholder excluded.
- Integrity: 1/1 checksum match; 0 missing database files; 0 orphan payload files.
- Manifest SHA-256: `d467b84f74781c449158a4a21387c8e1ec4a91c43d6e1aa5339a2d39b0cddd3c`.
- Storage root exists and is within the configured backend upload boundary; its absolute path and private storage key are omitted.

All SQL ran in an explicit read-only transaction and was rolled back. P0-02 conclusion: `PARTIAL` because revision/count/storage evidence passed, while `alembic check` exposed non-blocking schema metadata drift. Historical revision 018 restore evidence is not current revision 020 restore proof.

## P0-03 UI And Demo Baseline

Capture context:

- Captured: `2026-07-17 18:18 CST`.
- Frontend origin: local existing development instance on port 2025.
- Backend origin: local existing FastAPI instance on port 8000.
- Browser: fresh anonymous automated Chromium session; no saved credentials, no `AUTH_BYPASS`.
- Viewports: desktop `1280×720`; mobile home `390×844`.

Screenshot index:

| Surface | Login state | Artifact | Result |
|---|---|---|---|
| Home desktop | anonymous | `assets/2026-07-17-home-desktop-1280x720.png` | INVALID RENDER — blank/black state |
| Home mobile | anonymous | `assets/2026-07-17-home-mobile-390x844.png` | INVALID RENDER — blank state |
| Blog desktop | anonymous | `assets/2026-07-17-blog-anonymous-desktop-1280x720.png` | INVALID RENDER — loading artwork only |
| Notes desktop | anonymous | `assets/2026-07-17-notes-anonymous-desktop-1280x720.png` | INVALID RENDER — loading artwork only |
| Mistakes desktop | anonymous | `assets/2026-07-17-mistakes-anonymous-desktop-1280x720.png` | INVALID RENDER — loading artwork only |
| Manage desktop | anonymous | `assets/2026-07-17-manage-anonymous-desktop-1280x720.png` | INVALID RENDER — loading state only |
| Manage workspace pages | authenticated admin | not captured | BLOCKED — no real admin session |

The documents for `/`, `/blog`, `/notes`, `/mistakes`, and `/manage` returned HTTP 200, but the browser network log showed HTTP 500 for the generated `_next` CSS and JavaScript chunks, plus a 500 for the optimized avatar request. The rendered body remained `加载中...` or blank. These screenshots are current failure evidence, not visual-acceptance proof.

The prior 10–15 minute demo flow remains documented in `docs/workflows/mvp-local-trial-acceptance/demo-script.md`: Public Read → Private Manage → Core Learning Loop → Attachment/Closure Evidence. It is not executable against the current local frontend instance until the chunk-serving failure is resolved or a clean runtime is established. No cache deletion, process termination, code fix, login, or write action was performed during Phase 0.

P0-03 conclusion: `PARTIAL / BLOCKED`. Artifacts and runtime failure evidence were saved, but valid rendered public screenshots and authenticated management screenshots are unavailable.

## P0-04 Issue And Deferred-Capability Reconciliation

### LT-ISSUE-002

Current source catches malformed/disabled password hashes at `verify_password()` and returns `False`; the login route maps this to `401 Invalid credentials`. The dedicated regression suite passed on 2026-07-17: `2 passed` in `tests/test_auth_error_handling.py`.

Canonical status for Phase 0: `FIXED IN CODE AND TESTS / CURRENT LIVE ACCOUNT SCENARIO NOT RE-EXECUTED`. Old checklist, trial-record, demo-script, and early validation paragraphs that still say “500/open/conditional” are historical evidence, not current status. Gate B must still run the approved auth matrix with controlled credentials before Production Ready can be claimed.

### Capability map

| Capability | Current factual status | Evidence and boundary |
|---|---|---|
| AI Gateway/model abstraction | COMPLETE infrastructure | `ai_gateway.py` exposes text/vision/general/stream paths; historical real-provider and fallback evidence exists. |
| Prompt registry/standardization | COMPLETE infrastructure | Prompt registry/standard modules and Batch 10 workflows exist. No current editable Prompt management product UI was established in this audit. |
| AI call/run tracking | COMPLETE backend, PARTIAL product surface | `ai_call_logs`/`ai_runs` exist and DB has 29 runs; backend lifecycle and review were previously validated. Current `/manage/ai` and `/manage/ai/runs` route files are placeholders that explicitly do not read records. |
| AI-generated draft workflow | PARTIAL | Capture recognition/draft services call the Gateway and validate structured suggestions; AI remains advisory and human confirmation is the formal-data boundary. Current main Capture page is a placeholder. |
| Capture domain/API | PARTIAL | Model, schema, service, admin API and a substantial `CaptureWorkspace` component exist, but `/manage/capture/page.tsx` renders a placeholder and current DB has 0 capture rows. |
| Image input/import workflow | PARTIAL | Private attachment upload and CaptureWorkspace upload code exist; the active route does not expose the workspace. |
| Real OCR/multimodal provider | DEFERRED / NOT CURRENTLY VERIFIED | A `call_vision` implementation path exists and historical provider proof exists, but the current route says OCR/Capture is not enabled and Phase 0 made no provider call. |
| Human confirmation after OCR/AI | PARTIAL | Conversion contracts and component code exist; active-route browser proof is unavailable and current route is placeholder. |
| Learning Analytics | DEFERRED / MISSING product | `/manage/analytics` is a static placeholder; target metric tables are architecture-only and no current implementation was found. |
| BKT/mastery | DEFERRED | Architecture explicitly postpones BKT; no BKT/mastery implementation or current tables were found. |

The key reconciliation is therefore not “AI/OCR absent.” Infrastructure and hidden/inactive workflow code exist, while the active management routes still present those capabilities as disabled. This is product-surface and route-ownership drift, not proof of an enabled daily workflow.

P0-04 conclusion: `PASS` for state reconciliation. No provider call, auth-account mutation, migration, feature activation or route change was performed.

## P0-05 Baseline Publication

The canonical release baseline was published at `docs/releases/v1.0-baseline.md`. It contains the Git identity, revision, core counts, attachment integrity, route/core-flow summary, screenshot index, Demo boundary, capability classification, known issues, deferred scope and Gate recommendation.

Phase 0 final result: `PARTIAL / CONDITIONAL`.

- PASS: Git/architecture inventory, database counts, attachment integrity, issue/capability reconciliation and baseline publication.
- PARTIAL: `alembic check` reports schema metadata drift.
- BLOCKED: valid browser rendering and authenticated management screenshots because the current local frontend chunks return HTTP 500 and no real admin session was available.

Gate recommendation: do not automatically enter Phase 1.0A or 1.0B. A new approval should first acknowledge the clean-runtime prerequisite, schema-authority risk and current evidence gaps.

## Historical Planning Snapshot

- Phase 1.0 productization planning started after the user approved beginning the next stage.
- This file fed the v1.0 runtime baseline; Gate 0 is complete and its evidence appears above.
- Current worktree already contains untracked files under:
  - `docs/project-assessment/mvp-gap-analysis.md`
  - `docs/workflows/mvp-goal-gap-analysis/`
- Those files are user/current-session artifacts and must be preserved.

## Historical Phase 0 Planning Assumptions

- Existing acceptance documents report Alembic `020 (head)` and a completed manual core learning loop.
- `LT-ISSUE-002` is marked `fixed-in-separate-workflow` in `issues.md`, while older summary/risk paragraphs still contain stale unresolved wording.
- Historical Phase D-4 backup/restore proof is for revision `018`, not automatic proof for current revision `020`.
- The UI review found strong public visual consistency but current product-state drift:
  - mobile home lacks an obvious navigation path at 390px;
  - Dashboard still advertises `Coming Soon` / static shell;
  - Drafts and Capture are absent from the main manage sidebar;
  - some active/deferred routes and Chinese/English labels are inconsistent.

These assumptions were resolved by P0-01 through P0-05 and are retained only as planning history.

## No-change Statement

No business code changed. No schema or migration changed. No database or production data changed. No deployment or runtime configuration changed.

## Phase 0.5 Planning Record

- Source risk: `RISK-P10-009`.
- Canonical plan: `phase-0-5-runtime-recovery-gate.md`.
- Requirements: `REQ-P05-001` through `REQ-P05-005`.
- Tasks: P05-01 through P05-05.
- Current status: `APPROVED / IN PROGRESS`; P05-01 through P05-03 passed.
- Authorized planning changes: workflow documentation only.
- Runtime/process/cache/source/config/dependency/lockfile/database/migration changes: none.

## P05-01 Frontend Runtime Audit

Phase 0.5 was explicitly approved on 2026-07-17 for P05-01 through P05-05.

Runtime ownership and versions:

- Port 2025 listener: PID `19659`, cwd is this repository, command identifies `next-server`.
- Parent: launchd; stdout/stderr: `/private/tmp/blog-frontend.log`.
- Process age at audit: approximately 19 hours.
- Running Next version from process/log: `16.0.10`.
- Current installed and package-lock Next version: `16.2.10`.
- Authoritative lockfile found: `package-lock.json`; package manager field is unset and no competing lockfile was found.
- Node: `v26.0.0`; npm: `11.12.1`.
- `NEXT_PUBLIC_API_URL` is present in development and production environment files; values were not printed.

Failure reproduction:

- `/` document: HTTP 200.
- The document referenced 17 first-party `_next/static` JS/CSS files.
- All 17 returned HTTP 500.
- None of the 17 referenced filenames existed in the current `.next/static/chunks` output.
- Current `.next/BUILD_ID`: `exdOhE1rN8DmxqJyDP2Us`.
- Runtime log separately reports Next image optimization failing for `/images/avatar.png` with `handleRequest is not a function` and HTTP 500.

Root-cause conclusion: `CONFIRMED runtime/build-output mismatch`. A long-lived Next 16.0.10 process is serving HTML with obsolete chunk hashes while the repository dependency and current `.next` output are Next 16.2.10. This is a generated-runtime mismatch, not evidence that source files must be edited.

Pre-recovery data guard:

- Alembic: `020 (head)`.
- Counts: subjects 1; knowledge points 3; question drafts 3; questions 3; mistake drafts 3; mistakes 3; review items 3; review records 4; attachments 1; attachment links 1; capture items 0; AI runs 29.
- Query mode: explicit read-only transaction, rolled back.

P05-01 result: `PASS`. No process, cache, source, config, dependency, lockfile, database or migration change was made.

## P05-02 Clean Build Recovery

- Initial direct PID termination was followed by an immediate launchd restart, confirming `com.blog.frontend` is a KeepAlive service.
- LaunchAgent ownership was verified: it runs only this repository's `scripts/start-frontend.sh`, which executes `next start -p 2025`.
- The project frontend LaunchAgent was booted out before generated-output handling; backend and unrelated processes were not stopped.
- Previous generated output was quarantined at `/private/tmp/2025-blog-public-next-quarantine-20260717-183153`.
- `npm run build`: exit 0 on Next `16.2.10`; compilation, TypeScript, page-data collection and 40/40 static pages passed.
- Non-blocking build warning: Node reports deprecated `module.register()` usage from the current toolchain.
- New build ID: `cjCI0LBekoSFV0Hvxxa__`.
- The same `com.blog.frontend` LaunchAgent was bootstrapped again; new PID `55116`, Next `16.2.10`, repository cwd, port 2025.
- Direct post-start probe: `/` document 200; 16 requested JS/CSS chunks, 16 returned 200, 0 failures.
- Git scope remained documentation-only; `.next` is generated/ignored and no source, config, dependency or lockfile change appeared.

P05-02 result: `PASS`. Clean production build/runtime recovered without source/config/dependency/database/migration changes.

## P05-03 Browser Verification

Fresh anonymous Chromium sessions verified `/`, `/blog`, `/notes`, `/mistakes`, and `/manage` at both `1280×720` and `390×844`. All ten combinations reached a complete document state, rendered non-empty interactive DOM, left no permanent loading state, and produced zero browser runtime errors and zero console messages/errors. Fresh screenshots are stored under this workflow's `assets/` directory with the `2026-07-17-p05-*` prefix.

Hydration was verified through an attached React component tree and a harmless client interaction on `/blog`: selecting the `月` filter changed the button to its selected client state without navigation, blanking, loading regression or console error.

Anonymous `/api/auth/me` requests returned the expected remote 401 without UI or console failure. Desktop home also issued a speculative RSC prefetch to one unavailable mistake-detail path and received 404; this did not affect the page document, generated chunks, static assets, hydration or visual result and is retained as a non-blocking product-route observation.

P05-03 result: `PASS`. No mock, authentication bypass, write operation, source change, database operation or migration was used.

## P05-04 Asset Loading Validation

Direct document parsing and HTTP probes verified every target route's referenced first-party production bundles: `/` loaded 15/15 JS and 1/1 CSS, `/blog`, `/notes`, and `/mistakes` each loaded 14/14 JS and 1/1 CSS, and `/manage` loaded 15/15 JS and 1/1 CSS. All five documents returned 200.

Critical assets also returned 200 with valid content types: `/favicon.png`, `/manifest.json`, `/images/avatar.png`, `/images/cursor.svg`, and Next-optimized avatar requests at widths 32, 48, and 64. Browser DOM inspection found zero incomplete or zero-natural-width images across the five target routes. No first-party font files were requested; the configured web-font stylesheet is third-party and outside the first-party acceptance boundary.

`/favicon.ico` returns 404 but is not referenced by page metadata; the referenced `/favicon.png` passes. P05-04 result: `PASS`. No asset was hidden, replaced, mocked or modified.

## P05-05 Environment Closure

Final runtime identity: PID `55116`, Next `16.2.10`, repository cwd, port 2025, active build ID `cjCI0LBekoSFV0Hvxxa__`, managed by the existing running `com.blog.frontend` LaunchAgent. Backend `/api/health` returned 200 with both application and database status `ok`.

Post-recovery Alembic current and heads both remain `020 (head)`. The explicit read-only count transaction returned the exact pre-recovery values: subjects 1; knowledge points 3; question drafts 3; questions 3; mistake drafts 3; mistakes 3; review items 3; review records 4; attachments 1; attachment links 1; capture items 0; AI runs 29. The transaction was rolled back; no DML, DDL or migration ran.

Git scope contains only the existing untracked assessment, release and workflow documentation/artifacts. No tracked source, config, dependency or lockfile diff exists. Temporary browser sessions were closed. The old generated output remains quarantined at `/private/tmp/2025-blog-public-next-quarantine-20260717-183153` for reversible cleanup.

Phase 0.5 final result: `PASS`. `RISK-P10-009` is resolved and the frontend-runtime blocker is removed. This result does not authorize Phase 1.0A, Phase 1.0B, RC or Phase 1.0C.

## Phase 1.0A Execution

Gate A was explicitly approved on 2026-07-19 for A-P0-01 through A-P0-06 and A-P1-01 through A-P1-03.

### A-P0-01 Mobile Home Navigation

The existing mobile navigation was extended to the home route. Public destinations render immediately; the management destination is appended only after `useAdminAuth` confirms an administrator. The page does not wait for that check before rendering public navigation, and write routes remain excluded. A focused behavior suite passed 2/2. Final 390px browser and auth-noise evidence is assigned to A-P0-06.

### A-P0-02 Dashboard Data Contract Audit

Questions, mistakes, knowledge points and attachments expose admin list APIs without aggregate totals. The review queue exposes due items, but review records are available only per review item. Reusing these contracts would require several unbounded list requests and an N+1 path for recent review activity, while producing no single snapshot time.

The frozen decision is an additive, admin-only, read-only `GET /api/admin/dashboard/summary` endpoint with bounded recent lists, aggregate counts, a generated timestamp and safe service/database/storage status. It uses existing tables, adds no schema or migration, and never exposes filesystem paths or secrets. A-P0-02 result: `PASS`; implementation is assigned to A-P0-03.

### A-P0-03 Dashboard Implementation

The frozen contract is implemented through a thin admin router, Pydantic response schema and dashboard service. Aggregate counts are collected in one SQL statement, recent lists are bounded to five, and recent review activity joins back to its mistake question without per-item requests. The frontend consumes one typed API client and renders a restrained operational surface: today's due work, latest mistake, content counts, recent questions/reviews and safe system status.

The Dashboard no longer contains `Coming Soon`, `No API connected` or `Static shell`. Backend tests passed 2/2, the focused frontend behavior test passed 1/1, and TypeScript passed. No table, migration, seed or production data changed.

### A-P0-04 Manage Navigation

Desktop and mobile management navigation now share a product-oriented information architecture: 学习空间, 内容管理, 知识体系, 学习计划, 资料管理, 工具 and 系统. Drafts and Capture are first-class entries, so the visible path now includes 草稿 → 题目 → 错题 → 复习. Existing Subjects/Knowledge Points remain discoverable. Search, Analytics and Jobs were not deleted; they moved to the lower-weight 后续能力 group pending the route-state audit in A-P0-05. Navigation tests passed 6/6.

### A-P0-05 Capability State Closure

The route audit separates implemented infrastructure from enabled product behavior. Drafts is active because its existing workspace reads both question and mistake draft APIs and supports human review. Capture, AI/AI Runs, Search, Analytics and Jobs remain deferred. Their route files are retained, but product copy is now Chinese and explicitly states that the current version does not read, invoke, generate, poll or simulate those capabilities. Deferred navigation entries carry a `后续` label. No AI/OCR provider call, analytics schema, worker, route deletion or migration was introduced. Focused state/navigation tests passed 13/13.

### A-P1-01 Controlled Feature State

`FeatureState` now provides one discriminated management UI contract for labelled skeleton loading, actionable empty, retryable error and explicitly deferred states. Deferred is not represented as empty, and loading does not use a permanent generic text message. The component remains under the manage domain because no public route consumes it in this Gate. Focused tests passed 3/3.

### A-P1-02 Core Page State Adoption

Dashboard, Drafts, Questions, Mistakes, Review and Attachments now use the controlled state component for their applicable loading, empty and error states. Retry actions call the real page loaders rather than only changing presentation. AI, Capture, Search, Analytics, Jobs and shared future-capability pages use the deferred state. Focused state suites passed 15/15 and TypeScript passed. Specialized detail/editor loading states remain outside the selected core-page scope.

### A-P1-03 Chinese Product Language and Display

Management product headings and selected core list/detail metadata now use Chinese display terms. A single render-layer helper maps existing question, difficulty, status and attachment enum values without changing backend or frontend API contracts. Dates use one full Chinese convention and a fixed Asia/Shanghai product timezone. The root document language is `zh-CN`.

During this closure audit, the Drafts list was confirmed active but its linked detail route still rendered a Batch 1 static placeholder. The route now invokes the existing `DraftEditor`, aligning the visible flow with the already-approved Draft capability; no new endpoint, schema, migration or deferred capability was activated. Helper tests passed 2/2, focused Dashboard/Drafts regressions passed 6/6, and TypeScript passed. A-P1-03 result: `PASS`.

### A-P0-06 Gate A Closure

Gate A passed real Chromium verification at desktop and 390×844. Anonymous home renders public navigation immediately and hides 管理; authenticated management renders real Dashboard counts/activity, grouped navigation, active Draft list/detail and explicit deferred Capture state. No browser console error, hydration failure, first-party asset failure or horizontal layout blocker was observed.

Final verification passed frontend 39/39, backend 246/246, TypeScript and a clean Next.js 16.2.10 production build. The existing LaunchAgent serves build `U8aVfvseH5-5uScRCbhnl` with document 200. Alembic remains `020 (head)` and final database counts match baseline. Temporary auth and browser-triggered validation rows were precisely removed; no user business record, schema or migration remains changed.

Gate A final result: `COMPLETE / PASS`. Gate B, RC and Gate C remain outside current authorization.

## Phase 1.0B Execution

Gate B was explicitly approved on 2026-07-19 for B-P0-01 through B-P0-06 and B-P1-01 through B-P1-02. RC and Gate C remain not authorized.

### B-P0-01 / B-P0-02 Auth Regression

The controlled current-version matrix passed anonymous, valid administrator, revoked, expired, disabled-password and public-read boundaries. LT-ISSUE-002 did not reproduce: the disabled account returned 401 rather than 500. `AUTH_BYPASS` was inactive. Temporary database fixtures were removed and users, admin_sessions and audit_logs counts matched before/after values exactly. B-P0-02 therefore required no Auth code change.

### B-P0-03 PostgreSQL Backup

A revision `020` custom-format backup was generated outside the repository at `/Users/limengyang/.codex/backups/2025-blog-public/phase-1-0b/blog_db-phase-1-0b-rev020-20260719T112321+0800.dump`. Its SHA-256 is `1f7c9ba0965365fca13f30932884b69d8cda251a76400904c38dc34eb33c8b79`; `pg_restore --list` passed. The read-only source count snapshot matches the Gate A closure baseline. No DDL, DML or migration ran against the source database.

### B-P0-04 Attachment Backup

The complete configured upload root was archived outside the repository with a per-file TSV manifest. The archive SHA-256 is `beb4809c54f2c02219f84c686bdb60ec3d6f0b4cd8e96f080ef9fdbb662b76be`; the manifest SHA-256 is `906693fd5694339d44a96935e040c34962aea6f562302f9e54c5312378f32715`. The one active attachment row matches its file by storage key, byte count and content checksum. No attachment or database row changed.

### B-P0-05 Isolated Restore

The database and attachment archives were restored into a temporary PostgreSQL cluster and temporary upload root. The restored database reports `020 (head)`, all selected domain counts equal the backup snapshot, and the restored attachment matches its database key, byte count and checksum. FastAPI completed its revision readiness check; `/api/health` and public `/api/notes` both returned 200. The source database's revision and selected counts were identical before and after. Temporary processes and directories were removed. No source migration or mutation occurred.

### B-P1-01 Monitoring Audit

Current monitoring is incomplete: public health exposes a DB field while still reporting overall `ok` on DB failure; Dashboard diagnostics hard-code DB success, only test Storage directory existence, and omit Auth; no request correlation or uniform safe unhandled-error record exists. B-P1-02 is therefore required. Its frozen scope is additive admin diagnostics plus request observability and a simplified public health response, with no schema, migration, third-party monitor or sensitive request capture.

### B-P1-02 Monitoring Implementation

Public health now reports only overall service availability. `GET /api/admin/diagnostics` is protected by `get_current_admin` and returns bounded DB, Storage and Auth states without paths or configuration details. Every HTTP response receives a server-owned UUID request ID. Unhandled exceptions return a generic 500 and log only route template, UTC timestamp, request ID, anonymized actor hash, exception class and a fixed summary; exception messages, headers, cookies, bodies and query strings are not recorded by this boundary. Seven focused tests and live anonymous/authenticated probes passed. No table, migration or external monitoring dependency was added.

### B-P0-06 Gate B Final Assessment

All approved Gate B tasks are complete. Auth regression, revision `020` backup, attachment archive, isolated restore, monitoring, full tests, TypeScript, production build, production runtime and final database baseline passed. The recovery procedure is documented in `recovery-runbook.md`.

Gate B cannot receive an unconditional release pass. `alembic check` still detects the known knowledge-point authority mismatch: the database contains three indexes not represented by current ORM metadata, while ORM metadata proposes a different sibling-name unique constraint. Gate B did not authorize a schema decision, DDL or migration. The correct result is therefore `COMPLETE / CONDITIONAL PASS`, with `RISK-P10-008` remaining a Production Ready and RC blocker. RC and Gate C remain not authorized.

## 2026-07-19 Goal Reconciliation — Read-only

This reconciliation reviewed the existing Phase 1.0 workflow, the dirty worktree, RISK-P10-008 and the remaining approval gates before any new task execution.

| Area | Current evidence | Result |
|---|---|---|
| Dirty worktree | Contains the already-recorded Gate A/B source and document changes plus untracked workflow/source files. No reset, cleanup, staging or source modification was performed by this reconciliation. | PRESERVED |
| Gate B | Approved task evidence remains complete, including revision-020 backup/isolated restore and runtime checks. | COMPLETE / CONDITIONAL PASS |
| Alembic revision | `current` and `heads` both report `020 (head)`. | PASS, not sufficient alone |
| Alembic metadata check | Current command exits nonzero: three database knowledge-point indexes are proposed for removal and lifecycle metadata proposes `uq_knowledge_points_sibling_name`. | FAIL / RISK-P10-008 OPEN |
| Schema lifecycle entrypoints | Startup is read-only revision readiness; Alembic points to explicit lifecycle metadata and excludes governed guest tables. This is architectural evidence only. | PARTIAL / NOT ACCEPTANCE |
| Schema Authority | No user choice between existing database contract, ORM sibling-name contract, or an explicit compatibility contract was found. | NOT AUTHORIZED |
| RC Gate | No separate RC approval found. | NOT AUTHORIZED / BLOCKED by RISK-P10-008 |
| Gate C | No RC PASS or standalone Learning Feedback approval found. | DEFERRED / NOT AUTHORIZED |

No database changes executed. No migration executed. No production data modified. No backup/restore, fixture cleanup, process stop, deployment, push or destructive operation was executed in this reconciliation. The remaining work is now decomposed in `requirements.md`, `design.md` and `tasks.md`; implementation must wait for explicit approval of the relevant Gate and task IDs.

## 2026-07-19 SA-P0-01 — SA-A Decision and Compatibility Preflight

User decision and approval: **SA-A — the existing database indexes and hierarchical uniqueness semantics are authoritative.** This task was documentation and read-only evidence only.

| Contract area | Authoritative database fact | Metadata implication |
|---|---|---|
| Tree lookup | `idx_knowledge_points_parent` on `parent_id` | Retain as an ORM index |
| Ordered tree lookup | `idx_knowledge_points_subject_parent_sort` on `(subject_id, parent_id, sort_order, id)` | Retain as an ORM index |
| Historical ordered subject lookup | `idx_knowledge_points_subject_sort` on `(subject_id, sort_order, id)` | Retain as an ORM index |
| Root names | `uq_knowledge_points_root_name`: unique `(subject_id, lower(name))` where `parent_id IS NULL` | Model as a case-insensitive partial unique index, not a nullable unique constraint |
| Child names | `uq_knowledge_points_child_name`: unique `(subject_id, parent_id, lower(name))` where `parent_id IS NOT NULL` | Model as a case-insensitive partial unique index, not a nullable unique constraint |

The source model currently declares one case-sensitive `uq_knowledge_points_sibling_name`. It does not match SA-A: PostgreSQL unique constraints permit multiple `NULL` values and it lacks `lower(name)` normalization. Read-only duplicate-group preflight returned `0` root groups, `0` child groups and `3` total knowledge-point rows. No row content, identifiers, database URL or credentials were recorded.

No database changes executed. No migration executed. No production data modified. No source code modified. SA-P0-02 remains unapproved.

## 2026-07-19 SA-P0-02 — SA-A Metadata Alignment

Scope: test-first, source-only metadata/service alignment; no DDL, migration or data write.

| Evidence | Result |
|---|---|
| Root case-variant create RED | Reproduced a physical `uq_knowledge_points_root_name` violation leaking past the service conflict boundary |
| Child case-variant rename RED | Reproduced a physical `uq_knowledge_points_child_name` violation leaking past the service conflict boundary |
| Minimal service alignment | PASS — create/update duplicate prechecks use database-equivalent lower-name comparison and retain `TaxonomyConflict` behavior |
| Lifecycle metadata alignment | PASS — adds SA-A's three query indexes and two partial expression unique indexes; removes incompatible nullable sibling constraint |
| Targeted metadata/service tests | PASS — 3/3 |
| Full taxonomy suite | PASS — 10/10 |
| Alembic | PASS — current/heads `020 (head)`; check reports no upgrade operations |
| Guest lifecycle exclusion | PASS — zero governed guest tables present in lifecycle metadata |
| Post-test knowledge-point count | PASS — `3` |
| DDL / migration / DML | NONE |

The first targeted pytest invocation lacked the repository-required `PYTHONPATH=.` and did not collect tests. The corrected invocation was used for all RED/GREEN and final results. A transient `NameError` from removing a shared `UniqueConstraint` import was corrected before the final GREEN run; no data action occurred. SA-P0-02 is complete. SA-P0-03 must now record whether its conditional DDL/migration path is required.

## 2026-07-19 SA-P0-03 — DDL/Migration Applicability

Result: **NOT REQUIRED / PASS**. SA-A changes only the application lifecycle metadata and the service's existing conflict precheck so that both describe the already-present physical database contract. The final `alembic check` has no upgrade operations, `current` and `heads` remain revision `020`, and no backup/restore boundary changed. No migration or DDL plan was created or executed; no backup refresh or isolated restore exercise was warranted.

## 2026-07-19 SA-P0-04 — Schema Authority Closure

Schema Authority Gate result: **COMPLETE / PASS**. Final read-only evidence: HEAD `939ad1fa`; `current`/`heads` `020 (head)`; `alembic check` no upgrade operations; core counts `1/3/6/3/3/3/1` for subjects/knowledge-points/knowledge-point-links/questions/mistakes/review-items/attachments. SHA-256 fingerprints for the modified taxonomy model, taxonomy service and taxonomy tests are recorded in `validation.md`.

No migration or DDL was necessary: the selected SA-A contract was already physically present, and only lifecycle metadata/service prechecks were aligned. Because neither revision nor recovery boundary changed, the Gate B revision-020 backup and isolated restore evidence remains valid without regeneration. `RISK-P10-008` is closed. Known warning: Alembic emits non-actionable SERIAL sequence detection lines before its PASS result.

## 2026-07-19 RC-P0-01 — Recovery Evidence Applicability

Result: **NOT REQUIRED / PASS**. The final SA-A source alignment left physical schema, Alembic revision and recovery boundary unchanged. Fresh `current`/`heads` remain `020 (head)` and `check` has no upgrade operations. Gate B's revision-020 backup pair and isolated PostgreSQL/temporary-storage restore therefore remain the applicable restore proof. No archive, restore, source database, attachment storage, process or temporary fixture was touched for this RC item.

## 2026-07-19 RC-P0-03 — Full Command Validation

| Check | Result |
|---|---|
| Frontend `npm test` | PASS — 39/39 |
| Backend `PYTHONPATH=. .venv/bin/pytest -q` | PASS — 256/256; 2 known AsyncMock warnings |
| `npx tsc --noEmit` | PASS |
| `npm run build` | PASS — 40/40 pages; local-only invalid API build value used to satisfy the production guard without contacting an API |
| Alembic current / heads / check | PASS — `020 (head)` / `020 (head)` / no upgrade operations |
| `git diff --check` | PASS |

The first frontend invocation incorrectly added Vitest-unsupported `--runInBand`; no test ran in that command. The immediately corrected project command is the passing evidence. Full pytest generated exactly two validation-owned AI runs, two logs and one recommendation in addition to its pre-run baseline; all were deleted by exact ID and final `ai_runs`/`ai_call_logs`/`recommendations` counts are `29/44/27`. Temporary RC users/sessions are `0/0`.

## 2026-07-19 RC Runtime Evidence Audit

The RC browser used a fresh local `localhost` frontend paired with the local FastAPI backend, avoiding the existing production-runtime external API origin. Anonymous public reads were successful and management access was redirected until a short-lived real administrator session was supplied. The session was not an authentication bypass.

The protected API matrix returned 200 for Health, diagnostics, Dashboard, Questions, Mistakes, Review items and Attachments. The management Dashboard, Questions, Mistakes, Review and Attachments routes rendered under that session. A real HTTP learning chain created a temporary question, created and converted its mistake draft, submitted a review, and read back one review record. All resulting records, the administrator, and its session were selected and deleted by exact identifiers; post-cleanup core counts returned to `questions/mistakes/review-items/review-records = 3/3/3/4` and `ai-runs/logs/recommendations = 29/44/27`.

Anonymous desktop and 390px evidence is retained in the two sanitized assets listed in `validation.md`. A direct resource probe found the document and 23 referenced first-party JS/CSS resources at 200. Fresh-session browser errors were empty; the interactive mobile navigation state change provides hydration evidence.

## 2026-07-19 RC-P0-05 Code Quality Audit

Scoped review of the SA-A source diff found the ORM index declarations, service case-normalization checks and focused tests mutually consistent with the approved physical database contract. The review did not identify an additional reproducible defect, so no speculative refactor was performed. Final `git diff --check` passed.

## 2026-07-19 Gate C Minimal Feedback Audit

Gate C implementation is confined to the existing protected Dashboard component and its test. The added pure derivation consumes only `due_reviews`, `mistakes` and `questions` from the existing summary, emits one honest next-step message and links to existing management routes. It introduces no API call, model, schema, migration, storage operation, telemetry, AI call, recommendation row or public surface.

## 2026-07-19 Gate C Closure Audit

Fresh anonymous and real-administrator browser sessions verified that protected Dashboard feedback remains private and that the real priority-one action targets the review route. `AUTH_BYPASS` was not used. Full regression then passed: frontend 43/43, backend 256/256, TypeScript, production build, Alembic current/heads/check and diff hygiene. The shared backend test path generated one validation-owned AI run/log; both were deleted by exact identifier and verified absent. Final counts and all RC fixture-user/session checks match the recorded baseline.

Conclusion: Demo Ready and Personal Use Ready are **YES** for the approved v1.0 scope. Production Ready is **CONDITIONAL / NOT CLAIMED**, because no deployment or production-data verification was authorized and separate security/service readiness remains outside scope.

## 2026-07-19 Production Startup Security Follow-up

The review finding was reproduced in the application lifespan: production previously blocked default JWT and unsafe CORS with `SystemExit`, but did not reject the active dual bypass configuration. The scoped fix evaluates the dual bypass with the same case-insensitive semantics as the auth router and rejects it before database readiness. All three production-insecure conditions now use `RuntimeError`, producing one framework-standard startup-failure boundary. Diagnostics remains warning-only by design; it is observability, not the enforcement point.

Full verification passed: targeted startup/monitoring tests 11/11, backend suite 260/260, Alembic current/heads/check at `020 (head)`, and `git diff --check`. The shared full-test path generated one validation-owned AI run/log; both were removed by exact identifier, restoring the recorded `29/44/27` AI baseline.

## 2026-07-19 RISK-P10-011 Recommendation Contract Remediation

The public today route was confirmed to invoke the write-capable get-or-create service. It now uses a distinct read-only service and returns a bounded missing result when no record exists. Generation moved to an explicit administrator-only POST; deletion and history are administrator-only, and history no longer serializes raw context. This preserves the public ShareCard fallback while preventing anonymous browsing from initiating AI work or persistence.

## 2026-07-19 Release Safety and Production Template Review

The predeploy gate was extended without executing deployment: it retains the clean-worktree fail-closed first check, then requires different explicitly supplied test and target database URLs before running backend pytest and Alembic current/heads/check. Its syntax passed; the current dirty tree correctly stops it before dependencies, databases or external services are touched.

Static production review passes the default-JWT, wildcard-CORS and active-bypass startup hard blocks. It cannot issue Production Ready: registration defaults to enabled unless deployment configuration changes it, and the Cloudflare template enables 100% invocation sampling with persistent logs. Both require an explicit deployment-time security/privacy policy and separate approval; no credential, deployed configuration or production endpoint was inspected.

## 2026-07-19 REL-P1-05 Release-Safety Closure Audit

The approved recommendation remediation is coherent across router, service, schema, management client and route tests: public reads do not invoke the generation service; generation, deletion and history are administrator operations; the history response excludes raw context. The predeploy script retains its clean-worktree fail-closed first gate and now adds an isolated backend-test database plus a distinct target database for backend pytest and Alembic authority checks.

Full local regression passed (frontend 43/43, backend 266/266, TypeScript, production build, revision `020` current/heads/check and diff hygiene). Shared-suite fixtures were removed only after exact identity checks; final AI runs/logs/recommendations counts returned to `29/44/27`.

Conclusion: **Release Safety code scope COMPLETE; deployment eligibility BLOCKED.** This is not a deployment result. The remaining blockers are the unchanged dirty worktree, the undecided production registration and Cloudflare invocation-log privacy/retention policy in `RISK-P10-015`, no authorized target-DB execution, and no deployment authorization. No production system, configuration, credential or data was accessed.

## 2026-07-19 Deployment-Task Preparation Audit

Read-only preparation reconfirmed that the release command is fail-closed behind `predeploy:check`, while the current worktree remains intentionally dirty. The frontend Cloudflare/OpenNext runtime and FastAPI/PostgreSQL/Attachment Storage boundary must be released and verified independently. The prepared task list therefore separates policy decisions, clean release scope, target authorization, predeploy, individual deployment commands, post-deploy smoke and rollback/acceptance.

No deployment action occurred. No target endpoint, production configuration, credential, database, attachment storage, commit, push, migration, DDL, restore or destructive cleanup was accessed or changed.

## 2026-07-19 DEP-P0-01 Release-Boundary Freeze

Read-only Git inventory found branch `notes-workspace-ux-upgrade` at committed baseline `939ad1f`, with a mixed set of modified and untracked backend, frontend, tests and workflow paths. This is not a clean or attributable release artifact, and no exact publish file set or commit has been approved. The release strategy is therefore an isolated clean worktree created only from a future user-approved commit. The current worktree was preserved exactly: no staging, commit, cleanup, push, target access or deployment occurred.

## 2026-07-19 DEP-P1-01 Scoped Release Artifact

The user explicitly authorized pushing only this round. The staged set was limited to the v1.0 productization code, tests, release baseline and Phase 1.0 workflow evidence; unrelated `docs/project-assessment/` and `docs/workflows/mvp-goal-gap-analysis/` remained unstaged. Cached path review and whitespace checks passed. Commit `57915a8` was then checked out in a temporary detached worktree, whose status was clean, before that temporary worktree was removed. This establishes a traceable release artifact without modifying or cleaning unrelated worktree paths. No predeploy, target access or deployment occurred.

## 2026-07-19 DEP-P0-02 Approved Production Policy

The user chose the conservative personal-system policy: public registration disabled; Workers invocation logs retained at 1% head sampling with platform short retention. The policy is intentionally narrower than the previous 100% sampling default and preserves limited incident observability without treating edge logs as a durable audit store. It authorizes only the local template/release-gate implementation; no deployed configuration, target database, credential or production system was read or changed.

## 2026-07-19 DEP-P1-01A Frontend/Backend Gate Split

The release gate is now decomposed into a frontend-only gate, a backend authority gate and their full composition. The frontend gate has no database variables or target-DB commands; it fail-closes on clean-worktree, audit, dependency, test, Cloudflare-build, TypeScript or diff-hygiene failure. The backend gate retains the distinct test/target database requirement before pytest and read-only Alembic authority checks. Production startup now hard-rejects enabled self-registration before database readiness, and the Workers template uses 1% sampling. This is local source/template behavior only; no target configuration or deployment was inspected or changed.

The new source/template changes are intentionally not treated as part of commit `57915a8`. A second scoped artifact must be approved, cached-reviewed, committed, pushed and clean-worktree verified before any frontend deployment task can use it.

## 2026-07-19 DEP-P1-01B Updated Scoped Release Artifact

The user approved the exact 16-path release-gate scope. Commit `929dd08` contains only the production-registration hard block, release-gate split, Workers sampling template, their tests and workflow evidence. Cached scope/whitespace review passed; the two unrelated workflow/document directories remained unstaged. A temporary detached worktree at `929dd08` had clean status and was removed. No predeploy, target access or deployment occurred.
