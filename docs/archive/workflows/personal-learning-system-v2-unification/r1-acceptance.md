# R1 验收记录

日期：2026-07-30  
结论：`PASS BY P0-AUTH + CLEANUP`

## 自动化验证

### TDD 与回归测试

- RED：新增 Dashboard 快捷行动测试首先因缺少“快速开始”区块失败。
- GREEN：实现四个真实入口后，测试进一步暴露可访问名称包含描述文本；补充明确 `aria-label` 后通过。
- 定向组合：

  ```text
  npm test -- --run \
    'src/app/manage/(workspace)/dashboard/dashboard-overview.test.tsx' \
    'src/app/batch7-compatibility.test.ts' \
    'src/app/manage/components/manage-sidebar.test.ts' \
    'src/app/manage/components/manage-sidebar.test.tsx' \
    'src/app/manage/components/manage-mobile-nav.test.tsx'
  ```

  结果：5 个测试文件、23 项测试通过。

- 完整前端测试：`npm test -- --run`
  - 结果：21 个测试文件、59 项测试通过。
  - 非阻断噪音：既有 AI 测试存在 React `act(...)` warning；Node 输出 `DEP0205` warning。

### TypeScript 与生产构建

- 主工作区 `npx tsc --noEmit --pretty false`：`BLOCKED`。
- 主工作区 `npm run build`：编译成功后在类型检查阶段 `BLOCKED`。
- 两项检查的首个失败都来自保留且排除于 R1 的未跟踪 `src/app/workspace/page.tsx`：
  - 第 63 行使用不存在的 `ReviewStats.total_notes`。
  - 第 126 行使用未安装/未扩展的 Dayjs `fromNow`。
- 从 `HEAD` 创建隔离 worktree，仅应用 R1 的 Dashboard 源码与测试改动，并排除未跟踪 `/workspace` 原型：
  - `npx next typegen`：通过。
  - `npx tsc --noEmit --pretty false`：通过。
  - `npm run build`：通过，40/40 页面生成完成。

该隔离结果证明 R1 diff 本身通过类型与生产构建，但不能替代主工作区总门禁；因此 R1 不标记 `PASS`。

## 真实浏览器验证

环境：

- 隔离前端：本地临时 worktree，Next.js 开发服务器。
- 本地 API：`http://localhost:8000`。
- 认证：项目 CLI 创建的一次性临时管理员，未使用 `AUTH_BYPASS`。
- 验收后：临时管理员已禁用、浏览器会话已退出、一次性凭据文件与隔离 worktree 已删除、临时前端已停止。

通过项：

- 匿名访问 `/manage/dashboard` 回退到登录入口。
- 管理员访问 `/manage/dashboard` 正常显示“快速开始”。
- 四个入口均唯一且目标正确：
  - 写笔记 → `/write-note`
  - 写博客 → `/write`
  - 图片采集 → `/manage/capture`
  - 开始复习 → `/manage/review`
- 390×844、1280×800、1440×900 均无横向溢出。
- 快捷行动可取得键盘焦点，并使用明确可访问名称。
- 管理员 Dashboard 验收阶段浏览器 console warning/error 为 0。

失败项：

- 管理员被 CLI 降权后，原会话访问 `/manage/dashboard` 会回退到 `/manage`，但旧 `/manage` 仍显示管理面板和管理操作。后端写入权限仍需独立核验；就页面边界而言，失效/非管理员会话没有安全、清晰地回到登录态。

## 截图

- [匿名 390×844](./assets/r1/anonymous-390x844.png)
- [管理员 390×844](./assets/r1/admin-390x844.png)
- [管理员 1280×800](./assets/r1/admin-1280x800.png)
- [管理员 1440×900](./assets/r1/admin-1440x900.png)
- [键盘焦点 1280×800](./assets/r1/focus-admin-1280x800.png)
- [失效管理员会话 390×844](./assets/r1/invalid-session-390x844.png)

## 门禁结论

R1-09 已执行完毕但验收为 `PARTIAL`。以下两项阻止 R1 成为 `PASS`：

1. 主工作区 TypeScript/生产构建受未跟踪 `/workspace` 原型阻断。
2. 失效/非管理员会话回退到旧 `/manage` 后仍展示管理界面。

## 2026-07-30 后续收口

- P0-AUTH 已修复第 2 项，并完成四类身份 × 三尺寸浏览器矩阵和全部管理写路由权限契约。
- CLEANUP 已按方案 A 删除第 1 项原型，主工作区 23 files / 64 tests、
  TypeScript 与 40 页生产构建直接通过。
- CLEANUP 三尺寸确认 `/workspace` 为 404，匿名管理入口与 clone 管理员 Dashboard
  均符合权限边界。
- 因此上述历史阻断均已关闭，R1 最终验收更新为 `PASS`。
