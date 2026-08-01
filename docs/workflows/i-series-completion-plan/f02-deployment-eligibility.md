# F-02 Deployment Eligibility Review

Review date: 2026-08-01

Environment: local runtime authority `blog_v2:5432`, revision `025`; Legacy
`blog_db:5432`, revision `025`, read-only; isolated restore/acceptance databases removed
after verification.

Historical decision: `ELIGIBLE AT REVISION 024 (NOT DEPLOYED; PRODUCTION RUNTIME ENABLEMENT REQUIRED)`

Current decision (2026-08-01):
`TECHNICALLY ELIGIBLE FOR A SEPARATELY AUTHORIZED DEPLOYMENT / CURRENT DIRTY WORKTREE DO NOT DEPLOY`.
E-06、I11-04 和 post-cutover F-01 均已 PASS；但仓库的 exact-artifact
`predeploy:check` 要求 clean worktree，当前任务改动和既有用户改动使该门禁按设计
fail closed。不能提交、隐藏或回退用户改动来伪造可部署制品。

This is a quality and recoverability eligibility decision for a future separately authorized deployment. It does not authorize push, deployment, production configuration changes, database writes, or starting the production backend.

| Check | Status | Evidence |
|---|---|---|
| C1 owner manifest | PASS | Immutable revision-020 manifest covers 121 rows; current 024→020 projection has missing/extra/duplicate/hash/owner/orphan=0 and aggregate `b40b109a...89adb6`. |
| 020→025 schema authority | PASS | Historical 020→024 chain plus 025 head; live target and independent acceptance DB current=head=025 and `alembic check` clean. |
| Final integrity | PASS | I11 post-cleanup source/target 123/123, independent full-row hash match, immutable 121+2 owner manifest, seven relationship gates=0. |
| 024 backup / 025 recovery | PASS | Fresh 2026-08-01 DB and attachment backup 5/5 hashes, readable dump, isolated 024 restore then 025 upgrade, count/PK/hash/owner/relationship match; target removed. |
| E-05 shadow migration | PASS | 2026-07-31 isolated shadow reconciled 123/123 rows with one owner, zero orphans, idempotent replay, independent SQL, clean rollback/destruction, and unchanged source fingerprint. |
| E-06 switch/reverse delta | PASS | First switch, observation, forward delta/idempotency, reverse delta, actual rollback observation, final re-switch and Legacy read-only archive all recorded; runtime authority is `blog_v2`. |
| F-01 permissions/failure/browser/quality | PASS | Real admin/non-admin sessions with bypass false; anonymous/invalid 401, non-admin 403, admin 200; three requested viewports/keyboard; independent SQL cross-check. |
| Frontend suite | PASS | 23 files, 64/64 tests; TypeScript, Next production build and OpenNext Cloudflare build PASS, 40/40 pages generated. |
| Backend suite | PASS | 307/307 tests on isolated DB; compileall PASS; live and acceptance Alembic current=head=025/check clean. |
| Production dependency audit | PASS | `npm audit --omit=dev --audit-level=high` reports 0 vulnerabilities; Next/OpenNext dependency tree valid. |
| Exact clean-artifact predeploy wrapper | BLOCKED AS DESIGNED | `npm run predeploy:check` stops at `worktree is not clean`; current dirty state is preserved and is not promoted to a deployable artifact. |
| Local runtime authority | ENABLED LOCALLY | Existing `com.blog.backend` is healthy on 127.0.0.1:8000 and connected only to `blog_v2`; this is the approved authority switch, not a new application deployment. |
| Actual deployment | NOT DEPLOYED | No push, deploy, production config modification, or production listener was performed. |

## Conditions Before Any Future Deployment

1. Obtain separate authorization for push/deployment and production configuration.
2. Form an intentionally reviewed clean commit without sweeping unrelated user changes,
   then rerun the repository `predeploy:check` against that exact commit; create a fresh
   pre-deployment backup if deployment occurs after this dated recovery point.
3. Configure secrets, non-wildcard CORS, registration policy, and production `AUTH_BYPASS=false`; fail startup if bypass flags are both true.
4. Start and health-check the production backend before routing traffic; preserve rollback ownership and the validated C5/C7 recovery contract.
5. Reassess unrelated dirty worktree content so deployment scope is reproducible and does not include user work outside this closure.

Historical conclusion: the revision-024 artifact was `ELIGIBLE`. Current revision-025
technical/recovery candidate is also eligible for a future separately authorized deployment,
but the exact dirty worktree is `DO NOT DEPLOY` until a clean reproducible artifact passes the
wrapper gate. Actual application deployment and Git push remain `NOT DEPLOYED / NOT PERFORMED`.
