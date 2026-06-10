# Requirements

## Problem Statement

The current site still behaves like an admin-centric system with public pages attached around it:

1. Public navigation is legacy-shaped and does not reflect the intended public reading experience.
2. `GENERAL` and management-forward placement make the site look structurally unfinished.
3. Discovery routes are split across old categories instead of one coherent public exploration system.
4. Public content pages do not yet form a complete site-wide closure loop.
5. Anonymous guest interaction does not exist as a first-class public domain.

## Functional Requirements

REQ-01: The public site must adopt a stable primary IA.

- Public primary routes must be: 首页, 博客, 笔记, 错题, 发现, 留言, 关于.
- `管理` must remain accessible but not appear as a peer of the primary public content routes.

REQ-02: Shared navigation must be reorganized into two named groups.

- Group 1: `公开内容`
- Group 2: `互动探索`
- Desktop and mobile navigation must represent the same public hierarchy.

REQ-03: `/manage` must keep the single-route model, but anonymous visitors must see a complete public entry page rather than a backend-looking shell.

REQ-04: Blogs must remain fully public.

- Blog list and detail pages remain readable in full.
- Public-facing backend action buttons must not be shown to anonymous visitors.

REQ-05: Notes must remain fully public.

- Note list and detail pages remain readable in full.
- Public-facing backend action buttons must not be shown to anonymous visitors.

REQ-06: Mistakes must use limited public views.

- Public list remains queryable.
- Public detail may show title, question, correct answer, tags/subject/date.
- Public detail must not show internal answer, AI analysis, review metrics, or private study diagnostics.

REQ-07: `推荐分享` and `优秀博客` must merge into `发现`.

- `发现` must support at least three internal sections:
  - 推荐分享
  - 优秀博客
  - 优秀笔记
- Legacy `/share` and `/bloggers` routes must follow an explicit compatibility strategy instead of remaining behaviorally ambiguous.

REQ-08: Discovery curation must use a consistent editorial weighting model.

- Public discovery rendering must support curated prominence using fields such as `featured`, `stars`, and `sort_order`.
- `stars` is editorial weight, not end-user social count.

REQ-09: A first-class guest message domain must be added.

- Anonymous users can submit messages.
- Public users can read visible messages.
- Messages can attach to at least `home`, `blog`, `note`, or `mistake`.

REQ-10: Guest messages must have realistic abuse controls.

- The system must not rely on MAC address detection.
- Abuse controls must be server-side and must include IP-based rate limiting or temporary banning.
- Repeated abuse must be traceable for admin moderation.

REQ-11: The whole site must satisfy site-wide closure.

- No primary public page may be a dead end.
- Every primary public page must link onward to at least two other core site destinations.
- Every content detail page must route users back into the main reading/discovery/interaction graph.
- Management changes that affect public curation or moderation must be visible back in the public site.

REQ-12: Closure must exist at both navigation and data levels.

- Navigation closure: users can move across the main site without orphan paths.
- Data closure: curation, relations, and moderation affect what the public sees.

## Acceptance Criteria

AC-01: Shared desktop navigation renders `公开内容` and `互动探索` instead of `GENERAL`.

AC-02: Public primary nav contains blog, notes, mistakes, discover, guestbook, and about; management is demoted.

AC-03: Anonymous `/manage` renders a public-facing management entry experience.

AC-04: Blog detail remains full-read and shows no anonymous backend action buttons.

AC-05: Note detail remains full-read and shows no anonymous backend action buttons.

AC-06: Mistake public detail omits internal answer, AI analysis, and internal review diagnostics.

AC-07: Discover page contains three sections: 推荐分享, 优秀博客, 优秀笔记.

AC-07.1: Legacy `/share` and `/bloggers` routes resolve into the new discovery experience through an intentional compatibility path.

AC-08: Guest messages can be created anonymously and displayed publicly under the allowed visibility rules.

AC-09: Guest message abuse limits trigger correctly under repeated rapid requests.

AC-10: Each primary public route offers onward movement into at least two other core routes.

## Non-Goals

- Do not replace the current admin auth architecture.
- Do not redesign unrelated note-editor or AI-generation internals unless directly needed by the public-site scope.
- Do not build a full social system with likes/follows/replies in this task unless the scope is explicitly expanded later.
