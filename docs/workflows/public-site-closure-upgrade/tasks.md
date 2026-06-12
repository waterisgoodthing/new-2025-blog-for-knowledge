# Tasks

Status: All phases implemented and browser-validated on 2026-06-12. `npx tsc --noEmit` passes. Backend 108 routes loaded. Browser validation completed.

## Phase 0: Scope Lock

- [x] **P0-01** Confirm the public IA and closure contract.
- [x] **P0-02** Confirm public content boundaries.
- [x] **P0-03** Confirm discovery and guest-message contracts.

## Phase 1: Shared Navigation And Public Shell

- [x] **P1-01** Rebuild shared desktop navigation around the approved public IA.
- [x] **P1-02** Align mobile navigation with the same IA.
- [x] **P1-03** Update home-page public shell so it distributes users into the new closure graph.
- [x] **P1-04** Make the home page explicitly participate in site-wide closure.

## Phase 2: `/manage` Anonymous Experience

- [x] **P2-01** Redesign anonymous `/manage` into a full public-facing entry page.
  - Avatar + site title branding, login form preserved, quick-links to all public routes added.
- [x] **P2-02** Keep authenticated `/manage` behavior intact while separating the visual shell from the anonymous state.
  - Authenticated state unchanged; only `LoginForm` component redesigned.

## Phase 3: Public Content Boundaries

- [x] **P3-01** Remove anonymous backend action affordances from blog public views.
  - Edit button gated with `useAdminAuth` in `blog-detail-content.tsx`.
- [x] **P3-02** Remove anonymous backend action affordances from note public views.
  - Edit/delete buttons gated with `useAdminAuth` in `note-detail-content.tsx`.
- [x] **P3-03** Create a limited public mistake-detail presentation.
  - Hidden for non-admin: 我的答案, 复习状态, 错因与解析, AI 解析, 图示解析, 关联知识面板, 开始复习 button.
  - Visible: 题目, 正确答案, 标签, difficulty/subject/date metadata.
- [x] **P3-04** Add content-to-content closure links across blog/note/mistake detail flows.
  - Non-admin blog detail: bottom links to 发现/留言/更多博客/首页.
  - Non-admin note/mistake detail: bottom links to 发现/留言/首页.

## Phase 4: Discover System Merge

- [x] **P4-01** Merge legacy `share` and `bloggers` public positioning into `发现`.
  - New `/discover` page with tabbed sections: 推荐分享, 优秀博客, 优秀笔记.
- [x] **P4-02** Introduce `优秀笔记` into the discovery system.
  - Notes section uses `listNotes({ featured: true, sort_by: 'sort_order' })` — only notes with `sort_order > 0` appear.
  - Backend `list_notes` endpoint now supports `featured` and `sort_by` query params.
- [x] **P4-03** Align discovery rendering with a common editorial weighting model.
  - Shares and bloggers sorted by `stars` descending. Notes sorted by `sort_order` descending.
  - All sections support search filtering.
- [x] **P4-04** Define and implement legacy route compatibility.
  - `/share` redirects non-admin to `/discover?tab=shares`; admin retains edit mode.
  - `/bloggers` redirects non-admin to `/discover?tab=bloggers`; admin retains edit mode.

## Phase 5: Guest Message Domain

- [x] **P5-01** Add guest-message backend contract and persistence path.
  - Model: `GuestMessage` (content, nickname, attachment_type/slug, ip, user_agent, status).
  - Model: `GuestMessageBan` (ip, reason, expires_at).
  - Schema: `GuestMessageCreate`, `GuestMessageOut`, `GuestMessageListResponse`, `GuestMessageModerate`.
  - Router: `POST/GET /api/guest-messages`, `PUT /{id}/moderate`, `GET /bans`.
- [x] **P5-02** Add public guest-message UI.
  - `/guestbook` page: submission form, public message list, pagination, cross-links to attached content.
- [x] **P5-03** Add abuse controls and moderation hooks.
  - IP-based rate limiting: 5 messages/60s window.
  - Auto-ban: 24h temporary ban on rate limit violation.
  - Ban table with admin listing endpoint.
  - User-agent recorded on every submission.
- [x] **P5-04** Make guest messages participate in site-wide closure.
  - Guestbook page has bottom links to 首页/发现/博客/笔记.
  - Messages with attachments always render a "查看关联内容" link: home → `/`, blog/note/mistake with slug → detail, without slug → list page.
  - Admin moderation UI added to `/manage` as `留言审核` tab (filter all/visible/hidden, hide/restore actions).

## Phase 6: Site-Wide Closure Pass

- [x] **P6-01** Verify every primary public route has onward links into the core graph.
  - Home: nav-card → all routes. Discover: bottom links. Guestbook: bottom links. About: bottom links.
- [x] **P6-02** Verify each content detail route participates in the site-wide closure loop.
  - Blog/note/mistake detail: non-admin closure links to 发现/留言/首页.
- [x] **P6-03** Verify management-to-public feedback loops for discovery and moderation.
  - Admin share/blogger edits affect discover page data.
  - Admin note sort_order > 0 makes note appear in discover "优秀笔记".
  - Guest message hide/restore in manage tab directly affects public guestbook visibility.
- [x] **P6-04** Add explicit closure handling for `关于`.
  - About page now has bottom links: 首页/发现/博客/笔记/留言.
- [x] **P6-05** Add explicit closure handling for `发现`.
  - Discover page has bottom links: 浏览博客/浏览笔记/浏览错题/留言板.

## Phase 7: Validation

- [x] **P7-01** Run frontend validation.
  - `npx tsc --noEmit`: 0 errors.
- [x] **P7-02** Run backend validation for new guest-message/public-route contracts.
  - All new imports resolve. `main.py` loads with 108 routes.
- [x] **P7-03** Perform browser validation for navigation, discover, guest messages, and public detail boundaries.
  - Browser validated on 2026-06-12. See validation.md for full evidence.
- [x] **P7-04** Record results in `validation.md`.
