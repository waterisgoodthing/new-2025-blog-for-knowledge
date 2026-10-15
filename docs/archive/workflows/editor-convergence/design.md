# Design

The current note editor has toolbar, preview, slash command, and AI-assistant modules. Blog and mistake editors have different workflows and data requirements. Convergence starts from a capability matrix, not from a forced component merger.

The output must identify reusable primitives, type-specific fields, save/preview contracts, and private-route access requirements. Only a later approved implementation task may extract a shared primitive or introduce a new editor owner.

## E4 implementation-direction comparison (evidence only)

### Option A — minimal shared primitives with domain-editor coexistence (recommended)

Keep `/write*`, `/write-note*` and `/write-mistake*` as their present owners. A later separately approved implementation task may extract only the E2-supported primitives behind explicit per-domain adapters:

- typed Note mutation payload assembly boundaries, without changing current `expected_revision` behavior;
- tag normalization/empty-tag suggestion and save pending/error/success support;
- a blog/note-only Markdown selection/insert/wrap utility, with each route retaining its toolbar, slash, preview and image semantics.

Mistake remains a structured editor with first-class fields, review attributes, evidence images and protected AI stages. Blog/note preview owners remain separate and continue to use their current renderer until a separately authorized Markdown migration. The implementation rollback is import-level: remove a new primitive/adaptor and restore each existing local owner; no schema, data, route or preview migration is involved.

### Option B — larger unified editor owner

Introduce a new polymorphic owner capable of dispatching blog, note and mistake forms, preview modes, asset flows, AI behaviors, revision handling and route gates. This is not currently evidence-ready: legacy blog uses Zustand/file placeholders, note uses local hooks/toolbar/slash/version flow, and mistake has structured AI/review semantics. It would require a new approved design, integration tests for all three editors, a separate page-level access remediation decision for legacy `/write/[slug]`, and an explicit migration/rollback plan before any source extraction.

### Current decision boundary

E1–E3 support Option A only as a future **implementation direction**, not as implementation authorization. Option B is documented for comparison and remains high-risk/unsupported. D2 must select one direction before E5 can create a separately approvable task list. Neither option permits schema changes, route moves, renderer cutover, permission relaxation, AI/upload/review changes, production Markdown migration, visual redesign, Git or deployment in this workflow.
