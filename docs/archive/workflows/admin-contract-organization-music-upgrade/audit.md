# Planning Audit

## Current State

- Requirements, design, and tasks have been drafted.
- No implementation has started for this task group.
- The repository has unrelated dirty files. They must be preserved.

## Approval Status

Approved by the user in conversation on 2026-06-08.

Implementation ownership is assigned to another intelligent agent. Codex has not started business-code implementation for this workflow.

## Closure Verification 2026-06-08

Checked requirements, design, and tasks for front-to-back closure.

Corrections made:

- Public read contract now matches the user's final decision: notes and mistakes are public-read in this iteration.
- Folder relationships now explicitly cover note, blog, and mistake content through the shared content model.
- Password login is documented as fallback for ordinary administrator operations while passkey-only actions remain blocked.
- Administrator password storage now states hashed/backend or environment/CLI initialization, with no raw password exposure.
- AI management and weak-point diagnosis now describe how their records connect to existing entities and actions.
- `tasks.md` now includes a required entity closure matrix task before implementation.

Music scope update:

- Apple Music / MusicKit integration was removed from the iteration.
- The temporary local music-file link was also removed.
- Music now uses a deployable NetEase Cloud Music API service, backend-synchronized candidate pool, configured artist/search rules, and AI daily-song selection.

Current closure status:

- Requirements cover roles, inputs, processing, outputs, failure handling, and acceptance for the requested feature groups.
- Design maps the feature groups to backend models/services/routers, frontend routes/components/API clients, permissions, and validation.
- Tasks map each requirement group to implementation and validation work.
- No business code has been changed in this workflow.

## Entity Closure Matrix

| Entity / Capability | Creation / Source | Relationships | UI / API Entry | Edit / Move / Delete | Permission | Audit | Failure / Acceptance |
| --- | --- | --- | --- | --- | --- | --- | --- |
| AdminSession | Password/passkey login | Actor for protected actions and audit rows | login API, session API, logout API | revoke on logout/expiry | public none, password/passkey admin by level | login/logout/revoke | 401 expired/revoked; 3-day password and 7-day passkey sessions verified |
| PasskeyCredential | Local CLI temporary registration service | One credential for admin identity | backend CLI plus temporary local service | reset only through CLI | local operator registration, passkey admin login | register/reset/use | duplicate rejected unless reset; project path/site name confirmation |
| AdminPassword | passkey admin security page or CLI/env initialization | admin identity, sessions issued from password login | `/manage/security`, backend auth API, CLI | set/reset/clear | passkey admin or local operator only | set/reset/login | password admin gets 403 for credential changes |
| ContentRecord | write-note/write-mistake/blog workflows | Folder, tags, audit, weak points, review | `/notes`, `/mistakes`, `/blog`, `/manage`, detail pages | edit, move folder/inbox, delete, copy link | public read; password/passkey admin mutate | create/edit/delete/move | unauthenticated mutation 401; context menus hidden for public |
| Folder | sidebar or `/manage` folders/tags tab | parent folder, child folders, content records | sidebar, manage tab, folder APIs | rename, sort, nest, delete, move content into/out | admin only | create/rename/move/delete | max depth 4, self/descendant moves rejected, delete moves content to inbox and promotes children |
| Tag | content save or tag management | many-to-many with content | sidebar tags, tag context menu, manage tab | rename, merge, delete, copy/filter | admin mutate, public filter/read if visible | rename/merge/delete | delete never deletes content; rename collision prompts merge |
| NetEaseApiConfig | `/manage/music` | MusicSourceRule sync and candidate refresh | manage music tab, backend config/health API | edit/enable/disable/test | admin manage; sensitive deployment config may require passkey | config/test | unhealthy API disables sync and records failure |
| MusicSourceRule | `/manage/music` artist/search rules | MusicCandidate sync and DailySong source | manage music tab, backend music APIs | enable/disable/order/edit/weight | admin manage | config changes | empty rule result records sync failure and keeps prior candidates |
| MusicCandidate | NetEase metadata sync | source rule and DailySong | manage music candidate list, backend sync APIs | enable/disable/tag/weight/refresh | admin manage; public read selected metadata | sync/edit/disable | missing playback URL keeps jump URL when available |
| MusicSyncLog | health checks, candidate sync, play URL checks, daily generation | NetEaseApiConfig, MusicSourceRule, MusicCandidate, DailySong | `/manage/music` status/failure logs | read/filter; no public mutation | admin read, backend write | sync/failure events | failures visible without deleting prior candidates |
| DailySong | 08:00 Asia/Shanghai scheduler | MusicCandidate, source rule, AI reason, history | public `/music`, manage music history | not manually replaced same day | public read/play/jump; admin configure | generation/fallback/config | AI failure uses deterministic random fallback; NetEase failure uses cache/history/fallback |
| AI Prompt/Template | `/manage/ai` | AI feature switches and calls | manage AI tab, AI APIs | create/edit/disable/test | admin for calls; passkey for sensitive config if implemented | prompt changes/test calls | missing config disables tests safely |
| AIUsageLog | AI call execution | actor session, feature, related entity, model | `/manage/ai`, audit/log APIs | read/filter; no normal delete | admin read, backend create | AI calls/failures | unauthenticated AI calls fail and are logged when applicable |
| WeakPoint | derived from mistakes and related notes | mistake records, notes, review, AI outputs | `/mistakes` diagnosis module | derived refresh; actions create review/variants/cards/plans | public view; admin actions | AI/action events | insufficient data state; no repeated flat cards; expanded actions verified |
| AuditLog | protected/security action | actor session, entity before/after | `/manage/audit`, backend audit service | read/filter; no public mutation | admin read, backend write | self | high-risk audit failure surfaced or fallback-recorded |
