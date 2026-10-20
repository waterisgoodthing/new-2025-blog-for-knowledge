# Phase 1 启动 Prompt — 给 Gemini

---

## 背景

你正在完成一个 Next.js 个人博客项目的 UI 系统重构（visual-system-consolidation）。项目当前有 3 套并存的 Token 系统造成混乱，需要在 Phase 1 合并为 1 套统一的双表面系统。

**项目信息**：
- 仓库：`/Users/limengyang/2025-blog-public`
- 分支：`refactor/baseline`
- 状态：clean（无未提交更改）
- 前端框架：Next.js 16.3.8 + React 19 + Tailwind 4
- 当前测试状态：531 passed / 0 failed

---

## 任务目标

**完成 Phase 1：Token 系统冻结**

目标：将 3 套并存的 Token 系统合并为 1 套统一的双表面系统

### 具体任务

#### VSC-02-A：扩展 UI V2 Token（2 小时）

**文件**：`src/components/ui-v2/tokens.css`

**内容**：在现有 UI V2 Token 基础上追加：

1. **Editorial Token**（公开阅读表面）：
   ```css
   --editorial-bg: #f5f1eb;              /* warm beige 底色 */
   --editorial-surface: #fffef8;         /* warm white 卡片 */
   --editorial-surface-elevated: #ffffff; /* 悬浮卡片 */
   --editorial-text-primary: #4a3832;    /* 深棕主文字 */
   --editorial-text-secondary: #8b7667;  /* 次要文字 */
   --editorial-text-tertiary: #b8a393;   /* 三级文字 */
   --editorial-accent: #b85e4c;          /* brick red 强调 */
   --editorial-accent-soft: #d4998c;     /* 淡化版 */
   --editorial-border: rgba(74, 56, 50, 0.12);
   --editorial-divider: rgba(74, 56, 50, 0.08);
   ```

2. **Admin Token**（管理工具表面）：
   ```css
   --admin-bg: linear-gradient(180deg, #f0fffe 0%, #f5fbfb 100%);
   --admin-surface: #ffffff;
   --admin-surface-subtle: #fafcfc;
   --admin-text-primary: #2d3e3c;        /* cool charcoal */
   --admin-text-secondary: #6b7b79;
   --admin-text-tertiary: #9eadab;
   --admin-border: rgba(45, 62, 60, 0.12);
   --admin-divider: rgba(45, 62, 60, 0.08);
   --admin-grid: rgba(61, 184, 168, 0.04); /* faint teal grid */
   ```

3. **Navigation / Overlay Token**（共享）：
   ```css
   --nav-glass-bg: rgba(255, 255, 255, 0.8);
   --nav-glass-border: rgba(255, 255, 255, 0.3);
   --nav-glass-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
   --nav-blur: blur(20px);
   --nav-active-bg: rgba(61, 184, 168, 0.12);  /* teal tint */
   --nav-hover-bg: rgba(255, 255, 255, 0.6);
   ```

4. **统一品牌色**（从参考图中间值取）：
   ```css
   --brand: #3db8a8;              /* 从 #35bfab 调整到中间值 */
   --brand-ink: #1f7a6e;
   --brand-hover: #2a9d8f;
   ```

5. **保留现有的**：
   - spacing（`--uiv2-space-*`）
   - radius（`--uiv2-radius-*`）
   - shadow（`--uiv2-shadow-*`）
   - duration（`--uiv2-duration-*`）
   - 所有其他现有 Token

**验证**：
- TypeScript 0 errors（`npx tsc --noEmit`）
- CSS 语法检查通过

---

#### VSC-02-B：创建 Demo 页（3 小时）

**文件**：`src/app/_dev/tokens/page.tsx`（新建）

**要求**：
- 需管理员登录才能访问（使用 AuthGate）
- 布局：左右对比 + 顶部 Glass Bar

**左侧 Editorial 区**：
- 背景色：`--editorial-bg` (#f5f1eb warm beige)
- 标题：大、清晰、深棕文字
- 展示内容：
  - 卡片网格（warm white 背景，subtle shadow）
  - Brick red 序号（`--editorial-accent`）
  - 排版示例（标题、正文、次要文字）
  - 间距示例（体现 generous spacing）

**右侧 Admin 区**：
- 背景色：`--admin-bg`（渐变）
- 标题：紧凑布局
- 展示内容：
  - 表格或表单控件
  - Teal 主色按钮（`--brand`）
  - Admin 风格卡片（白色，极细 shadow）
  - 密集信息展示

**顶部 Glass Bar**：
- 初始状态（页面顶部）：透明，悬浮
- 滚动状态（滚动后）：sticky，glass 效果（`backdrop-filter: var(--nav-blur)`）
- 展示 glass 效果的对比

**验证**：
- 浏览器打开 `http://localhost:2025/_dev/tokens`
- Dark/Light 模式都能正常显示
- 截图对比设计参考图

---

#### VSC-02-C：更新全局样式（1 小时）

**文件 1**：`src/app/layout.tsx`

**内容**：在 `htmlStyle` 中桥接 Legacy → UI V2

```tsx
const htmlStyle = {
  cursor: 'url(/images/cursor.svg) 2 1, auto',
  // 桥接 Brand 色
  '--brand': theme.colorBrand || '#3db8a8',
  // 桥接 Editorial（新增）
  '--editorial-bg': theme.editorialBg || '#f5f1eb',
  '--editorial-surface': theme.editorialSurface || '#fffef8',
  '--editorial-text-primary': theme.editorialTextPrimary || '#4a3832',
  '--editorial-text-secondary': theme.editorialTextSecondary || '#8b7667',
  '--editorial-accent': theme.editorialAccent || '#b85e4c',
  // 桥接 Admin（新增）
  '--admin-text-primary': theme.adminTextPrimary || '#2d3e3c',
  '--admin-text-secondary': theme.adminTextSecondary || '#6b7b79',
  // 保留其他 Legacy Token 向后兼容
  '--color-primary': theme.colorPrimary,
  '--color-secondary': theme.colorSecondary,
  // ...
}
```

**文件 2**：`src/styles/globals.css`

**内容**：更新导入顺序，确保 UI V2 Token 优先级正确

```css
@import 'tailwindcss';
@import 'katex/dist/katex.min.css';
@import '../components/ui-v2/tokens.css';  /* 提前到前面 */
@import './article.css';
/* @import './theme.css';  保留但注释，稍后删除 */
```

**验证**：
- `npm run build` 成功
- 现有页面视觉无明显变化
- Demo 页能正常显示新 Token

---

#### VSC-02-D：废弃 theme.css（0.5 小时）

**文件 1**：`src/styles/theme.css`

**内容**：
- 删除该文件（或移到 archive）

**文件 2**：`src/styles/globals.css`

**内容**：
- 移除 `@import './theme.css';` 行

**验证**：
```bash
# 确认文件已删除
ls src/styles/theme.css
# 预期：No such file or directory

# 确认构建成功
npm run build

# 确认测试通过
npm test
# 预期：531 passed
```

---

## 完成标准

所有 4 个任务都需要满足：

- [ ] **VSC-02-A**：新 Token 完整追加到 `ui-v2/tokens.css`
- [ ] **VSC-02-B**：Demo 页可访问，左右对比清晰，glass bar 可见
- [ ] **VSC-02-C**：现有页面无视觉回归
- [ ] **VSC-02-D**：`theme.css` 已删除，构建成功

### 最终验收

- [ ] TypeScript 0 errors
- [ ] `npm run build` 成功
- [ ] 前端测试 531 passed
- [ ] Demo 页浏览器验证通过
- [ ] 现有页面截图对比无非预期变化

---

## 文件位置与引用

**关键文件**：
- `src/components/ui-v2/tokens.css` — 主要修改
- `src/app/layout.tsx` — 样式注入
- `src/styles/globals.css` — 导入顺序
- `src/styles/theme.css` — 待废弃

**参考文档**：
- 完整 Token 设计规范：`docs/current/ui-technical-specification/02-to-be/design-foundations.md`
- 参考图（色值验证）：`docs/current/workflows/visual-system-consolidation/assets/admin-login-cool-grid-reference.png` 等

**色值参考**（已从参考图实测）：
- Editorial bg: `#f5f1eb` (warm beige)
- Editorial accent: `#b85e4c` (brick red)
- Admin bg: `#f0fffe → #f5fbfb` (gradient)
- Admin text: `#2d3e3c` (cool charcoal)
- Brand teal: `#3db8a8` (cyan-teal 中间值)

---

## 技术约束

**必须遵守**：
- ✅ 不删除现有 Token（只追加和修改值）
- ✅ 保留 Legacy Token 运行时配置能力（通过 `layout.tsx` 桥接）
- ✅ 不修改任何页面（只修改 Token）
- ✅ TypeScript 0 errors
- ✅ 测试 531 passed

**工程约束**：
- 新创建的文件（Demo 页）需要权限检查（AuthGate）
- CSS 必须有效（无警告）
- 构建必须成功

---

## 时间估计

| 任务 | 预计时间 |
|------|----------|
| VSC-02-A | 2h |
| VSC-02-B | 3h |
| VSC-02-C | 1h |
| VSC-02-D | 0.5h |
| **总计** | **6.5h** |

---

## 交付物

完成后应该有：

1. ✅ 统一的 Token 系统（`ui-v2/tokens.css`）
2. ✅ 可访问的 Demo 页（`/_dev/tokens`）
3. ✅ 更新的全局样式（`layout.tsx` + `globals.css`）
4. ✅ 删除的过时文件（`theme.css`）
5. ✅ 所有测试通过
6. ✅ 构建成功

---

## 下一步

完成 Phase 1 后：
- 给 Kiro 看 Demo 页截图
- 验证色值和设计是否符合期望
- 如果有调整，回到 VSC-02-A 微调 Token 值
- 然后启动 Phase 2（Overlay 加固）

---

**开始吧！**
