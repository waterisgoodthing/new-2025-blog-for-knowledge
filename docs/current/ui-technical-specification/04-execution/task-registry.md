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
| VSC-03 | 实现 useOverlay Hook | 2 | 4h | P0 | - | 📋 待执行 |
| VSC-04 | 重构 Modal/Drawer | 2 | 6h | P0 | VSC-03 | 📋 待执行 |
| VSC-05 | 重构 ContextMenu | 2 | 4h | P0 | VSC-03 | 📋 待执行 |
| VSC-06 | 试点接入 — Dashboard | 2 | 8h | P0 | VSC-04 | 📋 待执行 |
| VSC-07 | 试点接入 — Notes | 2 | 6h | P0 | VSC-04 | 📋 待执行 |
| VSC-09 | 实现 PublicTopNav | 3 | 8h | P0 | VSC-02-D | 📋 待执行 |
| VSC-10 | 实现 AdminSidebar | 3 | 8h | P0 | VSC-02-D | 📋 待执行 |
| VSC-11 | 实现 MobileDrawer | 3 | 6h | P0 | VSC-04 | 📋 待执行 |
| VSC-12 | 更新 AppShell | 3 | 4h | P0 | VSC-09,10,11 | 📋 待执行 |
| VSC-13 | 迁移路由 | 3 | 10h | P0 | VSC-12 | 📋 待执行 |
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
- [ ] 单元测试覆盖
- [ ] TypeScript 类型完整

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
- [ ] axe-core 检测通过
- [ ] 键盘导航测试
- [ ] 组件测试

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
- [ ] axe-core 检测通过
- [ ] 键盘导航测试
- [ ] 边界位置测试

**工时**：4h

---

### VSC-06：试点接入 — Dashboard

**文件**：`src/app/dashboard/page.tsx`

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
- [ ] 功能回归测试
- [ ] 视觉验证（截图对比）
- [ ] 响应式验证
- [ ] TypeScript 0 errors

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
- [ ] 功能回归测试
- [ ] 视觉验证
- [ ] 响应式验证

**工时**：6h

---

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
- [ ] 滚动行为测试
- [ ] 浏览器兼容（Chrome/Safari/Firefox）
- [ ] 键盘导航
- [ ] axe-core 检测

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
- [ ] 展开/收缩动画流畅
- [ ] 键盘导航
- [ ] axe-core 检测

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
- [ ] 真机测试（iOS/Android）
- [ ] 焦点管理
- [ ] axe-core 检测

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
- [ ] 路由切换测试
- [ ] 响应式测试

**工时**：4h

---

### VSC-13：迁移路由

**文件**：所有 `src/app/**/layout.tsx`

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
- [ ] 全量功能回归测试
- [ ] 视觉验证
- [ ] 响应式验证

**工时**：10h

---

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
