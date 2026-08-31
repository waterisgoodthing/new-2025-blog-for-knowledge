# Tasks

## Approval State

Status: `CURRENT RUN PARTIAL — PRA-04 PASS; PRA-05 PASS_WITH_NOTES; PRA-06 PASS; PRA-07 PASS_WITH_NOTES; PRA-08 PASS; no deployment or production change authorization`

The user separately and explicitly approved exactly PRA-01 through PRA-08 on 2026-08-17. This approval permits only the specified isolated readiness evidence, minimal instrumentation, harnesses and workflow artifacts. It does not authorize deployment, production-service/data/credential use, performance refactoring, Git publication, or changes to auth/permission/route/renderer contracts. G2/G3/G4 retain their limited PASS evidence.

## F4 前质量审查修复（已批准；严格顺序执行）

- [x] FIX-03-PRA. **COMPLETE (2026-08-16):** 已同步 README/tasks/audit/validation：G3 为当前 PASS，但 F4 输入仍未就绪；历史 2026-08-16 输入包均标为快照，当前交付只引用本轮动态验证结果。
- [x] FIX-05-PRA. **COMPLETE (2026-08-16):** 已复核 F4 输入边界、未跟踪交付文件、验证与残余风险；FIX-01～05 与全部指定回归通过，结论恢复为“F4 输入已就绪，可等待单独审批”。未执行任何 PRA/F4 工作。

## PRA-01

- [x] 状态：COMPLETE (2026-08-17)

- 任务名称：冻结场景、数据与指标合同
- 优先级：P1
- 来源需求：PRA-REQ-01 至 PRA-REQ-05
- 涉及文件：本 workflow 文档、目标页面与现有加载状态
- 修改内容：确认 E0/L20/D1/M30、ready/empty/error 条件、mark 名称、样本定义和原始数据格式
- 完成标准：每个指标都有起点、终点、失败条件和证据位置
- 验证方式：设计/需求/任务交叉检查
- 风险说明：指标口径不清时不得进入采样

执行记录：冻结合同见 `audit.md` 的 “PRA-01 frozen contract”；原始机器可读样本将写入 `assets/pra-raw-samples.json`，每条样本包含场景、browser/server 温度、navigation、LCP、readiness mark、API、DOM、console/page error、failed request、navigation/dialog/download 与明确失败原因。当前脏工作树的候选源文件已有可区分、非 instrumentation 的会话改动；PRA 源码增量只以精确补丁叠加，并在独立 worktree 中运行构建/服务。

## PRA-02

- [x] 状态：COMPLETE (2026-08-17)

- 任务名称：先建立渲染就绪状态测试
- 优先级：P1
- 来源需求：PRA-REQ-01
- 涉及文件：`src/app/notes/`、代表性详情、`src/app/manage/page.tsx` 相关测试
- 修改内容：测试 loading、ready、empty、error DOM 状态和 Performance Mark 时机
- 完成标准：测试能够区分 API 完成与 UI 真正落地
- 验证方式：目标 Vitest
- 风险说明：不得在 mark 中包含个人数据

执行记录：先新增 `src/lib/render-readiness.test.ts`，运行 `npx vitest run src/lib/render-readiness.test.ts --reporter=dot` 首次失败，原因是 `./render-readiness` 不存在。PRA-03 的最小实现后同一测试 `2 passed`；覆盖首次 mark 与重复渲染不重复 mark。该 unit test 与后续真实浏览器 DOM 采样共同构成 state/mark 证据，jsdom 不作为浏览器验收替代。

## PRA-03

- [x] 状态：COMPLETE (2026-08-17)

- 任务名称：实现最小渲染就绪标记
- 优先级：P1
- 来源需求：PRA-REQ-01
- 涉及文件：PRA-01 确认的最小页面/组件文件
- 修改内容：增加稳定 `data-render-state` 与 route-specific marks，不改变视觉或业务行为
- 完成标准：PRA-02 通过；重复渲染不会产生歧义性重复 mark
- 验证方式：目标测试与 `npx tsc --noEmit`
- 风险说明：若需建立大型性能框架则暂停重新审批

执行记录：新增 `src/lib/render-readiness.ts`，仅导出固定 union 白名单 `notes:list-ready`、`notes:detail-ready`、`manage:auth-submit`、`manage:content-ready`；重复 entry 不再 mark。`notes` list/detail 和旧 `/manage` content owner 只增加 `main[data-render-state]` 与成功提交时 mark；不改变 API、Cookie、AuthGate、路由或 Markdown renderer。验证：`npx vitest run src/lib/render-readiness.test.ts --reporter=dot` = `2 passed`；`npx tsc --noEmit` = PASS。

## PRA-04

- [x] 状态：COMPLETE (2026-08-22; isolated evidence PASS; services intentionally left active for the separately gated next tasks)

- 任务名称：建立隔离生产构建与合成数据
- 优先级：P1
- 来源需求：PRA-REQ-02、PRA-REQ-03
- 涉及文件：临时 worktree、隔离数据库、`assets/` 中的非敏感运行清单
- 修改内容：迁移空库、生成 E0/L20/D1/M30、创建临时管理员、构建并启动生产模式
- 完成标准：提交、版本、端口、API 主机、认证开关和数据计数均可复核
- 验证方式：`npm run build`、健康检查、数据库计数、公开可见性 API 检查
- 风险说明：不能隔离 API 时标记 BLOCKED，不连接真实生产数据

执行记录：先前 partial-copy approach 已清理。重新评估后，当前主工作树可作为只读、逐文件保真的 snapshot（不写回主树），在 detached worktree 中完整复制并使用 worktree 私有 `node_modules`；这保留当前跨文件 auth/session 合同，也不覆盖或暂存用户脏改动。PRA-04 已完成当前运行，证据见 `assets/pra04-isolation-manifest-20260822.json` 及同名 `pra04-*.log` 文件。

### PRA-04 current-run evidence (2026-08-22)

- Snapshot: detached `/tmp/pra04-20260822-auWgUg/worktree`, complete source/dirty/untracked state copied from the main tree; no external `node_modules` symlink. Credential-like `.env` files were excluded from the isolated copy. Dry-run comparison found no source content delta; generated `next-env.d.ts` content was identical.
- Dependencies: private frontend `npm ci` PASS. Initial private backend install under Python 3.14.6 failed at `pydantic-core`/PyO3 compatibility; the retained failure is `assets/pra04-private-env-failure.log`. Private Python 3.12.13 `.pra04-venv` install from unchanged `backend/requirements.txt` PASS.
- Database: new local PostgreSQL cluster at `127.0.0.1:55432`, database `pra_f4`, empty-cluster Alembic replay `001 -> 025` PASS, current/head `025`, 40 tables and 46 foreign keys. Synthetic-only counts: 30 total, 20 public visible, 10 hidden, types note/blog/mistake `10/10/10`.
- Build: `NEXT_PUBLIC_API_URL=http://api.localhost:8100 NEXT_PUBLIC_SITE_URL=http://localhost:3100 npm run build` PASS with Next.js 16.2.12 Turbopack; Webpack fallback was not needed.
- Runtime: API `127.0.0.1:8100`, frontend `localhost:3100`, and database `127.0.0.1:55432` are active. `api.localhost` resolved to `127.0.0.1`; frontend root/notes and API health returned 200.
- Auth/visibility: normal password login returned 200, `admin_session` was HttpOnly, authenticated `/api/auth/me` returned 200, anonymous `/api/auth/me` returned 401, admin note total was 30, public total was 20, hidden fixture did not leak, and D1 returned 200. `AUTH_BYPASS=false` and `AUTH_BYPASS_ALLOW=false`.
- Browser sampling: NOT STARTED by PRA-04 scope. No browser metrics, raw samples, p50/p90/max, failure-rate or production-readiness claim exists.
- Handoff: services, database and detached worktree remain active for PRA-05/PRA-06. The runtime-generated password was neither printed nor persisted; the next task must generate/rotate any login password at runtime without recording it.

## PRA-05

- [x] 状态：COMPLETE (2026-08-22; E0/L20/D1 each 10 valid server-warm samples; failures retained)

- 任务名称：采集匿名列表与详情性能
- 优先级：P1
- 来源需求：PRA-REQ-04
- 涉及文件：`validation.md`、`assets/` 原始样本与截图
- 修改内容：分别执行 E0、L20、D1 至少 10 个浏览器冷/服务器暖样本，另存服务器冷样本
- 完成标准：每个有效样本包含 navigation、LCP、ready mark、关键 API 与 DOM 断言
- 验证方式：真实浏览器 Performance/Resource Timing 和网络日志
- 风险说明：失败样本必须保留且不得从统计中静默删除

执行记录：在 `assets/pra05-browser-sampler.cjs` 中建立可复现 harness，使用隔离生产构建 `http://localhost:3100`、隔离 API `http://api.localhost:8100`，Chromium `151.0.7922.34`，fresh browser context、server-warm、`[data-render-state]` 唯一性断言，未使用 `locator('main')`。E0、L20、D1 均逐样本以 fsync append 写入 NDJSON；每条包含 navigation/TTFB/DOMContentLoaded/load、LCP（不可用时为 null）、readiness mark、API method/status/start/responseEnd/duration、DOM、console/page errors、failed requests、unexpected navigation、dialogs、downloads 和 `failure_reason`。

- E0：`assets/pra05-e0-raw.ndjson`，10 valid + 1 failed；首次单样本失败也已追加到同一 raw artifact，并保留副本 `assets/pra05-e0-smoke.ndjson`，原因是 harness 初版错误把空状态 `h3` 当作记录计数，已修正并未丢弃。
- L20：`assets/pra05-l20-raw.ndjson`，10/10 valid；另有修正 health probe 后的 1 个校验样本 `assets/pra05-l20-health-check.ndjson`。
- D1：`assets/pra05-d1-raw.ndjson`，10/10 valid；`pra04-d1` 的 rendered Markdown DOM 断言通过。
- 所有 full-run 样本均为 `browser_temperature=cold`、`server_temperature=warm`；API 必需请求均为 200，selector 均为 `[data-render-state]` 且唯一，未发现 strict `/api/auth/me` 或 `/api/admin/*` 请求。
- 合成 fixture 变更记录于 `assets/pra05-fixture-events.ndjson`；`assets/pra05-fixture-baseline-v3.json` 在结束时恢复 M30：30 total、20 public visible、5 published hidden、5 draft hidden、D1 public。未触碰主数据库，服务和隔离资源保留给 PRA-06。
- 本任务不计算或声明 p50/p90、最大值、失败率或性能 baseline；这些留给 PRA-07。

## PRA-06

- [x] 状态：PASS (2026-08-22; 10/10 M30 raw samples, independent negative boundary, and cleanup evidence independently verified)

- 任务名称：采集管理员登录到内容就绪性能
- 优先级：P1
- 来源需求：PRA-REQ-04
- 涉及文件：`validation.md`、`assets/` 原始样本与截图
- 修改内容：M30 数据下执行至少 10 个正常密码登录样本，覆盖提交、会话确认和管理列表就绪
- 完成标准：无认证绕过；每个样本登录成功、权限正确且管理列表达到 ready
- 验证方式：浏览器 mark、网络记录、后端日志与 DOM 断言
- 风险说明：临时凭据不得进入命令输出或仓库

执行记录：已创建并执行 `assets/pra06-login-sampler.cjs` 的一个有界 M30 探针，raw 结果即时写入 `assets/pra06-login-raw.ndjson`。登录 POST 为 200，但 `/api/auth/me` 两次均为 401，未观察到 HttpOnly `admin_session`，管理 API、`[data-render-state]`、`manage:auth-submit` 后的 `manage:content-ready` 均缺失；因此 0/10 有效样本。失败样本、manifest 和无效负向探针保留在 `assets/pra06-login-manifest.json`、`assets/pra06-negative-probe.json`。

Block Type：TASK_BLOCK；Severity：High；Problem：正常密码登录后的会话没有在隔离浏览器中建立，无法完成严格管理员确认与管理内容就绪；Evidence：`pra06-login-raw.ndjson` 的 M30-01；Impact：不能证明 HttpOnly session、管理员授权、内容 ready 或 logout/失效边界；Reproduction：对隔离 `http://localhost:3100/manage` 提交一次正常密码登录，POST 200 后 `/api/auth/me` 401 且 selector/marks 缺失；Required Action：单独审查隔离 host/CORS/cookie 会话传递原因，未经授权不得修改 auth/CORS/权限合同；Recheck Condition：修复或批准的隔离配置下，至少 10 条有效 fresh-browser/server-warm M30 样本及独立负向边界证据全部持久化。

### PRA-06 CORS runtime recheck evidence (2026-08-22)

- Recheck scope was one variable only: runtime `ALLOWED_ORIGINS=http://localhost:3101`; `AUTH_BYPASS=false` and `AUTH_BYPASS_ALLOW=false`; no auth/CORS source, route, schema, permission, renderer, dependency or main-tree product file was changed.
- A new complete detached snapshot was built with private dependencies, a fresh PostgreSQL cluster at `127.0.0.1:55433/pra06_cors_recheck`, API `http://api.localhost:8101`, and frontend origin `http://localhost:3101`. The synthetic M30 fixture was 30 total / 20 public-visible / 5 published-hidden / 5 drafts.
- The first preflight failure (frontend process reclaimed before navigation; no login submitted) is preserved in `assets/pra06-cors-recheck-20260822.preflight.log` and `assets/pra06-cors-recheck-20260822.preflight-negative.json`; it is not treated as auth evidence.
- Exactly one normal-login form probe reached login: `assets/pra06-cors-recheck-20260822.raw.ndjson` M30-02. Login POST was 200, but no `admin_session` was observed; `/api/auth/me` was 401; strict `/api/admin/dashboard/summary` was 401; management API, unique `main[data-render-state]`, and `manage:content-ready` were absent. Exact failure text remains in the raw row.
- Independent non-browser verification showed the runtime CORS response returned `Access-Control-Allow-Origin: http://localhost:3101` and `Access-Control-Allow-Credentials: true`; the CORS variable therefore took effect but did not establish the browser session. The negative no-cookie probe is explicitly invalid because normal auth was not established.
- Recheck result: `FAIL`. No 10-sample run started; no performance/readiness claim follows. Exact artifacts are listed in `assets/pra06-cors-recheck-20260822.manifest.json`.
- Cleanup: only the new API/frontend/PostgreSQL resources were stopped; ports 3101/8101/55433 are free; the detached worktree was unregistered; the exact isolated root is recoverable at `/Users/limengyang/.Trash/pra06-cors-recheck-20260822-wUJZDh`; main status inventory hash is unchanged and `git diff --check` passes.

### PRA-06 cookie propagation diagnostic (2026-08-22)

- 结果：`FAIL / BLOCKED`。本次只执行一个 normal browser login，不启动 10×，不计算性能指标，也不授权修复 auth/CORS。
- 新建完整 dirty-tree detached snapshot、私有 Node 24/npm 11 与 Python 3.12 依赖、fresh PostgreSQL `127.0.0.1:55434/pra06_cookie_diagnostic`；Alembic `001 -> 025`、生产构建、API/frontend health 和合成 M30 `30/20/5/5` 均通过。运行时仅使用 `NEXT_PUBLIC_API_URL=http://api.localhost:8102`、`ALLOWED_ORIGINS=http://localhost:3102`、`AUTH_BYPASS=false`、`AUTH_BYPASS_ALLOW=false`。
- 启动阶段曾发生一次重复启动调用：第二次 API/frontend 绑定失败；未提交登录，已单独保存在 `assets/pra06-cookie-diagnostic-20260822-preflight.log`，健康检查随后确认唯一 active listener 正常，未混入 Cookie 结论。
- 唯一一次实际表单登录记录于 `assets/pra06-cookie-diagnostic-20260822.raw.ndjson` 的 `M30-cookie-diagnostic-01`：login POST `200`；POST 响应包含 `admin_session` 的 Set-Cookie 属性（Path、Max-Age、HttpOnly、SameSite=Lax），原始值未持久化；CDP blocked-cookie reason 数为 `0`。
- 同一浏览器上下文中 cookie jar 没有 `admin_session`；后续 `/api/auth/me` GET 为 `401`（两次），严格 `/api/admin/dashboard/summary` 为 `401`，这些请求的 Cookie header 均不存在；`[data-render-state]`/management ready DOM 不存在，`manage:auth-submit` 有 1 个，`manage:content-ready` 为 0。完整失败原因为 raw `failure_reason`。
- 诊断结论：服务端不是“未发 Set-Cookie”；证据也不是“已存储但后续请求未发送”，而是浏览器未将该响应 cookie 留在 jar，且本次 CDP 未暴露更细的阻断原因。具体拒收策略仍未知，不得据此猜测或修改 auth/CORS 合同。
- 完整资产：`pra06-cookie-diagnostic-20260822.manifest.json`、`.raw.ndjson`、`.log`、`-preflight.log`、`-cleanup.log`；密码、token、cookie 原始值均未持久化。
- 清理 PASS：临时管理员已禁用，隔离 session 已撤销；新 API/frontend/PostgreSQL 已停止；3102/8102/55434 无监听；detached worktree 已注销，快照可恢复于 `/Users/limengyang/.Trash/pra06-cookie-diagnostic-20260822-6YOPhy`；主树和生产资源未触碰。

### PRA-06 same-host topology diagnostic (2026-08-22)

- 结果：`BLOCKED BEFORE BROWSER LOGIN`。严格保持单次实验边界；未运行 10×，未创建临时管理员，未提交登录。
- 新建完整 dirty-tree detached snapshot 与私有 Node 24/npm 11、Python 3.12 依赖；PostgreSQL `127.0.0.1:55435/pra06_same_host` 迁移 `001 -> 025` 通过。目标运行时配置为 `frontend=http://localhost:3103`、`api=http://localhost:8103`、`NEXT_PUBLIC_API_URL=http://localhost:8103`、`ALLOWED_ORIGINS=http://localhost:3103`，两个 bypass 均为 false。
- 生产前端构建在 page-data 阶段失败：当前 `src/lib/api/config.ts` 的现行生产守卫拒绝 localhost API base，精确错误与独立启动失败证据保存在 `assets/pra06-same-host-diagnostic-20260822-build.log`。不绕过守卫、不改产品源码、不降级为开发服务器，因此没有可归因的真实浏览器 Cookie/auth/readiness 证据。
- 脱敏 raw/manifest 明确记录 login status、Set-Cookie 属性、browser jar、Cookie header、`/api/auth/me`、strict management 和 readiness 均为 `not_started/null`，失败原因为 `startup-frontend-build-failed:production-guard-rejected-localhost-api; login-not-submitted`。完整资产使用 `assets/pra06-same-host-diagnostic-20260822.*` 前缀。
- 清理 PASS：PostgreSQL 停止，3103/8103/55435 无监听，detached worktree 注销，临时根移除；可恢复副本在 `/Users/limengyang/.Trash/pra06-same-host-diagnostic-20260822-sBC76G`；主树状态哈希保持 `6de303c46f48dfd069c96161d5b6e967a54ba056fa60879093ebd3ef21ea2476`，`git diff --check` PASS。
- 结论仅为启动边界阻断，不替代 auth/CORS 根因诊断，不授权源码修复，也不产生 readiness/performance claim。

### PRA-06 same-hostname execution diagnostic (2026-08-22)

- 结果：`BLOCKED / LIFECYCLE FAILURE`。按要求使用 frontend `http://api.localhost:3107`、API `http://api.localhost:8107`（bind `127.0.0.1:8107`）、PostgreSQL `127.0.0.1:55439`、`NEXT_PUBLIC_API_URL` 同 API、`ALLOWED_ORIGINS=http://api.localhost:3107`，两个 bypass 均为 false；未运行 10×。
- 完整 dirty-tree detached snapshot、私有 Node `v24.18.0`/npm `11.16.0`、Python `3.12.13` venv、`node_modules/.bin/next` 断言、Alembic `001 -> 025`、生产构建和 M30 `30/20/5/5` 均完成。构建首次因未注入 API URL 被 guard 拒绝，随后按指定 API URL 重跑 PASS。
- 启动失败证据保留：首次错误入口 `app.main:app` 见 `pra06-same-hostname-exec-20260822.api.log`；改用快照 `backend` cwd 的 `main:app` 后，生产 lifespan 因默认 `ENABLE_REGISTRATION=true` 拒绝，见 `pra06-same-hostname-exec-20260822.api-restart.log`。补齐 runtime `ENABLE_REGISTRATION=false` 后曾返回 health 200，但进程在浏览器前退出。
- 唯一一次真实 Playwright 正常登录探针从快照 cwd 执行，M30/admin seed 已创建；其 raw 记录为生命周期失败，所有 API 请求均 `ERR_CONNECTION_REFUSED`，因此不计入 auth/Cookie 结论。精确 `failure_reason` 保存在 `pra06-same-hostname-exec-20260822.raw.ndjson`。
- 持久化重启未通过：`nohup main:app` 启动并返回一次 health 200，但 10 秒 listener/health 复核的首个间隔即发现 8107 无 listener；证据见 `pra06-same-hostname-exec-20260822.api-persistent.log` 和 `pra06-same-hostname-exec-20260822.persistent-preflight.log`。未再启动浏览器，不把生命周期失败转写为认证失败。
- 清理 PASS：临时管理员由 harness 禁用；3107/8107/55439 无监听；PostgreSQL exact cluster stopped；worktree 已注销；root 可恢复于 `/Users/limengyang/.Trash/pra06-same-hostname-exec-20260822-qmNpfI`。无产品源、auth/CORS、route/schema/renderer/dependency/main-tree/production 修改，无 deploy/commit/push。

### PRA-06 single-shell retry (2026-08-22)

- 结果：`BLOCKED BEFORE BROWSER LOGIN`。按已审 runner 原样执行 `PRA_RUN_ID=pra06-single-shell-retry-20260822 bash docs/workflows/production-render-readiness-acceptance/assets/pra06-single-shell-runner-20260822.sh`；runner exit code 为 `30`，在迁移阶段停止，未启动 API/frontend 或浏览器探针。
- 当前 HEAD 为 `202ea14d3362a84a491a7a8e32d2afd5d2e0bc1f`；运行时记录 frontend `3110`、API `8110`、PostgreSQL `55441/pra06_single_shell`，`AUTH_BYPASS=false`、`AUTH_BYPASS_ALLOW=false`、`product_source_changed=false`。npm、Python venv、生产构建、空 PostgreSQL 初始化和启动步骤均已到达迁移前后；迁移日志报告 `FAILED: Path doesn't exist: '/Users/limengyang/2025-blog-public/alembic'`，随后提示需用 `init` 创建 scripts folder。
- 本次未创建 manifest/raw、临时管理员、会话、API/frontend 服务或浏览器样本；本次前缀下仅保留 runner、snapshot、依赖、构建、PostgreSQL 和 migration 日志：`assets/pra06-single-shell-retry-20260822.*`。收尾时资产目录全部 47 个 JSON/NDJSON 文件（117 个文档/记录）解析通过，错误数为 0；本次 retry 没有新增 JSON/NDJSON。
- 运行后 3110/8110/55441 无监听；主工作树状态 hash 仍为 `6de303c46f48dfd069c96161d5b6e967a54ba056fa60879093ebd3ef21ea2476`，`git diff --check` PASS。runner 清理未完全闭合：本次 `/private/tmp/pra06-single-shell-retry-20260822-siiSYs/worktree` 仍在 `git worktree list --porcelain` 中显示为 `prunable`，且本次根目录未在 `/private/tmp` 或 `/Users/limengyang/.Trash` 找到；未执行额外 prune 或删除。
- 结论仅为迁移前阻断，不产生 auth/CORS/Cookie、readiness、性能或生产就绪证据；未修改产品源代码、auth/CORS、部署、commit 或 push。

### PRA-06 corrected single-shell retry2 (2026-08-22)

- 结果：`BLOCKED BEFORE BROWSER LOGIN / HARNESS LIFECYCLE FAILURE`。按要求原样执行 `PRA_RUN_ID=pra06-single-shell-retry2-20260822 bash docs/workflows/production-render-readiness-acceptance/assets/pra06-single-shell-runner-20260822.sh`；runner 最终退出码为 `0`，但 probe 自身记录 `probe_exit=1`。
- 修正验证通过：runner 在 snapshot `backend` cwd 执行 Alembic，迁移完整到 `001 -> 025`；生产构建 PASS，API/frontend 启动与 health PASS，CORS preflight 为 200；运行时 frontend `3110`、API `8110`、PostgreSQL `55441/pra06_single_shell`，`AUTH_BYPASS=false`、`AUTH_BYPASS_ALLOW=false`、`product_source_changed=false`。
- 浏览器 probe 未进入 manifest/raw 写入：rsync 后 detached snapshot 不含可用 `.git`，probe 在 `git rev-parse HEAD` 处失败；精确错误保存在 `assets/pra06-single-shell-retry2-20260822.log`。因此本次没有 manifest、raw NDJSON、临时管理员、会话或浏览器样本，不把该失败解释为 auth/CORS/Cookie 结果。
- 清理核验：runner 报告 3110/8110/55441 均无监听；`main_status_hash_after_cleanup` 仍为 `6de303c46f48dfd069c96161d5b6e967a54ba056fa60879093ebd3ef21ea2476`；精确 root 已在 `/Users/limengyang/.Trash/pra06-single-shell-retry2-20260822-TADkxk` 可恢复。但 `git worktree list --porcelain` 仍显示该 run 的 `/private/tmp/pra06-single-shell-retry2-20260822-TADkxk/worktree` 为 `prunable`，未执行 prune/delete。
- 结论仅为 probe 生命周期/资产生成阻断；不产生管理员登录、readiness、性能或生产就绪证据，也不授权修复 runner、auth/CORS、依赖、部署、commit 或 push。

### PRA-06 M30 batch sampling (2026-08-22): PASS

- Primary Owner executed `PRA_RUN_ID=pra06-m30-batch-20260822 PRA_M30_COUNT=10 PRA_M30_MAX_ATTEMPTS=12 bash docs/workflows/production-render-readiness-acceptance/assets/pra06-single-shell-runner-20260822.sh` in `production-build-local-isolated`: private dependencies, detached snapshot, fresh PostgreSQL `55441`, API `8110`, frontend `3110`, `AUTH_BYPASS=false`, `AUTH_BYPASS_ALLOW=false`, and no product source change.
- The authoritative manifest is `assets/pra06-m30-batch-final-20260822.manifest.json`: attempts `10`, valid `10`, failed `0`, failure rate `0`, with raw and per-sample manifest paths for `M30-01` through `M30-10`. Each raw is browser-cold/server-warm and was atomically persisted by its child probe before the next attempt.
- Each raw contains navigation status plus TTFB/DOMContentLoaded/load/duration, an explicit `lcp` field (observed `null` where no LCP entry was emitted), API ResourceTiming entries and response status evidence, exact readiness marks, `[data-render-state]` selector/main/state and 30-row DOM evidence, console/page errors, all failed requests with expected/unexpected partitions, unexpected navigation/dialog/download arrays, and `failure_reason`.
- All ten samples are `valid=true`; each has login `200`, authenticated `/api/auth/me` and strict management `200`, one ready main, one `manage:auth-submit`, one `manage:content-ready`, zero unexpected console/errors/failed requests/side effects. Expected 401/ERR_ABORTED noise remains in raw and is not counted as failure.
- Independent negative boundary evidence is `assets/pra06-m30-negative-final-20260822-negative.json`: fresh no-cookie `auth_me=401` and strict management `401`; after a normal authenticated login, logout `200`, then `auth_me=401`, strict management `401`, and no remaining `admin_session`. Earlier harness failures are preserved at `assets/pra06-m30-batch-20260822-negative.json` and `assets/pra06-m30-negative-recheck-20260822-negative.json` and are not counted as M30 sample failures.
- Negative-history clarification: both preserved earlier negative raw files already contain no-cookie HTTP statuses `auth_me=401` and `strict_management=401`, but their top-level `valid=false` was a harness classification inconsistency caused by incorrect field-name checks; the same earlier recheck raw separately has `logout_boundary.valid=true`. The final corrected raw has both `no_cookie_boundary.valid=true` and `logout_boundary.valid=true`, so no HTTP 401 evidence was discarded or reinterpreted as an application failure.
- Cleanup PASS for the batch and recheck runs: runner logs show ports `3110/8110/55441` at zero listeners and unchanged main status hash `6de303c46f48dfd069c96161d5b6e967a54ba056fa60879093ebd3ef21ea2476`; only the four pre-existing worktrees remain. `node --check`, `bash -n` and `git diff --check` pass.
- Independent Verifier Hegel completed a read-only audit: all ten raw records, schema/counts, auth/Cookie/readiness, noise classification, final negative boundary and cleanup evidence passed. The negative-only runner's `probe_exit=2` is retained as a bookkeeping note because its sample counter was zero; its final negative raw was `valid=true`.
- This closes PRA-06 as an independently verified PASS and authorizes PRA-07 only for serial raw-data aggregation. It does not authorize optimization, F4 PASS, production readiness, deployment, commit or push.

## PRA-04 to PRA-08 current evidence recheck (2026-08-23)

- [x] PRA-04 `PASS`: manifest and retained build/migration/runtime logs agree on HEAD, isolated hosts and ports, bypass flags, Alembic `025`, 40 tables, 46 foreign keys, synthetic counts `30/20/10`, and normal/anonymous authentication boundaries. The former isolated services and worktree are absent, as required after PRA-08.
- [x] PRA-05 `PASS_WITH_NOTES`: authoritative E0/L20/D1 raw files contain `11/10/10` attempts and `10/10/10` valid rows; the E0 failed row remains present. All valid rows have the required state/mark/API/DOM/error fields and cold-browser/warm-server labels. All LCP fields are null; no server-cold primary aggregate exists; the original scenario manifests retain the earlier 404 warm-probe result while the corrected check is separate.
- [x] PRA-06 `PASS`: the final manifest lists ten distinct raw files and all ten prove normal login, HttpOnly `/api` cookie presence, authenticated `/api/auth/me` and strict management success, unique ready DOM with 30 rows, exact auth/content marks and zero unexpected error partitions. The final negative raw proves both no-cookie and post-logout 401 boundaries without persisted secret values.
- [x] PRA-07 `PASS_WITH_NOTES`: the contract test passes; a temporary-directory rerun is equal to the persisted JSON after removing only `generated_at`; all 14 recorded input hashes match; E0 remains `1/11` failed and all scenario LCP summaries remain unavailable.
- [x] PRA-08 `PASS`: all 30 target ports have zero listeners; four known worktrees remain and prune dry-run is empty; 94 JSON/NDJSON files parse as 164 records; no staged path exists; `git diff --check` passes; the current status hash still equals `6de303c46f48dfd069c96161d5b6e967a54ba056fa60879093ebd3ef21ea2476`.
- Boundary: this was a Primary Owner read-only perspective pass, not a new sampling run and not an independent review. No product source, service, database, account, credential, deployment, commit or push was changed. Residual limitations are recorded in `risks.md` and routed through `next-requirements.md`.

## PRA-07

- [x] 状态：PASS_WITH_NOTES (2026-08-22; raw-only aggregation; PRA-08 PASS)

- 任务名称：从持久化 raw 形成可重算聚合并记录未验证观察
- 优先级：P1
- 来源需求：PRA-REQ-05
- 涉及文件：`validation.md`、验收/风险/下一轮需求文档
- 修改内容：只读 E0/L20/D1 与 M30 manifest 列出的 raw，计算 readiness、TTFB、DOMContentLoaded、load、LCP（null 保持不可用）、关键 API timing 的 p50/p90/max/failure_rate，并单列 M30 认证状态码概览
- 完成标准：输入文件、温度、过滤规则、失败样本、nearest-rank 算法和缺失字段均可重算；不把开发空数据值或单个最好样本当作 SLA
- 验证方式：聚合脚本运行、独立 raw 重算、JSON/NDJSON 解析、输入/输出计数和敏感值检查
- 风险说明：E0 有 1 个失败样本；LCP 全部 null；无 server-cold 主聚合；这些限制不升级为生产基线或生产就绪结论

执行记录：脚本 `assets/pra07-raw-aggregation.py` 只读取 `pra05-e0-raw.ndjson`、`pra05-l20-raw.ndjson`、`pra05-d1-raw.ndjson` 和 `pra06-m30-batch-final-20260822.manifest.json` 明列的 10 个 M30 raw。输出为 `assets/pra07-raw-aggregation-20260822.json` 与 `.md`；使用 nearest-rank（ceil(q*n)，不插值），仅 `valid=true` 且有限非负数值进入延迟统计，失败样本保留在 attempts/failed_samples。结果：E0 11 attempts/10 valid/1 failed/0.09090909090909091，L20 10/10/0/0，D1 10/10/0/0，M30 10/10/0/0。四场景均达到至少 10 valid。LCP 10/10/10/10 均为 null，输出 `not_available`，未当作 0；M30 登录/me/strict 的 HTTP 状态仅作认证边界概览，不作延迟值。独立重算、敏感值扫描、`git diff --check` 均通过。没有生成 SLA、生产性能承诺、优化已验证或 F4 PASS；PRA-08 已完成最终 QA cleanup/independent review。

## PRA-08

- [x] 状态：PASS (2026-08-22; final QA cleanup and independent read-only review)

- 任务名称：清理与最终复核
- 优先级：P1
- 来源需求：PRA-REQ-02、PRA-REQ-03
- 涉及文件：`tasks.md`、`validation.md`
- 修改内容：禁用临时管理员，清除凭据，停止进程，移除临时 worktree，并复核工作树
- 完成标准：不存在本轮临时账户访问能力、运行进程、凭据或遗留 worktree
- 验证方式：CLI/数据库、端口、进程、auth vault、`git worktree list` 和 `git status`
- 风险说明：清理未通过时任务不得标记 COMPLETE

执行记录：PRA-08 最终只读证据见 `assets/pra08-final-cleanup-20260822.json`。目标端口 `3000、3100-3108、3110、8100-8108、8110、55432-55441` 均无监听；`ps` 仅显示与本轮无关的既有 8000 后端/Next 进程，未触碰。`git worktree list --porcelain` 仅保留四个已知既有 worktree，`git worktree prune -n -v` 无输出。workflow 记录确认临时管理员已禁用、3 个隔离会话已撤销/过期；最终 negative raw 的密码/token/raw cookie 持久化标记为 false，清理日志存在且无秘密值。全部 94 个 JSON/NDJSON 非空可解析，PRA-07 的 14 个输入哈希与当前文件匹配，历史失败样本仍保留。主工作树 status hash 与 `6de303c46f48dfd069c96161d5b6e967a54ba056fa60879093ebd3ef21ea2476` 一致，无 staged paths，`git diff --check` PASS。未启动服务、未重新采样、未连接真实服务、未 commit/push/deploy；总体仍为 PARTIAL，不构成 F4 PASS、生产就绪或部署授权。

## Stop Conditions

- 需要生产数据、真实管理员、生产部署、机器级 DNS/CORS 放宽或 `AUTH_BYPASS`。
- 构建/测试暴露超出最小 instrumentation 的产品改动。

## PRA-06 corrected single-probe harness confirmation (2026-08-22)

- [x] 状态：PASS — independent Senior QA/SDET single-probe confirmation
- [x] 使用既有 runner 且只执行一次：`PRA_RUN_ID=pra06-noise-confirm-20260822 bash docs/workflows/production-render-readiness-acceptance/assets/pra06-single-shell-runner-20260822.sh`
- [x] Harness review：Playwright cookie query 使用 API `/api/auth/me` matching path，能够返回 Path `/api` 的 cookie；raw `console_errors`、`failed_requests` 及 expected/unexpected 分组均持久化。
- [x] Noise review：本次 raw 保留 1 条 console 401、26 条 frontend `/notes|/blog` `net::ERR_ABORTED` link-prefetch 事件和 1 条 Google Analytics `/g/collect` `net::ERR_ABORTED` 事件；expected 分组分别为 `1/26+1`，unexpected 分组均为 `0`。
- [x] Core browser conditions：login POST `200`；Set-Cookie 中 `admin_session` 的 Path/HttpOnly 等属性证据存在；cookie jar 有 `admin_session`、`path=/api`、`HttpOnly=true`；strict management `200` 且 Cookie header 存在；唯一 `main[data-render-state]` 为 `ready`，唯一 `manage:content-ready` mark 存在。
- [x] Boundary：manifest/raw 的 `ten_sample_run=false`、`performance_baseline=false`、`production_readiness_claim=false`；未修改产品 source/auth/CORS/dependencies，未运行 10×。
- [x] 独立核验：38 个 JSON、21 个 NDJSON 全部解析；`git diff --check` PASS；3110/8110/55441 无监听；noise run worktree/temp root 无残留；runner 前后主工作树 status hash 均为 `6de303c46f48dfd069c96161d5b6e967a54ba056fa60879093ebd3ef21ea2476`。
- 证据：`assets/pra06-noise-confirm-20260822.manifest.json`、`assets/pra06-noise-confirm-20260822.raw.ndjson`、`assets/pra06-noise-confirm-20260822.log`、`assets/pra06-noise-confirm-20260822.runner.log`。
- 该 PASS 仅关闭本次 corrected single-probe harness/auth-session evidence block；不授权 PRA-07、性能基线、生产就绪、部署、commit 或 push。
