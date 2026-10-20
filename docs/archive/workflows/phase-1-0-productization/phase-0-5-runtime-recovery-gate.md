# Phase 0.5 Runtime Recovery Gate

> Status: **COMPLETE / PASS — P05-01 through P05-05 closed on 2026-07-17**

## Goal

恢复并证明当前本地 Next.js 运行环境可稳定提供页面文档、生成的 JavaScript/CSS、React hydration 与第一方静态资源，从而解除 Phase 1.0A/B 的 frontend-runtime blocker。

本 Gate 通过只代表“后续工作具备可运行和可验收的前端基线”，不自动授权 Phase 1.0A、Phase 1.0B、RC 或 Phase 1.0C。

## Source

- Phase 0 baseline: `docs/releases/v1.0-baseline.md`。
- Residual risk: `RISK-P10-009 Current local frontend chunks return HTTP 500`。
- Current symptom: route documents return 200, while generated `_next` CSS/JavaScript chunks and optimized avatar requests return 500; pages remain blank or loading.

## Scope

### P05-01 Frontend Runtime Audit

- Identify the process listening on the frontend port, its working directory, command, parent process and start context.
- Record Node/npm/Next versions, package-manager authority, current build ID/cache state and safe environment-variable presence without printing secrets.
- Reproduce one document/chunk failure and determine whether it is stale process/cache, build-output mismatch, missing asset or source/config defect.
- Remain read-only. No process termination, generated-cache move or source edit in this task.

### P05-02 Clean Build Recovery

- Stop only the confirmed project frontend process when needed; do not terminate unrelated Node processes.
- Quarantine the generated `.next` directory with a timestamp instead of deleting it immediately.
- Run the repository's clean production build with the authoritative package manager and require exit code 0.
- Start the newly built local frontend runtime on the agreed local port for verification.
- If recovery requires source, dependency, lockfile or configuration changes, stop and request a scope amendment before editing.

### P05-03 Browser Verification

- Use a fresh anonymous browser session at desktop `1280×720` and mobile `390×844`.
- Verify `/`, `/blog`, `/notes`, `/mistakes`, and `/manage`.
- Record document, JavaScript and CSS status; hydration result; console errors; visible loading/blank states; screenshots.
- Do not use `AUTH_BYPASS`, saved administrator credentials or network mocks.

### P05-04 Asset Loading Validation

- Validate first-party favicon, avatar, cursor, route imagery and Next image-optimizer requests exercised by the target routes.
- Require no critical first-party asset 4xx/5xx responses.
- Record third-party font/analytics failures separately; do not weaken first-party acceptance because of external services.

### P05-05 Environment Closure

- Recheck Git/worktree scope, frontend process/port, backend health, database revision and core counts.
- Confirm temporary browser sessions are closed and quarantined generated artifacts are documented.
- Update this workflow's audit, validation, risks, tasks and `docs/releases/v1.0-baseline.md` with recovery evidence.
- Issue a strict PASS/FAIL decision for the Runtime Recovery Gate.

## Acceptance Matrix

| Layer | Required result |
|---|---|
| Next.js documents | Target route documents return HTTP 200 |
| Clean build | Repository production build exits 0 from quarantined generated state |
| JavaScript | Every first-party JS chunk requested by target routes returns HTTP 200 |
| CSS | Every first-party stylesheet requested by target routes returns HTTP 200 |
| Hydration | React hydration completes; rendered content is interactive and not stuck blank/loading |
| Browser console | Zero console errors on every target route at both required viewports |
| First-party assets | Critical first-party image/icon/font/optimizer requests return HTTP 200 or valid 304 |
| Database | Core baseline counts remain unchanged |
| Migration | Alembic remains exactly `020 (head)` before and after |
| Security | No `AUTH_BYPASS`, credential exposure or admin-session fabrication |
| Scope | No unapproved source/config/dependency/lockfile changes |

## Gate Decision Rule

- `PASS`: every acceptance row passes with recorded evidence. `RISK-P10-009` becomes resolved and the runtime blocker on Phase 1.0A/B is removed.
- `FAIL`: any document/chunk/CSS/hydration/console/asset/database/revision condition fails. The blocker remains and the failure moves into residual risks.
- `PARTIAL` is not sufficient to unlock subsequent work.

## Final Decision

`PASS`. All acceptance rows were proved against the recovered local production runtime. `RISK-P10-009` is resolved and the frontend-runtime prerequisite is removed. This does not authorize Phase 1.0A, Phase 1.0B, RC or Phase 1.0C.

## Explicit Non-goals

- Dashboard, navigation, state component or product-language implementation.
- Auth behavior changes or administrator-session creation.
- Alembic metadata-drift remediation, migration creation or schema changes.
- Dependency upgrades, lockfile normalization or package-manager migration.
- AI, OCR, Capture, Analytics, BKT or learning-product expansion.
- Production deployment or public-site release.
