# I12 验证

最终状态必须区分代码、隔离验证、发布资格、部署和迁移切换。I10 owner gate、
I11 E-05 与 E-06 live authority 已完成；下列 I12-01 证据均为 2026-08-01
最终 authority 或精确隔离 acceptance DB 上的新鲜复验。

## I12-01 / F-01 E-06 后全量验证（2026-08-01）

- Runtime：`blog_v2` revision 025、默认可写；Legacy `blog_db` revision 025、
  默认只读；health=200、公开 notes=200，LaunchAgent 恢复后应用连接仅到
  `blog_v2`。新鲜 source/target 快照与独立 SQL row/hash、owner、关系、附件、
  回滚基线见 I11 `I11-03H` 与 `I11-04` 证据。
- Backend：精确隔离 `i12_f01_acceptance_20260801` 上
  `python -m pytest tests/ -v` 为 `307 passed, 2 warnings`；warnings 是既有
  AI gateway `AsyncMock` 未 await 警告，不影响断言。隔离 DB current=head=025，
  `alembic check`=`No new upgrade operations detected`。
- Frontend：`npm test` 为 23 files/64 tests passed；`npx tsc --noEmit` PASS；
  `npm run build` 使用 `.env.production` 编译成功并生成 40/40 pages；
  `PYTHONPYCACHEPREFIX` 隔离执行 compileall PASS；`git diff --check` PASS。
- Browser：真实临时管理员、匿名、失效和非管理员会话均在同源隔离开发服务器
  完成；管理员摘要=200，非管理员摘要=403，匿名/失效=401，非管理员进入
  `/manage/dashboard` 被安全送回 `/manage`；公开读取=200。390×844、1280×800、
  1440×900 均无横向溢出，390px 键盘路径可达导航/菜单/学习操作，浏览器错误为空。
  机器证据：`assets/e06-f01-browser-matrix-20260801.json` 及同目录截图。
- 浏览器临时会话关闭、临时身份随后精确删除；未使用 `AUTH_BYPASS`，未保存密码、
  password hash、正文或 session 文件。

结论：I12-01/F-01 `PASS`。恢复/回切由 I11-03B、I11-03F 与 I11-03H 证据覆盖；
代码、隔离验证、live authority 和权限/浏览器门均已通过。

## I12-02 / F-02 部署资格审查（2026-08-01）

- 生产依赖审计 0 vulnerabilities；Next/OpenNext 依赖树有效；OpenNext Cloudflare
  build PASS（40/40 pages），仅有 compatibility date 更新建议。
- 仓库包装门 `npm run predeploy:check` 在第一项 clean-worktree 检查按设计阻断：
  `predeploy: blocked - worktree is not clean`。没有通过 commit、stash、回退用户
  改动或修改门禁绕过该结果。
- 判定：revision-025 代码、恢复、权限和构建技术候选具备未来单独授权部署资格；
  当前 exact dirty worktree 不是可部署制品，结论为 `DO NOT DEPLOY CURRENT WORKTREE`。
  形成审查过的 clean commit 并在该 commit 重跑包装门之前不得部署。
- 本任务未执行应用部署、Git push、Cloudflare 路由/配置变更或发布。

结论：I12-02/F-02 `COMPLETE`；资格边界见 I-series
`f02-deployment-eligibility.md`。

## I12-03 / I12-04 最终报告与交叉验证（2026-08-01）

- F-03 十维报告已改写为 revision-025 终态，并与 I11、I12、I-series 和主
  workflow 清单同步；2026-07-29 C8/C9 SKIPPED 文档均标注为历史基线。
- Fresh runtime 复核：health/public notes=200；`blog_v2|025|off`、
  `blog_db|025|on`；LaunchAgent running，应用连接仅 `blog_v2|blog_user`。
  隔离 `:3000` 已停止，用户既有 `:2025` 未触碰。
- 全部 workflow JSON 通过 `jq empty`；post-cleanup reconciliation、独立
  cross-validation 和 browser matrix 的 `passed=true`。immutable v1 manifest
  SHA-256 仍为 `a2d91fd48c96f4dfde15346c33b66e6ee58e581fb25dfa3258725dcd49dbbe4e`，
  121+2=123、重复 source key=0。
- 独立工具测试：I11 shadow/cutover 8/8、I-series manifest/integrity 5/5；
  临时 pycache 已移入废纸篓。敏感文件/凭据/session/dump/tar 扫描为空；
  acceptance DB catalog=0、agent-browser active sessions=0。
- `git diff --check`、`.env.production` 未修改、`.env.production.local` 不存在；
  所有 tracked 修改均位于四个批准 workflow。当前工作树仍 dirty，因此部署包装门
  继续 fail closed；这与 F-02 `DO NOT DEPLOY CURRENT DIRTY WORKTREE` 一致。

结论：I12-03/F-03 `COMPLETE`，I12-04 `PASS`。四个 workflow 已形成唯一终态；
实际应用部署与 Git push 均未执行。

## 历史记录：I12 independent cross-check continuation (2026-07-26)

以下内容保留为 dated evidence boundary，不代表 2026-08-01 终态。

本轮复核以主结论可能错误为前提，未写入源库、生产库、生产配置或权限数据。

### PASS

- 浏览器运行时：`npx --yes agent-browser doctor --offline --quick` 为 `5 pass, 1 warn, 0 fail`；使用三个全新 session 打开现有生产构建 `http://127.0.0.1:2025/manage`。
- 三尺寸截图与横向溢出：
  - [390×844](assets/cross-390-manage.png)：`innerWidth=390, scrollWidth=390`。
  - [1280×800](assets/cross-1280-manage.png)：`innerWidth=1280, scrollWidth=1280`。
  - [1440×900](assets/cross-1440-manage.png)：`innerWidth=1440, scrollWidth=1440`。
- 匿名浏览器快照只显示公开导航，不显示管理工作区；390px 会话连续 `Tab` 后焦点落在带 aria-label 的“博客”“笔记”链接，键盘路径可达。
- 新进程失效会话 API：`GET /api/auth/me` 无 cookie 与 `Cookie: admin_session=invalid-session` 均为 `401 application/json`，body 为 `{"detail":"Not authenticated"}`。
- 隔离数据库 `pls_v2_i4_target`：`alembic current=024 (head)`、`alembic heads=024 (head)`、`alembic check=No new upgrade operations detected`；异步只读身份为 `('pls_v2_i4_target','blog_user','off')`、revision `024`。
- 隔离数据库后端组合测试：
  `DATABASE_URL=postgresql+asyncpg://blog_user@127.0.0.1:55435/pls_v2_i4_target PYTHONPATH=. .venv/bin/pytest -q tests/test_i7_file_workspace.py tests/test_i7_file_workspace_routes.py tests/test_i8_markdown_search.py tests/test_i8_search_routes.py tests/test_i9_governance_routes.py` → `10 passed`。
- 前端组合测试：6 个测试文件、20 tests passed；`npx tsc --noEmit`、`npm run build`（40/40 pages）、`PYTHONPATH=. .venv/bin/python -m compileall -q app` 和 `git diff --check` 均 PASS。
- 源库安全复核使用 `BEGIN; SET TRANSACTION READ ONLY`：身份为 `blog_db/blog_user`、`transaction_read_only=on`；只读计数仍为 `notes=13, attachments=1, ai_runs=32`。

### Fresh production-server recheck

- `npm run build` 后，以新进程 `npm run start -- -p 3025` 启动独立 production server；三尺寸 session 均加载 `/manage`，静态 chunk 网络记录全部为 `200`。
- 全新 production session 的匿名页面正文包含“登录后即可管理内容”以及用户名、密码、密码登录控件；Passkey 请求失败时明确显示“无法检查 Passkey 状态：Failed to fetch。可先使用密码登录。”，属于可见失败态而非假成功。
- 新截图与几何核验：
  - [production 390×844](assets/prod-390-manage.png)：`scrollWidth=390`。
  - [production 1280×800](assets/prod-1280-manage.png)：`scrollWidth=1280`。
  - [production 1440×900](assets/prod-1440-manage.png)：`scrollWidth=1440`。
- 390px production session 的 accessibility snapshot 暴露“用户名”“密码”“密码登录”以及公开导航；连续 Tab 后焦点落在表单 input，键盘入口可达。

### PARTIAL / NOT VERIFIED

- 首次后端组合测试因遗漏隔离 `DATABASE_URL` 命中了源库 revision 020，出现缺少 `attachments.display_name`、`notes.revision` 和 `attempts` 表的失败；未据此宣称通过，随后已停止源库重试并以隔离目标重跑通过。该失败保留为验证流程缺陷证据。
- 管理员真实会话、受保护管理页面内部内容、恢复/回滚演练和失败态的完整浏览器路径：`NOT VERIFIED`；不能在源库创建临时管理员，也不能使用认证绕过替代真实会话。
- 现有 `:2025` 进程另有独立失败：网络记录显示多个 `_next/static` chunk 返回 500，页面停在“加载中”；该进程不作为 production build 通过证据，已通过新构建 `:3025` 复核替代。
- I10 owner/backfill：`PASS`。I11 E-05：`PASS`；E-06：
  `READY / NOT AUTHORIZED`。E-05 证据包含 123/123 ledger、单 owner、
  orphan=0、双扫描/幂等 replay、shadow 销毁、backend 307/307、frontend
  64/64、type/build 与 source fingerprint 不变。权威切换未执行，因此本
  历史路径的 F-01～F-03 不据此自动完成。
