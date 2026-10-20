# Tasks

Status: `COMPLETE — D2 OPTION A; E1～E5 COMPLETE; G4 PASS; F4 INPUT MAY BE ASSEMBLED IN PARENT`

- [x] E1. Inventory current editor pages, components, save paths, preview renderers, and page/backend access boundaries.
- [x] E2. Produce a capability matrix and identify only evidence-backed common primitives.
- [x] E3. Record domain-specific fields and public/private access constraints.
- [x] E4. Design a minimal extraction or coexistence option with rollback and validation.
- [x] D2. User selected Option A on 2026-08-16: minimal shared primitives with domain-editor coexistence.
- [x] E5. Produce a separately gated implementation task list; do not implement it.

## G4

- [x] Status: `PASS — F4 INPUT ONLY` (2026-08-16)
- Contract conclusion: E1–E3 source evidence covers all current fields, save paths, preview owners and public/private/backend boundaries; E4 compares coexistence/rollback options; D2 selected Option A; E5 creates a separately approval-gated implementation list.
- Preserved boundaries: first-class mistake/review fields; separate route/component owners; divergent `expected_revision` semantics; existing preview/renderer owners; strict AuthGate and backend `get_current_admin`; protected AI/upload/review; public Note filters.
- Residual risks: current `/write/[slug]` lacks page-level AuthGate although mutation endpoints remain protected; legacy and standard update-concurrency modes differ; production Markdown renderer is not migrated. These are recorded and assigned, not fixed or hidden.
- Gate scope: PASS allows only the parent F4 input package to be assembled. It does not authorize the unapproved E5 list, any source extraction, security remediation, route/schema/renderer migration, F4 execution, Git or deployment.

E1 result: current source inventory is in `audit.md` and exact read-only commands/results are in `validation.md`. It identifies the separate legacy-blog Zustand workflow, note editor hooks/tooling, staged mistake create flow, standard mistake edit form, common typed Note API, preview owners, and access evidence. No editor source, schema, route, API contract, Markdown renderer, or visual behavior changed.

E2 result: `audit.md` now separates supported common primitive candidates from non-common behavior. The shared candidates are deliberately limited to typed save mutation boundary, metadata/tag normalization, save-state feedback, and a future Markdown selection/insert core for blog/note only. It does not decide a shared UI, preview, AI, image or mistake editor. E3 is the only next item.

E3 result: `audit.md` freezes the field, save, preview and permission matrices. First-class mistake/review fields, AI metadata and protected routes remain domain-owned; different revision semantics and the legacy `/write/[slug]` page-level gap are explicit constraints, not normalization work. E4 is the only next item.

E4 result: `design.md` compares Option A (minimal shared primitives with domain-editor coexistence) and Option B (larger unified owner). Current evidence supports only Option A as a later implementation direction; Option B is high-risk and requires a new design/integration/migration decision. E5 and G4 are blocked until the user makes D2; no implementation has occurred.

D2 result: the user selected Option A. This approves E5 documentation only: it does not approve any extraction, route/AuthGate correction, schema/API/renderer change, test-source change, visual work, Git or deployment. E5 is the only next item.

E5 result: `implementation-tasks.md` contains the separate, non-approved Option A implementation list. It requires a fresh explicit approval before any future checkbox, starts with characterization tests, confines extraction to blog/note helpers, excludes mistake flattening and assigns the legacy `/write/[slug]` gate gap to separate security scope. G4 is the only next item.

G4 result: PASS for F4 input only. The editor contract is complete and has a scoped, separately approved future implementation path; its documented residuals remain open and do not claim an editor migration or permission remediation.
