# Phase 0 — 工程 Gate 实测证据（T-00 / T-00b）

> 执行日期：2026-09-04 ｜ 基线：`refactor/baseline`（工作树含未跟踪 workflow 文档，无代码改动）
> 环境：macOS（darwin）｜ Node 26.0.0（engines 声明 24.x，见 R-T00-5）｜ Python 3.12.13（backend/.venv）｜ PostgreSQL 16.14（Homebrew，localhost:5432）
> 本文档是 PR-01（D12 smoke）与 CI Job 3/4（D13）的拓扑事实源。

## 1. T-00 — 命令基线实测

| # | 命令 | 结果 | 证据摘要 |
| --- | --- | --- | --- |
| 1 | `npx tsc --noEmit` | **PASS** | exit 0，无输出 |
| 2 | `npm run test:typecheck` | **PASS** | exit 0（tsconfig.test.json） |
| 3 | `npm test`（vitest run） | **PASS** | 39 test files，374 tests passed，0 failed |
| 4 | `pytest`（backend/，.venv） | **PASS** | 412 passed，6 skipped，2 warnings（ResourceWarning，既有） |
| 5 | `npm run build`（next build） | **PASS**（重跑后） | 首跑 FAIL：`ENOTEMPTY ... rmdir .next/server`（stale 缓存 flake）；清理 `.next` 后重跑 PASS |
| 6 | `alembic upgrade head`（空库） | **PARTIAL** | 空库直接执行在 migration 026 失败（F-T00-1/F-T00-2）；补两项集群前置后 000→026 全链 PASS（46 张 public 表，`alembic_version=026`）。详见 §2 |

### 环境事实

- `pytest` 无需 `PYTHONPATH=.`（backend/ 目录下直接通过）。
- `npm run build` 的 ENOTEMPTY 是 `.next` 残留缓存问题：CI 全新 checkout 不会遇到；本地验证前清理 `.next` 可复现性更好（R-T00-4）。

## 2. 空库 `alembic upgrade head` — 发现与定版

### F-T00-1（HIGH，影响 CI Job 2/3）：migration 026 在 PG15+ 全新库失败

`026_legacy_system_retirement.py:1215-1220` 执行 `ALTER TABLE public.* OWNER TO legacy_migration_owner`。PostgreSQL 规定：变更表属主时，**新属主必须对表所在 schema 拥有 CREATE 权限**。026 仅在 `:305` `GRANT USAGE ON SCHEMA public TO legacy_migration_owner`，而 PG 15+ 起新库 public schema 不再默认授予 PUBLIC CREATE 权限。

- 实测：scratch 空库回放在 026 报 `InsufficientPrivilegeError: permission denied for schema public`。
- 对照：`blog_db` 的 `\dn+ public` 显示历史手工授权 `blog_user=UC`（CREATE+USAGE）——本机之所以能跑通，是依赖这一不在任何 migration 中的手工授权。
- 影响：CI `postgres service → alembic upgrade head（空库）`（D13 Job 2）若以**普通应用角色**执行会失败；以 fresh postgres service 的**超级用户**执行则天然满足（superuser 绕过该检查）。
- 处置：Phase 0 不改 migration（schema 变更属 HIGH，超出本 Phase）。CI 契约定版为**以 postgres 超级用户执行 alembic**；若未来 CI 改为应用角色，需先 `GRANT CREATE ON SCHEMA public TO legacy_migration_owner` 或修 026。

### F-T00-2（MEDIUM，仅本机集群复用场景）：集群级角色已存在时的 ADMIN OPTION 要求

026 顶部以 `IF NOT EXISTS` 防御性 `CREATE ROLE`（`:105-123`）并执行 `GRANT legacy_note_adapter TO legacy_note_adapter_runner`。角色是**集群级**对象：在同一集群上对第二个空库回放时，角色已由历史运行创建，执行 alembic 的应用用户（非超管）报 `permission denied to grant role "legacy_note_adapter"`。本机复现处置：由集群管理员 `GRANT <role> TO <app_user> WITH ADMIN OPTION`（5 个角色：legacy_note_adapter / legacy_migration_owner / legacy_note_verifier / app_role / legacy_migration_maintenance_runner）后回放通过。fresh CI postgres 无此问题。

### 回放结论（前置补齐后）

| 项 | 结果 |
| --- | --- |
| 迁移链 | 000→026 全部 PASS（单次顺序回放，无手动干预） |
| public 表数量 | 46（scratch 实测）；blog_db 为 42（含历史演化差异，不作相等断言） |
| `alembic_version` | `026` |
| 清理 | scratch 库已删除，临时 ADMIN OPTION 授权已 CASCADE 撤销 |

## 3. T-00b — runtime/CI 拓扑定版（全部实测）

### 3.1 前端 production 工件与启动

| 项 | 定版 | 证据 |
| --- | --- | --- |
| 构建 | `npm run build:cf`（opennextjs-cloudflare build，F14） | 产物 `.open-next/worker.js` + `.open-next/assets`（wrangler.toml `main`/`[assets]`） |
| 本地 production 启动 | `npm run preview`（opennextjs-cloudflare preview → wrangler dev / workerd） | 实测日志 `[wrangler:info] Ready on http://localhost:8787` |
| 端口 | **8787**（wrangler 默认） | 同上 |
| 禁止冒充 | 不得以 `next dev` / `next start` / 纯 `next build` 顶替 | R31-1；`next start` 非 workerd runtime，不等价 |
| build:cf 稳定性 | 首跑 FAIL（bundling 报错、无 worker.js），立即重跑 PASS——transient flake | R-T00-3：CI 中首跑失败可重试一次再判 FAIL；持续观察 |

### 3.2 探针实测（本地 production 拓扑）

| 探针 | 结果 |
| --- | --- |
| `GET http://localhost:8787/` | **200** |
| `GET http://localhost:8787/notes` | **200**（静态预渲染） |
| 首页 HTML 引用 `_next` 资产逐个 GET | **referenced=16 / failed=0**（本地工件自洽） |

> 对照：R31 审计的生产 404（16 引用中 8×404）**不属于工件自缺资源**——本地 preview 全部 200，佐证 404 为部署一致性/多窗口问题，须以 post-deploy smoke 在生产 URL 实测（PR-01）。

### 3.3 Backend 启动契约

| 项 | 定版 | 证据 |
| --- | --- | --- |
| 启动命令 | `backend/.venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port <PORT>`（workdir `backend/`） | 实测通过 |
| smoke 端口 | **8001** | **8000 被常驻 backend 实例占用**（本机有非本会话管理的服务进程监听 127.0.0.1:8000，服务 blog_db；实测 bind 报 `address already in use`）。smoke 不得杀常驻进程，固定用 8001 |
| health 探针 | `GET http://127.0.0.1:8001/api/health` → 200 `{"status":"ok"}` | 实测（8001 smoke 实例） |
| alembic 时点 | **`alembic upgrade head` 必须先于 backend 启动** | `backend/main.py:17,24-35`：lifespan 启动即校验 `alembic_version == "026"`，不满足直接启动失败（fail-closed） |
| DB 隔离 | smoke 使用一次性 scratch 库（upgrade head + seed），不指向 blog_db | 实测：8001 实例仅返回 seed 行 |

### 3.4 环境变量集（定版，不含真实 secrets）

- **backend**（`backend/.env` 实际键；模板见 `backend/.env.example`）：`DATABASE_URL`、`JWT_SECRET_KEY`、`JWT_ALGORITHM`、`JWT_EXPIRE_MINUTES`、`AI_API_KEY`、`AI_BASE_URL`、`AI_MODEL`、`DASHSCOPE_API_KEY`、`DASHSCOPE_MODEL`、`DEEPSEEK_API_KEY`、`DEEPSEEK_MODEL`、`KEEP_ALIVE_ENABLED`、`KEEP_ALIVE_INTERVAL`、`KEEP_ALIVE_URL`、`WEBAUTHN_RP_ID`、`WEBAUTHN_ORIGIN`、`OPERATOR_REGISTRATION_KEY`、`UPLOAD_ROOT`。其余（`ENV`、`ALLOWED_ORIGINS`、`AUTH_BYPASS` 等）走 `config.py` 默认值。smoke 实例仅需 `DATABASE_URL` 覆盖 scratch 库，其余默认。
- **frontend**：`NEXT_PUBLIC_API_URL`（构建期内联）：`.env.production` = `https://public-api.limengyang.me`、`.env.development` = `http://localhost:8000`。**本地 preview 使用 production 内联值**——页面数据请求指向生产 API（只读 GET）；smoke 对本地拓扑只验证资产完整性与页面壳，`/api/health` 探针独立打本地 backend。不为了 smoke 重构建 artifact（保持与生产同一工件）。
- secrets 纪律：本证据文档与 CI 均不落任何真实 `*_API_KEY` / `JWT_SECRET_KEY` / DB 口令。

### 3.5 Seed fixture（定版）

在 scratch 库 `alembic upgrade head` 之后执行（实测可读）：

```sql
INSERT INTO notes (id,slug,title,content,type,status,hidden) VALUES
 (gen_random_uuid(),'smoke-seed-note-001','Phase0 Smoke Note','# smoke seed note','note','published',false),
 (gen_random_uuid(),'smoke-seed-mistake-001','Phase0 Smoke Mistake','# smoke seed legacy mistake','mistake','published',false);
```

- "public mistake" 当前拓扑 = **legacy `Note(type='mistake', status='published')`**（公共 `/mistakes` 的现行读取路径，F9）。实测 `GET /api/notes?type=mistake` 返回 seed 行。
- canonical `Mistake.visibility` 受 CHECK 锁定 `'private'`（F13），当前**无法** seed 公开 canonical mistake；PR-09（migration 031）落地后 seed fixture 需同步更新并重验。
- notes 最小必需列（实测）：`id`（Python 侧默认，SQL 需显式提供）、`slug`、`title`、`content`、`type`、`status`、`hidden`。

### 3.6 CI 契约（D13 Job 3/4 前置事实，据此实施）

```
Job 3 (smoke):  npm ci → npm run build:cf →
                scratch PG（superuser: alembic upgrade head + seed §3.5）→
                uvicorn main:app --port 8001（DATABASE_URL=scratch）→
                opennextjs-cloudflare preview（:8787）→
                runtime-smoke：GET / →资产逐个 200→ GET /notes → GET 127.0.0.1:8001/api/health
                （smoke 脚本本体属 PR-01 交付物；本 Phase 定版拓扑与探针）
Job 2 (backend): alembic upgrade head 以 postgres 超级用户执行（F-T00-1/F-T00-2）
```

## 4. Phase 0 Gate 结论

| Gate 要求 | 状态 |
| --- | --- |
| 命令清单全部可执行并记录基线结果 | **PASS**（6/6 实测记录；alembic 为 PARTIAL 已定因） |
| T-00b 拓扑定版留证据 | **PASS**（§3，全部实测；PR-01 与 CI Job 3/4 前置已满足） |

**Phase 0 = PASS。** 遗留输入到后续 PR：

- F-T00-1/F-T00-2 → PR-04 / PR-17（CI superuser 契约）；如 CI 无法用 superuser，则 026 需一次修复（HIGH，另行走审批）。
- R-T00-3（build:cf 首跑 flake）→ PR-17 CI 重试策略。
- R-T00-5（Node 26 vs engines 24.x）→ 本机与 CI Node 版本统一在 PR-17 处理。
- Seed fixture 的 public canonical mistake 更新 → PR-09。

## 5. 独立复核记录（2026-09-04，第二会话执行）

| 主张 | 复核方式 | 结果 |
| --- | --- | --- |
| tsc / test:typecheck PASS | 独立复跑 | PASS |
| vitest 39 files / 374 passed | 独立复跑 | **精确一致**（39/374，0 failed） |
| pytest 412 passed, 6 skipped, 2 warnings | 独立复跑 | **精确一致** |
| build 首跑 ENOTEMPTY flake，清理 `.next` 后 PASS | 独立复跑：首跑**当场复现** `ENOTEMPTY rmdir .next/server`；`rm -rf .next` 重跑 PASS | **处置路径复现成立** |
| F-T00-1 行号（026:1215-1220 ALTER OWNER、:305 仅 GRANT USAGE、:105-123 防御 CREATE ROLE） | sed 核对 | 全部属实 |
| 超管空库全链 000→026 → 46 表 + version 026 | 全新 scratch 库（`phase0_verify_a`）独立回放 | **精确一致**（46 / 026） |
| 非超管回放不可靠（F-T00-2 机制） | 第二 scratch 库属主=非超管角色，以该角色执行 | **失败于 `GRANT legacy_note_adapter TO legacy_note_adapter_runner`：`Only roles with the ADMIN option on role "legacy_note_adapter" may grant this role`** —— 机制证实，CI superuser 契约成立 |
| `main.py` lifespan fail-closed 校验 026 | 读源码（`EXPECTED_ALEMBIC_REVISION="026"`，`alembic_version` 不匹配即 RuntimeError） | 属实 |
| `:8000` 被常驻进程占用、`:8787` 空闲 | `lsof` 实测 | 属实（Python PID 常驻 8000；8787 无残留） |
| `preview`=opennextjs-cloudflare preview、engines node 24.x | package.json 核对 | 属实 |
| scratch 资源清理 | 复核自建 scratch 库×2、角色×1 已全部删除（残留查询=0） | 干净；本复核未触碰 `blog_db` |

> 复核未复跑 `build:cf`/`preview`/探针段（§3.1–3.2 为本会话已实测的同一工件路径，重复启动成本高且无状态差异）；该段状态维持原记录，PR-01 实施时在 CI 中首次常态化执行。
> alembic 运行需 `PYTHONPATH=.`（与 AGENTS.md 约定一致；CI Job 命令需包含）。
