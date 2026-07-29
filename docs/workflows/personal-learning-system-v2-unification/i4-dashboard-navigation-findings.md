# I4 现状发现

日期：2026-07-20。以下均为实现观察，不代表 I4 已获批准。

- `/manage/dashboard` 已使用受保护的 `/api/admin/dashboard/summary`，前端已有整体 loading 和 error/retry。
- `DashboardSummary` 当前一次性返回计数、最近题目/错题/复习和系统状态；服务层将 `service`、`database` 固定为 `ok`，附件目录存在性决定 `storage`。这不足以区分局部查询不可用与经验证健康。
- `DashboardOverview` 已具备题目/错题/复习的空态文案，但没有局部 unavailable 状态；全量摘要失败时所有内容被一个整体错误状态替代。
- `ManageSidebar` 的 `navGroups` 已是桌面导航唯一配置；Capture 已在 I3 启用，但 `manageCapabilityStates.capture` 仍为 `deferred`，侧栏因此显示“后续”。
- `/manage/**` 已由工作区布局保护，Dashboard API 也依赖 `get_current_admin`。I4 必须保持这两道边界。
