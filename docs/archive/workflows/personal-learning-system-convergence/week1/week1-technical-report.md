# Week 1 技术报告：TRUSTED RUNTIME

> 执行日期：2026-09-08—09  
> 主 agent / `primary_owner` / 最终代码验收：Astra  
> 授权范围：PR-02 → PR-03 → PR-04 → Week 1 Gate；保留并重新验证 PR-01  
> 最终状态：**PASS**

## 1. 结论

Week 1 已按串行顺序完成。PR-01、PR-02、PR-03、PR-04 的实现、行为验证、独立评审和主 agent 验收均为 **PASS**；Week 1 Gate 为 **PASS**。

本次证明当前代码可以从 fresh `build:cf` 工件经 workerd production preview 运行，公共 `/notes` 可读，Note 与 Blog 的新建、编辑和发布路径可用，异步失败可见且 Retry 会真实重发请求，migration 027 可在隔离 PostgreSQL 中处理 fresh、兼容存量和不完整 schema 三类状态，前后端全量测试无新增回归。

本结论不代表代码已提交、部署或在生产环境生效。真实 `blog_db` 升级、生产 migration、部署、commit、push、merge 和 Week 2+ 均为 **NOT_AUTHORIZED**。

## 2. 状态总览

| 项目 | 实现状态 | 独立评审 | 验证结果 | Gate | 主 agent 验收 |
| --- | --- | --- | --- | --- | --- |
| PR-01 runtime smoke | PASS | PASS | PASS | PASS | PASS |
| PR-02 authoring | PASS | PASS | PASS | PASS | PASS |
| PR-03 AsyncStatePanel | PASS | PASS | PASS | PASS | PASS |
| PR-04 migration 027 | PASS | PASS | PASS | PASS（G2） | PASS |
| Week 1 | PASS | PASS | PASS | PASS | PASS |

用户授权边界：Week 1 实现与 scratch 验证为 **PASS**；生产和版本控制写操作为 **NOT_AUTHORIZED**。

## 3. 关键设计与实现

### PR-01：可阻断的 production runtime smoke

- 保留 `scripts/runtime-smoke.mjs`、15 项 Node 测试、`package.json` 命令和发布 runbook 集成。
- 以 `build:cf` + workerd preview 作为 production runtime 拓扑，没有用 `next dev` 或 `next start` 替代。
- Gate 重跑时发现 Node 26 在输出完成后仍因 fetch 连接保持进程存活；在 CLI 主入口所有异步工作完成后显式按 `process.exitCode` 退出。正向和负向运行随后分别稳定返回 0 与 1。

### PR-02：单一 ContentEditor 与写作路由收敛

- 新建 `/manage/notes`、`/manage/notes/new`、`/manage/notes/[slug]`，并完成旧 Note/Blog 写作入口和内部链接的 redirect 迁移。
- `ContentEditor` 是 Note 与 Blog 共用的唯一编辑器；`useNoteEditor` 移至 `src/hooks/`，旧路径仅保留 re-export shim。共享 `TagInput` 同样保留兼容 shim，没有复制业务逻辑。
- manage 侧边栏新增“笔记写作”，指向 `/manage/notes`。
- 保存使用串行请求和 latest-intent；成功后更新 revision，失败或 409 冲突时保留输入并允许重试。发布操作有确认流程。
- 浏览器验证发现 `router.replace` 在创建成功后触发路由重挂载，导致保存状态和焦点丢失；改为 `history.replaceState` 建立 canonical URL。
- 浏览器验证还发现祖先 `backdrop-filter` 改变移动端 fixed 抽屉的定位基准；抽屉改为 portal 到 `document.body`，打开时聚焦首个属性控件。

### PR-03：共享 AsyncStatePanel

- 新增共享 `AsyncStatePanel`，接入公共 `/notes`、Dashboard 主摘要与个人资料面板；既有 `FeatureState` 委托该组件并保留现有 deferred 兼容语义。
- 覆盖 loading、empty、error、retry；Retry 有 busy guard 和 `aria-busy`，reduced-motion 下不播放加载动画。
- 首轮真实浏览器故障注入发现重试成功后错误面板卸载，焦点落到 `BODY`；`/notes` 与 Dashboard 现在记录 retry 意图并在数据恢复后聚焦持久结果区域。
- 独立评审发现任意 `Error.message` 可能泄露内部信息。先写失败测试复现 `postgres password=secret` 泄露，再限制为可信 API 错误；普通运行时错误显示统一安全文案。

### PR-04：Guestbook migration 027 与启动 pin

- 新增单链 migration 027，`down_revision = "026"`；`backend/main.py` 的 `EXPECTED_ALEMBIC_REVISION` 更新为 `027`，LSR03 与安全契约测试同步。
- fresh 环境创建两张 guestbook 表和四个预期索引，并写入 `pr04:guest-schema:027:owned` ownership marker。
- 模拟存量环境中，只有表、列、索引和约束与当前模型精确一致时才 no-op；部分存在、结构漂移或多余索引/约束均 fail-closed。
- migration 使用 transaction advisory lock。downgrade 只删除带完整 ownership marker 的 027 自建结构；兼容存量表保持不变，marker 不完整时 fail-closed。
- 内部审查发现 PostgreSQL `COMMENT ON TABLE` 不能使用 bind 参数，以及早期校验没有拒绝额外索引/约束；已分别改为安全 literal 和精确集合校验。

## 4. 多模型协作实录

| 实际身份 | 任务 | 结果 |
| --- | --- | --- |
| Astra | 现场核对、范围与验收定版、派工、整合、浏览器和数据库验证、返工裁决、最终 Gate 与报告 | PASS |
| `opencode-go/omen-alpha` | PR-02 边界实现首选 | FAIL：两次长时间读取后均未产出实现；因工具调用效率不适合该任务停止使用，没有将其判断计入验收 |
| `opencode-go/gpt-5.6-luna` | PR-02、PR-03、PR-04 的限定实现和初测 | PASS：产出由 Astra 复核并经过独立评审与实际验证 |
| `opencode-go/qwen3.7-max` | PR-02、PR-03 独立只读代码评审与返工复核 | PASS：发现侧栏旧测试、错误详情边界等问题；返工后复核通过 |
| `gemini-3.1-pro-high`（agy） | PR-02 设计与验收覆盖审查 | PASS：提出竞态、发布重试、输入保留、canonical identity、Modal 焦点和移动抽屉风险 |
| `gemini-3.8-flash-low`（agy） | PR-02 后续代码审查 | PARTIAL：agy 泛化执行错误中止；已输出的移动抽屉焦点意见完成修复，不作为完整独立评审 |
| `gemini-3.1-pro-high`（agy） | PR-03 窄审查 | FAIL：4 分钟内无输出并超时；改由未参与实现的 qwen3.7-max 完成独立评审 |
| `gemini-3.8-flash-low`（agy） | PR-04 Database Architect 评审、最终 Week 1 Gate 只读评审 | PASS：两次均无 blocker；最终评审逐项对照 10 份原始日志 |

模型身份只说明任务分工。所有 **PASS** 均以当前代码、自动测试、真实浏览器、scratch DB 或 runtime 原始证据为依据，最终裁决由 Astra 作出。

## 5. 评审发现与关闭证据

| 发现 | 处理 | 关闭证据 |
| --- | --- | --- |
| 创建后路由替换导致状态和焦点丢失 | 使用 History API 更新 canonical URL | PR-02 Chromium 全流程 PASS |
| 移动端抽屉定位和初始焦点错误 | portal 到 `document.body` 并聚焦首控件 | 390/320/横屏/1024 视口及焦点检查 PASS |
| `manage-sidebar.test.ts` 仍断言旧导航 | 同步“笔记写作”和 `/manage/notes` | 独立复核 5 files / 17 tests PASS |
| Retry 成功后焦点落到 `BODY` | 聚焦持久结果区域 | PR-03 浏览器 9/9 PASS |
| 普通 `Error.message` 可泄露内部详情 | 增加 RED 测试并采用安全回退 | PR-03 定向 5 files / 24 tests PASS |
| migration COMMENT bind 语法错误 | 改为固定安全 literal | scratch fresh replay PASS |
| migration 未拒绝额外索引/约束 | 改为精确 schema 集合校验 | fresh/existing/partial 回放和独立评审 PASS |
| runtime smoke 输出后不退出 | 主入口显式使用最终 exit code 退出 | 单测 15/15，真实正向 exit 0、负向 exit 1 |

## 6. 验证证据

### 自动测试与静态检查

- Frontend：43 files / 395 tests **PASS**。
- Backend：显式连接 scratch@027，416 passed / 7 skipped **PASS**。
- PR-01：15/15 **PASS**。
- PR-02 定向复核：5 files / 17 tests **PASS**；manage 范围 16 files / 62 tests **PASS**。
- PR-03 定向：5 files / 24 tests **PASS**。
- PR-04 定向：24 passed **PASS**；`alembic heads` 为单一 `027`。
- `npx tsc --noEmit`、`npm run test:typecheck`、`git diff --check`：**PASS**。

### 真实浏览器与 scratch 持久化

- 浏览器运行于 fresh `build:cf` 的 workerd preview，构建时 `NEXT_PUBLIC_API_URL` 明确为 `http://scratch.localhost:8001`。
- PR-02 Chromium：19/19 **PASS**。覆盖 Note/Blog 新建和编辑、保存失败与重试、发布确认、409 乐观并发、输入保留、Modal 焦点陷阱和还焦、移动抽屉、多视口无横向溢出及 reduced-motion。
- 最新 scratch 行验证：`astra-note-mttpl009` 为 draft、revision 2、编辑正文已持久化；`astra-blog-mttpl009` 为 published、revision 4、失败重试后的正文已持久化。
- PR-03 Chromium：9/9 **PASS**。`/notes` 与 Dashboard 首次 API 503 后 Error 可见，Retry 产生第二次请求并恢复，错误消失，焦点不落到 `BODY`；reduced-motion 下 loading 无动画。
- 可视证据位于 [evidence](evidence/)；原始结果为 `/tmp/astra-week1-20260908/pr02-browser-production.log`、`pr03-browser-production.log`、`gate-authoring-db.log`。

### Migration 与 Guestbook

- fresh DB：000→027 成功，两表、四索引和 marker 在场；插入并读回 guest message 与 ban；027→026 删除 027 自建表，再升级成功。
- simulated existing DB：026 上预建精确兼容表并写入 sentinel；升级 027 和降级 026 均保留两表及数据。
- partial DB：026 上只存在一张 guest 表时，upgrade exit 1，revision 保持 026，已有表保留且缺失表未被创建。
- fresh@027 backend：`GET /api/health` 200，Guestbook `POST` 201，后续 `GET` 读到持久化 sentinel。
- 原始证据：`/tmp/astra-week1-20260908/pr04-replay.log`、`pr04-partial-upgrade.log`、`pr04-runtime-evidence.json`。

### Production runtime Gate

- fresh `NEXT_PUBLIC_API_URL=http://scratch.localhost:8001 npm run build:cf`：**PASS**；Next.js 与 OpenNext 生成 42 条路由及 workerd 工件。
- 正向 smoke：exit 0，`referenced=20 ok=20 failed=0`、`checks=23 failed=0`。
- 失效 API 负向 smoke：exit 1，20 项资产仍通过，API health 失败被准确计入 `totalFailed=1`。
- Gemini 最终独立 Gate 评审：**PASS**，0 blocker。
- 原始证据：`/tmp/astra-week1-20260908/build-cf.log`、`runtime-smoke-gate.log`、`runtime-smoke-negative.log`、`frontend-full-test.log`、`backend-full-scratch.log`、`week1-gate-gemini-review.log`。

## 7. 已知限制与执行边界

- Backend 全量 scratch 测试有 2 个既有 `test_ai_gateway.py` AsyncMock warning；Week 1 核心路径未受影响，状态为 **PARTIAL** 的维护观察项。
- 执行中曾有一次从 `backend/` 运行全量测试时遗漏显式 `DATABASE_URL` 覆盖。读取到的本地 `.env` 目标是 localhost:5432 的 `blog_v2`，不是 `blog_db`；没有运行 Alembic、DDL 或 schema 修改。该轮因数据库仍为 026、启动 pin 已为 027 而出现 24 failed / 392 passed / 7 skipped，随后立即停止依赖该结果，并在显式 scratch@027 上重跑为 416 passed / 7 skipped。测试 fixture 可能执行并清理测试行，因此这是一次执行失误；没有将其描述为生产验证。
- 没有升级或查询真实 `blog_db`，没有修改共享 PostgreSQL 权限，没有重启历史 `:8000` 服务。
- 没有删除旧写作目录、改变认证语义、扩大 API 或数据所有权边界。
- commit、push、merge、部署、发布、生产数据写入、真实数据库升级和 Week 2+：**NOT_AUTHORIZED**。

## 8. 代码完成、Gate 与生产可运行的区别

**代码完成 PASS** 表示授权范围内的源代码、迁移、测试和文档已经实现。**Week 1 Gate PASS** 表示这些改动在本地 fresh build、workerd production preview、真实 Chromium 和隔离 scratch PostgreSQL 上满足本周验收标准。

生产环境仍需要独立授权和变更流程：审查生产数据库当前 revision 与 guestbook schema、执行 027、设置正式环境变量、部署工件，再运行 post-deploy smoke。上述生产步骤均未执行，当前状态为 **NOT_AUTHORIZED**。
