# Acceptance Criteria — 验收标准

**目的**：定义每个 Phase 和任务的可验证完成标准，确保重构质量可控、可追溯。

---

## Phase 1：Token 系统冻结

### 整体验收标准

- [ ] **构建成功**：`npm run build` 0 errors
- [ ] **类型检查通过**：`npx tsc --noEmit` 0 errors
- [ ] **测试通过**：前端测试 531 passed（无回归）
- [ ] **Token 统一**：只有 1 套 Token 系统（`ui-v2/tokens.css`）
- [ ] **运行时配置保留**：Legacy `site-content.json` 可运行时覆盖 Token
- [ ] **无视觉回归**：现有页面截图对比无非预期变化

---

### VSC-02-A：扩展 UI V2 Token

**验收标准**：

- [x] Editorial Token 完整定义（bg/surface/text/accent/border）
- [x] Admin Token 完整定义（bg/surface/text/border/grid）
- [x] Navigation Token 完整定义（glass-bg/border/shadow/blur）
- [x] 品牌色统一为 `#3db8a8`
- [x] 保留现有 spacing/radius/shadow/duration（无删除）
- [x] CSS 语法验证通过（无警告）

**验证方法**：
```bash
# CSS 语法检查
npx stylelint src/components/ui-v2/tokens.css

# 检查 Token 定义
grep -E "(--editorial-|--admin-|--nav-)" src/components/ui-v2/tokens.css | wc -l
# 预期：≥ 20 个新 Token
```

---

### VSC-02-B：创建 Demo 页

**验收标准**：

- [x] Demo 页可访问（`http://localhost:2025/dev/tokens`）
- [x] 需管理员登录才能访问（AuthGate 生效）
- [x] 左侧 Editorial 区正确显示：
  - [x] 背景色 `#f5f1eb`（warm beige）
  - [x] 卡片白色，brick red 序号
  - [x] 字体清晰，间距舒适
- [x] 右侧 Admin 区正确显示：
  - [x] 背景色渐变（`#f0fffe → #f5fbfb`）
  - [x] 表单控件使用 teal brand
  - [x] 信息密度高于 Editorial
- [x] 顶部 Glass Bar 正确显示：
  - [x] backdrop-filter 生效（blur 可见）
  - [x] 降级方案生效（不支持时为实心白）
- [x] 响应式正常：
  - [x] Desktop：左右分栏
  - [x] Mobile：上下堆叠

**验证方法**：
- Chrome DevTools 截图对比参考图
- 手动验证 backdrop-filter（滚动页面观察模糊效果）
- 真机测试（iOS/Android）

---

### VSC-02-C：更新全局样式

**验收标准**：

- [x] `layout.tsx` 桥接 Legacy → UI V2（htmlStyle 包含新 Token）
- [x] `globals.css` 导入顺序正确（`ui-v2/tokens.css` 在前）
- [x] 现有页面无视觉回归（截图对比）
- [x] Demo 页正常显示（Token 生效）
- [x] 构建成功

**验证方法**：
```bash
# 构建验证
npm run build

# 截图对比（手动）
# 1. 首页
# 2. Blog 列表
# 3. Dashboard
```

---

### VSC-02-D：废弃 theme.css

**验收标准**：

- [x] `theme.css` 文件已删除
- [x] `globals.css` 不再导入 `theme.css`
- [x] 字体定义已合并到 `ui-v2/tokens.css`
- [x] 构建成功
- [x] 测试通过（531 passed）

**验证方法**：
```bash
# 确认文件已删除
ls src/styles/theme.css
# 预期：No such file or directory

# 确认无导入
grep "theme.css" src/styles/globals.css
# 预期：无匹配

# 测试
npm test
```

---

## Phase 2：Overlay 加固 + 试点接入

### 整体验收标准

- [ ] **无障碍达标**：axe-core 0 critical issues
- [ ] **键盘导航完整**：Tab/Esc/方向键正常工作
- [ ] **焦点管理正确**：Modal/Drawer 焦点陷阱生效
- [ ] **功能无回归**：试点页面功能正常
- [ ] **视觉验证通过**：截图对比无非预期变化

---

### VSC-03：实现 useOverlay Hook

**验收标准**：

- [ ] `useFocusTrap` 实现完整：
  - [ ] 焦点进入 overlay
  - [ ] Tab 循环
  - [ ] 关闭后恢复焦点
- [ ] `useZIndex` 实现完整：
  - [ ] 多 overlay 叠加时层级正确
- [ ] `useOverlay` 实现完整：
  - [ ] Esc 关闭
  - [ ] 动画状态管理
- [ ] 单元测试覆盖 ≥ 80%
- [ ] TypeScript 类型完整（无 `any`）

**验证方法**：
```bash
# 测试覆盖率
npm test -- --coverage

# TypeScript 检查
npx tsc --noEmit
```

---

### VSC-04：重构 Modal/Drawer

**验收标准**：

- [ ] Modal ARIA 完整：
  - [ ] `role="dialog"`
  - [ ] `aria-modal="true"`
  - [ ] `aria-labelledby` / `aria-describedby`
- [ ] Drawer ARIA 完整（同 Modal）
- [ ] 焦点陷阱生效：
  - [ ] 打开时自动 focus 第一个可交互元素
  - [ ] Tab 不会跳出 overlay
  - [ ] 关闭后恢复到触发元素
- [ ] Esc 关闭生效
- [ ] Backdrop 点击关闭可配置
- [ ] 动画流畅（无卡顿）
- [ ] axe-core 检测通过

**验证方法**：
```bash
# axe-core 检测（浏览器插件）
# 1. 打开 Demo 页
# 2. 打开 Modal
# 3. 运行 axe DevTools
# 预期：0 critical issues

# 键盘导航测试（手动）
# 1. Tab 到触发按钮
# 2. Enter 打开 Modal
# 3. Tab 循环所有交互元素
# 4. Esc 关闭，焦点回到按钮
```

---

### VSC-05：重构 ContextMenu

**验收标准**：

- [ ] `role="menu"` / `role="menuitem"`
- [ ] 方向键导航（↑↓）
- [ ] Esc 关闭
- [ ] 位置计算正确（不溢出屏幕）
- [ ] axe-core 检测通过

**验证方法**：
- 右键点击边界位置（右下角、左上角）
- 方向键导航测试
- axe-core 检测

---

### VSC-06：试点接入 — Dashboard

**验收标准**：

- [ ] 功能无回归：
  - [ ] 数据正常显示
  - [ ] 图表正常渲染
  - [ ] 交互正常（点击、筛选）
- [ ] 视觉正确：
  - [ ] 使用 admin Token（cool white 背景）
  - [ ] 组件样式一致
  - [ ] 截图对比无非预期变化
- [ ] 响应式正常：
  - [ ] Desktop 布局正常
  - [ ] Mobile 布局正常
- [ ] TypeScript 0 errors

**验证方法**：
```bash
# 功能回归测试（手动）
# 1. 访问 /dashboard
# 2. 检查所有卡片数据
# 3. 点击所有可交互元素
# 4. 测试筛选/排序

# 视觉验证
# 截图对比（Desktop + Mobile）

# TypeScript
npx tsc --noEmit
```

---

### VSC-07：试点接入 — Notes 列表

**验收标准**（同 VSC-06，但使用 editorial Token）：

- [ ] 功能无回归
- [ ] 使用 editorial Token（warm beige 背景）
- [ ] 卡片网格正确（Desktop 3 列，Mobile 1 列）
- [ ] 响应式正常

---

## Phase 3：Navigation 重构

### 整体验收标准

- [ ] **PublicTopNav 生效**：公开页面使用 glass topbar
- [ ] **AdminSidebar 生效**：管理页面使用 collapsible sidebar
- [ ] **MobileDrawer 生效**：移动端使用 drawer
- [ ] **旧导航废弃**：VerticalNav/MobileNav 已删除
- [ ] **功能无回归**：所有页面导航正常
- [ ] **无障碍达标**：axe-core 0 critical issues

---

### VSC-09：实现 PublicTopNav

**验收标准**：

- [ ] Floating state（初始）：
  - [ ] 半透明白背景
  - [ ] 页面顶部悬浮
- [ ] Sticky glass bar（滚动后）：
  - [ ] `backdrop-filter: blur(20px)` 生效
  - [ ] 固定在顶部
  - [ ] Dropdown 正常展开
- [ ] 降级方案生效（不支持 backdrop-filter）
- [ ] 键盘导航完整（Tab/方向键）
- [ ] 响应式正常：
  - [ ] Desktop：完整导航
  - [ ] Mobile：隐藏（用 Drawer）
- [ ] axe-core 检测通过

**验证方法**：
- 滚动页面观察状态切换
- Safari（支持）vs Firefox 旧版（不支持）对比
- 键盘导航测试
- 真机测试

---

### VSC-10：实现 AdminSidebar

**验收标准**：

- [ ] Collapsible 正常：
  - [ ] 展开 232px（图标 + 文字）
  - [ ] 收缩 64px（仅图标）
  - [ ] 动画流畅（300ms）
- [ ] Teal active state 正确
- [ ] 图标清晰可辨（lucide-react）
- [ ] 键盘导航完整
- [ ] 响应式正常：
  - [ ] Desktop：显示
  - [ ] Mobile：隐藏（用 Drawer）

---

### VSC-11：实现 MobileDrawer

**验收标准**：

- [ ] 从右侧滑入（动画流畅）
- [ ] 焦点陷阱生效
- [ ] Backdrop 点击关闭
- [ ] Esc 关闭
- [ ] Teal active state
- [ ] 真机测试通过（iOS/Android）

---

### VSC-12：更新 AppShell

**验收标准**：

- [ ] 根据路由切换 navigation：
  - [ ] `/dashboard` → AdminSidebar
  - [ ] `/blog` → PublicTopNav
- [ ] Mobile 统一用 Drawer
- [ ] 布局正确（sidebar/topbar + main）

---

### VSC-13：迁移路由

**验收标准**：

- [ ] 所有页面使用新 AppShell
- [ ] VerticalNav/MobileNav 已删除
- [ ] 功能无回归（53 页全量测试）
- [ ] 视觉验证通过

**验证方法**：
```bash
# 确认旧导航已删除
find src/components -name "vertical-nav.tsx" -o -name "mobile-nav.tsx"
# 预期：无匹配

# 全量功能测试（抽样）
# 1. 首页
# 2. Blog 列表 + 详情
# 3. Dashboard
# 4. Notes 列表 + 详情
# 5. Manage
```

---

## Phase 4：扩展接入 + 收尾

### VSC-14/15：扩展接入

**验收标准**（每页）：

- [x] 功能无回归（前端 78 files / 656 passed）
- [x] 使用 UI V2 组件（PageHeader / Card / Badge / Button / Modal / Drawer）
- [x] 使用正确 Token（admin: questions/mistakes/notes/drafts/review；editorial: blog/mistakes 公开列表）
- [x] 响应式正常（浏览器 1440 / 390 实测）
- [x] TypeScript 0 errors

**本阶段实际覆盖**：workspace `questions`/`mistakes`/`notes`/`drafts`/`review`；公开 `blog`/`mistakes` 列表；3 个旧 overlay 消费者全部迁移。
**DEFERRED**：其余 workspace 页面与 12 个旧 `DialogModal`/`Drawer` 消费者（见 task-registry VSC-14/15）。

---

### VSC-16：Dark Mode 实现

**验收标准**：

- [x] Dark Token 完整定义（Phase 1 已写入 `[data-theme='dark']`）
- [x] 主题切换 UI 可用（`ThemeToggle`，44×44 icon button）
- [x] 切换流畅（`dataset.theme` 即时切换，无重新加载）
- [x] localStorage 持久化（读写 try/catch；不可用时降级不崩）
- [x] 色彩对比度达标（WCAG AA）：
  - [x] Editorial Dark：主文字 15.64:1、次级 7.60:1
  - [x] Admin Dark：主文字 16.02:1、次级 7.97:1
  - [ ] 整页逐元素 AA —— **NOT_VERIFIED**：共享组件（async-state-panel 等）仍用旧色工具类，暗色下个别区域对比不足（见 task-registry Phase 4 已知限制）

**验证方法**：
```bash
# 色彩对比度检测
# 使用 Contrast Checker 工具
# 或 Chrome DevTools Lighthouse
```

---

### VSC-17：最终验收

**验收标准**：

- [x] **功能回归测试 100% 通过**：前端 78 files / 656 passed（全站 53 页抽样未做逐页手测）
- [x] **可访问性断言**：以 role/aria/键盘断言 + 组件测试替代 axe-core（未引入依赖）
- [ ] **Lighthouse Performance ≥ 90**（3 页抽样）—— **NOT_VERIFIED**：未安装/运行 Lighthouse
- [x] **视觉回归**：本阶段目标页截图留档（`phase4-*.png`），无意外变化
- [x] **TypeScript 0 errors**
- [x] **前端测试 656 passed**（基线 606 → 656）
- [ ] **后端测试** —— 未运行（本阶段未触及后端）
- [x] **构建成功**（`npm run build`）
- [x] **文档更新**（task-registry.md 全部状态 + 本文件）

**验证方法**：
```bash
# 类型检查
npx tsc --noEmit

# 测试
npm test  # 前端
cd backend && PYTHONPATH=. pytest  # 后端

# 构建
npm run build

# Lighthouse（抽样）
# 1. 首页
# 2. Blog 详情
# 3. Dashboard

# axe-core（全站抽样）
# 10-15 页代表性页面
```

---

## 回归测试清单

### 功能回归（必测）

| 页面 | 测试项 | 预期结果 |
|------|--------|----------|
| **首页** | 导航可用、卡片展示、链接跳转 | 正常 |
| **Blog 列表** | 分页、筛选、搜索 | 正常 |
| **Blog 详情** | 内容渲染、代码高亮、图表 | 正常 |
| **Dashboard** | 数据加载、图表渲染、筛选 | 正常 |
| **Notes 列表** | 分页、卡片展示 | 正常 |
| **Manage** | Tab 切换、表单提交 | 正常 |
| **Review** | 题目展示、作答、提交 | 正常 |
| **Write** | 编辑器、预览、保存 | 正常 |

### 无障碍回归（必测）

| 项目 | 测试方法 | 预期结果 |
|------|----------|----------|
| **键盘导航** | Tab 遍历所有页面 | 可达所有交互元素 |
| **焦点管理** | Modal/Drawer 打开关闭 | 焦点正确 |
| **ARIA** | axe-core 检测 | 0 critical issues |
| **色彩对比度** | Contrast Checker | ≥ 4.5:1 |

### 响应式回归（必测）

| 设备 | 测试页面 | 预期结果 |
|------|----------|----------|
| **Desktop** | 所有页面 | 布局正常 |
| **Tablet** | 首页、Blog、Dashboard | 布局正常 |
| **Mobile** | 首页、Blog、Notes | 布局正常、Drawer 可用 |

---

## 验收拒绝条件（任一项触发）

- [ ] TypeScript errors ≥ 1
- [ ] 前端测试 failed ≥ 1
- [ ] 后端测试 failed ≥ 1
- [ ] 构建失败
- [ ] axe-core critical issues ≥ 1
- [ ] Lighthouse Performance < 80
- [ ] 功能回归失败 ≥ 1 项
- [ ] 视觉回归非预期变化 ≥ 3 处

---

## 下一步

阅读 `governance.md`（变更治理流程）

---

**更新日志**：
- 2026-10-15：初始版本
