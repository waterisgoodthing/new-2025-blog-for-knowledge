# Decisions — deepseek-session

**Primary Owner**: opencode (deepseek-v4.1-flash)
**最后更新**: 2026-10-13

---

## D001: 以当前运行事实为准，纠正文档中过时/错误断言

**场景**: 接手时按 AGENTS.md §1 要求执行 `git status` 与只读侦察，核对 `docs/STATUS_TRACKER.md` / `REALITY_CHECK.md` / `ISSUES_REALITY.md` 对现状的断言。

**选项**:
- A. 直接采信文档（254 脏文件、`.env` 不存在、测试环境缺失）并据此规划。
- B. 以实际命令输出为准，记录文档与事实的差异，再规划。

**选择**: B

**理由**: AGENTS.md 明确 "Current source, tests, runtime evidence… outrank historical descriptions"。实际证据：
1. 脏文件 **313**（153 未跟踪 / 156 修改 / 4 删除），文档称 254 — 数值错误。
2. `backend/.env` **已存在**且被 git 忽略（2026-08-01 创建），文档称 "不存在" — 事实错误。
3. `.env` 中 `DATABASE_URL` 指向 **blog_v2**（非 `astra_week*`），这才是 pytest 报 `non-scratch connection refused before DBAPI` 的真实根因；文档把它归因为"文件不存在"是错误归因。
4. 连接池 diff 与文档一致（真实）。

**风险**: 若采信文档，会在"创建 .env"上做无用功，甚至**覆盖已有的含密钥 .env**（危险）。纠正后需重新定义 Q2 的真实修复动作（改 DATABASE_URL 指向测试库，或引入独立 TEST_DATABASE_URL）。

**状态**: 已记录，待用户决策确认。

---

## D002: 分类本次任务为 WORKER 模式（整体）/ 当前步骤 SOLO

**场景**: 用户明确要求 Worker 模式，并要求"每个独立修改需要独立审查者"。

**选项**:
- A. 全程 SOLO。
- B. 当前"读文档 + 建跟踪文件 + 侦察"步骤 SOLO；后续代码修复按 WORKER 模式派工。
- C. 立即批量派发所有 Worker。

**选择**: B

**理由**: 当前步骤仅只读侦察与文档创建，无 auth/data/contract 风险，目标明确可验证 → SOLO 合理。但待办修复涉及后端运行时配置（连接池、测试库指向）与前端运行时验证，属于需要独立验证的边界 → 修复阶段必须 WORKER 模式。

**后续 Worker 派发预案（待用户决策后启用）**:
| 任务 | 实施者（profile）| 独立审查者 |
|------|------------------|------------|
| Q1 连接池提交 | Senior Backend Engineer | Principal Technical Reviewer |
| Q2 测试库指向修正 | DevOps/SRE + Database Architect | QA/SDET（独立复跑 pytest）|
| Q3 `/manage` 页面加载 | Senior Frontend Engineer | QA/SDET（runtime-delivery-verifier，真实浏览器）|
| Q5 A13 TypeScript | Senior Frontend Engineer | Principal Technical Reviewer |

**风险**: 若把文档任务误升级为跨域高风险流程，会重复此前"过度规划"问题。已按比例裁剪。

**状态**: 已记录。

---

## D003: 在用户决策前保持只读，不修改任何代码/配置

**场景**: 用户明确 "在用户做决策之前…不要提前修改代码"。

**选择**: 严格遵守。仅创建 `docs/deepseek-session/` 下的跟踪文档（低风险、文档类），不改任何源码/配置/`.env`。

**理由**: AGENTS.md §5 与用户约束一致；254/313 个脏文件现场不能误触。

**风险**: 无。跟踪文档本身不进入功能路径。

**状态**: 已遵守。

---

## D004: 测试环境修复 = 迁移 scratch 库，而非改 `.env`

**场景**: 用户授权按判断执行路径 A。文档原方案是"创建/覆盖 `.env` 指向 astra_week4_ci"。

**发现**: `backend/tests/conftest.py` 安装全局守卫 `install_test_connection_guard`，拒绝任何非本地 `astra_week[34]_*` 的 PG 连接。`.env` 的 `DATABASE_URL=blog_v2` **正是被有意拒绝的目标**。改 `.env` 指向测试库还会让开发后端连到测试库。

**选项**:
- A. 覆盖 `.env` 的 DATABASE_URL（文档方案）→ 破坏开发配置，且非预期用法。
- B. 用官方 `scripts/week4-scratch-guard.py` 注入 `astra_week4_ci`，并按需迁移 scratch 库到 head。

**选择**: B

**理由**: 这是仓库设计的受支持路径。且 scratch 库停在 033，而 `main.py` 要求 `EXPECTED_ALEMBIC_REVISION="034"`，故需 `alembic upgrade head`（头不可逆护？不，034 为附加列、可降级）。迁移的是 `astra_week4_*` scratch 库（守卫允许），非生产库。

**执行**: `python3 scripts/week4-scratch-guard.py run --db-name astra_week4_ci -- … alembic upgrade head` → 033→034。

**结果**: 全量 pytest `945 passed, 9 skipped, 0 failed`。

**风险**: 仅影响本地 scratch 库；无生产/仓库文件改动。

**状态**: 完成。

---

## D005: 修复 A13（真实存在），采用最小类型修复

**场景**: `npx tsc --noEmit`（主构建）通过，但 `npm run test:typecheck`（tsconfig.test.json）报 2 个 TS2322，位于 `review-queue.test.tsx:169/219`。A13 **真实存在**，此前被"主构建通过"掩盖。

**选项**:
- A. 保留 `unknown`，在赋值处 cast `resolve as (v: unknown)=>void`（掩盖）。
- B. 用真实类型 `ReanswerResult`/`Question | PromiseLike<…>` 标注捕获的 resolve（精确），并在刻意传入的局部 fixture 调用点用 `as never`（沿用文件既有约定）。

**选择**: B

**理由**: 精确类型修正根因（参数逆变），`as never` 与文件既有 3 处约定一致，仅用于测试替身，未掩盖真实缺陷（组件只读 attempt.id / evaluation / question.id 等字段）。

**风险**: 低。可逆，仅测试文件。

**状态**: 完成并独立审查 PASS。

---

## D006: 仅提交 Q1（database.py），不提交未跟踪的测试文件

**场景**: 用户授权按判断执行，且约束 #4 要求"每个独立修复单独提交"。

**判断**: 提交 `backend/app/database.py`（Q1，用户明确讨论）。`review-queue.test.tsx` 是**未跟踪文件**（153 个 ?? 之一），提交它等于向仓库新增文件，属于更大的决定；在 313 脏文件现场下保守起见，仅在工作树保留该修复并报告。

**结果**: commit `3138812`（1 file, +8/-1）。未 push。

**风险**: A13 修复未被版本化；用户可随时 `git add` 该文件后提交。

**状态**: 完成。

---

## D007: 不擅自迁移 blog_v2，不重启运行中的 next-server

**场景**: 验证中发现两个"修复需越界"的情况：
1. 开发库 `blog_v2` 停在 **032**，而 `main.py` 要求 **034** → 后端无法启动（`RuntimeError: … expected 034; found ['032']`）。修复需对 `blog_v2` 执行迁移 033+034。
2. 运行中的 `next-server`(PID 1403) 启动于 **Sep 27**，而 `.next` 于 **Oct 13 17:27** 被重建 → 服务 HTML 引用的 chunk `3yf-qbrjn6oha.js` 在磁盘缺失 → 404 → `/manage` 卡在"加载中..."。修复需重启（并可能重建）前端服务。

**选择**: 两者都**不擅自执行**，改为记录 + 建议。

**理由**: (1) `blog_v2` 迁移属 G2/G5 数据/生产边界，AGENTS.md 要求单独显式授权；(2) 终止用户已运行 16 天的服务、且无法确证其原始启动命令/端口（`npm start` 默认 3000，实为 2025），有中断用户环境的风险。

**风险**: 若用户期望"全自动修复"，此两项会显得未完成 —— 但按仓库规则这是正确边界。

**状态**: 待用户授权。

---

## D008: 用户授予全权后，先备份再迁移 `blog_v2`，并以 launchd 为准恢复服务

**场景**: 用户"重新定义权能…拥有一切权力…包括增删改查"。

**选项**:
- A. 立刻迁移 + 重启（无备份）。
- B. 先 `pg_dump` 备份，再迁移；服务交由 launchd（KeepAlive）自然重启，不手动托管。

**选择**: B

**理由**: 即使有全权，真实数据库迁移前备份是基本数据保护。迁移走仓库设计的 `BLOG_APPROVED_MIGRATION_TARGET` 授权路径（非绕过守卫）。服务发现由 launchd 管理后，正确做法是让 launchd 重启，而非留下我自己的临时进程。

**执行/结果**:
- 备份 → `…/opencode/ds-backups/blog_v2_pre034_20261013-203155.sql`（627 KB）。
- `alembic upgrade head`：032→033→034；复核 revision=034、新表/新列存在。
- kill 陈旧前端 → launchd 自动重启（新服务读当前 `.next`，chunk 404 消失）。
- 后端由 launchd 在迁移后立即成功启动。

**风险**: 迁移为附加型（新表 + 可空列），已备份，可降级（033 downgrade 为 fail-closed）。风险低。

**状态**: 完成。

---

## D009: 提交 A13 修复（含新增未跟踪测试文件）

**场景**: 用户授予全权 + 约束 #4"每个独立修复单独提交"。A13 修复位于一个未跟踪文件。

**选择**: `git add` 该文件并单独提交 `1cb95f5`。

**理由**: 全权 + 增量提交要求；测试自洽（typecheck 0、vitest 9/9）。可 revert。

**风险**: 向仓库新增文件；若该文件本应保持未跟踪，可 `git revert 1cb95f5`。

**状态**: 完成。

---

## D010: 不改用 dev 服务器；以 launchd 生产服务为准

**场景**: 我尝试 `npm run dev` 以使用本地后端（`.env.development` → localhost:8000），但端口 2025 被 launchd 生产服务占用（EADDRINUSE）。

**选择**: 放弃 dev，沿用 launchd 的 `next start` 生产服务。

**理由**: 环境已定义 launchd 架构（前端 `next start:2025` + 后端 `uvicorn:8000` + cloudflared 隧道）。尊重既有架构优于引入并行 dev 进程。

**风险**: 生产构建把 `NEXT_PUBLIC_API_URL` 烘焙为 `https://public-api.limengyang.me`；当隧道不可用时，浏览器侧 API 调用失败（本次即如此）。这是既有架构的既存特征，非我引入。

**状态**: 完成。

