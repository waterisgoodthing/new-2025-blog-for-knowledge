# P0 Precheck Audit

## P0 Scope Freeze

The source P0 scope is docs/roadmap-design.md section 2 and docs/roadmap-tasks.md P0:

1. Management bulk-delete wording.
2. Destructive-action presentation and confirmation.
3. /manage login-state and administrator-boundary acceptance.
4. Historical task-document cleanup.

## Documentation Conflicts

| Item | Recorded claim | Precheck interpretation |
| --- | --- | --- |
| P0 status | Roadmap task boxes are marked complete. | Completion is historical evidence, not current acceptance evidence. |
| Auth description | The roadmap describes an unconditional bypass implementation. | Current settings expose AUTH_BYPASS and AUTH_BYPASS_ALLOW; source and effective environment must be checked separately. |
| P0 validation | Historical login/browser checks cite a dated temporary environment. | They do not establish current runtime or browser acceptance. |
| Documentation authority | roadmap-tasks calls itself current while other documents retain historical sync and route assertions. | Present-state claims require source comparison before use. |

## Scope Boundary

This precheck may correct only its own workflow evidence. It does not revise historical roadmap documents, change P0 source, run stateful tests, or use credentials.

## Destructive-Action Source Audit

| Surface | Current source evidence | Classification |
| --- | --- | --- |
| Manage bulk delete | handleDeleteSelected rejects stale selection, summarizes note/blog/mistake counts, asks for confirmation, calls batchDeleteNotes, and reports success or failure. | VERIFIED in source. |
| Manage single delete | handleDeleteOne labels the content type, asks for confirmation, calls deleteNote, and reports success or failure. | VERIFIED in source. |
| Manage delete presentation | Bulk action uses a red weak-background variant and table-row delete uses a red weak-background variant. | VERIFIED in source; visual browser parity is UNVERIFIED. |
| Note-detail delete | The action is admin-conditional, asks for confirmation, deletes through deleteNote, and uses a red weak-background variant. | VERIFIED in source; public-session behavior is not browser-verified here. |
| Blog editor and list delete | Source contains confirmation messages and red weak-background styling for the audited controls. The list action removes selected items from local editable state before a save action. | PARTIAL: visual and confirmation presence verified; persistence and cancellation behavior require a controlled browser test. |

No source defect requiring a P0 code change was proven by this static audit.

## Authentication-Boundary Source Audit

| Boundary | Current source evidence | Classification |
| --- | --- | --- |
| Bypass semantics | AUTH_BYPASS is active only when both AUTH_BYPASS and AUTH_BYPASS_ALLOW are true. Defaults and the example configuration are false; production startup rejects the dual-true combination. | VERIFIED in source; effective runtime environment intentionally not inspected. |
| Normal session path | Login verifies a password, creates an AdminSession, and returns an HttpOnly admin_session cookie. get_current_user and get_current_admin resolve that cookie and return 401 or 403 as appropriate. | VERIFIED in source. |
| Frontend /manage gate | ManagePage calls getMe before showing the admin surface and renders the login flow when the session is not an administrator. AuthGate redirects protected routes to /manage. | VERIFIED in source; browser redirect and cookie behavior are UNVERIFIED. |
| Protected writes | Note create, update, delete, batch delete, upload, version, backlink, review, and AI routes shown in the audit use get_current_admin. | VERIFIED in source. |
| Public reads | Note list and detail use optional identity rather than a mandatory admin dependency. | VERIFIED in source; current anonymous filtering requires a live or targeted test before closure. |
| Roadmap auth description | Historical P0 text describes JWT Bearer-token transport. Current source uses an HttpOnly session cookie. | CONTRADICTED documentation; it must not be used as an implementation instruction. |

No credential, environment file, browser session, or live endpoint was accessed.

## Validation Evidence Classification

| Requirement | Existing evidence | Current precheck status | Safe next verification |
| --- | --- | --- | --- |
| Manage type-summary confirmation | Current source implements the required string construction. No current browser assertion was found. | PARTIAL. | Controlled browser test with disposable content or mocked API; do not delete user content. |
| Weak-red delete presentation | Current source has the required style families. No current visual comparison was found. | PARTIAL. | Three-viewport browser inspection of manage, note detail, blog editor, and blog list. |
| /manage unauthenticated experience | Historical browser evidence is dated 2026-06-03. Current ManagePage and AuthGate source support the intended branch. | PARTIAL. | Fresh browser session with no admin cookie; verify login form and no protected data request. |
| Administrator mutation acceptance | Historical temporary-environment evidence is dated and the current flow now uses cookie sessions. | UNVERIFIED. | Isolated backend/database with AUTH_BYPASS and AUTH_BYPASS_ALLOW false, a disposable administrator, exact fixture cleanup, and browser/API checks. |
| Anonymous and non-admin rejection | Current backend tests include 401 and 403 assertions for protected management routes; not run in this precheck. | DOCUMENTED_ONLY. | Run targeted tests only in an approved isolated test environment. |
| Production bypass safety | Source and a targeted monitoring test exist for production dual-true rejection; neither effective environment nor test execution was checked here. | DOCUMENTED_ONLY. | Source-only review is complete; any runtime check requires separate environment authorization. |

## Test-Safety Decision

No test command ran. Frontend and backend suites may create fixtures or require database dependencies. This precheck therefore does not treat their mere presence as execution evidence and does not authorize running them against the shared local or production database.

## Pre-Execution Decision

Status: PARTIAL / NO P0 SOURCE CHANGE AUTHORIZED

- P0 deletion wording and weak-red action treatment are source-present.
- P0 documentation is stale in material ways, including its old Bearer-token transport description.
- Current anonymous, administrator, cookie-session, persistence, and visual acceptance evidence is incomplete.
- No source defect was proven that authorizes a corrective P0 patch.

If fresh P0 acceptance is needed, create and approve one narrow validation task with an isolated backend/database, AUTH_BYPASS and AUTH_BYPASS_ALLOW both false, a disposable administrator, no production cookies, exact fixture cleanup, and browser checks for anonymous, admin, cancel, and delete-success paths. Do not combine it with route, editor, Markdown, or visual-system implementation.
