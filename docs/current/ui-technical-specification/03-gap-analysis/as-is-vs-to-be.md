# Gap Analysis — As-Is vs To-Be

**现状基线**：Git HEAD `700f345` (2026-10-15)  
**目标规范**：`docs/current/workflows/visual-system-consolidation/design.md`

---

## 总览

| 维度 | 现状（As-Is） | 目标（To-Be） | 差距等级 | Phase |
|------|--------------|--------------|----------|-------|
| **Token 系统** | 3 套并存，值冲突 | 1 套统一双表面系统 | **P0** | Phase 1 |
| **UI V2 接入** | 15 组件，0 接入 | 全量接入 | **P0** | Phase 2+ |
| **Navigation** | VerticalNav + MobileNav | Glass topbar + Sidebar + Drawer | **P0** | Phase 3 |
| **Overlay** | Modal/Drawer/ContextMenu（独立） | 统一 accessibility 系统 | **P0** | Phase 2 |
| **响应式** | 部分覆盖 | 全覆盖 | **P1** | Phase 2+ |
| **无障碍** | 局部缺失 | WCAG 2.2 AA | **P1** | Phase 2+ |
| **Dark Mode** | 未实现 | 支持 | **P1** | Phase 4 |

---

## 1. Token 系统

### 现状（As-Is）

**3 套并存**：

1. **Legacy**（`site-content.json`）：8 个变量，运行时注入
2. **Tailwind**（`theme.css`）：10 个变量，与 Legacy 值冲突
3. **UI V2**（`ui-v2/tokens.css`）：40+ 变量，完整系统但零接入

**关键冲突**：

| Token | Legacy | Tailwind | UI V2 | 问题 |
|-------|--------|----------|-------|------|
| 品牌色 | `#2fcbe7` | `#35bfab` | `#35bfab` | 2 vs 1 |
| 主色 | `#5B423F` | `#334f52` | 未定义 | 完全不同 |
| 背景色 | `#d4e8f3` | `#eeeeee` | `#ffffff` | 3 套不同 |

---

### 目标（To-Be）

**1 套统一系统**（基于 UI V2 架构）：

```css
/* 双表面支持 */
--editorial-bg: #f5f1eb;
--editorial-surface: #fffef8;
--editorial-text-primary: #4a3832;
--editorial-accent: #b85e4c;

--admin-bg: linear-gradient(...);
--admin-surface: #ffffff;
--admin-text-primary: #2d3e3c;

/* 共享 */
--brand: #3db8a8;
--space-*: ...;
--radius-*: ...;
--shadow-*: ...;
```

---

### 差距

| 差距项 | 说明 | 优先级 |
|--------|------|--------|
| **Token 合并** | 废弃 theme.css，合并到 UI V2 | P0 |
| **Editorial Token** | UI V2 缺 editorial warm 表面 | P0 |
| **运行时配置桥接** | Legacy 运行时配置需桥接到新系统 | P0 |
| **Dark Mode Token** | 未定义暗色模式变量 | P1 |

---

### 执行任务

- **VSC-02**：Token 系统冻结（Phase 1）
  - 在 `ui-v2/tokens.css` 追加 editorial token
  - 更新 `layout.tsx` 使用新 token
  - 废弃 `theme.css`（合并到 UI V2）
  - Demo 页验证（`/dev/tokens`）

---

## 2. UI V2 接入

### 现状（As-Is）

- ✅ 15 个组件已实现（Card/Button/Badge/AppShell...）
- ✅ 测试覆盖完整
- ❌ **路由使用率 = 0**

**验证方法**：
```bash
grep -r "import.*from '@/components/ui-v2" src/app --include="*.tsx" | wc -l
# 结果：0
```

---

### 目标（To-Be）

- 所有管理页面使用 UI V2 组件
- 公开页面选择性使用（Editorial 风格调整后）

---

### 差距

| 差距项 | 说明 | 优先级 |
|--------|------|--------|
| **组件未接入** | 15 个组件存在但未被路由使用 | P0 |
| **Editorial 风格缺失** | UI V2 只有 admin cool，缺 editorial warm | P0 |
| **AppShell 未启用** | AppShell 定义了 navigation 结构但未使用 | P0 |

---

### 执行任务

- **Phase 2 试点**：
  - 选 1-2 页接入（Dashboard 或 Notes）
  - 验证 Token + 组件集成
- **Phase 3 扩展**：
  - 剩余管理页面接入
  - 公开页面 Editorial 风格调整

---

## 3. Navigation 系统

### 现状（As-Is）

**Desktop**：
- `VerticalNav`：左侧悬浮，展开/收缩（56px → 180px）
- 样式：半透明白 + blur + teal active
- 固定在左侧（`fixed left-2`）

**Mobile**：
- `MobileNav`：底部固定，5 个图标
- 样式：白色背景 + teal active

---

### 目标（To-Be）

**Public Desktop**（公开阅读）：
- **Floating topbar**（初始）：半透明，页面顶部悬浮
- **Sticky glass bar + dropdown**（滚动后）：liquid glass，下拉菜单展开

**Admin Desktop**（管理工具）：
- **Collapsible sidebar**：232px → 64px
- 样式：实心白 + teal accent
- 固定在左侧

**Mobile**（统一）：
- **Sticky topbar + drawer**
- Drawer 从右侧滑入

---

### 差距

| 差距项 | 说明 | 优先级 |
|--------|------|--------|
| **架构不符** | 现有 VerticalNav 不符合设计目标 | P0 |
| **Liquid Glass 未实现** | 无 backdrop-filter 效果 | P0 |
| **Public/Admin 未区分** | 所有页面用同一套导航 | P0 |
| **Dropdown 缺失** | 无下拉菜单组件 | P0 |

---

### 执行任务

- **VSC-09-13**（Phase 3）：
  - 实现 PublicTopNav（glass + dropdown）
  - 实现 AdminSidebar（collapsible）
  - 实现 MobileDrawer
  - 更新路由使用新 navigation
  - 废弃 VerticalNav

---

## 4. Overlay 系统

### 现状（As-Is）

**独立实现**：
- `dialog-modal.tsx`：Modal
- `drawer.tsx`：Drawer
- `context-menu.tsx`：ContextMenu

**问题**：
- ❌ 无统一焦点管理
- ❌ 无统一键盘导航（Escape/Tab）
- ❌ 缺少 ARIA（role/aria-modal/aria-labelledby）
- ❌ 层级管理混乱

---

### 目标（To-Be）

**统一 Overlay 系统**：

| 组件 | 职责 | 键盘 | ARIA |
|------|------|------|------|
| **Modal** | 阻断式对话框 | Esc 关闭，Tab 焦点陷阱 | `role="dialog"`, `aria-modal="true"` |
| **Drawer** | 侧边滑入面板 | Esc 关闭 | `role="dialog"` |
| **Popover** | 轻量浮层（非阻断） | Esc 关闭 | `role="dialog"` 或 `role="menu"` |
| **ContextMenu** | 右键菜单 | 方向键导航，Esc 关闭 | `role="menu"` |

**共享逻辑**：
- 焦点管理（`useFocusTrap`）
- 键盘导航（`useKeyboardNav`）
- 层级管理（`useZIndex`）
- 动画（统一 motion variants）

---

### 差距

| 差距项 | 说明 | 优先级 |
|--------|------|--------|
| **焦点管理缺失** | Modal/Drawer 无焦点陷阱 | P0 |
| **ARIA 缺失** | ContextMenu 无 `role="menu"` | P0 |
| **职责不清** | Modal/Drawer/Popover 职责重叠 | P0 |
| **代码重复** | 3 个组件各自实现关闭逻辑 | P1 |

---

### 执行任务

- **VSC-03-05**（Phase 2）：
  - 实现统一 `useOverlay` hook
  - 实现 `useFocusTrap`
  - 重构 Modal/Drawer/ContextMenu
  - 添加 ARIA

---

## 5. 响应式覆盖

### 现状（As-Is）

**[需验证 L3]** — 需浏览器测试

**已知问题**：
- 部分组件无移动端适配
- 表格无横向滚动或卡片转换
- 某些 Modal 在小屏幕溢出

---

### 目标（To-Be）

**断点**：
```css
--breakpoint-sm: 640px;   /* Mobile */
--breakpoint-md: 768px;   /* Tablet */
--breakpoint-lg: 1024px;  /* Desktop */
--breakpoint-xl: 1280px;  /* Large Desktop */
```

**适配策略**：
- **Navigation**：Desktop sidebar → Mobile drawer
- **Table**：Desktop 表格 → Mobile 卡片
- **Modal**：Desktop 居中 → Mobile 全屏
- **Card Grid**：Desktop 3 列 → Tablet 2 列 → Mobile 1 列

---

### 差距

| 差距项 | 说明 | 优先级 |
|--------|------|--------|
| **部分组件未适配** | 需逐个验证和修复 | P1 |
| **断点不统一** | 硬编码 `maxSM` vs CSS 断点 | P1 |

---

### 执行任务

- **Phase 2+**：逐页验证和修复

---

## 6. 无障碍（Accessibility）

### 现状（As-Is）

**[需验证 L3]** — 需 axe-core 检测

**已知问题**：
- ContextMenu 无 `role="menu"`
- Modal 无 `aria-modal="true"`
- 部分按钮无 `aria-label`
- 键盘导航不完整

---

### 目标（To-Be）

**WCAG 2.2 AA 基线**：

| 类别 | 要求 | 状态 |
|------|------|------|
| **语义化 HTML** | 正确使用 `<button>`, `<nav>`, `<main>` 等 | ⚠️ 待验证 |
| **ARIA** | Role/Label/State 完整 | ❌ 缺失 |
| **键盘导航** | Tab/Shift+Tab 可达所有交互元素 | ⚠️ 待验证 |
| **焦点管理** | Modal 焦点陷阱 | ❌ 缺失 |
| **色彩对比度** | 文字 4.5:1，图形 3:1 | ⚠️ 待验证 |
| **Reduced Motion** | `prefers-reduced-motion: reduce` | ❌ 未实现 |

---

### 差距

| 差距项 | 说明 | 优先级 |
|--------|------|--------|
| **ARIA 缺失** | Modal/Drawer/ContextMenu | P0 |
| **焦点管理** | Modal 无焦点陷阱 | P0 |
| **Reduced Motion** | 未适配 | P1 |
| **自动化检测** | 无 CI axe-core | P1 |

---

### 执行任务

- **Phase 2**：Overlay ARIA + 焦点管理
- **Phase 3**：全站 axe-core 检测
- **Phase 4**：Reduced Motion 适配

---

## 7. Dark Mode

### 现状（As-Is）

❌ 未实现

---

### 目标（To-Be）

**双主题支持**：
- Editorial Dark：深棕背景 + warm white text
- Admin Dark：深青灰背景 + cool white text
- Liquid Glass Dark：深色半透明

---

### 差距

| 差距项 | 说明 | 优先级 |
|--------|------|--------|
| **Token 未定义** | 无暗色 token | P1 |
| **切换机制** | 无主题切换 UI | P1 |

---

### 执行任务

- **Phase 4**（P1）：Dark Mode 实现

---

## 优先级总结

### P0（Phase 1-2，必须完成）

1. **Token 系统冻结**（VSC-02）
2. **UI V2 试点接入**（Phase 2）
3. **Overlay 加固**（VSC-03-05）
4. **Navigation 重构**（VSC-09-13）

### P1（Phase 3-4，重要但可延后）

1. **响应式全覆盖**
2. **无障碍全验证**
3. **Dark Mode**

### P2（后续优化）

1. **性能优化**
2. **视觉回归测试**
3. **组件文档**

---

## 下一步

阅读 `04-execution/refactoring-roadmap.md`（执行路线图）

---

**更新日志**：
- 2026-10-15：初始版本
