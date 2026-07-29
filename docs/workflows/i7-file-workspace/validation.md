# I7 验证

主实现验证（2026-07-24）：

- 隔离目标执行 `022→023`，`alembic current` 为 `023 (head)`，`alembic check` 为 `No new upgrade operations detected`。
- `tests/test_i7_file_workspace.py tests/test_i7_file_workspace_routes.py`：`5 passed`。

独立交叉验证：`NOT VERIFIED`。仍需新进程、组合回归、API 权限/预览、三尺寸浏览器和只读 DB 查询证据；I7 暂不能标记 PASS。

补充证据（2026-07-24）：

- 新进程只读查询确认目标数据库 `pls_v2_i4_target`、revision `023`，`attachments` 存在 `display_name`、`folder_id`、`trashed_at` 与状态约束；I7 服务/路由重新执行 `5 passed`。
- 后端组合主验证 `20 passed`；`compileall`、`npx tsc --noEmit`、`npm run build`（40/40）和 `git diff --check` 通过。
- 前端全量 Vitest：`18 files / 56 tests`，`55 passed / 1 failed`。失败为既有 Capture placeholder 测试缺少 App Router mock；标记 `PARTIAL`，未因本轮无关而修复。
- `agent-browser` CLI 不存在，独立生产构建浏览器三尺寸、键盘、横向溢出与真实 API 预览：`NOT VERIFIED`。
- 最终只读核对：`pls_v2_i4_target / 023`，`attachments` 计数 `1`，attachment 审计计数 `0`（测试事务均回滚）；未连接或写入源 `blog_db`。

独立浏览器交叉验证（2026-07-24）：

- Playwright 新进程、新浏览器上下文访问隔离生产构建；匿名和失效 `admin_session` 访问 `/manage/attachments` 均收到 `/api/auth/me` `401` 并回到 `/manage`。
- 管理员使用一次性隔离账号登录后，`/manage/attachments` 的 `/api/admin/attachments` 返回 `200`，显示真实附件列表、私有提示和刷新入口；账号随后已禁用。
- 390×844、1280×800、1440×900 截图已保存到 `assets/browser/`；三尺寸 `scrollWidth === clientWidth`，无 page error。

I7 结论：`PASS`（I7 范围）。全量 Vitest 的 1 项既有 Capture placeholder failure 不属于 I7 变更，保留为跨项目残余风险，不伪造为全量绿灯。
