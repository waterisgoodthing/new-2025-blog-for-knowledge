# P0-AUTH 管理权限回退收口修复

## 任务目标

修复管理页面对“存在会话”和“真实管理员”的混淆，确保匿名、普通用户、被降权管理员和失效 cookie 都不能进入 `/manage` 或 `/manage/dashboard` 的管理界面，同时完整审计管理写路由的后端 `get_current_admin` 或更严格保护。

## 影响域

- Frontend：`auth`、`manage`、共享基础设施。
- Backend：仅权限依赖审计与测试；只有发现真实缺口且仍在批准范围内时才允许最小修复。
- Public：`/blog`、`/notes`、`/mistakes` 只做回归验证，不改变公开读取边界。

## 当前状态

`P0-AUTH-01～09 COMPLETE / PASS / WORKSPACE GATE CLOSED BY CLEANUP`

用户已于 2026-07-30 批准 P0-AUTH 的目标、验收要求和边界，并在审阅任务组后明确回复“批准执行”，授权 P0-AUTH-01 至 P0-AUTH-09。

后续 [CLEANUP 收口](../cleanup-workspace-db-revision-closure/acceptance.md)
已删除范围外原型，并在主工作区通过 64 项前端测试、TypeScript、40 页生产构建
和三尺寸浏览器验证；原 `WORKSPACE PARTIAL` 已解除。

## 已确认现状

1. `AuthGate` 使用 `useAdminAuth()`，后者读取 `/api/auth/me` 的 `is_admin === true`；但共享 SWR 缓存的 60 秒 dedupe 和关闭 focus/reconnect revalidation 会使受保护入口不一定立即重新核验降权状态。
2. 旧 `/manage` 不使用 `AuthGate`，只把 `getMe()` 成功视为 `authenticated=true`，没有检查 `user.is_admin`。这是 R1 浏览器中降权用户仍看到旧管理面板的直接原因。
3. 后端 `get_current_admin` 会对无会话返回 401、对非管理员返回 403；当前路由枚举显示管理写路由均声明了 `get_current_admin` 或更严格的 `get_passkey_admin`，但尚缺少一个覆盖全部管理写路由的统一契约测试。
4. 当前未跟踪 `src/app/workspace/page.tsx` 有两个既有类型错误。该原型明确排除于本任务，因此主工作区 TypeScript/构建若继续失败，必须记为外部阻断；不得通过修改原型或弱化 TypeScript 配置绕过。

## 文档

- [需求](./requirements.md)
- [设计](./design.md)
- [任务清单](./tasks.md)
- [验证计划](./validation.md)
- [验收报告](./acceptance.md)
- [剩余风险](./risks.md)
- [下一轮需求](./next-requirements.md)
- [差异报告](./diff-report.md)
- [审计记录](./audit.md)
- [交接提示](./handoff-prompt.md)
