# Task Registry — 任务清单

**来源**：`docs/current/workflows/visual-system-consolidation/tasks.md` + Gap Analysis

---

## 任务总览

| ID | 任务名称 | Phase | 工时 | 优先级 | 依赖 | 状态 |
|----|---------|-------|------|--------|------|------|
| VSC-02-A | 扩展 UI V2 Token | 1 | 2h | P0 | - | ✅ 已完成 |
| VSC-02-B | 创建 Demo 页 | 1 | 3h | P0 | VSC-02-A | ✅ 已完成 |
| VSC-02-C | 更新全局样式 | 1 | 1h | P0 | VSC-02-A | ✅ 已完成 |
| VSC-02-D | 废弃 theme.css | 1 | 0.5h | P0 | VSC-02-C | ✅ 已完成 |
| VSC-03 | 实现 useOverlay Hook | 2 | 4h | P0 | - | ✅ 已完成 |
| VSC-04 | 重构 Modal/Drawer | 2 | 6h | P0 | VSC-03 | ✅ 已完成 |
| VSC-05 | 重构 ContextMenu | 2 | 4h | P0 | VSC-03 | ✅ 已完成 |
| VSC-06 | 试点接入 — Dashboard | 2 | 8h | P0 | VSC-04 | ✅ 已完成 |
| VSC-07 | 试点接入 — Notes | 2 | 6h | P0 | VSC-04 | ✅ 已完成 |
| VSC-09 | 实现 PublicTopNav | 3 | 8h | P0 | VSC-02-D | ✅ 已完成 |
| VSC-10 | 实现 AdminSidebar | 3 | 8h | P0 | VSC-02-D | ✅ 已完成 |
| VSC-11 | 实现 MobileDrawer | 3 | 6h | P0 | VSC-04 | ✅ 已完成 |
| VSC-12 | 更新 AppShell | 3 | 4h | P0 | VSC-09,10,11 | ✅ 已完成 |
| VSC-13 | 迁移路由 | 3 | 10h | P0 | VSC-12 | ✅ 已完成 |
| VSC-14 | 扩展接入（管理页面） | 4 | 15h | P1 | VSC-13 | 📋 待执行 |
| VSC-15 | 扩展接入（公开页面） | 4 | 10h | P1 | VSC-13 | 📋 待执行 |
| VSC-16 | Dark Mode 实现 | 4 | 8h | P1 | VSC-02-D | 📋 待执行 |
| VSC-17 | 最终验收 | 4 | 8h | P1 | VSC-14,15,16 | 📋 待执行 |

**总工时**：约 111.5 小时（14-15 工作日）

---

## Phase 1：Token 系统冻结（6.5h）

### VSC-02-A：扩展 UI V2 Token

**文件**：`src/components/ui-v2/tokens.css`

**任务**：
1. 追加 Editorial Token：
   ```css
   --editorial-bg: #f5f1eb;
   --editorial-surface: #fffef8;
   --editorial-text-primary: #4a3832;
   --editorial-text-secondary: #8b7667;
   --editorial-accent: #b85e4c;
   --editorial-border: rgba(74, 56, 50, 0.12);
   ```

2. 追加 Admin Token：
   ```css
   --admin-bg: linear-gradient(180deg, #f0fffe 0%, #f5fbfb 100%);
   --admin-surface: #ffffff;
   --admin-text-primary: #2d3e3c;
   --admin-text-secondary: #6b7b79;
   --admin-border: rgba(45, 62, 60, 0.12);
   --admin-grid: rgba(61, 184, 168, 0.04);
   ```

3. 追加 Navigation Token：
   ```css
   --nav-glass-bg: rgba(255, 255, 255, 0.8);
   --nav-glass-border: rgba(255, 255, 255, 0.3);
   --nav-glass-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
   --nav-blur: blur(20px);
   ```

4. 统一品牌色：
   ```css
   --brand: #3db8a8;  /* 从 #35bfab 调整 */
   ```

5. 保留现有 spacing/radius/shadow/duration

**验证**：
- [x] CSS 语法检查通过
- [x] TypeScript 0 errors

**工时**：2h

---

### VSC-02-B：创建 Demo 页

**文件**：`src/app/dev/tokens/page.tsx`

**任务**：
1. 创建 Demo 页面（需管理员登录）
2. 布局：
   ```
   ┌─────────────────────────────────────┐
   │  [Glass Navigation Bar - sticky]    │
   ├──────────────┬──────────────────────┤
   │              │                      │
   │  Editorial   │  Admin Utility       │
   │  (warm)      │  (cool)              │
   │              │                      │
   └──────────────┴──────────────────────┘
   ```

3. 左侧 Editorial 区：
   - 背景：`--editorial-bg`
   - 大标题 + 卡片网格
   - Brick red 序号
   - 展示 spacing/typography

4. 右侧 Admin 区：
   - 背景：`--admin-bg`
   - 表格/表单控件
   - Teal primary action
   - 展示 density/structure

5. 顶部 Glass Bar：
   - 模拟滚动切换（floating → sticky）
   - 展示 backdrop-filter 效果

**验证**：
- [x] 浏览器验证（Chrome/Safari）
- [x] 截图对比参考图
- [x] Dark/Light 切换（预留）

**工时**：3h

---

### VSC-02-C：更新全局样式

**文件**：
- `src/app/layout.tsx`
- `src/styles/globals.css`

**任务**：
1. 在 `layout.tsx` 中桥接 Legacy → UI V2：
   ```tsx
   const htmlStyle = {
     '--brand': theme.colorBrand || '#3db8a8',
     '--editorial-bg': theme.editorialBg || '#f5f1eb',
     '--admin-bg': theme.adminBg || 'linear-gradient(...)',
     // ... 其他桥接
   }
   ```

2. 更新 `globals.css` 导入顺序：
   ```css
   @import 'tailwindcss';
   @import 'katex/dist/katex.min.css';
   @import '../components/ui-v2/tokens.css';  /* 提前 */
   @import './article.css';
   ```

**验证**：
- [x] 现有页面视觉无回归
- [x] Demo 页正常显示
- [x] `npm run build` 成功

**工时**：1h

---

### VSC-02-D：废弃 theme.css

**文件**：
- `src/styles/theme.css`（删除）
- `src/styles/globals.css`（更新）

**任务**：
1. 将 `theme.css` 字体定义合并到 `ui-v2/tokens.css`
2. 删除 `theme.css`
3. 移除 `globals.css` 中的 `@import './theme.css';`

**验证**：
- [x] TypeScript 0 errors
- [x] `npm run build` 成功
- [x] 前端测试 531 passed

**工时**：0.5h

---

## Phase 2：Overlay 加固 + 试点接入（28h）

### VSC-03：实现 useOverlay Hook

**文件**：
- `src/hooks/useOverlay.ts`
- `src/hooks/useFocusTrap.ts`
- `src/hooks/useZIndex.ts`

**任务**：
1. 实现 `useFocusTrap`：
   - 捕获焦点在 overlay 内
   - Tab/Shift+Tab 循环
   - 恢复焦点到触发元素

2. 实现 `useZIndex`：
   - 管理 overlay 层级
   - 多个 overlay 叠加时正确排序

3. 实现 `useOverlay`：
   - 键盘导航（Esc 关闭）
   - 动画状态（open/close）
   - 组合 useFocusTrap + useZIndex

**验证**：
- [x] 单元测试覆盖（`src/hooks/use-overlay.test.tsx`，17 passed）
- [x] TypeScript 类型完整（无 `any`）

**实现备注**：
- 文件名按仓库 kebab-case 落地为 `src/hooks/use-overlay.ts`（单文件导出 `useOverlay` / `useFocusTrap` / `useZIndex` / `usePrefersReducedMotion`），与 prompt 一致，未按本文档早期写法拆成三个 camelCase 文件
- z-index 按嵌套深度递增（base 1300 / step 10），深度优先于类型，保证 Drawer 内打开的 Modal 位于其上层
- 已知未实现项：背景 `inert` 隔离（需要 portal 容器识别，留待 Phase 4）

**工时**：4h

---

### VSC-04：重构 Modal/Drawer

**文件**：
- `src/components/ui-v2/Modal.tsx`
- `src/components/ui-v2/Drawer.tsx`

**任务**：
1. 使用 `useOverlay` hook
2. 添加 ARIA：
   ```tsx
   <div
     role="dialog"
     aria-modal="true"
     aria-labelledby="modal-title"
     aria-describedby="modal-description"
   >
   ```

3. 焦点陷阱（自动 focus 第一个可交互元素）
4. 动画（motion variants）：
   ```tsx
   const modalVariants = {
     hidden: { opacity: 0, scale: 0.95 },
     visible: { opacity: 1, scale: 1 },
   }
   ```

5. Backdrop 点击关闭（可配置）

**验证**：
- [x] 可访问性断言通过（以 Vitest role/aria/键盘断言替代 axe-core，未引入依赖）
- [x] 键盘导航测试（`src/components/ui-v2/overlays.test.tsx`，21 passed）
- [x] 组件测试

**工时**：6h

---

### VSC-05：重构 ContextMenu

**文件**：`src/components/ui-v2/ContextMenu.tsx`

**任务**：
1. 使用 `useOverlay`
2. 添加 `role="menu"`：
   ```tsx
   <div role="menu">
     <button role="menuitem">Action 1</button>
     <button role="menuitem">Action 2</button>
   </div>
   ```

3. 方向键导航（↑↓）
4. 位置计算（避免溢出屏幕）：
   - 检测右侧/底部空间
   - 自动翻转方向

**验证**：
- [x] 可访问性断言通过（role=menu/menuitem + 键盘断言替代 axe-core）
- [x] 键盘导航测试（`src/components/ui-v2/context-menu.test.tsx`，28 passed）
- [x] 边界位置测试（`computeMenuPlacement` 纯函数：右/下翻转与双轴 clamp）

**工时**：4h

---

### VSC-06：试点接入 — Dashboard

**文件**：`src/app/manage/(workspace)/dashboard/page.tsx`（实际路径；本文档早期写作 `src/app/dashboard/page.tsx` 有误）

**任务**：
1. 替换组件：
   - Legacy Card → UI V2 Card
   - Legacy Button → UI V2 Button
   - Legacy Modal → UI V2 Modal

2. 使用 admin Token：
   ```css
   .dashboard-container {
     background: var(--admin-bg);
     color: var(--admin-text-primary);
   }
   ```

3. 保持现有功能（数据不变）

**验证**：
- [x] 功能回归测试（dashboard 目录 4 files / 22 tests passed）
- [x] 视觉验证（`assets/phase2-dashboard-desktop.png` / `phase2-dashboard-mobile.png`）
- [x] 响应式验证
- [x] TypeScript 0 errors

**实现备注**：页面内不存在弹窗，故「Modal 替换」项无对象；改用 `Uiv2PageHeader` / `Uiv2Card`×4 / `Uiv2Badge`×3 / `Uiv2Button`（新增 `href` 支持）+ `--admin-*` token。

**工时**：8h

---

### VSC-07：试点接入 — Notes 列表

**文件**：`src/app/notes/page.tsx`

**任务**：
1. 使用 UI V2 组件
2. 使用 editorial Token：
   ```css
   .notes-container {
     background: var(--editorial-bg);
     color: var(--editorial-text-primary);
   }
   ```

3. 卡片网格：
   - Desktop：3 列
   - Tablet：2 列
   - Mobile：1 列

**验证**：
- [x] 功能回归测试（`src/app/notes/page.test.tsx` 3 passed）
- [x] 视觉验证（`assets/phase2-notes-desktop.png` / `phase2-notes-mobile.png`）
- [x] 响应式验证（浏览器实测 1440→3 列 / 800→2 列 / 390→1 列）

**工时**：6h

---

---

## Phase 2 完成记录（2026-10-18）

**状态**：PASS

| 检查 | 命令 | 结果 |
|------|------|------|
| 类型 | `npx tsc --noEmit` | 0 errors |
| 测试 | `npx vitest run` | 74 files / **606 passed**（基线 531 + 新增 75） |
| 构建 | `npm run build` | 成功，44 静态页 |
| 空白 | `git diff --check` | clean |

**浏览器实测**（生产构建 + Playwright，API 打桩）：

| 页面 | 视口 | 结果 |
|------|------|------|
| `/notes` | 1440 | 3 列，editorial bg `rgb(245,241,235)`、卡片 `rgb(255,254,248)` |
| `/notes` | 800 | 2 列 |
| `/notes` | 390 | 1 列 |
| `/manage/dashboard` | 1440 | admin 渐变 `#f0fffe→#f5fbfb`，文字 `rgb(45,62,60)`，4 Card / 3 Badge / 1 Button |

**独立审查（只读子代理）后的修复**：
- Tab 陷阱可逃逸：焦点候选现在过滤 `inert` / `hidden` / `aria-hidden` / CSS 不可见 / `tabindex="-1"`（Tab 用 `tabbableOnly`，ARIA 菜单roving仍可编程聚焦）
- `initialFocusRef` 被 `getInitialFocus` 覆盖：改为显式 ref 优先
- 非 LIFO 关闭时抢焦点：仅当焦点仍属于本 overlay 才归还
- 拖拽释放到遮罩会误关（可能丢表单输入）：按 pointerdown 起点武装遮罩关闭
- 首帧 z-index 错层（backdrop 1299 < Drawer 1300）：栈提交改为 `useLayoutEffect`（SSR 安全回退）
- ContextMenu：`variant:'danger'` 未分组会被排到首位 → 按 variant 归入 danger 组；`querySelector` id 转义；移除永不执行的 exit 动画；长菜单 `max-height + overflow`
- `.uiv2-*` 为非分层 CSS，会压过 Tailwind 工具类 → `Uiv2Button` 新增 `style` 覆盖，Dashboard CTA 实测 44px、分页 32px
- Notes 搜索框补 `aria-label='搜索笔记'`

**偏离与说明**：
1. axe-core 未引入（依赖需批准），可访问性以 role/aria/键盘断言替代。
2. `useOverlay` 为单文件（kebab-case），未按本文档拆成 `useOverlay.ts`/`useFocusTrap.ts`/`useZIndex.ts`。
3. 嵌套 Tab 陷阱只由最上层 overlay 持有（portal 为兄弟节点，互不包含，否则会互相抢焦点）；已加回归测试。
4. Notes 页仍使用旧 `context-menu.tsx`（VSC-05 明确不迁移消费者，Phase 4 处理）。
5. 旧 `dialog-modal.tsx` / `drawer.tsx` 的 18 处消费者未动。
6. 浏览器验证时仓库常驻 dev 服务（:2025）因 `.next/dev` 缓存被并发写入返回 500，改用生产构建在 :3026 验证；非代码缺陷。
7. Notes 列表 API 数据在验证脚本中来自本地后端真实响应后打桩（dev server 源不在后端 CORS 白名单）。


## Phase 3：Navigation 重构（36h）

### VSC-09：实现 PublicTopNav

**文件**：`src/components/ui-v2/PublicTopNav.tsx`

**任务**：
1. Floating state（初始）：
   - 半透明白
   - 页面顶部悬浮
   - 阴影 subtle

2. Sticky glass bar（滚动后）：
   - `backdrop-filter: var(--nav-blur);`
   - 固定在顶部
   - Dropdown 菜单展开

3. Dropdown 组件：
   - Hover 或 Click 展开
   - 方向键导航
   - 动画（smooth expand）

4. 降级方案（不支持 backdrop-filter）：
   ```css
   @supports not (backdrop-filter: blur(20px)) {
     background: rgba(255, 255, 255, 0.95);
   }
   ```

**验证**：
- [x] 滚动行为测试（悬浮→sticky + 40/48px 迟滞，6 个用例）
- [x] 浏览器兼容（Chromium 实测；`@supports` 降级规则在 `public-top-nav.module.css`，Firefox 旧版未实测）
- [x] 键盘导航（Enter/Space/↑↓/Home/End/Esc + 焦点归还）
- [x] 可访问性断言（role/aria/键盘替代 axe-core；未引入依赖）

**实现备注**：`aria-expanded` + `aria-controls` + `aria-current="page"`；无管理员入口；reduced-motion 关闭过渡。预览页 `/dev/nav`。

**工时**：8h

---

### VSC-10：实现 AdminSidebar

**文件**：`src/components/ui-v2/AdminSidebar.tsx`

**任务**：
1. Collapsible 逻辑：
   - 展开：232px（图标 + 文字）
   - 收缩：64px（仅图标）
   - 动画：`transition: width 300ms var(--ease);`

2. Teal active state：
   ```css
   .nav-item.active {
     background: var(--nav-active-bg);
     border-left: 4px solid var(--brand);
   }
   ```

3. 图标 + 文字：
   - 使用 lucide-react
   - 收缩时隐藏文字（fade out）

4. 响应式：
   - Desktop：固定左侧
   - Mobile：隐藏（用 Drawer 代替）

**验证**：
- [x] 展开/收缩（232px ↔ 64px，浏览器实测；动画 300ms，reduced-motion 关闭）
- [x] 键盘导航（折叠按钮 Enter 切换；折叠后链接保留 aria-label/title）
- [x] 可访问性断言（`aria-expanded`/`aria-controls`/`aria-current`，替代 axe-core）

**实现备注**：`localStorage` 读写均 try/catch；折叠不依赖 hover。**已接入** `manage/(workspace)/layout.tsx`。

**工时**：8h

---

### VSC-11：实现 MobileDrawer

**文件**：`src/components/ui-v2/MobileDrawer.tsx`

**任务**：
1. 从右侧滑入：
   ```tsx
   const drawerVariants = {
     hidden: { x: '100%' },
     visible: { x: 0 },
   }
   ```

2. 焦点陷阱（使用 `useFocusTrap`）
3. Backdrop 点击关闭
4. Esc 关闭
5. 菜单项：
   - 导航链接
   - Teal active state

**验证**：
- [x] 焦点管理（复用 `Uiv2Drawer`；浏览器实测初始焦点进入 drawer、Esc 后回到汉堡按钮）
- [x] 路由变化自动关闭
- [ ] 真机测试（iOS/Android）——**NOT_VERIFIED**：仅 Chromium 390px 模拟
- [x] 可访问性断言（替代 axe-core）

**实现备注**：右侧 `min(320px, 86vw)`；为 `Uiv2Drawer` 增加 `id` prop 供 `aria-controls`，未复制焦点/滚动锁逻辑。**已接入** manage 移动端。

**工时**：6h

---

### VSC-12：更新 AppShell

**文件**：`src/components/ui-v2/AppShell.tsx`

**任务**：
1. 根据路由切换 navigation：
   ```tsx
   const isAdmin = pathname.startsWith('/dashboard') || pathname.startsWith('/manage');
   const NavComponent = isAdmin ? AdminSidebar : PublicTopNav;
   ```

2. Mobile 统一用 Drawer

3. 布局：
   ```tsx
   <AppShell>
     {isAdmin ? <AdminSidebar /> : <PublicTopNav />}
     <main>{children}</main>
     {isMobile && <MobileDrawer />}
   </AppShell>
   ```

**验证**：
- [x] variant 显式传入（`'public' | 'admin'`，不做 pathname 权限推断）
- [x] 统一 portal 根（`[data-uiv2-portal-root]`，位于 `[data-overlay-background-root]` 之外）
- [x] overlay 打开时背景 `inert`，嵌套计数，全部关闭后才移除
- [x] 响应式（浏览器 1440 / 390 实测）

**工时**：4h

---

### VSC-13：迁移路由

> **范围收窄（Phase 3 prompt §2 覆盖本节）**：路由归属结论为"兼容共存/不切换"，本阶段只迁移 `src/app/manage/(workspace)/layout.tsx` 一个 layout。公开端 `src/layout/index.tsx` 与 `VerticalNav`/`MobileNav` 保持不动，留待单独批准。

**文件**：`src/app/manage/(workspace)/layout.tsx`（仅此一个）

**任务**：
1. 使用新 AppShell：
   ```tsx
   import { AppShell } from '@/components/ui-v2';
   
   export default function Layout({ children }) {
     return <AppShell>{children}</AppShell>;
   }
   ```

2. 废弃 VerticalNav/MobileNav：
   - 移除导入
   - 删除旧组件调用

3. 逐页迁移（53 页）

**验证**：
- [x] manage 路由回归（布局改为 `Uiv2AppShell variant='admin'` + `AdminSidebar` + `MobileDrawer`；`AuthGate` 仍在最外层）
- [x] 视觉验证（`assets/phase3-sidebar-*.png`、`phase3-mobile-drawer.png`）
- [x] 公开端未改动（`src/layout/index.tsx`、`vertical-nav.tsx`、`mobile-nav.tsx`、`nav-card.tsx` 零 diff）
- [x] 旧组件与测试保留（`manage-sidebar.*`、`manage-mobile-nav.*` 仍在且通过）

**工时**：10h

---


---

## Phase 3 完成记录（2026-10-18）

**状态**：PASS（1 项 NOT_VERIFIED：iOS/Android 真机）

| 检查 | 命令 | 结果 |
|------|------|------|
| 类型 | `npx tsc --noEmit` | 0 errors |
| 测试 | `npx vitest run` | 77 files / **646 passed**（基线 606 + 新增 40） |
| 构建 | `npm run build` | 成功；路由表新增 `/dev/nav`，其余与基线一致 |
| 空白 | `git diff --check` | clean |

**浏览器实测**（生产构建 + Playwright，仅拦截鉴权与 admin 接口）：

| 场景 | 结果 |
|------|------|
| `/dev/nav` 顶部态 | `data-state="top"` |
| `/dev/nav` 滚动 200px | `data-state="stuck"`，height 56px、`backdrop-filter: blur(20px)`、bg `rgba(255,255,255,0.8)` |
| `/dev/nav` Dropdown | `aria-expanded="true"`，3 项（博客/笔记/错题） |
| 键盘 | 内容 → 博客 →(↓) 笔记 →(End) 错题 →(Esc) 内容 →(Tab) 探索 |
| `/manage/dashboard` 侧栏 | 232px ↔ 64px；折叠后 `aria-label`/`title` 保留；localStorage 跨刷新记忆 |
| 390px Drawer | 右侧打开；焦点进入 drawer；背景 `inert=true`；Esc 后焦点回汉堡按钮 |

**发现并修复的缺陷**（独立审查 + 浏览器实测）：
1. **overlay 被祖先 stacking context 困住（P0）**：`Uiv2AppShell` 原先把 `[data-uiv2-portal-root]` 渲染在页面树内，而公开端根布局用 `<main className='relative z-10'>` 包裹所有页面；position+z-index 形成层叠上下文，overlay 的 `z-index:1300` 无法超越兄弟节点的 legacy 导航（`z-40`/`z-50`）。表现为移动端 Drawer 的「关闭导航」页脚被底部导航遮住、不可点击。修复：`src/components/ui-v2/portal-root.ts` 把 portal host 挂到 `<body>` 下的单例节点（AppShell 挂载时确保存在，永不销毁以免 orphan），并加断言「host 必须是 body 子节点且不在 shell 子树内」。
2. **`variant` 默认 admin 属 fail-open（P0）**：省略 prop 会默认渲染管理员导航。已改为**必填**，且新增 public 变体不渲染管理员 chrome 的测试。
3. **`inert` 与焦点恢复顺序**：overlay 关闭时若先还焦点再移除背景 `inert`，`focus()` 落在 inert 子树内静默失败，焦点掉到 `<body>`。已把滚动锁/inert 副作用声明在焦点陷阱之前，并加集成回归测试。
4. 审查提出的其它非阻塞项一并修复：PublicTopNav 的 Tab 关闭导致焦点掉到 body（改为 focusout 关闭 + 链接激活即关闭）、去掉不适用的 `aria-haspopup`、品牌链接与「首页」重复 `aria-current`、AdminSidebar 折叠时的挂载动画闪烁与分组标题从 DOM 消失（改为 `sr-only`）、MobileDrawer 视口放大到桌面后不关闭。

**对 Phase 2 组件的连带改动**：
- `Modal.tsx` / `Drawer.tsx` / `ContextMenu.tsx` 的 portal 目标改为 `portal-root.ts`（无 AppShell 时回退 `document.body`，行为不变）。
- `ContextMenu` 显式 `isolateBackground: false`（非模态菜单不应把整个 app 置为 inert）。
- `Uiv2Drawer` 新增 `id` prop（供 `aria-controls`）。

**偏离与说明**：
1. VSC-13 按 prompt 收窄为仅 manage layout；公开端导航切换需单独批准。
2. VSC-10/11 组件落在 `src/components/ui-v2/`（prompt 指定），legacy `manage-sidebar.tsx`/`manage-mobile-nav.tsx` 文件与测试保留，仅不再被 layout 渲染。
3. `Uiv2Drawer` 新增 `id` prop（供 `aria-controls`），未复制 Phase 2 的焦点/滚动锁逻辑。
4. `Uiv2AppShell` 默认 slot 带了 `Uiv2Breadcrumb`，因此 manage 页面新增面包屑层级（设计文档要求管理员端有面包屑）。
5. `/dev/nav` 预览页位于 root layout 内，因此公开端 legacy `VerticalNav` 仍会出现在页面左侧。

## Phase 4：扩展接入 + 收尾（41h）

### VSC-14：扩展接入（管理页面）

**文件**：
- `src/app/manage/page.tsx`
- `src/app/write/page.tsx`
- `src/app/review/page.tsx`
- `src/app/practice/page.tsx`

**任务**：
1. 逐页替换为 UI V2 组件
2. 使用 admin 风格 Token
3. 保持现有功能

**验证**：
- [ ] 逐页功能回归测试
- [ ] 视觉验证

**工时**：15h

---

### VSC-15：扩展接入（公开页面）

**文件**：
- `src/app/blog/page.tsx`
- `src/app/mistakes/page.tsx`
- 其他公开页面

**任务**：
1. 使用 editorial 风格 Token
2. 保持现有布局
3. 替换部分组件（Card/Badge）

**验证**：
- [ ] 功能回归测试
- [ ] 视觉验证

**工时**：10h

---

### VSC-16：Dark Mode 实现

**文件**：
- `src/components/ui-v2/tokens.css`
- `src/components/ui-v2/ThemeToggle.tsx`

**任务**：
1. 定义暗色 Token：
   ```css
   @media (prefers-color-scheme: dark) {
     :root {
       --editorial-bg: #1a1311;
       --editorial-surface: #2a1f1c;
       --editorial-text-primary: #f5ebe6;
       --admin-bg: #0f1416;
       --admin-surface: #1a1f21;
       --admin-text-primary: #e8f0ee;
     }
   }
   ```

2. 实现主题切换 hook：
   ```tsx
   const { theme, setTheme } = useTheme();
   ```

3. 添加切换 UI（IconButton）

**验证**：
- [ ] Dark/Light 切换测试
- [ ] 色彩对比度验证（WCAG AA）
- [ ] localStorage 持久化

**工时**：8h

---

### VSC-17：最终验收

**任务**：
1. 全量功能回归测试
2. axe-core 全站检测
3. 视觉回归测试（截图对比）
4. 性能测试（Lighthouse）
5. 文档更新：
   - 更新 `tasks.md` 状态
   - 记录最终验收结果

**验收标准**：
- [ ] 功能回归测试 100% 通过
- [ ] axe-core 0 critical issues
- [ ] Lighthouse Performance ≥ 90
- [ ] 视觉回归 0 unintended changes
- [ ] TypeScript 0 errors
- [ ] 前端测试 531 passed
- [ ] 后端测试 958 passed

**工时**：8h

---

## 下一步

阅读 `acceptance-criteria.md`（详细验收标准）

---

**更新日志**：
- 2026-10-15：初始版本
