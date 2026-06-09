# Requirements

## Background

The site-level protection has been removed, so the application now needs its own internal administrator contract. Public users should be able to read public knowledge content and listen to music previews, while every write, AI, management, folder, tag, and settings operation must be protected.

At the same time, the existing knowledge workspace needs richer organization. Folders currently cannot be deleted cleanly, files cannot reliably be added to folders, drag-and-drop needs to cover content and folders, and context menus should be available across the system. The music page is also broken or incomplete and should be rebuilt around a deployable NetEase Cloud Music API candidate-pool daily-song behavior. The mistake page's structured weak-point section needs a more useful diagnostic design.

## Roles

- Public reader: can read blogs, notes, mistakes, and listen to music previews.
- Password administrator: can create/edit/delete content, manage folders/tags, write notes, write mistakes, call AI, and use content management tools.
- Passkey administrator: has all password administrator permissions plus sensitive settings such as page settings, administrator password settings, security status, and NetEase API service configuration if needed.
- Local operator: can run backend CLI commands for passkey registration/reset and password reset.

## Global Entity Closure Rule

Every new entity or major capability must define:

- Creation entry and allowed actor.
- Core fields and storage location.
- Relationships with other entities.
- Display locations.
- Edit, move, delete, and undo behavior.
- Search, filter, right-click, and drag/drop participation when relevant.
- Permission behavior for public, password admin, and passkey admin.
- Audit events.
- Failure handling.
- Acceptance evidence.

## Functional Requirements

### REQ-01 Administrator Session Contract

Input: login through password or passkey.

Processing:
- Password login validates administrator username and password.
- Passkey login validates the registered WebAuthn credential.
- Both login methods issue administrator sessions through HttpOnly cookies.
- Passkey sessions last 7 days.
- Password sessions last 3 days.
- No "remember me" option is shown.
- Logout revokes the token/session server-side.
- If passkey is unavailable, password login remains a fallback for ordinary administrator operations, but passkey-only operations stay blocked.

Output:
- Valid administrator session cookie.
- Session metadata includes auth level: `passkey` or `password`.

Failure handling:
- Invalid login returns a clear error.
- Expired/revoked session behaves as unauthenticated.
- Sensitive action with password session returns 403 with "passkey required" meaning.

Acceptance:
- Password login creates a 3-day session.
- Passkey login creates a 7-day session.
- Logout revokes session on the server.
- Sensitive settings fail under password session and pass under passkey session.

### REQ-02 Passkey Registration And Reset

Input: local backend CLI command.

Processing:
- CLI starts a local temporary registration service.
- User registers exactly one passkey credential from the local device.
- CLI can reset passkey.
- CLI can reset or clear administrator password.
- Administrator password can be stored as a backend hash or initialized from environment/local CLI input; raw passwords are never returned through APIs.
- CLI requires second confirmation by typing the project path or site name.
- No frontend passkey setup entry exists.

Output:
- Stored passkey credential id, public key, sign count, device name, created time, and last used time.

Failure handling:
- If a passkey already exists, CLI refuses unless reset mode is used.
- If confirmation does not match, CLI aborts.

Acceptance:
- Only one passkey can be registered.
- Device name is recorded.
- Passkey reset removes the old credential.

### REQ-03 Public Read-Only Contract

Input: public user visits blog, notes, mistakes, or music.

Processing:
- Public users can read blogs, notes, and mistakes.
- Notes and mistakes are public-read by default for this iteration, not limited to draft/hidden flags unless a later task reintroduces visibility rules.
- Public users can listen to music previews.
- Public users cannot see admin-only context actions.
- Public users cannot create, edit, delete, move, tag, call AI, or change settings.

Output:
- Read-only content UI.

Failure handling:
- Attempted admin API mutation without session returns 401.
- Hidden admin actions are not visible in public UI.

Acceptance:
- `/blog`, `/notes`, `/mistakes`, and `/music` are readable without login.
- Public mutation API requests fail.
- Public right-click menus do not expose admin actions.

### REQ-04 Protected Content Operations

Input: administrator uses write/edit/delete/move actions.

Processing:
- Password and passkey administrators can write notes, write mistakes, edit content, manage folders/tags, call AI, and manage content.
- Page settings and administrator password changes require passkey administrator.

Output:
- Successful content mutation and audit event.

Failure handling:
- No session returns 401.
- Password session on passkey-only action returns 403.

Acceptance:
- Protected APIs require administrator session.
- Passkey-only APIs reject password sessions.

### REQ-05 Unified `/manage` Administrator Console

Input: administrator visits `/manage`.

Processing:
- `/manage` becomes the unified administrator console.
- Tabs use clear names that are understandable to the user.
- Include at least: Overview, Content, Folders And Tags, Music, AI, Page Settings, Security, Sync, Audit Logs.
- Existing page settings move into `/manage`.
- Old settings entry redirects or links to the new location.

Output:
- Single management entry for all admin work.

Failure handling:
- Public users cannot access management tools.
- Unauthorized users are prompted to login.

Acceptance:
- Each tab renders and respects auth level.
- Page settings are editable only by passkey administrator.

### REQ-06 Content Context Menus Across System

Input: administrator right-clicks content in notes, mistakes, blog, manage, or detail pages.

Processing:
- Content context menu supports: open, edit, move to folder, move to inbox, copy link, delete.
- Public users do not see management actions.
- Delete requires confirmation.
- Move/delete actions emit audit logs.

Output:
- Contextual actions for the selected content entity.

Failure handling:
- Action failure shows toast and preserves current state.

Acceptance:
- Context menus work on `/notes`, `/mistakes`, `/blog`, `/manage`, and content detail pages where content is visible.

### REQ-07 Folder Entity Closure

Input: administrator creates, moves, sorts, nests, renames, or deletes folders.

Processing:
- Folders can be created from sidebar and admin console.
- Folders support parent-child nesting up to 4 levels.
- Folders support same-level sorting.
- Cross-level movement happens by dragging into another folder.
- Folder cannot be moved into itself or its descendants.
- Deleting a folder moves contained content to inbox.
- Deleting a parent folder preserves child folders by promoting them to the deleted folder's parent.
- Folder operations emit audit logs.

Output:
- Updated folder tree and related content placement.

Failure handling:
- Invalid nesting depth is rejected.
- Invalid move is rejected with a clear message.
- Failed move/delete leaves data unchanged.

Acceptance:
- Delete non-empty folder moves content to inbox.
- Delete folder with children promotes children to parent.
- Folder sorting and nesting persist after refresh.

### REQ-08 Tag Entity Closure

Input: administrator right-clicks or manages tags.

Processing:
- Tags support filter, rename, merge, delete, and copy name.
- Deleting a tag removes the tag from content but never deletes content.
- Merging tag A into tag B moves all associations to B and deletes A.
- Renaming to an existing tag prompts merge confirmation.
- Tag operations emit audit logs.

Output:
- Updated tag list and content associations.

Failure handling:
- Duplicate/conflicting rename prompts confirmation.
- Failed operations preserve current state.

Acceptance:
- Rename, merge, delete, and filter all work from tag context menu and admin tab.

### REQ-09 Drag-And-Drop Organization

Input: administrator drags content or folders.

Processing:
- Content dragged onto folder moves into that folder.
- Content dragged onto inbox moves out of folder.
- Folder dragged within same level reorders.
- Folder dragged onto another folder changes parent, if nesting depth <= 4.
- Move operations provide undo toast.

Output:
- Updated content folder assignment or folder tree.

Failure handling:
- Invalid drops are rejected visually and by API.
- Undo reverts last move when possible.

Acceptance:
- Content-to-folder, content-to-inbox, folder sort, and folder nesting can be tested in browser.
- Undo reverts a move.

### REQ-10 NetEase Candidate-Pool Daily Song

Input: public user opens music page; administrator configures NetEase source rules.

Processing:
- Keep the existing music interface but restore it around a daily song experience.
- Apple Music API / MusicKit and local music-file storage are not used in this iteration.
- Use a deployable NetEase Cloud Music API service configured through backend settings.
- Daily song source comes from a backend-maintained candidate pool synchronized from NetEase metadata.
- Candidate sources include specified artists plus search rules.
- Specified artists include at least: 陈奕迅, 孙燕姿, 周杰伦, 陶喆, and 西二.
- 孙燕姿 is a high-priority artist and should receive higher candidate weight and selection preference than the other specified artists unless manually changed in `/manage/music`.
- Search style rule: mainly 2000s Mandarin lyrical songs, campus nostalgia, and Cantonese classics, with a small amount of folk, English rock, and game music; overall style should keep clear melody, emotional aftertaste, and avoid excessive noise.
- AI selects one song from the eligible candidate pool each day using random or weighted-random behavior guided by the style rule, then generates a recommendation reason.
- Configuration lives in the Music tab of `/manage`.
- Backend periodically synchronizes NetEase song metadata into the local candidate pool.
- Refresh happens daily at 08:00 Asia/Shanghai.
- Administrator cannot manually change the song for the current day.
- Daily song is saved to history.
- Every daily song gets an AI-generated recommendation reason.
- Future upgrade can recommend based on previous day's system content.

Output:
- Daily song with NetEase song id, title, artist, album, cover, playable URL when available, NetEase jump URL, play/pause control, recommendation reason, date, source rule, and history entry.

Failure handling:
- If NetEase playback URL is unavailable, show jump-to-NetEase action and keep metadata visible.
- If AI selection fails, use deterministic random fallback from enabled candidates.
- If candidate pool is empty, show setup/sync-needed fallback.
- If NetEase API is unavailable, use current-day cache, then previous daily song, then empty fallback.

Acceptance:
- Public user can play available NetEase audio or jump to NetEase when playback is unavailable.
- Daily selection uses only synchronized candidate-pool records.
- History persists.

### REQ-11 NetEase Candidate Pool Management

Input: administrator configures NetEase API and candidate rules.

Processing:
- `/manage/music` includes API status detection, artist/search-rule configuration, manual candidate-pool refresh, current candidate-pool list, daily-song history, failure logs, and "generate tomorrow recommendation" preview.
- NetEase API base URL is configurable and must not be hardcoded to one third-party service.
- The deployable NetEase API service contract must be documented with required endpoints, health check behavior, timeout/retry policy, and optional service access token if the deployed service is protected.
- No personal NetEase account login is required because the user has no NetEase playlist to import.
- Candidate records can be enabled, disabled, weighted, tagged, and refreshed from NetEase metadata.
- Backend periodically syncs candidate metadata from NetEase into the local database.
- Sync and playback-url failures are recorded as music sync/failure log entries visible in `/manage/music`.

Output:
- Backend can select from synchronized candidate records and frontend can render playback/jump affordances.

Failure handling:
- NetEase API failure is visible in `/manage/music` status and failure logs.
- Sync failure preserves existing candidate pool.
- Missing playback URL keeps the track selectable only if jump URL exists, or marks it unavailable according to admin policy.

Acceptance:
- Public frontend receives only song metadata, playback URL if available, and NetEase jump URL.
- Admin can configure sources, refresh candidates, inspect failures, and preview tomorrow's recommendation.

### REQ-12 Music Page Interaction

Input: public user hovers or interacts with music page.

Processing:
- Existing music page is retained.
- Daily song is prominent.
- Historical playlist/list remains.
- Hovering over a song for a short time shows an information card.
- Mobile optimization is optional/future task.

Output:
- Music display with preview playback and hover card.

Failure handling:
- Missing preview gracefully shows jump-only state.

Acceptance:
- Public user can preview and see hover card.

### REQ-13 AI Management

Input: administrator opens AI tab under `/manage`.

Processing:
- First version should include full AI management content, not only status/log/test.
- Include configuration status, model status, feature switches, prompt/template management, usage/call logs, test calls, and failure summaries.
- AI calls require administrator session.
- AI call audit/log entries are recorded.

Output:
- AI management dashboard.

Failure handling:
- Missing AI config shows safe status and disables tests.

Acceptance:
- AI tab shows config status, logs, prompts/templates, test entry, and feature controls.

### REQ-14 Structured Weak-Point Diagnosis

Input: public or administrator views mistake page.

Processing:
- Replace repeated flat weak-point cards with a diagnostic module.
- Module name should be understandable, for example "薄弱点诊断".
- Show weak-point clusters for recent time ranges.
- Each cluster includes name, subject, module, tags, error type, severity, mistake count, due count, recent count, last seen time, diagnosis, recommended actions, related mistakes, and related notes.
- Collapsed state shows summary.
- Expanded state shows related mistakes, related notes, AI remediation steps, and one-click actions such as start review, generate variants, generate knowledge card, and save plan.

Output:
- A structured diagnosis panel that explains what is weak, why, and what to do next.

Failure handling:
- If not enough data exists, show an empty/insufficient-context state.

Acceptance:
- Mistake page no longer repeats identical flat cards.
- Weak-point diagnosis can be expanded and acted on.

### REQ-15 Audit Logs

Input: protected action occurs.

Processing:
- Record login/logout, token revocation, content create/edit/delete, folder move/delete, tag rename/merge/delete, page settings changes, AI calls, NetEase music config/sync changes, and security changes.

Output:
- Audit log entries visible in `/manage`.

Failure handling:
- If audit logging fails, high-risk actions should report failure or record fallback error, depending action type.

Acceptance:
- Representative actions create audit records.

## Non-Functional Requirements

- Security: no admin mutation without administrator session; passkey-only actions enforced server-side.
- Privacy: no personal NetEase account credentials are required or stored for this iteration.
- Reliability: folder/tag operations should be transactionally safe.
- Recoverability: destructive actions require confirmation and audit logs; move operations support undo.
- Performance: right-click and drag/drop should not trigger large unnecessary reloads.
- Accessibility: icon-only buttons must have accessible names.
- Maintainability: route components should use hooks/services/API clients, not direct ad hoc API calls.
- Compatibility: public pages should continue working after site-level protection is removed.

## Out Of Scope For This Iteration

- Multiple passkeys.
- Multiple administrator accounts unless already supported.
- Public user login.
- Mobile-first redesign of music page.
- Apple Music / MusicKit integration.
- Local music-file storage/import link.
- AI recommendation based on previous day's content, except as future extension note.
- Bulk recursive folder deletion of child folders.
