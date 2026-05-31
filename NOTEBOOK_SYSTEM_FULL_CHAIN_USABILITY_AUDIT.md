# 个人笔记本系统全链路可用性审查报告

## 1. 结论摘要

### 1.1 总体结论

- **博客发布闭环**：部分闭环
- **错题整理闭环**：基本完整
- **笔记撰写整理闭环**：基本完整
- **当前是否适合继续扩展 Mermaid**：暂不适合
- **当前是否适合继续扩展 AI 图片生成**：暂不适合
- **当前最优先修复方向**：统一博客与笔记的数据持久化层，补齐笔记编辑器的预览和图片能力

### 1.2 阻断级问题总览

| 优先级 | 模块 | 问题 | 是否阻断闭环 | 证据 |
|---|---|---|---|---|
| P0 | 博客 | 博客与笔记使用完全不同的持久化层（GitHub 静态文件 vs PostgreSQL），导致搜索、标签、分类互不可见 | 是 | `src/app/write/services/push-blog.ts` vs `src/lib/api/notes.ts` |
| P0 | 博客 | 博客列表/详情从静态文件 `/blogs/index.json` 加载，后端 `type=blog` 的笔记永远不会出现在博客列表 | 是 | `src/hooks/use-blog-index.ts:21`, `src/app/blog/[id]/page.tsx:28` |
| P0 | 笔记 | 笔记编辑器无 Markdown 预览功能，博客编辑器有完整预览 | 否（体验） | `src/app/write-note/page.tsx` vs `src/app/write/components/preview.tsx` |
| P0 | 笔记 | 笔记创建/编辑表单缺少 `cover` 和 `category` 字段入口，虽然后端模型支持 | 否（字段缺失） | `src/app/write-note/page.tsx`, `src/app/write-note/[slug]/page.tsx` |
| P0 | 笔记 | 笔记编辑器无图片上传能力，博客编辑器支持粘贴图片上传到 GitHub | 否（功能缺失） | `src/app/write/components/editor.tsx:130-156` vs `src/app/write-note/page.tsx` |
| P1 | 错题 | AI 分析的图片仅以 base64 临时发送，不持久化到数据库或存储 | 否（数据丢失风险） | `src/app/write-mistake/page.tsx:53-79`, `backend/app/routers/ai.py:236-263` |
| P1 | 错题 | `/mistakes/[id]` 路由目录为空，错题详情实际使用 `/notes/[slug]` | 否（路由冗余） | `src/app/mistakes/[id]/` (空目录) |
| P1 | 错题 | `/write-mistake/[slug]` 路由目录为空，错题编辑使用 `/write-note/[slug]` | 否（路由冗余） | `src/app/write-mistake/[slug]/` (空目录) |
| P1 | 跨模块 | 博客分类存储在 GitHub JSON，后端有 Category 表但笔记编辑器无分类选择入口 | 是（数据不一致） | `backend/app/models/note.py:86-91` vs `src/app/write/components/sections/meta-section.tsx` |
| P1 | 跨模块 | Subject 表存在但笔记创建/编辑中 subject 字段为自由文本输入，无下拉选择 | 否（体验） | `backend/app/models/note.py:79-83`, `src/app/write-note/page.tsx:145-149` |

## 2. 项目结构识别

```
前端目录：src/app/ (Next.js App Router)
后端目录：backend/app/ (FastAPI + SQLAlchemy)
主要路由：
  - / (首页)
  - /blog (博客列表，数据来自 GitHub 静态文件)
  - /blog/[id] (博客详情，数据来自 GitHub 静态文件)
  - /write (博客编辑器，发布到 GitHub)
  - /write/[slug] (博客再编辑)
  - /notes (笔记列表，数据来自后端 API)
  - /notes/[id] (笔记详情，数据来自后端 API)
  - /write-note (创建笔记/博客/错题，保存到后端)
  - /write-note/[slug] (编辑笔记)
  - /mistakes (错题列表，数据来自后端 API)
  - /mistakes/review (错题复习)
  - /write-mistake (创建错题，含 AI 分析)
  - /manage (管理面板)

主要 API：
  - GET/POST/PUT/DELETE /api/notes (笔记 CRUD)
  - GET/POST /api/review/queue, /api/review/{slug}, /api/review/stats (复习)
  - POST /api/ai/analyze, /api/ai/analyze-text (AI 分析)
  - GET/POST/DELETE /api/tags (标签)
  - GET/POST/PUT/DELETE /api/categories (分类)
  - GET/POST/DELETE /api/subjects (科目)
  - GET /api/search (搜索)
  - POST /api/auth/login, /api/auth/register (认证)
  - POST /api/sync/push (GitHub 同步)

主要数据模型：
  - Note (统一模型: type=note|blog|mistake)
  - Tag (标签，多对多关联 Note)
  - Category (分类，独立表)
  - Subject (科目，独立表)
  - User (用户)

是否确认为个人笔记本系统：是
```

## 3. 三大模块入口与调用链

### 3.1 博客发布调用链

```
入口页面：
  - 首页 "写文章" 按钮 → /write
    路径: src/app/(home)/write-buttons.tsx:38

编辑页面：
  - /write (新建) → src/app/write/page.tsx
  - /write/[slug] (编辑) → src/app/write/[slug]/page.tsx

列表页面：
  - /blog → src/app/blog/page.tsx
  - 数据来源: /blogs/index.json (GitHub 静态文件)

详情页面：
  - /blog/[id] → src/app/blog/[id]/page.tsx
  - 数据来源: /blogs/{slug}/config.json + /blogs/{slug}/index.md

相关组件：
  - WriteEditor: src/app/write/components/editor.tsx
  - WriteSidebar: src/app/write/components/sidebar.tsx
  - WriteActions: src/app/write/components/actions.tsx
  - WritePreview: src/app/write/components/preview.tsx
  - MetaSection: src/app/write/components/sections/meta-section.tsx
  - CoverSection: src/app/write/components/sections/cover-section.tsx
  - BlogPreview: src/components/blog-preview.tsx

前端 API：
  - pushBlog: src/app/write/services/push-blog.ts (GitHub API)
  - deleteBlog: src/app/write/services/delete-blog.ts (GitHub API)
  - loadBlog: src/lib/load-blog.ts (fetch 静态文件)
  - saveBlogEdits: src/app/blog/services/save-blog-edits.ts (GitHub API)

后端 API：
  - 无专用博客 API。博客通过 GitHub App API 直接操作仓库文件。

后端模型：
  - 后端 Note 模型支持 type='blog'，但博客发布流程不使用后端。
```

### 3.2 错题整理调用链

```
入口页面：
  - 导航栏 "错题集" → /mistakes
    路径: src/components/nav-card.tsx:42-46
  - /mistakes 页面 "添加错题" 按钮 → /write-mistake
    路径: src/app/mistakes/page.tsx:78-83

录入页面：
  - /write-mistake → src/app/write-mistake/page.tsx

AI 分析页面或组件：
  - 图片识别: src/app/write-mistake/page.tsx:53-79
  - 文本分析: src/app/write-mistake/page.tsx:82-96
  - 后端 AI 路由: backend/app/routers/ai.py
  - AI 服务: backend/app/services/ai_service.py

列表页面：
  - /mistakes → src/app/mistakes/page.tsx
  - 数据来源: GET /api/notes?type=mistake (后端 API)

详情页面：
  - /mistakes/[id] 目录为空！
  - 错题详情实际使用 /notes/[slug] → src/app/notes/[id]/page.tsx

复习页面：
  - /mistakes/review → src/app/mistakes/review/page.tsx

相关组件：
  - useNoteIndex hook: src/hooks/use-note-index.ts
  - useReviewStats hook: src/hooks/use-note-index.ts:17-21
  - EditableStarRating: src/components/editable-star-rating.tsx

前端 API：
  - analyzeMistake: src/lib/api/ai.ts:14
  - analyzeText: src/lib/api/ai.ts:21
  - createNote: src/lib/api/notes.ts:106
  - getReviewQueue: src/lib/api/review.ts:11
  - submitReview: src/lib/api/review.ts:15
  - getReviewStats: src/lib/api/review.ts:22

后端 API：
  - POST /api/ai/analyze (图片 OCR)
  - POST /api/ai/analyze-text (文本分析)
  - POST /api/notes (创建错题)
  - GET /api/review/queue (复习队列)
  - POST /api/review/{slug} (提交评分)
  - GET /api/review/stats (复习统计)

后端模型：
  - Note (type='mistake'), 含 SM-2 字段: ef, interval, repetitions, next_review, last_reviewed
  - 错题特有字段: subject, difficulty, question, my_answer, correct_answer, analysis, knowledge_points
```

### 3.3 笔记撰写整理调用链

```
入口页面：
  - 导航栏 "笔记" → /notes
    路径: src/components/nav-card.tsx:37-40
  - /notes 页面 "写笔记" 按钮 → /write-note
    路径: src/app/notes/page.tsx:57-62

编辑页面：
  - /write-note (新建) → src/app/write-note/page.tsx
  - /write-note/[slug] (编辑) → src/app/write-note/[slug]/page.tsx

列表页面：
  - /notes → src/app/notes/page.tsx
  - 数据来源: GET /api/notes (后端 API)

详情页面：
  - /notes/[id] → src/app/notes/[id]/page.tsx

管理页面：
  - /manage → src/app/manage/page.tsx (表格视图，支持批量删除、同步)

相关组件：
  - useNoteIndex hook: src/hooks/use-note-index.ts
  - useMarkdownRender hook: src/hooks/use-markdown-render.tsx
  - CodeBlock: src/components/code-block.tsx
  - MarkdownImage: src/components/markdown-image.tsx

前端 API：
  - listNotes: src/lib/api/notes.ts:88
  - getNote: src/lib/api/notes.ts:102
  - createNote: src/lib/api/notes.ts:106
  - updateNote: src/lib/api/notes.ts:113
  - deleteNote: src/lib/api/notes.ts:120

后端 API：
  - GET /api/notes (列表，支持 type/tag/subject/category/q/hidden 筛选)
  - GET /api/notes/{slug} (详情)
  - POST /api/notes (创建)
  - PUT /api/notes/{slug} (更新)
  - DELETE /api/notes/{slug} (删除)
  - POST /api/notes/batch-delete (批量删除)
  - GET /api/search (搜索)

后端模型：
  - Note (type='note'), 含: slug, title, content, summary, cover, category, hidden, tags
```

## 4. 博客发布闭环审查

### 4.1 能力矩阵

| 能力项 | 状态 | 证据路径 | 是否阻断闭环 | 说明 |
|---|---|---|---|---|
| 进入发布页 | 已支持 | `src/app/(home)/write-buttons.tsx:38` → `/write` | 否 | 首页有明确入口 |
| 编辑正文 | 已支持 | `src/app/write/components/editor.tsx` | 否 | 支持 Markdown、快捷键、粘贴图片 |
| Markdown 预览 | 已支持 | `src/app/write/components/preview.tsx` | 否 | 使用 BlogPreview 组件渲染 |
| 保存草稿 | 未支持 | - | 是 | 发布直接 commit 到 GitHub，无草稿状态 |
| 发布 | 已支持 | `src/app/write/services/push-blog.ts` | 否 | 通过 GitHub App API 创建 commit |
| 列表展示 | 已支持 | `src/app/blog/page.tsx`, `src/hooks/use-blog-index.ts` | 否 | 从 `/blogs/index.json` 加载 |
| 详情展示 | 已支持 | `src/app/blog/[id]/page.tsx` | 否 | 从 `/blogs/{slug}/` 加载 |
| 再编辑 | 已支持 | `src/app/write/[slug]/page.tsx` | 否 | 详情页有编辑按钮 |
| 删除/隐藏 | 已支持 | `src/app/write/services/delete-blog.ts`, `src/app/blog/page.tsx:204-211` | 否 | 支持删除（GitHub commit）和 hidden 字段 |
| 错误提示 | 部分支持 | `src/app/write/hooks/use-publish.ts:34-36` | 否 | 使用 toast 提示，但错误信息不够结构化 |
| 刷新后数据仍在 | 已支持 | 博客存储在 GitHub 仓库文件中 | 否 | 部署后通过静态文件访问 |

### 4.2 数据流审查

```
用户进入 /write 页面
  → src/app/write/page.tsx (WritePage)
  → 使用 useWriteStore (Zustand) 管理表单状态

用户输入标题/正文/标签/摘要/日期/分类
  → src/app/write/components/editor.tsx (标题、slug、Markdown 正文)
  → src/app/write/components/sections/meta-section.tsx (摘要、标签、分类、日期、hidden)
  → src/app/write/components/sections/cover-section.tsx (封面图)

用户点击预览
  → src/app/write/components/preview.tsx
  → 调用 useMarkdownRender (src/hooks/use-markdown-render.tsx)
  → 调用 renderMarkdown (src/lib/markdown-renderer.ts)
  → 支持 Shiki 代码高亮、KaTeX 数学公式

用户点击发布
  → src/app/write/components/actions.tsx:18-24 (handleImportOrPublish)
  → src/app/write/hooks/use-publish.ts:21-39 (onPublish)
  → src/app/write/services/push-blog.ts:28-179 (pushBlog)
    1. 获取 GitHub 分支 ref → getRef()
    2. 上传图片 → createBlob() × N
    3. 创建 index.md blob → createBlob()
    4. 创建 config.json blob → createBlob()
    5. 更新 blogs/index.json → prepareBlogsIndex() + createBlob()
    6. 创建 tree → createTree()
    7. 创建 commit → createCommit()
    8. 更新分支引用 → updateRef()
  → GitHub 仓库文件更新
  → Cloudflare Workers 部署触发
  → 静态页面更新

用户查看博客列表
  → src/app/blog/page.tsx
  → useBlogIndex() → fetch('/blogs/index.json')
  → 从静态文件加载，非后端 API

用户查看博客详情
  → src/app/blog/[id]/page.tsx
  → loadBlog(slug) → fetch('/blogs/{slug}/config.json') + fetch('/blogs/{slug}/index.md')
  → BlogPreview 组件渲染
```

**关键问题**：博客发布数据流完全不经过后端 API，直接操作 GitHub 仓库。后端 Note 模型虽支持 `type='blog'`，但博客发布流程与后端完全脱节。

### 4.3 主要问题

**P0-1：博客与笔记持久化层完全分裂**
- 博客通过 GitHub App API 直接写入仓库文件 (`src/app/write/services/push-blog.ts`)
- 笔记/错题通过后端 API 写入 PostgreSQL (`src/lib/api/notes.ts`)
- 后端 Note 模型支持 `type='blog'`，但博客发布流程从不调用后端 API
- 结果：`/notes?type=blog` 查询后端数据库，永远查不到通过 `/write` 发布的博客
- 博客列表 (`/blog`) 从 `/blogs/index.json` 加载，不包含后端创建的 blog 类型笔记

**P0-2：博客无草稿状态**
- 发布直接创建 GitHub commit (`push-blog.ts:168-176`)
- 无"保存草稿"按钮或中间状态
- 发布后需要等待 Cloudflare Workers 部署才能看到更新

**P1-1：博客分类与后端 Category 表不一致**
- 博客分类存储在 `public/blogs/categories.json`（GitHub 文件）
- 后端有独立的 `Category` 表和 `/api/categories` 接口
- 两者数据完全独立，无法互通

**P1-2：博客搜索不覆盖后端笔记**
- 博客搜索依赖前端从 `/blogs/index.json` 加载后本地过滤
- 后端 `/api/search` 只搜索数据库中的笔记
- 无法统一搜索所有内容

**P2-1：无导出功能**
- 博客无法导出为 PDF 或其他格式

### 4.4 闭环结论

**博客发布闭环：部分闭环**

理由：
1. 博客的创建、编辑、发布、列表、详情、删除流程本身是完整的，但全部基于 GitHub 静态文件。
2. 博客与后端笔记系统完全脱节，导致搜索、标签、分类无法统一。
3. 无草稿状态，发布即 commit，无回退机制。
4. 博客发布依赖 Cloudflare Workers 部署，存在延迟。

## 5. 错题整理闭环审查

### 5.1 能力矩阵

| 能力项 | 状态 | 证据路径 | 是否阻断闭环 | 说明 |
|---|---|---|---|---|
| 进入错题录入页 | 已支持 | `src/app/mistakes/page.tsx:78-83` → `/write-mistake` | 否 | 错题列表页有明确入口 |
| 手动录入 | 已支持 | `src/app/write-mistake/page.tsx:184-269` | 否 | 完整的手动录入表单 |
| 图片识别 | 已支持 | `src/app/write-mistake/page.tsx:53-79` | 否 | 支持多图片上传，AI OCR 分析 |
| 文本分析 | 已支持 | `src/app/write-mistake/page.tsx:82-96` | 否 | 粘贴文本后 AI 分析 |
| AI 结果填充表单 | 已支持 | `src/app/write-mistake/page.tsx:39-51` (applyResult) | 否 | AI 结果正确填充所有字段 |
| 用户确认保存 | 已支持 | `src/app/write-mistake/page.tsx:98-131` (handleSave) | 否 | 用户可修改后保存 |
| 列表展示 | 已支持 | `src/app/mistakes/page.tsx` | 否 | 支持按科目、难度筛选，显示复习信息 |
| 详情展示 | 已支持 | `src/app/notes/[id]/page.tsx:73-114` | 否 | 展示题目、答案、分析、知识点、SM-2 信息 |
| 编辑错题 | 已支持 | `src/app/write-note/[slug]/page.tsx:132-156` | 否 | 通过笔记编辑页实现，支持错题字段编辑 |
| 删除错题 | 已支持 | `src/app/notes/[id]/page.tsx:33-42` | 否 | 详情页有删除按钮 |
| 标签/科目/难度 | 已支持 | `src/app/write-mistake/page.tsx:194-269` | 否 | 完整支持，标签存入 note_tags 关联表 |
| 复习队列 | 已支持 | `src/app/mistakes/review/page.tsx` | 否 | 加载到期错题，逐题复习 |
| 提交复习评分 | 已支持 | `src/app/mistakes/review/page.tsx:39-56` | 否 | 0-5 分评分，调用 submitReview API |
| SM-2 字段更新 | 已支持 | `backend/app/routers/review.py:30-60`, `backend/app/services/sm2.py` | 否 | 正确更新 ef, interval, repetitions, next_review, last_reviewed |
| AI 失败兜底 | 部分支持 | `src/app/write-mistake/page.tsx:75-76` | 否 | alert 提示后用户可手动填写 |
| 图片证据持久化 | 未支持 | - | 是 | 图片仅以 base64 临时发送给 AI，不保存到数据库或存储 |

### 5.2 数据流审查

```
用户进入 /write-mistake 页面
  → src/app/write-mistake/page.tsx

方式一：图片识别
  → 用户上传图片 (handleImageUpload)
  → FileReader 转 base64
  → 调用 analyzeMistake(images) → src/lib/api/ai.ts:14
  → POST /api/ai/analyze → backend/app/routers/ai.py:236-237
  → call_ocr_model(messages) → backend/app/services/ai_service.py:8-17
  → 调用 DashScope (qwen-vl-max) API
  → 返回 AnalyzeResponse (title, question, correct_answer, analysis, knowledge_points, subject, difficulty, tags)
  → 前端 applyResult() 填充表单

方式二：文本分析
  → 用户粘贴文本 (handleTextAnalyze)
  → 调用 analyzeText(text) → src/lib/api/ai.ts:21
  → POST /api/ai/analyze-text → backend/app/routers/ai.py:266-267
  → call_text_model(messages) → backend/app/services/ai_service.py:20-29
  → 调用 DeepSeek API
  → 返回 AnalyzeResponse
  → 前端 applyResult() 填充表单

用户确认并保存
  → handleSave() → src/app/write-mistake/page.tsx:98-131
  → 构造 content (Markdown 格式拼接 question/my_answer/correct_answer/analysis/knowledge_points)
  → createNote({ slug, title, content, type: 'mistake', tags, subject, difficulty, question, ... })
  → POST /api/notes → backend/app/routers/notes.py:94-133
  → _get_or_create_tags() 创建/关联标签
  → 创建 Note 记录 (type='mistake')
  → 自动设置 next_review = date.today()
  → 写入 PostgreSQL
  → 前端 router.push('/mistakes')

错题列表展示
  → /mistakes → src/app/mistakes/page.tsx
  → useNoteIndex({ type: 'mistake', ... }) → GET /api/notes?type=mistake
  → 后端查询 Note 表，返回分页数据
  → 前端按 subject、difficulty 筛选（difficulty 为前端过滤）

复习流程
  → /mistakes/review → src/app/mistakes/review/page.tsx
  → getReviewQueue() → GET /api/review/queue
  → 后端查询 type='mistake' AND next_review <= today
  → 逐题展示，用户评分 0-5
  → submitReview(slug, quality) → POST /api/review/{slug}
  → 后端调用 sm2() 算法更新 ef/interval/repetitions/next_review/last_reviewed
  → 写入 PostgreSQL
```

### 5.3 主要问题

**P1-1：图片证据不持久化**
- 用户上传的错题图片仅以 base64 临时发送给 AI (`write-mistake/page.tsx:59-71`)
- AI 分析完成后，图片数据不保存到数据库
- `Note` 模型无 `image_url` 或 `image_data` 字段
- 如果图片中包含关键题目信息（如图表、几何图形），保存后无法回溯原始图片

**P1-2：错题详情/编辑路由冗余**
- `/mistakes/[id]` 目录为空，错题详情使用 `/notes/[slug]`
- `/write-mistake/[slug]` 目录为空，错题编辑使用 `/write-note/[slug]`
- 用户在错题列表点击某题，跳转到 `/notes/{slug}`，URL 路径显示 "notes" 而非 "mistakes"

**P1-3：difficulty 筛选为前端过滤**
- `src/app/mistakes/page.tsx:29`: `const filtered = data?.items.filter(item => !difficulty || item.difficulty === difficulty) || []`
- 后端 `list_notes` 接口不支持 `difficulty` 参数筛选
- 当数据量大时，前端过滤只作用于当前页，可能遗漏

**P2-1：AI 分析失败提示简陋**
- `write-mistake/page.tsx:76`: `alert('AI 分析失败: ' + err.message)`
- 使用浏览器原生 alert，不符合现代 UI 体验
- 错误信息可能包含技术细节，不够用户友好

**P2-2：AI 分析结果与用户保存内容可能不一致**
- AI 分析结果先填充表单，用户可修改后保存
- 但如果用户不修改直接保存，content 字段是拼接的 Markdown，而 question/my_answer 等字段是独立存储的
- 详情页同时展示 content（Markdown 渲染）和独立字段，可能存在重复

### 5.4 闭环结论

**错题整理闭环：基本完整**

理由：
1. 主流程完整：录入（手动/图片/文本）→ AI 分析 → 表单填充 → 保存 → 列表展示 → 详情查看 → 编辑 → 删除 → 复习队列 → SM-2 评分 → 字段更新。
2. SM-2 复习算法正确实现，复习后正确更新所有间隔重复字段。
3. 标签、科目、难度等元数据正确保存到后端。
4. 存在少量非阻断问题：图片证据不持久化、路由冗余、difficulty 筛选为前端过滤。

## 6. 笔记撰写整理闭环审查

### 6.1 能力矩阵

| 能力项 | 状态 | 证据路径 | 是否阻断闭环 | 说明 |
|---|---|---|---|---|
| 进入写笔记页 | 已支持 | `src/app/notes/page.tsx:57-62` → `/write-note` | 否 | 笔记列表页有明确入口 |
| 新建笔记 | 已支持 | `src/app/write-note/page.tsx` | 否 | 支持 note/blog/mistake 三种类型 |
| 编辑笔记 | 已支持 | `src/app/write-note/[slug]/page.tsx` | 否 | 加载已有数据，支持修改 |
| 保存笔记 | 已支持 | `src/lib/api/notes.ts:106` (createNote), `:113` (updateNote) | 否 | 调用后端 API 持久化 |
| 列表展示 | 已支持 | `src/app/notes/page.tsx` | 否 | 分页、按类型筛选、搜索 |
| 详情展示 | 已支持 | `src/app/notes/[id]/page.tsx` | 否 | Markdown 渲染 + 标签展示 |
| Markdown 渲染 | 已支持 | `src/hooks/use-markdown-render.tsx`, `src/lib/markdown-renderer.ts` | 否 | 使用 marked + Shiki + KaTeX |
| 代码块渲染 | 已支持 | `src/lib/markdown-renderer.ts:203-229` | 否 | Shiki 语法高亮，支持 copy |
| LaTeX 渲染 | 已支持 | `src/lib/markdown-renderer.ts:107-123, 126-180` | 否 | KaTeX 渲染行内和块级公式 |
| 图片插入 | 未支持 | - | 是 | 笔记编辑器无图片上传功能 |
| 标签保存 | 已支持 | `backend/app/routers/notes.py:29-39` | 否 | 自动创建或关联已有标签 |
| 分类保存 | 部分支持 | `backend/app/models/note.py:45` (category 字段存在) | 是 | 后端支持但前端表单无 category 输入 |
| 科目保存 | 已支持 | `src/app/write-note/page.tsx:145-149` | 否 | 自由文本输入，保存到 subject 字段 |
| 搜索 | 已支持 | `src/app/notes/page.tsx:37-42`, `backend/app/routers/notes.py:66-73` | 否 | 后端 ilike 搜索 title/content/question |
| 筛选 | 已支持 | `src/app/notes/page.tsx:43-55` | 否 | 按类型筛选，支持搜索关键词 |
| 删除 | 已支持 | `src/app/notes/[id]/page.tsx:33-42`, `backend/app/routers/notes.py:167-173` | 否 | 真删除（非软删除） |
| 导出 | 未支持 | - | 否 | 无导出功能 |
| 刷新后数据仍在 | 已支持 | 数据存储在 PostgreSQL | 否 | 刷新后从后端重新加载 |

### 6.2 数据流审查

```
用户进入 /write-note 页面
  → src/app/write-note/page.tsx
  → 表单状态: useState 管理 (title, content, type, tags, summary, subject, difficulty, ...)

用户选择类型 (note/blog/mistake)
  → type 切换影响表单字段展示
  → blog: 显示 summary 输入
  → mistake: 显示 question/my_answer/correct_answer/analysis/knowledge_points 输入

用户输入内容
  → 标题、slug、Markdown 正文 (或错题字段)
  → 标签: 手动输入，Enter 添加

用户点击发布
  → handleSave() → src/app/write-note/page.tsx:42-79
  → 对于 mistake 类型: 拼接 Markdown content
  → createNote(data) → src/lib/api/notes.ts:106-111
  → POST /api/notes → backend/app/routers/notes.py:94-133
  → _get_or_create_tags(db, req.tags): 自动创建或关联标签
  → 创建 Note 对象，写入 PostgreSQL
  → 对于 mistake: 自动设置 next_review = date.today()
  → 返回 NoteOut
  → 前端 router.push('/notes')

笔记列表展示
  → /notes → src/app/notes/page.tsx
  → useNoteIndex({ type, q, page, size }) → GET /api/notes?...
  → 后端查询 Note 表，支持 type/tag/subject/category/q/hidden 筛选
  → 返回 NoteListResponse (items, total, page, size)
  → 前端渲染列表，显示类型标签、难度、科目、摘要、标签

笔记详情展示
  → /notes/[slug] → src/app/notes/[id]/page.tsx
  → getNote(slug) → GET /api/notes/{slug}
  → useMarkdownRender(note.content)
  → 对于 mistake 类型: 额外展示 question/my_answer/correct_answer/analysis/knowledge_points/SM-2 信息
  → 对于 note/blog 类型: 渲染 Markdown 内容

笔记编辑
  → /write-note/[slug] → src/app/write-note/[slug]/page.tsx
  → getNote(slug) 加载已有数据
  → 表单填充
  → updateNote(slug, data) → PUT /api/notes/{slug}
  → 后端更新 Note 记录
  → 前端 router.push(`/notes/${slug}`)

笔记删除
  → notes/[id]/page.tsx → handleDelete()
  → deleteNote(slug) → DELETE /api/notes/{slug}
  → 后端删除 Note 记录（真删除）
  → 前端 router.push('/notes')
```

### 6.3 主要问题

**P0-1：笔记编辑器无 Markdown 预览**
- 博客编辑器 (`/write`) 有完整的预览功能 (`WritePreview` 组件)
- 笔记编辑器 (`/write-note`, `/write-note/[slug]`) 只有纯文本 textarea
- 用户在写笔记时无法预览 Markdown 渲染效果、代码高亮、LaTeX 公式

**P0-2：笔记编辑器无图片上传**
- 博客编辑器支持粘贴图片上传到 GitHub (`editor.tsx:130-156`)
- 笔记编辑器无任何图片上传能力
- 后端 Note 模型有 `cover` 字段，但前端表单无入口

**P1-1：笔记表单缺少 category 字段**
- 后端 NoteCreate/NoteUpdate schema 都支持 `category` 字段
- 笔记创建页面 (`write-note/page.tsx`) 无 category 输入
- 笔记编辑页面 (`write-note/[slug]/page.tsx`) 无 category 输入
- 博客编辑器 (`/write`) 有完整的分类选择功能

**P1-2：笔记表单缺少 cover 字段**
- 后端 Note 模型有 `cover` 字段
- 笔记创建/编辑表单均无封面图输入
- 笔记列表页可展示 cover，但无法设置

**P1-3：Subject 为自由文本输入**
- 后端有独立的 `Subject` 表 (`/api/subjects`)
- 笔记表单中 subject 为 `<input>` 自由文本
- 无下拉选择已有科目，可能导致拼写不一致

**P1-4：笔记编辑器能力远弱于博客编辑器**
- 博客编辑器: 标题、slug、Markdown (带快捷键)、粘贴图片、摘要、标签、分类、日期、hidden、封面、预览、导入 MD
- 笔记编辑器: 标题、slug、Markdown (纯 textarea)、标签、(summary 仅 blog 类型)、(错题字段仅 mistake 类型)
- 差距: 预览、图片、快捷键、分类、日期、hidden、封面、导入

**P2-1：错误提示风格不一致**
- 笔记编辑器使用 `alert()` (`write-note/page.tsx:76`, `write-note/[slug]/page.tsx:96`)
- 博客编辑器使用 `toast` (`use-publish.ts:36`)

**P2-2：无导出功能**
- 笔记不支持导出为 Markdown、PDF 或其他格式

**P2-3：无收藏/置顶功能**
- 后端 Note 模型无 `pinned` 或 `favorite` 字段
- 前端无相关 UI

### 6.4 闭环结论

**笔记撰写整理闭环：基本完整**

理由：
1. 主流程完整：新建 → 编辑 → 保存 → 列表 → 详情 → 搜索 → 筛选 → 删除。
2. Markdown 渲染完整：代码高亮 (Shiki)、数学公式 (KaTeX)、图片、TOC。
3. 标签系统完整：创建时自动关联，保存到 note_tags 关联表。
4. 搜索真实查询后端，支持 title/content/question 全文搜索。
5. 存在非阻断问题：编辑器无预览、无图片上传、缺少 category/cover 入口、Subject 无下拉选择。

## 7. 跨模块一致性审查

### 7.1 博客编辑器与笔记编辑器能力不一致

| 能力 | 博客编辑器 (/write) | 笔记编辑器 (/write-note) |
|---|---|---|
| Markdown 编辑 | 带快捷键 (Ctrl+B/I/K, Tab) | 纯 textarea |
| 预览 | 完整预览 (BlogPreview) | 无 |
| 图片上传 | 粘贴图片上传到 GitHub | 无 |
| 标签 | TagInput 组件 | 手动输入 |
| 分类 | Select 下拉 (来自 categories.json) | 无 |
| 摘要 | 有 | 仅 blog 类型 |
| 日期 | datetime-local 选择器 | 无 |
| Hidden | 复选框 | 无 |
| 封面 | CoverSection (URL/文件) | 无 |
| 导入 MD | 支持 | 无 |
| 错误提示 | toast (sonner) | alert() |
| 删除 | 有 (GitHub commit) | 有 (后端 API) |

### 7.2 Markdown 渲染器复用情况

- 博客详情页 (`/blog/[id]`) 使用 `BlogPreview` → `useMarkdownRender` → `renderMarkdown`
- 笔记详情页 (`/notes/[id]`) 使用 `useMarkdownRender` → `renderMarkdown`
- 博客编辑预览使用 `WritePreview` → `BlogPreview` → `useMarkdownRender`
- **结论**：详情页和预览共用同一渲染器 (`src/lib/markdown-renderer.ts`)，行为一致

### 7.3 标签、分类、科目语义一致性

| 概念 | 博客 | 笔记/错题 | 是否一致 |
|---|---|---|---|
| 标签 | 存储在 `config.json` 的 `tags` 数组 | 存储在 `note_tags` 关联表 | 不一致 |
| 分类 | 存储在 `blogs/categories.json` 的字符串数组 | 存储在 `Note.category` 字段 + `categories` 表 | 不一致 |
| 科目 | 不适用 | 存储在 `Note.subject` 字段 + `subjects` 表 | 仅笔记/错题有 |

### 7.4 搜索覆盖范围

- 博客搜索：前端从 `/blogs/index.json` 加载后本地过滤 (`useBlogIndex`)
- 笔记/错题搜索：后端 `/api/notes?q=...` 或 `/api/search?q=...` (数据库 ilike)
- **问题**：无法统一搜索博客和笔记

### 7.5 删除行为一致性

| 模块 | 删除方式 | 数据恢复 |
|---|---|---|
| 博客 | GitHub commit 删除文件 | Git 历史可恢复 |
| 笔记 | 后端 DELETE /api/notes/{slug} (真删除) | 不可恢复 |
| 错题 | 同笔记 | 不可恢复 |

### 7.6 错误提示风格

| 位置 | 方式 |
|---|---|
| 博客发布/删除 | toast (sonner) |
| 笔记创建/编辑 | alert() |
| 错题 AI 分析 | alert() |
| 复习提交 | alert() |
| 管理面板 | alert() |

## 8. 数据模型与字段一致性审查

### 8.1 字段一致性问题表

| 模块 | 前端字段 | 后端 schema | 数据模型 | 问题 | 影响 |
|---|---|---|---|---|---|
| 笔记 | 无 cover 输入 | NoteCreate.cover: str\|None | Note.cover: str\|None | 前端无入口设置 cover | 列表页可展示但无法设置 |
| 笔记 | 无 category 输入 | NoteCreate.category: str\|None | Note.category: str\|None | 前端无入口设置 category | 分类功能不可用 |
| 笔记 | subject 为自由文本 | NoteCreate.subject: str\|None | Note.subject: str\|None | 不查询 Subject 表 | 可能拼写不一致 |
| 博客 | tags: string[] | 不使用后端 | config.json.tags | 博客标签与后端 Tag 表无关 | 搜索不互通 |
| 博客 | category: string | 不使用后端 | blogs/categories.json | 博客分类与后端 Category 表无关 | 数据分裂 |
| 错题 | difficulty 为前端筛选 | 后端不支持 difficulty 参数 | Note.difficulty | 前端过滤仅作用于当前页 | 大数据量时遗漏 |
| 错题 | 图片不持久化 | 后端无 image 字段 | 无 | AI 分析图片丢失 | 无法回溯原始图片 |

### 8.2 Note 模型字段使用情况

| 字段 | 创建时 | 编辑时 | 列表展示 | 详情展示 | 搜索 |
|---|---|---|---|---|---|
| slug | 填写 | 不可修改 | - | URL 参数 | - |
| title | 填写 | 可修改 | 展示 | 展示 | ilike |
| content | 填写/拼接 | 可修改 | - | Markdown 渲染 | ilike |
| type | 选择 | 不可修改 | 标签展示 | 标签展示 | 筛选参数 |
| hidden | 无入口 | 无入口 | 过滤 | - | 筛选参数 |
| summary | blog 时填写 | 可修改 | 展示 | - | - |
| cover | 无入口 | 无入口 | - | - | - |
| category | 无入口 | 无入口 | - | - | 筛选参数 |
| subject | 填写 | 可修改 | 展示 | 展示 | 筛选参数 |
| difficulty | 选择 | 可修改 | 展示 | 展示 | 无后端筛选 |
| question | 填写 | 可修改 | - | 展示 | ilike |
| my_answer | 填写 | 可修改 | - | 展示 | - |
| correct_answer | 填写 | 可修改 | - | 展示 | - |
| analysis | 填写 | 可修改 | - | 展示 | ilike (search) |
| knowledge_points | 填写 | 可修改 | - | 展示 | ilike (search) |
| ef | 自动 (2.5) | SM-2 更新 | 展示 | 展示 | - |
| interval | 自动 (0) | SM-2 更新 | - | 展示 | - |
| repetitions | 自动 (0) | SM-2 更新 | 展示 | 展示 | - |
| next_review | 自动 (today) | SM-2 更新 | 展示 | 展示 | - |
| last_reviewed | null | SM-2 更新 | - | 展示 | - |
| tags | 填写 | 可修改 | 展示 | 展示 | 筛选参数 |

## 9. 可用性问题分级

### P0：阻断主流程

| 编号 | 问题 | 模块 | 影响 |
|---|---|---|---|
| P0-1 | 博客与笔记使用完全不同的持久化层，搜索/标签/分类互不可见 | 博客+笔记 | 系统分裂为两个独立系统 |
| P0-2 | 博客无草稿状态，发布即 commit | 博客 | 无法保存未完成的博客 |
| P0-3 | 笔记编辑器无 Markdown 预览 | 笔记 | 用户无法在编辑时查看渲染效果 |
| P0-4 | 笔记编辑器无图片上传 | 笔记 | 无法在笔记中插入图片 |
| P0-5 | 笔记表单缺少 category 字段入口 | 笔记 | 分类功能形同虚设 |

### P1：影响核心体验

| 编号 | 问题 | 模块 | 影响 |
|---|---|---|---|
| P1-1 | AI 分析图片不持久化 | 错题 | 丢失原始图片证据 |
| P1-2 | 错题详情/编辑路由冗余 (/mistakes/[id] 为空) | 错题 | URL 语义不清晰 |
| P1-3 | difficulty 筛选为前端过滤 | 错题 | 大数据量时筛选不完整 |
| P1-4 | 笔记表单缺少 cover 字段入口 | 笔记 | 无法设置封面图 |
| P1-5 | Subject 为自由文本，不查询 Subject 表 | 笔记+错题 | 可能拼写不一致 |
| P1-6 | 博客分类与后端 Category 表不一致 | 博客 | 数据无法互通 |
| P1-7 | 笔记编辑器能力远弱于博客编辑器 | 笔记 | 体验不一致 |
| P1-8 | 错误提示风格不一致 (toast vs alert) | 跨模块 | 用户体验不统一 |

### P2：增强型问题

| 编号 | 问题 | 模块 | 影响 |
|---|---|---|---|
| P2-1 | 无导出功能 | 笔记 | 无法导出 Markdown/PDF |
| P2-2 | 无收藏/置顶功能 | 笔记 | 无法标记重要内容 |
| P2-3 | 无版本历史 | 跨模块 | 无法查看修改记录 |
| P2-4 | 无软删除 | 笔记+错题 | 误删不可恢复 |
| P2-5 | 搜索不覆盖博客 | 博客 | 无法统一搜索 |

## 10. 修复路线建议

### 第一阶段：先修闭环 P0

#### P0-1：统一博客与笔记的持久化层

- **问题**：博客通过 GitHub 静态文件存储，笔记通过 PostgreSQL 存储，两套系统完全独立。
- **影响**：搜索、标签、分类无法统一；博客不在笔记列表中出现。
- **建议修复**：
  - 方案 A：将博客发布流程改为调用后端 API（POST /api/notes, type='blog'），同时保留 GitHub 同步作为部署手段。
  - 方案 B：保持博客独立，但在管理面板增加"同步博客到后端"功能。
  - 推荐方案 A。
- **涉及文件**：
  - `src/app/write/services/push-blog.ts`
  - `src/app/write/hooks/use-publish.ts`
  - `src/hooks/use-blog-index.ts`
  - `src/app/blog/page.tsx`
  - `backend/app/routers/notes.py`
  - `backend/app/services/github_sync.py`
- **验收标准**：通过 `/write` 发布的博客出现在 `/notes?type=blog` 列表中；统一搜索可覆盖博客。

#### P0-2：为博客增加草稿状态

- **问题**：发布即 commit，无法保存未完成内容。
- **影响**：用户中断写作后内容丢失。
- **建议修复**：
  - 在前端增加"保存草稿"按钮，将内容存入 localStorage 或后端。
  - 发布按钮改为"发布"语义，保存草稿不触发 GitHub commit。
- **涉及文件**：
  - `src/app/write/components/actions.tsx`
  - `src/app/write/stores/write-store.ts`
- **验收标准**：用户可保存草稿，刷新后恢复；发布与保存草稿分离。

#### P0-3：为笔记编辑器增加 Markdown 预览

- **问题**：笔记编辑器只有纯 textarea，无预览。
- **影响**：用户无法在编辑时查看 Markdown 渲染效果。
- **建议修复**：
  - 在 `/write-note` 和 `/write-note/[slug]` 页面增加预览按钮和预览面板。
  - 复用已有的 `useMarkdownRender` hook 和 `BlogPreview` 组件。
- **涉及文件**：
  - `src/app/write-note/page.tsx`
  - `src/app/write-note/[slug]/page.tsx`
  - `src/hooks/use-markdown-render.tsx`
- **验收标准**：笔记编辑器可切换预览模式，正确渲染 Markdown、代码块、LaTeX。

#### P0-4：为笔记编辑器增加图片上传

- **问题**：笔记编辑器无图片上传能力。
- **影响**：无法在笔记中插入图片。
- **建议修复**：
  - 增加图片上传到后端对象存储或 GitHub 的能力。
  - 在 textarea 中插入 `![](url)` Markdown 图片语法。
  - 需要后端增加图片上传接口或复用 GitHub 存储。
- **涉及文件**：
  - `src/app/write-note/page.tsx`
  - `src/app/write-note/[slug]/page.tsx`
  - `backend/app/routers/` (新增图片上传路由)
- **验收标准**：笔记编辑器支持粘贴/选择图片上传，插入 Markdown 图片语法，详情页正确展示。

#### P0-5：为笔记表单增加 category 字段

- **问题**：后端支持 category 字段，但前端表单无入口。
- **影响**：分类功能不可用。
- **建议修复**：
  - 在 `/write-note` 和 `/write-note/[slug]` 页面增加 category 下拉选择。
  - 查询 `/api/categories` 获取已有分类列表。
- **涉及文件**：
  - `src/app/write-note/page.tsx`
  - `src/app/write-note/[slug]/page.tsx`
- **验收标准**：笔记创建/编辑时可选择分类，保存后列表/详情页正确展示。

### 第二阶段：补齐 P1 体验问题

#### P1-1：持久化 AI 分析图片

- **问题**：AI 分析图片仅临时发送，不保存。
- **影响**：错题中的图表、几何图形等视觉信息丢失。
- **建议修复**：
  - 在 Note 模型增加 `images` 字段（JSON 数组，存储图片 URL）。
  - 图片上传到对象存储，保存 URL 到数据库。
  - 或将 base64 图片转为文件存储到 GitHub。
- **涉及文件**：
  - `backend/app/models/note.py`
  - `backend/app/schemas/note.py`
  - `src/app/write-mistake/page.tsx`
  - `backend/alembic/versions/` (新增迁移)
- **验收标准**：错题保存后可查看原始图片证据。

#### P1-2：清理错题冗余路由

- **问题**：`/mistakes/[id]` 和 `/write-mistake/[slug]` 目录为空。
- **影响**：URL 语义不清晰。
- **建议修复**：
  - 要么实现独立的错题详情/编辑路由，要么移除空目录。
  - 错题列表中的链接保持指向 `/notes/[slug]` 或改为 `/mistakes/[slug]`。
- **涉及文件**：
  - `src/app/mistakes/[id]/` (决策：实现或移除)
  - `src/app/write-mistake/[slug]/` (决策：实现或移除)
  - `src/app/mistakes/page.tsx:100` (链接目标)
- **验收标准**：路由清晰，无空目录。

#### P1-3：difficulty 筛选改为后端查询

- **问题**：difficulty 筛选为前端过滤。
- **影响**：大数据量时筛选不完整。
- **建议修复**：
  - 后端 `list_notes` 接口增加 `difficulty` 参数。
  - 前端将 difficulty 传入 API 请求参数。
- **涉及文件**：
  - `backend/app/routers/notes.py`
  - `src/lib/api/notes.ts`
  - `src/app/mistakes/page.tsx`
- **验收标准**：difficulty 筛选由后端完成，分页数据正确。

#### P1-4：Subject 下拉选择

- **问题**：Subject 为自由文本输入。
- **影响**：可能拼写不一致。
- **建议修复**：
  - 在笔记/错题表单中增加 Subject 下拉选择（从 `/api/subjects` 加载）。
  - 保留自由输入能力（支持新增科目）。
- **涉及文件**：
  - `src/app/write-note/page.tsx`
  - `src/app/write-note/[slug]/page.tsx`
  - `src/app/write-mistake/page.tsx`
- **验收标准**：Subject 字段支持从已有科目中选择，也支持手动输入新科目。

#### P1-5：统一错误提示风格

- **问题**：部分页面使用 alert()，部分使用 toast。
- **影响**：用户体验不一致。
- **建议修复**：全部改为 toast (sonner)。
- **涉及文件**：所有使用 alert() 的文件。
- **验收标准**：所有错误/成功提示使用 toast。

### 第三阶段：再考虑扩展能力

- **Mermaid 图表**：需要先确保 Markdown 渲染器支持 Mermaid 语法解析和渲染。
- **AI 生成 Mermaid**：需要先有 Mermaid 渲染能力。
- **图片存储系统**：需要统一的文件上传和存储方案。
- **附件管理**：需要后端增加附件模型和 API。
- **导出**：需要实现 Markdown/PDF 导出功能。
- **版本历史**：需要后端增加版本模型，记录每次修改。

## 11. 当前不建议做的事情

- **不建议先做 Mermaid**：三个主流程尚未完全闭环，博客与笔记持久化层未统一，Mermaid 无法在两个系统间一致工作。
- **不建议先做 AI 图片生成**：图片存储方案未确定，生成的图片无处持久化。
- **不建议先换复杂编辑器**：当前笔记编辑器的首要问题是缺少预览和图片，而非编辑器本身。应先补齐基础能力。
- **不建议先做知识图谱**：数据模型尚不稳定，标签/分类/科目未统一。
- **不建议先做大规模 UI 重构**：应先修复闭环问题，再优化 UI。
- **不建议先改数据库结构**：除非 P0 闭环要求必须改（如增加图片字段）。

## 12. 需要用户确认的问题

1. **博客是否需要草稿和发布两个状态？** 当前博客发布直接 commit 到 GitHub，无草稿机制。是否需要增加草稿功能？

2. **错题是否必须保存原始图片证据？** 当前 AI 分析图片不持久化。如果错题中包含图表、几何图形等视觉信息，是否需要保存原始图片？

3. **普通笔记和错题是否继续共用 Note 模型？** 当前 Note 模型通过 `type` 字段区分 note/blog/mistake。是否继续这种设计，还是拆分为独立模型？

4. **删除是否需要软删除？** 当前笔记/错题删除为真删除，不可恢复。是否需要改为软删除（增加 deleted_at 字段）？

5. **搜索是否需要覆盖博客、笔记、错题三个模块？** 当前博客搜索和笔记搜索完全独立。是否需要统一搜索？

6. **标签和分类是否全局共用？** 当前博客标签存储在 GitHub JSON，笔记标签存储在后端 Tag 表。是否需要统一？

7. **博客是否需要迁移到后端持久化？** 当前博客通过 GitHub 静态文件管理。是否需要将博客也纳入后端 Note 模型，保留 GitHub 同步作为部署手段？

8. **笔记编辑器是否需要达到与博客编辑器同等的能力？** 当前笔记编辑器缺少预览、图片上传、快捷键、分类、封面等功能。是否需要补齐？

---

## 结论

**结论一：**
博客发布功能当前属于：**部分闭环**。
理由：
1. 博客的创建、编辑、发布、列表、详情、删除流程本身完整，但全部基于 GitHub 静态文件，与后端 Note 模型完全脱节。
2. 博客与笔记/错题无法统一搜索、统一标签管理、统一分类管理。
3. 无草稿状态，发布即 commit，无回退机制。

**结论二：**
错题整理功能当前属于：**基本完整**。
理由：
1. 主流程完整：手动录入、图片 AI 识别、文本 AI 分析 → 表单填充 → 保存 → 列表 → 详情 → 编辑 → 删除 → 复习队列 → SM-2 评分 → 字段更新。
2. SM-2 算法正确实现，复习后正确更新所有间隔重复字段。
3. 存在非阻断问题：图片证据不持久化、路由冗余、difficulty 筛选为前端过滤。

**结论三：**
笔记撰写整理功能当前属于：**基本完整**。
理由：
1. 主流程完整：新建 → 编辑 → 保存 → 列表 → 详情 → 搜索 → 筛选 → 删除。
2. Markdown 渲染完整：代码高亮、数学公式、图片、TOC。
3. 存在非阻断问题：编辑器无预览、无图片上传、缺少 category/cover 入口。

**总判断：**
当前是否适合进入 Mermaid / 图形生成扩展阶段：**暂不适合**。
理由：
1. 博客与笔记的持久化层尚未统一，扩展功能无法在两个系统间一致工作。
2. 笔记编辑器缺少基础能力（预览、图片），扩展 Mermaid 的前提不满足。
3. 应先修复 P0 闭环问题（统一持久化、补齐编辑器基础能力），再考虑扩展。
