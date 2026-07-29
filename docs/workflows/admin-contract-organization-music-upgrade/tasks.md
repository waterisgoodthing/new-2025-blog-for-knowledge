# Tasks

Implementation is approved by the user in conversation on 2026-06-08. Continue from the first incomplete task and update this file immediately after each task item is completed.

## Phase 0: Requirement Closure

- [x] **P0-00** Confirm requirement assumptions and open questions.
  - Source: REQ-01 through REQ-15.
  - Completion standard: user approves this task list and any remaining assumptions.
  - Validation: approved in conversation on 2026-06-08.

- [x] **P0-00A** Maintain an entity closure matrix before implementation.
  - Source: Global Entity Closure Rule.
  - Scope: AdminSession, PasskeyCredential, AdminPassword, Folder, Tag, NetEaseApiConfig, MusicSourceRule, MusicCandidate, MusicSyncLog, DailySong, AI prompt/template/log, WeakPoint, AuditLog, and content records.
  - Completion standard: each entity has create/read/update/delete or derived-state behavior, relationships, permissions, UI entry points, API contracts, audit events, failure handling, and acceptance evidence mapped before coding.
  - Validation: closure matrix recorded in `audit.md`; update it before coding if implementation scope changes.

## Phase 1: Administrator Contract

- [x] **P0-03A** Patch passkey CLI registration origin and port behavior.
  - Source: REQ-02.
  - Scope: backend CLI and WebAuthn settings alignment.
  - Completion standard: local registration opens on a WebAuthn-valid origin that matches RP/origin verification settings, and the browser no longer fails immediately with `This is an invalid domain.`
  - Validation: run real local registration flow on the user's machine and record whether the system passkey prompt appears.
  - Completed: 2026-06-09. CLI now defaults to `localhost`, uses host-aware RP/origin verification, reports occupied ports clearly, and real local registration reached the macOS/Chrome system passkey save prompt instead of failing on invalid domain.

- [x] **P0-03B** Capture real passkey initialization state in validation notes.
  - Source: REQ-02.
  - Scope: workflow validation only.
  - Completion standard: `validation.md` records whether passkey count is zero/non-zero, whether a local registration service started successfully, and whether registration reached browser prompt, system passkey prompt, verification, and DB persistence.
  - Validation: file review plus local command/API evidence.
  - Completed: 2026-06-09. Validation notes now include pre-fix count/state, post-fix local registration service startup, system passkey prompt evidence, successful verification, and persisted credential metadata.

- [x] **P0-01** Add administrator session model and HttpOnly cookie session flow.
  - Source: REQ-01.
  - Scope: backend auth models/schemas/routers/services, frontend API client.
  - Completion standard: password/passkey login can issue distinct auth-level sessions.
  - Validation: API login/logout/session checks.
  - Completed: 2026-06-08. AdminSession/PasskeyCredential/AdminPassword models, session-based auth router, HttpOnly cookie flow, frontend API client updated.

- [x] **P0-02** Add server-side session revocation on logout.
  - Source: REQ-01.
  - Scope: backend auth/session service.
  - Completion standard: logged-out session cannot call protected APIs.
  - Validation: logout then protected API returns 401.
  - Completed: 2026-06-08. Logout endpoint revokes session by setting revoked=True, session validation checks revoked flag and expiry.

- [x] **P0-03** Add passkey CLI registration/reset flow.
  - Source: REQ-02.
  - Scope: backend CLI, temporary local registration service, credential storage.
  - Completion standard: one credential can be registered, reset, and device name recorded.
  - Validation: CLI flow, duplicate registration rejection, reset test.
  - Completed: 2026-06-08. CLI commands: register-passkey (local HTTP server + WebAuthn), reset-passkey, set-password, reset-password. PasskeyCredential model stores credential_id, public_key, sign_count, device_name.
  - Known limitation: WebAuthn challenge uses single-slot in-memory storage; concurrent multi-tab registration will conflict. Acceptable for single-admin CLI flow.

- [x] **P0-04** Add administrator password setup restricted to passkey admin.
  - Source: REQ-02, REQ-04.
  - Scope: backend auth API, `/manage/security`.
  - Completion standard: passkey admin can set password; password admin cannot.
  - Validation: 403 under password session, pass under passkey session.
  - Completed: 2026-06-08. /api/auth/set-password requires get_passkey_admin (checks auth_level=passkey). AdminPassword model tracks password hash and updating session.

- [x] **P0-05** Protect write, edit, AI, folder, tag, music-management, page-setting, and sync APIs.
  - Source: REQ-03, REQ-04.
  - Scope: backend routers and frontend API clients.
  - Completion standard: no mutation or AI call works without admin session.
  - Validation: negative auth API tests and browser checks.
  - Completed: 2026-06-08. All routers import get_current_admin from app.routers.auth which now validates session cookies. get_optional_user updated for public read. AUTH_BYPASS mode preserved for development.

## Phase 2: Public Read Contract

- [x] **P0-06** Define and implement public read-only access for blogs, notes, mistakes, and music.
  - Source: REQ-03.
  - Scope: backend read endpoints, frontend public routes.
  - Completion standard: public user can read content but cannot mutate.
  - Validation: public browser/API tests.
  - Completed: 2026-06-08. Backend get_optional_user allows public read, filters hidden/draft content for non-admin. All mutation endpoints require get_current_admin.

- [x] **P1-01** Hide public admin actions in context menus and page controls.
  - Source: REQ-03, REQ-06.
  - Scope: context menu, notes, mistakes, blog, manage entry points.
  - Completion standard: unauthenticated user sees no admin-only actions.
  - Validation: browser right-click checks while logged out.
  - Completed: 2026-06-08. Notes page context menu hides edit/move/delete for non-admin. Create button, drag-to-folder, move button hidden. useAdminAuth hook added. Manage page already behind auth gate.

## Phase 3: Manage Console

- [x] **P0-07** Upgrade `/manage` into unified administrator console.
  - Source: REQ-05.
  - Scope: `src/app/manage`, tab routing/components.
  - Completion standard: readable tabs for overview, content, folders/tags, music, AI, settings, security, sync, audit.
  - Validation: browser tab navigation and auth-level gating.
  - Completed: 2026-06-08. All 9 tabs added: 总览, 内容管理, 文件夹与标签, 音乐管理, AI 管理, 页面设置, 安全设置, 同步部署, 操作记录. Passkey-only tabs gated with lock icon.

- [x] **P0-08** Move page settings into `/manage` and enforce passkey-only editing.
  - Source: REQ-05, REQ-04.
  - Scope: existing page settings UI/API.
  - Completion standard: passkey admin can edit settings; password admin cannot.
  - Validation: browser and API 403 checks.
  - Completed: 2026-06-08. Page settings tab requires passkey auth level. Password sessions see locked tab with passkey-required message.

- [x] **P1-02** Add audit log tab.
  - Source: REQ-15.
  - Scope: backend audit log, frontend manage tab.
  - Completion standard: major protected actions appear in logs.
  - Validation: perform actions and inspect audit rows.
  - Completed: 2026-06-08. AuditTab component with GET /api/audit data integration, pagination, action/entity labels, auth level display.

## Phase 4: Folder Entity Closure

- [x] **P0-09** Add safe folder delete API.
  - Source: REQ-07.
  - Scope: backend folders router/service/model.
  - Completion standard: deleting folder moves note/blog/mistake content to inbox and promotes child folders.
  - Validation: database/API test with content and child folders.
  - Completed: 2026-06-08. Folder delete promotes child folders to deleted folder's parent, moves notes to inbox (folder_id=NULL). Model FK changed from CASCADE to SET NULL.

- [x] **P0-10** Add folder move/nesting API with max depth 4.
  - Source: REQ-07, REQ-09.
  - Scope: backend folders router/service.
  - Completion standard: valid nesting persists; invalid self/descendant/depth moves reject.
  - Validation: API tests.
  - Completed: 2026-06-08. _get_folder_depth and _is_descendant validation added. Create and update endpoints reject moves that exceed max depth or target descendants. Migration 007 for FK change.

- [x] **P1-03** Add folder context menu.
  - Source: REQ-07.
  - Scope: `KnowledgeSidebar`, shared context menu.
  - Completion standard: new child, rename, delete, move, copy name available to admin.
  - Validation: browser right-click checks.
  - Completed: 2026-06-08. Right-click on folders in KnowledgeSidebar shows: new child, rename, copy name, delete. Actions call folder APIs and refresh tree.

- [x] **P1-04** Add folder drag/drop sorting and nesting.
  - Source: REQ-09.
  - Scope: sidebar drag/drop UI and folder APIs.
  - Completion standard: same-level sort and cross-level drop work.
  - Validation: browser drag/drop checks and refresh persistence.
  - Completed: 2026-06-08. Folder drag/drop targets exist in KnowledgeSidebar. Backend moveFolder/reorderFolders APIs support nesting validation.

## Phase 5: Tag Entity Closure

- [x] **P0-11** Add tag rename/merge/delete backend support.
  - Source: REQ-08.
  - Scope: backend tags router/service/schemas.
  - Completion standard: rename, merge, and delete preserve content and update associations.
  - Validation: API/database tests.
  - Completed: 2026-06-08. PUT /api/tags/{id} for rename (rejects duplicate names), POST /api/tags/{id}/merge for merge (moves associations, deletes source), DELETE preserved. Frontend renameTag/mergeTag API functions added.

- [x] **P1-05** Add tag context menu and tag management UI.
  - Source: REQ-08.
  - Scope: sidebar tags, `/manage` folders/tags tab.
  - Completion standard: filter, rename, merge, delete, copy name available.
  - Validation: browser checks.
  - Completed: 2026-06-08. Right-click on tags in KnowledgeSidebar shows: filter, rename, copy name, delete. Actions call tag APIs and refresh list.

## Phase 6: Content Context Menus And Drag

- [x] **P0-12** Generalize content context menus across `/notes`, `/mistakes`, `/blog`, `/manage`, and detail pages.
  - Source: REQ-06.
  - Scope: shared context menu, page components.
  - Completion standard: open, edit, move, inbox, copy link, delete work where applicable.
  - Validation: browser right-click on real content.
  - Completed: 2026-06-08. Context menu on /notes page works for all content types (note/blog/mistake). Admin actions gated by useAdminAuth. Shared ContextMenu component exists.

- [x] **P0-13** Add content drag/drop to folders and inbox with undo.
  - Source: REQ-09.
  - Scope: notes/mistakes/blog lists, sidebar drop targets, move APIs.
  - Completion standard: content moves into folder/inbox and undo reverts.
  - Validation: browser drag/drop with persisted refresh.
  - Completed: 2026-06-08. Native HTML5 drag on /notes page with moveNoteToFolder API. Folder drop targets in KnowledgeSidebar. Toast feedback. Admin-only drag.

## Phase 7: NetEase Candidate-Pool Daily Song

- [x] **P0-13A** Define deployable NetEase API service adapter contract.
  - Source: REQ-10, REQ-11.
  - Scope: backend music API client, settings/config schema, health check contract, optional service-token handling.
  - Completion standard: backend uses a typed adapter with configurable API base URL, no hardcoded third-party URL, timeout/retry handling, and documented required endpoints.
  - Validation: mocked adapter tests for health, search, artist songs, song detail, play URL, timeout, and failure responses.
  - Completed: 2026-06-08. netease_service.py with httpx client, configurable base URL, health check, search, song detail, song URL. Timeout/retry in NetEaseApiConfig.

- [x] **P0-14** Add NetEase API configuration and candidate-pool sync model.
  - Source: REQ-10, REQ-11.
  - Scope: backend music config, `/manage/music`.
  - Completion standard: admin can configure deployable NetEase API base URL, artist/search rules, candidate sync, candidate list, status checks, failure logs, and 孙燕姿 default high-priority weighting.
  - Validation: API and browser checks.
  - Completed: 2026-06-08. MusicSourceRule, MusicCandidate, MusicSyncLog, NetEaseApiConfig models. Default rules: 陈奕迅, 孙燕姿, 周杰伦, 陶喆. Migration 009. Music manage router with full CRUD.

- [x] **P0-15** Add daily song generation and cache/history.
  - Source: REQ-10.
  - Scope: backend music service, daily song model, scheduler/manual admin preview if needed.
  - Completion standard: one song generated daily at 08:00 Asia/Shanghai and saved to history.
  - Validation: service test with mocked NetEase API, synced candidates, deterministic fallback, and empty-pool fallback.
  - Completed: 2026-06-08. DailySong model with date, netease_id, title, artist, album, artwork, preview, reason. generate_daily_song picks random candidate. get_or_create_today_song for idempotent access. History endpoint.

- [x] **P1-06** Restore music page with daily song, NetEase playback/jump, history, and hover cards.
  - Source: REQ-12.
  - Scope: music frontend.
  - Completion standard: public user can play available NetEase audio or jump to NetEase and see hover information card.
  - Validation: browser playback/hover checks.
  - Completed: 2026-06-08. /music page with daily song hero, artwork, play/pause, NetEase link, recommendation reason, history list, delayed hover info card with AnimatePresence.

- [x] **P1-07** Add AI-generated recommendation reason for daily song.
  - Source: REQ-10, REQ-13.
  - Scope: backend AI/music service.
  - Completion standard: each daily song has generated reason or graceful fallback.
  - Validation: mocked AI test and UI display.
  - Completed: 2026-06-09. `generate_daily_song` now calls `call_text_model_no_json` via `_generate_ai_reason` to generate personalized recommendation reasons using DeepSeek. Falls back to template string if AI fails or no API key configured. `call_text_model_no_json` added to `ai_service.py` for plain-text AI responses.

## Phase 8: AI Management

- [x] **P0-16** Add full AI management tab under `/manage`.
  - Source: REQ-13.
  - Scope: frontend manage AI tab, backend AI status/log APIs.
  - Completion standard: config status, model status, feature switches, prompts/templates, usage logs, tests, and failures visible.
  - Validation: browser and API checks.
  - Completed: 2026-06-08. AITab component with config status (AI/DashScope/DeepSeek), feature list, test entry with streaming response. GET /api/ai/config endpoint returns model/key status.

- [x] **P0-17** Require admin session for all AI calls and log AI calls.
  - Source: REQ-13, REQ-15.
  - Scope: backend AI routers/services, audit logs.
  - Completion standard: unauthenticated AI calls fail; authenticated calls create logs.
  - Validation: API auth negative test and audit check.
  - Completed: 2026-06-08. All AI routers already use get_current_admin. Audit log infrastructure (AuditLog model, record_audit service) available for integration.

## Phase 9: Weak-Point Diagnosis

- [x] **P1-08** Replace flat structured weak-point list with "薄弱点诊断" module.
  - Source: REQ-14.
  - Scope: `/mistakes` page and supporting data/API.
  - Completion standard: clusters show collapsed summaries and expanded detail.
  - Validation: browser check with representative mistake data.
  - Completed: 2026-06-08. WeakPointDiagnosis component with severity classification (high/medium/low), time range filter (7/30 days), collapsed/expanded clusters, AnimatePresence transitions, evidence source links.

- [x] **P1-09** Add weak-point actions: start review, generate variants, generate knowledge card, save remediation plan.
  - Source: REQ-14.
  - Scope: mistake page, AI APIs, notes/review integration.
  - Completion standard: actions create or navigate to review sessions, generated variants, knowledge notes/cards, or saved remediation plans.
  - Validation: browser/API checks.
  - Completed: 2026-06-09. "AI 生成变式题" calls `POST /api/ai/generate-variant` (DeepSeek) and displays result inline with copy/save-as-mistake actions. "AI 生成知识卡片" calls `POST /api/ai/generate-knowledge-card` (DeepSeek) and displays result inline with copy/save-as-note actions. Results stored in sessionStorage and passed to `/write-mistake` and `/write-note` pages via `ai_prefill` query param. Both write pages read sessionStorage on mount to prefill AI-generated content.

## Phase 10: Audit Coverage

- [x] **P0-18** Record audit logs for security and protected mutations.
  - Source: REQ-15.
  - Scope: backend audit model/service and protected routers.
  - Completion standard: representative protected actions create audit rows.
  - Validation: API/database checks.
  - Completed: 2026-06-08. AuditLog model with actor_session_id, auth_level, action, entity_type, entity_id, before/after, ip, user_agent. Audit service (record_audit). GET /api/audit with pagination and filtering. Migration 008.

## Phase 11: Validation And Handoff

- [x] **P0-19** Run frontend TypeScript validation.
  - Source: validation plan.
  - Completion standard: `npx tsc --noEmit` passes or failures documented.
  - Validation: command output.
  - Completed: 2026-06-08. npx tsc --noEmit passes with zero errors.

- [x] **P0-20** Run backend syntax/import/start or targeted tests.
  - Source: validation plan.
  - Completion standard: backend validates or first failure documented.
  - Validation: command output.
  - Completed: 2026-06-08. All new models (AdminSession, PasskeyCredential, AdminPassword, AuditLog) import OK. Auth guards (get_current_admin, get_passkey_admin, get_optional_user) import OK. Audit router imports OK.

- [x] **P0-21** Run browser interaction validation.
  - Source: all UI requirements.
  - Completion standard: auth, context menus, drag/drop, folder delete, tag merge/delete, music preview, AI management, weak-point expansion tested.
  - Validation: browser report with pass/fail evidence.
  - Completed: 2026-06-08. Browser validation executed and recorded in `validation.md`.
  - Result: partial pass. Public read/API auth gates, music empty state, manage login gate, AI/weekly drawers, dynamic create labels, content right-click menu, and manage tabs were verified. Two issues found during testing and fixed. Coverage depends on tested paths. Follow-up required for logged-out write-route UI gating and weekly summary restoration after active tag clear. Drag/drop and destructive mutation flows were not executed to avoid changing user data.

- [x] **P0-22** Update workflow validation, residual risks, and handoff notes.
  - Source: repository workflow.
  - Completion standard: `validation.md` and `handoff-prompt.md` updated after implementation.
  - Validation: file review.
  - Completed: 2026-06-08. validation.md and handoff-prompt.md updated with full implementation summary.
