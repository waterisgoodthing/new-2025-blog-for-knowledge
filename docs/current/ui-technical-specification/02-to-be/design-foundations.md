# Design Foundations — 设计基础规范

**来源**：`docs/current/workflows/visual-system-consolidation/design.md` + 参考图  
**设计讨论日期**：2026-08-29  
**证据等级**：L1（参考图实测） + L2（设计文档）

---

## 核心设计原则

### 双表面系统（Dual-Surface System）

**目标**：区分公开阅读和管理工具的视觉语言。

| 表面类型 | 适用场景 | 视觉特征 |
|----------|----------|----------|
| **Editorial** | 公开阅读（Blog/Notes/Mistakes 详情） | Warm whitespace, generous spacing, strong hierarchy, restrained cards |
| **Admin** | 管理工具（Dashboard/Review/Manage） | Cool white utility, faint teal structure, higher density, stable controls |
| **Navigation** | 共享导航（顶栏/侧边栏） | Translucent liquid glass, backdrop blur, floating |

---

## 1. 色彩系统（Color System）

### 1.1 品牌色（Brand）

**统一 Teal**：从参考图提取中间值

```css
--brand: #3db8a8;              /* 主品牌色（cyan-teal 中间值） */
--brand-ink: #1f7a6e;          /* 深色文字/按钮 */
--brand-hover: #2a9d8f;        /* hover 态 */
```

**来源**：
- Legacy `#2fcbe7`（偏蓝）
- UI V2 `#35bfab`（偏绿）
- 参考图 admin-login 按钮 `#4db8a8` 左右
- **取中间值 `#3db8a8`，兼顾历史和设计目标**

---

### 1.2 Editorial 表面（公开阅读）

**参考图**：`editorial-whitespace-reference.png`

```css
/* 背景与表面 */
--editorial-bg: #f5f1eb;              /* warm beige 底色（实测） */
--editorial-surface: #fffef8;         /* warm white 卡片（实测） */
--editorial-surface-elevated: #ffffff; /* 悬浮卡片 */

/* 文字 */
--editorial-text-primary: #4a3832;    /* 深棕主文字（实测） */
--editorial-text-secondary: #8b7667;  /* 次要文字（实测） */
--editorial-text-tertiary: #b8a393;   /* 三级文字 */

/* 强调色 */
--editorial-accent: #b85e4c;          /* brick red（实测，用于序号/标签） */
--editorial-accent-soft: #d4998c;     /* 淡化版 */

/* 边框与分隔 */
--editorial-border: rgba(74, 56, 50, 0.12);
--editorial-divider: rgba(74, 56, 50, 0.08);
```

**视觉特征**：
- Warm, editorial, content-first
- 大留白（generous spacing）
- 圆角卡片 + subtle shadow
- Brick red 用于视觉节奏（序号、强调、标签）

---

### 1.3 Admin 表面（管理工具）

**参考图**：`admin-login-cool-grid-reference.png`

```css
/* 背景与表面 */
--admin-bg: linear-gradient(180deg, #f0fffe 0%, #f5fbfb 100%);
--admin-surface: #ffffff;
--admin-surface-subtle: #fafcfc;

/* 文字 */
--admin-text-primary: #2d3e3c;        /* cool charcoal（实测） */
--admin-text-secondary: #6b7b79;      /* 次要文字 */
--admin-text-tertiary: #9eadab;       /* 三级文字 */

/* 结构色 */
--admin-border: rgba(45, 62, 60, 0.12);
--admin-divider: rgba(45, 62, 60, 0.08);
--admin-grid: rgba(61, 184, 168, 0.04); /* faint teal grid */
```

**视觉特征**：
- Cool, utility, tool-oriented
- Higher information density
- Faint teal structure（subtle grid/border）
- Flat, stable, no decorative elements

---

### 1.4 Navigation / Overlay（共享）

**参考图**：`editorial-liquid-glass-reference.png`

```css
/* Liquid Glass */
--nav-glass-bg: rgba(255, 255, 255, 0.8);
--nav-glass-border: rgba(255, 255, 255, 0.3);
--nav-glass-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
--nav-blur: blur(20px);

/* Active State */
--nav-active-bg: rgba(61, 184, 168, 0.12);  /* teal tint */
--nav-hover-bg: rgba(255, 255, 255, 0.6);
```

**视觉特征**：
- Translucent (80% white)
- Backdrop filter: blur(20px)
- Floating, lightweight
- 适用于顶栏、侧边栏、Dropdown、Popover

---

## 2. Typography（字体系统）

### 2.1 字体族（Font Families）

```css
--font-sans: 'PingFang SC', -apple-system, system-ui, sans-serif;
--font-serif: 'Noto Serif SC', Georgia, serif;  /* editorial 长文本备选 */
--font-mono: 'JetBrains Mono', 'Menlo', monospace;
--font-display: 'Averia Gruesa Libre', sans-serif; /* 特殊装饰用 */
```

**使用规则**：
- **Editorial**：优先 sans，长文本可选 serif
- **Admin**：统一 sans
- **Code**：mono
- **装饰性标题**：display

---

### 2.2 流式尺寸（Fluid Scale）

**设计目标**：所有字号用 `clamp()` 实现流式缩放。

```css
/* 基础尺寸 */
--text-xs: clamp(0.75rem, 0.7rem + 0.25vw, 0.8rem);      /* 12-12.8px */
--text-sm: clamp(0.875rem, 0.85rem + 0.25vw, 0.95rem);   /* 14-15.2px */
--text-base: clamp(1rem, 0.95rem + 0.35vw, 1.125rem);    /* 16-18px */
--text-lg: clamp(1.125rem, 1.05rem + 0.5vw, 1.375rem);   /* 18-22px */
--text-xl: clamp(1.25rem, 1.125rem + 0.75vw, 1.75rem);   /* 20-28px */
--text-2xl: clamp(1.5rem, 1.35rem + 1vw, 2.25rem);       /* 24-36px */
--text-display: clamp(1.875rem, 1.5rem + 1.5vw, 3rem);   /* 30-48px */
```

**字重（Font Weight）**：

```css
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

**行高（Line Height）**：

```css
--leading-tight: 1.25;     /* 标题 */
--leading-snug: 1.375;     /* 短文本 */
--leading-normal: 1.5;     /* 正文（Editorial） */
--leading-relaxed: 1.625;  /* 长文本（Editorial） */
--leading-loose: 2;        /* 特殊用途 */
```

**字距（Letter Spacing）**：

```css
--tracking-tight: -0.025em;   /* 大标题 */
--tracking-normal: 0;         /* 正文 */
--tracking-wide: 0.025em;     /* 小号文字 */
--tracking-wider: 0.05em;     /* 全大写标签 */
```

---

## 3. 间距系统（Spacing Scale）

**基数**：4px

```css
--space-0: 0;
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-5: 20px;
--space-6: 24px;
--space-8: 32px;
--space-10: 40px;
--space-12: 48px;
--space-16: 64px;
--space-20: 80px;
--space-24: 96px;
--space-32: 128px;
```

**使用规则**：
- **Editorial**：慷慨间距（12/16/24/32）
- **Admin**：紧凑间距（4/8/12/16）
- **组件内部**：4/8/12
- **区块间隔**：16/24/32

---

## 4. 圆角系统（Radius Scale）

**目标**：全圆角几何（design.md 要求）

```css
--radius-none: 0;
--radius-sm: 8px;       /* 小组件（badge/chip） */
--radius-md: 12px;      /* 标准组件（button/input/card） */
--radius-lg: 16px;      /* 大卡片 */
--radius-xl: 24px;      /* 特殊容器 */
--radius-full: 9999px;  /* 完全圆形（pill button/avatar） */
```

**使用规则**：
- **Button/Chip**：`--radius-full`（pill 形状）
- **Card/Input**：`--radius-md` (12px)
- **Avatar/Icon Well**：`--radius-full` (50%)
- **Modal/Drawer**：`--radius-lg` (16px)

---

## 5. 阴影系统（Shadow Scale）

**设计原则**：克制、单层、柔和

```css
/* 基础阴影 */
--shadow-xs: 0 1px 2px rgba(0, 0, 0, 0.04);
--shadow-sm: 0 1px 4px rgba(0, 0, 0, 0.06);
--shadow-md: 0 4px 16px rgba(0, 0, 0, 0.08);
--shadow-lg: 0 12px 32px rgba(0, 0, 0, 0.12);
--shadow-xl: 0 20px 48px rgba(0, 0, 0, 0.16);

/* 特殊阴影 */
--shadow-glass: 0 8px 32px rgba(0, 0, 0, 0.08);  /* liquid glass */
--shadow-elevated: 0 16px 40px rgba(0, 0, 0, 0.1); /* 悬浮卡片 */
```

**使用规则**：
- **Editorial Card**：`--shadow-sm` 或 `--shadow-md`
- **Admin Card**：`--shadow-xs`（极细）
- **Liquid Glass**：`--shadow-glass`
- **Dropdown/Popover**：`--shadow-lg`
- **Modal**：`--shadow-xl`

---

## 6. 边框系统（Border Scale）

```css
/* 宽度 */
--border-none: 0;
--border-thin: 1px;
--border-medium: 2px;
--border-thick: 4px;

/* 颜色（继承 editorial/admin token） */
--border-subtle: <editorial-border | admin-border>;
--border-medium: <editorial-border 增强不透明度>;
--border-strong: <editorial-text-secondary | admin-text-secondary>;
```

---

## 7. 动效系统（Motion Scale）

```css
/* Duration */
--duration-instant: 0ms;
--duration-fast: 150ms;
--duration-normal: 200ms;
--duration-slow: 300ms;
--duration-slower: 450ms;

/* Easing */
--ease: cubic-bezier(0.4, 0, 0.2, 1);          /* 标准缓动 */
--ease-out: cubic-bezier(0, 0, 0.2, 1);        /* 出场 */
--ease-in: cubic-bezier(0.4, 0, 1, 1);         /* 入场 */
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);   /* 双向 */
--ease-spring: cubic-bezier(0.68, -0.55, 0.265, 1.55); /* 弹性 */
```

**使用规则**：
- **Hover/Focus**：`--duration-fast` + `--ease-out`
- **Modal/Drawer 入场**：`--duration-normal` + `--ease-out`
- **Navigation 展开**：`--duration-slow` + `--ease-spring`
- **加载动画**：持续（无限循环）

**Reduced Motion**：

```css
@media (prefers-reduced-motion: reduce) {
  :root {
    --duration-fast: 0ms;
    --duration-normal: 0ms;
    --duration-slow: 0ms;
    --duration-slower: 0ms;
  }
}
```

---

## 8. 层级系统（Z-Index Scale）

```css
--z-base: 0;
--z-dropdown: 1000;
--z-sticky: 1100;
--z-fixed: 1200;
--z-modal-backdrop: 1300;
--z-modal: 1400;
--z-popover: 1500;
--z-tooltip: 1600;
--z-toast: 1700;
```

---

## 9. Token 架构

### 三层 Token 体系

```
Primitive Tokens (基础值)
      ↓
Semantic Tokens (语义层)
      ↓
Component Tokens (组件层)
```

**示例**：

```css
/* Primitive */
--blue-600: #3db8a8;

/* Semantic */
--color-action-primary: var(--blue-600);

/* Component */
--button-primary-bg: var(--color-action-primary);
```

---

## 10. Dark Mode（暗色模式）

**优先级**：P1（Phase 2）

**策略**：
- Editorial：深棕背景（`#1a1311`）+ warm white text
- Admin：深青灰背景（`#0f1416`）+ cool white text
- Liquid Glass：深色半透明（`rgba(26, 19, 17, 0.8)`）

**实现方式**：
- CSS `@media (prefers-color-scheme: dark)`
- 或 `[data-theme="dark"]` 类

---

## 下一步

1. **阅读** `component-system.md`（组件规范）
2. **阅读** `navigation-system.md`（Navigation 详细规范）
3. **阅读** `overlay-system.md`（Overlay 详细规范）

---

**更新日志**：
- 2026-10-15：初始版本（基于 design.md + 参考图实测）
