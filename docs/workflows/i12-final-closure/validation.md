# I12 验证

尚未完成；最终状态必须区分代码、隔离验证、发布资格、部署和迁移切换。
2026-07-31 更新：I10 owner gate 已通过。I11 E-05/E-06 当前为
`READY / NOT AUTHORIZED` 且未执行，因此仍不得从本状态推导生产切换或新的
最终完成结论。

## I12 independent cross-check continuation (2026-07-26)

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
- I10 owner/backfill：`PASS`。I11 E-05/E-06：`READY / NOT AUTHORIZED`；
  权威切换未执行，因此本历史路径的 F-01～F-03 不据此更新。
