# Tasks

Status: Phase 0 (scope lock) and Phase 1 (shared navigation and public shell) implemented on 2026-06-10. Code changes in `vertical-nav.tsx`, `mobile-nav.tsx`, `nav-card.tsx`, and `share-card.tsx`.

## Phase 0: Scope Lock

- [x] **P0-01** Confirm the public IA and closure contract.
  - Lock primary public routes: 首页 / 博客 / 笔记 / 错题 / 发现 / 留言 / 关于.
  - Lock nav groups: `公开内容` and `互动探索`.
  - Lock management demotion from the primary public nav.

- [x] **P0-02** Confirm public content boundaries.
  - 博客全文公开.
  - 笔记全文公开.
  - 错题公开受限，仅展示题目与正确答案等轻量字段.

- [x] **P0-03** Confirm discovery and guest-message contracts.
  - `推荐分享` + `优秀博客` 合并为 `发现`.
  - `发现` 增加 `优秀笔记`.
  - 留言允许匿名提交，但必须有服务端风控和治理入口.

## Phase 1: Shared Navigation And Public Shell

- [x] **P1-01** Rebuild shared desktop navigation around the approved public IA.
  - Replace `GENERAL` with `公开内容`.
  - Add `互动探索`.
  - Demote `管理` to a weak bottom entry.

- [x] **P1-02** Align mobile navigation with the same IA.
  - Mobile route grouping must mirror desktop semantics.

- [x] **P1-03** Update home-page public shell so it distributes users into the new closure graph.
  - Ensure home is a true public hub, not a partial admin/product shell.

- [x] **P1-04** Make the home page explicitly participate in site-wide closure.
  - Home must link into all primary public destinations.
  - Home must expose onward paths into discovery and guest interaction, not only legacy creation residue.

## Phase 2: `/manage` Anonymous Experience

- [ ] **P2-01** Redesign anonymous `/manage` into a full public-facing entry page.
  - Preserve single-route behavior.
  - Remove backend-shell feel from the anonymous state.

- [ ] **P2-02** Keep authenticated `/manage` behavior intact while separating the visual shell from the anonymous state.

## Phase 3: Public Content Boundaries

- [ ] **P3-01** Remove anonymous backend action affordances from blog public views.

- [ ] **P3-02** Remove anonymous backend action affordances from note public views.

- [ ] **P3-03** Create a limited public mistake-detail presentation.
  - Hide my answer, AI analysis, review metrics, and internal study diagnostics.

- [ ] **P3-04** Add content-to-content closure links across blog/note/mistake detail flows.

## Phase 4: Discover System Merge

- [ ] **P4-01** Merge legacy `share` and `bloggers` public positioning into `发现`.

- [ ] **P4-02** Introduce `优秀笔记` into the discovery system.

- [ ] **P4-03** Align discovery rendering with a common editorial weighting model.
  - Support `featured`, `stars`, and `sort_order` behavior through the chosen data path.

- [ ] **P4-04** Define and implement legacy route compatibility.
  - `/share` must intentionally resolve into the discovery experience.
  - `/bloggers` must intentionally resolve into the discovery experience.
  - Avoid leaving duplicate first-class public paths with unclear ownership.

## Phase 5: Guest Message Domain

- [ ] **P5-01** Add guest-message backend contract and persistence path.
  - Include source attachment capability for `home/blog/note/mistake`.

- [ ] **P5-02** Add public guest-message UI.
  - Submission flow
  - Public message display
  - Cross-links back to attached content

- [ ] **P5-03** Add abuse controls and moderation hooks.
  - IP-based rate limiting / temporary banning
  - traceable moderation data for admin handling

- [ ] **P5-04** Make guest messages participate in site-wide closure.
  - Message lists should route back to attached content where present.
  - Content detail pages should be able to route into related discussion.

## Phase 6: Site-Wide Closure Pass

- [ ] **P6-01** Verify every primary public route has onward links into the core graph.

- [ ] **P6-02** Verify each content detail route participates in the site-wide closure loop.

- [ ] **P6-03** Verify management-to-public feedback loops for discovery and moderation.

- [ ] **P6-04** Add explicit closure handling for `关于`.
  - About must not be a terminal page; it should route back into home, discovery, or live content.

- [ ] **P6-05** Add explicit closure handling for `发现`.
  - Discover must route users into curated internal content and/or attached discussion, not just isolated listing cards.

## Phase 7: Validation

- [ ] **P7-01** Run frontend validation.
  - `npx tsc --noEmit`
  - build-sensitive checks as needed

- [ ] **P7-02** Run backend validation for new guest-message/public-route contracts.

- [ ] **P7-03** Perform browser validation for navigation, discover, guest messages, and public detail boundaries.

- [ ] **P7-04** Record results in `validation.md`.
