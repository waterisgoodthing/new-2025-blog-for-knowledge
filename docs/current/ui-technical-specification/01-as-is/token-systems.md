# Token Systems — 3 套 Token 系统对比

**证据等级**：L1（已验证）  
**审计日期**：2026-10-15

---

## 核心问题

**系统分裂**：项目中存在 **3 套并行的 Token 定义系统**，职责重叠、值冲突，无统一真相来源。

---

## 系统 1：Legacy Theme（`site-content.json`）

### 定义位置

`src/config/site-content.json` → 运行时注入到 `<html style>`

### Token 清单（8 个）

| Token | 值 | 说明 |
|-------|-----|------|
| `--color-brand` | `#2fcbe7` | 品牌色（cyan-teal，偏蓝） |
| `--color-primary` | `#5B423F` | 主色（深棕） |
| `--color-secondary` | `#8b7667` | 次要色（棕灰） |
| `--color-brand-secondary` | `#eec25e` | 品牌辅助色（金黄） |
| `--color-bg` | `#d4e8f3` | 背景色（浅青） |
| `--color-border` | `#ffffff` | 边框色（白） |
| `--color-card` | `#ffffff99` | 卡片色（半透明白） |
| `--color-article` | `#ffffffcc` | 文章背景（80% 白） |

### 注入方式

```tsx
// src/app/layout.tsx
const htmlStyle = {
  cursor: 'url(/images/cursor.svg) 2 1, auto',
  '--color-brand': theme.colorBrand,
  '--color-primary': theme.colorPrimary,
  '--color-secondary': theme.colorSecondary,
  '--color-brand-secondary': theme.colorBrandSecondary,
  '--color-bg': theme.colorBg,
  '--color-border': theme.colorBorder,
  '--color-card': theme.colorCard,
  '--color-article': theme.colorArticle
}

<html style={htmlStyle}>
```

### 特征

- ✅ 运行时可配置（通过后端 API 修改）
- ✅ 已在生产使用
- ❌ 只有颜色，无 spacing/radius/shadow
- ❌ 职责混乱（`colorPrimary` 深棕与品牌 teal 无关联）
- ❌ 配置文件驱动，前端无法独立迭代

### 视觉风格

**Translucent glassmorphism + Warm beige/cyan 混合**

---

## 系统 2：Tailwind Theme（`theme.css`）

### 定义位置

`src/styles/theme.css` → Tailwind `@theme` 指令

### Token 清单（10 个）

| Token | 值 | 说明 | 与 Legacy 冲突？ |
|-------|-----|------|------------------|
| `--color-primary` | `#334f52` | 深青灰 | ❌ 与 Legacy `#5B423F` 冲突 |
| `--color-secondary` | `#7b888e` | 中灰 | ❌ 与 Legacy `#8b7667` 冲突 |
| `--color-brand-secondary` | `#1fc9e7` | 亮青 | ❌ 与 Legacy `#eec25e` 冲突 |
| `--color-bg` | `#eeeeee` | 浅灰背景 | ❌ 与 Legacy `#d4e8f3` 冲突 |
| `--color-border` | `#fff` | 白 | ✅ 一致 |
| `--color-brand` | `#35bfab` | 绿松石 | ❌ 与 Legacy `#2fcbe7` 冲突 |
| `--color-card` | `#ffffff66` | 40% 白 | ❌ 与 Legacy `#ffffff99` 冲突 |
| `--color-article` | `#ffffffcc` | 80% 白 | ✅ 一致 |
| `--font-averia` | `'Averia Gruesa Libre', sans-serif` | 特殊字体 | - |
| `--font-sans` | `'PingFang SC', ...` | 标准字体栈 | - |

### 特征

- ✅ Tailwind 集成（可用 `bg-brand` 等工具类）
- ✅ 包含字体定义
- ❌ **与 Legacy 值冲突**（品牌色 `#35bfab` vs `#2fcbe7`）
- ❌ 无法运行时配置
- ❌ 无 spacing/radius/shadow

### 注意

**实际运行时，`theme.css` 的值会被 `layout.tsx` 的内联样式覆盖**（因为内联样式优先级更高）。

---

## 系统 3：UI V2 Tokens（`ui-v2/tokens.css`）

### 定义位置

`src/components/ui-v2/tokens.css`

### Token 清单（约 40+）

#### 色彩（10+）

| Token | 值 | 说明 |
|-------|-----|------|
| `--uiv2-brand` | `#35bfab` | 品牌色（与 theme.css 一致） |
| `--uiv2-brand-ink` | `#1f7a6e` | 品牌深色 |
| `--uiv2-surface-solid` | `#ffffff` | 实心表面 |
| `--uiv2-surface-glass` | `rgba(255,255,255,0.8)` | 玻璃表面 |
| `--uiv2-text-primary` | `#1e2636` | 主文字 |
| `--uiv2-text-secondary` | `#6b7280` | 次要文字 |
| `--uiv2-text-tertiary` | `#9ca3af` | 三级文字 |
| `--uiv2-text-inverse` | `#ffffff` | 反色文字 |
| `--uiv2-border-subtle` | `rgba(0,0,0,0.06)` | 细边框 |
| `--uiv2-border-medium` | `rgba(0,0,0,0.12)` | 中边框 |

#### 间距（8 个）

| Token | 值 |
|-------|-----|
| `--uiv2-space-1` | `4px` |
| `--uiv2-space-2` | `8px` |
| `--uiv2-space-3` | `12px` |
| `--uiv2-space-4` | `16px` |
| `--uiv2-space-6` | `24px` |
| `--uiv2-space-8` | `32px` |
| `--uiv2-space-12` | `48px` |
| `--uiv2-space-16` | `64px` |

#### 圆角（5 个）

| Token | 值 |
|-------|-----|
| `--uiv2-radius-sm` | `4px` |
| `--uiv2-radius-md` | `8px` |
| `--uiv2-radius-lg` | `12px` |
| `--uiv2-radius-xl` | `16px` |
| `--uiv2-radius-full` | `9999px` |

#### 阴影（3 个）

| Token | 值 |
|-------|-----|
| `--uiv2-shadow-sm` | `0 1px 4px rgba(0,0,0,0.06)` |
| `--uiv2-shadow-md` | `0 4px 16px rgba(0,0,0,0.08)` |
| `--uiv2-shadow-lg` | `0 12px 32px rgba(0,0,0,0.12)` |

#### 动效（3 个）

| Token | 值 |
|-------|-----|
| `--uiv2-duration-fast` | `150ms` |
| `--uiv2-duration-normal` | `200ms` |
| `--uiv2-duration-slow` | `300ms` |

### 特征

- ✅ **完整 token 系统**（color/spacing/radius/shadow/duration）
- ✅ **命名空间隔离**（`--uiv2-*`）
- ✅ **单一真相来源**（CSS 文件，不依赖后端）
- ✅ **组件已实现**（15 个）
- ❌ **路由接入率 = 0**（关键问题）
- ❌ **只有 cool utility 风格，缺 editorial warm 表面**

### 视觉风格

**Cool white utility surfaces + Restrained shadows**

---

## 冲突矩阵

| Token 名称 | Legacy | Tailwind | UI V2 | 冲突？ |
|-----------|--------|----------|-------|--------|
| **品牌色** | `#2fcbe7` (cyan) | `#35bfab` (teal) | `#35bfab` | ❌ 2 vs 1 |
| **主色** | `#5B423F` (棕) | `#334f52` (青灰) | 未定义 | ❌ 完全不同 |
| **次要色** | `#8b7667` (棕灰) | `#7b888e` (中灰) | 未定义 | ❌ 不同 |
| **背景色** | `#d4e8f3` (浅青) | `#eeeeee` (浅灰) | `#ffffff` | ❌ 三套不同 |
| **卡片色** | `#ffffff99` (60% 白) | `#ffffff66` (40% 白) | `#ffffff` | ❌ 透明度不同 |
| **边框色** | `#ffffff` | `#ffffff` | `rgba(0,0,0,0.06)` | ⚠️ 语义不同 |

---

## 实际运行时优先级

```
1. layout.tsx 内联样式（Legacy）      ← 最高优先级
2. theme.css (@theme)                  ← 被覆盖
3. ui-v2/tokens.css (--uiv2-*)         ← 隔离命名空间，不冲突
```

**结论**：
- Legacy 覆盖 Tailwind theme
- UI V2 通过 namespace 隔离，不与前两者冲突
- **但 UI V2 未被使用，实际页面只看到 Legacy 样式**

---

## 问题总结

### P0 — 系统性问题

1. **品牌色不一致**：`#2fcbe7` (Legacy) vs `#35bfab` (Tailwind + UI V2)
2. **Token 系统分裂**：3 套定义，无统一真相来源
3. **UI V2 投入浪费**：完整系统已实现但零接入
4. **维护成本高**：修改一个颜色需要同步 3 处

### P1 — 架构问题

1. **运行时配置依赖**：Legacy 依赖后端 API，前端无法独立迭代
2. **缺失 Token 类型**：Legacy/Tailwind 缺 spacing/radius/shadow
3. **视觉覆盖不完整**：UI V2 只有 cool utility，缺 editorial warm

---

## 推荐方案

### Phase 1：合并 Token 系统

**目标**：统一为 UI V2 架构，补充 editorial warm 表面。

**步骤**：
1. 在 `ui-v2/tokens.css` 中追加 editorial token
2. 保留 Legacy 运行时配置能力（通过 CSS 变量桥接）
3. 废弃 `theme.css`（合并到 UI V2）
4. 更新 `layout.tsx` 使用新 token

**预期结果**：
- 1 套统一 token 系统
- 双表面支持（editorial warm + admin cool）
- 保留运行时配置能力（向后兼容）

---

## 下一步

阅读 `02-to-be/design-foundations.md`（目标 Token 系统定义）

---

**更新日志**：
- 2026-10-15：初始版本（基于 HEAD 700f345）
