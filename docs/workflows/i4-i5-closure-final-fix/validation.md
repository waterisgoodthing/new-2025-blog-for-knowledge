# 验证记录

状态：`COMPLETE / PASS / FINAL-FIX-VERIFIED (2026-07-24)`

本文件记录 FINAL-01 至 FINAL-07 的实际输出。未执行迁移、部署、推送或源库写入。

## 预期证据

- 四文件 pytest 完整输出与退出码。
- `alembic current` / `heads` 均为 `022`。
- 前端测试实际数量、`npx tsc --noEmit`、`npm run build`。
- 390×844、1280×800、1440×900 截图和 viewport 可缩放检查。
- closure-fix-2 文档同步后的最终状态。

## 实际结果

| 项目 | 结果 |
|---|---|
| 后端 lifecycle 隔离 | 单一 `asyncio.run()` 覆盖 commit、rollback、close、异常后恢复；通过 |
| 独立局部失败 | learning、activity、storage 三个独立故障回归测试；3 passed |
| viewport | 移除 `maximum-scale` / `user-scalable=no`；契约测试通过 |
| 数据库目标 | `127.0.0.1:55435/pls_v2_i4_target`；`alembic current=heads=022`，未迁移 |
| 后端组合套件 | `test_attempt_service.py`、`test_admin_profile_routes.py`、`test_dashboard_dependency_lifecycle.py`、`test_dashboard_routes.py`；17 passed |
| 前端定向套件 | 7 files、26 tests passed |
| 类型/构建 | `npx tsc --noEmit`、`npm run build`、Python `compileall`、`git diff --check` 均通过；build 生成 40/40 页面 |

前端全仓库 Vitest 另有 1 个既有、非本批次 AI capture 路由测试失败（`useRouter` 缺少 App Router 挂载）；本批次 26 项定向范围全部通过，未扩大范围修复该无关失败。

## 浏览器证据

生产构建下使用本机 Playwright + Chrome headless，并以受控 API fixture 注入管理员 profile/summary，验证真实 Dashboard DOM 对偏好契约的响应；这部分不是独立登录会话的身份认证证明。fixture 为 `section_order=[activity,today,storage,stats]`、`hidden_sections=[stats]`。

三种 viewport 均得到 `最近活动 → 今日任务 → 系统状态`，统计区块不存在，viewport 为 `width=device-width, initial-scale=1`，无横向溢出；390×844 首次 Tab 聚焦“打开导航菜单”。截图位于：

- [390×844](./assets/dashboard-390x844.png)
- [1280×800](./assets/dashboard-1280x800.png)
- [1440×900](./assets/dashboard-1440x900.png)
- [键盘 390×844](./assets/dashboard-keyboard-390x844.png)

## 最终决定

本批次 `FINAL-01` 至 `FINAL-07` 均完成，状态为 `COMPLETE / PASS`。closure-fix-2 的历史 020 记录仅表示默认 `blog_db` 运行时曾存在 schema drift，不再作为本次 022 隔离目标的阻断结论。
