# Route and navigation audit

Current repair status: `R1–R5/G1 are historical complete; FIX-03～05 complete; F4 input is ready for separate approval; no route implementation is authorized`. The dated route inventory and decisions below remain source-backed historical evidence, not an `EXECUTING` route-change plan.

## R1 — current source inventory (2026-08-10)

| Route family | Current source evidence | Access boundary | Navigation / compatibility observation |
| --- | --- | --- |
| Public content | `src/app/notes/page.tsx`, `src/app/notes/[id]/page.tsx`, `src/app/blog/page.tsx`, `src/app/blog/[id]/page.tsx`, `src/app/mistakes/page.tsx` | No page-level `AuthGate`; local `useAdminAuth()` is display state only. | `src/lib/content-routes.ts` sends note/mistake detail to `/notes/[slug]` and blog detail to `/blog/[slug]`. |
| Private workspace | `src/app/manage/(workspace)/layout.tsx` wraps every `/manage/*` workspace page in `AuthGate`. | Strict `AuthGate`; backend still owns authorization. | Home learning-card, sidebar and workspace components link directly to `/manage/dashboard`, `/manage/review`, `/manage/mistakes`, `/manage/questions` and sibling workspace URLs. |
| Legacy blog writer | `src/app/write/page.tsx` and `src/app/write/[slug]/page.tsx` remain route files and wrap `WriteEditor` in `AuthGate`. | Strict `AuthGate`. | Workspace dashboard still links to `/write`; this is a live private entry, not an unused file. |
| Legacy note writer | `src/app/write-note/page.tsx` and `src/app/write-note/[slug]/page.tsx` remain route files and wrap their editor content in `AuthGate`. | Strict `AuthGate`. | Workspace dashboard still links to `/write-note`; current content helper instead directs generic note/blog edits to `/manage/dashboard`, so the intended direct-edit owner is not proved by this helper alone. |
| Legacy mistake writer/review | `src/app/write-mistake/page.tsx`, `src/app/write-mistake/[slug]/page.tsx`, and `src/app/mistakes/review/page.tsx` remain AuthGate-protected. | Strict `AuthGate`. | The legacy mistake page labels itself compatibility mode and points to `/manage/mistakes`; public `/mistakes` links the review action to `/manage/review`. |

### Redirect and route-group check

- Source search found navigation calls and helper-level cutover comments, but no Next `redirect()` or `permanentRedirect()` implementing a redirect for the five route families above.
- `(workspace)` is a Next.js route group: its name is absent from public URLs; the owner family is `/manage/*`, not `/manage/workspace/*`.
- The inventory is source-based. No live browser run was performed in R1, so current browser-only behavior is `UNKNOWN` rather than inferred from historic timing notes.

## R2 — ownership classification and compatibility risk (2026-08-10)

| Classification | Routes | Current contract | Compatibility risk if changed now |
| --- | --- | --- | --- |
| Public read owner | `/notes`, `/notes/[id]`, `/blog`, `/blog/[id]`, `/mistakes` | Must remain ungated; admin controls are conditional display only. | High: an AuthGate or redirect to `/manage` would violate root access rules and break public links. |
| Private workspace owner | `/manage/*` (including `/manage/dashboard`, `/manage/review`, `/manage/mistakes`) | Shared workspace layout is AuthGate-protected; route-group text is not part of the URL. | High: weakening the layout or changing workspace URLs affects private learning flows. |
| Legacy-but-live private writers | `/write`, `/write/[slug]`, `/write-note`, `/write-note/[slug]`, `/write-mistake`, `/write-mistake/[slug]` | AuthGate-protected page files still exist; dashboard quick actions still target `/write` and `/write-note`; mistake writer announces compatibility mode. | High: deletion/redirect would break in-product entry points and possible bookmarks; no browser evidence proves that their flows are retired. |
| Legacy private review alias | `/mistakes/review` | Root rule keeps it AuthGate-protected; existing compatibility test expects a non-permanent redirect to `/manage/review`. | Medium: redirect semantics must preserve strict access and links; source-only inspection does not prove live redirect behavior. |

The existing `src/app/batch7-compatibility.test.ts` expresses the current compatibility contract: public routes have no page AuthGate, listed private entries retain AuthGate, old write routes remain while generic content links target `/manage/*`, and `/mistakes/review` is configured to redirect to `/manage/review`. This test is evidence of intended source contract, not a substitute for a live browser request.

## R3 — option comparison (2026-08-10)

| Option | What it would mean | Benefits | Material risks / missing evidence |
| --- | --- | --- | --- |
| Retain compatible coexistence | Keep public read routes, `/manage/*` workspace and all legacy writers at their current URLs; describe `/manage/*` as workspace owner and legacy writers as compatibility owners until a dedicated migration. | Zero route behavior change; preserves dashboard quick actions, existing source contracts, bookmarks and strict protection. Fully reversible because it adds no redirect or deletion. | Duplicated private entry points remain; generic edit helper and dashboard quick actions are not one unified product story. |
| Redirect legacy writers to `/manage/*` | Replace each old writer with a compatible redirect and make workspace the single private owner. | Fewer URLs and a clearer future owner. | Current `/manage/dashboard` is not a source-proven equivalent editor for every blog/note writer; dashboard still links to legacy writers. Requires explicit mapping, browser flow proof, bookmark handling and a separately approved implementation task. |
| Create a new writer family | Introduce a new canonical editor route family, then migrate or redirect both existing groups. | Could give an intentionally designed long-term owner. | Scope expands into new routes, navigation, editor, auth and likely visual work; no requirement names a new route family or specifies product behavior. It cannot be chosen without a new product decision and approval. |

No option authorizes changing public URLs or weakening AuthGate/backend authorization. The first option is the only one fully supported by the current source without inventing an editor-equivalence claim.

## R4 — recommendation

Recommendation: **retain compatible coexistence and defer route implementation**. This is a G1 decision, not a product-routing change: public read routes stay public; `/manage/*` owns the private workspace; live legacy writers stay available and protected until a later route-specific implementation proves a complete replacement.

The separately gated cutover checklist is in `design.md`. It deliberately starts with evidence of functional equivalence, then moves one reversible route family at a time. No redirect, deletion, navigation rewrite, AuthGate change or API change is proposed for execution in this task.
