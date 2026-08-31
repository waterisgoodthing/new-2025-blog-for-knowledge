# F4 输入包（已就绪，等待单独审批；禁止自行执行）

Status: `F4 INPUT READY FOR SEPARATE APPROVAL — FIX-01～05 COMPLETE; F4 NOT EXECUTED OR AUTHORIZED`.

This package is the current F4 input for `production-render-readiness-acceptance`. It does not authorize instrumentation, source changes, synthetic seeding, production build, browser performance sampling, deployment, Git, or any production Markdown migration. A future F4 run requires a separate explicit approval of that child workflow's task list after a fresh worktree/environment review.

## 1. Gate inputs

| Gate | Current evidence                                                                                                                                                                                     | F4 boundary                                                                                                                   |
| ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| G2   | Current isolated-scope `PASS`; historic totals are snapshots, and FIX-05 determines the final count.                                                                                                 | No production consumer is switched. F4 must not enable, invoke or use any PoC adapter as a production fallback.               |
| G3   | Current `PASS`; FIX-01 covers public detail and mobile nav. Historic totals are snapshots; FIX-05 determines final count.                                                                            | Public scenarios must not request strict `/api/auth/me` or administrator-only APIs; management stays strict.                  |
| G4   | `PASS / GO FOR F4 INPUT ONLY`: E1–E5 fields/save/preview/permission/reuse/rollback contract complete; Option A implementation list remains unapproved. Evidence: `editor-convergence/validation.md`. | Do not implement any editor primitive or remediate the legacy blog edit gate within F4. Carry residuals as observations only. |

Gate residuals carried forward:

Current evidence pointers: G2 is in `markdown-special-adapter-enablement/validation.md`; G3 is in `public-session-state-optimization/validation.md`; the future final command totals belong exclusively to FIX-05.

- Existing production Markdown renderer remains unchanged; the isolated PoC is not a production fallback or migration.
- Legacy `/write/[slug]` currently lacks a page-level `AuthGate`; its mutation endpoints remain protected and its remediation is a separately gated security task.
- Blog, note and standard mistake update-concurrency semantics currently differ; F4 must observe, not normalize them.

## 2. Frozen F4 scenario and data matrix

| Scenario                      | Dataset                                               | Browser/DOM success condition                                                                    | Required network/security checks                                                                        |
| ----------------------------- | ----------------------------------------------------- | ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------- |
| Anonymous list empty          | E0: no published visible notes                        | `/notes` reaches declared `empty` state and `notes:list-ready` mark                              | no strict `/api/auth/me`, no admin API noise, no hidden/draft leak                                      |
| Anonymous list full           | L20: 20 deterministic published visible notes/tags    | `/notes` has 20 visible records, `ready` state and mark                                          | same public-boundary checks; all required public API responses succeed                                  |
| Anonymous detail              | D1: one deterministic public normal-Markdown note     | detail content reaches `ready` state and `notes:detail-ready` mark                               | fixture excludes Mermaid/Markmap/Chart execution and all untrusted/personal content; no PoC adapter use |
| Administrator login/manage    | M30: 30 deterministic mixed note/blog/mistake records | normal password login reaches `manage:auth-submit`, then `manage:content-ready` and settled list | normal HttpOnly Cookie only; strict page and backend permission checks remain effective                 |
| Session boundary confirmation | M30 plus synthetic temporary admin session lifecycle  | logout/expired session rejects strict management and public reads remain readable                | no `AUTH_BYPASS`, no public admin API probes, preserve 401/403 semantics                                |

The implementation must create E0/L20/D1/M30 only in an isolated database at the current migration revision. Titles, slugs, tags, Markdown, images and credentials must be deterministic synthetic values; no real personal content, API, credential, or production account may be used.

## 3. Readiness and measurement contract

- The minimal selected owners must expose `data-render-state="loading|ready|empty|error"` on the main content region, and emit exactly one non-sensitive route-specific mark when a successful `ready` or `empty` state commits: `notes:list-ready`, `notes:detail-ready`, `manage:auth-submit`, `manage:content-ready`.
- Marks must not contain a slug, title, username, token, content, session identifier or any other personal value. Error states are separate and never count as successful readiness.
- Per valid sample record: navigation timing (TTFB, DOMContentLoaded, load), LCP when available, readiness mark timing, required API start/responseEnd/duration/status, DOM result, console/page errors, failed requests, navigation/dialog/download events, and failure reason.
- For each scenario collect at least 10 valid fresh-browser/server-warm samples. Keep server-cold and browser-warm samples distinct, retain every failed sample, and report raw values plus p50, p90, maximum and failure rate. Screenshots supplement but never replace timing/DOM/network evidence.

## 4. Isolation, configuration and cleanup contract

- Before execution record Node/npm/browser versions, current commit/worktree status, effective non-secret API host, migration revision, build mode, dataset profile and exact commands. Do not touch user dirty files.
- Proposed isolated bindings are frontend `127.0.0.1:3100`, backend `127.0.0.1:8100`, and isolated PostgreSQL `127.0.0.1:55432`; execution must first prove each is free and select new values rather than displacing a user process.
- Use a detached or otherwise isolated worktree and isolated build output/database. The production frontend may communicate only with the isolated backend at an explicitly verified local host; inability to do this without real API/DNS/CORS changes is `BLOCKED`, not a reason to use a production service.
- Temporary admin credentials must be generated at runtime, kept out of command output and repository files, and disabled/removed during cleanup. `AUTH_BYPASS` remains false and is never a validation path.
- Cleanup proof must show temporary account/session/credential removal, database cleanup, stopped processes, closed browser contexts, released ports, removed isolated worktree/build output, and preserved original dirty worktree.

## 5. Proposed F4 execution task sequence — separately approval-gated

1. PRA-01: reconfirm this scenario/data/metric contract against current source and environment.
2. PRA-02 → PRA-03: failing-first readiness-state/mark tests, then minimal implementation.
3. PRA-04: isolated build/database/synthetic data only after readiness tests pass.
4. PRA-05 → PRA-06: collect the public and management/browser matrices with raw artifacts.
5. PRA-07: calculate evidence-backed baseline/budget proposal; never call a historical target achieved automatically.
6. PRA-08: clean all temporary resources and verify cleanup before any closeout claim.

Each future task must update `production-render-readiness-acceptance/tasks.md`, `audit.md` and `validation.md` immediately with exact commands, counts, warnings, artifacts and residual risks. A failed isolation/readiness/data/cleanup precondition is `BLOCKED`; a performance shortfall becomes a separately approved optimization task, not an in-place rewrite.

## 6. Decision and prohibition

This is `F4 输入已就绪，可等待单独审批`, not F4 PASS, production readiness, or deployment approval. The required next human action is to review and separately approve the current F4 task list. Until then, no F4 work starts.
