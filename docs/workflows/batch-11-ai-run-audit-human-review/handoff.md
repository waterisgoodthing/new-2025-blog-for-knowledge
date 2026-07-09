# Handoff：Batch 11 Browser Verification Patch

> 状态：**已通过并关闭**
>
> 本文件不批准代码修改，也不进入 Batch 12。

## 阻断问题

`/manage/ai/runs` 返回 Next.js 404。当前实现只有 `/manage/ai` 页面中的
`AiRunsPanel`，没有独立 route。

复现：

```text
GET http://127.0.0.1:2025/manage/ai/runs
页面标题：404: This page could not be found.
```

## 已采取动作

- 只读检查本地服务与 workflow。
- 浏览器访问目标路由并取得 404 证据。
- 更新 validation/audit/handoff。
- 未修改业务代码、migration、Gateway、Prompt、provider 或 stream。

## 等待用户选择

### 方案 A：补齐独立页面

新增 `/manage/ai/runs`，并让 `/manage/ai` 提供清晰入口。该方案属于 P1 代码修改，
需要用户明确批准后才能实施。

### 方案 B：修改验收目标

保留现有架构，把 Browser Verification Patch 的目标路由正式改为 `/manage/ai`，
然后在管理员登录状态下继续列表、详情、筛选、decision、retry、敏感数据与公开页面
网络请求验收。

在用户选择前，RISK-B11-001 保持未关闭，Browser Verification Patch 保持阻断。

## 临时管理员补证更新（2026-07-06）

用户允许创建临时账号后，已在隔离的当前版本前后端完成以下验证：

- `/manage/ai` Run 列表加载：通过。
- 状态筛选：通过。
- Run 详情：通过。
- retry 缺 replay input：后端 409，前端明确显示错误。
- 匿名 Run API：401。
- 当前样本敏感字段检查：通过。
- 公开 `/`、`/blog`、`/notes` 未请求 Run API。

新增 P1：

- Run 列表没有分页，只请求前 30 条。

仍未验证：

- 接受/拒绝的确认、loading、成功与失败反馈。
- revision 冲突 409。

原因：当前数据库没有 pending-review Run，本轮未获授权伪造业务 Run 数据。

临时管理员已禁用，隔离服务已停止。下一步仍需用户选择：

1. 批准 P1 修复：新增 `/manage/ai/runs` 与 Run 分页；同时提供受控 pending fixture
   或测试入口完成 decision/revision 浏览器验证。
2. 正式把目标路由改为 `/manage/ai`，并单独决定是否接受无分页的当前范围。

RISK-B11-001 后续已由 Browser Fix Patch 关闭，见下方完成移交。

## Browser Fix Patch 完成移交（2026-07-06）

状态：**通过，RISK-B11-001 已关闭**。

完成内容：

- `/manage/ai/runs` 已成为独立业务 Run 审计页。
- `/manage/ai` 与独立审计页互相提供清晰入口。
- 列表 API 和前端已接入 total/limit/offset 分页，支持上一页、下一页和筛选重置。
- accept/reject 使用页面内确认；reject 支持 note；loading、成功和失败反馈齐全。
- stale revision 返回 409，并显示“该 Run 已被更新，请刷新后重试。”
- decision 序列化 500 已通过审计后 refresh 修复并补回归断言。
- 匿名 API 401，匿名页面回登录页；列表/详情未暴露受禁字段。
- `/`、`/blog`、`/notes` 浏览器访问未请求 Run API。

最终验证：

```text
backend pytest: 209 passed, 2 warnings
npx tsc --noEmit: passed
npm run build: passed
git diff --check: passed
```

验收 fixture 与临时管理员均已清理。未改 AI Gateway、Prompt Registry、provider、
stream 或 migration；未调用真实 provider；未进入 Batch 12。
