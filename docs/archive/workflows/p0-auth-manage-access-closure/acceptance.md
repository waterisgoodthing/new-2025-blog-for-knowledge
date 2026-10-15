# P0-AUTH 验收报告

日期：2026-07-30  
结论：`PASS / WORKSPACE GATE CLOSED BY CLEANUP`

## 范围

- `/manage` 真实管理员判定。
- 共享 `AuthGate` 的严格入口与 focus/reconnect 重新核验。
- 全部管理写路由的管理员依赖契约。
- Note create/update/delete 的匿名、失效和降权运行时权限。
- `/blog`、`/notes`、`/mistakes` 公开读取回归。
- 四类身份 × 三种尺寸真实浏览器矩阵。

## 自动化结果

- 完整前端：23 个文件、64 项测试通过。
- P0-AUTH 后端权限 + Batch 7：10 项通过。
- 其中 `test_manage_write_permissions.py`：
  - 动态覆盖 102 条受保护管理写路由；
  - 8 条明确认证/公开写 allowlist；
  - Note create/update/delete 对匿名/失效 session 为 401；
  - Note create/update/delete 对非管理员 session 为 403。
- `git diff --check`：通过。

既有噪音：

- AI 测试存在 React `act(...)` warning。
- Node/Tailwind 输出 `DEP0205`。
- AuthGate 的 jsdom focus 模拟输出 `TimeoutNaNWarning`，真实浏览器没有对应错误。

## TypeScript 与生产构建

- R1 + P0-AUTH scoped 隔离源码：
  - `npx next typegen`：通过。
  - `npx tsc --noEmit --pretty false`：通过。
  - `npm run build`：通过，40/40 页面生成。
- 主工作区：
  - TypeScript：失败。
  - 生产构建：编译成功后在 TypeScript 阶段失败。
  - 失败仅来自明确排除的未跟踪 `src/app/workspace/page.tsx`：
    - `ReviewStats.total_notes` 不存在；
    - Dayjs `fromNow` 不存在。

因此 P0-AUTH diff 本身通过构建，但工作区整体不得标 `PASS`。

## 浏览器矩阵

每个单元格均检查 `/manage` 和 `/manage/dashboard`：

| 身份 | 390×844 | 1280×800 | 1440×900 |
|---|---:|---:|---:|
| 匿名 | PASS | PASS | PASS |
| 管理员 | PASS | PASS | PASS |
| 降权用户 | PASS | PASS | PASS |
| 失效 cookie | PASS | PASS | PASS |

行为：

- 匿名、降权和失效 cookie：`/manage` 显示登录态；`/manage/dashboard` 回到 `/manage` 登录态；不显示管理面板或 Dashboard。
- 管理员：`/manage` 显示旧管理面板；`/manage/dashboard` 显示学习 Dashboard。
- 所有尺寸无横向溢出。
- 匿名 `/blog`、`/notes`、`/mistakes` 在三尺寸均保持原路径、无登录重定向。
- 浏览器无 error；登录头像产生既有 Next.js LCP warning。

## 截图

### 匿名

- [390×844](./assets/anonymous-390x844.png)
- [1280×800](./assets/anonymous-1280x800.png)
- [1440×900](./assets/anonymous-1440x900.png)

### 管理员

- [390×844](./assets/admin-390x844.png)
- [1280×800](./assets/admin-1280x800.png)
- [1440×900](./assets/admin-1440x900.png)

### 降权用户

- [390×844](./assets/downgraded-390x844.png)
- [1280×800](./assets/downgraded-1280x800.png)
- [1440×900](./assets/downgraded-1440x900.png)

### 失效 cookie

- [390×844](./assets/invalid-cookie-390x844.png)
- [1280×800](./assets/invalid-cookie-1280x800.png)
- [1440×900](./assets/invalid-cookie-1440x900.png)

## 清理

- 临时管理员已禁用。
- 该管理员的本地测试 session 已撤销。
- 一次性凭据文件已删除。
- 浏览器会话、临时前端和两个隔离 worktree 已清理。
- 未使用 AUTH_BYPASS，未修改 JWT、Passkey、schema、migration 或 `/workspace` 原型。

## 后续 CLEANUP 收口

原验收中的主工作区构建阻断已由单独批准的
[CLEANUP 收口](../cleanup-workspace-db-revision-closure/acceptance.md) 解除：

- `/workspace` 原型按方案 A 可恢复删除。
- 主工作区 64 项前端测试、TypeScript、40 页生产构建通过。
- revision 025 在隔离 clone 完成升级/回滚/重放与权限组合验证。
- P0-AUTH 最终结论更新为 `PASS`；未部署、未推送、未迁移日常库。
