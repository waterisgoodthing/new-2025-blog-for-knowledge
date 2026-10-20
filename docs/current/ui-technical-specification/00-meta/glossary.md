# Glossary — 术语表

**目的**：统一文档和代码中的术语，避免歧义。

---

## 系统与架构

| 术语 | 定义 | 别名 | 示例 |
|------|------|------|------|
| **Token** | 设计系统的最小单位，CSS 变量形式的设计决策 | Design Token | `--brand: #3db8a8;` |
| **Token 系统** | 完整的 Token 集合，包括 color/spacing/radius/shadow 等 | Design System | `ui-v2/tokens.css` |
| **双表面系统** | Editorial（公开阅读）+ Admin（管理工具）两套视觉语言 | Dual-Surface | - |
| **UI V2** | 新 UI 组件系统，基于 `src/components/ui-v2/` | - | `UI V2 Card` |
| **Legacy** | 旧 UI 组件系统，基于 `src/components/` | - | `Legacy Button` |
| **AppShell** | 应用外壳，包含 navigation + main content | - | `<AppShell>{children}</AppShell>` |

---

## 视觉设计

| 术语 | 定义 | 别名 | 示例 |
|------|------|------|------|
| **Editorial** | 公开阅读表面，warm/generous/content-first | Editorial Whitespace | Warm beige 背景 + brick red |
| **Admin** | 管理工具表面，cool/dense/utility | Cool Utility | Cool white 背景 + teal |
| **Liquid Glass** | 半透明玻璃效果，用于 navigation/overlay | Glass Morphism | `backdrop-filter: blur(20px)` |
| **Brick Red** | Editorial 强调色 `#b85e4c` | Editorial Accent | 序号、标签 |
| **Teal** | 品牌色系 `#3db8a8` | Brand, Cyan-Teal | 按钮、active state |
| **Warm Beige** | Editorial 背景色 `#f5f1eb` | Editorial BG | 公开阅读页面底色 |
| **Cool White** | Admin 背景色 `#ffffff` | Admin Surface | 管理页面卡片 |

---

## 组件

| 术语 | 定义 | 别名 | 示例 |
|------|------|------|------|
| **Overlay** | 覆盖在主内容上的浮层，包括 Modal/Drawer/Popover/ContextMenu | - | - |
| **Modal** | 阻断式对话框，焦点陷阱 | Dialog | 确认删除弹窗 |
| **Drawer** | 侧边滑入面板 | Sidebar Panel | Mobile 导航 |
| **Popover** | 轻量浮层，非阻断 | - | Tooltip、Dropdown |
| **ContextMenu** | 右键菜单 | Right-click Menu | 右键操作菜单 |
| **Navigation** | 导航系统，包括 topbar/sidebar/drawer | Nav | - |
| **PublicTopNav** | 公开页面顶部导航（glass） | Public Navigation | Blog/Notes 顶栏 |
| **AdminSidebar** | 管理页面侧边栏（collapsible） | Admin Navigation | Dashboard 左侧栏 |
| **MobileDrawer** | 移动端抽屉导航 | Mobile Navigation | Mobile 右侧滑入 |

---

## 技术术语

| 术语 | 定义 | 别名 | 示例 |
|------|------|------|------|
| **焦点陷阱** | 焦点限制在 overlay 内，Tab 循环 | Focus Trap | Modal 打开时 |
| **焦点管理** | 控制焦点进入、移动、恢复 | Focus Management | `useFocusTrap` |
| **ARIA** | 无障碍富互联网应用，语义标注 | Accessible Rich Internet Applications | `role="dialog"` |
| **WCAG** | Web 内容无障碍指南 | Web Content Accessibility Guidelines | WCAG 2.2 AA |
| **axe-core** | 无障碍自动化检测工具 | - | Chrome 插件 |
| **Lighthouse** | Google 性能/无障碍检测工具 | - | Chrome DevTools |
| **Backdrop Filter** | 背景模糊效果（CSS 属性） | - | `backdrop-filter: blur(20px)` |
| **Reduced Motion** | 减少动画（无障碍偏好） | - | `prefers-reduced-motion: reduce` |

---

## 流程术语

| 术语 | 定义 | 别名 | 示例 |
|------|------|------|------|
| **Phase** | 重构阶段，包含多个任务 | - | Phase 1: Token 系统冻结 |
| **Task** | 单个可执行任务 | - | VSC-02-A: 扩展 UI V2 Token |
| **Evidence Level** | 证据等级（L1-L4） | - | L1: Verified |
| **As-Is** | 现状，当前实现 | Current State | 3 套 Token 并存 |
| **To-Be** | 目标，期望状态 | Target State | 1 套统一 Token |
| **Gap** | 差距，As-Is 与 To-Be 之间的距离 | - | Token 合并 |
| **P0/P1/P2** | 优先级（P0 最高） | Priority | P0: Token 系统冻结 |
| **验收** | 任务完成的可验证标准 | Acceptance | 构建成功 + 测试通过 |
| **回归** | 修改后功能/视觉出现非预期变化 | Regression | 功能回归测试 |
| **回滚** | 撤销变更，恢复到之前状态 | Rollback | Git revert |

---

## 项目特定术语

| 术语 | 定义 | 别名 | 示例 |
|------|------|------|------|
| **VSC** | Visual System Consolidation（视觉系统整合） | - | VSC-02 |
| **site-content.json** | Legacy 运行时配置文件 | - | 8 个 Token 变量 |
| **theme.css** | Tailwind token 定义文件（已废弃） | - | `@theme` 指令 |
| **ui-v2/tokens.css** | UI V2 token 系统 | - | 40+ Token 变量 |
| **VerticalNav** | 旧垂直导航组件（已废弃） | - | 左侧悬浮导航 |
| **MobileNav** | 旧移动端导航组件（已废弃） | - | 底部固定导航 |

---

## 常见缩写

| 缩写 | 全称 | 说明 |
|------|------|------|
| **UI** | User Interface | 用户界面 |
| **UX** | User Experience | 用户体验 |
| **a11y** | Accessibility | 无障碍（11 = 中间 11 个字母） |
| **i18n** | Internationalization | 国际化（18 = 中间 18 个字母） |
| **CSS** | Cascading Style Sheets | 层叠样式表 |
| **TS** | TypeScript | - |
| **JSX/TSX** | JavaScript/TypeScript XML | React 组件语法 |
| **API** | Application Programming Interface | 应用程序接口 |
| **CRUD** | Create, Read, Update, Delete | 增删改查 |

---

## 反模式术语（避免使用）

| ❌ 避免 | ✅ 使用 | 原因 |
|---------|---------|------|
| "新系统" | UI V2 | 不明确，容易混淆 |
| "旧系统" | Legacy | 不明确 |
| "主题" | Token 系统 | "主题"通常指 Dark/Light，Token 更准确 |
| "样式库" | Token 系统 或 组件库 | 不明确 |
| "导航栏" | PublicTopNav 或 AdminSidebar | 职责不清 |
| "弹窗" | Modal 或 Drawer | 不明确 |
| "菜单" | ContextMenu 或 Dropdown | 不明确 |

---

**更新日志**：
- 2026-10-15：初始版本
