# Phase 2 启动 Prompt — 给 DeepSeek

你是本仓库的前端实施智能体，任务是完成 UI 重构 **Phase 2：Overlay 加固 + 试点接入**（VSC-03 至 VSC-07）。只做 Phase 2，做完停下汇报。

## 0. 开工前必读

1. 先读 `AGENTS.md`（仓库强制规则），再读：
   - `docs/current/ui-technical-specification/04-execution/task-registry.md`（唯一执行清单，以它为准）
   - `docs/current/ui-technical-specification/04-execution/acceptance-criteria.md`
   - `docs/current/ui-technical-specification/02-to-be/design-foundations.md`
   - `docs/current/workflows/visual-system-consolidation/navigation-overlay-context-actions.md`（Overlay 职责边界的需求来源）
2. 本项目的 Next.js 版本有破坏性变更，写代码前查 `node_modules/next/dist/docs/` 中相关指南。
3. 运行 `git status --short`。Phase 1 已单独提交（品牌色统一为 `#3db8a8`，Token Demo 在 `src/app/dev/tokens/page.tsx`，访问 `/dev/tokens`）。若开工时仍有未提交改动，视为用户改动，**不要回滚、重排、格式化或覆盖**。

## 1. 现场事实（已核实，优先于文档中的描述）

- 仓库：`/Users/limengyang/2025-blog-public`，分支 `refactor/baseline`
- 前端：Next.js 16 + React 19 + Tailwind 4 + `motion`；测试用 Vitest（`vitest.config.ts`）+ `@testing-library/react`
- Token：`src/components/ui-v2/tokens.css` 已是统一双表面系统（`--brand` / `--editorial-*` / `--admin-*` / `--nav-*` / `--uiv2-*`），只消费，不改色值
- `src/app/layout.tsx` 的桥接变量**故意没有** `|| '#fallback'`，否则会压掉暗色模式。不要加回去
- 文档路径修正：
  - Dashboard 实际路径是 `src/app/manage/(workspace)/dashboard/page.tsx`，不是 `src/app/dashboard/page.tsx`
  - Notes 列表：`src/app/notes/page.tsx`
- 现有 Overlay 组件：`src/components/dialog-modal.tsx`、`src/components/drawer.tsx`、`src/components/context-menu.tsx`，共约 18 处消费者
- UI V2 现有组件：`src/components/ui-v2/`（AppShell、Card、Button、Badge、PageHeader、Skeleton、ErrorState、PageStateView 等，经 `index.ts` 导出）
- **没有安装 axe-core**。新增依赖需要用户批准，见第 3 节

## 2. 任务（严格串行，每项完成后更新 task-registry.md 状态再开始下一项）

### VSC-03 Overlay 行为测试 + `useOverlay`
- 先写测试，再写实现
- 新建 `src/hooks/use-overlay.ts`（文件名沿用仓库 kebab-case 习惯），组合焦点管理（进入焦点、Tab 约束、关闭后焦点恢复）、Esc 关闭、滚动锁定、层级（z-index 栈）、`prefers-reduced-motion`
- 测试覆盖：role/label、初始焦点、焦点约束、焦点恢复、Escape、遮罩点击、滚动锁定、嵌套层级
- 不得为了让测试通过而删除可访问性断言

### VSC-04 Modal / Drawer
- 新建 `src/components/ui-v2/Modal.tsx`、`src/components/ui-v2/Drawer.tsx`，使用 `useOverlay`，从 `ui-v2/index.ts` 导出
- Modal：`role="dialog"`、`aria-modal`、`aria-labelledby`/`aria-describedby`，尺寸变体（确认 / 短表单 / 沉浸预览），遮罩关闭可配置
- Drawer：左 / 右 / 底三方向，Header/Body/Footer 结构，视口安全区
- 动画用 `motion`，遵守 reduced-motion
- **不迁移**现有 `dialog-modal.tsx` / `drawer.tsx` 的 18 处消费者（那是 Phase 4 的事），旧组件保持原样可用

### VSC-05 ContextMenu
- 新建 `src/components/ui-v2/ContextMenu.tsx`，使用 `useOverlay`
- `role="menu"` / `menuitem`，↑↓、Home/End、Enter、Escape，`Shift+F10` 和 Menu 键打开，边缘自动翻转，关闭后焦点恢复，支持禁用项和危险分组
- 右键只是快捷入口，必须同时提供"更多"按钮入口
- 不得全局拦截浏览器原生 `contextmenu`；文本、输入框、链接、代码、图片上保留原生菜单

### VSC-06 试点：Dashboard（admin 表面）
- 文件：`src/app/manage/(workspace)/dashboard/page.tsx` 及其路由内组件
- 换用 UI V2 Card/Button/Badge/PageHeader 和 `--admin-*` token；页内弹窗换成 UI V2 Modal
- 数据流、接口调用、权限逻辑一律不动

### VSC-07 试点：Notes 列表（editorial 表面）
- 文件：`src/app/notes/page.tsx` 及其路由内组件
- 换用 UI V2 组件和 `--editorial-*` token；卡片网格桌面 3 列 / 平板 2 列 / 手机 1 列
- 数据流、接口调用、公开/私有可见性不动

## 3. 边界（违反任一条立即停止并汇报）

- 不改后端、API 合约、认证/授权、路由归属，不新增或删除路由
- 不改 `tokens.css` 色值、`layout.tsx` 桥接逻辑、`globals.css` 的 cursor 规则（cursor 问题另案处理）
- 不做 Phase 3 导航（PublicTopNav / AdminSidebar / MobileDrawer / AppShell 切换）
- **不新增依赖**。acceptance 里的 "axe-core 检测" 先用 Vitest 里的 role/aria/键盘断言替代；如果你认为必须引入 axe 类库，停下，报告包名、精确版本、体积和理由，等用户批准
- 不 commit、不 push、不 merge、不部署
- 不做顺手重构、依赖升级、文件搬迁

## 4. 验证（每项任务完成后都要跑）

```bash
npx tsc --noEmit
npx vitest run <本项相关测试>
```

Phase 2 全部完成后再跑：

```bash
npx vitest run
npm run build
git diff --check
```

- jsdom 测试不能证明真实浏览器行为。VSC-06/07 需要在 `npm run dev`（端口 2025，可能已被 launchd 服务占用，直接使用现有服务）下用真实浏览器检查桌面和手机宽度，附截图或明确写 `NOT_VERIFIED`
- 任何失败如实报告，不得通过跳过测试、`@ts-ignore`、放宽断言来"通过"

## 5. 最终汇报格式

先给结论，状态只能是 `PASS` / `PARTIAL` / `FAIL` / `BLOCKED` / `NOT_VERIFIED`，然后：

- **Changes**：按任务列出新增/修改的文件
- **Verification**：每条命令及结果（通过数/失败数）
- **Browser evidence**：VSC-06/07 的真实浏览器检查结果
- **Deviations**：与 task-registry 不一致的地方及原因
- **Remaining / Decision Needed**：未完成项、需要用户决定的事（例如是否引入 axe 依赖）

同时更新 `task-registry.md` 中 VSC-03 至 VSC-07 的状态和证据。
