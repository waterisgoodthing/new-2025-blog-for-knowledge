# Design

## Architectural Lines

This task crosses both active architecture lines:

- Frontend App Router under `src/`.
- FastAPI backend under `backend/`.

Touched domains:

- `auth`, `notes`, `mistakes`, `blog`, `music`, `manage`, `review`, shared infrastructure.

All frontend protected operations should follow:

`page/component -> hook/local action -> src/lib/api/* -> backend API`

All backend APIs should follow:

`router -> schema validation -> service/model -> response schema`

## Permission Model

### Roles

| Role | Public Read | Content Write | AI Calls | Page Settings | Security Settings |
| --- | --- | --- | --- | --- | --- |
| Public | Yes | No | No | No | No |
| Password Admin | Yes | Yes | Yes | No | No |
| Passkey Admin | Yes | Yes | Yes | Yes | Yes |

### Session

- Sessions are represented by HttpOnly cookies.
- Backend stores active sessions or session ids so logout can revoke them.
- Session claims:
  - `sub`
  - `role = admin`
  - `auth_level = passkey | password`
  - `exp`
  - `iat`
  - `jti`

### Token Lifetimes

- Passkey session: 7 days.
- Password session: 3 days.
- No "remember me".

### Auth Guards

Frontend:

- Protected pages check current session status.
- Protected actions hide or disable controls when not authorized.
- Sensitive tabs show passkey-required messaging for password sessions.

Backend:

- `require_admin`
- `require_passkey_admin`
- `require_public_or_admin_read` for public read paths.

## Passkey Design

### Entity: PasskeyCredential

Fields:

- `id`
- `credential_id`
- `public_key`
- `sign_count`
- `device_name`
- `created_at`
- `last_used_at`

Relationships:

- Belongs to administrator identity.
- Only one credential is allowed.

Lifecycle:

- Create: local backend CLI starts temporary registration service.
- Use: passkey login validates challenge/response.
- Reset: local CLI removes or replaces credential.
- Delete: only through CLI reset.

Failure handling:

- Existing credential blocks registration unless reset flag is used.
- CLI requires project path/site name confirmation.

## Administrator Password Design

### Entity: AdminPassword

Fields:

- `username`
- `password_hash`
- `updated_at`
- `updated_by_session_id`

Lifecycle:

- Create/update only by passkey administrator in `/manage/security`.
- Reset by local CLI.
- Password admin cannot modify credentials.

Failure handling:

- Weak passwords rejected.
- Password login rate-limited.

## Public Read Design

Public users can read:

- Blogs.
- Notes.
- Mistakes.
- Music page.

Public users cannot:

- See management context actions.
- Trigger mutations.
- Call AI.
- Access `/manage` tools.

Public read contract:

- Public read exposes all notes and mistakes for this iteration, matching the user's confirmation.
- If draft/hidden visibility returns later, it must be introduced as a new explicit content visibility contract instead of implied filtering.

## `/manage` Console Design

Keep `/manage` as the administrator console.

Suggested readable tabs:

- 总览
- 内容管理
- 文件夹与标签
- 音乐管理
- AI 管理
- 页面设置
- 安全设置
- 同步部署
- 操作记录

Entity closure:

- Every tab should expose list, create/edit when relevant, delete/disable when relevant, and audit.
- Passkey-only tabs: 页面设置, 安全设置, sensitive NetEase API service configuration if implemented.

## Context Menu Design

Shared component:

- `src/components/context-menu.tsx` should become a general menu primitive.

Content menu actions:

- Open.
- Edit.
- Move to folder.
- Move to inbox.
- Copy link.
- Delete.

Folder menu actions:

- New child folder.
- Rename.
- Delete.
- Move to folder.
- Copy name.

Tag menu actions:

- Filter by tag.
- Rename.
- Merge into another tag.
- Delete tag.
- Copy name.

Empty-space menu actions:

- New note.
- New blog.
- New mistake.
- New folder.
- Refresh.

Public behavior:

- Public users do not see admin-only context actions.

## Folder Design

### Entity: Folder

Fields:

- `id`
- `name`
- `parent_id`
- `sort_order`
- `created_at`
- `updated_at`

Relationships:

- Folder has many content records through `Note.folder_id`; `Note.content_type` distinguishes note, blog, and mistake.
- Folder may have a parent folder.
- Folder may have child folders.

Lifecycle:

- Create from sidebar or manage console.
- Rename from context menu or manage console.
- Sort within same parent.
- Move under another folder, max depth 4.
- Assign note/blog/mistake content into folder from context menu, drag/drop, and manage console.
- Delete:
  - Move content to inbox.
  - Promote child folders to deleted folder's parent.
  - Delete folder.

Failure handling:

- Reject move into self or descendant.
- Reject nesting deeper than 4.
- Transactionally update content and child folders during delete.

Undo:

- Content move operations should include toast undo.
- Folder nesting/sort undo may be offered later if too complex, but action must be audited.

## Tag Design

### Entity: Tag

Fields:

- `id`
- `name`
- `created_at`
- `updated_at`

Relationships:

- Many-to-many with content.

Lifecycle:

- Create through content save or tag management.
- Rename.
- Merge.
- Delete from content associations.

Failure handling:

- Rename to existing tag prompts merge confirmation.
- Delete tag never deletes content.

## Drag And Drop Design

Use an established drag/drop library already present in the project where possible.

Content drag:

- Drag note/blog/mistake to folder -> assign folder.
- Drag note/blog/mistake to inbox -> clear folder.
- Show hover highlight.
- Show success toast with undo.

Folder drag:

- Drag within same parent -> reorder.
- Drag onto folder -> change parent if depth <= 4.
- Prevent invalid targets.

Backend:

- Folder moves and reorder should be persisted server-side.
- Invalid moves rejected server-side too.

## NetEase Candidate-Pool Daily Song Design

### Entity: NetEaseApiConfig

Fields:

- `id`
- `api_base_url`
- `service_token_ref`
- `enabled`
- `last_health_check_at`
- `last_health_status`
- `timeout_ms`
- `retry_count`
- `created_at`
- `updated_at`

Lifecycle:

- Configured in `/manage/music`.
- Health-checked by backend.
- Public frontend should not depend on a hardcoded third-party NetEase API URL.
- Optional service access token is backend-only if the deployed service is protected.

Failure handling:

- Missing or unhealthy API base URL disables sync and shows status in `/manage/music`.

### NetEase API Service Contract

The backend adapter should isolate the deployable NetEase API service behind a typed client.

Required capabilities:

- Search songs by keyword/style query.
- Resolve artist songs by artist id/name.
- Fetch song detail and album/cover metadata.
- Fetch playable URL when available.
- Build or store a NetEase jump URL.
- Health check.

Operational behavior:

- API base URL comes from backend settings or `/manage/music` configuration.
- Optional service token is never sent to public frontend.
- Timeouts, retries, and failure reasons are recorded.

### Entity: MusicSourceRule

Fields:

- `id`
- `source_type`: netease_artist, netease_search_rule.
- `source_value`: artist name/id or search rule text.
- `weight`
- `enabled`
- `sort_order`

Configured sources:

- 陈奕迅.
- 孙燕姿, high priority by default.
- 周杰伦.
- 陶喆.
- 西二.
- Search style: mainly 2000s Mandarin lyrical songs, campus nostalgia, and Cantonese classics, with a small amount of folk, English rock, and game music; overall clear melody, emotional aftertaste, and not overly noisy.

Default weighting:

- 孙燕姿 source rules and candidates should start with higher weight than the other specified artists.
- `/manage/music` can expose weight controls so the priority can be adjusted later.

### Entity: MusicCandidate

Fields:

- `id`
- `netease_song_id`
- `title`
- `artists`
- `album`
- `cover_url`
- `play_url`
- `netease_url`
- `source_rule_id`
- `tags`
- `mood`
- `weight`
- `enabled`
- `last_synced_at`
- `last_play_url_checked_at`
- `availability_status`
- `failure_reason`
- `created_at`
- `updated_at`

Lifecycle:

- Created or refreshed by backend sync from the deployable NetEase API service.
- Listed, enabled/disabled, weighted, tagged, and refreshed in `/manage/music`.
- Used as the candidate pool for daily-song generation.
- Existing records are preserved when sync fails.

Failure handling:

- API sync failure records failure logs and keeps prior candidates.
- Missing playback URL can still allow a NetEase jump URL.

### Entity: MusicSyncLog

Fields:

- `id`
- `operation`: health_check, artist_sync, search_sync, play_url_check, daily_generation.
- `source_rule_id`
- `status`
- `message`
- `request_summary`
- `result_count`
- `failure_reason`
- `started_at`
- `finished_at`

Lifecycle:

- Created by health checks, manual refresh, scheduled sync, playback URL checks, and daily-song generation.
- Listed in `/manage/music` failure/status logs.
- Not publicly visible.

### Entity: DailySong

Fields:

- `id`
- `date`
- `timezone`
- `candidate_id`
- `netease_song_id`
- `title`
- `artist`
- `album`
- `artwork_url`
- `play_url`
- `netease_url`
- `recommendation_reason`
- `source_rule_id`
- `selection_seed`
- `selection_strategy`
- `created_at`

Lifecycle:

- Created by daily refresh at 08:00 Asia/Shanghai.
- Not manually replaceable for the same day.
- Saved to history.
- Publicly displayed.
- AI selects from enabled `MusicCandidate` records using random or weighted-random behavior guided by the configured style rule, then writes the recommendation reason.

Failure handling:

- If NetEase API is unavailable:
  - Use current-day cache.
  - Else use previous daily song.
  - Else show empty fallback.
- If AI selection fails:
  - Use deterministic random fallback from enabled candidates.
- If candidate pool is empty:
  - Show setup/sync-needed fallback.
- If playback URL is missing:
  - Show jump-to-NetEase action.

Display:

- Existing music interface remains.
- Daily song is primary.
- Historical playlist remains.
- Hovering over song shows small card after delay.
- Mobile optimization optional.

## AI Management Design

AI tab under `/manage` should include:

- Configuration status.
- Model status.
- Feature switches.
- Prompt/template management.
- Usage/call logs.
- Test calls.
- Failure summaries.
- Audit events.

Protected:

- AI calls require admin session.
- Sensitive AI configuration changes may require passkey session.

Entity closure:

- Prompt/template records can be created, edited, disabled, tested, and audited.
- Feature switches affect specific AI entry points such as note polishing, tag generation, mistake analysis, weak-point actions, and music recommendation reasons.
- Usage logs link each AI call to actor session, feature, related entity, model, status, and failure details.

## Structured Weak-Point Diagnosis Design

### Entity: WeakPoint

Fields:

- `weak_point_id`
- `name`
- `subject`
- `module`
- `tags`
- `error_type`
- `severity`
- `mistake_count`
- `due_count`
- `recent_count`
- `last_seen_at`
- `diagnosis`
- `recommended_action`
- `related_mistake_slugs`
- `related_note_slugs`

Display:

- Rename section to "薄弱点诊断".
- Show time range filter: 7 days / 30 days.
- Show sort: severity / frequency / due review.
- Collapsed cluster card:
  - title
  - subject
  - severity
  - mistake count
  - due count
  - recent frequency
  - diagnosis sentence
  - error type tags
- Expanded cluster:
  - related mistakes
  - related notes
  - remediation steps
  - start review
  - generate variants
  - generate knowledge card
  - save remediation plan

Failure handling:

- Insufficient data state.
- AI diagnosis unavailable state.

Entity closure:

- Weak points are derived from mistake records and related notes, not manually created as standalone content in the first version.
- Generated actions must create or update existing entities: review session, generated mistake variants, knowledge note/card, or saved remediation plan.
- Public readers may view diagnosis and related content; AI generation and save actions require administrator session.

## Audit Design

### Entity: AuditLog

Fields:

- `id`
- `actor_session_id`
- `auth_level`
- `action`
- `entity_type`
- `entity_id`
- `before`
- `after`
- `ip`
- `user_agent`
- `created_at`

Events:

- Login/logout.
- Token revocation.
- Content create/edit/delete.
- Folder create/rename/move/delete.
- Tag rename/merge/delete.
- Page setting changes.
- AI calls.
- NetEase music config/sync changes.
- Security changes.

## Validation Plan

- TypeScript: `npx tsc --noEmit`.
- Build-sensitive frontend: `npm run build` or deploy-specific build when relevant.
- Backend: targeted tests if present; import/start checks at minimum.
- Browser: interactive checks for right-click, drag/drop, tooltip, music preview, admin auth, weak-point expansion.
- API: auth negative tests for 401/403, folder delete transaction, tag merge/delete, NetEase music fallback.
- Data: verify folder deletion effects, tag merge effects, audit log creation.
