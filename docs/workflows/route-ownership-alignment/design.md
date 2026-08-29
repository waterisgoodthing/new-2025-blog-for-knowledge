# Design

Current source contains src/app/manage/(workspace) and legacy src/app/write, src/app/write-note, and src/app/write-mistake. The route group name is not a public URL contract.

This task first inventories actual paths, links, redirects, and public/private behavior. It then records one product decision: retain legacy routes, redirect them to a chosen owner, or introduce a new route family. Any implementation is deferred to a new approved task list after that decision.

## 2026-08-10 decision

Choose **compatible coexistence / deferral**. `/manage/*` is the private workspace owner; public read routes retain their existing owner; `/write*` and `/write-note*` remain compatibility-owned private writer routes. The existing `/mistakes/review` compatibility redirect to `/manage/review` remains the only source-proven redirect in this family.

This is deliberately not a claim that `/manage/dashboard` is a functionally equivalent editor for all legacy routes. A future cutover must first prove an editor-by-editor destination and preserve public routes and strict access boundaries.

## Separately gated future implementation list

Do not execute the following under this workflow or parent authorization:

1. Define the owner and equivalent destination for each legacy writer, including direct edit, save, preview, cancellation and bookmark behavior.
2. Add focused route/redirect tests and browser evidence for one route family at a time, including anonymous denial and authenticated success.
3. Implement one reversible redirect or navigation cutover with a documented rollback path; preserve the legacy page until validation passes.
4. Re-run public-route, AuthGate and backend permission regression tests; record browser evidence before considering the next family.
5. Only after every family is validated, decide whether legacy files may be deprecated in a separately approved cleanup task.
