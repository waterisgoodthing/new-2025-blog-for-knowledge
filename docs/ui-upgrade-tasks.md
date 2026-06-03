# UI 升级 — 任务清单

> 版本: 1.0
> 日期: 2026-06-03
> 关联: `docs/ui-upgrade-design.md` | `docs/ui-upgrade-requirements.md`

---

## 执行边界

1. 每次开发前先执行 `git status --short`。
2. 不回退用户已有改动。
3. 前端 API 调用优先走 `src/lib/api/*`。
4. 后端 router 保持 thin，复杂逻辑进入 `backend/app/services/`。
5. UI 变更必须符合半透明卡片、圆角、轻量动效和个人工作台风格。
6. 默认不 `git add`、`git commit`、`git push`。

---

## 阶段回滚策略

| 阶段 | 回滚方式 |
|------|----------|
| P0 导航 | 移除 VerticalNav/MobileNav 组件；恢复 NavCard `form === 'icons'` 渲染 |
| P1 渲染 | 移除 MarkmapBlock/ChartBlock 组件；注释 markdown-renderer 中新增的语言检测分支 |
| P2 写作 | 回退后端 prompt 修改；隐藏 AI 面板新增按钮 |
| P3 空状态 | 移除 EmptyState 组件；恢复各页面内联空状态 |

---

## 任务概览

| 阶段 | 任务范围 | 任务数 |
|------|---------|--------|
| P0 | 导航：VerticalNav + NavCard 裁剪 + MobileNav + Layout 集成 + 可访问性修复 + 验收 | 6 |
| P1 | 渲染：Markmap + ECharts + DiagramViewer + 管线集成 + 工具栏更新 + 验收 | 7 |
| P2 | 写作：AI prompt 更新 + AI 面板 + 错题 AI 增强 + 色板 + 对比块模板 + 验收 | 5 |
| P3 | 反馈：EmptyState 组件 + 分批替换 + 按钮统一 + 验收 | 4 |
| P4 | 最终走查 | 1 |
| **合计** | | **23** |

---

## 依赖关系图

```text
P0 (导航，全部可并行)
  T-U01 VerticalNav 组件 ← 无依赖
  T-U02 NavCard 裁剪 + 可访问性修复 ← 无依赖
  T-U03 MobileNav 组件 ← 无依赖
  T-U04 Layout 集成 ← T-U01 + T-U02 + T-U03
  T-U05 首页 NavCard 细节检查 ← 无依赖
  T-U06 P0 验收 ← T-U01~05

P1 (渲染)
  T-U07 安装依赖 + MarkmapBlock 组件 ← npm install markmap-lib markmap-view
  T-U08 Markdown 管线集成 markmap ← T-U07
  T-U09 安装依赖 + ChartBlock 组件 ← npm install echarts echarts-for-react
  T-U10 Markdown 管线集成 chart ← T-U09
  T-U11 DiagramViewer 优化 ← 无依赖
  T-U12 工具栏/斜杠命令更新 ← T-U07 + T-U09
  T-U21 P1 验收 ← T-U07~12

P2 (写作)
  T-U13 后端 AI prompt 更新 (data_chart + mindmap + analyze_mistake) ← 无依赖
  T-U14 前端 AI 面板更新 ← T-U13
  T-U15 错题 AI 分析入口增强 ← 无依赖
  T-U16 颜色色板 + 对比块模板优化 ← 无依赖
  T-U22 P2 验收 ← T-U13~16

P3 (空状态与反馈)
  T-U17 EmptyState 组件 ← 无依赖
  T-U18 分批替换空状态 ← T-U17
  T-U19 按钮颜色统一 ← 无依赖
  T-U23 P3 验收 ← T-U17~19

P4 (验证)
  T-U20 UI 走查与文档更新 ← T-U06 + T-U21 + T-U22 + T-U23
```

---

## 阶段 P0: 导航体验修复

目标：桌面端内页用竖向导航栏替换横向图标栏；移动端用底部标签栏；NavCard 只保留首页和写作页模式。

### T-U01: VerticalNav 组件

**影响域**: shared UI
**依赖**: 无
**关联需求**: FR-1.1 ~ FR-1.11
**文件范围**:

- `src/components/vertical-nav.tsx` (新建)

**子任务**:

- [ ] 新建 `VerticalNav` 组件，固定 `left-0 top-1/2 -translate-y-1/2 z-40`
- [ ] 默认 56px 只显示图标，hover 展开至 180px 显示图标 + 中文标签
- [ ] 展开动画: `motion animate={{ width }}` spring(400, 30)
- [ ] 7 个导航项: 首页、近期文章、笔记、错题集、关于网站、推荐分享、优秀博客
- [ ] 当前页高亮: `bg-[var(--color-brand)]/15` + 品牌色图标 + `motion layoutId` 胶囊滑动
- [ ] 头像区域: `/images/avatar.png` + 站点标题（展开时显示）
- [ ] 图标统一使用 `<Icon className='h-[18px] w-[18px]' />` 渲染
- [ ] 样式: `rounded-r-2xl border border-l-0 border-white/40 bg-white/70 backdrop-blur-xl shadow-lg`
- [ ] 所有链接 `aria-label` + `title`，`<nav>` 语义标签
- [ ] 在 `/write*` 路由下不显示（由 Layout 条件控制）

**验收标准**:

- 桌面端内页左侧显示竖向导航栏。
- hover 展开平滑，当前页高亮明显。
- 所有链接有 aria-label 和 title。
- 写作页和首页不显示此组件。

---

### T-U02: NavCard 裁剪 + 可访问性修复

**影响域**: shared UI, home
**依赖**: 无
**关联需求**: FR-2.1 ~ FR-2.5
**文件范围**:

- `src/components/nav-card.tsx`

**子任务**:

- [ ] `form === 'icons'` 分支开头加 `return null`
- [ ] **禁止改动** `form === 'full'`（首页）和 `form === 'mini'`（写作页）渲染逻辑
- [ ] **禁止改动** `HomeDraggableLayer` 的 `cardKey` 和定位计算逻辑
- [ ] 首页头像链接 (`line 148`) 补齐 `aria-label='返回首页'` + `title='返回首页'`
- [ ] 首页导航链接补齐 `aria-label={item.label}` + `title={item.label}`

**验收标准**:

- 内页不再显示横向图标栏。
- 首页 NavCard 行为完全不变（拖拽、定位、导航）。
- 写作页 mini NavCard 保留。
- 首页所有链接有 aria-label 和 title。

---

### T-U03: MobileNav 组件

**影响域**: shared UI
**依赖**: 无
**关联需求**: FR-3.1 ~ FR-3.10
**文件范围**:

- `src/components/mobile-nav.tsx` (新建)

**子任务**:

- [ ] 新建 `MobileNav` 组件，底部标签栏 4 个主入口 + "更多"按钮
- [ ] 仅在 `sm` 断点以下显示
- [ ] 固定底部 `fixed inset-x-0 bottom-0 z-50`
- [ ] 背景 `bg-white/80 backdrop-blur-xl border-t border-white/40`
- [ ] 底部安全区 `pb-[env(safe-area-inset-bottom)]`
- [ ] "更多"抽屉: 从底部弹出，含关于网站、推荐分享、优秀博客，点击遮罩关闭
- [ ] 当前页高亮: 品牌色图标 + 文字
- [ ] 所有链接 `aria-label` + `title`

**验收标准**:

- 移动端内页底部显示导航栏。
- "更多"抽屉正常展开/关闭。
- 不遮挡页面标题和搜索框。

---

### T-U04: Layout 集成

**影响域**: shared UI
**依赖**: T-U01, T-U02, T-U03
**关联需求**: FR-1.11, FR-3.7, FR-3.8, FR-3.9
**文件范围**:

- `src/layout/index.tsx`

**子任务**:

- [ ] 定义路由变量: `isHome = pathname === '/'`、`isWrite = pathname.startsWith('/write')`、`isInnerPage = !isHome && !isWrite`
- [ ] 引入 `VerticalNav`，条件渲染: `!maxSM && isInnerPage`
- [ ] 引入 `MobileNav`，条件渲染: `maxSM && isInnerPage`
- [ ] 移动端 ScrollTopButton 上移至 `bottom-20` 避免与 MobileNav 重叠
- [ ] 移动端 Toaster 位置改为 `top-center`
- [ ] 移动端内容区预留底部安全距离
- [ ] **不对全局 `<main>` 加 padding-left**

**验收标准**:

- 桌面端内页有竖向导航，首页和写作页无。
- 移动端内页有底部导航，写作页无。
- ScrollTopButton 和 MobileNav 不重叠。
- Toast 不被底部导航遮挡。

---

### T-U05: 首页 NavCard 细节检查

**影响域**: home
**依赖**: 无
**关联需求**: FR-2.5

**子任务**:

- [ ] 检查 active 胶囊在不同主题色下对比度
- [ ] 检查图标颜色可读性
- [ ] 检查文字截断（52px 行高下中文标签）
- [ ] 确保导航项列表与 VerticalNav 一致

**验收标准**:

- 首页 NavCard 视觉效果与内页 VerticalNav 语言统一。

---

### T-U06: P0 验收

**影响域**: shared UI
**依赖**: T-U01 ~ T-U05

**验证**:

- [ ] `npx tsc --noEmit`
- [ ] 桌面端: `/` NavCard 正常、`/notes` VerticalNav 显示、`/blog` VerticalNav 显示
- [ ] 移动端: `/notes` MobileNav 显示、`/write-note` 无 MobileNav
- [ ] 首页拖拽编辑功能正常
- [ ] 写作页 mini NavCard 正常
- [ ] 可访问性: 所有导航链接有 aria-label/title

---

## 阶段 P1: 笔记渲染升级

目标：思维导图切换到 Markmap，新增 ECharts 数据图表，优化 DiagramViewer。

### T-U07: 安装依赖 + MarkmapBlock 组件

**影响域**: notes, markdown
**依赖**: `npm install markmap-lib markmap-view`
**关联需求**: FR-4.1 ~ FR-4.9
**文件范围**:

- `package.json` — 新增依赖
- `package-lock.json` — lockfile 自动更新
- `src/components/markmap-block.tsx` (新建)

**子任务**:

- [ ] 安装: `npm install markmap-lib markmap-view`
- [ ] 新建 `MarkmapBlock` 组件，接收 `code: string`
- [ ] 渲染: `Transformer.transform(code)` → `{ root }` → `Markmap.create(svgRef, options, root)`
- [ ] **必须懒加载**: 动态 `import('markmap-lib')` 和 `import('markmap-view')`
- [ ] 模块缓存: 加载成功后缓存引用（同 `mermaidPromise` 模式）
- [ ] 渲染失败降级为 `<pre><code>{原始 Markdown}</code></pre>`
- [ ] 默认适配容器宽度
- [ ] 节点可折叠/展开
- [ ] MarkmapBlock 自行处理全屏和缩放（不强依赖 DiagramViewer）

**验收标准**:

- ` ```markmap\n# 主题\n## 分支\n` ` ` 正确渲染为思维导图。
- 节点可折叠展开。
- 渲染失败降级为代码块。
- 首屏 bundle 不包含 markmap。

---

### T-U08: Markdown 管线集成 markmap

**影响域**: notes, markdown
**依赖**: T-U07
**关联需求**: FR-4.10, FR-4.11, FR-4.12
**文件范围**:

- `src/lib/markdown-renderer.ts`
- `src/hooks/use-markdown-render.tsx`

**子任务**:

- [ ] `markdown-renderer.ts`: `codeToken.lang === 'markmap'` → `<div class="markmap">${escaped}</div>`
- [ ] `use-markdown-render.tsx`: `domNode.attribs?.class?.includes('markmap')` → `<MarkmapBlock>`
- [ ] `use-markdown-render.tsx`: `block.preHtml.includes('class="markmap"')` → `<MarkmapBlock>`
- [ ] 旧 `mermaid mindmap` 代码块仍由 `MermaidBlock` 渲染（向后兼容）

**验收标准**:

- 新建 markmap 代码块在详情页和编辑预览中正确渲染。
- 旧 mermaid mindmap 不受影响。

---

### T-U09: 安装依赖 + ChartBlock 组件

**影响域**: notes, markdown, mistakes, review
**依赖**: `npm install echarts echarts-for-react`
**关联需求**: FR-5.1 ~ FR-5.9
**文件范围**:

- `package.json` — 新增依赖
- `package-lock.json` — lockfile 自动更新
- `src/components/chart-block.tsx` (新建)

**子任务**:

- [ ] 安装: `npm install echarts echarts-for-react`
- [ ] ECharts 按需引入: Bar/Line/Pie/Radar + Grid/Tooltip/Legend/Title + CanvasRenderer
- [ ] 新建 `ChartBlock` 组件，接收 JSON 配置字符串
- [ ] **安全边界**: 白名单类型 (`bar`/`line`/`pie`/`radar`) + 白名单字段 + `series.data` 长度限制 (1000)
- [ ] 解析失败或校验不通过降级为代码块
- [ ] 默认高度 400px，自适应容器宽度
- [ ] 主题适配: 使用 `--color-brand` 作为主色调
- [ ] ChartBlock 自行处理全屏和下载（不扩展 DiagramViewer）

**验收标准**:

- ` ```chart\n{"type":"bar",...}\n` ` ` 正确渲染为图表。
- 4 种图表类型均正确渲染。
- 非白名单 JSON 降级为代码块。
- 超大数据不导致卡顿。

---

### T-U10: Markdown 管线集成 chart

**影响域**: notes, markdown
**依赖**: T-U09
**关联需求**: FR-5.10, FR-5.11
**文件范围**:

- `src/lib/markdown-renderer.ts`
- `src/hooks/use-markdown-render.tsx`

**子任务**:

- [ ] `markdown-renderer.ts`: `codeToken.lang === 'chart'` → `<div class="chart">${escaped}</div>`
- [ ] `use-markdown-render.tsx`: `domNode.attribs?.class?.includes('chart')` → `<ChartBlock>`
- [ ] `use-markdown-render.tsx`: `block.preHtml.includes('class="chart"')` → `<ChartBlock>`

**验收标准**:

- chart 代码块在笔记详情页和编辑预览中正确渲染。

---

### T-U11: DiagramViewer 适配优化

**影响域**: shared UI
**依赖**: 无
**关联需求**: FR-6.1 ~ FR-6.5
**文件范围**:

- `src/components/diagram-viewer.tsx`

**子任务**:

- [ ] preview 区域增加 `max-w-full overflow-hidden`
- [ ] 全屏 modal 增加"适配"按钮（fit to viewport）
- [ ] SVG → PNG 下载 best-effort；失败时保留 SVG 下载并提示用户
- [ ] 移动端全屏 modal 增加 `touch-action: pan-x pan-y`
- [ ] **不增加 `kind: 'chart'`**

**验收标准**:

- Mermaid/SVG 图谱默认适配容器，不溢出。
- 全屏查看支持缩放、适配、下载。
- 移动端 SVG/图片查看无横向溢出。

---

### T-U12: 工具栏/斜杠命令更新

**影响域**: notes
**依赖**: T-U07, T-U09
**关联需求**: FR-7.1, FR-7.2, FR-7.7, FR-7.8
**文件范围**:

- `src/app/write-note/components/note-toolbar.tsx`
- `src/app/write-note/components/slash-command-menu.tsx`

**子任务**:

- [ ] `NoteToolbar` 插入菜单: 思维导图模板改为 Markmap Markdown
- [ ] `NoteToolbar` 插入菜单: 图表模板改为 chart JSON
- [ ] `SlashCommandMenu`: `mindmap` 命令改为 Markmap Markdown
- [ ] `SlashCommandMenu`: 增加 `chart` 命令
- [ ] 保留旧 Mermaid 流程图模板 (`graph TD`) 不变

**验收标准**:

- 工具栏插入思维导图为 Markmap 语法。
- 工具栏插入图表为 chart JSON 语法。
- 斜杠命令同步更新。

---

### T-U21: P1 验收

**影响域**: notes, markdown
**依赖**: T-U07 ~ T-U12

**验证**:

- [ ] `npx tsc --noEmit`
- [ ] `npm install markmap-lib markmap-view echarts echarts-for-react` 后无报错
- [ ] Markmap 代码块在详情页正确渲染，节点可折叠展开
- [ ] 旧 Mermaid mindmap 代码块仍正常渲染
- [ ] Chart 代码块 4 种图表类型均正确渲染
- [ ] 非白名单 JSON 降级为代码块
- [ ] 工具栏插入思维导图为 Markmap 语法
- [ ] 工具栏插入图表为 chart JSON 语法
- [ ] 斜杠命令 `/mindmap` 和 `/chart` 正常
- [ ] DiagramViewer SVG/图片全屏、缩放、下载正常
- [ ] 移动端图表和图谱不溢出

---

## 阶段 P2: 写作体验升级

目标：AI 输出格式更新、错题 AI 入口增强、颜色色板、对比块模板优化。

### T-U13: 后端 AI prompt 更新

**影响域**: AI, notes
**依赖**: 无
**关联需求**: FR-8.1, FR-8.2, FR-8.3, FR-8.7
**文件范围**:

- `backend/app/schemas/ai_polish.py`
- `backend/app/services/ai_polish_service.py`

**子任务**:

- [ ] `PolishAction` 枚举增加 `data_chart`（不使用 `analyze`，避免与错题分析接口混淆）
- [ ] `mindmap` prompt 改为输出 Markmap Markdown 层级（非 Mermaid 语法）
- [ ] 新增 `data_chart` prompt: 输出 ECharts chart JSON 配置
- [ ] 验证新 action 的 SSE 流正常返回

**验收标准**:

- `mindmap` action 返回 `# 主题\n## 分支` 格式。
- `data_chart` action 返回 `{"type":"bar",...}` 格式。
- 原有 14 个 action 不受影响。

---

### T-U14: 前端 AI 面板更新

**影响域**: notes
**依赖**: T-U13
**关联需求**: FR-8.4, FR-8.5, FR-8.6
**文件范围**:

- `src/lib/api/ai-polish.ts`
- `src/app/write-note/components/ai-assistant-panel.tsx`

**子任务**:

- [ ] `ai-polish.ts` 类型增加 `data_chart`
- [ ] AI 面板"插入内容"分组增加"数据分析"按钮
- [ ] AI 思维导图结果前端自动包裹 ` ```markmap\n...\n` ` `
- [ ] AI 数据分析结果前端自动包裹 ` ```chart\n...\n` ` `

**验收标准**:

- 面板显示"数据分析"按钮。
- 思维导图结果插入后可直接渲染。
- 数据分析结果插入后可直接渲染。

---

### T-U15: 错题 AI 分析入口增强

**影响域**: mistakes
**依赖**: 无
**关联需求**: FR-9.1 ~ FR-9.5
**文件范围**:

- `src/app/write-mistake/page.tsx`

**子任务**:

**必做**:
- [ ] 在非流式接口返回前展示轮换式阶段文案（不代表后端真实阶段）
- [ ] 分析失败时显示错误原因 + "重试"按钮
- [ ] 优化图片拖拽上传区域文案与粘贴图片提示

**可选增强（不阻塞本轮验收，可后续迭代）**:
- [ ] 分析结果预览卡片 + 确认填充
- [ ] 分析完成后"重新分析"按钮

**验收标准**:

- 分析中有明确等待反馈。
- 失败有错误提示和重试按钮。
- 可选增强不计入本轮验收。

---

### T-U16: 颜色色板 + 对比块模板优化

**影响域**: notes
**依赖**: 无
**关联需求**: FR-7.3 ~ FR-7.6
**文件范围**:

- `src/app/write-note/components/note-toolbar.tsx`

**子任务**:

- [ ] 工具栏增加颜色选择按钮，弹出 8 色色板（red/blue/green/yellow/purple/orange/gray/pink）
- [ ] 选中文本后点击色块 → `wrapSelection(`{${color}|`, `}`)` 
- [ ] 未选中时点击 → 插入 `{red|示例文本}` 并选中"示例文本"
- [ ] 对比块模板改为带示例内容的可读版本

**验收标准**:

- 颜色色板可选择 8 色，插入正确语法。
- 对比块模板含具体示例而非占位符。

---

### T-U22: P2 验收

**影响域**: notes, mistakes, AI
**依赖**: T-U13 ~ T-U16

**验证**:

- [ ] `npx tsc --noEmit`
- [ ] 后端 import/start check
- [ ] AI `mindmap` action 返回 Markmap Markdown 格式
- [ ] AI `data_chart` action 返回 chart JSON 格式
- [ ] AI 面板"数据分析"按钮可点击，结果插入后可渲染
- [ ] AI 思维导图结果插入后可直接渲染
- [ ] 错题 AI 分析中有轮换式等待文案
- [ ] 错题 AI 分析失败有错误提示和重试按钮
- [ ] 颜色色板 8 色均可选择并插入正确语法
- [ ] 对比块模板含具体示例

---

## 阶段 P3: 空状态和反馈优化

目标：统一空状态组件，分批替换；统一按钮颜色语义。

### T-U17: EmptyState 组件

**影响域**: shared UI
**依赖**: 无
**关联需求**: FR-10.1, FR-10.2, FR-10.3
**文件范围**:

- `src/components/empty-state.tsx` (新建)

**子任务**:

- [ ] 新建 `EmptyState` 组件，支持 4 种 variant: `no-content`、`no-results`、`not-logged-in`、`load-error`
- [ ] 每种 variant 有对应图标、标题、描述、操作按钮
- [ ] 样式: `rounded-xl border border-white/40 bg-white/60 backdrop-blur-sm`
- [ ] 支持自定义标题、描述、操作按钮覆盖

**验收标准**:

- 4 种 variant 均正确渲染。
- 样式与现有玻璃卡片风格一致。

---

### T-U18: 分批替换空状态

**影响域**: notes, mistakes, manage, blog, share, bloggers, snippets
**依赖**: T-U17
**关联需求**: FR-10.4 ~ FR-10.7
**文件范围**: 见设计文档 §5.1 完整清单（36+ 处）

**子任务**:

- [ ] **第一批 (B1)**: `/notes`、`/mistakes`、`/manage` 核心列表页（~7 文件/区域）
  - `src/app/notes/page.tsx:125`
  - `src/app/manage/page.tsx:164`
  - `src/app/mistakes/page.tsx:131, 182`
  - `src/app/mistakes/review/page.tsx:74`
  - `src/app/notes/components/suggestion-card.tsx:74`
  - `src/app/notes/[id]/note-detail-content.tsx:48`
  - `src/app/manage/page.tsx:297`
- [ ] B1 完成后 `npx tsc --noEmit` + 视觉检查
- [ ] **第二批 (B2)**: `/blog`、`/share`、`/bloggers` 公开页面（~4 文件）
  - `src/app/blog/page.tsx:440`
  - `src/app/blog/[id]/blog-detail-content.tsx:83`
  - `src/app/bloggers/grid-view.tsx:74`
  - `src/app/share/grid-view.tsx:65`
- [ ] B2 完成后视觉检查
- [ ] **第三批 (B3)**: 弹窗、管理子 tab、TOC、卡片等小区域（~13 文件）
  - `src/app/snippets/page.tsx:168`
  - `src/components/move-to-folder-dialog.tsx:124`
  - `src/app/manage/recommendation-tab.tsx:113, 119`
  - `src/app/manage/music-tab.tsx:86`
  - `src/app/blog/components/category-modal.tsx:96, 136`
  - `src/app/(home)/aritcle-card.tsx:56`
  - `src/components/blog-toc.tsx:69`
  - `src/app/write-note/[slug]/page.tsx:197`
  - `src/app/manage/music-form-modal.tsx:176`
  - `src/app/write-note/components/ai-assistant-panel.tsx:228`
- [ ] B3 完成后 `npx tsc --noEmit`

**验收标准**:

- 核心页面空状态有明确引导操作。
- 真无内容 vs 筛选为空显示不同文案和按钮。
- 每批完成后无 tsc 错误。

---

### T-U19: 按钮颜色统一

**影响域**: manage, notes, mistakes, blog, shared UI
**依赖**: 无
**关联需求**: FR-11.1 ~ FR-11.5

**子任务**:

- [ ] 审计知识系统核心页面删除按钮，统一为 `bg-red-500/10 text-red-500 hover:bg-red-500/20`
- [ ] 审计主操作按钮，统一为品牌色
- [ ] 审计次级操作按钮，统一为弱化样式
- [ ] KnowledgeSidebar 移动关闭按钮补齐 `aria-label='关闭导航'`
- [ ] 审计所有图标按钮确保有 `title` + `aria-label`

**验收标准**:

- 危险操作按钮视觉一致（红色弱背景）。
- 所有图标按钮有 title 和 aria-label。

---

### T-U23: P3 验收

**影响域**: notes, mistakes, manage, blog, shared UI
**依赖**: T-U17 ~ T-U19

**验证**:

- [ ] `npx tsc --noEmit`
- [ ] B1 核心页面空状态显示正确引导操作
- [ ] B2 公开页面空状态显示正确
- [ ] B3 小区域空状态显示正确
- [ ] 真无内容 vs 筛选为空显示不同文案和按钮
- [ ] 危险操作按钮视觉一致（红色弱背景）
- [ ] 主操作按钮品牌色
- [ ] 所有图标按钮有 title 和 aria-label

---

## 阶段 P4: 最终走查

### T-U20: UI 走查与文档更新

**影响域**: 全部
**依赖**: T-U06 + T-U21 + T-U22 + T-U23

**子任务**:

- [ ] 桌面端走查: `/`、`/notes`、`/mistakes`、`/manage`、`/write-note`
- [ ] 移动端走查: `/notes`、`/mistakes`、`/write-note`
- [ ] 检查文字溢出、遮挡、按钮含义、跳转是否明确
- [ ] 确认 `docs/ui-upgrade-design.md` 与实际实现一致

**验收标准**:

- 桌面端和移动端走查无明显 UI 问题。
- 文档与实现一致。
