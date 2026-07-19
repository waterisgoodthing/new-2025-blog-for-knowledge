# Tasks: Phase 1.0 Productization

> Status: **Phase 0 COMPLETE; Phase 0.5 COMPLETE / PASS.**
>
> 本任务清单创建不代表实施授权。Phase 0 与 Phase 0.5 已完成；Phase 1.0A、1.0B、RC 和 1.0C 仍需要后续独立 Gate 与明确批准。

## Gate 0 — Baseline Freeze

### P0-01 Current Git and architecture baseline

- [x] **P0-01**
- 任务名称：记录当前 Git、工作树与双架构线基线。
- 优先级：P0。
- 来源需求：REQ-P10-001。
- 涉及文件：只读检查仓库；更新本 workflow `audit.md`、`validation.md`。
- 修改内容：记录 branch、HEAD、完整 `git status --short`、公开/管理路由、现有 workflow 与架构边界。
- 完成标准：不把已有未跟踪评估文档误称为本阶段变更；明确 `src/` 与 `backend/` 两条架构线。
- 验证方式：Git 命令、`rg --files`、route inventory。
- 风险说明：工作树已有用户文件；不得 reset、删除或批量格式化。

### P0-02 Current database and storage baseline

- [x] **P0-02** — `PARTIAL`: revision/count/storage evidence complete; `alembic check` recorded metadata drift.
- 任务名称：读取当前 revision、schema、counts 和附件存储状态。
- 优先级：P0。
- 来源需求：REQ-P10-001、REQ-P10-008。
- 涉及文件：数据库与 attachment root 只读；更新 `audit.md`、`validation.md`。
- 修改内容：运行 `alembic current/heads/history/check`、核心表只读 counts/抽样、附件 manifest/checksum 摘要。
- 完成标准：记录当前 revision 与历史 revision 018 backup 证据差异；无 DDL/DML/migration。
- 验证方式：`PYTHONPATH=. .venv/bin/alembic ...`、只读 SQL、文件只读 hash/manifest。
- 风险说明：不得输出 secret、绝对内部 storage 路径或私人附件内容。

### P0-03 Current UI screenshots and Demo baseline

- [x] **P0-03** — `PARTIAL / BLOCKED`: failure screenshots saved; Next.js chunks return 500; no real admin session.
- 任务名称：保存当前公开与管理入口 UI 基线。
- 优先级：P0。
- 来源需求：REQ-P10-001、REQ-P10-003、REQ-P10-004。
- 涉及文件：`assets/`、`docs/releases/v1.0-baseline.md`、`validation.md`。
- 修改内容：采集桌面/移动首页、Blog、Notes、Mistakes、Manage 登录页；有真实管理员会话时采集 Dashboard/Questions/Mistakes/Review/Attachments。
- 完成标准：截图带页面、viewport、时间和登录状态说明；无法登录的管理页标 `BLOCKED`。
- 验证方式：真实浏览器 DOM + screenshot；不使用 `AUTH_BYPASS`。
- 风险说明：截图不得包含密码、token、私有附件或敏感 AI input。

### P0-04 Known issue and deferred-capability reconciliation

- [x] **P0-04** — `PASS`: issue history and active/partial/deferred capability states reconciled.
- 任务名称：统一当前 issue 与延期能力状态。
- 优先级：P0。
- 来源需求：REQ-P10-001、REQ-P10-007、REQ-P10-010。
- 涉及文件：既有 acceptance/issues/risks 只读；更新本 workflow `audit.md`、`risks.md`。
- 修改内容：确认 LT-ISSUE-002 当前为历史已修复待回归；区分 AI infrastructure、AI product expansion、Capture、真实 OCR、BKT、Analytics。
- 完成标准：没有同一问题同时显示 open/fixed 的无解释冲突；UNKNOWN 保持 UNKNOWN。
- 验证方式：源码、当前定向测试清单、既有 workflow 状态交叉核对。
- 风险说明：不得因为文档写“已修复”就跳过当前回归要求。

### P0-05 Publish v1.0 baseline and Phase 0 validation

- [x] **P0-05** — `PASS`: canonical baseline published; Phase 0 overall result is `PARTIAL / CONDITIONAL`.
- 任务名称：生成并审查 v1.0 baseline。
- 优先级：P0。
- 来源需求：REQ-P10-001。
- 涉及文件：`docs/releases/v1.0-baseline.md`、本 workflow README/audit/risks/validation/tasks。
- 修改内容：汇总 P0-01 至 P0-04 的证据，给出 Phase 0 pass/partial/fail 和 Gate A/B 建议。
- 完成标准：报告含 commit、revision、counts、核心流程、已知问题、截图索引、Demo、延期项、证据限制。
- 验证方式：链接检查、`git diff --check`、范围检查；本任务完成后立即勾选。
- 风险说明：Phase 0 完成不自动授权 Phase 1.0A/B。

## Gate 0.5 — Runtime Recovery

> APPROVED：P05-01 至 P05-05 已于 2026-07-17 明确批准。必须完整 PASS，PARTIAL 不解除后续 runtime blocker。

### P05-01 Frontend Runtime Audit

- [x] **P05-01** — `PASS`: confirmed stale Next 16.0.10 runtime vs current 16.2.10 build-output mismatch.
- 任务名称：审计当前 frontend process、generated chunks 与失败层级。
- 优先级：P0。
- 来源需求：REQ-P05-001；RISK-P10-009。
- 涉及文件：运行环境只读；更新本 workflow `audit.md`、`validation.md`。
- 修改内容：记录 process/port/cwd/command/version/build/cache/env-presence；复现 document 200 + chunk 500；给出根因与最小恢复路径。
- 完成标准：确认进程归属并区分 stale runtime/cache、build mismatch、asset failure、source/config defect。
- 验证方式：`lsof`、`ps`、`pwdx/lsof cwd`、package metadata、HTTP/network evidence；不输出 secret。
- 风险说明：本任务不得停止进程、移动 `.next` 或编辑代码。

### P05-02 Clean Build Recovery

- [x] **P05-02** — `PASS`: clean Next 16.2.10 build and recovered production runtime; 16/16 initial chunks returned 200.
- 任务名称：隔离旧 generated output 并恢复干净 frontend runtime。
- 优先级：P0。
- 来源需求：REQ-P05-002。
- 涉及文件：仅已确认项目进程与 generated `.next`；更新本 workflow evidence。
- 修改内容：停止已确认的项目 frontend process；将 `.next` 移入 timestamped quarantine；使用权威 package manager 执行 clean production build，并启动新构建。
- 完成标准：production build exit 0；runtime 稳定监听；target document 与首次 JS/CSS 不再 500。
- 验证方式：build output/exit code、process/port、startup output、direct HTTP status 与 chunk probes。
- 风险说明：若需要 source/config/dependency/lockfile 修改，立即停止并请求新批准。

### P05-03 Browser Verification

- [x] **P05-03** — `PASS`: 5 routes × 2 viewports rendered and hydrated; interactive React state change succeeded; browser console errors were 0.
- 任务名称：桌面与移动浏览器验证 document/chunks/hydration/console。
- 优先级：P0。
- 来源需求：REQ-P05-003。
- 涉及文件：workflow `assets/` screenshots 与 validation evidence。
- 修改内容：匿名验证 `/`、`/blog`、`/notes`、`/mistakes`、`/manage`，viewport 为 1280×720 与 390×844。
- 完成标准：documents/JS/CSS 200；hydration success；每页 console error 为 0；无 blank/永久 loading。
- 验证方式：真实浏览器 DOM、network、console、screenshots；不 mock、不 bypass。
- 风险说明：任何页面失败均阻塞 Gate，不用其他页面通过替代。

### P05-04 Asset Loading Validation

- [x] **P05-04** — `PASS`: all referenced first-party JS/CSS and critical image/icon/manifest/optimizer assets returned 200; 0 broken DOM images.
- 任务名称：验证目标页面第一方静态与优化图片资源。
- 优先级：P0。
- 来源需求：REQ-P05-004。
- 涉及文件：workflow asset manifest/validation；不修改 public assets。
- 修改内容：检查 favicon、avatar、cursor、route imagery、Next optimizer 与实际页面资源请求。
- 完成标准：critical first-party assets 为 200 或有效 304；无 broken image；第三方失败单列。
- 验证方式：browser network、direct HTTP/content-type probes、visual screenshots。
- 风险说明：不得为通过验收隐藏请求、关闭优化或替换为 mock asset。

### P05-05 Environment Closure

- [x] **P05-05** — `PASS`: runtime, health, database, revision, Git scope, evidence and session closure all passed; Runtime Recovery Gate closed.
- 任务名称：完成环境前后对比并签发 Runtime Recovery Gate 结论。
- 优先级：P0。
- 来源需求：REQ-P05-005。
- 涉及文件：本 workflow README/audit/risks/validation/tasks、`docs/releases/v1.0-baseline.md`。
- 修改内容：复核 Git scope、process/port、backend health、database counts、Alembic revision、browser/asset evidence；关闭临时 session；记录 quarantine。
- 完成标准：database unchanged；migration 仍为 `020 (head)`；五项 acceptance 全 PASS 后才解除 RISK-P10-009 blocker。
- 验证方式：before/after read-only SQL、Alembic current、status/diff、browser evidence link check。
- 风险说明：PARTIAL/UNKNOWN/FAIL 均不得解锁后续工作；Gate PASS 不等于 A/B 实施授权。

## Gate A — Phase 1.0A UI/Product Polish

> NOT AUTHORIZED：Phase 0.5 已完整 PASS；等待明确批准 Gate A tasks。

- [x] **A-P0-01** — `PASS`: 移动首页立即显示公开导航；仅在管理员会话确认后追加管理入口，定向行为测试 2/2 通过。
- [x] **A-P0-02** — `PASS`: 现有列表 API 无 totals 且 review records 为逐 item 合同；已冻结 admin-only `GET /api/admin/dashboard/summary` 单快照合同。
- [x] **A-P0-03** — `PASS`: 新增 admin-only summary API 与真实学习管理首页；删除 static-shell 文案，无 mock、schema 或 migration。
- [x] **A-P0-04** — `PASS`: 桌面/移动导航按学习闭环重组，补齐草稿与采集，并将搜索/分析/任务降级到“后续能力”。
- [x] **A-P0-05** — `PASS`: Drafts 定为 active；Capture、AI/AI Runs、Search、Analytics、Jobs 定为 deferred；路由保留且 UI 明确标注“后续”。
- [x] **A-P1-01** — `PASS`: 引入受控 `FeatureState`，明确区分 loading skeleton、empty、error/retry 与 deferred。
- [x] **A-P1-02** — `PASS`: Dashboard、Drafts、Questions、Mistakes、Review、Attachments 与 deferred 页面统一使用 `FeatureState`。
- [x] **A-P1-03** — `PASS`: 管理端核心标题、状态、题型、难度、附件术语和日期统一为中文展示；API enum、schema 与 migration 未改。
- [x] **A-P0-06** — `PASS`: production build、前后端全量测试、桌面/390px 真实浏览器、权限噪音、JS/CSS、Alembic 与数据库恢复基线全部通过。

## Gate B — Phase 1.0B Production Hardening

> AUTHORIZED on 2026-07-19：用户已明确批准 B-P0-01 至 B-P0-06、B-P1-01 至 B-P1-02。RC 与 Gate C 仍未授权。

- [x] **B-P0-01** — `PASS`: 匿名、有效管理员、撤销、过期、禁用账号与公开读取矩阵通过；临时记录清理后 counts 不变。
- [x] **B-P0-02** — `NOT REQUIRED / PASS`: LT-ISSUE-002 未复现；按条件任务不修改 Auth 代码。
- [x] **B-P0-03** — `PASS`: 已为 revision `020` 生成 custom-format PostgreSQL backup，`pg_restore --list` 与 SHA-256 校验通过；来源 DB 未写入。
- [x] **B-P0-04** — `PASS`: 已生成 Attachment manifest、archive 与双重 SHA-256；1 条有效数据库附件的路径、大小和内容 checksum 全部匹配。
- [x] **B-P0-05** — `PASS`: custom DB archive 与附件 archive 已在隔离 PostgreSQL/临时 storage 成功恢复；revision、counts、文件 checksum、应用启动、Health 和公开读取通过，源库快照不变。
- [x] **B-P1-01** — `PASS`: 现状仅有公开 DB health 与 Dashboard 静态 system 字段，缺少 Auth 诊断和统一安全异常上下文；已冻结公开轻量 health、admin-only diagnostics、request ID 与脱敏错误日志边界。
- [x] **B-P1-02** — `PASS`: 已实现轻量公开 Health、admin-only DB/Storage/Auth diagnostics、服务端 request ID 与脱敏未处理异常日志；7/7 定向测试及真实运行时权限/诊断通过。
- [x] **B-P0-06** — `CONDITIONAL PASS`: Auth、revision 020 backup/isolated restore、附件完整性、Health/diagnostics、全量测试、TSC/build 与运行时通过；恢复手册已建立。`RISK-P10-008` schema metadata drift 仍阻断 Production Ready。

## Schema Authority Gate — RISK-P10-008

> SA-A DECIDED; SA-P0-01 and SA-P0-02 COMPLETE. `current`/`heads` remain `020 (head)` and `alembic check` now passes without upgrade operations. SA-P0-03 is evaluated separately because SA-A metadata alignment required no DDL/migration.

- [x] **SA-P0-01** — `PASS`: 用户于 2026-07-19 选择并批准 SA-A；只读 preflight 已确认现有三个 query indexes 与 root/child、`lower(name)` partial unique semantics，且 root/child duplicate groups 均为 0。requirements/design/compatibility matrix 已更新；未执行 DDL、migration 或数据写入。
- [x] **SA-P0-02** — `PASS`: test-first aligned `KnowledgePoint` lifecycle metadata with SA-A (three query indexes plus root/child case-insensitive partial unique indexes) and aligned create/update conflict prechecks. RED tests reproduced the prior database-integrity leak; 10 taxonomy tests pass after the minimal source change. `current`/`heads` remain `020 (head)`, `alembic check` reports no upgrade operations, guest lifecycle exclusions remain absent, and the knowledge-point count remains `3`. No DDL/migration/DML executed.
- [x] **SA-P0-03** — `NOT REQUIRED / PASS`: SA-A closed by lifecycle metadata and service-precheck alignment only. Revision remains `020`; no physical schema, recovery boundary, SQL or data impact changed; `alembic check` has no upgrade operations. Therefore no migration/DDL plan, backup refresh or isolated restore is required for this task.
- [x] **SA-P0-04** — `PASS`: final source-only closure recorded. HEAD remains `939ad1fa`; source hashes are archived in validation; `current`/`heads` are `020 (head)`, `check` has no upgrade operations, and read-only core counts are `1/3/6/3/3/3/1` (subjects/knowledge-points/links/questions/mistakes/review-items/attachments). Recovery boundary did not change, so Gate B's revision-020 isolated restore remains applicable. `RISK-P10-008` is resolved.

## RC Gate — v1.0 Acceptance

> AUTHORIZED by the user's 2026-07-19 all-content approval. Schema Authority Gate is PASS. RC execution remains sequential; RC does not make Gate C complete without its own design/implementation evidence.

- [x] **RC-P0-01** — `NOT REQUIRED / PASS`: SA-A did not change physical schema, revision or recovery boundary. Rechecked `current`/`heads` `020 (head)` and `check` PASS; Gate B's revision-020 DB + attachment backup and isolated restore evidence therefore remains valid. No backup/restore ran and no source database/storage was touched.
- [x] **RC-P0-02** — `PASS`: same-site local frontend → FastAPI → real administrator-session → PostgreSQL/Attachment Storage path was verified without `AUTH_BYPASS`. Public reads, Dashboard, Health, diagnostics, Questions, Mistakes, Review and Attachments returned the expected real responses; a temporary Question → Mistake → Review write/read loop passed over HTTP. All temporary identities and learning records were deleted by exact IDs and core counts returned to baseline.
- [x] **RC-P0-03** — `PASS`: frontend 39/39, backend 256/256 (2 known AsyncMock warnings), `npx tsc --noEmit`, `npm run build` (40/40 static pages), `git diff --check`, and Alembic `020 (head)` current/heads/check all passed. Validation-owned AI/recommendation rows were precisely removed; final AI counts returned to `29/44/27` and RC fixture users/sessions are `0/0`.
- [x] **RC-P0-04** — `PASS`: real desktop and 390px browser evidence confirms document and 23 first-party JS/CSS resources return 200, client interaction/hydration succeeds, page errors are zero, public reads stay public, and administrator routes require a real session. Sanitized anonymous screenshots and request summaries are archived.
- [x] **RC-P0-05** — `PASS`: scoped review found the SA-A model, service and tests consistent with the approved physical contract; no additional defect or out-of-scope refactor was justified. `git diff --check` passed after all RC evidence updates.
- [x] **RC-P0-06** — `PASS`: final warnings, deferred items, fixture cleanup and Ready boundaries are archived. RC is COMPLETE / PASS: schema authority, recovery applicability, full command suite, runtime/API/browser evidence and scoped code quality are all closed. This enables the separately scoped Gate C design task, not automatic Gate C feature implementation.

## Gate C — Learning Feedback

> RC PASS 已达成。用户 2026-07-19 的“批准所有内容直至目标完成”授权适用于下列已冻结的无 schema 最小范围；它不授权 DDL/migration、Analytics Lite、BKT、推荐、多用户、AI 扩展、部署或推送。

- [x] **C-P0-01** — `PASS`: 冻结管理员“下一步做什么”的确定性反馈合同：仅从既有 Dashboard counts 派生，优先级为到期复习、错题、题目、空状态；无正文读取、AI、持久化或新 API/schema。
- [x] **C-P0-02** — `PASS`: `requirements.md` 与 `design.md` 已记录精确输入/输出、权限、数据来源、保留策略、UI/API 合同、四分支验收和 `NO schema` 决定；本 task list 即为获批实施范围。
- [x] **C-P1-01** — `PASS`: test-first implemented the Dashboard learning-feedback card and pure four-branch derivation. It reuses only existing protected summary counts, adds no API/schema/persistence/AI behavior, and routes to existing management surfaces. RED then GREEN evidence and targeted 5/5 tests are archived.
- [x] **C-P1-02** — `NOT REQUIRED / PASS`: 已冻结 `NO schema`；不需要 backup/restore、revision/rollback 或 migration/DDL。
- [x] **C-P1-03** — `PASS`: anonymous redirect and real-admin Dashboard feedback/action were browser-verified without bypass; full frontend 43/43, backend 256/256, TypeScript, build, Alembic and diff checks pass. The one validation-owned AI run/log created by the shared backend suite was deleted by exact ID; final counts and zero RC fixtures were rechecked.

## Security Follow-up — Production Startup Guard

> AUTHORIZED：用户于 2026-07-19 明确要求“直接启动修改程序并备注在原 workflow”。只修改生产启动安全拒绝逻辑与对应测试；不授权 DDL/migration、部署、生产数据、公开权限或 AUTH_BYPASS 使用。

- [x] **SEC-P0-01** — `PASS`: requirements/design 已冻结三项 production startup 拒绝条件、非生产兼容语义、`RuntimeError` 失败边界和无 secret 输出要求。
- [x] **SEC-P1-01** — `PASS`: test-first added production double-bypass rejection, JWT/CORS `RuntimeError`, and non-production compatibility coverage. The new bypass test was RED before implementation; JWT/CORS tests were RED while `SystemExit` remained.
- [x] **SEC-P1-02** — `PASS`: minimal lifespan change now rejects double bypass before readiness and raises `RuntimeError` for all three production-insecure configurations. Diagnostics/auth-router semantics and non-production behavior remain unchanged.
- [x] **SEC-P1-03** — `PASS`: targeted monitoring/startup suite 11/11 and full backend suite 260/260 passed; Alembic `020 (head)` current/heads/check and diff hygiene pass. The validation-owned AI run/log from full pytest were deleted by exact ID; final AI counts returned to `29/44/27`.

## Release Safety Follow-up — RISK-P10-011 and Pre-deploy Gate

> APPROVED AND EXECUTED: REL-P1-01 至 REL-P1-05 已获用户批准并完成。没有部署、push、生产访问、生产配置读取、DDL/migration 或非测试数据删除。

- [x] **REL-P0-01** — `PASS`: read-only preflight confirmed the public GET → AI/write path, the management regenerate dependency, public history exposure, and the current frontend-only/clean-worktree predeploy limitation.
- [x] **REL-P1-01** — `PASS`: test-first route contract now covers public existing/missing reads, admin-only explicit generation, admin-only history, and history DTO raw-context exclusion; 6/6 targeted tests pass.
- [x] **REL-P1-02** — `PASS`: public GET is read-only, `POST /today/generate` is admin-only, history is admin-only and no longer returns raw context. The public share card keeps its existing missing-result fallback; management regenerate now uses the explicit mutation. No schema/migration change.
- [x] **REL-P1-03** — `PASS`: predeploy checker now requires different isolated-test and target database variables before backend pytest/Alembic checks; syntax passes. Current actual invocation correctly stops at the existing dirty-worktree gate, with no cleanup or external/database action.
- [x] **REL-P1-04** — `COMPLETE / FINDINGS RECORDED`: source/template review confirms startup JWT/CORS/bypass hard blocks and recommendation boundary remediation, but identifies production-deployment blockers: default registration remains enabled unless configured otherwise, and full Cloudflare invocation sampling needs an explicit privacy/retention decision. No credential or production system was accessed.
- [x] **REL-P1-05** — `COMPLETE / DEPLOYMENT BLOCKED`: frontend 43/43、backend 266/266、TypeScript、production build、Alembic `020 (head)` current/heads/check 与 diff hygiene 均通过；测试副作用按精确 ID 清理，AI counts 回到 `29/44/27`。未运行真实 target-DB gate 或部署：工作树保持 dirty，且 `RISK-P10-015` 的生产注册与 Cloudflare 日志政策尚未决定；无生产访问/部署授权。

## Deployment Readiness and Authorized Release — RISK-P10-014 / RISK-P10-015

> PLANNED / AWAITING APPROVAL: these tasks prepare a deployment decision. They do **not** authorize staging, commit, push, deployment, production access, credentials/configuration reads, DDL/migration, restore, or destructive cleanup. Execute exactly one approved item at a time and update this list immediately.

- [x] **DEP-P0-01** — `COMPLETE / BLOCKED FOR RELEASE ARTIFACT`: read-only inventory confirms HEAD `939ad1f` is the last committed baseline while the current branch contains a mixed dirty worktree of modified and untracked backend, frontend, tests and workflow files. No exact publish file set or release commit has been approved. Strategy is therefore an isolated clean worktree based on a future approved commit; no staging, commit, cleanup, target access or deployment occurred. `DEP-P1-01` remains blocked until the user approves the exact release file set and commit.
- [ ] **DEP-P0-02** Obtain and record the two required production policy decisions: registration posture, and Cloudflare invocation-log sampling/retention posture. If either remains undecided, mark deployment blocked; do not infer safe values or edit production configuration.
- [ ] **DEP-P0-03** Establish secret-safe target authorization and recovery preflight. Confirm which frontend and/or backend targets are in scope, the authorized target database boundary, applicable backup/release identities and rollback owner. No target connection, production read, migration, DDL, restore or deployment in this planning item.
- [x] **DEP-P1-01** — `PASS`: after the user's explicit “only push this round” authorization, the exact v1.0 productization/release-safety path set was staged and cached-reviewed; unrelated `docs/project-assessment/` and `docs/workflows/mvp-goal-gap-analysis/` remained unstaged. Commit `57915a8` is the release artifact, and a temporary detached worktree at that commit was verified clean then removed. Push is authorized by the same user instruction and follows this evidence update; no predeploy, target access or deployment is implied.
- [ ] **DEP-P1-02** Run the fail-closed predeploy matrix in the approved clean scope after separate authorization for the isolated test database and target-database Alembic checks. Record only sanitized pass/fail, revision and release identity; stop on any failure.
- [ ] **DEP-P1-03** Deploy the explicitly approved frontend and/or backend target after a separate deployment authorization. Record platform release identity and rollback point; do not infer authorization for the other runtime boundary.
- [ ] **DEP-P1-04** Run post-deploy public/admin smoke and resource checks without `AUTH_BYPASS`; verify frontend document/JS/CSS/hydration/console, Health, public read, protected write boundary, Attachment read and diagnostics. Stop and request direction on any failure.
- [ ] **DEP-P1-05** Issue an explicit Demo Ready / Personal Use Ready / Production Ready verdict, list warnings/deferred items, and record either acceptance or an authorized rollback outcome.
