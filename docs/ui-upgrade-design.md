# UI 升级设计文档 — 个人知识系统

> 版本: 1.2
> 日期: 2026-06-03
> 状态: Draft
> 关联: `docs/roadmap-design.md` | `docs/roadmap-tasks.md` | `AGENTS.md`
>
> **v1.2 变更**: 修正 10 处审查问题 — NavCard 硬约束、图标渲染方式、padding 策略、ScrollTopButton 冲突、ECharts 安全边界、DiagramViewer 降级、Markmap 懒加载、错题 AI 入口、空状态分批、mini NavCard 保留。

---

## 0. 文档定位

本文档覆盖系统 **UI 层** 的升级设计，与 `docs/roadmap-design.md`（后端/数据/业务逻辑演进）互补。roadmap-design 侧重 P0-P6 的数据模型、API、AI 服务；本文档侧重 **导航体验、渲染引擎、写作工具链、空状态与反馈**。

两份文档共享同一套 P 编号体系，但关注面不同：

| 维度 | roadmap-design | 本文档 |
|------|---------------|--------|
| 导航 | 未涉及 | P0 全面覆盖 |
| 渲染 | P3 compare/颜色 | P1 Markmap/ECharts/DiagramViewer |
| 写作 | P2 AI action 扩展 | P2 工具栏/AI 输出格式 |
| 空状态 | 未涉及 | P3 全面覆盖 |
| 数据模型 | P1-P6 | 不涉及 |

---

## 1. 当前 UI 状态摘要

### 1.1 导航

| 组件 | 位置 | 当前状态 |
|------|------|----------|
| `NavCard` | `src/components/nav-card.tsx` | 全局浮动卡片，三种模式：`full`（首页）、`icons`（内页横向图标栏）、`mini`（写作页仅头像）。通过 `HomeDraggableLayer` 定位，首页可拖拽。 |
| `KnowledgeSidebar` | `src/app/notes/components/knowledge-sidebar.tsx` | /notes、/mistakes、/manage 共用的知识库侧栏。桌面端固定左侧 `w-56`，移动端抽屉。包含文件夹树和标签。 |
| Header/Footer | `src/layout/header.tsx` / `footer.tsx` | 空占位符。 |

**问题**:
- 内页横向图标栏 (`form === 'icons'`) 空间紧凑，图标无文字说明，新用户难理解。
- 当前页面高亮不够明显（仅 `layoutId` 动画胶囊，品牌色弱）。
- 移动端图标栏居中浮在顶部，遮挡页面标题。
- 首页 NavCard 和内页图标栏的视觉语言割裂。
- **可访问性缺失**: NavCard 中所有 `<Link>` 均无 `aria-label` 和 `title` 属性。`form === 'icons'` 时标签文本被隐藏，链接变为纯图标无无障碍名称（`nav-card.tsx:182-191`）。首页头像链接同样缺失（`nav-card.tsx:148`）。
- **图标实现不统一**: 笔记图标使用自定义 SVG (`@/svgs/pen.svg`)，其余使用自定义 SVG（非 lucide-react）。VerticalNav 需要统一处理 SVG 组件和 lucide-react 组件的渲染方式。
- **数值偏差**: `fullItemHeight` 实际为 52（非设计假设的 42），`hoveredIndex` 初始值为 `0`（非 `undefined`），胶囊渐变使用 `--color-border` 和 `--color-card` CSS 变量（非 `rgba(255,255,255,.86)`）。

### 1.2 渲染

| 组件 | 位置 | 当前状态 |
|------|------|----------|
| `MermaidBlock` | `src/components/mermaid-block.tsx` | 懒加载 mermaid，渲染 SVG，通过 `DiagramViewer` 展示。 |
| `DiagramViewer` | `src/components/diagram-viewer.tsx` | 支持 image/svg 两种 kind，全屏 modal、缩放 0.5x-3x、重置、关闭。 |
| `useMarkdownRender` | `src/hooks/use-markdown-render.tsx` | `marked` + `html-react-parser`，检测 mermaid 代码块替换为 `MermaidBlock`。 |

**问题**:
- 思维导图依赖 Mermaid mindmap，节点多时布局差、样式不可控。
- 无数据图表能力（柱状图、饼图等），错题统计只能用纯 CSS。
- `DiagramViewer` 默认不自适应容器宽度，大图需手动缩放。

### 1.3 写作

| 组件 | 位置 | 当前状态 |
|------|------|----------|
| `NoteToolbar` | `src/app/write-note/components/note-toolbar.tsx` | 格式化 + 插入（Mermaid/对比块/思维导图/复习卡片）。 |
| `SlashCommandMenu` | `src/app/write-note/components/slash-command-menu.tsx` | `/` 触发，24 个命令，键盘导航。 |
| `AIAssistantPanel` | `src/app/write-note/components/ai-assistant-panel.tsx` | 选区操作 + 插入内容 + 全文处理，SSE 流式。 |

**问题**:
- 思维导图插入模板仍为 Mermaid mindmap 语法。
- 字体颜色靠手写 `{red|文本}`，无可视化色板。
- 对比块模板暴露 `:::compare` 语法，不够直观。
- AI 思维导图输出仍为 Mermaid 语法，需切换为 Markmap Markdown。
- AI 错题解析输出结构不够完整（缺考点、易错点、类似题型）。

### 1.4 空状态与反馈

**当前状态**: 无统一 `EmptyState` 组件，所有空状态为内联 JSX。共 36+ 处，样式不一致（详见 §5.1）。

**问题**:
- 不区分"真无内容"、"筛选为空"、"未登录"、"API 失败"。
- 无引导操作（如"创建第一篇笔记"）。
- 按钮颜色不统一：危险操作有时红色有时灰色，主操作无品牌色。

---

## 2. P0 — 导航体验修复

### 2.1 全局内页导航重构

**目标**: 将内页横向图标栏替换为左侧竖向导航栏。

**现状分析**:

`NavCard` 在 `form === 'icons'` 时渲染横向图标栏（`src/components/nav-card.tsx:127-199`），定位在左上角 `(24, 16)`，宽度 340px，高度 64px，6 个图标横向排列。通过 `HomeDraggableLayer` 包装。所有 `<Link>` 缺失 `aria-label`/`title`（`nav-card.tsx:148` 首页链接、`nav-card.tsx:182-191` 导航链接）。笔记图标使用自定义 SVG `@/svgs/pen.svg`（非 lucide-react `PenLine`），其余也为自定义 SVG。`hoveredIndex` 初始值为 `0`，`fullItemHeight` 为 52px。

**方案**: 新建 `VerticalNav` 组件替换内页导航，`NavCard` 仅保留首页 (`full`) 和写作页 (`mini`) 模式。

**硬约束 — NavCard 改动边界**:
- `NavCard` 被 `HomeDraggableLayer` 包裹（`nav-card.tsx:129`），首页布局编辑（拖拽保存偏移）依赖此组件。
- **禁止改动** `form === 'full'`（首页）和 `form === 'mini'`（写作页 `/write*`）的渲染逻辑。
- **只允许** 在 `form === 'icons'` 分支开头加 `return null`。
- 首页 `HomeDraggableLayer` 的 `cardKey='navCard'`、`x`/`y`/`width`/`height` 计算逻辑不得修改。
- 写作页 `mini` 模式（64×64 头像卡片）必须保留，写作页无 VerticalNav。

**组件设计** — `src/components/vertical-nav.tsx`:

```
┌──────┐      ┌──────────────────┐
│ 头像 │      │ 头像  站点标题     │
│──────│      │──────────────────│
│ 🏠   │  →   │ 🏠  首页          │ hover/
│ 📜   │      │ 📜  近期文章       │ 展开
│ 📝   │      │ 📝  笔记          │
│ ❌   │      │ ❌  错题集         │
│ ℹ️   │      │ ℹ️  关于网站       │
│ 🔗   │      │ 🔗  推荐分享       │
│ 🌐   │      │ 🌐  优秀博客       │
└──────┘      └──────────────────┘
56px 宽         180px 宽
```

**交互规范**:

| 状态 | 宽度 | 内容 | 动画 |
|------|------|------|------|
| 默认 | 56px | 图标（18×18） | — |
| hover | 180px | 图标 + 中文标签 | spring(400, 30) |
| 当前页 | 56px/180px | 品牌色背景胶囊 + 品牌色图标 | `layoutId` 滑动 |

**定位**: `fixed left-0 top-1/2 -translate-y-1/2 z-40`

**样式**: 右侧圆角卡片，`rounded-r-2xl border border-l-0 border-white/40 bg-white/70 backdrop-blur-xl shadow-lg`。与现有玻璃卡片风格统一。

**高亮规范**:
- 当前页: `bg-[var(--color-brand)]/15` + 品色图标 + `font-medium`
- hover: `bg-white/60`
- 使用 `motion layoutId='vertical-nav-active'` 实现胶囊滑动动画

**图标处理**:
- 导航列表复用 `nav-card.tsx` 的 `list` 数组
- **统一使用 `<Icon className='h-[18px] w-[18px]' />` 渲染所有图标**，不依赖 `size` 属性
- SVGR 导入的自定义 SVG（ScrollOutlineSVG 等）和 lucide-react 图标（Home 等）都是 React 组件，`className` 方式对两者都可靠
- 不使用 `typeof Icon === 'function'` 判断（SVGR 和 lucide 组件本质上都是函数组件，无法区分）
- 颜色通过父容器 `text-*` class 继承，图标本身不设独立颜色

**可访问性** (当前缺失，需补齐):
- NavCard 首页链接 (`nav-card.tsx:148`): 缺失 `aria-label`、`title`
- NavCard 导航链接 (`nav-card.tsx:182-191`): 缺失 `aria-label`、`title`，`icons` 模式下无可见文本
- KnowledgeSidebar 移动关闭按钮 (`knowledge-sidebar.tsx:258`): 缺失 `aria-label`
- VerticalNav 每个链接: 必须有 `aria-label` + `title`
- 导航区域: `<nav>` 语义标签
- 头像链接: `aria-label='返回首页'`

**布局影响**:
- VerticalNav 是 `fixed` 定位，不占据文档流空间
- **不给全局 `<main>` 加 padding-left**（会影响首页、写作页、详情页等所有路由）
- 改为：仅在内页列表容器（如 `/notes`、`/mistakes`、`/manage` 的内容区）加 `pl-16`，或让 VerticalNav 以覆盖式悬浮，由各页面自行确保左侧 56px 区域无关键交互元素
- `/blog`、`/about`、`/share`、`/bloggers` 等简单页面：内容居中布局，左侧 56px 被 VerticalNav 覆盖不影响阅读
- `/notes`、`/mistakes`、`/manage`：已有 `KnowledgeSidebar`（`w-56`），sidebar 本身在左侧，VerticalNav 不遮挡主内容区
- 移动端不显示此组件

**修改文件**:
- `src/components/vertical-nav.tsx` — 新建
- `src/components/nav-card.tsx` — `form === 'icons'` 时 return null
- `src/layout/index.tsx` — 条件渲染 VerticalNav；不对全局 main 加 padding

---

### 2.2 首页左侧栏收敛

**目标**: 保持首页 NavCard 玻璃卡片风格，检查细节，与内页竖向导航视觉统一。

**现状**: 首页 `form === 'full'` 渲染完整 NavCard，包含头像 + 标题 + 导航列表。通过 `cardStyles.navCard` 控制定位和尺寸。

**检查项**:

| 检查点 | 当前代码位置 | 预期 |
|--------|-------------|------|
| active 胶囊 | `nav-card.tsx:159-178` | `motion layoutId='nav-hover'`，渐变背景 `linear-gradient(to right bottom, var(--color-border) 60%, var(--color-card) 100%)`。需确认在不同主题色下对比度足够。 |
| 图标颜色 | `nav-card.tsx:188` | 选中态 `text-brand`，未选中为默认色。需确认品牌色在白色胶囊上可读。 |
| 文字截断 | `nav-card.tsx:190` | 无 `truncate`，需确认 52px 行高下中文标签不溢出。 |
| 首页链接 | `nav-card.tsx:148` | 缺失 `aria-label`/`title`，需补齐。 |
| 圣诞装饰 | `nav-card.tsx:137-146` | 条件渲染 `siteContent.enableChristmas`。与导航无关，保持现状。 |

**视觉统一**:
- 首页 NavCard 和内页 VerticalNav 使用相同的图标集（`navItems` 列表）。
- 首页 active 胶囊样式和内页 active 胶囊样式保持同一套设计语言：品牌色半透明背景 + 品牌色图标。
- 内页 VerticalNav 的头像区域复用首页 NavCard 的头像 + 标题布局。

**修改文件**:
- `src/components/nav-card.tsx` — 细节微调（如需要）

---

### 2.3 移动端导航单独设计

**目标**: 移动端不直接使用桌面竖向栏，优先底部导航或抽屉。

**约束**:
- 不遮挡页面标题（`<h1>` 区域）
- 不遮挡搜索框
- 不遮挡编辑器工具栏（`NoteToolbar`）
- 遵循 `safe-area-inset-bottom`

**方案**: 新建 `MobileNav` 组件 — 底部标签栏 + "更多"抽屉。

**组件设计** — `src/components/mobile-nav.tsx`:

**底部标签栏** (4 个主入口 + 更多):

```
┌──────────────────────────────────────┐
│  🏠      📜      📝      ❌     ⋮   │
│  首页    文章    笔记    错题   更多  │
└──────────────────────────────────────┘
```

- 仅在 `sm` 断点以下 (`maxSM`) 显示
- 固定底部: `fixed inset-x-0 bottom-0 z-50`
- 背景: `bg-white/80 backdrop-blur-xl border-t border-white/40`
- 底部安全区: `pb-[env(safe-area-inset-bottom)]`

**"更多" 抽屉**:
- 点击"更多"从底部弹出
- 包含: 关于网站、推荐分享、优秀博客
- 样式: `rounded-t-2xl bg-white/95 backdrop-blur-xl`
- 点击遮罩关闭

**与编辑页冲突处理**:
- `/write-note` 页面底部有编辑器区域，MobileNav 会遮挡
- 方案: 在写作页面 (`/write*`) 不渲染 MobileNav（Layout 中 `isWrite` 判断）
- 编辑页已有独立的移动端 AI 面板底部抽屉，不冲突

**Toast 位置适配**:
- 移动端有底部导航时，Toaster 位置改为 `top-center` 避免被遮挡

**布局影响**:
- 内页 `<main>` 需要 `padding-bottom: 56px`（移动端）
- 桌面端不受影响
- **ScrollTopButton 冲突处理**: 当前 `src/layout/index.tsx:62` 移动端 ScrollTopButton 固定在 `right-6 bottom-8`。MobileNav 高度约 56px + safe-area。ScrollTopButton 需上移至 `bottom-20`（约 80px）避免与 MobileNav 重叠。条件：`maxSM && isInnerPage` 时 ScrollTopButton 使用 `bottom-20`，否则保持 `bottom-8`。

**修改文件**:
- `src/components/mobile-nav.tsx` — 新建
- `src/layout/index.tsx` — 条件渲染 MobileNav；移动端内容区预留底部安全距离；调整 Toaster 和 ScrollTopButton

---

## 3. P1 — 笔记渲染升级

### 3.1 思维导图：从 Mermaid 切换到 Markmap

**背景**: 当前思维导图使用 Mermaid `mindmap` 语法（`src/components/mermaid-block.tsx`）。Mermaid mindmap 在节点多时布局差，样式不可控，不支持折叠/展开。

**方案**: 引入 [markmap](https://markmap.js.org/) 作为思维导图渲染引擎。

**依赖**:
- `markmap-lib` — Markdown → markmap 数据转换
- `markmap-view` — SVG/交互渲染

**新增组件** — `src/components/markmap-block.tsx`:

```tsx
type MarkmapBlockProps = {
  code: string  // Markdown 层级文本
}
```

**渲染流程**:

```
Markdown 层级文本
  → markmap-lib Transformer.transform(code)
  → 获取 { root } 树结构
  → markmap-view Markmap.create(svgRef, options, root)
  → SVG 渲染到容器
  → 包装 DiagramViewer 提供全屏/缩放
```

**支持的 Markdown 语法**:

```markmap
# 中心主题
## 一级分支
### 二级分支
#### 三级分支
- 叶子节点
- 另一个叶子
## 另一个一级分支
- [链接文字](https://example.com)
```

**特性**:
- 默认适配容器宽度
- 节点可折叠/展开（markmap-view 内置支持）
- 支持链接、粗体、代码等行内 Markdown
- **必须懒加载**: `markmap-lib` 和 `markmap-view` 通过动态 `import()` 加载，不在首屏 bundle 中
- 渲染失败时降级为代码块（复用 MermaidBlock 的降级模式：`<pre><code>{原始 Markdown}</code></pre>`）
- 懒加载模块缓存: 加载成功后缓存引用，后续渲染不再重复加载（同 MermaidBlock 的 `mermaidPromise` 模式）

**AI 输出格式变更**:

| 场景 | 当前输出 | 新输出 |
|------|----------|--------|
| AI 思维导图 | ` ```mermaid\nmindmap\n  root((主题))\n` ` ` | ` ```markmap\n# 主题\n## 分支1\n### 子项\n` ` ` |
| 工具栏插入 | ` ```mermaid\nmindmap\n` ` ` 模板 | ` ```markmap\n# 主题\n## 分支1\n` ` ` 模板 |
| 斜杠命令 | `mindmap` → Mermaid mindmap | `mindmap` → Markmap Markdown |

**向后兼容**:
- 旧笔记中的 ` ```mermaid\nmindmap\n` ` ` 仍由 `MermaidBlock` 渲染（Mermaid 11.15.0 原生支持）
- `use-markdown-render.tsx` 中同时检测 `mermaid` 和 `markmap` 代码块
- 新建/编辑思维导图时默认使用 Markmap 语法

**Markdown 渲染管线修改**:

实际管线分两层:

1. **`markdown-renderer.ts`** (`src/lib/markdown-renderer.ts`): 预处理阶段。`renderer.code` 中检测 `codeToken.lang === 'mermaid'`，输出 `<div class="mermaid">` 包裹转义后的代码（`markdown-renderer.ts:463-467`）。其他代码块走 shiki 高亮。结果存入 `codeBlockMap`，输出为 `<div class="ag-code-block" data-code="...">` 占位符。

2. **`use-markdown-render.tsx`** (`src/hooks/use-markdown-render.tsx`): 后处理阶段。两处检测 Mermaid:
   - 第 74 行: `domNode.attribs?.class?.includes('mermaid')` — 处理 `<div class="mermaid">` 直接渲染
   - 第 97 行: `block.preHtml.includes('class="mermaid"')` — 处理 codeBlock placeholder 中的 mermaid

**集成 markmap/chart 的修改点**:

```typescript
// markdown-renderer.ts — 增加 markmap/chart 语言检测
if (codeToken.lang === 'mermaid') { /* 现有 */ }
else if (codeToken.lang === 'markmap') {
  const escaped = escapeHtml(originalCode)
  codeBlockMap.set(key, { html: `<div class="markmap">${escaped}</div>`, original: originalCode })
  codeToken.text = key
}
else if (codeToken.lang === 'chart') {
  const escaped = escapeHtml(originalCode)
  codeBlockMap.set(key, { html: `<div class="chart">${escaped}</div>`, original: originalCode })
  codeToken.text = key
}

// use-markdown-render.tsx — 增加 markmap/chart div 检测 (line 74 附近)
if (domNode.attribs?.class?.includes('markmap')) { return <MarkmapBlock code={decoded} /> }
if (domNode.attribs?.class?.includes('chart')) { return <ChartBlock code={decoded} /> }

// use-markdown-render.tsx — 增加 codeBlock placeholder 检测 (line 97 附近)
if (block.preHtml.includes('class="markmap"')) { return <MarkmapBlock code={block.code} /> }
if (block.preHtml.includes('class="chart"')) { return <ChartBlock code={block.code} /> }
```

**修改文件**:
- `src/components/markmap-block.tsx` — 新建
- `src/hooks/use-markdown-render.tsx` — 增加 markmap/chart 检测分支
- `src/lib/markdown-renderer.ts` — 增加 markmap/chart 语言检测
- `src/app/write-note/components/note-toolbar.tsx` — 思维导图模板改为 Markmap
- `src/app/write-note/components/slash-command-menu.tsx` — mindmap 命令改为 Markmap
- `backend/app/services/ai_polish_service.py` — mindmap prompt 输出 Markmap Markdown

---

### 3.2 图表渲染：ECharts 数据图表

**背景**: 当前无数据图表能力。错题分布、复习趋势、知识点统计只能用纯 CSS 柱状图或表格。

**方案**: 引入 ECharts 作为数据图表渲染引擎。

**依赖**:
- `echarts` — 核心图表库
- `echarts-for-react` — React 封装

**新增组件** — `src/components/chart-block.tsx`:

```tsx
type ChartBlockProps = {
  option: EChartsOption  // ECharts 配置
  title?: string
  height?: number        // 默认 400
}
```

**支持的图表类型**:

| 类型 | ECharts type | 使用场景 |
|------|-------------|----------|
| 柱状图 | `bar` | 错题按科目分布、按难度分布 |
| 折线图 | `line` | 复习趋势、新增错题趋势 |
| 饼图 | `pie` | 知识点分布、掌握程度分布 |
| 雷达图 | `radar` | 多维度能力评估 |

**Markdown 中的图表语法**:

采用 JSON 配置块语法：

````markdown
```chart
{
  "type": "bar",
  "title": "错题按科目分布",
  "xAxis": ["数学", "英语", "物理"],
  "series": [{ "name": "错题数", "data": [12, 8, 5] }]
}
```
````

**渲染流程**:

```
chart 代码块 (```chart)
  → markdown-renderer.ts: codeToken.lang === 'chart'
  → 输出 <div class="chart">{escaped JSON}</div>
  → use-markdown-render.tsx: class 包含 'chart' → <ChartBlock>
  → JSON.parse → 白名单校验 → 构建安全 ECharts option
  → <ReactEChartsCore option={option} />
```

**安全边界 — ChartBlock JSON 白名单**:

直接 `JSON.parse` 并透传任意 JSON 给 ECharts 有风险（超大配置、不可控样式、恶意脚本）。ChartBlock 必须做白名单校验：

```typescript
const ALLOWED_CHART_TYPES = ['bar', 'line', 'pie', 'radar'] as const
const ALLOWED_OPTION_KEYS = ['type', 'title', 'xAxis', 'yAxis', 'series', 'categories', 'legend', 'tooltip', 'data']

function parseChartOption(raw: string): SafeChartOption | null {
  try {
    const parsed = JSON.parse(raw)
    if (!ALLOWED_CHART_TYPES.includes(parsed.type)) return null
    // 只保留白名单字段，丢弃未知 key
    const safe: Record<string, unknown> = {}
    for (const key of ALLOWED_OPTION_KEYS) {
      if (key in parsed) safe[key] = parsed[key]
    }
    return safe as SafeChartOption
  } catch {
    return null
  }
}
```

- 只允许 4 种图表类型：`bar`、`line`、`pie`、`radar`
- 只保留白名单字段：`type`、`title`、`xAxis`/`yAxis`、`series`、`categories`、`legend`、`tooltip`、`data`
- 丢弃未知 key，防止注入自定义 ECharts 渲染逻辑
- `series.data` 限制最大长度（如 1000 项），防止超大数据导致卡顿
- 解析失败或校验不通过时降级为代码块

**ECharts 按需引入** (控制包大小):

```typescript
import * as echarts from 'echarts/core'
import { BarChart, LineChart, PieChart, RadarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, TitleComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([BarChart, LineChart, PieChart, RadarChart, GridComponent, TooltipComponent, LegendComponent, TitleComponent, CanvasRenderer])
```

**AI 输出格式变更**:

| 场景 | 当前输出 | 新输出 |
|------|----------|--------|
| AI 数据分析 | 无 | ` ```chart\n{ "type": "bar", ... }\n` ` ` |

**使用场景扩展**:
- 复习完成页 (`/mistakes/review`): 掌握程度分布图
- 错题列表页 (`/mistakes`): 按科目/难度分布图
- 知识库管家: 知识点覆盖雷达图

**修改文件**:
- `src/components/chart-block.tsx` — 新建
- `src/hooks/use-markdown-render.tsx` — 增加 chart 代码块检测
- `src/lib/markdown-renderer.ts` — 增加 chart 语言检测
- `src/app/write-note/components/note-toolbar.tsx` — 增加图表插入模板
- `src/app/write-note/components/slash-command-menu.tsx` — 增加 chart 命令
- `backend/app/services/ai_polish_service.py` — diagram prompt 输出 chart JSON

---

### 3.3 DiagramViewer 优化

**现状**: `DiagramViewer` (`src/components/diagram-viewer.tsx`) 已支持全屏 modal + 缩放 + 重置。

**需优化**:

| 项目 | 当前 | 目标 | 优先级 |
|------|------|------|--------|
| 容器适配 | preview 区域无宽度约束 | `max-w-full` + `overflow-hidden`，自动适配父容器 | P1 必做 |
| 全屏缩放 | 按钮缩放 0.5x-3x | 保持，增加"适配"按钮（fit to viewport） | P1 必做 |
| 下载 | SVG 可下载 data URL | 增加 PNG 下载（Canvas 转换） | P1 必做 |
| 移动端 | `w-[94vw] h-[92vh]` | 保持，增加 `touch-action: pan-x pan-y` | P1 必做 |
| 图表类型 | 仅 image/svg | ~~增加 `chart` kind~~ → 见下方"可选增强" | 可选 |

**关于 `kind: 'chart'`**:

~~原方案将 DiagramViewer 扩展为同时承担 image/svg/chart 三类渲染。~~

**修正**: ChartBlock 自身负责 ECharts 渲染和全屏预览，不需要 DiagramViewer 承担 chart 渲染职责。理由：
- DiagramViewer 当前只处理静态内容（SVG 字符串、图片 URL），chart 需要动态 ECharts 实例，职责不同
- ChartBlock 内部自己处理预览 + 全屏更简单，避免 DiagramViewer 变重
- 如果后续需要统一全屏交互（如缩放手势），可作为**可选增强**再扩展 DiagramViewer

**ChartBlock 自行处理全屏**:

```tsx
// chart-block.tsx 内部
function ChartBlock({ code }: { code: string }) {
  const option = parseChartOption(code)
  if (!option) return <CodeBlock>{code}</CodeBlock>
  return (
    <figure className='chart-viewer my-6 w-full'>
      <ReactEChartsCore option={buildEChartsOption(option)} style={{ height: 400 }} />
      <ChartToolbar onFullscreen={...} onDownload={...} />
    </figure>
  )
}
```

**修改文件**:
- `src/components/diagram-viewer.tsx` — image/svg 容器适配、fit 按钮、下载和移动端触摸优化；不增加 chart kind

---

## 4. P2 — 写作体验升级

### 4.1 工具栏增加可视化插入

**现状**: `NoteToolbar` 有"插入"下拉菜单，包含图表 (Mermaid)、对比块、思维导图 (Mermaid mindmap)、复习卡片。

**变更**:

| 菜单项 | 当前模板 | 新模板 |
|--------|----------|--------|
| 思维导图 | ` ```mermaid\nmindmap\n  root((主题))\n` ` ` | ` ```markmap\n# 主题\n## 分支1\n### 子项\n## 分支2\n` ` ` |
| 图表 | ` ```mermaid\ngraph TD\n` ` ` (流程图) | ` ```chart\n{\n  "type": "bar",\n  "title": "图表标题",\n  "xAxis": ["A", "B", "C"],\n  "series": [{ "name": "数据", "data": [10, 20, 15] }]\n}\n` ` ` |
| 对比块 | `:::compare\ntitle: ...\nleft: ...\nright: ...\n:::` | 改为更可读的模板，增加示例内容填充 |

**字体颜色色板**:

当前: 手写 `{red|文本}`

目标: 工具栏增加颜色选择按钮，点击弹出色板，选择后自动包裹选中文本。

**色板 UI**:

```
┌─────────────────────────┐
│ ● ● ● ● ● ● ● ●       │
│ 红 蓝 绿 黄 紫 橙 灰 粉 │
└─────────────────────────┘
```

8 色对应 `markdown-renderer.ts` 中已实现的 `COLOR_PALETTE` 白名单（`markdown-renderer.ts:124-133`）。

**交互流程**:
1. 用户选中文本
2. 点击工具栏"颜色"按钮
3. 弹出色板 popover
4. 点击色块 → `wrapSelection(`{${color}|`, `}`)` 
5. 未选中时点击 → 插入 `{red|示例文本}` 并选中"示例文本"

**对比块模板优化**:

当前模板:
```
:::compare
title: 对比标题
left: 选项A
right: 选项B
- 区别1
- 区别2
:::
```

优化为带示例内容的模板:
```
:::compare
title: 函数与方法对比
left: 函数
right: 方法
- 定义位置：函数独立定义，方法定义在类中
- 调用方式：函数直接调用，方法通过对象调用
- this 绑定：函数无 this，方法有 this
:::
```

**修改文件**:
- `src/app/write-note/components/note-toolbar.tsx` — 更新模板 + 增加颜色按钮

---

### 4.2 AI 写作助手输出格式更新

**现状**: `AIAssistantPanel` 有三组操作（选区操作、插入内容、全文处理），通过 `streamPolish` 调用后端。当前 `PolishAction` 有 14 个值，无 `data_chart`。

**变更**:

#### 思维导图输出

后端 `mindmap` action 的 system prompt 变更:

```
当前: "将以下内容整理为 Mermaid mindmap 语法。只返回 Mermaid 代码块，不要其他内容。"
目标: "将以下内容整理为 Markmap 思维导图的 Markdown 层级格式。
      使用 # 作为中心主题，## 作为一级分支，### 作为二级分支，以此类推。
      只返回 Markdown 层级文本，不要包含 ```markmap 代码块标记。"
```

前端插入时自动包裹 ` ```markmap\n...\n` ` `。

#### 数据分析输出

新增 `data_chart` action（避免与 `/api/ai/analyze` 错题分析接口混淆）:

```
System: "分析以下数据或文本中的量化信息，生成 ECharts 图表配置。
         返回 JSON 格式，包含 type (bar/line/pie/radar)、title、xAxis/categories、series。
         只返回 JSON，不要解释。"
```

前端插入时自动包裹 ` ```chart\n...\n` ` `。

#### 错题解析输出

后端错题解析 prompt 增强（如新增 `analyze_mistake` action）:

```
System: "分析以下错题，返回结构化 JSON：
{
  "error_reason": "错误原因",
  "key_steps": ["关键步骤1", "关键步骤2"],
  "knowledge_points": ["考点1", "考点2"],
  "traps": ["易错点1", "易错点2"],
  "similar_types": ["类似题型1的描述", "类似题型2的描述"],
  "review_advice": "复习建议"
}
只返回 JSON。"
```

**修改文件**:
- `backend/app/services/ai_polish_service.py` — 更新 mindmap prompt + 新增 data_chart/analyze_mistake prompt
- `backend/app/schemas/ai_polish.py` — PolishAction 枚举增加 `data_chart`（原命名 `analyze` 易与错题分析接口混淆）
- `src/lib/api/ai-polish.ts` — 前端类型同步
- `src/app/write-note/components/ai-assistant-panel.tsx` — 增加"数据分析"按钮

---

### 4.3 错题页 AI 分析入口增强

**背景**: `/write-mistake` 页面已有可视化 AI 分析面板，支持粘贴文本和上传图片，点击按钮触发分析。

**现状**: 已有"AI 分析错题"面板入口，用户粘贴文本或上传图片后点击按钮触发分析。分析结果自动填充表单字段（科目、难度、题目、我的答案、正确答案、解析、知识点）。

**需增强**:

| 项目 | 当前 | 目标 | 优先级 |
|------|------|------|--------|
| 状态反馈 | 有基础 loading | 显示分析中 spinner + 阶段文案（"正在识别题目..."、"正在生成解析..."） | P2 必做 |
| 失败提示 | 基础错误提示 | 分析失败时显示错误原因 + "重试"按钮 | P2 必做 |
| 图片上传 | 支持 | 增加拖拽上传区域 + "或粘贴图片" 提示优化 | P2 必做 |
| 分析结果预览 | 直接填充表单 | 先展示 AI 分析结果卡片，用户确认后再填充 | P2 增强（可后续迭代） |
| 重新分析 | 无 | 分析完成后可点击"重新分析"按钮 | P2 增强 |

**UI 设计**:

```
┌─────────────────────────────────────────┐
│  📷 拖拽上传错题图片                      │
│  ───────── 或 ─────────                  │
│  📝 在下方粘贴题目文本                    │
│  ┌─────────────────────────────────┐    │
│  │                                 │    │
│  └─────────────────────────────────┘    │
│                                         │
│  [🤖 AI 分析错题]                        │
│                                         │
│  ┌─ 分析结果预览 ──────────────────┐    │
│  │ 科目: 数学  难度: 中等           │    │
│  │ 错误原因: 对概念理解不清晰        │    │
│  │ 关键步骤: 第二步需要使用链式法则   │    │
│  │ 考点: 复合函数求导               │    │
│  │ 易错点: 混淆导数和微分           │    │
│  │ 复习建议: 建议 2 天后再次复习     │    │
│  │                                 │    │
│  │ [确认填充表单]  [重新分析]        │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

**与 AI 面板的关系**: 此入口独立于 `AIAssistantPanel`（写作助手），专门用于错题场景。不复用 AI 面板的 `streamPolish`，而是调用 `/api/ai/analyze` 接口。

**修改文件**:
- `src/app/write-mistake/page.tsx` — 增加可视化分析入口和结果预览

---

## 5. P3 — 空状态和反馈优化

### 5.1 列表空状态细分

**目标**: 统一空状态组件，按场景细分。

**新增组件** — `src/components/empty-state.tsx`:

```tsx
type EmptyStateVariant = 
  | 'no-content'      // 真无内容
  | 'no-results'      // 筛选为空
  | 'not-logged-in'   // 未登录
  | 'load-error'      // API 加载失败

type EmptyStateProps = {
  variant: EmptyStateVariant
  title?: string
  description?: string
  action?: { label: string; href?: string; onClick?: () => void }
  icon?: ReactNode
}
```

**各场景设计**:

| 场景 | 图标 | 标题 | 描述 | 操作按钮 |
|------|------|------|------|----------|
| `no-content` | `<FileText>` | 还没有内容 | 创建你的第一篇笔记开始记录 | "新建笔记" → `/write-note` |
| `no-results` | `<Search>` | 没有匹配结果 | 试试调整筛选条件或关键词 | "清除筛选" |
| `not-logged-in` | `<LogIn>` | 需要登录 | 登录后查看和管理你的内容 | "去登录" |
| `load-error` | `<AlertTriangle>` | 加载失败 | 网络异常或服务暂时不可用 | "重试" |

**样式**: 继承现有卡片风格 `rounded-xl border border-white/40 bg-white/60 backdrop-blur-sm`，居中布局，图标使用 `text-gray-300` 大号。

**替换策略 — 分 3 批，不一次性全量替换 36+ 处**:

| 批次 | 范围 | 文件数 | 验证方式 |
|------|------|--------|----------|
| 第一批 | `/notes`、`/mistakes`、`/manage` 核心列表页 | ~5 文件 | 核心工作流，手动验证 |
| 第二批 | `/blog`、`/share`、`/bloggers` 公开页面 | ~4 文件 | 公开页面，视觉检查 |
| 第三批 | 弹窗、管理子 tab、TOC、卡片等小区域 | ~15 文件 | 低风险，批量替换 |

每批完成后单独验证（tsc + 视觉检查），确认无回归再进入下一批。

**替换清单** (完整，按批次分):

**"暂无内容"类** (16 处):

| # | 批次 | 文件 | 行号 | 当前文案 | 设计 variant |
|---|:----:|------|------|----------|-------------|
| 1 | B1 | `notes/page.tsx` | 125 | 暂无内容 | `no-content` / `no-results`（根据 activeFilter） |
| 2 | B1 | `manage/page.tsx` | 164 | 暂无内容 | `no-content` / `no-results` |
| 3 | B1 | `mistakes/page.tsx` | 182 | 暂无错题 | `no-content` / `no-results` |
| 4 | B1 | `mistakes/page.tsx` | 131 | 暂无可归总的知识点 | `no-content`（内联子区域） |
| 5 | B2 | `blog/page.tsx` | 440 | 暂无文章 | `no-content` / `no-results` |
| 6 | B3 | `snippets/page.tsx` | 168 | 暂无内容 | `no-content` |
| 7 | B1 | `mistakes/review/page.tsx` | 74 | 所有错题都已复习完毕 | `no-content`（自定义，庆祝风格） |
| 8 | B1 | `suggestion-card.tsx` | 74 | 知识库状态良好 | `no-content`（积极文案） |
| 9 | B3 | `move-to-folder-dialog.tsx` | 124 | 暂无文件夹 | `no-content` |
| 10 | B3 | `recommendation-tab.tsx` | 113 | 今日暂无推荐 | `no-content` |
| 11 | B3 | `recommendation-tab.tsx` | 119 | 暂无历史记录 | `no-content` |
| 12 | B3 | `music-tab.tsx` | 86 | 暂无音乐 | `no-content` |
| 13 | B3 | `category-modal.tsx` | 96 | 暂无分类 | `no-content` |
| 14 | B3 | `category-modal.tsx` | 136 | 暂无文章 | `no-content` |
| 15 | B3 | `aritcle-card.tsx` | 56 | 暂无文章 | `no-content` |
| 16 | B3 | `blog-toc.tsx` | 69 | 暂无 | `no-content` |

**"筛选为空"类** (2 处):

| # | 批次 | 文件 | 行号 | 当前文案 |
|---|:----:|------|------|----------|
| 17 | B2 | `bloggers/grid-view.tsx` | 74-76 | 没有找到相关博主 |
| 18 | B2 | `share/grid-view.tsx` | 65-68 | 没有找到相关资源 |

**"加载/错误"类** (6 处):

| # | 批次 | 文件 | 行号 | 当前文案 | variant |
|---|:----:|------|------|----------|---------|
| 19 | B3 | `write-note/[slug]/page.tsx` | 197 | 未找到 | `load-error` |
| 20 | B1 | `note-detail-content.tsx` | 48 | 未找到 | `load-error` |
| 21 | B2 | `blog-detail-content.tsx` | 83-84 | 加载错误 | `load-error` |
| 22 | B1 | `manage/page.tsx` | 297 | 登录错误 | `load-error` |
| 23 | B3 | `music-form-modal.tsx` | 176 | 表单错误 | `load-error` |
| 24 | B3 | `ai-assistant-panel.tsx` | 228-234 | AI 错误 | `load-error` |

**未登录判断**: 通过现有 `useAuth` 或 `getMe()` 判断登录态，未登录时显示 `not-logged-in` variant。

**API 失败判断**: 列表 hook（SWR 或手动 fetch）的 `error` 状态触发 `load-error` variant。

**修改文件**:
- `src/components/empty-state.tsx` — 新建
- 上述 24+ 个文件 — 替换内联空状态

---

### 5.2 按钮反馈统一

**目标**: 统一按钮颜色语义。

**颜色规范**:

| 语义 | 样式 | 使用场景 |
|------|------|----------|
| 危险操作 | `bg-red-500/10 text-red-500 hover:bg-red-500/20` | 删除、批量删除、移除 |
| 主操作 | `bg-[var(--color-brand)]/10 text-[var(--color-brand)] hover:bg-[var(--color-brand)]/20` | 保存、发布、新建、确认 |
| 次级操作 | `bg-white/60 text-gray-600 hover:bg-white/80` | 取消、返回、关闭 |
| 品牌按钮 (实心) | `brand-btn` (现有 CSS 类) | 主 CTA 按钮 |

**图标按钮 hover 说明**:
- 所有图标按钮必须有 `title` 和 `aria-label` 属性
- `title` 在 hover 时显示浏览器原生 tooltip
- 无需额外 JS tooltip 库

**当前审计结果**:

| 页面 | 危险操作 | 主操作 | 次级操作 | 图标按钮 title/aria-label |
|------|----------|--------|----------|--------------------------|
| `/manage` | ✅ 已有红色样式 | ⚠️ 部分按钮无品牌色 | ✅ | ✅ |
| `/notes` 详情 | ✅ 删除按钮红色 | ⚠️ 编辑按钮无品牌色 | ✅ | ✅ |
| `/write-note` | ✅ | ✅ 保存按钮品牌色 | ✅ | ✅ 工具栏全部有 title/aria-label |
| `/blog` 列表 | ✅ | ⚠️ | ✅ | ⚠️ |
| NavCard | N/A | N/A | N/A | ❌ 所有 Link 缺失 aria-label/title |
| KnowledgeSidebar | N/A | N/A | N/A | ⚠️ 移动关闭按钮缺失 aria-label (`line 258`) |
| AI 面板 | ✅ 停止按钮红色 | ⚠️ 操作按钮无品牌色区分 | ✅ | ✅ |

**修改文件**:
- 各页面按钮样式统一（具体文件在 P4 UI 走查后确认）

---

## 6. P4 — 验证和文档

### 6.1 UI 走查清单

**桌面端**:

| 路由 | 检查项 |
|------|--------|
| `/` | NavCard 定位、active 胶囊、头像、导航链接、拖拽、玻璃卡片样式 |
| `/notes` | VerticalNav 显示、KnowledgeSidebar 布局、列表卡片、空状态、标签筛选 |
| `/mistakes` | VerticalNav 显示、复习规划卡片、薄弱点卡片、错题列表、空状态 |
| `/manage` | VerticalNav 显示、登录表单、内容表格、批量操作、空状态 |
| `/write-note` | mini NavCard、工具栏、斜杠命令、AI 面板、编辑/预览切换 |

**移动端** (宽度 < 640px):

| 路由 | 检查项 |
|------|--------|
| `/notes` | MobileNav 底部栏显示、抽屉展开、列表布局、文字溢出 |
| `/mistakes` | MobileNav、复习卡片布局、错题列表、空状态 |
| `/write-note` | 无 MobileNav（写作页）、工具栏换行、AI 面板底部抽屉 |

**重点检查**:
- [ ] 文字溢出: 长标题、长标签、长文件夹名
- [ ] 遮挡: 导航是否遮挡页面标题/搜索框/工具栏
- [ ] 按钮含义: 图标按钮是否有 title/aria-label
- [ ] 跳转明确: 链接跳转是否符合预期，返回按钮是否回到正确位置

### 6.2 文档更新

需更新的文档:

| 文档 | 更新内容 |
|------|----------|
| `docs/roadmap-tasks.md` | 新增 P-UI 阶段任务条目 |
| `docs/roadmap-design.md` | 新增交叉引用指向本文档 |
| `docs/ui-upgrade-design.md` | 本文档（新建） |

---

## 7. 文件变更总览

### 7.1 新建文件

| 文件 | 阶段 | 说明 |
|------|------|------|
| `src/components/vertical-nav.tsx` | P0 | 桌面端竖向导航栏 |
| `src/components/mobile-nav.tsx` | P0 | 移动端底部导航 |
| `src/components/markmap-block.tsx` | P1 | Markmap 思维导图渲染 |
| `src/components/chart-block.tsx` | P1 | ECharts 数据图表渲染 |
| `src/components/empty-state.tsx` | P3 | 统一空状态组件 |
| `docs/ui-upgrade-design.md` | P4 | 本文档 |

### 7.2 修改文件

| 文件 | 阶段 | 变更 |
|------|------|------|
| `src/components/nav-card.tsx` | P0 | `form === 'icons'` 时不渲染 |
| `src/layout/index.tsx` | P0 | 条件渲染 VerticalNav/MobileNav；移动端调整 ScrollTopButton 位置；不对全局 main 加 padding |
| `src/components/diagram-viewer.tsx` | P1 | image/svg 容器适配、下载、移动端触摸优化（不增加 chart kind，ChartBlock 自行处理图表全屏） |
| `src/hooks/use-markdown-render.tsx` | P1 | 增加 markmap/chart 代码块检测 |
| `src/lib/markdown-renderer.ts` | P1 | 增加 markmap/chart 语言检测 (`codeToken.lang === 'markmap'`/`'chart'` → `<div class="markmap">`/`<div class="chart">`) |
| `src/app/write-note/components/note-toolbar.tsx` | P1/P2 | 更新模板 + 颜色按钮 |
| `src/app/write-note/components/slash-command-menu.tsx` | P1 | 更新 mindmap 命令 + 增加 chart 命令 |
| `src/app/write-note/components/ai-assistant-panel.tsx` | P2 | 增加数据分析按钮 |
| `backend/app/schemas/ai_polish.py` | P2 | 增加 `data_chart` action |
| `backend/app/services/ai_polish_service.py` | P2 | 更新 mindmap prompt + 新增 `data_chart` prompt |
| `src/lib/api/ai-polish.ts` | P2 | 新 action 类型 |
| 第一批 (B1) | P3 | `/notes`、`/mistakes`、`/manage` 核心列表页（~5 文件） |
| 第二批 (B2) | P3 | `/blog`、`/share`、`/bloggers` 公开页面（~4 文件） |
| 第三批 (B3) | P3 | 弹窗、管理子 tab、TOC、卡片等小区域（~15 文件） |
| 各页面按钮 | P3 | 统一颜色语义 |

---

## 8. 依赖评估

| 包 | 大小 (min+gz) | 用途 | 必要性 |
|----|-------------|------|--------|
| `markmap-lib` | ~30KB | Markdown → markmap 数据 | P1 必要 |
| `markmap-view` | ~40KB | SVG/交互渲染 | P1 必要 |
| `echarts` | ~300KB (全量) / ~150KB (按需) | 数据图表 | P1 必要 |
| `echarts-for-react` | ~5KB | React 封装 | 便利层 |

**ECharts 按需引入**: 只注册 Bar/Line/Pie/Radar 四种图表 + Grid/Tooltip/Legend/Title 组件 + CanvasRenderer，控制在 ~150KB。

**与 AGENTS.md 一致性**: "不加大依赖"条款。ECharts 150KB 对于数据图表能力是合理代价。markmap 70KB 对于思维导图能力是合理代价。两者都是核心渲染能力，非工具类小依赖。

---

## 9. 开发顺序与依赖

```text
P0 (导航，全部可并行)
  9.1 VerticalNav 组件 ← 无依赖
  9.2 NavCard 裁剪 ← 无依赖
  9.3 Layout 集成 ← 9.1 + 9.2
  9.4 MobileNav 组件 ← 无依赖
  9.5 Layout 移动端集成 ← 9.4
  9.6 首页 NavCard 细节检查 ← 无依赖

P1 (渲染)
  9.7 MarkmapBlock 组件 ← npm install markmap-lib markmap-view
  9.8 Markdown 管线集成 markmap ← 9.7
  9.9 ChartBlock 组件 ← npm install echarts echarts-for-react
  9.10 Markdown 管线集成 chart ← 9.9
  9.11 DiagramViewer 优化 (image/svg 适配/下载/触摸) ← 无依赖
  9.12 工具栏/斜杠命令更新 ← 9.7 + 9.9

P2 (写作)
  9.13 后端 prompt 更新 ← 无依赖
  9.14 前端 AI 面板更新 ← 9.13
  9.15 颜色色板按钮 ← 无依赖
  9.16 对比块模板优化 ← 无依赖

P3 (空状态)
  9.17 EmptyState 组件 ← 无依赖
  9.18 页面替换 ← 9.17
  9.19 按钮颜色统一 ← 无依赖

P4 (验证)
  9.20 UI 走查 ← P0-P3 全部完成
  9.21 文档更新 ← 无依赖
```

---

## 10. 验证矩阵

| 阶段 | tsc --noEmit | 视觉检查 | 移动端检查 | ECharts 渲染 | Markmap 渲染 |
|------|:---:|:---:|:---:|:---:|:---:|
| P0 | ✅ | 桌面: /、/notes、/blog | 移动: /notes、/mistakes | — | — |
| P1 | ✅ | Markmap 渲染 | 移动端图表不溢出 | 柱/线/饼/雷达 | 折叠/展开 |
| P2 | ✅ | 色板/模板 | — | — | — |
| P3 | ✅ | 各空状态 | 移动端空状态 | — | — |
| P4 | 全量走查 | 全量 | 全量 | — | — |

---

## 11. 风险与回滚

| 阶段 | 主要风险 | 回滚方式 |
|------|----------|----------|
| P0 | VerticalNav 遮挡内容区 | 恢复 NavCard `form === 'icons'` 渲染 |
| P0 | MobileNav 遮挡编辑器工具栏 | 写作页条件排除已处理 |
| P1 | markmap 包体积过大 | 懒加载，失败降级为代码块 |
| P1 | ECharts 按需引入后缺组件 | 运行时按需补充注册 |
| P1 | 旧 Mermaid mindmap 不兼容 | 保留 MermaidBlock 不删除 |
| P2 | AI prompt 输出格式不稳定 | 前端增加格式校验和降级 |
| P3 | 空状态替换遗漏 | 逐一替换，每处可独立回滚 |

---

## 12. 差异分析报告（v1.1 补充）

> 基于代码逐行比对，以下为设计假设与实际代码的差异汇总。v1.1 已将关键修正内联到对应章节。

### 12.1 P0 导航差异

| # | 设计假设 | 实际代码 | 影响 | 修正 |
|---|----------|----------|------|------|
| D-01 | 笔记图标使用 `PenLine` (lucide-react) | 使用 `PenSVG` (`@/svgs/pen.svg`，自定义 SVG) | VerticalNav 需处理自定义 SVG 组件，不能假设都是 lucide-react | §2.1 已修正 |
| D-02 | `fullItemHeight = 42` | 实际为 `52` (`nav-card.tsx:95`) | 无关（仅影响首页 full 模式） | §2.2 已修正 |
| D-03 | `hoveredIndex` 初始值 `undefined` | 实际为 `0` (`nav-card.tsx:74`) | 首页默认高亮第一项 | §2.1 已修正 |
| D-04 | 胶囊渐变 `rgba(255,255,255,.86)` | 实际为 `linear-gradient(to right bottom, var(--color-border) 60%, var(--color-card) 100%)` | 使用 CSS 变量，更灵活 | §2.2 已修正 |
| D-05 | NavCard Link 有 aria-label/title | **全部缺失** (`nav-card.tsx:148, 182-191`) | 严重可访问性问题 | §2.1 已标注为修复项 |
| D-06 | KnowledgeSidebar 完善 | 移动关闭按钮缺失 aria-label (`line 258`) | 轻微 | §2.1 已标注 |
| D-07 | `nav-card.tsx:142-223` 代码范围 | 实际为 `127-199`（199 行非 228 行） | v1.0 行号偏差 | §2.1 已修正 |

### 12.2 P1 渲染管线差异

| # | 设计假设 | 实际代码 | 影响 | 修正 |
|---|----------|----------|------|------|
| D-08 | markmap 检测方式：`class.includes('markmap')` 在 `replace(domNode)` 中 | 实际管线分两层：`markdown-renderer.ts` 预处理 (`codeToken.lang` 检测) + `use-markdown-render.tsx` 后处理 (class 检测 + placeholder 检测) | 需在两层都添加 markmap/chart 分支 | §3.1 已重写集成方案 |
| D-09 | codeBlock placeholder 处理方式 | 实际使用 `ag-code-block` + `data-code` 属性模式，非简单 placeholder | 插入点更复杂 | §3.1 已修正代码路径 |
| D-10 | mermaid 检测仅在 `replace(domNode)` 中 | 实际有两处检测：line 74 (div class) 和 line 97 (preHtml in placeholder) | 两处都需添加 markmap/chart | §3.1 已修正 |

### 12.3 P2 写作工具差异

| # | 设计假设 | 实际代码 | 影响 | 修正 |
|---|----------|----------|------|------|
| D-11 | AI mindmap prompt 输出 Mermaid | **确认**：`"将以下内容整理为 Mermaid mindmap 语法。只返回 Mermaid 代码块"` | 需改为 Markmap Markdown | §4.2 已标注 |
| D-12 | 无 data_chart action | **确认**：PolishAction 有 14 值，无 `data_chart`（原名 `analyze` 易混淆） | 需新增为 `data_chart` | §4.2 已标注 |
| D-13 | PolishRequest 字段 | **确认**：`text`, `action`, `context`, `title`, `note_type`, `existing_tags` | 与设计一致 | 无需修正 |
| D-14 | SlashCommandMenu mindmap 命令 | **确认**：`insert: '```mermaid\nmindmap\n...'` (line 62) | 需改为 Markmap | §4.1 已标注 |

### 12.4 P3 空状态差异

| # | 设计假设 | 实际代码 | 影响 | 修正 |
|---|----------|----------|------|------|
| D-15 | 14+ 处空状态 | 实际 **36+ 处**（16 暂无 + 12 加载 + 2 筛选 + 6 错误） | 替换范围扩大 | §5.1 已补全清单 |
| D-16 | 统一 `text-gray-400` | 实际有 5 种样式模式（灰400/灰500/secondary/庆祝/绿色） | 统一工作量更大 | §5.1 已补全样式表 |
| D-17 | `blog/page.tsx:440` 使用 `text-gray-400` | 实际使用 `text-secondary` | 颜色 token 不一致 | §5.1 已标注 |
| D-18 | `category-modal` 为筛选为空 | 实际为"暂无分类"/"暂无文章"（真无内容场景） | variant 分类修正 | §5.1 已修正 |

### 12.5 无差异项（确认与设计一致）

| 章节 | 状态 |
|------|------|
| Layout 结构 (`src/layout/index.tsx`) | ✅ 与设计一致，NavCard 在 `<main>` 内，条件渲染逻辑清晰 |
| KnowledgeSidebar 结构 | ✅ 与设计一致，桌面端 `w-56` 固定侧栏，移动端抽屉 |
| NoteToolbar 内容块列表 | ✅ 4 项（图表/对比块/思维导图/复习卡片）与设计一致 |
| AI 面板分组 | ✅ 3 组（选区/插入/全文）与设计一致 |
| DiagramViewer 能力 | ✅ image/svg kind、全屏 modal、缩放 0.5x-3x、重置、关闭 |
| MermaidBlock 渲染 | ✅ 懒加载、SVG 输出、DiagramViewer 包装、失败降级 |
| COLOR_PALETTE | ✅ 8 色与设计一致 |
| CompareBlock 语法 | ✅ `:::compare` 已在 `markdown-renderer.ts` 实现 |
