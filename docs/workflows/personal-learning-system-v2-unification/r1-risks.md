# R1 风险与阻断项

日期：2026-07-30

## R1-RISK-01：未跟踪 `/workspace` 原型阻断主工作区门禁

状态：`RESOLVED BY CLEANUP / PASS`

- `src/app/workspace/page.tsx` 未受版本控制，R1-02 已明确保持原样。
- 当前导致主工作区 TypeScript 与生产构建失败：
  - `ReviewStats.total_notes` 不存在。
  - Dayjs `fromNow` 未扩展。
- R1 隔离 diff 已通过 TypeScript 与生产构建，但仓库整体不能据此标为健康。

处置结果：用户已单独批准 CLEANUP 方案 A。原型进入系统废纸篓，
主工作区 64 项前端测试、TypeScript、40 页生产构建和三尺寸 404 验证通过。

## R1-RISK-02：失效/非管理员会话回退到旧管理面板

状态：`RESOLVED BY P0-AUTH / FUNCTIONAL PASS`

- CLI 禁用临时管理员后，既有会话访问 `/manage/dashboard` 被回退到 `/manage`。
- 旧 `/manage` 仍显示管理面板、内容列表与编辑/删除操作。
- 本轮没有验证这些后端写操作是否能成功；不得把“界面可见”扩大描述成“后端越权已证实”。

处置结果：已由 [P0-AUTH 管理权限回退收口](../p0-auth-manage-access-closure/README.md) 完成。`/manage` 和 `AuthGate` 统一使用真实管理员判定；102 条管理写路由依赖契约、Note create/update/delete 401/403、四类身份 × 三尺寸浏览器矩阵均通过。

## R1-RISK-03：测试 warning

状态：`KNOWN / NON-BLOCKING FOR R1 DIFF`

- 完整前端测试通过，但既有 AI 测试输出 React `act(...)` warning。
- Node 输出 `DEP0205` warning。

处置要求：作为独立测试质量清理项处理，避免与权限修复或编辑器统一合并。
