# Design

## Closure Lanes

### Public Read Lane

`/`, `/blog`, `/blog/[id]`, `/notes`, `/notes/[id]`, and `/mistakes` remain anonymous-readable according to the existing public Note contract. Admin-only review stats, editing, deletion, upload, AI, and capture controls must be hidden or disabled without causing repeated `401/403` requests.

### Private Manage Lane

`/manage/**`, `/mistakes/review`, `/write-note`, `/write-note/[slug]`, `/write-mistake`, and `/write-mistake/[slug]` are operator workflows. Page-level `AuthGate` improves access experience; backend `get_current_admin` remains the security boundary.

### Compatibility Lane

Existing old routes are classified as active, redirect/notice, or preserved legacy entry points before any change. No route is removed solely because a newer `/manage` route exists. Any redirect must preserve intent and avoid leaking private data.

### Data Lane

The database is treated as data-bearing. Validation captures counts and representative IDs before/after. No cleanup script, re-keying, silent migration, or destructive route behavior is allowed.

## Proposed UI Behavior

- Public pages render gracefully for anonymous users and only add admin actions after confirmed admin state.
- Protected pages show a consistent login/access state before editor or review controls appear.
- Broken/missing resources show explicit recovery links rather than blank screens.
- Placeholder/future routes remain visibly non-operational and do not call reserved APIs.
