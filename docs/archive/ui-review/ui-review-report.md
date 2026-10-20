# UI Browser Review Report

## 1. Execution summary

**UI Review: PARTIAL.** The inherited `localhost:2025` Next process returned HTML but failed required CSS/JS chunks on every initial capture. A fresh independent `localhost:3000` process rendered healthy public and authenticated management pages, so the initial failure is confirmed as local runtime-state drift rather than a source-level UI conclusion. Authenticated management review then identified a genuine mobile table usability issue.

No business code, database, migration, authentication state, or Git commit was changed. No authentication was bypassed.

## 2. Test environment

- Date: 2026-07-19, Asia/Shanghai
- Frontend: inherited `next-server (v16.2.10)`, PID 74627, port 2025; independent clean review instance on port 3000
- URLs: `http://localhost:2025` (broken inherited process) and `http://localhost:3000` (fresh review instance)
- Browser: Playwright Chromium 149.0.7827.55
- Viewports: 1440x900 desktop, 1280x800 laptop, 390x844 mobile
- Backend: configured local API is `http://localhost:8000`; `/health` returned 404, while `/api/auth/passkey/status` returned 200.
- Authentication follow-up: password login succeeded with the user-supplied local temporary account; credentials were neither recorded nor retained. The browser context was closed after review.

## 3. Page coverage and screenshots

43 route modules were discovered. 23 directly addressable routes were captured at desktop and mobile; 6 representative routes were also captured at laptop width. The initial pass yielded 46 desktop, 12 laptop, 46 mobile, and 1 interaction-state PNGs. The follow-up added 7 authenticated desktop screenshots, 5 authenticated mobile screenshots, and 10 clean-instance public screenshots. See [page-inventory.md](page-inventory.md) and [screenshot-index.md](screenshot-index.md).

Dynamic detail routes were not opened because no safe public identifiers were available. Authenticated follow-up covered `/manage`, `/manage/dashboard`, `/manage/questions`, `/manage/mistakes`, `/manage/review`, and `/manage/ai/runs`; remaining workspace routes were not covered.

## 4. P0 / P1 issues

### UIR-001 — P1: inherited dev-server static chunk failure

- Pages / viewports: all reviewed routes, all three viewports.
- Evidence: `artifacts/mobile/mistakes-390x844-first.png`, `artifacts/desktop/guestbook-1440x900-first.png`.
- Reproduce: open any route in a new browser context; inspect Network. The HTML loads 200, but the hash-referenced styles/scripts return 500 or 404.
- User impact: the inherited developer process is unusable for local QA, although a fresh process renders correctly.
- Likely cause: stale/mismatched Next/Turbopack chunk manifest in the long-running process.
- Required change: document a safe local reset/restart path and add an asset-smoke gate that loads a new context and asserts all JS/CSS request statuses are <400.
- Acceptance: five consecutive fresh loads of `/`, `/notes`, `/mistakes`, `/guestbook`, and `/manage` produce no failed CSS/JS request and screenshots show the intended style layer.

### UIR-007 — P1: legacy management table is not mobile-operable

- Page / viewport: authenticated `/manage` at 390x844.
- Evidence: `artifacts/authenticated/manage-390x844-authenticated.png`.
- Reproduce: sign in, keep the legacy manager's content-management tab selected, then view at 390px width.
- User impact: a user can read titles but cannot reliably see dates or management actions; status chips wrap vertically and the dense table does not communicate its horizontal affordance.
- Required change: at <=640px replace this table with content cards, or expose an explicitly horizontally scrollable table with sticky title/selection column and a visible edit action. Defer delete to an overflow menu/confirmation.
- Acceptance: title, type, date, and edit action are all readable/actionable at 390px without guessing where hidden columns are.

### UIR-002 / UIR-003 — P2: load and mobile fail-safe gaps in the broken instance

- Page / viewport: all reviewed pages at 390x844.
- Evidence: `artifacts/mobile/image-toolbox-390x844-first.png`, `artifacts/mobile/mistakes-390x844-first.png`.
- Reproduce: repeat UIR-001 at 390px width.
- User impact: raw SVGs consume most of the screen and expected tap targets/navigation lose form and hierarchy.
- Required change: fix UIR-001 first, then add 390px screenshot assertions for the nav, primary action, form field, modal, and long-list states.
- Acceptance: mobile navigation remains reachable; main controls have at least 44x44px targets; no visual regression or raw SVG layout appears.

## 5. P2 / P3 issues

See [issue-inventory.md](issue-inventory.md) for UIR-002 through UIR-006. Fresh-instance screenshots allow a preliminary management UI review; full public visual review remains incomplete because the initial public captures used the unhealthy process.

## 6. Global design consistency and desktop analysis

The clean authenticated management desktop view has a coherent pale-blue/white visual system, clear navigation, readable table rows, and consistent cyan emphasis. The legacy management desktop table is dense but scannable. The mobile legacy table does not carry this quality through to 390px; see UIR-007.

No horizontal overflow was measured at 1440px or 1280px; this is recorded only as a raw geometry fact, not a UI pass.

## 7. Mobile analysis

The clean workspace dashboard and question-list screens render a coherent single-column mobile layout with persistent bottom navigation. The legacy manager's table is the exception: core metadata/actions become clipped or impractical at 390px. Retest menu open/closed, dialog, field validation, long list/table, and keyboard viewport states after its responsive redesign.

## 8. Console, network, and static resources

Across 52 unique route/viewport observations, Chromium captured 108 console errors, 108 failed requests, and 108 >=400 responses. No hydration, React key, DOM nesting, or uncaught page exception was observed beyond the resource failures.

Repeated evidence:

- `500`: `/_next/static/chunks/23666q1ipim6p.css`, `/_next/static/chunks/2amyw6tbv9dkb.js`
- `404`: `/_next/static/chunks/3uehc4ecw3k49.css`, `/_next/static/chunks/0l7hucj3buzbt.js`

Direct verification after the run returned the same 500/404 statuses. This is reproducible rather than an isolated browser timing artifact.

## 9. Modification priority and suggested order

1. **P1 — Make legacy `/manage` content management responsive at 390px.** Use cards or a deliberately scrollable table.
2. **P1 — Add local dev-server asset smoke coverage.** Fresh browser context; fail on any CSS/JS >=400.
3. **P2 — Implement time-bounded, actionable load/error/auth states.** Do not leave `加载中...` / `验证中...` indefinitely.
4. **P2 — Remove zoom restriction and duplicate viewport declaration.** Preserve browser zoom.
5. **P2/P3 — Repeat full public visual QA against a healthy fresh server.** Cover hierarchy, spacing, type, contrast, component states, menus, dialogs, and authenticated management flows.

## 10. Post-fix acceptance checklist

- [ ] All current HTML-referenced CSS and JS chunks return 200 in a fresh browser context.
- [ ] No console error, failed request, hydration warning, or uncaught exception on primary routes.
- [ ] Desktop 1440x900 and laptop 1280x800 screenshots show the intended layout.
- [ ] Mobile 390x844 shows usable navigation, no horizontal overflow, no clipped dialog, and >=44px primary targets.
- [ ] Empty, loading, error, and authorization states are visually distinct and provide next actions.
- [ ] Browser zoom remains enabled; only one viewport tag is emitted.
- [ ] Public content routes stay public; protected management/editor/review routes retain server-side auth boundaries.
- [ ] Authenticated management/detail route review is run with a supplied non-production account.

## 11. Uncovered scope

The following could not be assessed: authenticated workspace screens, dynamic detail/edit routes without known safe IDs, backend-dependent populated/empty/error permutations, uploads, destructive confirmations, AI flows, review submission, modal/dropdown focus behavior, pagination, and meaningful hover/focus/disabled states. They require a healthy style layer and, where appropriate, a user-provided non-production test account.
