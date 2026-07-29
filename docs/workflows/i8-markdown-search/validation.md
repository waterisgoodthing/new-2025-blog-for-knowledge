# I8 验证

主实现验证（2026-07-24）：

- 隔离目标 `023→024`，`alembic current=heads=024`，`alembic check` 无新升级操作；`pg_trgm` 在隔离目标存在。
- 后端 I8 服务/路由、I7 回归、附件/题目/错题组合测试：`22 passed`；Python compileall 通过。
- 前端搜索/API 与能力状态定向测试：`3 passed`；`npx tsc --noEmit`、`git diff --check` 通过。
- I8 已覆盖真实 Note 版本、WikiLink/反链和已发布/未隐藏搜索过滤；未把模拟结果作为主数据。

独立交叉验证：待重启 revision 024 的后端与新 Playwright 会话完成；当前状态 `NOT VERIFIED`。

独立交叉验证（2026-07-24）：

- 新生产构建/新 Next 进程 + 新 Playwright context；管理员真实 API 创建两条隔离 Note，版本接口 `200/count=1`，反链接口 `200` 返回稳定 `source_note_id`、source slug/title，管理员搜索 `200/count=2`；随后删除测试 Note 并禁用临时账号。
- 搜索页三尺寸截图：`assets/390x844-admin-search.png`、`1280x800-admin-search.png`、`1440x900-admin-search.png`，每个 `scrollWidth === clientWidth`；匿名与失效会话均在 `/api/auth/me=401` 后回到 `/manage`，未请求 `/api/admin/search`。
- 390×844 页面证据显示真实搜索结果 `I8 Visible Search Evidence`；空结果与失败态分别由 UI 分支保留，未生成模拟结果。

I8 结论：`PASS`（代码、隔离 DB、API 权限、版本/WikiLink/反链、搜索 UI 与三尺寸浏览器范围）。
