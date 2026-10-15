# Design

## Scope Boundary

This task redesigns the public information architecture and selected content flows. It should not casually refactor unrelated editor internals, AI pipelines, or backend admin logic outside the approved public-site scope.

## Product Direction

The site should behave like a public knowledge garden with a complete flow, not an admin-first tool that also happens to expose public pages.

Primary public principles:

1. Public visitors should always understand where to go next.
2. No major public page should be a dead end.
3. Public content and management content must have visibly different shells.
4. Discovery and guest interaction must feed users back into the main content graph.

## Site-Wide Closure Model

The closure requirement expands from individual modules to the whole site.

### 1. Public Navigation Loop

All primary public entry points must be reachable through a stable shared nav:

- 首页
- 博客
- 笔记
- 错题
- 发现
- 留言
- 关于

`管理` remains reachable but is demoted from the main public grouping.

### 2. Content Loop

The content system forms the main reading loop:

- 博客 -> related notes / discovery / messages
- 笔记 -> related blogs / related mistakes / discovery / messages
- 错题 -> related notes / nearby mistakes / messages

In addition, top-level public pages must also close the loop:

- 首页 -> all primary public destinations
- 发现 -> internal content or external curated resources, plus return to core content and guest interaction
- 留言 -> recent discussed content, home, and discovery
- 关于 -> home, discovery, and at least one live content path

### 3. Discovery Loop

`发现` is no longer a single legacy route category. It becomes a curation hub containing:

- 推荐分享
- 优秀博客
- 优秀笔记

Discovery items should route users into either:

- external resources, or
- internal long-form content and notes.

Legacy routes must not be left ambiguous after the merge:

- `/share` should become a compatibility route that forwards users into the new `发现` experience with 推荐分享 active.
- `/bloggers` should become a compatibility route that forwards users into the new `发现` experience with 优秀博客 active.
- `优秀笔记` should live inside the same discovery experience instead of creating another top-level public route.

This preserves old links while keeping one exploration hub.

### 4. Interaction Loop

`留言` is not a floating wall. Messages should support source attachment:

- `home`
- `blog`
- `note`
- `mistake`

This allows:

- content detail pages to show related discussion,
- the guestbook page to surface recent discussion across the site,
- management moderation to influence the public interaction layer.

### 5. Management Feedback Loop

Management actions should flow back into public presentation:

- discovery curation fields (`featured`, `stars`, `sort_order`) affect public discovery/home rendering;
- guestbook moderation affects public visible messages;
- content publication and relation metadata affect public cross-links.

## Information Architecture

### Public Desktop/Mobile Navigation Groups

Use two public groups:

- `公开内容`
  - 博客
  - 笔记
  - 错题
- `互动探索`
  - 发现
  - 留言
  - 关于

`管理` is placed as a weak bottom entry, not in either public group.

### `/manage` Anonymous State

Keep the single `/manage` route, but redesign the anonymous state as a complete public-facing management entry page:

- clear title and explanation
- passkey/password login options
- no backend-shell framing
- visually aligned with the public site

Authenticated state continues to render the admin console.

## Public Content Boundaries

### Blogs

- stay fully public
- keep full detail reading
- remove public-facing backend action buttons

### Notes

- stay fully public
- keep full detail reading
- remove public-facing backend action buttons
- add cross-links to blogs/discovery/messages

### Mistakes

- public list stays searchable/filterable
- public detail shows:
  - title
  - question
  - correct answer
  - lightweight metadata like subject/tags/date
- public detail hides:
  - my answer
  - internal review metrics
  - AI analysis
  - error-reason and review strategy panels

## Discovery Data Model Direction

The merged discovery system should converge on a common curation shape across discovery-adjacent entities:

- `featured: boolean`
- `stars: number`
- `sort_order: number`
- `status: active | hidden`

`stars` is an editorial curation weight, not a public social-like count.

## Guest Message Direction

### Functional Shape

- anonymous users can submit messages
- public users can read already-visible messages
- messages may attach to site entities
- admins can moderate/remove abusive content

### Abuse Control

The web app cannot obtain MAC addresses. Abuse control should be server-side and realistic:

- IP-based rate limiting
- user-agent recording
- cookie/device hint if needed
- temporary bans with escalation windows
- audit trail for repeated abuse

## Risks

- Public/full-public notes may expose more internal language than expected unless detail templates are intentionally cleaned up.
- Merging legacy discovery routes without a stable shared model may cause partial UI migration.
- Guest messages without server-side constraints will invite abuse very quickly.
- Closure can become superficial if links are added without relation logic or source attachment.

## Recommended Implementation Order

1. Create the new public IA and navigation model.
2. Redesign `/manage` anonymous shell.
3. Merge discovery routes and curation structure.
4. Add guest message domain and moderation/rate-limit path.
5. Retrofit blog/note/mistake detail pages for site-wide closure.
