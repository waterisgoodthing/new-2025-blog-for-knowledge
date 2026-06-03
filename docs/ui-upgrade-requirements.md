# UI 升级 — 需求文档

> 版本: 1.0
> 日期: 2026-06-03
> 关联设计文档: `docs/ui-upgrade-design.md`

---

## 1. 项目背景

### 1.1 现状问题

当前系统 UI 层存在以下不足：

| 问题 | 影响 |
|------|------|
| 内页导航为横向图标栏，无文字说明 | 新用户难理解各入口含义 |
| 移动端图标栏居中浮在顶部 | 遮挡页面标题和搜索框 |
| 思维导图依赖 Mermaid mindmap | 节点多时布局差、样式不可控、不支持折叠展开 |
| 无数据图表能力 | 错题分布和复习趋势只能用纯 CSS 或表格 |
| 字体颜色靠手写 `{red\|文本}` | 无可视化色板，学习成本高 |
| AI 思维导图输出仍为 Mermaid 语法 | 与新的 Markmap 渲染引擎不匹配 |
| AI 错题解析输出结构不完整 | 缺考点、易错点、类似题型 |
| 空状态全部为内联 JSX | 不区分"无内容"/"筛选为空"/"未登录"/"API 失败"，无引导操作 |
| 按钮颜色语义不统一 | 危险操作有时红色有时灰色，主操作无品牌色 |
| NavCard 所有 Link 缺失 aria-label/title | 严重可访问性问题 |

### 1.2 目标

| 维度 | 当前 | 目标 |
|------|------|------|
| 桌面端内页导航 | 横向图标栏 | 左侧竖向导航栏，默认紧凑，hover 展开 |
| 移动端内页导航 | 横向图标栏居中 | 底部标签栏 + "更多"抽屉 |
| 思维导图 | Mermaid mindmap | Markmap（懒加载、可折叠、失败降级） |
| 数据图表 | 无 | ECharts（柱状图、折线图、饼图、雷达图） |
| 字体颜色 | 手写语法 | 工具栏色板选择 |
| AI 思维导图输出 | Mermaid 语法 | Markmap Markdown 层级 |
| AI 数据分析输出 | 无 | chart JSON 配置 |
| 空状态 | 16 处内联"暂无" | 统一组件 × 4 种 variant |
| 按钮反馈 | 不统一 | 危险红、主操作品牌色、次级弱化 |

### 1.3 范围

**本需求覆盖**:
- 全局内页导航重构（桌面竖向 + 移动端底部）
- 首页 NavCard 收敛和可访问性修复
- Markmap 思维导图渲染
- ECharts 数据图表渲染
- DiagramViewer 适配优化
- 写作工具栏色板和模板升级
- AI 写作助手输出格式更新
- 错题 AI 分析入口增强
- 统一空状态组件
- 按钮颜色语义统一

**本阶段暂不覆盖**:
- 首页布局编辑功能改造
- 完整块编辑器替换 Markdown
- 新增后端数据模型
- 新增 API 端点（除 AI polish action 扩展）
- 多用户协作

---

## 2. 用户故事

### US-1: 快速理解内页导航

作为用户，我希望打开内页时看到左侧竖向导航栏，只显示图标，hover 后显示中文名称，这样我能快速理解每个入口的含义并跳转到目标页面。

### US-2: 移动端便捷导航

作为移动端用户，我希望在页面底部看到固定的导航标签栏，这样我不需要滚动到顶部就能切换页面。

### US-3: 思维导图可视化

作为知识整理者，我希望在笔记中用 Markdown 层级语法写思维导图，系统自动渲染为可折叠展开的交互式思维导图，这样我能看到知识结构全貌。

### US-4: 数据图表

作为错题复习者，我希望在笔记中嵌入柱状图、饼图等数据图表，可视化展示错题分布和复习趋势，这样我能更直观地了解薄弱环节。

### US-5: 可视化字体颜色

作为写作者，我希望通过工具栏色板选择字体颜色，而不是手写 `{red|文本}` 语法，这样更直观高效。

### US-6: AI 输出格式匹配

作为用户，我希望 AI 生成的思维导图直接使用 Markmap 语法、数据分析直接输出 chart 配置，这样插入笔记后能直接渲染，不需要手动转换格式。

### US-7: 清晰的空状态引导

作为用户，我希望当列表为空时看到明确的说明和下一步操作按钮（如"新建笔记"），而不是只有"暂无内容"四个字。

---

## 3. 功能需求

### FR-1: 桌面端竖向导航栏

**优先级**: P0

**描述**: 在桌面端内页（非首页、非写作页）显示左侧竖向导航栏，替换当前横向图标栏。

| 编号 | 需求 | 验收标准 |
|------|------|---------|
| FR-1.1 | 新建 `VerticalNav` 组件，固定在 `left-0 top-1/2 -translate-y-1/2 z-40` | 组件渲染在页面左侧中央 |
| FR-1.2 | 默认宽度 56px，只显示图标（18×18） | 未 hover 时仅显示图标 |
| FR-1.3 | hover 展开至 180px，显示图标 + 中文标签 | 展开动画 spring(400, 30) 平滑 |
| FR-1.4 | 当前页高亮：品牌色半透明背景 + 品牌色图标 + `motion layoutId` 胶囊滑动 | 切换页面时胶囊平滑滑动到新位置 |
| FR-1.5 | 导航项：首页、近期文章、笔记、错题集、关于网站、推荐分享、优秀博客 | 7 个入口均可点击跳转 |
| FR-1.6 | 头像区域：复用站点头像 + 标题（展开时显示） | 点击头像跳转首页 |
| FR-1.7 | 所有链接有 `aria-label` 和 `title` 属性 | 无障碍审计通过 |
| FR-1.8 | 使用 `<nav>` 语义标签 | 语义正确 |
| FR-1.9 | 图标统一使用 `<Icon className='h-[18px] w-[18px]' />` 渲染 | 自定义 SVG 和 lucide-react 图标均正常显示 |
| FR-1.10 | 样式：`rounded-r-2xl border border-l-0 border-white/40 bg-white/70 backdrop-blur-xl shadow-lg` | 与现有玻璃卡片风格统一 |
| FR-1.11 | 在 `/write*` 路由下不显示 | 写作页仅有 mini NavCard |

---

### FR-2: NavCard 裁剪

**优先级**: P0

**描述**: NavCard 在 `form === 'icons'` 时不再渲染，由 VerticalNav 接管。

| 编号 | 需求 | 验收标准 |
|------|------|---------|
| FR-2.1 | `form === 'icons'` 分支开头加 `return null` | 内页不再显示横向图标栏 |
| FR-2.2 | **禁止改动** `form === 'full'`（首页）渲染逻辑 | 首页 NavCard 行为不变，拖拽编辑正常 |
| FR-2.3 | **禁止改动** `form === 'mini'`（写作页）渲染逻辑 | 写作页 64×64 头像卡片保留 |
| FR-2.4 | `HomeDraggableLayer` 的 `cardKey`、定位计算逻辑不得修改 | 首页布局编辑功能不受影响 |
| FR-2.5 | 首页 NavCard 补齐链接的 `aria-label` 和 `title` | 首页头像链接有 `aria-label='返回首页'` |

---

### FR-3: 移动端底部导航

**优先级**: P0

**描述**: 移动端内页显示底部标签栏 + "更多"抽屉。

| 编号 | 需求 | 验收标准 |
|------|------|---------|
| FR-3.1 | 新建 `MobileNav` 组件，底部标签栏 4 个主入口 + "更多"按钮 | 首页、文章、笔记、错题 + 更多 |
| FR-3.2 | 仅在 `sm` 断点以下显示 | 桌面端不显示 |
| FR-3.3 | 固定底部 `fixed inset-x-0 bottom-0 z-50` | 不随页面滚动 |
| FR-3.4 | 背景 `bg-white/80 backdrop-blur-xl border-t border-white/40` | 半透明玻璃风格 |
| FR-3.5 | 底部安全区 `pb-[env(safe-area-inset-bottom)]` | iPhone 刘海屏适配 |
| FR-3.6 | "更多"抽屉：从底部弹出，包含关于网站、推荐分享、优秀博客 | 点击遮罩关闭 |
| FR-3.7 | 在 `/write*` 路由下不显示 | 写作页无底部导航 |
| FR-3.8 | ScrollTopButton 上移至 `bottom-20` 避免与 MobileNav 重叠 | 两者不重叠 |
| FR-3.9 | Toaster 位置改为 `top-center` | 不被底部导航遮挡 |
| FR-3.10 | 所有链接有 `aria-label` 和 `title` | 无障碍审计通过 |

---

### FR-4: Markmap 思维导图渲染

**优先级**: P1

**描述**: 新增 MarkmapBlock 组件，支持 `markmap` 代码块渲染为交互式思维导图。

| 编号 | 需求 | 验收标准 |
|------|------|---------|
| FR-4.1 | 新建 `MarkmapBlock` 组件，接收 `code: string`（Markdown 层级文本） | 组件可渲染 |
| FR-4.2 | 支持 Markdown 层级语法：`#` 中心主题、`##` 一级分支、`###` 二级分支 | 层级关系正确渲染 |
| FR-4.3 | 节点可折叠/展开 | 点击节点可折叠子树 |
| FR-4.4 | 支持行内 Markdown（链接、粗体、代码） | 渲染正确 |
| FR-4.5 | **必须懒加载** `markmap-lib` 和 `markmap-view`（动态 import） | 首屏 bundle 不包含 markmap |
| FR-4.6 | 渲染失败降级为 `<pre><code>{原始 Markdown}</code></pre>` | 失败时不白屏 |
| FR-4.7 | 懒加载模块缓存：加载成功后缓存引用 | 后续渲染不重复加载 |
| FR-4.8 | 默认适配容器宽度 | 不溢出 |
| FR-4.9 | MarkmapBlock 自行处理预览、全屏和缩放；可复用 DiagramViewer 的视觉样式，但不强依赖 DiagramViewer（交互式 SVG DOM 会丢失折叠展开） | 全屏按钮可用，节点交互保留 |
| FR-4.10 | `markdown-renderer.ts` 增加 `markmap` 语言检测 | `codeToken.lang === 'markmap'` → `<div class="markmap">` |
| FR-4.11 | `use-markdown-render.tsx` 增加 markmap div 检测 | `<MarkmapBlock>` 正确渲染 |
| FR-4.12 | 旧 `mermaid mindmap` 代码块仍由 `MermaidBlock` 渲染 | 向后兼容 |

---

### FR-5: ECharts 数据图表渲染

**优先级**: P1

**描述**: 新增 ChartBlock 组件，支持 `chart` 代码块渲染为 ECharts 图表。

| 编号 | 需求 | 验收标准 |
|------|------|---------|
| FR-5.1 | 新建 `ChartBlock` 组件，接收 JSON 配置字符串 | 组件可渲染 |
| FR-5.2 | 支持 4 种图表类型：`bar`、`line`、`pie`、`radar` | 各类型正确渲染 |
| FR-5.3 | **安全边界**：只允许白名单字段，丢弃未知 key | 不透传任意 JSON 给 ECharts |
| FR-5.4 | `series.data` 限制最大长度（1000 项） | 防止超大数据卡顿 |
| FR-5.5 | 解析失败或校验不通过时降级为代码块 | 不白屏 |
| FR-5.6 | ECharts 按需引入：只注册 4 种图表 + Grid/Tooltip/Legend/Title + CanvasRenderer | 包大小控制在 ~150KB |
| FR-5.7 | 默认高度 400px，自适应容器宽度 | 不溢出 |
| FR-5.8 | 主题适配：使用 `--color-brand` 作为主色调 | 与站点风格一致 |
| FR-5.9 | ChartBlock 自行处理全屏和下载（不扩展 DiagramViewer） | 全屏按钮可用 |
| FR-5.10 | `markdown-renderer.ts` 增加 `chart` 语言检测 | `codeToken.lang === 'chart'` → `<div class="chart">` |
| FR-5.11 | `use-markdown-render.tsx` 增加 chart div 检测 | `<ChartBlock>` 正确渲染 |

---

### FR-6: DiagramViewer 适配优化

**优先级**: P1

**描述**: 优化现有 DiagramViewer 的容器适配和交互，不增加 chart kind。

| 编号 | 需求 | 验收标准 |
|------|------|---------|
| FR-6.1 | preview 区域增加 `max-w-full overflow-hidden` | 自动适配父容器宽度 |
| FR-6.2 | 全屏 modal 增加"适配"按钮（fit to viewport） | 点击后内容适配屏幕 |
| FR-6.3 | SVG → PNG 下载 best-effort；失败时保留 SVG 下载并提示用户 | 下载按钮可用，SVG 保底 |
| FR-6.4 | 移动端全屏 modal 增加 `touch-action: pan-x pan-y` | 触摸滚动正常 |
| FR-6.5 | **不增加 `kind: 'chart'`** | ChartBlock 自行处理图表全屏 |

---

### FR-7: 工具栏可视化插入升级

**优先级**: P2

**描述**: NoteToolbar 插入菜单和颜色工具升级。

| 编号 | 需求 | 验收标准 |
|------|------|---------|
| FR-7.1 | 思维导图插入模板改为 Markmap Markdown | 插入 ` ```markmap\n# 主题\n## 分支\n` ` ` |
| FR-7.2 | 图表插入模板改为 chart JSON | 插入 ` ```chart\n{"type":"bar",...}\n` ` ` |
| FR-7.3 | 对比块模板改为带示例内容的可读版本 | 模板含具体示例而非占位符 |
| FR-7.4 | 增加颜色选择按钮，弹出 8 色色板 | 红/蓝/绿/黄/紫/橙/灰/粉 |
| FR-7.5 | 选中文本后点击色块，自动包裹 `{color\|text}` | 语法正确 |
| FR-7.6 | 未选中时点击，插入 `{red\|示例文本}` 并选中"示例文本" | 光标在可编辑位置 |
| FR-7.7 | 斜杠命令 `mindmap` 改为 Markmap Markdown | `/mindmap` 插入 Markmap 语法 |
| FR-7.8 | 斜杠命令增加 `chart` 命令 | `/chart` 插入 chart JSON 模板 |

---

### FR-8: AI 写作助手输出格式更新

**优先级**: P2

**描述**: 后端 AI polish action 输出格式更新。

| 编号 | 需求 | 验收标准 |
|------|------|---------|
| FR-8.1 | `mindmap` action prompt 改为输出 Markmap Markdown 层级 | AI 返回 `# 主题\n## 分支` 格式 |
| FR-8.2 | 新增 `data_chart` action，输出 ECharts chart JSON | AI 返回 `{"type":"bar",...}` 格式 |
| FR-8.3 | `data_chart` 命名避免与 `/api/ai/analyze` 错题分析接口混淆 | 命名为 `data_chart` 非 `analyze` |
| FR-8.4 | 前端 AI 面板增加"数据分析"按钮 | 按钮在"插入内容"分组中 |
| FR-8.5 | AI 思维导图结果前端自动包裹 ` ```markmap\n...\n` ` ` | 插入后可直接渲染 |
| FR-8.6 | AI 数据分析结果前端自动包裹 ` ```chart\n...\n` ` ` | 插入后可直接渲染 |
| FR-8.7 | `PolishAction` 枚举增加 `data_chart` | 后端 schema + 前端类型同步 |

---

### FR-9: 错题 AI 分析入口增强

**优先级**: P2

**描述**: 增强 `/write-mistake` 页面 AI 分析交互体验。

| 编号 | 需求 | 验收标准 | 优先级 |
|------|------|---------|--------|
| FR-9.1 | 在非流式接口返回前展示轮换式阶段文案（"正在识别题目..."、"正在生成解析..."）；不代表后端真实阶段，仅作为用户等待反馈 | 用户知道系统在处理 | P2 必做 |
| FR-9.2 | 分析失败时显示错误原因 + "重试"按钮 | 用户可重试 | P2 必做 |
| FR-9.3 | 优化图片拖拽上传区域文案与粘贴图片提示（基础入口已有，需完善引导文案） | 上传体验优化 | P2 必做 |
| FR-9.4 | 分析结果预览卡片 + 确认填充 | 结果可见后再填表 | P2 增强（可后续迭代） |
| FR-9.5 | 分析完成后可点击"重新分析" | 不需要刷新页面 | P2 增强 |

---

### FR-10: 统一空状态组件

**优先级**: P3

**描述**: 新建 EmptyState 组件，分 3 批替换核心空状态；完整审计范围约 36+ 处。

| 编号 | 需求 | 验收标准 |
|------|------|---------|
| FR-10.1 | 新建 `EmptyState` 组件，支持 4 种 variant | `no-content`、`no-results`、`not-logged-in`、`load-error` |
| FR-10.2 | 每种 variant 有对应图标、标题、描述、操作按钮 | 见设计文档 §5.1 场景表 |
| FR-10.3 | 样式继承玻璃卡片风格 | `rounded-xl border border-white/40 bg-white/60 backdrop-blur-sm` |
| FR-10.4 | **第一批 (B1)**: `/notes`、`/mistakes`、`/manage` 核心列表页（~5 文件）；完整审计范围约 36+ 处，分批推进 | 核心工作流验证 |
| FR-10.5 | **第二批 (B2)**: `/blog`、`/share`、`/bloggers` 公开页面（~4 文件） | 公开页面验证 |
| FR-10.6 | **第三批 (B3)**: 弹窗、管理子 tab、TOC、卡片等小区域（~15 文件） | 低风险批量替换 |
| FR-10.7 | 每批完成后单独验证（tsc + 视觉检查） | 无回归再进入下一批 |

---

### FR-11: 按钮颜色语义统一

**优先级**: P3

**描述**: 统一全站按钮颜色语义。

| 编号 | 需求 | 验收标准 |
|------|------|---------|
| FR-11.1 | 危险操作：`bg-red-500/10 text-red-500 hover:bg-red-500/20` | 删除、批量删除、移除 |
| FR-11.2 | 主操作：`bg-[var(--color-brand)]/10 text-[var(--color-brand)] hover:bg-[var(--color-brand)]/20` | 保存、发布、新建、确认 |
| FR-11.3 | 次级操作：`bg-white/60 text-gray-600 hover:bg-white/80` | 取消、返回、关闭 |
| FR-11.4 | 所有图标按钮有 `title` 和 `aria-label` | hover 显示功能说明 |
| FR-11.5 | KnowledgeSidebar 移动关闭按钮补齐 `aria-label` | `aria-label='关闭导航'` |

---

## 4. 非功能需求

### NFR-1: 包大小控制

| 包 | 预期大小 | 策略 |
|----|---------|------|
| markmap-lib + markmap-view | ~70KB | 懒加载，不在首屏 bundle |
| echarts (按需) | ~150KB | 只注册 4 种图表类型 + 必要组件 |
| echarts-for-react | ~5KB | 轻量封装 |

### NFR-2: 向后兼容

- 旧笔记中 `mermaid mindmap` 代码块仍正常渲染
- 首页 NavCard 拖拽编辑功能不受影响
- 写作页 mini NavCard 保留
- KnowledgeSidebar 功能不受影响

### NFR-3: 可访问性

- 所有导航链接有 `aria-label` + `title`
- 所有图标按钮有 `title` + `aria-label`
- 使用 `<nav>` 语义标签
- 不禁用用户缩放

### NFR-4: 移动端适配

- 移动端不显示桌面竖向导航
- 移动端底部导航遵循 `safe-area-inset-bottom`
- 移动端不遮挡标题、搜索框、编辑器工具栏
- 图表默认适配容器，不横向溢出

---

## 5. 约束

1. **NavCard 硬约束**: 只允许在 `form === 'icons'` 分支加 `return null`。禁止改动 `full`/`mini` 模式和 `HomeDraggableLayer` 定位逻辑。
2. **不给全局 `<main>` 加 padding**: VerticalNav 以 fixed 悬浮，各页面自行确保左侧 56px 无关键交互。
3. **ECharts 白名单**: 只允许 `bar`/`line`/`pie`/`radar` 类型和白名单字段，防止注入。
4. **ChartBlock 自行处理全屏**: 不扩展 DiagramViewer 的 kind。
5. **空状态分批替换**: 不一次性修改 36+ 文件，分 B1/B2/B3 三批。
6. **`data_chart` 命名**: 避免与 `/api/ai/analyze` 错题分析接口混淆。
7. **依赖选择**: 使用 `npm` 安装（项目已有 `package-lock.json`）。
8. **不引入新状态库**: 使用现有 Zustand。
9. **样式一致性**: 所有新组件遵循半透明卡片、圆角、轻量动效风格。
