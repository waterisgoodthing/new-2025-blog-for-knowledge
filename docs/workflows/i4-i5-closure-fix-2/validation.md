# 验证记录

状态：`COMPLETE / PASS / FINAL-FIX-VERIFIED (2026-07-24)`

本文件记录执行后的实际命令、输出、测试数量、截图路径和历史运行时差异。本轮未执行迁移、部署、推送或源库写入。

## 计划验证矩阵

| 层级 | 验证 |
|---|---|
| 后端 | Dashboard/profile 定向测试；局部失败、commit、empty、rollback/close、刷新一致 |
| 前端 | Dashboard/settings 定向测试；DOM 顺序、隐藏、行动保护、empty 文案、刷新生效 |
| 类型/构建 | `npx tsc --noEmit`；必要时生产构建 |
| Python | 相关模块编译/导入检查 |
| 浏览器 | 390×844、1280×800、1440×900；管理员设置偏好后刷新 Dashboard；键盘关键路径 |
| 文档 | 测试总数、截图链接、实际 changed-file scope、`git diff --check` |

## 当前结果

最终收口证据详见 [i4-i5-closure-final-fix validation](../i4-i5-closure-final-fix/validation.md)。022 隔离目标为 `127.0.0.1:55435/pls_v2_i4_target`，只读确认 `alembic current=heads=022`。

## CF2-06 浏览器证据

生产构建：`npm run build` PASS，40/40 静态页面生成，TypeScript 构建阶段 PASS。由于 `agent-browser` CLI 未安装，使用本机 Playwright + Chrome headless 作为等价浏览器执行器；浏览器运行时通过受控 API fixture 提供管理员 profile/summary，不代表真实数据库或真实登录会话已通过。

fixture 偏好：`section_order=[activity,today,storage,stats]`、`hidden_sections=[stats]`。

| viewport | 实际 DOM section 顺序 | hidden stats | 学习行动入口 | 截图 |
|---|---|---:|---:|---|
| 390×844 | 最近活动 → 今日任务 → 系统状态 | 0 | 2 | [dashboard-preferences-390x844.png](./assets/dashboard-preferences-390x844.png) |
| 1280×800 | 最近活动 → 今日任务 → 系统状态 | 0 | 2 | [dashboard-preferences-1280x800.png](./assets/dashboard-preferences-1280x800.png) |
| 1440×900 | 最近活动 → 今日任务 → 系统状态 | 0 | 2 | [dashboard-preferences-1440x900.png](./assets/dashboard-preferences-1440x900.png) |

键盘：390×844 首次 Tab 聚焦可访问按钮“打开导航菜单”；证据截图见 [dashboard-preferences-keyboard-390x844.png](./assets/dashboard-preferences-keyboard-390x844.png)。

## 定向测试结果

- Frontend：最终定向套件 26 项通过（7 个测试文件）。
- Backend：四文件组合 17 项通过，包含 profile HTTP、attempt、lifecycle 与 Dashboard 测试；lifecycle 已修复事件循环隔离，三类局部故障已独立固化。
- Backend：默认 `blog_db` 的历史 revision 020 仍是另一运行时的 schema drift，但不代表本次已确认的 022 隔离目标，也不构成本批次阻断；未执行迁移。
- TypeScript：`npx tsc --noEmit` PASS。
- `git diff --check`：PASS。

## CF2-08 代码质量与最终决定

- 代码质量检查：`npx tsc --noEmit`、Python `compileall`、`npm run build`、`git diff --check` 均通过。
- 范围检查：未新增 migration、未部署、未推送、未写源库；既有脏工作树未回滚。
- 最终状态：`COMPLETE / PASS`。真实 022 后端组合测试已通过；浏览器证据验证了 Dashboard 偏好排序、隐藏与可缩放行为，浏览器运行使用受控 API fixture，具体限制已在上方记录。
