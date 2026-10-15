# R1 后续需求建议

日期：2026-07-30  
状态：`PROPOSED / NOT AUTHORIZED`

## P0：管理权限回退收口（已执行）

状态：`FUNCTIONAL PASS / 见 P0-AUTH workflow`

目标：非管理员或失效管理员会话不得看到旧管理面板。

最小验收：

1. `/manage` 与 `/manage/dashboard` 对匿名、管理员、普通用户、失效 cookie 的页面行为有明确矩阵。
2. 管理页面级保护检查真实管理员身份，而不只检查“存在会话”。
3. 所有创建、更新、删除接口继续由后端 `get_current_admin` 保护。
4. 公开博客、笔记、错题列表和详情不被封闭。
5. 真实浏览器覆盖正常管理员、降权会话和登出会话。

执行证据：[P0-AUTH 验收报告](../p0-auth-manage-access-closure/acceptance.md)。

## P0：决定未跟踪 `/workspace` 原型归属

状态：`COMPLETED BY CLEANUP / ARCHIVED`

用户已选择并执行：

- 方案 A：可恢复删除该原型，不建立 redirect。
- 主工作区测试、TypeScript、生产构建和三尺寸 404 验证通过。

## P1：R2 内容创建入口适配与编辑器能力去重

依据 [R1 内容创建与编辑能力矩阵](./r1-content-editor-capability-matrix.md)，以既有真实路由为基线：

1. 先冻结 note/blog/mistake 的创建、编辑、发布与权限契约。
2. 统一可共享的编辑器能力，但不混淆三类内容的领域字段和后端 DTO。
3. 保留旧路由兼容期，另设调用方清零和删除门禁。
4. 本任务需要新的 design/requirements/tasks 并再次获得明确批准。
