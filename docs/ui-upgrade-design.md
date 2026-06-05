# UI 升级设计文档 — 日常使用体验修正

> 版本: 2.0
> 日期: 2026-06-04
> 状态: Draft
> 关联: `AGENTS.md` | `docs/ui-upgrade-requirements.md` | `docs/ui-upgrade-tasks.md`
>
> **v2.0**: 从"功能基本存在"调整为"每天使用不卡住"。覆盖 11 个日常使用阻断问题。

---

## 0. 文档定位

本文档针对 **唯一用户每天使用时遇到的实际阻断问题**，不是功能扩展。与 v1.x 设计文档的区别：

| 维度 | v1.x（功能扩展） | v2.0（体验修正） |
|------|-----------------|-----------------|
| 关注点 | 新增 VerticalNav、Markmap、ECharts | 修复导航溢出、跳转失效、渲染失败 |
| 驱动力 | "功能缺失" | "日常使用卡住" |
| 范围 | 新组件 + 新能力 | 现有组件的 bug fix + 体验补全 |

---

## 1. 问题全景

### 1.1 问题清单与代码定位

| # | 问题 | 严重度 | 代码位置 | 根因 |
|---|------|--------|----------|------|
| 1 | 左侧导航栏溢出 | P0 | `vertical-nav.tsx:48,54` | `fixed left-0` + 无 `overflow-y-auto` + 内容区无左侧 padding 预留 |
| 2 | 导航跳转失效 | P0 | `vertical-nav.tsx:95-130` | `motion layoutId` 胶囊动画与 `Link` 竞争；hover 展开后点击区域偏移 |
| 3 | My Blog 双重跳转语义 | P0 | `vertical-nav.tsx:55-85` | 头像+标题区域是 `<Link href='/'>`，但用户期望点击标题去设置 |
| 4 | 错题页 AI 入口不清晰 | P0 | `write-mistake/page.tsx:268-326` | AI 分析面板已存在，但按钮文案"开始 AI 分析"不够显眼；缺少"AI 生成解析""AI 生成知识点"等明确入口 |
| 5 | 思维导图渲染失败 | P0 | `markmap-block.tsx:45-61` | markmap-lib/view 懒加载可能失败；容器 `minHeight: 200` 但 SVG 可能为 0 宽度；SSR/CSR 边界 |
| 6 | Markdown 标题显示 # | P1 | `article.css:20-23` | `::before { content: '# ' }` 是装饰性前缀，用户误以为是原始 `#` 文本 |
| 7 | 写作入口文案写死 | P1 | `write-buttons.tsx:57` | 固定 `<span>写文章</span>`，不随页面上下文变化 |
| 8 | 左侧标签内容写死 | P1 | `knowledge-sidebar.tsx:52-58` | 标签从 `/api/tags` 动态获取，但 `/mistakes` 页面的 `KnowledgeSidebar` 未传入 `type='mistake'` 过滤 |
| 9 | 设置保存被 GitHub 错误阻断 | P1 | `config-dialog/index.tsx:84-123` + `push-site-content.ts:69-81` | `saveConfigToGithub` 失败时整个 `handleSave` catch，不区分本地保存和 GitHub 同步 |
| 10 | Live2D 页面体验断裂 | P2 | `live2d/page.tsx:1-7` | 仅一行文字"模型已清空"，无状态说明、管理入口、启用指引 |
| 11 | 设置管理未集中化 | P2 | `config-dialog/index.tsx` 隐藏在首页 `Ctrl+L` 快捷键 | 网站标题、头像、favicon、色彩、Live2D、社交按钮等设置分散在首页弹窗中，用户不知道在哪里改 |

### 1.2 关键发现（代码审计）

**导航溢出根因**:
- `vertical-nav.tsx:48`: `fixed left-0 top-1/2 z-40 -translate-y-1/2` — 无 `max-height` 约束
- `vertical-nav.tsx:54`: 内层 `div` 无 `overflow-y-auto`
- `layout/index.tsx:65`: `<main>` 无 `padding-left` 预留，但 VerticalNav 是 `fixed` 定位，实际不遮挡文档流
- 真正的问题：当 7 个导航项 + 头像区域在小屏幕上垂直空间不足时，底部项被裁切

**导航跳转根因**:
- `vertical-nav.tsx:107-112`: `motion.div` 使用 `layoutId='vertical-nav-active'` 覆盖在 `Link` 上层
- `vertical-nav.tsx:114`: 图标容器 `relative z-10`，但 `motion.div` 是 `absolute inset-0`
- `motion.div` 有 `pointer-events: none`（motion 默认行为），但需确认不会拦截点击
- 可能的真正问题：`AnimatePresence` 中 `motion.span` 的 `width: 0` → `width: 'auto'` 动画导致布局抖动，使点击目标偏移

**My Blog 双重语义**:
- `vertical-nav.tsx:55-85`: 整个头像+标题区域是 `<Link href='/'>`
- 用户期望：点击头像/标题 → 首页；点击齿轮/设置图标 → 设置页
- 当前无独立设置入口（设置通过首页 `Ctrl+L` 或 `Ctrl+,` 快捷键打开）

**错题 AI 入口**:
- `write-mistake/page.tsx:268-326`: AI 分析面板已存在，包含：
  - 文本粘贴 + "开始 AI 分析" 按钮（line 297-306）
  - 图片拖拽上传（line 309-324）
  - 阶段文案轮换（line 237-249）
  - 错误重试（line 251-266）
- 问题：按钮文案"开始 AI 分析"不够具体；缺少"AI 生成解析""AI 生成知识点"等分步入口

**思维导图渲染失败**:
- `markmap-block.tsx:7-35`: 懒加载有 `loadFailed` 标志，一旦失败永久不可恢复
- `markmap-block.tsx:51-59`: `Markmap.create()` 需要 SVG 元素有非零尺寸
- `markmap-block.tsx:141`: `style={{ minHeight: 200 }}` 但无 `minWidth`，容器可能为 0 宽度
- SSR 问题：`markmap-lib` 和 `markmap-view` 使用浏览器 API（SVG、DOM），必须在客户端加载

**Markdown 标题 # 问题**:
- `article.css:20-23`: `h1::before { content: '# ' }` — 这是 CSS 装饰，不是原始文本
- `markdown-renderer.ts:166-169`: heading 渲染正确输出 `<h1>text</h1>`
- 用户看到的 `#` 是 CSS `::before` 伪元素，设计意图是视觉装饰
- 问题：用户可能认为这是 bug，需要明确这是设计选择或移除装饰

**写作入口文案**:
- `write-buttons.tsx:57`: `<span>写文章</span>` — 硬编码
- 首页只显示"写文章"，跳转 `/write`
- `/notes` 页面有独立的"写笔记"按钮（`notes/page.tsx:116`）
- `/mistakes` 页面有独立的"添加错题"按钮（`mistakes/page.tsx:176`）

**左侧标签**:
- `knowledge-sidebar.tsx:56-58`: `listTags().then(setTags)` — 从 `/api/tags` 获取所有标签
- 标签是动态的，不是硬编码
- 但 `/mistakes` 页面使用同一个 `KnowledgeSidebar`，标签未按内容类型过滤
- `/api/tags` 返回所有标签（不分类型），这是后端行为

**设置保存**:
- `config-dialog/index.tsx:97-107`: 调用 `pushSiteContent()`，失败时 catch 显示 toast
- `push-site-content.ts:69-81`: 调用 `saveConfigToGithub()`，成功显示 commit SHA
- `saveConfigToGithub` → `POST /api/sync/save-config` → 后端 `github_sync.py`
- 问题：本地配置更新（Zustand store）和 GitHub 同步耦合在同一个 try-catch 中

---

## 2. 设计方案

### 2.1 左侧导航栏溢出修复

**问题**: 左侧竖栏在浏览器左边缘被裁切，展开态可能覆盖知识库侧栏主要操作。

**方案**: 给导航容器添加 `max-height` + `overflow-y-auto` + 左侧间距。

```
┌─────────────────┐
│ [头像] 站点标题  │ ← 固定区域
│─────────────────│
│ 🏠 首页         │
│ 📜 近期文章      │
│ 📝 笔记         │ ← 可滚动区域
│ ❌ 错题集        │
│ ℹ️ 关于网站      │
│ 🔗 推荐分享      │
│ 🌐 优秀博客      │
└─────────────────┘
```

**修改**:
- `vertical-nav.tsx:54`: 内层 `div` 添加 `max-h-[calc(100vh-32px)] overflow-y-auto`
- `vertical-nav.tsx:48`: `left-0` 改为 `left-2`，给左侧 8px 间距防止被浏览器边缘裁切
- 头像区域保持固定（不随滚动），导航列表区域可滚动
- 结构调整：头像区域和导航列表分为两个独立区域

**验收补充**:
- 在截图宽高下，左侧竖栏不能被浏览器左边缘裁切
- 展开态（180px）不能覆盖知识库侧栏（`KnowledgeSidebar`）的主要操作区域

**代码变更**:
```tsx
// vertical-nav.tsx — 修改内层结构
<motion.nav className='vertical-nav fixed left-0 top-1/2 z-40 -translate-y-1/2' ...>
  <div className='flex max-h-[calc(100vh-32px)] flex-col rounded-r-2xl border border-l-0 border-white/40 bg-white/70 shadow-lg backdrop-blur-xl'>
    {/* 头像区域 — 固定 */}
    <Link href='/' className='px-2 pt-3 pb-2 ...'>
      ...
    </Link>
    <div className='mx-2 border-t border-white/30' />
    {/* 导航列表 — 可滚动 */}
    <nav className='flex-1 overflow-y-auto px-2 py-1'>
      {navItems.slice(1).map(...)}
    </nav>
  </div>
</motion.nav>
```

### 2.2 导航跳转失效修复

**问题**: 点击导航项后不跳转或跳转异常。

**根因分析**:
1. `motion.div` with `layoutId` 作为 `absolute inset-0` 覆盖层，理论上 `pointer-events: none`
2. `AnimatePresence` 中 `motion.span` 的 `width: 0` → `width: 'auto'` 可能导致布局抖动
3. `Link` 组件的点击区域可能被动画元素遮挡

**方案**:

A. 确保 `motion.div`（active 胶囊）不拦截点击:
```tsx
// vertical-nav.tsx:108-112
{isActive && (
  <motion.div
    layoutId='vertical-nav-active'
    className='pointer-events-none absolute inset-0 rounded-xl bg-[var(--color-brand)]/15'
    // ↑ 添加 pointer-events-none
    transition={{ type: 'spring', stiffness: 400, damping: 30 }}
  />
)}
```

B. 简化标签展开动画，避免 `width: 0` → `width: 'auto'` 的布局抖动:
```tsx
// 改为 opacity + x 位移动画，不改变 width
<motion.span
  className='relative z-10 truncate text-[13px]'
  initial={{ opacity: 0, x: -8 }}
  animate={{ opacity: 1, x: 0 }}
  exit={{ opacity: 0, x: -8 }}
  transition={{ duration: 0.15 }}
>
  {item.label}
</motion.span>
```

C. 确保 `Link` 的 `z-index` 高于装饰元素:
```tsx
<Link className='relative z-10 flex w-full items-center ...'>
```

### 2.3 My Blog 跳转语义统一

**问题**: 代码中当前只有首页跳转，但产品语义缺少独立设置入口，导致用户预期冲突。用户期望"点击站点名去首页，点击设置去设置页"，但当前设置入口隐藏在首页快捷键中。

**方案**:
- 头像 + 站点名 → 始终跳转首页 `/`（保持不变）
- 新增独立设置入口：齿轮图标按钮

**设计**:
```
┌──────────────────┐
│ [头像] 站点标题   │ ← 点击跳转首页
│─────────────────│
│ ⚙️ 网站设置      │ ← 新增：点击打开设置
│─────────────────│
│ 🏠 首页          │
│ ...              │
└──────────────────┘
```

**修改**:
- `vertical-nav.tsx`: 在头像区域下方、导航列表上方添加"网站设置"入口
- 点击调用 `setConfigDialogOpen(true)`（已有 Zustand store 方法）
- 图标使用 `lucide-react` 的 `Settings`
- 样式与其他导航项一致

**代码变更**:
```tsx
// vertical-nav.tsx — 在分割线下方添加设置入口
<button
  onClick={() => setConfigDialogOpen(true)}
  aria-label='网站设置'
  title='网站设置'
  className='flex w-full items-center gap-2.5 rounded-xl px-2 py-2 text-gray-500 transition-colors hover:bg-white/60 hover:text-gray-700'
>
  <div className='flex h-7 w-7 shrink-0 items-center justify-center'>
    <Settings className='h-[18px] w-[18px]' />
  </div>
  <AnimatePresence>
    {expanded && (
      <motion.span
        className='relative z-10 truncate text-[13px]'
        initial={{ opacity: 0, x: -8 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -8 }}
      >
        网站设置
      </motion.span>
    )}
  </AnimatePresence>
</button>
```

### 2.4 错题页 AI 入口增强

**问题**: 用户粘贴题目后不知道 AI 分析入口在哪里。

**当前状态**: AI 分析面板已存在（`write-mistake/page.tsx:268-326`），包含文本粘贴和图片上传。

**方案**: 不新增功能，只优化可见性和文案。

**修改**:

A. 按钮文案更具体:
```
当前: "开始 AI 分析"
目标: "AI 智能解析题目"
```

B. 在表单区域增加 AI 辅助提示:
```
当前: 表单字段只有 placeholder
目标: 每个字段右侧增加"AI 填充"小图标提示
```

C. AI 面板标题更醒目:
```
当前: "AI 分析错题" + "错题助手" 标签
目标: 保持，但在面板下方增加操作说明文字
```

D. 增加分步 AI 入口按钮:
```
[AI 智能解析题目] ← 主按钮，一键填充所有字段
[AI 生成解析]     ← 次按钮，只填充 analysis 字段
[AI 生成知识点]   ← 次按钮，只填充 knowledge_points 字段
```

**代码变更**:
- `write-mistake/page.tsx:297-306`: 按钮文案改为"AI 智能解析题目"
- `write-mistake/page.tsx:276-280`: 面板描述文案增加"粘贴题目或上传图片，点击按钮自动填充"
- 在主按钮下方增加两个次级按钮（复用 `analyzeText` API，但只更新部分字段）

### 2.5 思维导图渲染修复

**问题**: Markmap 思维导图渲染失败。

**根因**:
1. `loadFailed` 标志一旦设为 `true` 就永久不可恢复
2. SVG 容器可能为 0 宽度
3. SSR/CSR 边界：组件在服务端渲染时 markmap 库不可用

**方案**:

A. 移除永久失败标志，允许重试:
```typescript
// 当前: loadFailed = true → 永久失败
// 改为: 每次渲染时重试加载
async function loadMarkmapLib() {
  if (!libPromise) {
    libPromise = import('markmap-lib').catch(err => {
      libPromise = null // 允许重试
      throw err
    })
  }
  return libPromise
}
```

B. 确保容器有最小宽度:
```tsx
// 当前: style={{ minHeight: 200 }}
// 改为: style={{ minHeight: 200, minWidth: 300 }}
<svg ref={previewSvgRef} className='h-auto w-full' style={{ minHeight: 200, minWidth: 300 }} />
```

C. 添加错误重试按钮:
```tsx
if (error) {
  return (
    <div className='my-6 rounded-lg border border-zinc-200/70 bg-zinc-50/70 p-4'>
      <p className='mb-2 text-sm text-zinc-500'>思维导图渲染失败</p>
      <button onClick={() => { setError(false); /* 重新渲染 */ }} className='...'>
        重试
      </button>
      <pre className='mt-2'><code>{code}</code></pre>
    </div>
  )
}
```

D. 添加 SSR 保护:
```tsx
const [mounted, setMounted] = useState(false)
useEffect(() => { setMounted(true) }, [])
if (!mounted) return <div className='min-h-[200px] animate-pulse bg-zinc-100 rounded-lg' />
```

### 2.6 Markdown 标题 # 装饰移除

**问题**: 用户看到标题前有 `# ` 前缀，认为是渲染 bug。用户明确要求去掉。

**当前行为**: `article.css:20-23` 使用 `::before { content: '# ' }` 作为装饰性前缀。

**方案**: 默认移除所有标题的 `::before` 伪元素装饰。

```css
/* 删除以下规则 */
.prose h1::before, .prose h2::before { content: '# '; ... }
.prose h3::before { content: '## '; ... }
.prose h4::before { content: '### '; ... }
.prose h5::before { content: '#### '; ... }
```

**保留 `scroll-margin-top`**: `article.css:250-252` 的 `.prose [id] { scroll-margin-top: 100px }` 保留，用于 TOC 锚点定位。

**未来可选**: 如需保留 # 装饰，可作为 `/manage` 设置页的可选配置项，不在本轮实现。

### 2.7 写作入口动态文案

**问题**: 首页"写文章"按钮文案固定。

**方案**: 首页按钮保持"写文章"（因为首页是全局入口），但在按钮下方增加快捷入口。

**实际修改**:
- `write-buttons.tsx:57`: 保持 `<span>写文章</span>`
- 但在首页 `NavCard` 或 `WriteButton` 附近增加"写笔记""写错题"快捷入口
- 或者：将单个按钮改为下拉菜单，包含"写文章""写笔记""写错题"

**推荐方案**: 保持单按钮"写文章"不变，因为：
1. `/notes` 页面已有独立"写笔记"按钮
2. `/mistakes` 页面已有独立"添加错题"按钮
3. 首页是全局入口，"写文章"是最通用的文案

**如果用户坚持需要动态文案**:
```tsx
// write-buttons.tsx — 根据最近访问的页面动态显示文案
const lastVisited = localStorage.getItem('last-visited-section')
const label = lastVisited === 'notes' ? '写笔记' : lastVisited === 'mistakes' ? '写错题' : '写文章'
```

### 2.8 左侧标签按页面动态聚合

**问题**: 用户要求左侧标签应为动态变化内容，按当前页面类型过滤。

**当前状态**: `knowledge-sidebar.tsx:56-58` 从 `/api/tags` 获取所有标签（不分类型）。

**方案**:

当前 `/api/tags` 只返回全量标签且无类型统计，不能直接前端按类型过滤。实现需二选一：方案 A 后端按 `contentTypes` 聚合；方案 B 前端从当前页面 items 聚合。
- `/notes` 页面：只显示与 note/blog 类型内容关联的标签
- `/mistakes` 页面：只显示与 mistake 类型内容关联的标签（或知识点）
- `/manage` 页面：显示全站所有标签

B. 实现方式——二选一：

**方案 A（推荐）：后端 `/api/tags` 增加 `contentTypes` 查询参数**
```python
# backend/app/routers/tags.py
@router.get("/api/tags")
async def list_tags(contentTypes: str | None = None, db: ...):
    # contentTypes 为逗号分隔的 note type，如 "note,blog" 或 "mistake"
    # 按 Note.type 聚合返回关联标签
```
```ts
// src/lib/api/meta.ts
export function listTags(contentTypes?: string[]): Promise<Tag[]> {
  const qs = contentTypes ? `?contentTypes=${contentTypes.join(',')}` : ''
  return apiFetch<Tag[]>(`/api/tags${qs}`)
}
```

**方案 B（临时）：前端从当前列表数据中聚合标签**
- `KnowledgeSidebar` 接收当前页面已加载的 items 列表
- 从 items 中提取 `item.tags` 聚合去重
- 不依赖 `/api/tags` 做类型过滤

当前 `Tag` 类型只有 `id` 和 `name`（`src/lib/api/meta.ts`），无 `content_type` 或关联统计，因此方案 A 需要后端配合。

C. 点击标签必须筛选当前页面内容（已有实现：`mistakes/page.tsx:30` `tag: activeTag`）。

D. 无标签时显示"暂无标签"。

**代码变更**:
```tsx
// knowledge-sidebar.tsx:197-218
{tags.length > 0 ? (
  // 现有标签渲染
) : (
  <div className='p-3'>
    <div className='mb-2 px-3 text-xs font-medium text-gray-400'>标签</div>
    <p className='px-3 text-xs text-gray-400'>暂无标签</p>
  </div>
)}
```

### 2.9 设置保存 GitHub 错误拆分

**问题**: 设置保存时 GitHub 同步失败会阻断整个保存流程。

**当前流程**:
```
handleSave() → pushSiteContent() → saveConfigToGithub() → POST /api/sync/save-config
                                    ↓ 失败
                              catch → toast.error('保存失败')
                              整个流程中断，Zustand store 不更新
```

**目标流程**:
```
handleSave() → 1. 更新 Zustand store（本地保存）
             → 2. pushSiteContent()（GitHub 同步）
                  ↓ 失败
                  toast.warning('本地设置已保存，GitHub 同步失败: ...')
                  不阻断本地保存
```

**方案**: 拆分 `handleSave` 为两步：

```typescript
const handleSave = async () => {
  setIsSaving(true)
  let localSaved = false
  let githubSynced = false
  let githubError = ''

  try {
    // Step 1: 本地保存（Zustand store + CSS 变量）
    setSiteContent(formData)
    setCardStyles(cardStylesData)
    updateThemeVariables(formData.theme)
    localSaved = true

    // Step 2: GitHub 同步（可选）
    try {
      await pushSiteContent(formData, cardStylesData, ...)
      githubSynced = true
    } catch (syncError: any) {
      githubError = syncError?.message || '未知错误'
    }

    // Step 3: 反馈
    if (localSaved && githubSynced) {
      toast.success('设置已保存并同步到 GitHub')
      onClose()
    } else if (localSaved && !githubSynced) {
      toast.warning(`本地设置已保存，GitHub 同步失败: ${githubError}`)
      onClose() // 仍然关闭，因为本地已保存
    }
  } catch (error: any) {
    toast.error(`保存失败: ${error?.message || '未知错误'}`)
  } finally {
    setIsSaving(false)
  }
}
```

### 2.10 Live2D 状态页

**问题**: `/live2d` 页面只有一行文字，体验断裂。

**方案**: 改为清晰的状态说明页。

**设计**:
```
┌─────────────────────────────────────────┐
│                                         │
│         🎭 Live2D 模型管理              │
│                                         │
│  ┌─ 当前状态 ──────────────────────┐   │
│  │ 状态: 未启用                     │   │
│  │ 模型: 未上传                     │   │
│  └──────────────────────────────────┘   │
│                                         │
│  ┌─ 如何使用 ──────────────────────┐   │
│  │ 1. 在网站设置中上传 Live2D 模型  │   │
│  │ 2. 启用 Live2D 显示             │   │
│  │ 3. 返回此页面查看模型            │   │
│  └──────────────────────────────────┘   │
│                                         │
│  [前往网站设置]                          │
│                                         │
└─────────────────────────────────────────┘
```

**代码变更**:
- `live2d/page.tsx`: 重写为状态说明页
- 添加"前往网站设置"按钮，调用 `setConfigDialogOpen(true)`
- 添加模型状态检查（从 `siteContent` 读取）

### 2.11 设置管理页集中化

**问题**: 网站相关设置（标题、头像、favicon、色彩、Live2D、社交按钮、备案信息）分散在首页 `Ctrl+L` 快捷键打开的弹窗中，用户不知道在哪里改。`/manage` 页面当前只有内容管理、音乐管理、推荐管理三个 tab，缺少网站设置入口。

**方案**: 在 `/manage` 页面新增"网站设置" tab，复用现有 `ConfigDialog` 中的 `SiteSettings`、`ColorConfig`、`HomeLayout` 组件。

**设计**:
```
/manage 页面 tab 栏:
┌──────────┬──────────┬──────────┬──────────┐
│ 内容管理  │ 音乐管理  │ 推荐管理  │ 网站设置  │ ← 新增
└──────────┴──────────┴──────────┴──────────┘
```

**"网站设置" tab 内容**:
- 复用 `SiteSettings` 组件（favicon/头像/站点信息/社交按钮/艺术图/背景图/备案/功能开关）
- 复用 `ColorConfig` 组件（色彩配置）
- 复用 `HomeLayout` 组件（首页布局）

**代码变更**:
- `src/app/manage/page.tsx`: 新增第四个 tab "网站设置"
- 复用已导出的 `SiteSettings`、`ColorConfig`、`HomeLayout`，必要时抽取共享保存 hook。
- `/manage` 页面的"网站设置" tab 与首页 `Ctrl+L` 弹窗共享同一套组件和保存逻辑

**保存逻辑**: 复用 `config-dialog/index.tsx` 的 `handleSave`（含 §2.9 的错误拆分改造）。

---

## 3. 修改文件总览

| 文件 | 变更类型 | 关联问题 |
|------|----------|----------|
| `src/components/vertical-nav.tsx` | 修改 | #1 溢出, #2 跳转, #3 My Blog |
| `src/app/write-mistake/page.tsx` | 修改 | #4 AI 入口 |
| `src/components/markmap-block.tsx` | 修改 | #5 思维导图 |
| `src/styles/article.css` | 修改 | #6 标题 # |
| `src/app/(home)/write-buttons.tsx` | 可选修改 | #7 写作入口 |
| `src/app/notes/components/knowledge-sidebar.tsx` | 修改 | #8 标签 |
| `src/app/(home)/config-dialog/index.tsx` | 修改 | #9 设置保存 |
| `src/app/(home)/services/push-site-content.ts` | 修改 | #9 设置保存 |
| `src/app/live2d/page.tsx` | 修改 | #10 Live2D |
| `src/app/manage/page.tsx` | 修改 | #11 设置集中化 |

---

## 4. 优先级与执行顺序

```text
P0（必须先修，阻断日常使用）
  ① 左侧导航栏溢出     → vertical-nav.tsx
  ② 导航跳转失效       → vertical-nav.tsx
  ③ My Blog 双重跳转    → vertical-nav.tsx
  ④ 错题 AI 入口不清晰   → write-mistake/page.tsx
  ⑤ 思维导图渲染失败     → markmap-block.tsx

P1（核心体验修正）
  ⑥ Markdown # 默认移除  → article.css
  ⑦ 写作入口动态文案     → write-buttons.tsx（可选）
  ⑧ 左侧标签按页面过滤   → knowledge-sidebar.tsx
  ⑨ 设置保存错误拆分     → config-dialog/index.tsx + push-site-content.ts

P2（结构整理）
  ⑩ Live2D 状态页       → live2d/page.tsx
  ⑪ 设置管理页集中化    → manage/page.tsx
```

---

## 5. 验收标准

| # | 验收项 | 验证方式 |
|---|--------|----------|
| 1 | 左侧导航在截图宽高下不被浏览器左边缘裁切，展开态不覆盖知识库侧栏主要操作 | 桌面端逐页检查 |
| 2 | 点击任意导航项都能稳定跳转 | 逐个点击测试 |
| 3 | My Blog 点击行为唯一（跳转首页），设置入口独立且可用 | 点击测试 |
| 4 | 错题页能明显看到"AI 智能解析题目"入口 | 视觉检查 |
| 5 | 思维导图能正常渲染，失败时有重试按钮 | 新建 markmap 代码块测试 |
| 6 | Markdown 标题不显示 # 装饰 | 详情页视觉检查 |
| 7 | 左侧标签按页面类型过滤，无标签时显示"暂无标签" | 各页面检查 |
| 8 | 设置保存时 GitHub 同步失败不阻断本地保存 | 模拟 GitHub API 失败 |
| 9 | Live2D 页面有清晰状态说明和管理入口 | 访问 /live2d |
| 10 | /manage 页面有"网站设置" tab，可修改站点配置 | 访问 /manage |

---

## 6. 风险与回滚

| 方案 | 风险 | 回滚 |
|------|------|------|
| 导航溢出修复 | 可能影响展开动画 | 恢复原 CSS |
| 导航跳转修复 | pointer-events 可能影响动画 | 恢复原 motion.div |
| 设置保存拆分 | 本地保存成功但 GitHub 不同步时数据不一致 | 下次保存时重新同步 |
| 思维导图重试 | 无限重试可能消耗资源 | 限制重试次数（3 次） |
