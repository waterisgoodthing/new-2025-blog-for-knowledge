# Phase 3 启动 Prompt — 给 DeepSeek

你是本仓库的前端实施智能体，任务是完成 UI 重构 **Phase 3：Navigation 重构**（VSC-09 至 VSC-13）。只做 Phase 3，做完停下汇报。

## 0. 开工前必读

1. 先读 `AGENTS.md`（仓库强制规则），再读：
   - `docs/current/ui-technical-specification/04-execution/task-registry.md`（唯一执行清单，Phase 3 章节）
   - `docs/current/ui-technical-specification/04-execution/acceptance-criteria.md`
   - `docs/current/ui-technical-specification/02-to-be/design-foundations.md`
   - `docs/current/workflows/visual-system-consolidation/design.md` 第 3 节（导航架构）与 `navigation-overlay-context-actions.md`（需求来源）
2. 本项目的 Next.js 版本有破坏性变更，写代码前查 `node_modules/next/dist/docs/` 中相关指南（layout、route group、`usePathname`）。
3. 运行 `git status --short`。Phase 1（`d351efb`）和 Phase 2（`c330db8`）均已提交。若开工时有未提交改动，视为用户改动，**不要回滚、重排、格式化或覆盖**。

## 1. 现场事实（已核实，优先于文档中的描述）

- 仓库：`/Users/limengyang/2025-blog-public`，分支 `refactor/baseline`
- 基线：`npx tsc --noEmit` 0 errors；`npx vitest run` 74 files / 606 passed
- 前端：Next.js 16 + React 19 + Tailwind 4 + `motion` + `lucide-react`；测试 Vitest + `@testing-library/react`
- Token：`src/components/ui-v2/tokens.css`，只消费不改色值。品牌色 `--brand: #3db8a8`；导航用 `--nav-glass-bg` / `--nav-glass-border` / `--nav-glass-shadow` / `--nav-blur` / `--nav-active-bg` / `--nav-hover-bg`
- **不要用** `--radius-*` / `--font-*` / `--shadow-*` 自定义同名变量，这些是 Tailwind 4 主题命名空间，Phase 1 踩过坑；用 `--ui-*` / `--uiv2-*`
- `src/app/layout.tsx` 桥接变量故意没有 `|| '#fallback'`，不要加回去
- Phase 2 已有可复用基础：`src/hooks/use-overlay.ts`（`useOverlay` / `useFocusTrap` / `useZIndex` / `usePrefersReducedMotion`）、`src/components/ui-v2/Drawer.tsx`（左/右/底）、`Modal.tsx`、`ContextMenu.tsx`。MobileDrawer **必须基于现有 Drawer**，不要另写一套焦点/滚动锁逻辑
- 现有导航（真实挂载点）：
  - `src/layout/index.tsx`：桌面内页 `VerticalNav`（`!maxSM && isInnerPage`）、移动端 `MobileNav`（`maxSM && !isWrite`），首页 `NavCard`
  - `src/app/manage/(workspace)/layout.tsx`：`AuthGate` + `ManageSidebar` + `ManageTopbar` + `ManageMobileNav`
  - 相关测试：`mobile-nav.test.tsx`、`manage-sidebar.test.ts(x)`、`manage-mobile-nav.test.tsx`
- 导航目的地清单以现有组件里的链接为准（`vertical-nav.tsx`、`mobile-nav.tsx`、`nav-card.tsx`、`manage-sidebar.tsx`），**不新增、不删除、不改名任何路由**
- 前置 workflow 状态（`docs/archive/workflows/`）：
  - `public-session-state-optimization`：PSS-01～06 完成，F4 未执行
  - `route-ownership-alignment`：结论为"兼容共存 / 不切换"，**NO ROUTE IMPLEMENTATION**

## 2. 范围（按此执行，覆盖 registry 中与之冲突的描述）

registry 的 VSC-13 写的是"迁移全部 53 页、废弃 VerticalNav/MobileNav"。由于路由归属结论是"不切换"，本阶段**收窄**为：

| 任务 | 内容 | 接入范围 |
|---|---|---|
| VSC-09 PublicTopNav | 初始悬浮 → 滚动后 sticky 玻璃条；Dropdown（基于 Popover 语义：click 展开、方向键、Esc、外部点击关闭）；`@supports not (backdrop-filter)` 降级为 95% 实色 | 只做组件 + `/dev/nav` 预览页 |
| VSC-10 AdminSidebar | 232px ↔ 64px 点击折叠；折叠态有 `aria-label`/tooltip；激活态 `--nav-active-bg` + 4px `--brand` 左边条；折叠状态 localStorage 记忆（try/catch 包裹） | **接入** `manage/(workspace)/layout.tsx`，替换 `ManageSidebar` 的渲染 |
| VSC-11 MobileDrawer | 基于 `ui-v2/Drawer`，右侧滑入，导航链接 + 激活态；路由变化后自动关闭 | **接入** manage 移动端，替换 `ManageMobileNav` 的渲染；公开端只在 `/dev/nav` 预览 |
| VSC-12 AppShell | 扩展现有 `ui-v2/AppShell.tsx`：`variant: 'public' \| 'admin'` 由调用方显式传入（**不要**用 pathname 猜测权限）；提供统一 portal 根节点；overlay 打开时对 portal 之外的 app 根设置 `inert`（Phase 2 遗留项） | manage workspace 使用 `variant='admin'` |
| VSC-13 路由接入 | 只迁移 manage workspace 一个 layout | 公开端 `src/layout/index.tsx` **不动** |

**保留不删**：`vertical-nav.tsx`、`mobile-nav.tsx`、`nav-card.tsx`、`manage-sidebar.tsx`、`manage-mobile-nav.tsx` 文件本身保留（manage 的两个只是不再被 layout 渲染）。如果它们的测试因此不再适用，保留测试并让它们继续测原组件，不要删除断言。

公开端 VerticalNav/MobileNav 的切换留到单独批准（依赖 F4 和路由归属决策）。

## 3. 权限边界（必须遵守）

- `AuthGate` 留在 manage workspace layout 最外层，不移动、不弱化。前端导航显隐只是 UX，后端 `get_current_admin` 才是边界
- AdminSidebar 不新增任何 `/api/auth/me` 探测；需要会话信息时复用 `useAdminAuth` 现有调用方式
- PublicTopNav 预览里不出现管理员入口（公开端管理员控件属于 F4 范围）
- `/dev/nav` 预览页与 `/dev/tokens` 一样包在 `AuthGate` 里，放在 `src/app/dev/nav/page.tsx`（**不要**用 `_` 前缀目录，Next.js 不会生成路由）

## 4. 执行顺序

1. 先写测试再写实现（每个组件同目录 `*.test.tsx`）：
   - PublicTopNav：滚动阈值切换状态类、Dropdown 键盘（Enter/Space 打开、↑↓、Esc 关闭并还焦点）、`aria-expanded`/`aria-controls`、`aria-current="page"`
   - AdminSidebar：折叠切换、`aria-expanded`、折叠态链接仍有可访问名、激活项 `aria-current`、localStorage 不可用时不崩
   - MobileDrawer：打开/关闭、焦点陷阱（复用 Phase 2 断言方式）、路由变化关闭
   - AppShell：portal 根存在；overlay 打开时 app 根有 `inert`，关闭后移除；嵌套 overlay 只在全部关闭后移除
2. VSC-09、VSC-10、VSC-11 写入范围互不重叠，可以并行；VSC-12、VSC-13 必须在三者完成后串行
3. 每完成一项，立即更新 `task-registry.md` 对应条目的状态、证据和偏离说明

## 5. 不允许做的事

- 改后端、API 契约、鉴权逻辑、数据库
- 新增、删除、重命名、重定向任何路由（`/dev/nav` 预览页除外）
- 改 `src/layout/index.tsx`、首页 `NavCard`、`globals.css` 的 cursor 规则
- 改 `tokens.css` 色值
- 新增依赖（包括 axe-core、`@vitest/coverage-v8`、Floating UI）。原生定位不够用时先停下说明
- 删除或弱化现有测试断言
- commit、push、部署

## 6. 验收

| 检查 | 要求 |
|---|---|
| `npx tsc --noEmit` | 0 errors |
| `npx vitest run` | 全部通过，数量 ≥ 606 + 新增 |
| `npm run build` | 成功，路由表含 `/dev/nav`，其余路由与基线一致 |
| `git diff --check` | clean |
| 浏览器（真实 Chromium） | `/dev/nav`：顶部 / 滚动后两态截图，Dropdown 展开截图；`/manage/dashboard`：侧栏展开 / 折叠截图、390px 宽度下 Drawer 打开截图；键盘 Tab 走一遍记录焦点顺序 |
| 回归 | 公开页（`/`、`/blog`、`/notes`）导航与基线一致，截图对比 |

截图放 `docs/current/workflows/visual-system-consolidation/assets/phase3-*.png`。
鉴权打桩只允许拦截浏览器端的鉴权探针和 admin 接口响应，不得修改鉴权源码。

## 7. 汇报格式

按 `AGENTS.md` 第 9 节：Conclusion、Changes、Verification（贴命令和结果）、Browser evidence、Deviations、Remaining / NOT_VERIFIED。状态只能用 PASS / PARTIAL / FAIL / BLOCKED / NOT_VERIFIED / NOT_AUTHORIZED。

如果用了独立子代理审查，写明审查者身份和它报的问题；没有就写"未做独立审查"，不要用自审冒充。
