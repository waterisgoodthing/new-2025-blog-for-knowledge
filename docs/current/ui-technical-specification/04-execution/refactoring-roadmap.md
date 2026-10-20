# Refactoring Roadmap — 重构路线图

**目标**：分阶段完成 UI 系统从现状到设计目标的迁移，保持功能稳定、可验证、可回滚。

---

## 总览

| Phase | 范围 | 工期 | 优先级 | 状态 |
|-------|------|------|--------|------|
| **Phase 1** | Token 系统冻结 | 2-3 天 | P0 | ✅ 用户已确认视觉路线（2026-10-17） |
| **Phase 2** | Overlay + 试点接入 | 5-7 天 | P0 | 📋 待执行 |
| **Phase 3** | Navigation 重构 | 7-10 天 | P0 | 📋 待执行 |
| **Phase 4** | 扩展接入 + 收尾 | 10-15 天 | P1 | 📋 待执行 |

**总工期**：约 24-35 天（分阶段交付）

---

## Phase 1：Token 系统冻结

**目标**：合并 3 套 Token → 1 套统一双表面系统

### 任务清单

#### VSC-02-A：扩展 UI V2 Token（2h）

**文件**：`src/components/ui-v2/tokens.css`

**内容**：
1. 追加 Editorial Token（warm beige + brick red）
2. 追加 Admin Token（cool white + teal）
3. 追加 Navigation Token（liquid glass）
4. 保留现有 spacing/radius/shadow/duration

**验证**：
- TypeScript 0 errors
- CSS 语法检查通过

---

#### VSC-02-B：创建 Demo 页（3h）

**文件**：`src/app/dev/tokens/page.tsx`

**内容**：
- 左侧：Editorial 风格示例（warm beige 背景 + brick red accent）
- 右侧：Admin 风格示例（cool white 背景 + teal accent）
- 顶部：Glass navigation bar 模拟
- Dark/Light 模式切换（预留）

**验证**：
- 浏览器验证（Chrome/Safari）
- 截图对比设计目标

---

#### VSC-02-C：更新全局样式（1h）

**文件**：
- `src/app/layout.tsx`：桥接 Legacy → UI V2
- `src/styles/globals.css`：更新导入顺序

**内容**：
```tsx
// layout.tsx
const htmlStyle = {
  '--brand': theme.colorBrand || '#3db8a8',
  '--editorial-bg': theme.editorialBg || '#f5f1eb',
  // ... 其他桥接
}
```

**验证**：
- 现有页面视觉无回归
- Demo 页正常显示

---

#### VSC-02-D：废弃 theme.css（0.5h）

**文件**：`src/styles/theme.css`

**内容**：
- 将 `theme.css` 内容合并到 `ui-v2/tokens.css`
- 删除 `theme.css`
- 更新 `globals.css` 导入

**验证**：
- `npm run build` 成功
- 前端测试 531 passed

---

### 交付物

- ✅ 统一 Token 系统（`ui-v2/tokens.css`）
- ✅ Demo 页验证（`/dev/tokens`）
- ✅ Legacy 运行时配置桥接
- ✅ `theme.css` 废弃

### 验收标准

- [x] TypeScript 0 errors（`npx tsc --noEmit`，2026-10-17）
- [ ] `npm run build` 成功 — NOT_VERIFIED
- [ ] 前端测试 531 passed — NOT_VERIFIED
- [x] Demo 页浏览器验证通过（用户口头确认满意，2026-10-17；具体查看的是 `/dev/tokens` 还是首页未记录）
- [ ] 现有页面无视觉回归 — NOT_VERIFIED（仅首页人工抽查）

### Phase 1 确认记录（2026-10-17）

- 视觉路线：以 `visual-system-consolidation/design.md` 为准，Editorial 暖 / Admin 冷 / Teal 玻璃导航三表面；用户确认满意。
- Token 收敛：`--uiv2-brand` 由 `#35bfab` 对齐为 `#3db8a8`，与 `--brand`、`--color-brand` 一致。
- Demo 路由：已迁至 `src/app/dev/tokens/page.tsx` → `/dev/tokens`（原 `_dev` 是 Next.js 私有目录不生成路由，`%5Fdev` shim 已移除；`_dev/visual-demo` 已删除）。
- 附带修复：自定义光标与导航 hover 偏移，见 [cursor-hotspot-fix](../../cursor-hotspot-fix.md)；导航 28px 补偿为估算值，属遗留项。
- 未授权事项：Phase 2 及以后（VSC-03 起）仍需单独批准。

---

## Phase 2：Overlay 加固 + 试点接入

**目标**：统一 Modal/Drawer/ContextMenu 系统，选 1-2 页接入 UI V2

### 任务清单

#### VSC-03：实现 useOverlay Hook（4h）

**文件**：`src/hooks/useOverlay.ts`

**内容**：
- 焦点管理（`useFocusTrap`）
- 键盘导航（Esc 关闭，Tab 循环）
- 层级管理（`useZIndex`）
- 动画状态（open/close）

**验证**：
- 单元测试覆盖

---

#### VSC-04：重构 Modal/Drawer（6h）

**文件**：
- `src/components/ui-v2/Modal.tsx`
- `src/components/ui-v2/Drawer.tsx`

**内容**：
- 使用 `useOverlay`
- 添加 ARIA（`role="dialog"`, `aria-modal="true"`）
- 焦点陷阱
- 动画（motion variants）

**验证**：
- axe-core 检测通过
- 键盘导航测试

---

#### VSC-05：重构 ContextMenu（4h）

**文件**：`src/components/ui-v2/ContextMenu.tsx`

**内容**：
- 使用 `useOverlay`
- 添加 `role="menu"`
- 方向键导航
- 位置计算（避免溢出屏幕）

**验证**：
- axe-core 检测通过
- 键盘导航测试

---

#### VSC-06：试点接入 — Dashboard（8h）

**文件**：`src/app/dashboard/page.tsx`

**内容**：
- 使用 UI V2 组件（Card/Badge/Button/PageHeader）
- 使用新 Token（admin 风格）
- 替换 Legacy Modal → UI V2 Modal

**验证**：
- 功能回归测试
- 视觉验证（截图对比）
- 响应式验证

---

#### VSC-07：试点接入 — Notes 列表（6h）

**文件**：`src/app/notes/page.tsx`

**内容**：
- 使用 UI V2 组件
- 使用新 Token（editorial 风格）
- 卡片网格

**验证**：
- 功能回归测试
- 视觉验证

---

### 交付物

- ✅ 统一 Overlay 系统（Modal/Drawer/ContextMenu）
- ✅ ARIA 完整
- ✅ 焦点管理
- ✅ 2 页试点接入

### 验收标准

- [ ] axe-core 0 critical issues
- [ ] 键盘导航完整
- [ ] 功能回归测试通过
- [ ] 视觉验证通过

---

## Phase 3：Navigation 重构

**目标**：实现 Public glass topbar + Admin collapsible sidebar + Mobile drawer

### 任务清单

#### VSC-09：实现 PublicTopNav（8h）

**文件**：`src/components/ui-v2/PublicTopNav.tsx`

**内容**：
- Floating state（初始）
- Sticky glass bar（滚动后）
- Dropdown 菜单
- Liquid glass 效果（backdrop-filter）

**验证**：
- 滚动行为测试
- 浏览器兼容（backdrop-filter 降级）

---

#### VSC-10：实现 AdminSidebar（8h）

**文件**：`src/components/ui-v2/AdminSidebar.tsx`

**内容**：
- Collapsible（232px → 64px）
- Teal active state
- 图标 + 文字
- 动画（smooth expand/collapse）

**验证**：
- 展开/收缩测试
- 键盘导航

---

#### VSC-11：实现 MobileDrawer（6h）

**文件**：`src/components/ui-v2/MobileDrawer.tsx`

**内容**：
- 从右侧滑入
- 焦点陷阱
- Backdrop 点击关闭

**验证**：
- 真机测试
- axe-core 检测

---

#### VSC-12：更新 AppShell（4h）

**文件**：`src/components/ui-v2/AppShell.tsx`

**内容**：
- 集成 PublicTopNav/AdminSidebar/MobileDrawer
- 根据路由切换 navigation 类型

**验证**：
- 路由切换测试

---

#### VSC-13：迁移路由（10h）

**文件**：所有 `src/app/**/layout.tsx`

**内容**：
- 使用新 AppShell
- 废弃 VerticalNav/MobileNav

**验证**：
- 全量功能回归测试
- 视觉验证

---

### 交付物

- ✅ PublicTopNav（glass + dropdown）
- ✅ AdminSidebar（collapsible）
- ✅ MobileDrawer
- ✅ 所有路由迁移

### 验收标准

- [ ] 功能回归测试通过
- [ ] 视觉验证通过
- [ ] 响应式验证通过
- [ ] axe-core 0 critical issues

---

## Phase 4：扩展接入 + 收尾

**目标**：剩余页面接入 UI V2，Dark Mode，最终验收

### 任务清单

#### VSC-14：扩展接入（剩余管理页面）（15h）

**文件**：
- `src/app/manage/page.tsx`
- `src/app/write/page.tsx`
- `src/app/review/page.tsx`
- `src/app/practice/page.tsx`

**内容**：
- 逐页替换为 UI V2 组件
- 使用 admin 风格 Token

**验证**：
- 逐页功能回归测试

---

#### VSC-15：扩展接入（公开内容页面）（10h）

**文件**：
- `src/app/blog/page.tsx`
- `src/app/mistakes/page.tsx`
- 其他公开页面

**内容**：
- 使用 editorial 风格 Token
- 保持现有布局

**验证**：
- 功能回归测试
- 视觉验证

---

#### VSC-16：Dark Mode 实现（8h）

**文件**：`src/components/ui-v2/tokens.css`

**内容**：
- 定义暗色 Token
- 实现主题切换
- 添加切换 UI

**验证**：
- Dark/Light 切换测试
- 色彩对比度验证

---

#### VSC-17：最终验收（8h）

**内容**：
- 全量功能回归测试
- axe-core 全站检测
- 视觉回归测试（Percy/Chromatic）
- 性能测试（Lighthouse）
- 文档更新

**验收标准**：
- [ ] 功能回归测试 100% 通过
- [ ] axe-core 0 critical issues
- [ ] Lighthouse Performance ≥ 90
- [ ] 视觉回归 0 unintended changes

---

## 风险与缓解

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| **Token 合并破坏现有页面** | 高 | 中 | 渐进式桥接，保留 Legacy 运行时配置 |
| **Navigation 重构回归** | 高 | 中 | 分阶段迁移，保留旧导航作为 fallback |
| **浏览器兼容（backdrop-filter）** | 中 | 低 | 降级方案（实心背景） |
| **工期延误** | 中 | 中 | 分 Phase 交付，每个 Phase 独立验收 |

---

## 回滚策略

### Phase 1
- 恢复 `theme.css`
- 恢复 `layout.tsx` 旧版本

### Phase 2-3
- 保留旧组件和导航
- 新组件通过 feature flag 控制

### Phase 4
- Git revert 到 Phase 3 完成状态

---

## 下一步

1. **阅读** `task-registry.md`（17 任务详细清单）
2. **阅读** `acceptance-criteria.md`（验收标准）
3. **选择** Phase 1 任务开始执行

---

**更新日志**：
- 2026-10-15：初始版本
